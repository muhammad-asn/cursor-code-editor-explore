"""AWS ECS Command Line Tool

A command-line interface tool for managing AWS ECS (Elastic Container Service) resources.
Provides functionality similar to kubectl but for ECS clusters, instances, and containers.

Authors:
    Muhammad Ardivan (muhammad.a.s.nugroho@gdplabs.id)
"""

import boto3
import click
from rich.console import Console
from rich.table import Table
from typing import List, Dict, Any, Optional
import sys
from datetime import datetime
import json
import os
from pathlib import Path
from dotenv import load_dotenv
import subprocess

load_dotenv()

# Constants
CONFIG_DIR = Path.home() / '.ecsctl'
CONFIG_FILE = CONFIG_DIR / 'config.json'

class AWSClient:
    """Interface for authenticating with Amazon Web Services (AWS).
    
    Handles AWS authentication and session management with support for role assumption.
    
    Attributes:
        profile_name (Optional[str]): AWS profile name for authentication
        region (str): AWS region for API calls
    
    Example:
        >>> client = AWSClient(profile_name="dev")
        >>> session = client.authenticate("arn:aws:iam::123456789012:role/MyRole")
    """

    def __init__(self, profile_name: Optional[str] = None) -> None:
        """Initialize AWS client.
        
        Args:
            profile_name: AWS profile name to use for authentication. If None,
                         uses AWS_PROFILE environment variable.
        """
        self.profile_name = profile_name or os.getenv('AWS_PROFILE')
        self.region = os.getenv('AWS_REGION', 'ap-southeast-1')

    def authenticate(self, role_arn: str, session_name: Optional[str] = "AssumeRoleSession"):
        """
        Authenticate with AWS and assume the specified role
        Args:
            role_arn (str): ARN of the role to assume
            session_name (str): Name for the assumed role session
        Returns:
            boto3.Session: Authenticated AWS session with assumed role credentials
        """
        try:
            # Create base session using either profile or environment credentials
            if self.profile_name:
                session = boto3.Session(profile_name=self.profile_name)
            else:
                session = boto3.Session(region_name=self.region)

            # Assume role using STS
            sts_client = session.client('sts')
            assumed_role = sts_client.assume_role(
                RoleArn=role_arn,
                RoleSessionName=session_name
            )

            # Return new session with temporary credentials
            return boto3.Session(
                aws_access_key_id=assumed_role['Credentials']['AccessKeyId'],
                aws_secret_access_key=assumed_role['Credentials']['SecretAccessKey'],
                aws_session_token=assumed_role['Credentials']['SessionToken'],
                region_name=self.region
            )
        except Exception as e:
            raise Exception(f"Failed to authenticate with AWS: {str(e)}")

class ECSCommandError(Exception):
    """Custom exception for ECS command errors."""
    pass

class ClusterConfig:
    """Manages ECS cluster configuration."""
    
    def __init__(self):
        """Initialize configuration management."""
        self.config_dir = CONFIG_DIR
        self.config_file = CONFIG_FILE
        self._ensure_config_exists()

    def _ensure_config_exists(self):
        """Create config directory and file if they don't exist."""
        self.config_dir.mkdir(exist_ok=True)
        if not self.config_file.exists():
            self._save_config({'current-cluster': None})

    def _save_config(self, config: Dict[str, Any]):
        """Save configuration to file."""
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file."""
        with open(self.config_file, 'r') as f:
            return json.load(f)

    def get_current_cluster(self) -> Optional[str]:
        """Get current cluster name."""
        config = self._load_config()
        return config.get('current-cluster')

    def set_current_cluster(self, cluster_name: str):
        """Set current cluster name."""
        config = self._load_config()
        config['current-cluster'] = cluster_name
        self._save_config(config)

class ECSController:
    """Controller for ECS operations.
    
    Manages interactions with ECS clusters, instances, and containers.
    Handles authentication and provides methods for common ECS operations.
    
    Raises:
        ECSCommandError: If AWS client initialization fails
    """
    
    def __init__(self) -> None:
        """Initialize AWS clients and configuration.
        
        Raises:
            ECSCommandError: If AWS client initialization fails
        """
        try:
            self._initialize_aws_clients()
        except Exception as e:
            raise ECSCommandError(f"Failed to initialize AWS clients: {str(e)}")

    def _initialize_aws_clients(self) -> None:
        """Set up AWS client connections.
        
        Creates authenticated sessions and initializes service clients.
        Uses role assumption if AWS_ROLE_ARN is set.
        """
        self.aws_client = AWSClient()
        role_arn = os.getenv('AWS_ROLE_ARN')
        
        session = (
            self.aws_client.authenticate(role_arn) if role_arn
            else boto3.Session(
                profile_name=self.aws_client.profile_name,
                region_name=self.aws_client.region
            )
        )
        
        self.ecs_client = session.client('ecs')
        self.ec2_client = session.client('ec2')
        self.ssm_client = session.client('ssm')
        self.console = Console()
        self.config = ClusterConfig()

    def get_clusters(self) -> List[str]:
        """Get list of all ECS clusters."""
        try:
            clusters = self.ecs_client.list_clusters()['clusterArns']
            return [cluster.split('/')[-1] for cluster in clusters]
        except Exception as e:
            raise ECSCommandError(f"Failed to get clusters: {str(e)}")

    def get_ec2_instances(self, cluster_name: str) -> List[Dict[Any, Any]]:
        """Get EC2 instances for specified cluster."""
        try:
            container_instances = self.ecs_client.list_container_instances(
                cluster=cluster_name
            )['containerInstanceArns']
            
            instances = []
            if container_instances:
                response = self.ecs_client.describe_container_instances(
                    cluster=cluster_name,
                    containerInstances=container_instances
                )
                
                for instance in response['containerInstances']:
                    ec2_response = self.ec2_client.describe_instances(
                        InstanceIds=[instance['ec2InstanceId']]
                    )
                    
                    instance_info = {
                        'InstanceId': instance['ec2InstanceId'],
                        'InstanceType': ec2_response['Reservations'][0]['Instances'][0]['InstanceType'],
                        'State': ec2_response['Reservations'][0]['Instances'][0]['State']['Name'],
                        'Status': instance['status'],
                        'RunningTasks': instance['runningTasksCount']
                    }
                    instances.append(instance_info)
            
            return instances
        except Exception as e:
            raise ECSCommandError(f"Failed to get EC2 instances: {str(e)}")

    def get_containers(self, cluster_name: str) -> List[Dict[Any, Any]]:
        """Get containers for specified cluster."""
        try:
            tasks = self.ecs_client.list_tasks(cluster=cluster_name)['taskArns']
            containers = []
            
            if tasks:
                response = self.ecs_client.describe_tasks(
                    cluster=cluster_name,
                    tasks=tasks
                )
                
                for task in response['tasks']:
                    for container in task['containers']:
                        container_info = {
                            'Name': container['name'],
                            'Status': container['lastStatus'],
                            'TaskId': task['taskArn'].split('/')[-1],
                            'CPU': container.get('cpu', 'N/A'),
                            'Memory': container.get('memory', 'N/A'),
                            'Created': datetime.fromtimestamp(
                                task['createdAt'].timestamp()
                            ).strftime('%Y-%m-%d %H:%M:%S')
                        }
                        containers.append(container_info)
            
            return containers
        except Exception as e:
            raise ECSCommandError(f"Failed to get containers: {str(e)}")

    def get_instance_details(self, cluster_name: str, instance_id: str) -> Optional[Dict[str, Any]]:
        """Get details for a specific EC2 instance in the cluster."""
        try:
            instances = self.get_ec2_instances(cluster_name)
            return next((instance for instance in instances if instance['InstanceId'] == instance_id), None)
        except Exception as e:
            raise ECSCommandError(f"Failed to get instance details: {str(e)}")

    def check_ssm_status(self, instance_id: str) -> bool:
        """Check if SSM is available on the instance."""
        try:
            response = self.ssm_client.describe_instance_information(
                Filters=[{'Key': 'InstanceIds', 'Values': [instance_id]}]
            )
            return len(response['InstanceInformationList']) > 0
        except Exception as e:
            return False

@click.group()
def cli():
    """ECS command line tool that mimics kubectl."""
    pass

@cli.command('use-cluster')
@click.argument('cluster_name')
def use_cluster(cluster_name: str):
    """Select ECS cluster to use."""
    try:
        ecs = ECSController()
        clusters = ecs.get_clusters()
        
        if cluster_name not in clusters:
            click.echo(f"Error: Cluster '{cluster_name}' not found. Available clusters:", err=True)
            for cluster in clusters:
                click.echo(f"  - {cluster}")
            sys.exit(1)
            
        ecs.config.set_current_cluster(cluster_name)
        click.echo(f"Switched to cluster '{cluster_name}'")
    except ECSCommandError as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)

@cli.command('get-clusters')
def get_clusters():
    """List available ECS clusters."""
    try:
        ecs = ECSController()
        clusters = ecs.get_clusters()
        current = ecs.config.get_current_cluster()
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Cluster Name")
        table.add_column("Current")
        
        for cluster in clusters:
            table.add_row(
                cluster,
                "*" if cluster == current else ""
            )
        
        ecs.console.print(table)
    except ECSCommandError as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)

@cli.group()
def get():
    """Get ECS resources."""
    pass

@get.command('ec2')
def get_ec2():
    """Get EC2 instances in current cluster."""
    try:
        ecs = ECSController()
        current_cluster = ecs.config.get_current_cluster()
        
        if not current_cluster:
            click.echo("Error: No cluster selected. Use 'ecsctl use-cluster' first.", err=True)
            sys.exit(1)
            
        instances = ecs.get_ec2_instances(current_cluster)
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Instance ID")
        table.add_column("Type")
        table.add_column("State")
        table.add_column("Status")
        table.add_column("Running Tasks")
        
        for instance in instances:
            table.add_row(
                instance['InstanceId'],
                instance['InstanceType'],
                instance['State'],
                instance['Status'],
                str(instance['RunningTasks'])
            )
        
        ecs.console.print(table)
    except ECSCommandError as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)

@get.command('containers')
def get_containers():
    """Get containers in current cluster."""
    try:
        ecs = ECSController()
        current_cluster = ecs.config.get_current_cluster()
        
        if not current_cluster:
            click.echo("Error: No cluster selected. Use 'ecsctl use-cluster' first.", err=True)
            sys.exit(1)
            
        containers = ecs.get_containers(current_cluster)
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Name")
        table.add_column("Status")
        table.add_column("Task ID")
        table.add_column("CPU")
        table.add_column("Memory")
        table.add_column("Created")
        
        for container in containers:
            table.add_row(
                container['Name'],
                container['Status'],
                container['TaskId'],
                str(container['CPU']),
                str(container['Memory']),
                container['Created']
            )
        
        ecs.console.print(table)
    except ECSCommandError as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)

@cli.command('exec')
@click.argument('instance_id')
def exec_instance(instance_id: str):
    """Execute interactive shell on EC2 instance using SSM."""
    try:
        ecs = ECSController()
        current_cluster = ecs.config.get_current_cluster()
        
        if not current_cluster:
            click.echo("Error: No cluster selected. Use 'ecsctl use-cluster' first.", err=True)
            sys.exit(1)

        # Verify instance exists in cluster
        instance = ecs.get_instance_details(current_cluster, instance_id)
        if not instance:
            click.echo(f"Error: Instance '{instance_id}' not found in cluster '{current_cluster}'", err=True)
            sys.exit(1)

        # Check SSM availability
        if not ecs.check_ssm_status(instance_id):
            click.echo(f"Error: SSM is not available on instance '{instance_id}'", err=True)
            sys.exit(1)

        # Start SSM session with profile and region
        click.echo(f"Starting session with instance '{instance_id}'...")
        cmd = ['aws', 'ssm', 'start-session', '--target', instance_id]
        
        # Add profile if available
        if ecs.aws_client.profile_name:
            cmd.extend(['--profile', ecs.aws_client.profile_name])
        
        # Add region
        cmd.extend(['--region', ecs.aws_client.region])
        
        subprocess.run(cmd)

    except ECSCommandError as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)

if __name__ == '__main__':
    cli() 
<div align="center">
  <img src="docs/assets/poseidon-ecs.png" alt="ECSCTL - Powered by Poseidon" width="400"/>

  # ECSCTL
  ### Command the Seas of Containers

  [![GitHub release](https://img.shields.io/github/v/release/username/ecsctl)](https://github.com/username/ecsctl/releases)
  [![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
  [![Go Report Card](https://goreportcard.com/badge/github.com/username/ecsctl)](https://goreportcard.com/report/github.com/username/ecsctl)
</div>

## 🔱 Overview

ECSCTL is your divine instrument for commanding Amazon ECS clusters with the power of Poseidon himself. Built with Python and Boto3, it provides kubectl-like commands for managing your Amazon ECS infrastructure.

## ⚡ Divine Powers

- 🌊 **Cluster Management** 
  - List and switch between ECS clusters
  - Store cluster preferences in `~/.ecsctl/config.json`
- 🚢 **EC2 Fleet Vision** 
  - View all EC2 instances in your cluster
  - Monitor instance states, types, and running tasks
- 👁️ **Container Insight** 
  - Track container statuses and details
  - View CPU, memory, and creation timestamps
- ⚓ **Instance Access** 
  - Direct SSH access via AWS Systems Manager (SSM)
  - Secure shell access to container instances

## 🏺 Installation

```bash
# Clone the repository
git clone https://github.com/username/ecsctl.git

# Install dependencies
cd python
pip install -r requirements.txt
```

## ⚔️ Quick Start

```bash
# List all available clusters
python3 ecsctl get-clusters

# Select a cluster to work with
python3 ecsctl use-cluster my-cluster-name

# View EC2 instances in your cluster
python3 ecsctl get ec2

# View containers running in your cluster
python3 ecsctl get containers

# Access an EC2 instance shell (requires SSM)
python3 ecsctl exec i-1234567890abcdef0
```

## 📖 Configuration

ECSCTL uses the following configuration sources:
- AWS credentials from environment variables or AWS profiles
- Custom configurations stored in `~/.ecsctl/config.json`
- Optional role assumption via `AWS_ROLE_ARN`
- Region settings (defaults to `ap-southeast-1`)

## ⚖️ Divine License
This project is protected by the [Apache 2.0 License](LICENSE) - may the gods watch over its use.

## 🙏 Acknowledgments
- The AWS Gods for their blessed APIs
- The Open Source Pantheon for their divine inspiration
- All contributors who have ascended to help this project

---

<div align="center">
  <i>Crafted with ⚡ by the Olympian Dev Team</i>
</div>

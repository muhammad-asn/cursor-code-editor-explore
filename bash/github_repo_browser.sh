#!/usr/bin/env bash

# GitHub Repository Browser
#
# Purpose: Browse GitHub repositories by organization and topic
# Usage: ./github_repo_browser.sh
#        Follow the interactive menu to search repositories by organization and topic
# Author: Muhammad Ardivan (muhammad.a.s.nugroho@gdplabs.id)
# Dependencies: curl, jq
# Date: 01-12-2024

# Error handling
set -euo pipefail
IFS=$'\n\t'  # Added for safer word splitting
trap 'echo "Error: Script failed on line $LINENO. Cleaning up..." >&2' ERR
trap 'echo "Script interrupted. Cleaning up..." >&2' INT TERM

# Check dependencies
check_dependencies() {
    local deps=("curl" "jq")
    for dep in "${deps[@]}"; do
        if ! command -v "$dep" >/dev/null 2>&1; then
            echo "Error: Required dependency '$dep' is not installed."
            exit 1
        fi
    done
}

# Enhanced environment validation
check_env() {
    local env_file=".env"
    local env_example=".env.example"
    
    if [[ ! -f "$env_file" ]]; then
        echo "Error: $env_file file not found" >&2
        echo "Required environment variables:" >&2
        echo "GITHUB_TOKEN - Your GitHub personal access token" >&2
        
        # Create example .env file if it doesn't exist
        if [[ ! -f "$env_example" ]]; then
            echo "GITHUB_TOKEN=your_token_here" > "$env_example"
            echo "Created $env_example file for reference" >&2
        }
        exit 1
    fi

    # Source .env file
    source "$env_file"

    if [[ -z "${GITHUB_TOKEN:-}" ]]; then
        echo "Error: GITHUB_TOKEN not set in $env_file file" >&2
        exit 1
    fi
}

# GitHub API request function
github_request() {
    local endpoint="$1"
    curl -s -H "Authorization: token $GITHUB_TOKEN" \
         -H "Accept: application/vnd.github.v3+json" \
         "https://api.github.com$endpoint"
}

# Display repositories
display_repos() {
    local org="$1"
    local topic="$2"

    echo "Fetching repositories for org '$org' with topic '$topic'..."
    
    # Get repositories for organization with topic
    local repos
    repos=$(github_request "/search/repositories?q=org:$org+topic:$topic" | \
            jq -r '.items[] | "\(.name) | Stars: \(.stargazers_count) | \(.description)"')

    if [[ -z "$repos" ]]; then
        echo "No repositories found."
        return
    fi

    echo -e "\nFound repositories:"
    echo "===================="
    echo "$repos" | nl
}

# Main menu
main_menu() {
    while true; do
        echo -e "\nGitHub Repository Browser"
        echo "======================="
        echo "1. Search repositories"
        echo "2. Exit"
        
        read -rp "Select an option: " choice

        case $choice in
            1)
                read -rp "Enter organization name: " org
                read -rp "Enter topic: " topic
                display_repos "$org" "$topic"
                ;;
            2)
                echo "Goodbye!"
                exit 0
                ;;
            *)
                echo "Invalid option"
                ;;
        esac
    done
}

# Main execution
main() {
    check_dependencies
    check_env
    main_menu
}

main 
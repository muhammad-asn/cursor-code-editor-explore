#!/bin/bash

# Check if GitHub username is provided
if [ $# -ne 1 ]; then
    echo "Usage: $0 <github_username>"
    exit 1
fi

USERNAME=$1

# Fetch repository data using GitHub API
echo "Fetching repositories for user: $USERNAME"
echo "----------------------------------------"

# Print table header
printf "%-40s | %-20s | %-10s | %-10s\n" "Repository" "Language" "Stars" "Forks"
printf "%.0s-" {1..85}
echo

# Fetch and format repository data
curl -s "https://api.github.com/users/$USERNAME/repos" | \
    jq -r '.[] | "\(.name)\t\(.language)\t\(.stargazers_count)\t\(.forks_count)"' | \
    while IFS=$'\t' read -r name language stars forks; do
        printf "%-40s | %-20s | %-10s | %-10s\n" \
            "${name:0:40}" \
            "${language:-N/A}" \
            "${stars:-0}" \
            "${forks:-0}"
    done

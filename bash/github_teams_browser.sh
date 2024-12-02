#!/usr/bin/env bash

# GitHub Teams Browser
#
# Purpose: List GitHub teams for a specified organization and display their details
# Usage: ./github_teams_browser.sh <organization-name>
# Author: Muhammad Ardivan (muhammad.a.s.nugroho@gdplabs.id)
# Dependencies: curl, jq
# Date: 01-12-2024

# Error handling
set -euo pipefail
trap 'echo "Error: Script failed on line $LINENO"' ERR

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

# Validate environment
check_env() {
    if [[ ! -f .env ]]; then
        echo "Error: .env file not found"
        exit 1
    fi

    # Source .env file
    source .env

    if [[ -z "${GITHUB_TOKEN:-}" ]]; then
        echo "Error: GITHUB_TOKEN not set in .env file"
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

# Display teams
display_teams() {
    local org="$1"

    echo "Fetching teams for organization '$org'..."
    
    # Get teams for organization
    local teams
    teams=$(github_request "/orgs/$org/teams" | \
            jq -r '.[] | "\(.name) | Members: \(.members_count) | Privacy: \(.privacy) | Description: \(.description // "N/A")"')

    if [[ -z "$teams" ]]; then
        echo "No teams found or insufficient permissions."
        return
    fi

    echo -e "\nFound teams:"
    echo "============="
    echo "$teams" | nl
}

# Main execution
main() {
    check_dependencies
    check_env

    if [[ $# -eq 0 ]]; then
        echo "Usage: $0 <organization-name>"
        exit 1
    fi

    display_teams "$1"
}

main "$@" 
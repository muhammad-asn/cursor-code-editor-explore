# Bash Scripts Collection

This repository contains a collection of bash scripts for various automation tasks.

## Scripts

### GitHub Repository Browser
A command-line tool to browse GitHub repositories by organization and topic.

#### Features
- Search repositories by organization and topic
- Display repository details including name, stars, and description
- Interactive menu interface
- Proper error handling and dependency checking

#### Requirements
- bash (4.0 or later)
- curl
- jq
- GitHub Personal Access Token

#### Installation
1. Clone this repository
2. Make the script executable:
   ```bash
   chmod +x github_repo_browser.sh
   ```
3. Create a `.env` file with your GitHub token:
   ```bash
   GITHUB_TOKEN=your_token_here
   ```

#### Usage

Follow the interactive menu to:
1. Search repositories by entering an organization name and topic
2. View results including repository names, star counts, and descriptions
3. Exit the program

#### Error Handling
The script includes comprehensive error handling:
- Validates all required dependencies
- Checks for environment variables
- Handles API errors gracefully
- Provides cleanup on script interruption

## Development Guidelines

### Script Standards
All bash scripts in this repository must:
1. Include a standardized header with:
   - Script purpose
   - Usage instructions
   - Author information
   - Dependencies
   - Date created/modified

2. Implement proper error handling:
   - Use `set -e` for exit on error
   - Use `set -u` for undefined variables
   - Include trap commands for cleanup

3. Follow code style best practices:
   - Use shellcheck for linting
   - Use meaningful variable names
   - Include comments for complex logic
   - Implement functions for reusable code

4. Handle environment variables:
   - Document required variables
   - Provide example .env files
   - Validate variables at runtime

### Permissions
- All executable scripts must have proper permissions (`chmod +x`)
- Special permission requirements must be documented

## Contributing
1. Follow the script standards outlined above
2. Run shellcheck on your scripts before submitting
3. Update this README.md with any new script additions

## Authors
- Muhammad Ardivan (muhammad.a.s.nugroho@gdplabs.id)

## Last Updated
01-12-2024
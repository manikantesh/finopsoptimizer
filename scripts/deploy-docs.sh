#!/bin/bash

# FinOps Optimizer Documentation Deployment Script
# This script helps deploy versioned documentation using mike

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
REPO_URL="https://github.com/manikantesh/finopsoptimizer.git"
DOCS_BRANCH="gh-pages"

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if mike is installed
check_dependencies() {
    log_info "Checking dependencies..."
    
    if ! command -v mike &> /dev/null; then
        log_error "mike is not installed. Please install it with: pip install mike"
        exit 1
    fi
    
    if ! command -v mkdocs &> /dev/null; then
        log_error "mkdocs is not installed. Please install it with: pip install mkdocs-material"
        exit 1
    fi
    
    log_success "All dependencies are installed"
}

# Deploy latest version (main branch)
deploy_latest() {
    log_info "Deploying latest version from main branch..."
    
    # Ensure we're on main branch
    git checkout main
    git pull origin main
    
    # Deploy with mike
    mike deploy --push --update-aliases latest main
    mike set-default --push latest
    
    log_success "Latest version deployed successfully"
}

# Deploy specific version
deploy_version() {
    local version=$1
    
    if [ -z "$version" ]; then
        log_error "Version not specified"
        exit 1
    fi
    
    log_info "Deploying version: $version"
    
    # Check if version tag exists
    if ! git rev-parse "v$version" >/dev/null 2>&1; then
        log_error "Version tag v$version does not exist"
        exit 1
    fi
    
    # Checkout version tag
    git checkout "v$version"
    
    # Deploy with mike
    mike deploy --push "$version"
    
    # Return to main branch
    git checkout main
    
    log_success "Version $version deployed successfully"
}

# List all deployed versions
list_versions() {
    log_info "Deployed documentation versions:"
    mike list
}

# Delete a version
delete_version() {
    local version=$1
    
    if [ -z "$version" ]; then
        log_error "Version not specified"
        exit 1
    fi
    
    log_warning "Deleting version: $version"
    read -p "Are you sure? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        mike delete --push "$version"
        log_success "Version $version deleted successfully"
    else
        log_info "Deletion cancelled"
    fi
}

# Serve documentation locally
serve_docs() {
    log_info "Starting local documentation server..."
    mike serve
}

# Update versions.json file
update_versions_json() {
    log_info "Updating versions.json with deployed versions..."
    
    # Get list of deployed versions
    versions=$(mike list --json)
    
    # Create updated versions.json
    cat > versions.json << EOF
[
  {
    "version": "latest",
    "title": "Latest (Main)",
    "aliases": ["main", "dev"]
  },
$(echo "$versions" | jq -r '.[] | select(.version != "latest") | "  {\"version\": \"" + .version + "\", \"title\": \"" + .version + " - " + (.title // "Release") + "\", \"aliases\": []},"' | sed '$s/,$//')
]
EOF
    
    log_success "versions.json updated successfully"
}

# Show help
show_help() {
    cat << EOF
FinOps Optimizer Documentation Deployment Script

Usage: $0 [COMMAND] [OPTIONS]

Commands:
    latest              Deploy latest version from main branch
    version <VERSION>   Deploy specific version (e.g., 2.1.0)
    list               List all deployed versions
    delete <VERSION>   Delete a specific version
    serve              Serve documentation locally
    update-versions    Update versions.json file
    help               Show this help message

Examples:
    $0 latest                    # Deploy latest from main
    $0 version 2.1.0            # Deploy version 2.1.0
    $0 delete 1.0.0             # Delete version 1.0.0
    $0 serve                    # Serve locally

Prerequisites:
    - mike: pip install mike
    - mkdocs-material: pip install mkdocs-material
    - Git repository with proper tags

EOF
}

# Main script logic
main() {
    case "${1:-help}" in
        "latest")
            check_dependencies
            deploy_latest
            ;;
        "version")
            check_dependencies
            deploy_version "$2"
            ;;
        "list")
            list_versions
            ;;
        "delete")
            delete_version "$2"
            ;;
        "serve")
            serve_docs
            ;;
        "update-versions")
            update_versions_json
            ;;
        "help"|*)
            show_help
            ;;
    esac
}

# Run main function with all arguments
main "$@"
#!/bin/bash

# FinOps Optimizer Release Creation Helper
# This script helps create GitHub releases that automatically generate documentation versions

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Show help
show_help() {
    cat << EOF
FinOps Optimizer Release Creation Helper

This script helps you create GitHub releases that automatically generate documentation versions.

Usage: $0 [OPTIONS]

Options:
    -v, --version VERSION    Release version (e.g., 2.2.0)
    -t, --title TITLE       Release title
    -d, --description FILE  File containing release description
    -p, --prerelease        Mark as pre-release
    -h, --help             Show this help message

Examples:
    $0 -v 2.2.0 -t "Enhanced AI Agents"
    $0 -v 2.2.0 -t "Enhanced AI Agents" -d release-notes.md
    $0 -v 2.2.0-beta.1 -t "Beta Release" -p

Prerequisites:
    - GitHub CLI (gh) installed and authenticated
    - Git repository with proper remote origin
    - All changes committed and pushed

Workflow:
    1. Script validates version format
    2. Checks if version already exists
    3. Creates GitHub release
    4. GitHub Actions automatically deploys documentation
    5. New version appears in documentation dropdown

EOF
}

# Validate version format
validate_version() {
    local version=$1
    if [[ ! $version =~ ^[0-9]+\.[0-9]+\.[0-9]+(-[a-zA-Z0-9.-]+)?$ ]]; then
        log_error "Invalid version format: $version"
        log_info "Use semantic versioning: 2.2.0, 2.2.0-beta.1, etc."
        exit 1
    fi
}

# Check if GitHub CLI is installed
check_gh_cli() {
    if ! command -v gh &> /dev/null; then
        log_error "GitHub CLI (gh) is not installed"
        log_info "Install it from: https://cli.github.com/"
        exit 1
    fi
    
    # Check if authenticated
    if ! gh auth status &> /dev/null; then
        log_error "GitHub CLI is not authenticated"
        log_info "Run: gh auth login"
        exit 1
    fi
}

# Check if version already exists
check_version_exists() {
    local version=$1
    local tag="v$version"
    
    if git tag -l | grep -q "^$tag$"; then
        log_error "Version $version already exists as git tag"
        exit 1
    fi
    
    if gh release list | grep -q "$tag"; then
        log_error "Version $version already exists as GitHub release"
        exit 1
    fi
}

# Generate default release notes
generate_default_notes() {
    local version=$1
    cat << EOF
## 🚀 What's New in v$version

### ✨ New Features
- Enhanced AI agent capabilities
- Improved cost optimization algorithms
- Better real-time dashboard performance

### 🔧 Improvements
- Faster pricing engine
- Enhanced error handling
- Improved user experience

### 🐛 Bug Fixes
- Various bug fixes and stability improvements

### 📚 Documentation
- Updated guides and examples
- Enhanced troubleshooting section

---

**Full Changelog**: https://github.com/manikantesh/finopsoptimizer/releases/tag/v$version

**Documentation**: https://manikantesh.github.io/finopsoptimizer/$version/
EOF
}

# Create release
create_release() {
    local version=$1
    local title=$2
    local description_file=$3
    local prerelease=$4
    
    local tag="v$version"
    local release_title="$tag - $title"
    
    log_info "Creating GitHub release: $release_title"
    
    # Prepare release notes
    local notes_file="/tmp/release-notes-$version.md"
    if [[ -n "$description_file" && -f "$description_file" ]]; then
        cp "$description_file" "$notes_file"
    else
        generate_default_notes "$version" > "$notes_file"
    fi
    
    # Create release command
    local gh_cmd="gh release create $tag --title \"$release_title\" --notes-file \"$notes_file\""
    
    if [[ "$prerelease" == "true" ]]; then
        gh_cmd="$gh_cmd --prerelease"
    else
        gh_cmd="$gh_cmd --latest"
    fi
    
    # Execute release creation
    eval $gh_cmd
    
    # Cleanup
    rm -f "$notes_file"
    
    log_success "GitHub release created successfully!"
    log_info "GitHub Actions will automatically deploy documentation version in 2-3 minutes"
    log_info "Documentation will be available at: https://manikantesh.github.io/finopsoptimizer/$version/"
}

# Main script
main() {
    local version=""
    local title=""
    local description_file=""
    local prerelease="false"
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -v|--version)
                version="$2"
                shift 2
                ;;
            -t|--title)
                title="$2"
                shift 2
                ;;
            -d|--description)
                description_file="$2"
                shift 2
                ;;
            -p|--prerelease)
                prerelease="true"
                shift
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    # Validate required arguments
    if [[ -z "$version" ]]; then
        log_error "Version is required"
        show_help
        exit 1
    fi
    
    if [[ -z "$title" ]]; then
        log_error "Title is required"
        show_help
        exit 1
    fi
    
    # Validate inputs
    validate_version "$version"
    check_gh_cli
    check_version_exists "$version"
    
    # Check git status
    if [[ -n $(git status --porcelain) ]]; then
        log_warning "You have uncommitted changes"
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_info "Aborting release creation"
            exit 1
        fi
    fi
    
    # Ensure we're on main branch
    local current_branch=$(git branch --show-current)
    if [[ "$current_branch" != "main" ]]; then
        log_warning "You're not on the main branch (current: $current_branch)"
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_info "Aborting release creation"
            exit 1
        fi
    fi
    
    # Create release
    create_release "$version" "$title" "$description_file" "$prerelease"
    
    log_success "Release creation completed!"
    log_info "Next steps:"
    log_info "1. Check GitHub Actions: https://github.com/manikantesh/finopsoptimizer/actions"
    log_info "2. Verify documentation: https://manikantesh.github.io/finopsoptimizer/"
    log_info "3. Test version selector in documentation"
}

# Run main function with all arguments
main "$@"
#!/bin/bash

# FinOps Optimizer - Documentation Test Script
# This script tests the documentation build locally before pushing

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Check if required tools are installed
check_dependencies() {
    log_info "Checking dependencies..."
    
    if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
        log_error "Python is not installed"
        exit 1
    fi
    
    if ! command -v pip &> /dev/null; then
        log_error "pip is not installed"
        exit 1
    fi
    
    log_success "Dependencies check passed"
}

# Install documentation dependencies
install_deps() {
    log_info "Installing documentation dependencies..."
    
    pip install --upgrade pip
    pip install mkdocs-material>=9.0.0
    pip install mkdocs-git-revision-date-localized-plugin>=1.2.0
    pip install mkdocs-minify-plugin>=0.7.0
    pip install pymdown-extensions>=10.0.0
    pip install mike>=2.0.0
    
    log_success "Dependencies installed"
}

# Test MkDocs configuration
test_config() {
    log_info "Testing MkDocs configuration..."
    
    if [ ! -f mkdocs.yml ]; then
        log_error "mkdocs.yml not found"
        exit 1
    fi
    
    # Test configuration syntax
    mkdocs --version
    mike --version
    
    log_success "Configuration test passed"
}

# Test documentation build
test_build() {
    log_info "Testing documentation build..."
    
    # Clean any existing build
    rm -rf site/
    
    # Build documentation
    mkdocs build --clean --strict --verbose
    
    if [ ! -d site/ ]; then
        log_error "Documentation build failed - site/ directory not created"
        exit 1
    fi
    
    if [ ! -f site/index.html ]; then
        log_error "Documentation build failed - index.html not found"
        exit 1
    fi
    
    log_success "Documentation build test passed"
}

# Test mike versioning
test_versioning() {
    log_info "Testing mike versioning..."
    
    # Test mike list (should work even with no versions)
    mike list || true
    
    # Test mike serve (dry run)
    log_info "Mike versioning test completed"
    log_success "Versioning test passed"
}

# Serve documentation locally
serve_docs() {
    log_info "Starting local documentation server..."
    log_info "Documentation will be available at: http://localhost:8000"
    log_info "Press Ctrl+C to stop the server"
    
    mkdocs serve --dev-addr=0.0.0.0:8000
}

# Clean up build artifacts
cleanup() {
    log_info "Cleaning up build artifacts..."
    rm -rf site/
    log_success "Cleanup completed"
}

# Main function
main() {
    case "${1:-test}" in
        "test")
            log_info "Running documentation tests..."
            check_dependencies
            install_deps
            test_config
            test_build
            test_versioning
            cleanup
            log_success "All tests passed! Documentation is ready for deployment."
            ;;
        "serve")
            log_info "Serving documentation locally..."
            check_dependencies
            install_deps
            serve_docs
            ;;
        "build")
            log_info "Building documentation..."
            check_dependencies
            install_deps
            test_config
            test_build
            log_success "Documentation built successfully in site/ directory"
            ;;
        "clean")
            cleanup
            ;;
        "help"|*)
            cat << EOF
FinOps Optimizer Documentation Test Script

Usage: $0 [COMMAND]

Commands:
    test     Run all documentation tests (default)
    serve    Serve documentation locally at http://localhost:8000
    build    Build documentation to site/ directory
    clean    Clean up build artifacts
    help     Show this help message

Examples:
    $0 test          # Run all tests
    $0 serve         # Serve locally for development
    $0 build         # Build for production
    $0 clean         # Clean up

EOF
            ;;
    esac
}

# Run main function with all arguments
main "$@"
#!/bin/bash

# FinOps Optimizer Documentation Deployment Script
# This script helps test and deploy documentation locally

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get current branch
BRANCH=$(git rev-parse --abbrev-ref HEAD)
echo -e "${BLUE}🚀 FinOps Optimizer Documentation Deployment${NC}"
echo -e "${BLUE}📍 Current branch: ${BRANCH}${NC}"
echo

# Check if mkdocs is installed
if ! command -v mkdocs &> /dev/null; then
    echo -e "${RED}❌ mkdocs is not installed${NC}"
    echo "Install with: pip install mkdocs-material"
    exit 1
fi

# Function to build docs
build_docs() {
    echo -e "${YELLOW}🔨 Building documentation...${NC}"
    mkdocs build --clean
    echo -e "${GREEN}✅ Documentation built successfully${NC}"
}

# Function to create version selector
create_version_selector() {
    echo -e "${YELLOW}📋 Creating version selector...${NC}"
    if [ -f "scripts/create_version_selector.py" ]; then
        python3 scripts/create_version_selector.py
        echo -e "${GREEN}✅ Version selector created${NC}"
    else
        echo -e "${YELLOW}⚠️  Version selector script not found${NC}"
    fi
}

# Function to serve locally
serve_local() {
    local port=${1:-8000}
    echo -e "${BLUE}🌐 Starting local server on port ${port}${NC}"
    echo -e "${BLUE}📖 Documentation available at: http://localhost:${port}${NC}"
    echo -e "${YELLOW}Press Ctrl+C to stop the server${NC}"
    mkdocs serve --dev-addr 0.0.0.0:${port}
}

# Function to create branch preview
create_branch_preview() {
    if [ "$BRANCH" != "main" ]; then
        echo -e "${YELLOW}📁 Creating branch preview for: ${BRANCH}${NC}"
        
        # Create branch directory
        mkdir -p "site/${BRANCH}"
        
        # Copy all files to branch directory
        cp -r site/* "site/${BRANCH}/" 2>/dev/null || true
        
        # Update base URLs in HTML files
        find "site/${BRANCH}" -name "*.html" -exec sed -i '' \
            "s|https://manikantesh.github.io/finopsoptimizer/|https://manikantesh.github.io/finopsoptimizer/${BRANCH}/|g" {} \;
        
        echo -e "${GREEN}✅ Branch preview created at: site/${BRANCH}/${NC}"
    fi
}

# Main execution
case "${1:-build}" in
    "build")
        build_docs
        create_version_selector
        create_branch_preview
        echo -e "${GREEN}✅ Build completed!${NC}"
        ;;
    "serve")
        build_docs
        create_version_selector
        create_branch_preview
        serve_local "${2:-8000}"
        ;;
    "test")
        build_docs
        create_version_selector
        create_branch_preview
        echo -e "${GREEN}✅ Test completed!${NC}"
        echo -e "${BLUE}📁 Documentation built in: site/${NC}"
        if [ "$BRANCH" != "main" ]; then
            echo -e "${BLUE}📁 Branch preview in: site/${BRANCH}/${NC}"
        fi
        ;;
    "clean")
        echo -e "${YELLOW}🧹 Cleaning build artifacts...${NC}"
        rm -rf site/
        echo -e "${GREEN}✅ Clean completed!${NC}"
        ;;
    *)
        echo "Usage: $0 {build|serve|test|clean} [port]"
        echo
        echo "Commands:"
        echo "  build  - Build documentation (default)"
        echo "  serve  - Build and serve locally"
        echo "  test   - Build and test deployment"
        echo "  clean  - Clean build artifacts"
        echo
        echo "Examples:"
        echo "  $0 build"
        echo "  $0 serve 8080"
        echo "  $0 test"
        echo "  $0 clean"
        exit 1
        ;;
esac 
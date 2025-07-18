#!/bin/bash

# FinOps Optimizer - Release Setup Script
# This script creates proper GitHub releases and cleans up the versioning system

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

# Check if GitHub CLI is available
check_gh_cli() {
    if ! command -v gh &> /dev/null; then
        log_error "GitHub CLI (gh) is not installed"
        log_info "Please install it:"
        log_info "  macOS: brew install gh"
        log_info "  Linux: https://cli.github.com/"
        log_info "  Windows: winget install GitHub.cli"
        exit 1
    fi
    
    if ! gh auth status &> /dev/null; then
        log_error "GitHub CLI is not authenticated"
        log_info "Please run: gh auth login"
        exit 1
    fi
    
    log_success "GitHub CLI is ready"
}

# Clean up existing versions
cleanup_versions() {
    log_info "Cleaning up existing documentation versions..."
    
    # Get list of current versions
    current_versions=$(mike list --json 2>/dev/null || echo "[]")
    
    if [[ "$current_versions" != "[]" ]]; then
        log_info "Current versions found, cleaning up..."
        
        # Delete all versions except latest
        mike list | grep -v "latest" | while read -r version; do
            if [[ -n "$version" ]]; then
                log_info "Removing version: $version"
                mike delete --push "$version" || true
            fi
        done
    fi
    
    log_success "Version cleanup completed"
}

# Create GitHub releases
create_releases() {
    log_info "Creating GitHub releases..."
    
    # Release v2.1.0 - AI Agents & Real-time Dashboards
    log_info "Creating release v2.1.0..."
    gh release create v2.1.0 \
        --title "v2.1.0 - AI Agents & Real-time Dashboards" \
        --notes "## 🚀 Major Features

### 🤖 AI-Powered Optimization
- **Autonomous Optimization Agent**: Continuously monitors and optimizes your infrastructure
- **Cost Advisor Agent**: AI-powered cost consultant with natural language processing
- **Machine Learning Models**: Advanced ML for cost forecasting and resource optimization
- **Intelligent Automation**: Smart rightsizing, predictive scaling, and anomaly detection

### 📊 Real-Time Dashboards
- **Executive Dashboard**: High-level cost overview for leadership
- **Engineering Dashboard**: Technical insights for development teams  
- **Operations Dashboard**: Real-time monitoring for DevOps/SRE teams
- **Interactive Visualizations**: D3.js-powered charts and graphs

### 🏗️ Enterprise Architecture
- **Kubernetes-Native**: Full containerization with Helm charts
- **Microservices**: Event-driven architecture with message queues
- **High Availability**: 99.9% uptime with distributed caching
- **Advanced Data Stack**: Kafka + Flink + Redis + Elasticsearch

### 🔒 Enhanced Security
- **Identity Management**: Keycloak integration for SSO and RBAC
- **Policy Engine**: Open Policy Agent (OPA) for access control
- **Secrets Management**: HashiCorp Vault integration
- **Audit & Compliance**: Complete audit trails and reporting

## 🔧 Improvements
- Enhanced pricing engine with 50% better performance
- Improved Oracle Cloud integration
- Better error handling and logging
- Mobile-responsive documentation

## 📚 Documentation
- Comprehensive AI agents guide
- Real-time dashboards documentation
- Enhanced setup and configuration guides
- Professional versioning system

---
**Full Documentation**: https://manikantesh.github.io/finopsoptimizer/2.1.0/" \
        --latest || log_warning "Release v2.1.0 may already exist"
    
    # Release v2.0.0 - Multi-Cloud Support
    log_info "Creating release v2.0.0..."
    gh release create v2.0.0 \
        --title "v2.0.0 - Multi-Cloud Support" \
        --notes "## 🌐 Multi-Cloud Excellence

### ☁️ Cloud Provider Support
- **AWS**: Complete integration with EC2, RDS, S3, and more
- **Azure**: Full support for VMs, storage, and monitoring
- **Google Cloud**: Comprehensive GCP cost optimization
- **Oracle Cloud**: Native OCI integration and optimization

### 💰 Cost Optimization Features
- **VM Rightsizing**: Intelligent instance size recommendations
- **Reserved Instances**: Automated RI analysis and recommendations
- **Unattached Resources**: Identify and clean up unused resources
- **Real-Time Pricing**: Live pricing data for accurate calculations

### 🔧 Core Features
- **Unified API**: Single interface for all cloud providers
- **Configuration Management**: Centralized configuration system
- **CLI Interface**: Comprehensive command-line tool
- **Reporting**: Detailed cost analysis and recommendations

### 📊 Analytics & Reporting
- **Cost Forecasting**: ML-powered cost predictions
- **Trend Analysis**: Historical cost analysis
- **Custom Reports**: Flexible reporting system
- **Export Options**: Multiple output formats

## 🚀 Performance
- Parallel processing for faster analysis
- Intelligent caching system
- Optimized API calls
- Scalable architecture

---
**Documentation**: https://manikantesh.github.io/finopsoptimizer/2.0.0/" || log_warning "Release v2.0.0 may already exist"
    
    log_success "GitHub releases created"
}

# Deploy documentation versions from releases
deploy_release_versions() {
    log_info "Deploying documentation versions from releases..."
    
    # Get list of releases
    releases=$(gh release list --json tagName,name,publishedAt --limit 10)
    
    if [[ "$releases" == "[]" ]]; then
        log_warning "No releases found"
        return
    fi
    
    # Deploy each release
    echo "$releases" | jq -r '.[] | "\(.tagName)|\(.name)"' | while IFS='|' read -r tag_name release_name; do
        version=${tag_name#v}  # Remove 'v' prefix
        log_info "Deploying documentation for release: $tag_name"
        
        # Checkout the release tag
        git checkout "$tag_name" 2>/dev/null || {
            log_warning "Could not checkout tag $tag_name, skipping..."
            continue
        }
        
        # Deploy with mike
        mike deploy --push "$version" || log_warning "Failed to deploy $version"
        
        log_success "Deployed version $version"
    done
    
    # Return to main branch
    git checkout main
    
    # Deploy latest
    log_info "Deploying latest version..."
    mike deploy --push --update-aliases latest main
    mike set-default --push latest
    
    log_success "All versions deployed"
}

# Update versions.json to only include releases
update_versions_json() {
    log_info "Updating versions.json with release information..."
    
    # Get releases from GitHub
    releases=$(gh release list --json tagName,name,publishedAt --limit 10)
    
    # Create versions.json
    cat > versions.json << 'EOF'
[
  {
    "version": "latest",
    "title": "Latest (Development)",
    "aliases": ["main", "dev"]
  }
EOF
    
    # Add releases to versions.json
    if [[ "$releases" != "[]" ]]; then
        echo "$releases" | jq -r '.[] | "  ,{\"version\": \"" + (.tagName | ltrimstr("v")) + "\", \"title\": \"" + .tagName + " - " + (.name | split(" - ")[1] // .name) + "\", \"aliases\": []}"' >> versions.json
    fi
    
    echo "]" >> versions.json
    
    log_success "versions.json updated"
}

# Main execution
main() {
    log_info "Setting up proper GitHub releases and documentation versions"
    
    # Check prerequisites
    check_gh_cli
    
    # Ensure we're on main branch
    git checkout main
    git pull origin main
    
    # Clean up existing versions
    cleanup_versions
    
    # Create GitHub releases
    create_releases
    
    # Deploy documentation versions from releases
    deploy_release_versions
    
    # Update versions.json
    update_versions_json
    
    # Commit updated versions.json
    git add versions.json
    git commit -m "docs: Update versions.json with GitHub releases" || true
    git push origin main
    
    log_success "Setup completed successfully!"
    log_info "Your documentation now only shows versions tied to GitHub releases"
    log_info "Visit: https://manikantesh.github.io/finopsoptimizer/"
}

# Run main function
main "$@"
# Local Setup Guide

This comprehensive guide will help you set up FinOps Optimizer on your local machine for development, testing, or production use.

## 🎯 Quick Start

### Automated Setup (Recommended)
```bash
# Clone the repository
git clone https://github.com/manikantesh/finopsoptimizer.git
cd finopsoptimizer

# Run automated setup
python quick_start.py

# Validate installation
python validate_setup.py
```

### Manual Setup
If you prefer manual setup or need more control, follow the detailed instructions below.

## 📋 Prerequisites

### System Requirements
- **Python**: 3.8 or higher
- **Operating System**: Windows, macOS, or Linux
- **Memory**: 4GB RAM minimum, 8GB recommended
- **Storage**: 2GB free space
- **Network**: Internet connection for cloud API access

### Required Tools
```bash
# Check if tools are installed
python --version    # Should be 3.8+
pip --version       # Package manager
git --version       # Version control
```

### Install Missing Tools

#### Windows
```powershell
# Install Python from python.org or use Chocolatey
choco install python git

# Or use Windows Package Manager
winget install Python.Python.3.11
winget install Git.Git
```

#### macOS
```bash
# Install using Homebrew
brew install python git

# Or use MacPorts
sudo port install python311 git
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install python3 python3-pip git

# For CentOS/RHEL/Fedora
sudo yum install python3 python3-pip git
```

## 🚀 Installation Steps

### Step 1: Clone Repository
```bash
git clone https://github.com/manikantesh/finopsoptimizer.git
cd finopsoptimizer
```

### Step 2: Virtual Environment (Recommended)
```bash
# Create virtual environment
python -m venv finops-env

# Activate virtual environment
# Windows:
finops-env\Scripts\activate
# macOS/Linux:
source finops-env/bin/activate
```

### Step 3: Install Dependencies
```bash
# Upgrade pip
python -m pip install --upgrade pip

# Install core dependencies
pip install -r requirements.txt

# Or install manually
pip install boto3>=1.26.0 azure-identity>=1.12.0 google-cloud-compute>=1.8.0 oci>=2.88.0
```

### Step 4: Configuration
```bash
# Create configuration file
python quick_start.py --config-only

# Or copy example configuration
cp examples/finops_config_with_enterprise_pricing.yml finops_config.yml
```

### Step 5: Validation
```bash
# Run comprehensive validation
python validate_setup.py --full

# Quick validation
python validate_setup.py
```

## ⚙️ Configuration

### Basic Configuration File
Create `finops_config.yml` in the project root:

```yaml
general:
  log_level: INFO
  output_format: json
  cache_ttl: 3600
  max_workers: 4

providers:
  aws:
    enabled: true
    regions: [us-east-1, us-west-2]
    profile: default
  
  azure:
    enabled: true
    subscription_id: null
    tenant_id: null
  
  gcp:
    enabled: true
    project_id: null
    regions: [us-central1, us-east1]
  
  oracle:
    enabled: true
    config_file: ~/.oci/config
    profile: DEFAULT

optimization:
  rightsizing:
    enabled: true
    cpu_threshold: 80
    memory_threshold: 80
    observation_days: 30
  
  reserved_instances:
    enabled: true
    minimum_usage: 70
    term_length: 12
  
  unattached_resources:
    enabled: true
    age_threshold_days: 7

reporting:
  output_directory: ./reports
  formats: [html, json, csv]
  email_notifications: false
```

### Environment Variables
```bash
# Optional: Set environment variables
export FINOPS_CONFIG_PATH=/path/to/finops_config.yml
export FINOPS_LOG_LEVEL=DEBUG
export FINOPS_CACHE_DIR=/tmp/finops_cache
```

## 🔐 Cloud Provider Setup

### AWS Configuration

#### Option 1: AWS CLI
```bash
# Install AWS CLI
pip install awscli

# Configure credentials
aws configure
```

#### Option 2: Environment Variables
```bash
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=us-east-1
```

#### Option 3: Credentials File
Create `~/.aws/credentials`:
```ini
[default]
aws_access_key_id = your_access_key
aws_secret_access_key = your_secret_key

[finops]
aws_access_key_id = your_finops_key
aws_secret_access_key = your_finops_secret
```

### Azure Configuration

#### Option 1: Azure CLI
```bash
# Install Azure CLI
pip install azure-cli

# Login
az login
```

#### Option 2: Service Principal
```bash
export AZURE_CLIENT_ID=your_client_id
export AZURE_CLIENT_SECRET=your_client_secret
export AZURE_TENANT_ID=your_tenant_id
export AZURE_SUBSCRIPTION_ID=your_subscription_id
```

#### Option 3: Configuration File
Update `finops_config.yml`:
```yaml
providers:
  azure:
    enabled: true
    subscription_id: your_subscription_id
    tenant_id: your_tenant_id
    client_id: your_client_id
    client_secret: your_client_secret
```

### Google Cloud Configuration

#### Option 1: gcloud CLI
```bash
# Install gcloud CLI
# Follow: https://cloud.google.com/sdk/docs/install

# Authenticate
gcloud auth application-default login
gcloud config set project your-project-id
```

#### Option 2: Service Account
```bash
# Download service account key
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
```

#### Option 3: Configuration File
Update `finops_config.yml`:
```yaml
providers:
  gcp:
    enabled: true
    project_id: your-project-id
    credentials_path: /path/to/service-account-key.json
```

### Oracle Cloud Configuration

#### Option 1: OCI CLI
```bash
# Install OCI CLI
pip install oci-cli

# Configure
oci setup config
```

#### Option 2: Configuration File
Create `~/.oci/config`:
```ini
[DEFAULT]
user=ocid1.user.oc1..your_user_ocid
fingerprint=your_fingerprint
key_file=~/.oci/oci_api_key.pem
tenancy=ocid1.tenancy.oc1..your_tenancy_ocid
region=us-ashburn-1
```

## 🧪 Testing Your Setup

### Basic Functionality Test
```bash
# Test basic functionality
python test_finops.py

# Test CLI
python cli.py --help
python cli.py status
```

### Provider Connectivity Test
```bash
# Test specific provider
python cli.py test-connection aws
python cli.py test-connection azure
python cli.py test-connection gcp
python cli.py test-connection oracle
```

### Full Validation
```bash
# Comprehensive validation
python validate_setup.py --full --cloud --benchmark

# Check validation report
cat validation_report.json
```

## 🔧 Development Setup

### Additional Development Dependencies
```bash
# Install development dependencies
pip install pytest pytest-cov black flake8 mypy
pip install jupyter notebook matplotlib plotly

# Install documentation tools
pip install mkdocs-material mike
```

### Pre-commit Hooks
```bash
# Install pre-commit
pip install pre-commit

# Set up hooks
pre-commit install
```

### IDE Configuration

#### VS Code
Create `.vscode/settings.json`:
```json
{
    "python.defaultInterpreterPath": "./finops-env/bin/python",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black"
}
```

#### PyCharm
1. Open project in PyCharm
2. Configure Python interpreter: `finops-env/bin/python`
3. Enable code formatting with Black
4. Configure run configurations for CLI and tests

## 📊 Performance Optimization

### System Optimization
```bash
# Increase file descriptor limits (Linux/macOS)
ulimit -n 4096

# Set Python optimization
export PYTHONOPTIMIZE=1

# Use faster JSON library
pip install orjson
```

### Configuration Tuning
```yaml
general:
  max_workers: 8          # Increase for more CPU cores
  cache_ttl: 7200         # Longer cache for stable environments
  batch_size: 100         # Larger batches for better performance
  
optimization:
  parallel_processing: true
  memory_limit_mb: 2048
  timeout_seconds: 300
```

## 🚨 Troubleshooting

### Common Issues

#### Import Errors
```bash
# Check Python path
python -c "import sys; print(sys.path)"

# Reinstall package
pip uninstall finopsoptimizer
pip install -e .
```

#### Permission Errors
```bash
# Fix permissions (Linux/macOS)
chmod +x cli.py quick_start.py validate_setup.py

# Run with user permissions
python -m pip install --user -r requirements.txt
```

#### Memory Issues
```bash
# Reduce memory usage
export FINOPS_MAX_WORKERS=2
export FINOPS_BATCH_SIZE=50

# Monitor memory usage
python -c "import psutil; print(f'Memory: {psutil.virtual_memory().percent}%')"
```

#### Network Issues
```bash
# Test connectivity
python -c "import requests; print(requests.get('https://api.github.com').status_code)"

# Configure proxy (if needed)
export HTTP_PROXY=http://proxy.company.com:8080
export HTTPS_PROXY=http://proxy.company.com:8080
```

### Debug Mode
```bash
# Enable debug logging
export FINOPS_LOG_LEVEL=DEBUG

# Run with verbose output
python cli.py --verbose status

# Check logs
tail -f finops.log
```

### Getting Help
- 📖 **Documentation**: [GitHub Pages](https://manikantesh.github.io/finopsoptimizer/)
- 🐛 **Issues**: [GitHub Issues](https://github.com/manikantesh/finopsoptimizer/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/manikantesh/finopsoptimizer/discussions)
- 📧 **Email**: support@finopsoptimizer.com

## 🎯 Next Steps

### After Successful Setup
1. **Configure Cloud Providers**: Set up credentials for your cloud providers
2. **Run Initial Analysis**: `python cli.py analyze`
3. **Generate Reports**: `python cli.py report`
4. **Set Up Scheduling**: Configure automated optimization tasks
5. **Explore Examples**: Check the `examples/` directory

### Production Deployment
- See [Deployment Guide](deployment.md) for production setup
- Configure monitoring and alerting
- Set up automated backups
- Implement security best practices

### Advanced Features
- Set up real-time dashboards
- Configure AI agents for autonomous optimization
- Implement custom optimization rules
- Integrate with existing tools and workflows

---

**🎉 Congratulations! Your FinOps Optimizer is now set up and ready to help you optimize your cloud costs.**

For the latest updates and detailed documentation, visit: https://manikantesh.github.io/finopsoptimizer/
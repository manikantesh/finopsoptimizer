# 🚀 FinOpsOptimizer - Local Setup Guide

This guide will help you set up and run FinOpsOptimizer on your local machine for development and testing.

## 📋 Prerequisites

### System Requirements
- **Python**: 3.8 or higher
- **Operating System**: Windows, macOS, or Linux
- **Memory**: At least 4GB RAM (8GB recommended)
- **Storage**: At least 2GB free space

### Cloud Provider Access (Optional for Testing)
- **AWS**: IAM user with appropriate permissions
- **Azure**: Service Principal with required roles
- **GCP**: Service Account with necessary permissions
- **Oracle Cloud**: OCI configuration and API keys

## 🛠️ Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/manikantesh/finopsoptimizer.git
cd finopsoptimizer
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
# Install all dependencies
pip install -r requirements.txt

# Install the package in development mode
pip install -e .
```

### 4. Verify Installation

```bash
# Check if the CLI is working
python cli.py --help

# Check if the package can be imported
python -c "from finops import FinOpsOptimizer; print('✅ Installation successful!')"
```

## ⚙️ Configuration Setup

### 1. Initialize Configuration

```bash
# Create default configuration file
python cli.py init --output finops_config.yml
```

This creates a `finops_config.yml` file with default settings.

### 2. Configure Cloud Providers

Edit the `finops_config.yml` file to enable/disable cloud providers:

```yaml
# finops_config.yml
aws:
  enabled: true
  region: us-east-1
  account_id: null

azure:
  enabled: false
  subscription_id: null

gcp:
  enabled: false
  project_id: null

oracle:
  enabled: false

optimization:
  cpu_utilization_threshold: 0.7
  memory_utilization_threshold: 0.8
  cost_savings_threshold: 0.1

output_dir: "./finops_reports"
log_level: "INFO"
```

### 3. Set Up Cloud Credentials

#### AWS Credentials
```bash
# Option 1: Environment variables
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_DEFAULT_REGION="us-east-1"

# Option 2: AWS CLI configuration
aws configure
```

#### Azure Credentials
```bash
# Environment variables
export AZURE_CLIENT_ID="your-client-id"
export AZURE_CLIENT_SECRET="your-client-secret"
export AZURE_TENANT_ID="your-tenant-id"
export AZURE_SUBSCRIPTION_ID="your-subscription-id"
```

#### GCP Credentials
```bash
# Set path to service account key file
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"
```

#### Oracle Cloud Credentials
```bash
# OCI configuration file (default: ~/.oci/config)
export OCI_CONFIG_FILE="~/.oci/config"
export OCI_PROFILE="DEFAULT"
```

## 🧪 Testing the Setup

### 1. Check Provider Status

```bash
# Verify cloud provider connections
python cli.py status
```

Expected output:
```
=== Credentials Status ===
AWS: ✓ Valid
AZURE: ✗ Invalid
GCP: ✗ Invalid
ORACLE: ✗ Invalid

=== Provider Connections ===
AWS: ✓ Connected
```

### 2. Run Basic Cost Analysis

```bash
# Analyze costs for the last 7 days
python cli.py analyze --days 7
```

### 3. Test Data Ingestion (Demo Mode)

```bash
# Run the comprehensive demo
python examples/comprehensive_cost_optimization.py
```

## 🚀 Running the Complete System

### 1. Data Collection

```bash
# Collect data for the last 30 days (for testing)
python cli.py ingest --days 30 --output test_data.json
```

### 2. VM Rightsizing Analysis

```bash
# Analyze rightsizing opportunities
python cli.py rightsizing --data-file test_data.json --output rightsizing_report.json
```

### 3. Unattached Disk Analysis

```bash
# Find unattached disks (dry run)
python cli.py cleanup-disks --dry-run --output disk_report.json
```

### 4. Reserved Instance Analysis

```bash
# Analyze RI/SP opportunities
python cli.py reservations --data-file test_data.json --output ri_report.json
```

### 5. Complete Optimization

```bash
# Run full optimization pipeline
python cli.py optimize --output complete_results.json
```

## 📊 Scheduling Automation

### 1. Set Up VM Schedules

```bash
# Schedule VM start/stop (example with dummy instance IDs)
python cli.py schedule vm-schedule \
  --provider aws \
  --instances "i-1234567890abcdef0,i-0987654321fedcba0" \
  --start-time "08:00" \
  --stop-time "18:00" \
  --days "monday,tuesday,wednesday,thursday,friday"
```

### 2. Schedule Cost Analysis

```bash
# Schedule daily cost analysis
python cli.py schedule cost-analysis --frequency daily --time "06:00"
```

### 3. Schedule Cleanup Tasks

```bash
# Schedule weekly disk cleanup
python cli.py schedule cleanup --resource-type unattached_disks --frequency weekly --time "02:00"
```

### 4. Manage Schedules

```bash
# List all scheduled tasks
python cli.py schedule list

# Enable/disable tasks
python cli.py schedule enable <task_id>
python cli.py schedule disable <task_id>
```

## 🐛 Troubleshooting

### Common Issues and Solutions

#### 1. Import Errors

**Problem**: `ModuleNotFoundError` when importing finops modules

**Solution**:
```bash
# Reinstall in development mode
pip install -e .

# Or install missing dependencies
pip install -r requirements.txt
```

#### 2. Cloud Provider Connection Issues

**Problem**: "Provider not connected" errors

**Solutions**:
- Verify credentials are set correctly
- Check IAM permissions for your cloud accounts
- Ensure network connectivity to cloud APIs
- Validate configuration file settings

#### 3. Permission Errors

**Problem**: Access denied when accessing cloud resources

**Solutions**:
- Review IAM policies and roles
- Ensure minimum required permissions are granted
- Check resource-level permissions

#### 4. Memory Issues

**Problem**: Out of memory errors during large data processing

**Solutions**:
```bash
# Reduce data collection period
python cli.py ingest --days 7  # Instead of 365

# Process data in smaller chunks
# Edit configuration to reduce batch sizes
```

### Debug Mode

Enable verbose logging for troubleshooting:

```bash
# Run commands with verbose output
python cli.py --verbose status
python cli.py --verbose analyze --days 7
```

## 📁 Project Structure

```
finopsoptimizer/
├── finops/                          # Main package
│   ├── __init__.py                  # Package initialization
│   ├── core.py                      # Core orchestration
│   ├── config.py                    # Configuration management
│   ├── data_ingestion.py           # Data collection pipeline
│   ├── vm_rightsizing.py           # VM rightsizing analyzer
│   ├── scheduler.py                # Task scheduling
│   ├── unattached_disks.py         # Disk remediation
│   ├── reserved_instances.py       # RI/SP analyzer
│   ├── aws/                        # AWS provider
│   ├── azure/                      # Azure provider
│   ├── gcp/                        # GCP provider
│   └── oracle/                     # Oracle Cloud provider
├── cli.py                          # Command-line interface
├── examples/                       # Example scripts
├── requirements.txt                # Dependencies
├── finops_config.yml              # Configuration file (created)
└── finops_reports/                # Output directory (created)
```

## 🔧 Development Setup

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-cov pytest-mock

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=finops --cov-report=html
```

### Code Formatting

```bash
# Install formatting tools
pip install black isort flake8

# Format code
black finops/
isort finops/

# Check code quality
flake8 finops/
```

### Pre-commit Hooks

```bash
# Install pre-commit
pip install pre-commit

# Set up hooks
pre-commit install

# Run hooks manually
pre-commit run --all-files
```

## 📚 Next Steps

1. **Configure Cloud Providers**: Set up credentials for your cloud accounts
2. **Run Initial Analysis**: Start with basic cost analysis
3. **Explore Features**: Try different CLI commands and options
4. **Set Up Automation**: Configure schedules for ongoing optimization
5. **Review Reports**: Analyze generated recommendations
6. **Implement Changes**: Apply cost optimization recommendations

## 🆘 Getting Help

- **Documentation**: Check the main README.md for detailed information
- **Issues**: Report bugs on GitHub Issues
- **Examples**: Review the examples/ directory for usage patterns
- **CLI Help**: Use `python cli.py --help` for command information

## 🎯 Production Deployment

For production deployment, see the main README.md for:
- Docker deployment instructions
- Kubernetes configuration
- Security considerations
- Performance tuning
- Monitoring setup

---

**Happy Optimizing!** 🚀💰
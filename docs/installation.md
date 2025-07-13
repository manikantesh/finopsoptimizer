# Installation Guide

This guide will help you install and set up FinOps Optimizer for your environment.

## 📋 Prerequisites

### System Requirements

- **Python**: 3.8 or higher
- **Memory**: 2GB RAM minimum (4GB recommended)
- **Storage**: 1GB free space
- **Network**: Internet access for cloud provider APIs

### Cloud Provider Access

Ensure you have access to at least one of the following cloud providers:

- **AWS**: Access key and secret key with appropriate permissions
- **Azure**: Service principal or managed identity
- **GCP**: Service account with billing access
- **Oracle Cloud**: API key and private key

## 🚀 Quick Installation

### Using pip

```bash
# Install from PyPI
pip install finopsoptimizer

# Install with all dependencies
pip install finopsoptimizer[all]
```

### Using conda

```bash
# Create new environment
conda create -n finops python=3.9
conda activate finops

# Install package
pip install finopsoptimizer
```

### From Source

```bash
# Clone repository
git clone https://github.com/manikantesh/finopsoptimizer.git
cd finopsoptimizer

# Install in development mode
pip install -e .

# Install development dependencies
pip install -r requirements-dev.txt
```

## 🔧 Detailed Installation

### 1. Python Environment Setup

#### Using virtualenv

```bash
# Create virtual environment
python -m venv finops-env

# Activate environment
# On Windows:
finops-env\Scripts\activate
# On macOS/Linux:
source finops-env/bin/activate

# Upgrade pip
pip install --upgrade pip
```

#### Using conda

```bash
# Create conda environment
conda create -n finops python=3.9
conda activate finops
```

### 2. Install Core Dependencies

```bash
# Install core package
pip install finopsoptimizer

# Install additional dependencies for specific features
pip install finopsoptimizer[web]      # Web dashboard
pip install finopsoptimizer[security] # Security features
pip install finopsoptimizer[monitoring] # Monitoring features
```

### 3. Install Cloud Provider SDKs

#### AWS

```bash
pip install boto3 botocore
```

#### Azure

```bash
pip install azure-mgmt-compute azure-mgmt-costmanagement azure-identity
```

#### GCP

```bash
pip install google-cloud-compute google-cloud-billing google-cloud-monitoring
```

#### Oracle Cloud

```bash
pip install oci
```

### 4. Install Development Dependencies

```bash
# Testing
pip install pytest pytest-cov pytest-mock

# Code quality
pip install flake8 black isort

# Security
pip install bandit safety

# Documentation
pip install mkdocs mkdocs-material
```

## 🌐 Cloud Provider Setup

### AWS Configuration

1. **Create IAM User**:
   ```bash
   # Install AWS CLI
   pip install awscli

   # Configure credentials
   aws configure
   ```

2. **Required Permissions**:
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Allow",
         "Action": [
           "ce:GetCostAndUsage",
           "ce:GetReservationUtilization",
           "ec2:DescribeInstances",
           "ec2:DescribeVolumes",
           "cloudwatch:GetMetricStatistics"
         ],
         "Resource": "*"
       }
     ]
   }
   ```

3. **Environment Variables**:
   ```bash
   export AWS_ACCESS_KEY_ID=your_access_key
   export AWS_SECRET_ACCESS_KEY=your_secret_key
   export AWS_DEFAULT_REGION=us-east-1
   ```

### Azure Configuration

1. **Create Service Principal**:
   ```bash
   # Install Azure CLI
   az login

   # Create service principal
   az ad sp create-for-rbac --name finops-optimizer
   ```

2. **Required Permissions**:
   - Cost Management Reader
   - Virtual Machine Contributor
   - Monitoring Reader

3. **Environment Variables**:
   ```bash
   export AZURE_CLIENT_ID=your_client_id
   export AZURE_CLIENT_SECRET=your_client_secret
   export AZURE_TENANT_ID=your_tenant_id
   ```

### GCP Configuration

1. **Create Service Account**:
   ```bash
   # Install gcloud CLI
   gcloud auth login

   # Create service account
   gcloud iam service-accounts create finops-optimizer
   ```

2. **Required Permissions**:
   - Cloud Billing Viewer
   - Compute Instance Viewer
   - Monitoring Viewer

3. **Download Key File**:
   ```bash
   gcloud iam service-accounts keys create key.json \
     --iam-account=finops-optimizer@your-project.iam.gserviceaccount.com
   ```

4. **Environment Variable**:
   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json
   ```

### Oracle Cloud Configuration

1. **Generate API Key**:
   ```bash
   # Generate private key
   openssl genrsa -out private_key.pem 2048

   # Generate public key
   openssl rsa -pubout -in private_key.pem -out public_key.pem
   ```

2. **Required Permissions**:
   - Cost Management Reader
   - Compute Instance Viewer
   - Monitoring Viewer

3. **Configuration**:
   ```yaml
   oracle:
     enabled: true
     tenancy_id: your_tenancy_id
     user_id: your_user_id
     fingerprint: your_fingerprint
     private_key_path: /path/to/private_key.pem
     region: us-ashburn-1
   ```

## 🔧 Configuration Setup

### 1. Initialize Configuration

```bash
# Create default configuration
python cli.py init

# This creates finops_config.yml
```

### 2. Edit Configuration

```yaml
# finops_config.yml
aws:
  enabled: true
  region: us-east-1
  account_id: your-account-id

azure:
  enabled: true
  subscription_id: your-subscription-id

gcp:
  enabled: true
  project_id: your-project-id

oracle:
  enabled: false
  tenancy_id: null
  user_id: null
  fingerprint: null
  private_key_path: null
  region: us-ashburn-1

optimization:
  cpu_utilization_threshold: 0.7
  memory_utilization_threshold: 0.8
  cost_savings_threshold: 0.1
  min_instances: 1
  max_instances: 10
  scale_up_threshold: 0.8
  scale_down_threshold: 0.3

performance:
  max_workers: 4
  cache_ttl: 3600
  batch_size: 100

security:
  max_login_attempts: 5
  session_timeout: 3600
  password_min_length: 8

output_dir: "./finops_reports"
log_level: "INFO"
```

### 3. Validate Configuration

```bash
# Test configuration
python cli.py status

# This will verify all cloud provider connections
```

## 🧪 Testing Installation

### 1. Run Basic Tests

```bash
# Test core functionality
python -c "from finops import FinOpsOptimizer; print('Installation successful!')"

# Test CLI
python cli.py --help
```

### 2. Test Cloud Providers

```bash
# Test AWS
python -c "import boto3; print('AWS SDK installed')"

# Test Azure
python -c "import azure.mgmt.compute; print('Azure SDK installed')"

# Test GCP
python -c "import google.cloud.compute; print('GCP SDK installed')"

# Test Oracle
python -c "import oci; print('Oracle SDK installed')"
```

### 3. Run Test Suite

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=finops --cov-report=html
```

## 🌐 Web Dashboard Setup

### 1. Install Web Dependencies

```bash
pip install flask flask-login werkzeug
```

### 2. Start Dashboard

```bash
# Start web server
python -m web.app

# Or use CLI
python cli.py web
```

### 3. Access Dashboard

- **URL**: http://localhost:5000
- **Username**: admin
- **Password**: admin123

## 🐳 Docker Installation

### 1. Build Image

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "-m", "web.app"]
```

### 2. Build and Run

```bash
# Build image
docker build -t finopsoptimizer .

# Run container
docker run -p 5000:5000 finopsoptimizer
```

## 🚀 Production Deployment

### 1. Install Production Dependencies

```bash
pip install finopsoptimizer[production]
pip install gunicorn
```

### 2. Configure Environment

```bash
export FINOPS_CONFIG_PATH=/path/to/config.yml
export FINOPS_SECRET_KEY=your-secret-key
export FINOPS_LOG_LEVEL=INFO
```

### 3. Start Production Server

```bash
# Using gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 web.app:app

# Using uwsgi
uwsgi --http :8000 --module web.app:app --processes 4
```

## 🔒 Security Setup

### 1. Generate Secret Key

```bash
# Generate secure secret key
python -c "import secrets; print(secrets.token_hex(32))"
```

### 2. Configure Security

```yaml
security:
  max_login_attempts: 5
  session_timeout: 3600
  password_min_length: 8
  api_key_hash: "your-api-key-hash"
```

### 3. Set Up SSL

```bash
# Install SSL certificate
sudo apt-get install certbot

# Generate certificate
sudo certbot certonly --standalone -d your-domain.com
```

## 📊 Monitoring Setup

### 1. Install Monitoring Dependencies

```bash
pip install psutil prometheus_client
```

### 2. Configure Monitoring

```yaml
monitoring:
  enabled: true
  metrics_port: 9090
  health_check_interval: 300
```

### 3. Start Monitoring

```bash
# Start with monitoring
python -m finops.monitoring
```

## 🛠 Troubleshooting

### Common Issues

#### 1. Import Errors

```bash
# Check Python version
python --version

# Reinstall package
pip uninstall finopsoptimizer
pip install finopsoptimizer
```

#### 2. Cloud Provider Errors

```bash
# Test AWS credentials
aws sts get-caller-identity

# Test Azure credentials
az account show

# Test GCP credentials
gcloud auth list
```

#### 3. Permission Errors

```bash
# Check file permissions
ls -la finops_config.yml

# Fix permissions
chmod 600 finops_config.yml
```

### Getting Help

- **Documentation**: [GitHub Pages](https://manikantesh.github.io/finopsoptimizer/)
- **Issues**: [GitHub Issues](https://github.com/manikantesh/finopsoptimizer/issues)
- **Discussions**: [GitHub Discussions](https://github.com/manikantesh/finopsoptimizer/discussions)

## ✅ Verification Checklist

- [ ] Python 3.8+ installed
- [ ] FinOps Optimizer package installed
- [ ] Cloud provider SDKs installed
- [ ] Configuration file created
- [ ] Cloud provider credentials configured
- [ ] Basic tests passing
- [ ] Web dashboard accessible
- [ ] Security settings configured
- [ ] Monitoring enabled (optional)

## 🎉 Next Steps

After successful installation:

1. **Read the Tutorial**: [Tutorial Guide](tutorial.md)
2. **Configure Cloud Providers**: [Configuration Guide](configuration.md)
3. **Explore the API**: [API Reference](api-reference.md)
4. **Set Up Monitoring**: [Performance Guide](performance.md)
5. **Review Security**: [Security Guide](security.md)

---

**Need help?** Check our [Troubleshooting Guide](troubleshooting.md) or [open an issue](https://github.com/manikantesh/finopsoptimizer/issues). 
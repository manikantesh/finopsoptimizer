# Troubleshooting Guide

This guide helps you resolve common issues with FinOps Optimizer.

## 📋 Common Issues

### 1. Installation Issues

#### Python Version Problems

**Problem**: `ModuleNotFoundError: No module named 'finops'`

**Solution**:
```bash
# Check Python version
python --version

# Ensure Python 3.8+ is installed
python3.8 --version

# Install in correct environment
pip install finopsoptimizer

# Or install from source
git clone https://github.com/manikantesh/finopsoptimizer.git
cd finopsoptimizer
pip install -e .
```

#### Dependency Conflicts

**Problem**: `ImportError: cannot import name 'boto3'`

**Solution**:
```bash
# Upgrade pip
pip install --upgrade pip

# Install cloud provider dependencies
pip install boto3 botocore
pip install azure-mgmt-compute azure-mgmt-costmanagement
pip install google-cloud-compute google-cloud-billing
pip install oci

# Check installed packages
pip list | grep -E "(boto3|azure|google|oci)"
```

### 2. Configuration Issues

#### Invalid Configuration File

**Problem**: `ConfigurationError: Invalid YAML syntax`

**Solution**:
```bash
# Validate YAML syntax
python -c "import yaml; yaml.safe_load(open('finops_config.yml'))"

# Check configuration
python cli.py validate-config

# Create new configuration
python cli.py init
```

#### Missing Required Fields

**Problem**: `ConfigurationError: Missing required field 'aws.region'`

**Solution**:
```yaml
# finops_config.yml
aws:
  enabled: true
  region: us-east-1  # Add missing field
  account_id: your-account-id

azure:
  enabled: false

gcp:
  enabled: false

optimization:
  cpu_utilization_threshold: 0.7
  memory_utilization_threshold: 0.8

output_dir: "./finops_reports"
log_level: "INFO"
```

### 3. Cloud Provider Issues

#### AWS Connection Issues

**Problem**: `ProviderError: Unable to connect to AWS`

**Solution**:
```bash
# Check AWS credentials
aws sts get-caller-identity

# Set environment variables
export AWS_ACCESS_KEY_ID=your-access-key
export AWS_SECRET_ACCESS_KEY=your-secret-key
export AWS_DEFAULT_REGION=us-east-1

# Test AWS CLI
aws ec2 describe-instances --max-items 1

# Check IAM permissions
aws iam get-user
```

**Common AWS Issues**:

1. **Invalid Credentials**
   ```bash
   # Regenerate access keys
   aws iam create-access-key --user-name your-username
   ```

2. **Insufficient Permissions**
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

3. **Region Issues**
   ```bash
   # Check available regions
   aws ec2 describe-regions --query 'Regions[].RegionName'
   
   # Set correct region
   export AWS_DEFAULT_REGION=us-east-1
   ```

#### Azure Connection Issues

**Problem**: `ProviderError: Unable to connect to Azure`

**Solution**:
```bash
# Login to Azure
az login

# Check subscription
az account show

# Create service principal
az ad sp create-for-rbac --name finops-optimizer

# Set environment variables
export AZURE_CLIENT_ID=your-client-id
export AZURE_CLIENT_SECRET=your-client-secret
export AZURE_TENANT_ID=your-tenant-id
```

**Common Azure Issues**:

1. **Service Principal Expired**
   ```bash
   # Create new service principal
   az ad sp create-for-rbac --name finops-optimizer-new
   ```

2. **Insufficient Permissions**
   ```bash
   # Grant permissions
   az role assignment create \
     --assignee your-service-principal-id \
     --role "Cost Management Reader" \
     --scope /subscriptions/your-subscription-id
   ```

#### GCP Connection Issues

**Problem**: `ProviderError: Unable to connect to GCP`

**Solution**:
```bash
# Login to GCP
gcloud auth login

# Set project
gcloud config set project your-project-id

# Create service account
gcloud iam service-accounts create finops-optimizer

# Download key file
gcloud iam service-accounts keys create key.json \
  --iam-account=finops-optimizer@your-project.iam.gserviceaccount.com

# Set environment variable
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json
```

**Common GCP Issues**:

1. **Service Account Key Expired**
   ```bash
   # Create new key
   gcloud iam service-accounts keys create new-key.json \
     --iam-account=finops-optimizer@your-project.iam.gserviceaccount.com
   ```

2. **Insufficient Permissions**
   ```bash
   # Grant permissions
   gcloud projects add-iam-policy-binding your-project \
     --member="serviceAccount:finops-optimizer@your-project.iam.gserviceaccount.com" \
     --role="roles/billing.viewer"
   ```

#### Oracle Cloud Connection Issues

**Problem**: `ProviderError: Unable to connect to Oracle Cloud`

**Solution**:
```bash
# Generate API key pair
openssl genrsa -out private_key.pem 2048
openssl rsa -pubout -in private_key.pem -out public_key.pem

# Set permissions
chmod 600 private_key.pem
chmod 644 public_key.pem

# Update configuration
```

**Common Oracle Issues**:

1. **Invalid API Key**
   ```bash
   # Regenerate API keys
   openssl genrsa -out new_private_key.pem 2048
   openssl rsa -pubout -in new_private_key.pem -out new_public_key.pem
   ```

2. **Incorrect Tenancy ID**
   ```bash
   # Find tenancy ID
   oci iam tenancy get --tenancy-id your-tenancy-id
   ```

### 4. Performance Issues

#### High Memory Usage

**Problem**: `MemoryError: Unable to allocate memory`

**Solution**:
```python
# Optimize memory usage
from finops.performance import MemoryOptimizer

optimizer = MemoryOptimizer()
optimizer.optimize_memory()

# Check memory usage
memory_info = optimizer.check_memory_usage()
print(f"Memory usage: {memory_info['percent']:.1f}%")
```

**Memory Optimization Tips**:

1. **Use Generators**
   ```python
   # Good: Use generator
   def cost_generator(cost_data):
       for item in cost_data:
           yield item['cost']
   
   # Bad: Load all data
   costs = [item['cost'] for item in cost_data]
   ```

2. **Clear Caches**
   ```python
   # Clear cache
   cache.clear()
   
   # Force garbage collection
   import gc
   gc.collect()
   ```

3. **Batch Processing**
   ```python
   # Process in batches
   batch_size = 100
   for i in range(0, len(data), batch_size):
       batch = data[i:i + batch_size]
       process_batch(batch)
   ```

#### Slow Performance

**Problem**: Cost analysis taking too long

**Solution**:
```python
# Enable caching
cache_config = {
    'enabled': True,
    'ttl': 3600,  # 1 hour
    'max_size': 1000
}

# Use parallel processing
from finops.performance import ParallelProcessor

processor = ParallelProcessor(max_workers=4)
results = processor.process_providers(providers, analyze_costs)
```

**Performance Optimization Tips**:

1. **Enable Caching**
   ```yaml
   performance:
     cache:
       enabled: true
       ttl: 3600
   ```

2. **Increase Workers**
   ```yaml
   performance:
     parallel:
       max_workers: 8
   ```

3. **Optimize Queries**
   ```python
   # Use indexes
   # Limit result sets
   # Use pagination
   ```

### 5. Web Dashboard Issues

#### Dashboard Not Loading

**Problem**: Dashboard returns 500 error

**Solution**:
```bash
# Check Flask app
python -m web.app

# Check logs
tail -f logs/finops.log

# Check configuration
python cli.py validate-config

# Test API endpoints
curl http://localhost:5000/api/status
```

#### Authentication Issues

**Problem**: Cannot login to dashboard

**Solution**:
```python
# Reset admin password
from werkzeug.security import generate_password_hash

new_password_hash = generate_password_hash('newpassword')
print(f"New password hash: {new_password_hash}")

# Update user database
users['admin'].password_hash = new_password_hash
```

#### Chart Not Displaying

**Problem**: Charts not loading or displaying

**Solution**:
```javascript
// Check browser console for errors
console.log('Chart data:', chartData);

// Verify data format
if (chartData && chartData.length > 0) {
    // Render chart
    renderChart(chartData);
} else {
    console.error('No chart data available');
}
```

### 6. Report Generation Issues

#### Report Not Generated

**Problem**: `ReportError: Unable to generate report`

**Solution**:
```bash
# Check output directory
ls -la finops_reports/

# Check permissions
chmod 755 finops_reports/

# Check disk space
df -h

# Test report generation
python cli.py report --type summary --format html
```

#### PDF Generation Fails

**Problem**: PDF reports fail to generate

**Solution**:
```bash
# Install PDF dependencies
pip install weasyprint

# Or use alternative
pip install reportlab

# Check system dependencies
# For weasyprint: libcairo2, libpango-1.0-0
sudo apt-get install libcairo2 libpango-1.0-0
```

### 7. Security Issues

#### Encryption Errors

**Problem**: `SecurityError: Encryption failed`

**Solution**:
```python
# Regenerate encryption key
import secrets

new_key = secrets.token_hex(32)
print(f"New encryption key: {new_key}")

# Update configuration
security_config['encryption_key'] = new_key
```

#### Authentication Failures

**Problem**: API authentication failing

**Solution**:
```python
# Check API key
api_key = get_api_key()
if not validate_api_key(api_key):
    # Generate new API key
    new_api_key = generate_api_key()
    update_api_key(new_api_key)
```

### 8. Monitoring Issues

#### Health Check Failures

**Problem**: Health checks failing

**Solution**:
```bash
# Run health check
python cli.py health

# Check provider status
python cli.py status

# Check system resources
python -c "
import psutil
print(f'CPU: {psutil.cpu_percent()}%')
print(f'Memory: {psutil.virtual_memory().percent}%')
print(f'Disk: {psutil.disk_usage('/').percent}%')
"
```

#### Metrics Not Collecting

**Problem**: Performance metrics not updating

**Solution**:
```python
# Check metrics collection
from finops.monitoring import HealthChecker

checker = HealthChecker()
metrics = checker.get_metrics()
print(f"Current metrics: {metrics}")

# Enable metrics collection
config.monitoring.metrics.enabled = True
```

## 🔧 Debug Mode

### 1. Enable Debug Logging

```bash
# Set debug environment
export FINOPS_LOG_LEVEL=DEBUG

# Run with debug
python cli.py --verbose analyze

# Check debug logs
tail -f logs/finops.log | grep DEBUG
```

### 2. Debug Configuration

```python
# Debug configuration loading
from finops.config import load_config

config = load_config()
print(f"Loaded config: {config}")

# Validate configuration
from finops.config import validate_config

validation = validate_config(config)
print(f"Validation results: {validation}")
```

### 3. Debug Cloud Providers

```python
# Test individual providers
from finops.aws import AWSProvider

aws_provider = AWSProvider(config.aws)
try:
    status = aws_provider.check_connection()
    print(f"AWS status: {status}")
except Exception as e:
    print(f"AWS error: {e}")
```

## 📊 Diagnostic Tools

### 1. System Diagnostics

```bash
# System information
python cli.py info

# Health check
python cli.py health

# Performance metrics
python cli.py metrics
```

### 2. Network Diagnostics

```bash
# Test cloud provider connectivity
python cli.py status --detailed

# Test API endpoints
curl -v http://localhost:5000/api/status

# Check DNS resolution
nslookup api.aws.amazon.com
```

### 3. Performance Diagnostics

```python
# Performance profiling
import cProfile
import pstats

def profile_function(func, *args, **kwargs):
    profiler = cProfile.Profile()
    profiler.enable()
    result = func(*args, **kwargs)
    profiler.disable()
    
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(10)
    
    return result

# Profile cost analysis
profile_function(optimizer.analyze_costs)
```

## 🚨 Emergency Procedures

### 1. Service Recovery

```bash
# Restart services
sudo systemctl restart finops-optimizer

# Clear caches
python cli.py cleanup --all

# Reset configuration
python cli.py init
```

### 2. Data Recovery

```bash
# Backup configuration
cp finops_config.yml finops_config.yml.backup

# Restore from backup
cp finops_config.yml.backup finops_config.yml

# Check data integrity
python cli.py validate-config
```

### 3. Emergency Contacts

- **Documentation**: [GitHub Pages](https://manikantesh.github.io/finopsoptimizer/)
- **Issues**: [GitHub Issues](https://github.com/manikantesh/finopsoptimizer/issues)
- **Discussions**: [GitHub Discussions](https://github.com/manikantesh/finopsoptimizer/discussions)
- **Email**: support@finopsoptimizer.com

## 📋 Troubleshooting Checklist

### 1. Installation Issues
- [ ] Python 3.8+ installed
- [ ] Dependencies installed
- [ ] Virtual environment activated
- [ ] Package installed correctly

### 2. Configuration Issues
- [ ] Configuration file exists
- [ ] YAML syntax valid
- [ ] Required fields present
- [ ] File permissions correct

### 3. Cloud Provider Issues
- [ ] Credentials valid
- [ ] Permissions sufficient
- [ ] Network connectivity
- [ ] API endpoints accessible

### 4. Performance Issues
- [ ] Memory usage acceptable
- [ ] CPU usage normal
- [ ] Cache working
- [ ] Database optimized

### 5. Security Issues
- [ ] Encryption working
- [ ] Authentication valid
- [ ] API keys secure
- [ ] Audit logging enabled

## 🔍 Getting Help

### 1. Self-Service Resources

- **Documentation**: [GitHub Pages](https://manikantesh.github.io/finopsoptimizer/)
- **Tutorial**: [Tutorial Guide](tutorial.md)
- **API Reference**: [API Reference](api-reference.md)
- **Configuration Guide**: [Configuration Guide](configuration.md)

### 2. Community Support

- **GitHub Issues**: [Open an issue](https://github.com/manikantesh/finopsoptimizer/issues)
- **GitHub Discussions**: [Start a discussion](https://github.com/manikantesh/finopsoptimizer/discussions)
- **Stack Overflow**: Tag with `finopsoptimizer`

### 3. Professional Support

- **Email**: support@finopsoptimizer.com
- **Response Time**: 24-48 hours
- **Priority Support**: Available for enterprise customers

### 4. Bug Reports

When reporting bugs, please include:

1. **Environment Information**
   ```bash
   python --version
   pip list | grep finops
   uname -a
   ```

2. **Error Messages**
   ```
   Full error traceback
   Log files
   Configuration (sanitized)
   ```

3. **Steps to Reproduce**
   ```
   Exact commands run
   Input data
   Expected vs actual output
   ```

4. **Additional Context**
   ```
   Cloud provider
   Data size
   Performance expectations
   ```

---

**Still having issues?** Check our [GitHub Issues](https://github.com/manikantesh/finopsoptimizer/issues) or [open a new issue](https://github.com/manikantesh/finopsoptimizer/issues/new). 
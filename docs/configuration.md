# Configuration Guide

This guide covers all configuration options for FinOps Optimizer, including cloud provider settings, optimization parameters, security configurations, and performance tuning.

## 📋 Configuration Overview

FinOps Optimizer uses a YAML configuration file (`finops_config.yml`) to manage all settings. The configuration is organized into several sections:

- **Cloud Providers**: AWS, Azure, GCP, Oracle Cloud settings
- **Optimization**: Rightsizing and autoscaling parameters
- **Performance**: Caching and parallel processing settings
- **Security**: Authentication and encryption settings
- **Monitoring**: Health checks and metrics collection
- **Output**: Report generation and logging settings

## 🚀 Quick Configuration

### Initialize Configuration

```bash
# Create default configuration file
python cli.py init

# This creates finops_config.yml with default settings
```

### Basic Configuration

```yaml
# finops_config.yml
aws:
  enabled: true
  region: us-east-1

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

## ☁️ Cloud Provider Configuration

### AWS Configuration

```yaml
aws:
  enabled: true
  region: us-east-1
  account_id: "123456789012"
  
  # Optional: Custom endpoints for private clouds
  endpoints:
    ec2: "https://ec2.us-east-1.amazonaws.com"
    ce: "https://ce.us-east-1.amazonaws.com"
  
  # Optional: Assume role configuration
  assume_role:
    enabled: false
    role_arn: "arn:aws:iam::123456789012:role/FinOpsRole"
    session_name: "FinOpsSession"
  
  # Optional: Cost Explorer settings
  cost_explorer:
    granularity: "DAILY"
    metrics: ["UnblendedCost", "UsageQuantity"]
    group_by: ["SERVICE", "REGION"]
```

**Required Permissions:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ce:GetCostAndUsage",
        "ce:GetReservationUtilization",
        "ce:GetReservationCoverage",
        "ec2:DescribeInstances",
        "ec2:DescribeVolumes",
        "ec2:DescribeReservedInstances",
        "cloudwatch:GetMetricStatistics",
        "rds:DescribeDBInstances",
        "elasticache:DescribeCacheClusters"
      ],
      "Resource": "*"
    }
  ]
}
```

### Azure Configuration

```yaml
azure:
  enabled: true
  subscription_id: "your-subscription-id"
  tenant_id: "your-tenant-id"
  
  # Optional: Resource group filtering
  resource_groups:
    - "production-rg"
    - "development-rg"
  
  # Optional: Custom endpoints
  endpoints:
    management: "https://management.azure.com"
    resource: "https://management.azure.com"
  
  # Optional: Managed identity
  managed_identity:
    enabled: false
    client_id: "your-managed-identity-client-id"
```

**Required Permissions:**
- Cost Management Reader
- Virtual Machine Contributor
- Monitoring Reader
- Network Contributor

### GCP Configuration

```yaml
gcp:
  enabled: true
  project_id: "your-project-id"
  
  # Optional: Multiple projects
  projects:
    - "project-1"
    - "project-2"
  
  # Optional: Custom API endpoints
  endpoints:
    compute: "https://compute.googleapis.com"
    billing: "https://billing.googleapis.com"
  
  # Optional: Service account impersonation
  impersonation:
    enabled: false
    target_service_account: "finops@project.iam.gserviceaccount.com"
```

**Required Permissions:**
- Cloud Billing Viewer
- Compute Instance Viewer
- Monitoring Viewer
- Storage Object Viewer

### Oracle Cloud Configuration

```yaml
oracle:
  enabled: true
  tenancy_id: "your-tenancy-id"
  user_id: "your-user-id"
  fingerprint: "your-fingerprint"
  private_key_path: "/path/to/private_key.pem"
  region: "us-ashburn-1"
  
  # Optional: Multiple compartments
  compartments:
    - "ocid1.compartment.oc1..example"
    - "ocid2.compartment.oc1..example"
  
  # Optional: Custom endpoints
  endpoints:
    compute: "https://iaas.us-ashburn-1.oraclecloud.com"
    monitoring: "https://telemetry.us-ashburn-1.oraclecloud.com"
```

**Required Permissions:**
- Cost Management Reader
- Compute Instance Viewer
- Monitoring Viewer

## ⚙️ Optimization Configuration

### Rightsizing Parameters

```yaml
optimization:
  # CPU utilization thresholds
  cpu_utilization_threshold: 0.7
  cpu_utilization_warning: 0.5
  
  # Memory utilization thresholds
  memory_utilization_threshold: 0.8
  memory_utilization_warning: 0.6
  
  # Cost savings thresholds
  cost_savings_threshold: 0.1  # 10% minimum savings
  cost_savings_warning: 0.05   # 5% warning threshold
  
  # Resource type specific thresholds
  resource_thresholds:
    compute:
      cpu_utilization: 0.7
      memory_utilization: 0.8
      cost_savings: 0.1
    storage:
      utilization: 0.6
      cost_savings: 0.15
    database:
      cpu_utilization: 0.6
      memory_utilization: 0.7
      cost_savings: 0.2
```

### Autoscaling Configuration

```yaml
optimization:
  autoscaling:
    # Instance limits
    min_instances: 1
    max_instances: 10
    
    # Scaling thresholds
    scale_up_threshold: 0.8
    scale_down_threshold: 0.3
    
    # Cooldown periods (seconds)
    scale_up_cooldown: 300
    scale_down_cooldown: 600
    
    # Scaling policies
    policies:
      cpu_based:
        enabled: true
        target_utilization: 0.7
      memory_based:
        enabled: true
        target_utilization: 0.8
      custom_metrics:
        enabled: false
        metrics: []
```

### Cost Allocation Settings

```yaml
optimization:
  cost_allocation:
    # Allocation methods
    methods:
      - "tag_based"
      - "resource_based"
      - "hybrid"
    
    # Default tags for allocation
    default_tags:
      - "Environment"
      - "Project"
      - "Team"
      - "CostCenter"
    
    # Department mapping
    departments:
      engineering: ["dev", "prod", "staging"]
      marketing: ["campaign", "analytics"]
      sales: ["crm", "leadgen"]
    
    # Project mapping
    projects:
      webapp: ["frontend", "backend", "database"]
      mobile: ["ios", "android", "api"]
      data: ["pipeline", "warehouse", "analytics"]
```

## ⚡ Performance Configuration

### Caching Settings

```yaml
performance:
  # Cache configuration
  cache:
    enabled: true
    ttl: 3600  # Time to live in seconds
    max_size: 1000  # Maximum cache entries
    cleanup_interval: 300  # Cleanup interval in seconds
  
  # Parallel processing
  parallel:
    max_workers: 4
    timeout: 300  # Timeout in seconds
    batch_size: 100
  
  # Memory optimization
  memory:
    max_usage: 0.8  # Maximum memory usage (80%)
    cleanup_threshold: 0.7  # Cleanup threshold (70%)
    gc_interval: 600  # Garbage collection interval
```

### Batch Processing

```yaml
performance:
  batch_processing:
    enabled: true
    batch_size: 100
    max_concurrent_batches: 4
    timeout: 300
    
    # Batch types
    types:
      cost_analysis:
        batch_size: 50
        timeout: 180
      rightsizing:
        batch_size: 25
        timeout: 240
      forecasting:
        batch_size: 100
        timeout: 300
```

## 🔒 Security Configuration

### Authentication Settings

```yaml
security:
  # Login settings
  authentication:
    enabled: true
    max_login_attempts: 5
    lockout_duration: 900  # 15 minutes
    session_timeout: 3600  # 1 hour
    
    # Password policy
    password_policy:
      min_length: 8
      require_uppercase: true
      require_lowercase: true
      require_digits: true
      require_special: true
      max_age: 90  # days
  
  # API security
  api:
    rate_limit: 100  # requests per hour
    rate_limit_window: 3600  # seconds
    require_api_key: true
    api_key_expiry: 365  # days
```

### Encryption Settings

```yaml
security:
  encryption:
    enabled: true
    algorithm: "AES-256"
    key_rotation: 90  # days
    
    # Encrypted fields
    encrypted_fields:
      - "aws.secret_access_key"
      - "azure.client_secret"
      - "gcp.private_key"
      - "oracle.private_key"
    
    # Key storage
    key_storage:
      type: "file"  # file, aws_kms, azure_keyvault
      path: "./.keys"
```

### Audit Logging

```yaml
security:
  audit:
    enabled: true
    log_level: "INFO"
    log_file: "./logs/audit.log"
    max_file_size: 10485760  # 10MB
    backup_count: 5
    
    # Events to log
    events:
      - "login"
      - "logout"
      - "cost_analysis"
      - "optimization"
      - "report_generation"
      - "configuration_change"
```

## 📊 Monitoring Configuration

### Health Checks

```yaml
monitoring:
  health_checks:
    enabled: true
    interval: 300  # 5 minutes
    timeout: 30  # seconds
    
    # Health check types
    checks:
      cloud_providers: true
      database: false
      disk_space: true
      memory_usage: true
      cpu_usage: true
    
    # Thresholds
    thresholds:
      disk_usage: 0.9  # 90%
      memory_usage: 0.8  # 80%
      cpu_usage: 0.9  # 90%
```

### Metrics Collection

```yaml
monitoring:
  metrics:
    enabled: true
    collection_interval: 60  # seconds
    retention_days: 30
    
    # Metrics to collect
    metrics:
      - "cost_analysis_duration"
      - "optimization_recommendations"
      - "cache_hit_rate"
      - "memory_usage"
      - "cpu_usage"
      - "api_requests"
      - "errors"
    
    # Export settings
    export:
      prometheus: false
      cloudwatch: false
      custom_endpoint: ""
```

### Alerting

```yaml
monitoring:
  alerts:
    enabled: true
    
    # Alert channels
    channels:
      email:
        enabled: false
        smtp_server: "smtp.gmail.com"
        smtp_port: 587
        username: "alerts@company.com"
        password: "encrypted_password"
      
      slack:
        enabled: false
        webhook_url: "https://hooks.slack.com/services/..."
      
      webhook:
        enabled: false
        url: "https://api.company.com/alerts"
    
    # Alert rules
    rules:
      high_cost:
        condition: "cost > threshold"
        threshold: 1000
        severity: "warning"
      
      optimization_opportunity:
        condition: "savings > threshold"
        threshold: 100
        severity: "info"
      
      system_error:
        condition: "error_rate > threshold"
        threshold: 0.05
        severity: "critical"
```

## 📤 Output Configuration

### Report Settings

```yaml
output:
  # Report directory
  directory: "./finops_reports"
  
  # Report formats
  formats:
    html:
      enabled: true
      template: "default"
      include_charts: true
      include_recommendations: true
    
    pdf:
      enabled: true
      page_size: "A4"
      orientation: "portrait"
    
    json:
      enabled: true
      pretty_print: true
      include_metadata: true
    
    csv:
      enabled: false
      delimiter: ","
      include_headers: true
  
  # Report scheduling
  scheduling:
    enabled: false
    frequency: "weekly"  # daily, weekly, monthly
    day_of_week: "monday"
    time: "09:00"
    timezone: "UTC"
```

### Logging Configuration

```yaml
output:
  logging:
    level: "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Log files
    files:
      application: "./logs/finops.log"
      error: "./logs/error.log"
      access: "./logs/access.log"
    
    # Log rotation
    rotation:
      max_size: 10485760  # 10MB
      backup_count: 5
      interval: "daily"
    
    # Console logging
    console:
      enabled: true
      level: "INFO"
```

## 🔧 Advanced Configuration

### Custom Plugins

```yaml
plugins:
  enabled: true
  directory: "./plugins"
  
  # Plugin configuration
  plugins:
    custom_optimizer:
      enabled: true
      config:
        custom_threshold: 0.5
        custom_algorithm: "ml_based"
    
    custom_reporter:
      enabled: false
      config:
        template: "custom_template.html"
        variables:
          company_name: "Your Company"
          logo_url: "https://company.com/logo.png"
```

### Environment-Specific Settings

```yaml
environments:
  development:
    log_level: "DEBUG"
    cache_enabled: false
    max_workers: 2
    
  staging:
    log_level: "INFO"
    cache_enabled: true
    max_workers: 4
    
  production:
    log_level: "WARNING"
    cache_enabled: true
    max_workers: 8
    security:
      require_ssl: true
      rate_limit: 50
```

## 🛠 Configuration Validation

### Validate Configuration

```bash
# Validate configuration file
python cli.py validate-config

# Test cloud provider connections
python cli.py status

# Run configuration tests
python -c "
from finops.config import load_config, validate_config
config = load_config()
result = validate_config(config)
print('Configuration valid:', result['valid'])
"
```

### Configuration Examples

#### Minimal Configuration

```yaml
aws:
  enabled: true
  region: us-east-1

optimization:
  cpu_utilization_threshold: 0.7
  memory_utilization_threshold: 0.8

output_dir: "./reports"
log_level: "INFO"
```

#### Production Configuration

```yaml
aws:
  enabled: true
  region: us-east-1
  account_id: "123456789012"

azure:
  enabled: true
  subscription_id: "azure-sub-id"

gcp:
  enabled: true
  project_id: "gcp-project-id"

optimization:
  cpu_utilization_threshold: 0.7
  memory_utilization_threshold: 0.8
  cost_savings_threshold: 0.1
  min_instances: 1
  max_instances: 10
  scale_up_threshold: 0.8
  scale_down_threshold: 0.3

performance:
  max_workers: 8
  cache_ttl: 3600
  batch_size: 100

security:
  max_login_attempts: 5
  session_timeout: 3600
  password_min_length: 8

monitoring:
  health_checks:
    enabled: true
    interval: 300

output:
  directory: "/var/finops/reports"
  formats:
    html:
      enabled: true
    pdf:
      enabled: true
    json:
      enabled: true

log_level: "WARNING"
```

## 🔄 Configuration Management

### Environment Variables

```bash
# Override configuration with environment variables
export FINOPS_AWS_REGION=us-west-2
export FINOPS_AZURE_ENABLED=true
export FINOPS_LOG_LEVEL=DEBUG
export FINOPS_OUTPUT_DIR=/custom/path
```

### Configuration Inheritance

```yaml
# base_config.yml
optimization:
  cpu_utilization_threshold: 0.7
  memory_utilization_threshold: 0.8

# production_config.yml
extends: base_config.yml

optimization:
  cpu_utilization_threshold: 0.8  # Override for production
  cost_savings_threshold: 0.15    # Add production-specific setting
```

### Dynamic Configuration

```python
from finops.config import Config

# Create configuration programmatically
config = Config()
config.aws.enabled = True
config.aws.region = "us-east-1"
config.optimization.cpu_utilization_threshold = 0.7

# Use configuration
optimizer = FinOpsOptimizer(config)
```

## ✅ Configuration Checklist

- [ ] Cloud provider credentials configured
- [ ] Optimization thresholds set appropriately
- [ ] Security settings configured
- [ ] Performance settings tuned
- [ ] Monitoring enabled
- [ ] Output directory configured
- [ ] Logging level set
- [ ] Configuration validated

## 🆘 Troubleshooting Configuration

### Common Issues

1. **Invalid YAML Syntax**
   ```bash
   # Validate YAML syntax
   python -c "import yaml; yaml.safe_load(open('finops_config.yml'))"
   ```

2. **Missing Required Fields**
   ```bash
   # Check required fields
   python cli.py validate-config
   ```

3. **Cloud Provider Connection Issues**
   ```bash
   # Test connections
   python cli.py status
   ```

### Getting Help

- **Documentation**: [GitHub Pages](https://manikantesh.github.io/finopsoptimizerdocs/)
- **Issues**: [GitHub Issues](https://github.com/manikantesh/finopsoptimizerdocs/issues)
- **Discussions**: [GitHub Discussions](https://github.com/manikantesh/finopsoptimizerdocs/discussions)

---

**Need help with configuration?** Check our [Troubleshooting Guide](troubleshooting.md) or [open an issue](https://github.com/manikantesh/finopsoptimizerdocs/issues). 
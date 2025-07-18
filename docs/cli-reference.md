# CLI Reference

This document provides comprehensive reference for the FinOps Optimizer command-line interface.

## 📋 Overview

The FinOps Optimizer CLI provides a command-line interface for all major operations including cost analysis, optimization, reporting, and configuration management.

## 🚀 Quick Start

```bash
# Initialize configuration
python cli.py init

# Check provider status
python cli.py status

# Analyze costs
python cli.py analyze

# Run optimization
python cli.py optimize

# Generate report
python cli.py report
```

## 📚 Command Reference

### Global Options

All commands support these global options:

```bash
python cli.py [OPTIONS] COMMAND [ARGS]...
```

**Options:**
- `--config, -c PATH`: Path to configuration file
- `--verbose, -v`: Enable verbose logging
- `--help, -h`: Show help message

**Example:**
```bash
python cli.py --config custom_config.yml --verbose analyze
```

## 🔧 Configuration Commands

### `init`

Initialize configuration file.

```bash
python cli.py init [OPTIONS]
```

**Options:**
- `--output, -o PATH`: Output file path (default: finops_config.yml)
- `--interactive, -i`: Interactive configuration setup
- `--template PATH`: Use configuration template

**Examples:**
```bash
# Create default configuration
python cli.py init

# Create configuration with custom path
python cli.py init --output my_config.yml

# Interactive setup
python cli.py init --interactive
```

**Output:**
```
Configuration file created: finops_config.yml
Please edit the file with your cloud provider credentials.
```

### `validate-config`

Validate configuration file.

```bash
python cli.py validate-config [OPTIONS]
```

**Options:**
- `--config, -c PATH`: Configuration file path
- `--strict`: Strict validation mode

**Examples:**
```bash
# Validate default configuration
python cli.py validate-config

# Validate specific configuration
python cli.py validate-config --config custom_config.yml

# Strict validation
python cli.py validate-config --strict
```

**Output:**
```
Configuration validation:
✅ AWS: Valid
✅ Azure: Valid
❌ GCP: Invalid credentials
✅ Oracle: Valid

Overall: 3/4 providers valid
```

## ☁️ Provider Commands

### `status`

Check cloud provider status and connectivity.

```bash
python cli.py status [OPTIONS]
```

**Options:**
- `--providers LIST`: Specific providers to check
- `--detailed`: Show detailed status information
- `--timeout SECONDS`: Connection timeout (default: 30)

**Examples:**
```bash
# Check all providers
python cli.py status

# Check specific providers
python cli.py status --providers aws,azure

# Detailed status
python cli.py status --detailed
```

**Output:**
```
Provider Status:
AWS: ✅ Connected (us-east-1)
Azure: ✅ Connected (subscription: abc123)
GCP: ❌ Disconnected (Invalid credentials)
Oracle: ⚠️ Warning (Limited permissions)

Summary: 2/4 providers connected
```

### `test-credentials`

Test cloud provider credentials.

```bash
python cli.py test-credentials [OPTIONS]
```

**Options:**
- `--providers LIST`: Specific providers to test
- `--permissions`: Test specific permissions
- `--verbose`: Show detailed test results

**Examples:**
```bash
# Test all providers
python cli.py test-credentials

# Test specific providers
python cli.py test-credentials --providers aws,gcp

# Test with permissions
python cli.py test-credentials --permissions
```

**Output:**
```
Credential Testing:
AWS:
  ✅ Access Key: Valid
  ✅ Secret Key: Valid
  ✅ Permissions: Cost Explorer, EC2, CloudWatch
  ✅ Region: us-east-1

Azure:
  ✅ Client ID: Valid
  ✅ Client Secret: Valid
  ✅ Permissions: Cost Management, Virtual Machines
  ✅ Subscription: abc123

GCP:
  ❌ Service Account: Invalid
  ❌ Permissions: Insufficient
  ❌ Project: Not found
```

## 💰 Cost Analysis Commands

### `analyze`

Analyze costs across cloud providers.

```bash
python cli.py analyze [OPTIONS]
```

**Options:**
- `--days, -d INTEGER`: Number of days to analyze (default: 30)
- `--start-date DATE`: Start date (YYYY-MM-DD)
- `--end-date DATE`: End date (YYYY-MM-DD)
- `--providers LIST`: Specific providers to analyze
- `--output, -o PATH`: Output file path
- `--format FORMAT`: Output format (json, csv, yaml)

**Examples:**
```bash
# Analyze last 30 days
python cli.py analyze

# Analyze specific period
python cli.py analyze --start-date 2024-01-01 --end-date 2024-01-31

# Analyze specific providers
python cli.py analyze --providers aws,azure

# Save results to file
python cli.py analyze --output cost_analysis.json --format json
```

**Output:**
```
Cost Analysis Results:
Period: 2024-01-01 to 2024-01-31
Total Cost: $2,450.75

AWS (us-east-1):
  Total Cost: $1,250.50
  Top Services:
    EC2: $750.25
    S3: $350.00
    RDS: $150.25

Azure (subscription: abc123):
  Total Cost: $800.25
  Top Services:
    Virtual Machines: $500.00
    Storage: $200.00
    SQL Database: $100.25

GCP (project: my-project):
  Total Cost: $400.00
  Top Services:
    Compute Engine: $250.00
    Cloud Storage: $100.00
    Cloud SQL: $50.00

Cost Trends:
  Daily Average: $79.06
  Weekly Trend: +5.2%
  Monthly Trend: +12.8%
```

### `cost-breakdown`

Get detailed cost breakdown.

```bash
python cli.py cost-breakdown [OPTIONS]
```

**Options:**
- `--days, -d INTEGER`: Number of days (default: 30)
- `--group-by FIELD`: Group by field (service, region, instance_type)
- `--filter FILTER`: Filter results
- `--sort-by FIELD`: Sort by field
- `--limit INTEGER`: Limit number of results

**Examples:**
```bash
# Get service breakdown
python cli.py cost-breakdown --group-by service

# Get regional breakdown
python cli.py cost-breakdown --group-by region

# Get instance type breakdown
python cli.py cost-breakdown --group-by instance_type

# Filter by cost threshold
python cli.py cost-breakdown --filter "cost > 100"
```

**Output:**
```
Cost Breakdown by Service:
EC2 Instances: $750.25 (30.6%)
  - t3.large: $300.00
  - t3.xlarge: $450.25

S3 Storage: $350.00 (14.3%)
  - Standard: $200.00
  - IA: $150.00

RDS Databases: $150.25 (6.1%)
  - db.t3.micro: $50.00
  - db.t3.small: $100.25

Virtual Machines: $500.00 (20.4%)
  - Standard_D2s_v3: $300.00
  - Standard_D4s_v3: $200.00
```

## ⚙️ Optimization Commands

### `optimize`

Run complete optimization pipeline.

```bash
python cli.py optimize [OPTIONS]
```

**Options:**
- `--providers LIST`: Specific providers to optimize
- `--types LIST`: Optimization types (rightsizing, autoscaling, allocation)
- `--output, -o PATH`: Output file path
- `--generate-report`: Generate optimization report
- `--save-results`: Save results to file

**Examples:**
```bash
# Run complete optimization
python cli.py optimize

# Optimize specific providers
python cli.py optimize --providers aws,azure

# Specific optimization types
python cli.py optimize --types rightsizing,autoscaling

# Save results
python cli.py optimize --output optimization_results.json
```

**Output:**
```
Running Optimization Pipeline...
✅ Cost Analysis: Complete
✅ Rightsizing Analysis: Complete
✅ Autoscaling Analysis: Complete
✅ Cost Allocation: Complete
✅ Forecasting: Complete

Optimization Results:
Total Recommendations: 15
Total Potential Savings: $450.75

Rightsizing Recommendations: 8
  - Downsize t3.xlarge to t3.large: $200.00
  - Terminate unused instances: $150.00
  - Optimize storage classes: $100.75

Autoscaling Recommendations: 5
  - Optimize scaling policies: $50.00
  - Adjust thresholds: $25.00
  - Add predictive scaling: $25.00

Cost Allocation Recommendations: 2
  - Implement tagging strategy: $50.00
  - Set up cost centers: $25.00

Implementation Priority:
1. High Priority (5 recommendations): $300.00
2. Medium Priority (7 recommendations): $125.00
3. Low Priority (3 recommendations): $25.75

Report generated: optimization_report_20240101.html
```

### `rightsizing`

Generate rightsizing recommendations.

```bash
python cli.py rightsizing [OPTIONS]
```

**Options:**
- `--providers LIST`: Specific providers
- `--threshold FLOAT`: Utilization threshold (default: 0.7)
- `--min-savings FLOAT`: Minimum savings threshold (default: 0.1)
- `--output, -o PATH`: Output file path
- `--detailed`: Show detailed analysis

**Examples:**
```bash
# Generate rightsizing recommendations
python cli.py rightsizing

# Custom thresholds
python cli.py rightsizing --threshold 0.8 --min-savings 0.15

# Specific providers
python cli.py rightsizing --providers aws

# Detailed analysis
python cli.py rightsizing --detailed
```

**Output:**
```
Rightsizing Analysis:
Analyzed 25 instances across 2 providers

AWS Rightsizing Opportunities: 8
1. i-123456 (t3.xlarge → t3.large)
   Current: 25% CPU, 30% Memory
   Savings: $200.00/month
   Risk: Low

2. i-789012 (t3.large → t3.medium)
   Current: 35% CPU, 40% Memory
   Savings: $100.00/month
   Risk: Low

Azure Rightsizing Opportunities: 3
1. vm-123 (Standard_D4s_v3 → Standard_D2s_v3)
   Current: 30% CPU, 35% Memory
   Savings: $150.00/month
   Risk: Medium

Total Potential Savings: $450.00/month
Implementation Effort: Low
Risk Level: Low
```

### `autoscaling`

Analyze and optimize autoscaling configurations.

```bash
python cli.py autoscaling [OPTIONS]
```

**Options:**
- `--providers LIST`: Specific providers
- `--scale-up-threshold FLOAT`: Scale up threshold (default: 0.8)
- `--scale-down-threshold FLOAT`: Scale down threshold (default: 0.3)
- `--min-instances INTEGER`: Minimum instances (default: 1)
- `--max-instances INTEGER`: Maximum instances (default: 10)
- `--output, -o PATH`: Output file path

**Examples:**
```bash
# Analyze autoscaling
python cli.py autoscaling

# Custom thresholds
python cli.py autoscaling --scale-up-threshold 0.7 --scale-down-threshold 0.4

# Specific providers
python cli.py autoscaling --providers aws
```

**Output:**
```
Autoscaling Analysis:
Analyzed 10 autoscaling groups

AWS Autoscaling Groups: 5
1. asg-web-app
   Current: 3-8 instances
   Recommended: 2-6 instances
   Savings: $150.00/month
   Reason: Over-provisioned

2. asg-api-service
   Current: 2-5 instances
   Recommended: 2-4 instances
   Savings: $75.00/month
   Reason: Conservative scaling

Azure Scale Sets: 3
1. vmss-frontend
   Current: 2-8 instances
   Recommended: 2-6 instances
   Savings: $100.00/month
   Reason: High idle time

Total Potential Savings: $325.00/month
```

## 📊 Forecasting Commands

### `forecast`

Generate cost forecasts.

```bash
python cli.py forecast [OPTIONS]
```

**Options:**
- `--days, -d INTEGER`: Days to forecast (default: 30)
- `--include-recommendations`: Include optimization impact
- `--confidence-level FLOAT`: Confidence level (default: 0.95)
- `--output, -o PATH`: Output file path
- `--format FORMAT`: Output format (json, csv, html)

**Examples:**
```bash
# Generate 30-day forecast
python cli.py forecast

# Generate 90-day forecast
python cli.py forecast --days 90

# Include optimization impact
python cli.py forecast --include-recommendations

# Custom confidence level
python cli.py forecast --confidence-level 0.9
```

**Output:**
```
Cost Forecast (30 days):
Base Forecast: $2,750.00
Confidence Interval: $2,500.00 - $3,000.00

Provider Breakdown:
AWS: $1,375.00 (+10.0%)
Azure: $880.00 (+10.0%)
GCP: $440.00 (+10.0%)

Optimization Impact:
Base Forecast: $2,750.00
Optimized Forecast: $2,300.00
Potential Savings: $450.00 (16.4%)

Trend Analysis:
- Daily Trend: +0.33%
- Weekly Trend: +2.3%
- Monthly Trend: +10.0%
- Seasonality: Detected

Forecast Factors:
- Historical patterns: Strong
- Seasonal trends: Moderate
- Growth rate: +10% monthly
- Optimization impact: -16.4%
```

## 📈 Reporting Commands

### `report`

Generate comprehensive reports.

```bash
python cli.py report [OPTIONS]
```

**Options:**
- `--type, -t TYPE`: Report type (comprehensive, summary, recommendations)
- `--format, -f FORMAT`: Output format (html, pdf, json)
- `--output, -o PATH`: Output file path
- `--template PATH`: Custom template path
- `--include-charts`: Include interactive charts
- `--include-recommendations`: Include optimization recommendations

**Examples:**
```bash
# Generate comprehensive HTML report
python cli.py report --type comprehensive --format html

# Generate PDF summary
python cli.py report --type summary --format pdf

# Generate JSON recommendations
python cli.py report --type recommendations --format json

# Custom output path
python cli.py report --output my_report.html
```

**Output:**
```
Report Generation:
Type: Comprehensive
Format: HTML
Template: Default

Generating report...
✅ Cost Analysis: Complete
✅ Optimization Recommendations: Complete
✅ Cost Forecast: Complete
✅ Interactive Charts: Complete
✅ Executive Summary: Complete

Report generated: finops_report_20240101_143022.html
File size: 2.5 MB
Charts included: 8
Recommendations: 15
```

### `dashboard`

Start web dashboard.

```bash
python cli.py dashboard [OPTIONS]
```

**Options:**
- `--host HOST`: Host to bind to (default: 0.0.0.0)
- `--port PORT`: Port to bind to (default: 5000)
- `--debug`: Enable debug mode
- `--config PATH`: Configuration file path
- `--ssl-cert PATH`: SSL certificate path
- `--ssl-key PATH`: SSL private key path

**Examples:**
```bash
# Start dashboard
python cli.py dashboard

# Custom host and port
python cli.py dashboard --host 127.0.0.1 --port 8080

# Enable debug mode
python cli.py dashboard --debug

# SSL enabled
python cli.py dashboard --ssl-cert cert.pem --ssl-key key.pem
```

**Output:**
```
Starting FinOps Dashboard...
Configuration loaded: finops_config.yml
Providers initialized: AWS, Azure, GCP
Web server starting...

Dashboard URL: http://0.0.0.0:5000
Default credentials: admin / admin123

Press Ctrl+C to stop the server
```

## 🔍 Monitoring Commands

### `health`

Check system health and status.

```bash
python cli.py health [OPTIONS]
```

**Options:**
- `--detailed`: Show detailed health information
- `--providers`: Check cloud provider health
- `--system`: Check system resources
- `--output, -o PATH`: Output file path

**Examples:**
```bash
# Check overall health
python cli.py health

# Detailed health check
python cli.py health --detailed

# Check specific components
python cli.py health --providers --system
```

**Output:**
```
System Health Check:
Overall Status: ✅ Healthy

Cloud Providers:
AWS: ✅ Connected (us-east-1)
Azure: ✅ Connected (subscription: abc123)
GCP: ⚠️ Warning (High latency)
Oracle: ❌ Disconnected

System Resources:
CPU Usage: 15% ✅
Memory Usage: 45% ✅
Disk Usage: 60% ✅
Network: ✅ Connected

Performance Metrics:
Cache Hit Rate: 85% ✅
Average Response Time: 250ms ✅
Error Rate: 0.1% ✅

Alerts: 0 active
```

### `metrics`

Show performance metrics.

```bash
python cli.py metrics [OPTIONS]
```

**Options:**
- `--period PERIOD`: Time period (1h, 24h, 7d, 30d)
- `--format FORMAT`: Output format (table, json, csv)
- `--output, -o PATH`: Output file path

**Examples:**
```bash
# Show current metrics
python cli.py metrics

# Last 24 hours
python cli.py metrics --period 24h

# JSON format
python cli.py metrics --format json
```

**Output:**
```
Performance Metrics (Last 24 hours):
Requests: 1,250
Successful: 1,245 (99.6%)
Failed: 5 (0.4%)

Response Times:
Average: 250ms
Median: 200ms
95th percentile: 500ms
99th percentile: 800ms

Cache Performance:
Hit Rate: 85%
Miss Rate: 15%
Total Hits: 1,062
Total Misses: 188

Resource Usage:
CPU: 15% average
Memory: 45% average
Disk I/O: 2.5 MB/s average

Errors by Type:
Authentication: 2
Network: 2
Configuration: 1
```

## 🔧 Utility Commands

### `version`

Show version information.

```bash
python cli.py version
```

**Output:**
```
FinOps Optimizer v2.0.0
Python: 3.9.7
Platform: Linux x86_64
Dependencies:
  - boto3: 1.26.0
  - azure-mgmt-compute: 29.0.0
  - google-cloud-compute: 1.0.0
  - oci: 2.100.0
```

### `info`

Show system information.

```bash
python cli.py info [OPTIONS]
```

**Options:**
- `--detailed`: Show detailed information
- `--providers`: Show provider information
- `--config`: Show configuration information

**Examples:**
```bash
# Basic information
python cli.py info

# Detailed information
python cli.py info --detailed

# Provider information
python cli.py info --providers
```

**Output:**
```
System Information:
Version: 1.0.0
Python: 3.9.7
Platform: Linux x86_64
Architecture: x86_64

Configuration:
Config File: finops_config.yml
Output Directory: ./finops_reports
Log Level: INFO

Cloud Providers:
AWS: Enabled (us-east-1)
Azure: Enabled (subscription: abc123)
GCP: Enabled (project: my-project)
Oracle: Disabled

Performance Settings:
Max Workers: 4
Cache TTL: 3600s
Batch Size: 100

Security Settings:
Encryption: Enabled
Authentication: Enabled
Rate Limiting: 100 req/hour
```

### `cleanup`

Clean up temporary files and caches.

```bash
python cli.py cleanup [OPTIONS]
```

**Options:**
- `--cache`: Clean cache files
- `--reports`: Clean old reports
- `--logs`: Clean log files
- `--all`: Clean all temporary files
- `--dry-run`: Show what would be cleaned

**Examples:**
```bash
# Clean all temporary files
python cli.py cleanup --all

# Clean only cache
python cli.py cleanup --cache

# Dry run
python cli.py cleanup --all --dry-run
```

**Output:**
```
Cleanup Operation:
Cache files: 15 files (2.5 MB)
Old reports: 8 files (15.2 MB)
Log files: 3 files (1.8 MB)

Cleaning up...
✅ Cache files removed: 15
✅ Old reports removed: 8
✅ Log files removed: 3

Total space freed: 19.5 MB
```

## 📝 Configuration Examples

### Basic Configuration

```bash
# Initialize configuration
python cli.py init

# Edit configuration file
nano finops_config.yml

# Validate configuration
python cli.py validate-config

# Test providers
python cli.py status
```

### Advanced Configuration

```bash
# Create custom configuration
python cli.py init --output custom_config.yml

# Use custom configuration
python cli.py --config custom_config.yml analyze

# Interactive setup
python cli.py init --interactive
```

### Automation Examples

```bash
# Daily cost analysis
python cli.py analyze --days 1 --output daily_costs.json

# Weekly optimization
python cli.py optimize --output weekly_optimization.json

# Monthly report
python cli.py report --type comprehensive --format html --output monthly_report.html

# Health check
python cli.py health --output health_status.json
```

## 🔧 Troubleshooting

### Common Issues

#### 1. Configuration Errors

```bash
# Validate configuration
python cli.py validate-config

# Check configuration syntax
python -c "import yaml; yaml.safe_load(open('finops_config.yml'))"
```

#### 2. Provider Connection Issues

```bash
# Test provider connections
python cli.py status --detailed

# Test credentials
python cli.py test-credentials

# Check environment variables
env | grep -E "(AWS|AZURE|GCP|ORACLE)"
```

#### 3. Permission Issues

```bash
# Check file permissions
ls -la finops_config.yml

# Fix permissions
chmod 600 finops_config.yml
```

### Debug Mode

```bash
# Enable verbose logging
python cli.py --verbose analyze

# Debug specific command
python cli.py --verbose --debug analyze
```

### Getting Help

```bash
# Show help for specific command
python cli.py analyze --help

# Show all commands
python cli.py --help

# Show version
python cli.py version
```

## 📊 Output Formats

### JSON Output

```bash
python cli.py analyze --format json --output results.json
```

### CSV Output

```bash
python cli.py cost-breakdown --format csv --output breakdown.csv
```

### YAML Output

```bash
python cli.py status --format yaml --output status.yml
```

---

**Need more help?** Check our [Tutorial Guide](tutorial.md) or [open an issue](https://github.com/manikantesh/finopsoptimizer/issues). 
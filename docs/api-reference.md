# API Reference

This document provides comprehensive API documentation for FinOps Optimizer.

## 📋 Table of Contents

- [Core Classes](#core-classes)
- [Cloud Providers](#cloud-providers)
- [Optimization Modules](#optimization-modules)
- [Web Dashboard](#web-dashboard)
- [Configuration](#configuration)
- [Utilities](#utilities)

## 🔧 Core Classes

### FinOpsOptimizer

The main class for cost optimization operations.

```python
from finops import FinOpsOptimizer
from finops.config import Config

# Initialize with default configuration
optimizer = FinOpsOptimizer()

# Initialize with custom configuration
config = Config()
config.aws.enabled = True
optimizer = FinOpsOptimizer(config)
```

#### Methods

##### `__init__(config=None)`

Initialize the FinOps optimizer.

**Parameters:**
- `config` (Config, optional): Configuration object. If None, loads from default locations.

**Example:**
```python
from finops import FinOpsOptimizer

optimizer = FinOpsOptimizer()
```

##### `analyze_costs(start_date=None, end_date=None)`

Analyze costs across all enabled cloud providers.

**Parameters:**
- `start_date` (datetime, optional): Start date for cost analysis. Defaults to 30 days ago.
- `end_date` (datetime, optional): End date for cost analysis. Defaults to now.

**Returns:**
- `Dict[str, Any]`: Dictionary containing cost analysis results

**Example:**
```python
from datetime import datetime, timedelta

# Analyze last 30 days
results = optimizer.analyze_costs()

# Analyze specific period
start_date = datetime.now() - timedelta(days=60)
end_date = datetime.now()
results = optimizer.analyze_costs(start_date, end_date)

print(f"Total cost: ${results['summary']['total_cost']:.2f}")
```

##### `generate_recommendations()`

Generate optimization recommendations across all providers.

**Returns:**
- `List[Dict[str, Any]]`: List of optimization recommendations

**Example:**
```python
recommendations = optimizer.generate_recommendations()

for rec in recommendations:
    print(f"Recommendation: {rec['description']}")
    print(f"Potential savings: ${rec['potential_savings']:.2f}")
    print(f"Priority: {rec['priority']}")
```

##### `allocate_costs(allocation_rules)`

Allocate costs based on provided rules.

**Parameters:**
- `allocation_rules` (Dict[str, Any]): Rules for cost allocation

**Returns:**
- `Dict[str, Any]`: Cost allocation results

**Example:**
```python
allocation_rules = {
    'method': 'tag_based',
    'tags': ['Environment', 'Project', 'Team'],
    'departments': ['Engineering', 'Marketing'],
    'projects': ['WebApp', 'MobileApp']
}

allocation_results = optimizer.allocate_costs(allocation_rules)

for dept, cost in allocation_results['allocated_costs']['by_department'].items():
    print(f"{dept}: ${cost:.2f}")
```

##### `forecast_costs(forecast_period=30, include_recommendations=True)`

Forecast future costs using machine learning.

**Parameters:**
- `forecast_period` (int): Number of days to forecast. Default: 30
- `include_recommendations` (bool): Include optimization impact. Default: True

**Returns:**
- `Dict[str, Any]`: Cost forecast results

**Example:**
```python
forecast = optimizer.forecast_costs(60)

print(f"Forecasted cost: ${forecast['total_forecast']:.2f}")
print(f"Confidence interval: {forecast['confidence_interval']}")
```

##### `generate_report(report_type="comprehensive", output_format="html")`

Generate comprehensive reports.

**Parameters:**
- `report_type` (str): Type of report ("comprehensive", "summary", "recommendations")
- `output_format` (str): Output format ("html", "pdf", "json")

**Returns:**
- `str`: Path to generated report

**Example:**
```python
# Generate comprehensive HTML report
report_path = optimizer.generate_report("comprehensive", "html")

# Generate PDF summary
pdf_path = optimizer.generate_report("summary", "pdf")

# Generate JSON recommendations
json_path = optimizer.generate_report("recommendations", "json")
```

##### `optimize_all(generate_report=True, save_results=True)`

Run complete optimization pipeline.

**Parameters:**
- `generate_report` (bool): Generate report after optimization. Default: True
- `save_results` (bool): Save results to file. Default: True

**Returns:**
- `Dict[str, Any]`: Complete optimization results

**Example:**
```python
results = optimizer.optimize_all()

print(f"Total recommendations: {results['summary']['total_recommendations']}")
print(f"Potential savings: ${results['summary']['total_potential_savings']:.2f}")
print(f"Report generated: {results['report_path']}")
```

##### `get_provider_status()`

Get status of all cloud providers.

**Returns:**
- `Dict[str, bool]`: Provider status dictionary

**Example:**
```python
status = optimizer.get_provider_status()

for provider, is_connected in status.items():
    print(f"{provider}: {'Connected' if is_connected else 'Disconnected'}")
```

##### `validate_credentials()`

Validate cloud provider credentials.

**Returns:**
- `Dict[str, Dict[str, Any]]`: Validation results for each provider

**Example:**
```python
validation = optimizer.validate_credentials()

for provider, result in validation.items():
    if result['valid']:
        print(f"{provider}: Valid credentials")
    else:
        print(f"{provider}: {result['error']}")
```

## ☁️ Cloud Providers

### AWSProvider

AWS cloud provider implementation.

```python
from finops.aws import AWSProvider
from finops.config import AWSConfig

config = AWSConfig()
config.enabled = True
config.region = "us-east-1"

aws_provider = AWSProvider(config)
```

#### Methods

##### `analyze_costs(start_date, end_date)`

Analyze AWS costs.

**Parameters:**
- `start_date` (datetime): Start date
- `end_date` (datetime): End date

**Returns:**
- `Dict[str, Any]`: AWS cost analysis results

##### `get_resource_inventory()`

Get AWS resource inventory.

**Returns:**
- `List[Dict[str, Any]]`: List of AWS resources

##### `get_rightsizing_recommendations(resources)`

Get rightsizing recommendations for AWS resources.

**Parameters:**
- `resources` (List[Dict[str, Any]]): List of resources

**Returns:**
- `List[Dict[str, Any]]`: Rightsizing recommendations

### AzureProvider

Azure cloud provider implementation.

```python
from finops.azure import AzureProvider
from finops.config import AzureConfig

config = AzureConfig()
config.enabled = True
config.subscription_id = "your-subscription-id"

azure_provider = AzureProvider(config)
```

### GCPProvider

GCP cloud provider implementation.

```python
from finops.gcp import GCPProvider
from finops.config import GCPConfig

config = GCPConfig()
config.enabled = True
config.project_id = "your-project-id"

gcp_provider = GCPProvider(config)
```

### OracleProvider

Oracle Cloud provider implementation.

```python
from finops.oracle import OracleProvider
from finops.config import OracleConfig

config = OracleConfig()
config.enabled = True
config.tenancy_id = "your-tenancy-id"
config.user_id = "your-user-id"
config.fingerprint = "your-fingerprint"
config.private_key_path = "/path/to/private_key.pem"

oracle_provider = OracleProvider(config)
```

## ⚙️ Optimization Modules

### RightsizingAnalyzer

Analyzes resources for rightsizing opportunities.

```python
from finops.rightsizing import RightsizingAnalyzer

analyzer = RightsizingAnalyzer(config)
```

#### Methods

##### `analyze_provider(provider, cost_data)`

Analyze a specific cloud provider for rightsizing opportunities.

**Parameters:**
- `provider`: Cloud provider instance
- `cost_data` (Dict[str, Any]): Cost data for the provider

**Returns:**
- `List[Dict[str, Any]]`: Rightsizing recommendations

##### `analyze_resources(resources)`

Analyze specific resources for rightsizing.

**Parameters:**
- `resources` (List[Dict[str, Any]]): List of resources

**Returns:**
- `List[Dict[str, Any]]`: Rightsizing recommendations

### AutoscalingOptimizer

Optimizes autoscaling configurations.

```python
from finops.autoscaling import AutoscalingOptimizer

optimizer = AutoscalingOptimizer(config)
```

#### Methods

##### `analyze_provider(provider, cost_data)`

Analyze autoscaling groups for optimization opportunities.

**Parameters:**
- `provider`: Cloud provider instance
- `cost_data` (Dict[str, Any]): Cost data for the provider

**Returns:**
- `List[Dict[str, Any]]`: Autoscaling recommendations

##### `optimize_scaling_policy(policy, metrics)`

Optimize a specific scaling policy.

**Parameters:**
- `policy` (Dict[str, Any]): Current scaling policy
- `metrics` (Dict[str, Any]): Performance metrics

**Returns:**
- `Dict[str, Any]`: Optimized scaling policy

### CostAllocator

Allocates costs based on various methods.

```python
from finops.cost_allocation import CostAllocator

allocator = CostAllocator(config)
```

#### Methods

##### `allocate_costs(cost_data, allocation_rules)`

Allocate costs based on rules.

**Parameters:**
- `cost_data` (Dict[str, Any]): Cost data
- `allocation_rules` (Dict[str, Any]): Allocation rules

**Returns:**
- `Dict[str, Any]`: Allocation results

##### `generate_recommendations(cost_data)`

Generate cost allocation recommendations.

**Parameters:**
- `cost_data` (Dict[str, Any]): Cost data

**Returns:**
- `List[Dict[str, Any]]`: Allocation recommendations

### CostForecaster

Forecasts future costs using machine learning.

```python
from finops.forecasting import CostForecaster

forecaster = CostForecaster(config)
```

#### Methods

##### `forecast_costs(cost_data, forecast_period=30)`

Forecast costs for a specific period.

**Parameters:**
- `cost_data` (Dict[str, Any]): Historical cost data
- `forecast_period` (int): Number of days to forecast

**Returns:**
- `Dict[str, Any]`: Forecast results

##### `evaluate_model(cost_data)`

Evaluate the forecasting model performance.

**Parameters:**
- `cost_data` (Dict[str, Any]): Cost data

**Returns:**
- `Dict[str, Any]`: Model evaluation metrics

## 🌐 Web Dashboard

### FinOpsWebApp

Flask web application for the dashboard.

```python
from web.app import FinOpsWebApp

app = FinOpsWebApp(config_path="finops_config.yml")
```

#### Methods

##### `run(host='0.0.0.0', port=5000, debug=False)`

Run the web application.

**Parameters:**
- `host` (str): Host to bind to
- `port` (int): Port to bind to
- `debug` (bool): Enable debug mode

**Example:**
```python
app.run(host='0.0.0.0', port=5000, debug=False)
```

### API Endpoints

#### GET `/api/costs`

Get cost analysis data.

**Query Parameters:**
- `days` (int): Number of days to analyze. Default: 30

**Response:**
```json
{
  "summary": {
    "total_cost": 1000.0,
    "providers_analyzed": ["aws", "azure"]
  },
  "aws": {
    "total_cost": 600.0,
    "service_breakdown": {...}
  },
  "azure": {
    "total_cost": 400.0,
    "service_breakdown": {...}
  }
}
```

#### GET `/api/recommendations`

Get optimization recommendations.

**Response:**
```json
[
  {
    "type": "rightsizing",
    "description": "Downsize instance i-123456",
    "potential_savings": 50.0,
    "priority": "high",
    "provider": "aws"
  }
]
```

#### GET `/api/forecast`

Get cost forecast.

**Query Parameters:**
- `days` (int): Number of days to forecast. Default: 30

**Response:**
```json
{
  "total_forecast": 1200.0,
  "confidence_interval": [1100.0, 1300.0],
  "provider_forecasts": {...}
}
```

#### POST `/api/optimize`

Run complete optimization.

**Response:**
```json
{
  "summary": {
    "total_recommendations": 5,
    "total_potential_savings": 200.0
  },
  "recommendations": [...],
  "report_path": "/path/to/report.html"
}
```

#### POST `/api/reports`

Generate report.

**Request Body:**
```json
{
  "type": "comprehensive",
  "format": "html"
}
```

**Response:**
```json
{
  "report_path": "/path/to/report.html"
}
```

#### GET `/api/status`

Get provider status.

**Response:**
```json
{
  "aws": true,
  "azure": false,
  "gcp": true
}
```

#### POST `/api/allocate`

Allocate costs.

**Request Body:**
```json
{
  "method": "tag_based",
  "tags": ["Environment", "Project"],
  "departments": ["Engineering", "Marketing"]
}
```

**Response:**
```json
{
  "allocated_costs": {
    "by_department": {
      "Engineering": 600.0,
      "Marketing": 400.0
    }
  }
}
```

## ⚙️ Configuration

### Config

Configuration management class.

```python
from finops.config import Config, load_config, validate_config
```

#### Methods

##### `load_config(config_path=None)`

Load configuration from file or environment.

**Parameters:**
- `config_path` (str, optional): Path to configuration file

**Returns:**
- `Config`: Configuration object

**Example:**
```python
# Load default configuration
config = load_config()

# Load from specific file
config = load_config("custom_config.yml")
```

##### `validate_config(config)`

Validate configuration object.

**Parameters:**
- `config` (Config): Configuration object

**Returns:**
- `Dict[str, Any]`: Validation results

**Example:**
```python
validation = validate_config(config)

if validation['valid']:
    print("Configuration is valid")
else:
    print("Configuration errors:", validation['errors'])
```

## 🔧 Utilities

### PerformanceOptimizer

Performance optimization utilities.

```python
from finops.performance import PerformanceOptimizer

perf_optimizer = PerformanceOptimizer(config)
```

#### Methods

##### `parallel_execute(tasks, timeout=None)`

Execute tasks in parallel.

**Parameters:**
- `tasks` (List[Callable]): List of callable tasks
- `timeout` (int, optional): Timeout in seconds

**Returns:**
- `List[Any]`: Results from tasks

##### `batch_process(items, batch_size, processor)`

Process items in batches.

**Parameters:**
- `items` (List[Any]): Items to process
- `batch_size` (int): Size of each batch
- `processor` (Callable): Function to process each batch

**Returns:**
- `List[Any]`: Processed results

##### `get_performance_metrics()`

Get performance metrics.

**Returns:**
- `Dict[str, Any]`: Performance metrics

### SecurityManager

Security management utilities.

```python
from finops.security import SecurityManager

security_manager = SecurityManager(config)
```

#### Methods

##### `encrypt_sensitive_data(data)`

Encrypt sensitive data.

**Parameters:**
- `data` (str): Data to encrypt

**Returns:**
- `str`: Encrypted data

##### `decrypt_sensitive_data(encrypted_data)`

Decrypt sensitive data.

**Parameters:**
- `encrypted_data` (str): Encrypted data

**Returns:**
- `str`: Decrypted data

##### `hash_password(password)`

Hash password securely.

**Parameters:**
- `password` (str): Plain text password

**Returns:**
- `str`: Hashed password

##### `verify_password(password, hashed_password)`

Verify password against hash.

**Parameters:**
- `password` (str): Plain text password
- `hashed_password` (str): Hashed password

**Returns:**
- `bool`: True if password matches

### HealthChecker

Health check and monitoring utilities.

```python
from finops.monitoring import HealthChecker

health_checker = HealthChecker(config)
```

#### Methods

##### `check_health()`

Perform comprehensive health check.

**Returns:**
- `Dict[str, Any]`: Health check results

##### `get_metrics()`

Get current metrics.

**Returns:**
- `Dict[str, Any]`: Current metrics

##### `get_alerts()`

Get current alerts.

**Returns:**
- `List[Dict[str, Any]]`: List of alerts

## 📊 Data Structures

### Cost Analysis Result

```python
{
    "summary": {
        "total_cost": 1000.0,
        "providers_analyzed": ["aws", "azure"],
        "analysis_period": {
            "start_date": "2024-01-01T00:00:00",
            "end_date": "2024-01-31T23:59:59"
        }
    },
    "aws": {
        "total_cost": 600.0,
        "service_breakdown": {
            "EC2": 400.0,
            "S3": 150.0,
            "RDS": 50.0
        },
        "resources": [...],
        "daily_costs": [...]
    },
    "azure": {
        "total_cost": 400.0,
        "service_breakdown": {...},
        "resources": [...],
        "daily_costs": [...]
    }
}
```

### Recommendation

```python
{
    "type": "rightsizing",
    "resource_id": "i-123456",
    "resource_type": "EC2",
    "description": "Downsize instance from t3.large to t3.medium",
    "current_config": {
        "instance_type": "t3.large",
        "cost": 100.0
    },
    "recommended_config": {
        "instance_type": "t3.medium",
        "cost": 50.0
    },
    "potential_savings": 50.0,
    "priority": "high",
    "provider": "aws",
    "confidence": 0.9,
    "implementation_effort": "low"
}
```

### Cost Forecast

```python
{
    "total_forecast": 1200.0,
    "confidence_interval": [1100.0, 1300.0],
    "forecast_period": 30,
    "provider_forecasts": {
        "aws": {
            "total_forecast": 720.0,
            "trend_analysis": {
                "trend_direction": "increasing",
                "volatility": 0.1
            }
        },
        "azure": {
            "total_forecast": 480.0,
            "trend_analysis": {...}
        }
    },
    "recommendations_impact": {
        "base_forecast": 1200.0,
        "optimized_forecast": 1000.0,
        "total_savings": 200.0,
        "savings_percentage": 16.7
    }
}
```

## 🔄 Error Handling

### Common Exceptions

#### `FinOpsError`

Base exception for FinOps Optimizer.

```python
from finops.exceptions import FinOpsError

try:
    results = optimizer.analyze_costs()
except FinOpsError as e:
    print(f"FinOps error: {e}")
```

#### `ConfigurationError`

Configuration-related errors.

```python
from finops.exceptions import ConfigurationError

try:
    config = load_config("invalid_config.yml")
except ConfigurationError as e:
    print(f"Configuration error: {e}")
```

#### `ProviderError`

Cloud provider-related errors.

```python
from finops.exceptions import ProviderError

try:
    aws_results = aws_provider.analyze_costs(start_date, end_date)
except ProviderError as e:
    print(f"AWS provider error: {e}")
```

### Error Response Format

```python
{
    "error": "Error message",
    "error_type": "ProviderError",
    "provider": "aws",
    "timestamp": "2024-01-01T12:00:00Z",
    "details": {
        "additional_info": "More details about the error"
    }
}
```

## 📝 Examples

### Complete Optimization Pipeline

```python
from finops import FinOpsOptimizer
from datetime import datetime, timedelta

# Initialize optimizer
optimizer = FinOpsOptimizer()

# Analyze costs
start_date = datetime.now() - timedelta(days=30)
end_date = datetime.now()
cost_results = optimizer.analyze_costs(start_date, end_date)

# Generate recommendations
recommendations = optimizer.generate_recommendations()

# Forecast costs
forecast = optimizer.forecast_costs(30)

# Generate report
report_path = optimizer.generate_report("comprehensive", "html")

# Run complete optimization
results = optimizer.optimize_all()

print(f"Analysis complete:")
print(f"- Total cost: ${cost_results['summary']['total_cost']:.2f}")
print(f"- Recommendations: {len(recommendations)}")
print(f"- Forecast: ${forecast['total_forecast']:.2f}")
print(f"- Report: {report_path}")
```

### Custom Configuration

```python
from finops import FinOpsOptimizer
from finops.config import Config

# Create custom configuration
config = Config()
config.aws.enabled = True
config.aws.region = "us-west-2"
config.optimization.cpu_utilization_threshold = 0.8
config.optimization.memory_utilization_threshold = 0.9
config.output_dir = "/custom/reports"
config.log_level = "DEBUG"

# Use custom configuration
optimizer = FinOpsOptimizer(config)
```

### Web Dashboard Integration

```python
from web.app import FinOpsWebApp

# Create web application
app = FinOpsWebApp("finops_config.yml")

# Run in production
app.run(host='0.0.0.0', port=8000, debug=False)
```

---

**Need more examples?** Check our [Tutorial Guide](tutorial.md) or [open an issue](https://github.com/manikantesh/finopsoptimizer/issues) for specific use cases. 
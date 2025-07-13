# Tutorial: Getting Started with FinOps Optimizer

This tutorial will guide you through setting up and using FinOps Optimizer to optimize costs across your multi-cloud infrastructure.

## Prerequisites

Before starting this tutorial, ensure you have:

- Python 3.8 or higher installed
- Access to AWS, Azure, and/or GCP accounts
- Proper credentials configured for your cloud providers
- Basic understanding of cloud cost management concepts

## Installation

First, install FinOps Optimizer:

```bash
pip install finops-optimizer
```

Or install from source:

```bash
git clone https://github.com/manikantesh/finopsoptimizerdocs.git
cd finopsoptimizer
pip install -e .
```

## Quick Start

### 1. Basic Configuration

Create a configuration file `config.yaml`:

```yaml
providers:
  aws:
    enabled: true
    regions: ["us-east-1", "us-west-2"]
    credentials:
      access_key_id: "your-access-key"
      secret_access_key: "your-secret-key"
  
  azure:
    enabled: true
    subscription_id: "your-subscription-id"
    tenant_id: "your-tenant-id"
    client_id: "your-client-id"
    client_secret: "your-client-secret"
  
  gcp:
    enabled: true
    project_id: "your-project-id"
    service_account_key: "path/to/service-account.json"

optimization:
  rightsizing:
    enabled: true
    min_savings_threshold: 10.0
  
  autoscaling:
    enabled: true
    scale_down_threshold: 30.0
  
  cost_allocation:
    enabled: true
    tags_required: ["Environment", "Project", "Team"]

monitoring:
  enabled: true
  metrics_retention_days: 30
  alert_threshold: 20.0

reporting:
  enabled: true
  schedule: "0 9 * * 1"  # Every Monday at 9 AM
  formats: ["html", "pdf", "csv"]
```

### 2. Initialize the Optimizer

```python
from finops import FinOpsOptimizer

# Initialize with configuration
optimizer = FinOpsOptimizer(config_path="config.yaml")

# Or initialize programmatically
optimizer = FinOpsOptimizer(
    providers={
        "aws": {"enabled": True, "regions": ["us-east-1"]},
        "azure": {"enabled": True},
        "gcp": {"enabled": True}
    }
)
```

### 3. Run Cost Analysis

```python
# Analyze current costs
analysis = optimizer.analyze_costs()

print(f"Total monthly cost: ${analysis.total_cost:.2f}")
print(f"Potential savings: ${analysis.potential_savings:.2f}")
print(f"Optimization opportunities: {len(analysis.recommendations)}")
```

### 4. Generate Optimization Recommendations

```python
# Get rightsizing recommendations
rightsizing = optimizer.get_rightsizing_recommendations()

for rec in rightsizing:
    print(f"Instance: {rec.instance_id}")
    print(f"Current cost: ${rec.current_cost:.2f}/month")
    print(f"Recommended cost: ${rec.recommended_cost:.2f}/month")
    print(f"Potential savings: ${rec.savings:.2f}/month")
    print("---")

# Get autoscaling recommendations
autoscaling = optimizer.get_autoscaling_recommendations()

for rec in autoscaling:
    print(f"Resource: {rec.resource_id}")
    print(f"Current utilization: {rec.current_utilization:.1f}%")
    print(f"Recommended action: {rec.recommended_action}")
    print("---")
```

### 5. Apply Optimizations

```python
# Apply rightsizing recommendations (dry run first)
results = optimizer.apply_rightsizing_recommendations(dry_run=True)

for result in results:
    print(f"Instance: {result.instance_id}")
    print(f"Status: {result.status}")
    print(f"Estimated savings: ${result.estimated_savings:.2f}")
    print("---")

# Apply for real (be careful!)
# results = optimizer.apply_rightsizing_recommendations(dry_run=False)
```

### 6. Set Up Monitoring

```python
# Start monitoring
optimizer.start_monitoring()

# Check monitoring status
status = optimizer.get_monitoring_status()
print(f"Monitoring active: {status.active}")
print(f"Last check: {status.last_check}")
print(f"Alerts: {len(status.alerts)}")
```

### 7. Generate Reports

```python
# Generate cost report
report = optimizer.generate_cost_report(
    start_date="2024-01-01",
    end_date="2024-01-31",
    format="html"
)

print(f"Report generated: {report.file_path}")
print(f"Report size: {report.size} bytes")
```

## Advanced Usage

### Custom Cost Allocation

```python
# Define custom cost allocation rules
allocation_rules = {
    "by_tag": {
        "Environment": ["dev", "staging", "prod"],
        "Team": ["frontend", "backend", "data"]
    },
    "by_service": {
        "compute": ["ec2", "lambda", "ecs"],
        "storage": ["s3", "ebs", "rds"],
        "network": ["vpc", "elb", "cloudfront"]
    }
}

optimizer.set_cost_allocation_rules(allocation_rules)
allocation = optimizer.allocate_costs()
```

### Custom Optimization Strategies

```python
# Define custom optimization strategies
custom_strategy = {
    "name": "conservative_rightsizing",
    "rules": [
        {
            "condition": "cpu_utilization < 20 and memory_utilization < 30",
            "action": "downsize",
            "savings_threshold": 15.0
        },
        {
            "condition": "cost_per_hour > 2.0 and utilization < 50",
            "action": "investigate",
            "priority": "high"
        }
    ]
}

optimizer.add_custom_strategy(custom_strategy)
recommendations = optimizer.get_custom_recommendations()
```

### Multi-Cloud Cost Comparison

```python
# Compare costs across providers
comparison = optimizer.compare_provider_costs()

for provider, costs in comparison.items():
    print(f"{provider.upper()}:")
    print(f"  Total cost: ${costs.total:.2f}")
    print(f"  Compute cost: ${costs.compute:.2f}")
    print(f"  Storage cost: ${costs.storage:.2f}")
    print(f"  Network cost: ${costs.network:.2f}")
    print("---")
```

## Best Practices

### 1. Start Small

- Begin with a single cloud provider
- Test optimizations in non-production environments
- Use dry-run mode before applying changes

### 2. Monitor Continuously

- Set up automated monitoring
- Configure alerts for cost spikes
- Review reports regularly

### 3. Tag Resources Properly

- Implement consistent tagging strategy
- Use tags for cost allocation
- Regularly audit tag compliance

### 4. Regular Reviews

- Schedule weekly cost reviews
- Track optimization effectiveness
- Adjust strategies based on results

### 5. Security First

- Use IAM roles and service accounts
- Implement least-privilege access
- Regularly rotate credentials

## Troubleshooting

### Common Issues

1. **Authentication Errors**
   - Verify credentials are correct
   - Check IAM permissions
   - Ensure service accounts have proper roles

2. **Missing Data**
   - Enable billing exports
   - Configure cost allocation tags
   - Check API quotas and limits

3. **Performance Issues**
   - Use appropriate regions
   - Implement caching
   - Optimize API calls

### Getting Help

- Check the [Troubleshooting Guide](troubleshooting.md)
- Review [API Reference](api-reference.md)
- Consult [CLI Reference](cli-reference.md)
- Open an issue on GitHub

## Next Steps

Now that you've completed the tutorial:

1. **Explore Advanced Features**: Check out the [API Reference](api-reference.md) for detailed information
2. **Set Up Monitoring**: Configure automated monitoring and alerts
3. **Customize Strategies**: Develop custom optimization strategies for your use case
4. **Join the Community**: Contribute to the project and share your experiences

For more information, see the [Configuration Guide](configuration.md) and [Security Best Practices](security.md). 
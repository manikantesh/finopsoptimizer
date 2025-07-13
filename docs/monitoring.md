# Monitoring and Alerting

FinOps Optimizer provides comprehensive monitoring and alerting capabilities to help you track cost optimization performance and respond to issues proactively.

## Overview

The monitoring system tracks:

- **Cost metrics**: Real-time cost tracking and trend analysis
- **Optimization performance**: Savings achieved and recommendations applied
- **Resource utilization**: CPU, memory, and storage usage patterns
- **Alert conditions**: Cost spikes, underutilized resources, and security issues
- **System health**: API availability and performance metrics

## Configuration

### Basic Monitoring Setup

```yaml
monitoring:
  enabled: true
  metrics_retention_days: 30
  alert_threshold: 20.0
  check_interval_minutes: 15
  
  # Cost monitoring
  cost_monitoring:
    enabled: true
    daily_budget: 1000.0
    weekly_budget: 7000.0
    monthly_budget: 30000.0
    
  # Performance monitoring
  performance_monitoring:
    enabled: true
    cpu_threshold: 80.0
    memory_threshold: 85.0
    storage_threshold: 90.0
    
  # Security monitoring
  security_monitoring:
    enabled: true
    check_public_resources: true
    check_unencrypted_storage: true
    check_iam_permissions: true
```

### Advanced Configuration

```yaml
monitoring:
  # Custom alert rules
  alert_rules:
    - name: "cost_spike"
      condition: "daily_cost > 1.5 * avg_daily_cost"
      severity: "high"
      channels: ["email", "slack"]
      
    - name: "underutilized_resource"
      condition: "cpu_utilization < 10 and cost_per_hour > 1.0"
      severity: "medium"
      channels: ["email"]
      
    - name: "security_violation"
      condition: "public_resource_detected or unencrypted_storage"
      severity: "critical"
      channels: ["email", "slack", "pagerduty"]
  
  # Notification channels
  notifications:
    email:
      enabled: true
      recipients: ["finops@company.com", "devops@company.com"]
      smtp_server: "smtp.company.com"
      smtp_port: 587
      
    slack:
      enabled: true
      webhook_url: "https://hooks.slack.com/services/..."
      channel: "#finops-alerts"
      
    pagerduty:
      enabled: true
      service_key: "your-service-key"
```

## Usage

### Starting Monitoring

```python
from finops import FinOpsOptimizer

optimizer = FinOpsOptimizer(config_path="config.yaml")

# Start monitoring
optimizer.start_monitoring()

# Check status
status = optimizer.get_monitoring_status()
print(f"Monitoring active: {status.active}")
print(f"Last check: {status.last_check}")
print(f"Active alerts: {len(status.alerts)}")
```

### Monitoring Status

```python
# Get detailed monitoring status
status = optimizer.get_monitoring_status()

print("=== Monitoring Status ===")
print(f"Active: {status.active}")
print(f"Last check: {status.last_check}")
print(f"Next check: {status.next_check}")
print(f"Metrics collected: {status.metrics_count}")
print(f"Active alerts: {len(status.alerts)}")

# Check specific metrics
cost_metrics = optimizer.get_cost_metrics(days=7)
print(f"Average daily cost: ${cost_metrics.average_daily_cost:.2f}")
print(f"Cost trend: {cost_metrics.trend}")

utilization_metrics = optimizer.get_utilization_metrics()
print(f"Average CPU utilization: {utilization_metrics.avg_cpu:.1f}%")
print(f"Average memory utilization: {utilization_metrics.avg_memory:.1f}%")
```

### Alert Management

```python
# Get active alerts
alerts = optimizer.get_active_alerts()

for alert in alerts:
    print(f"Alert: {alert.name}")
    print(f"Severity: {alert.severity}")
    print(f"Message: {alert.message}")
    print(f"Created: {alert.created_at}")
    print(f"Status: {alert.status}")
    print("---")

# Acknowledge alert
optimizer.acknowledge_alert(alert_id="alert-123")

# Resolve alert
optimizer.resolve_alert(alert_id="alert-123", resolution="Cost spike was due to legitimate traffic increase")
```

### Custom Alert Rules

```python
# Create custom alert rule
custom_rule = {
    "name": "custom_cost_threshold",
    "condition": "daily_cost > 2000.0",
    "severity": "high",
    "channels": ["email"],
    "description": "Daily cost exceeded $2000 threshold"
}

optimizer.add_alert_rule(custom_rule)

# List all alert rules
rules = optimizer.get_alert_rules()
for rule in rules:
    print(f"Rule: {rule.name}")
    print(f"Condition: {rule.condition}")
    print(f"Severity: {rule.severity}")
    print("---")
```

## Metrics and Dashboards

### Available Metrics

1. **Cost Metrics**
   - Daily, weekly, monthly costs
   - Cost trends and forecasts
   - Savings achieved
   - Cost by service, region, tag

2. **Performance Metrics**
   - CPU utilization
   - Memory utilization
   - Storage utilization
   - Network usage

3. **Optimization Metrics**
   - Recommendations generated
   - Recommendations applied
   - Savings realized
   - Optimization success rate

4. **Security Metrics**
   - Public resources detected
   - Unencrypted storage
   - IAM permission issues
   - Compliance violations

### Dashboard Access

```python
# Generate monitoring dashboard
dashboard = optimizer.generate_monitoring_dashboard(
    time_range="last_30_days",
    include_metrics=["cost", "performance", "optimization", "security"]
)

print(f"Dashboard URL: {dashboard.url}")
print(f"Dashboard file: {dashboard.file_path}")
```

### Custom Dashboards

```python
# Create custom dashboard
custom_dashboard = {
    "name": "Executive Summary",
    "metrics": [
        {
            "name": "Total Monthly Cost",
            "type": "cost",
            "aggregation": "sum",
            "period": "month"
        },
        {
            "name": "Savings Achieved",
            "type": "optimization",
            "aggregation": "sum",
            "period": "month"
        },
        {
            "name": "Resource Utilization",
            "type": "performance",
            "aggregation": "average",
            "period": "day"
        }
    ],
    "layout": "grid",
    "refresh_interval": 300
}

dashboard = optimizer.create_custom_dashboard(custom_dashboard)
```

## Integration with External Systems

### Prometheus Integration

```python
# Export metrics to Prometheus
optimizer.export_metrics_to_prometheus(
    endpoint="http://prometheus:9090",
    job_name="finops-optimizer"
)
```

### Grafana Integration

```python
# Create Grafana dashboard
grafana_dashboard = optimizer.create_grafana_dashboard(
    grafana_url="http://grafana:3000",
    api_key="your-grafana-api-key"
)
```

### Slack Integration

```python
# Send custom notification to Slack
optimizer.send_slack_notification(
    message="Cost optimization completed",
    channel="#finops",
    attachments=[
        {
            "title": "Monthly Savings",
            "value": "$1,234.56",
            "color": "good"
        }
    ]
)
```

## Best Practices

### 1. Set Appropriate Thresholds

- Start with conservative thresholds
- Adjust based on historical data
- Consider business context

### 2. Use Multiple Channels

- Email for important alerts
- Slack for team notifications
- PagerDuty for critical issues

### 3. Regular Review

- Review alert effectiveness weekly
- Adjust rules based on false positives
- Archive resolved alerts

### 4. Performance Optimization

- Use appropriate check intervals
- Implement metric retention policies
- Monitor monitoring system performance

### 5. Security Considerations

- Secure notification channels
- Implement alert authentication
- Audit alert access

## Troubleshooting

### Common Issues

1. **High Alert Volume**
   - Adjust thresholds
   - Implement alert grouping
   - Use alert suppression

2. **Missing Metrics**
   - Check API permissions
   - Verify data sources
   - Review collection intervals

3. **Performance Issues**
   - Reduce check frequency
   - Implement caching
   - Use async processing

### Getting Help

- Check the [Troubleshooting Guide](troubleshooting.md)
- Review monitoring logs
- Consult [API Reference](api-reference.md)
- Open an issue on GitHub

For more information, see the [Configuration Guide](configuration.md) and [Security Best Practices](security.md). 
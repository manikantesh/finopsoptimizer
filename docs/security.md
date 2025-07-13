# Security Guide

This guide covers security best practices, configuration, and features for FinOps Optimizer.

## 📋 Security Overview

FinOps Optimizer implements enterprise-grade security features to protect sensitive cloud provider credentials, cost data, and user information.

## 🔒 Security Features

### 1. Data Encryption

#### AES-256 Encryption

```python
from finops.security import SecurityManager

security_manager = SecurityManager()

# Encrypt sensitive data
encrypted_data = security_manager.encrypt_sensitive_data("your-secret-key")

# Decrypt data
decrypted_data = security_manager.decrypt_sensitive_data(encrypted_data)
```

#### Configuration Encryption

```yaml
# finops_config.yml
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
```

### 2. Authentication System

#### Password Hashing

```python
from werkzeug.security import generate_password_hash, check_password_hash

# Hash password
hashed_password = generate_password_hash("user_password")

# Verify password
is_valid = check_password_hash(hashed_password, "user_password")
```

#### Session Management

```python
# Session configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=1)
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
```

### 3. API Key Management

#### API Key Generation

```python
import secrets

# Generate secure API key
api_key = secrets.token_urlsafe(32)

# Hash API key for storage
api_key_hash = generate_password_hash(api_key)
```

#### API Key Validation

```python
def validate_api_key(api_key):
    # Validate API key format
    if len(api_key) < 32:
        return False
    
    # Check against stored hash
    stored_hash = get_stored_api_key_hash()
    return check_password_hash(stored_hash, api_key)
```

### 4. Input Validation

#### Sanitization

```python
import re
from html import escape

def sanitize_input(input_data):
    """Sanitize user input to prevent injection attacks."""
    if isinstance(input_data, str):
        # Remove potentially dangerous characters
        sanitized = re.sub(r'[<>"\']', '', input_data)
        return escape(sanitized)
    return input_data

def validate_email(email):
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None
```

#### SQL Injection Prevention

```python
# Use parameterized queries
def get_user_by_id(user_id):
    query = "SELECT * FROM users WHERE id = %s"
    cursor.execute(query, (user_id,))
    return cursor.fetchone()
```

### 5. Rate Limiting

#### Request Rate Limiting

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

@app.route('/api/costs')
@limiter.limit("10 per minute")
@login_required
def get_costs():
    # API endpoint with rate limiting
    pass
```

#### Configuration

```yaml
security:
  rate_limiting:
    enabled: true
    default_limit: "100 per hour"
    api_limit: "10 per minute"
    login_limit: "5 per minute"
    
    # IP-based limits
    ip_limits:
      default: "100 per hour"
      api: "10 per minute"
      login: "5 per minute"
```

### 6. Audit Logging

#### Security Event Logging

```python
import logging
from datetime import datetime

# Configure security logger
security_logger = logging.getLogger('security')
security_logger.setLevel(logging.INFO)

def log_security_event(event_type, user_id, details):
    """Log security events."""
    log_entry = {
        'timestamp': datetime.utcnow().isoformat(),
        'event_type': event_type,
        'user_id': user_id,
        'ip_address': request.remote_addr,
        'user_agent': request.headers.get('User-Agent'),
        'details': details
    }
    security_logger.info(f"SECURITY_EVENT: {log_entry}")
```

#### Audit Trail

```python
def audit_user_action(action, resource, user_id):
    """Audit user actions."""
    audit_entry = {
        'timestamp': datetime.utcnow(),
        'action': action,
        'resource': resource,
        'user_id': user_id,
        'ip_address': request.remote_addr,
        'session_id': session.get('session_id')
    }
    
    # Store audit entry
    store_audit_entry(audit_entry)
```

## 🔐 Configuration Security

### 1. Environment Variables

```bash
# Set secure environment variables
export FINOPS_SECRET_KEY="your-secure-secret-key"
export FINOPS_AWS_ACCESS_KEY_ID="your-aws-access-key"
export FINOPS_AWS_SECRET_ACCESS_KEY="your-aws-secret-key"
export FINOPS_AZURE_CLIENT_ID="your-azure-client-id"
export FINOPS_AZURE_CLIENT_SECRET="your-azure-client-secret"
```

### 2. Configuration File Security

```bash
# Set proper file permissions
chmod 600 finops_config.yml
chown finops:finops finops_config.yml

# Encrypt configuration file
gpg --encrypt --recipient your-email@domain.com finops_config.yml
```

### 3. SSL/TLS Configuration

```python
# SSL configuration
ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
ssl_context.load_cert_chain('cert.pem', 'key.pem')

app.run(
    host='0.0.0.0',
    port=5000,
    ssl_context=ssl_context
)
```

## 🛡️ Cloud Provider Security

### 1. AWS Security

#### IAM Best Practices

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
      "Resource": "*",
      "Condition": {
        "StringEquals": {
          "aws:RequestTag/Environment": "production"
        }
      }
    }
  ]
}
```

#### Credential Rotation

```python
def rotate_aws_credentials():
    """Rotate AWS credentials automatically."""
    # Generate new access key
    new_access_key = create_new_access_key()
    
    # Update configuration
    update_config_with_new_credentials(new_access_key)
    
    # Delete old access key after grace period
    schedule_old_key_deletion(old_access_key)
```

### 2. Azure Security

#### Service Principal Security

```bash
# Create service principal with minimal permissions
az ad sp create-for-rbac \
  --name finops-optimizer \
  --role "Cost Management Reader" \
  --scopes /subscriptions/your-subscription-id
```

#### Managed Identity

```python
# Use managed identity for authentication
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()
client = CostManagementClient(credential, subscription_id)
```

### 3. GCP Security

#### Service Account Security

```bash
# Create service account with minimal permissions
gcloud iam service-accounts create finops-optimizer \
  --display-name="FinOps Optimizer"

# Grant minimal permissions
gcloud projects add-iam-policy-binding your-project \
  --member="serviceAccount:finops-optimizer@your-project.iam.gserviceaccount.com" \
  --role="roles/billing.viewer"
```

#### Workload Identity

```python
# Use workload identity for authentication
from google.auth import default

credentials, project = default()
client = compute_v1.InstancesClient(credentials=credentials)
```

### 4. Oracle Cloud Security

#### API Key Security

```bash
# Generate secure API key pair
openssl genrsa -out private_key.pem 2048
openssl rsa -pubout -in private_key.pem -out public_key.pem

# Set proper permissions
chmod 600 private_key.pem
chmod 644 public_key.pem
```

## 🔍 Security Monitoring

### 1. Security Alerts

```python
def monitor_security_events():
    """Monitor security events and trigger alerts."""
    events = get_recent_security_events()
    
    for event in events:
        if event['severity'] == 'high':
            send_security_alert(event)
        
        if event['type'] == 'failed_login':
            check_for_brute_force(event)
```

### 2. Intrusion Detection

```python
def detect_suspicious_activity():
    """Detect suspicious activity patterns."""
    # Check for multiple failed logins
    failed_logins = get_failed_logins(time_window=300)  # 5 minutes
    
    if len(failed_logins) > 5:
        block_ip_address(failed_logins[0]['ip_address'])
        send_security_alert({
            'type': 'brute_force_attempt',
            'ip_address': failed_logins[0]['ip_address'],
            'attempts': len(failed_logins)
        })
```

### 3. Vulnerability Scanning

```python
def scan_for_vulnerabilities():
    """Scan for security vulnerabilities."""
    # Check for outdated dependencies
    outdated_packages = check_package_versions()
    
    # Check for known vulnerabilities
    vulnerabilities = check_security_vulnerabilities()
    
    # Generate security report
    generate_security_report(outdated_packages, vulnerabilities)
```

## 🔧 Security Configuration

### 1. Security Settings

```yaml
security:
  # Authentication
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
  
  # Encryption
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
  
  # Audit logging
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

### 2. Network Security

```yaml
security:
  network:
    # Firewall rules
    allowed_ips:
      - "192.168.1.0/24"
      - "10.0.0.0/8"
    
    # SSL/TLS
    ssl_enabled: true
    ssl_cert: "/path/to/cert.pem"
    ssl_key: "/path/to/key.pem"
    
    # Headers
    security_headers:
      X-Frame-Options: "DENY"
      X-Content-Type-Options: "nosniff"
      X-XSS-Protection: "1; mode=block"
      Strict-Transport-Security: "max-age=31536000; includeSubDomains"
```

### 3. Data Protection

```yaml
security:
  data_protection:
    # Data retention
    retention_policy:
      cost_data: 365  # days
      audit_logs: 2555  # 7 years
      user_data: 90  # days
    
    # Data classification
    data_classification:
      public: []
      internal: ["cost_analysis", "recommendations"]
      confidential: ["credentials", "audit_logs"]
      restricted: ["user_passwords", "api_keys"]
    
    # Data encryption
    encryption_at_rest: true
    encryption_in_transit: true
```

## 🚨 Incident Response

### 1. Security Incident Response Plan

```python
def handle_security_incident(incident_type, details):
    """Handle security incidents."""
    # Log incident
    log_security_incident(incident_type, details)
    
    # Determine severity
    severity = assess_incident_severity(incident_type, details)
    
    # Take immediate action
    if severity == 'critical':
        block_suspicious_activity(details)
        notify_security_team(incident_type, details)
        initiate_incident_response(incident_type)
    
    # Document incident
    document_incident(incident_type, details, severity)
```

### 2. Incident Categories

```python
INCIDENT_CATEGORIES = {
    'authentication': {
        'brute_force': 'high',
        'credential_stuffing': 'high',
        'session_hijacking': 'critical'
    },
    'data_access': {
        'unauthorized_access': 'high',
        'data_exfiltration': 'critical',
        'privilege_escalation': 'critical'
    },
    'system': {
        'malware_detection': 'critical',
        'system_compromise': 'critical',
        'denial_of_service': 'medium'
    }
}
```

### 3. Response Procedures

```python
def incident_response_procedures():
    """Define incident response procedures."""
    procedures = {
        'critical': [
            'Immediately isolate affected systems',
            'Notify security team and management',
            'Preserve evidence for investigation',
            'Implement emergency security measures',
            'Communicate with stakeholders'
        ],
        'high': [
            'Investigate incident thoroughly',
            'Implement security controls',
            'Update security policies',
            'Monitor for similar incidents'
        ],
        'medium': [
            'Document incident details',
            'Implement preventive measures',
            'Review security controls'
        ]
    }
    return procedures
```

## 📋 Security Checklist

### 1. Initial Setup

- [ ] Generate secure secret key
- [ ] Configure SSL/TLS certificates
- [ ] Set up firewall rules
- [ ] Configure authentication
- [ ] Enable audit logging
- [ ] Set up monitoring

### 2. Cloud Provider Security

- [ ] Use least privilege access
- [ ] Enable MFA for accounts
- [ ] Rotate credentials regularly
- [ ] Monitor access logs
- [ ] Use managed identities where possible

### 3. Application Security

- [ ] Validate all inputs
- [ ] Use parameterized queries
- [ ] Implement rate limiting
- [ ] Enable HTTPS only
- [ ] Set security headers

### 4. Data Security

- [ ] Encrypt sensitive data
- [ ] Implement data retention policies
- [ ] Regular security audits
- [ ] Monitor data access
- [ ] Backup security configurations

### 5. Monitoring and Response

- [ ] Set up security monitoring
- [ ] Configure alerts
- [ ] Test incident response
- [ ] Regular security reviews
- [ ] Update security policies

## 🔍 Security Testing

### 1. Vulnerability Assessment

```bash
# Run security scan
bandit -r finops/

# Check for known vulnerabilities
safety check

# Run dependency scan
pip-audit
```

### 2. Penetration Testing

```python
def security_testing():
    """Perform security testing."""
    tests = [
        'test_authentication',
        'test_authorization',
        'test_input_validation',
        'test_encryption',
        'test_session_management',
        'test_api_security'
    ]
    
    for test in tests:
        run_security_test(test)
```

### 3. Security Compliance

```python
def compliance_check():
    """Check security compliance."""
    compliance_checks = [
        'password_policy_compliance',
        'encryption_standards',
        'access_control_compliance',
        'audit_logging_compliance',
        'data_protection_compliance'
    ]
    
    results = {}
    for check in compliance_checks:
        results[check] = perform_compliance_check(check)
    
    return results
```

## 📚 Security Resources

### 1. Best Practices

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
- [Cloud Security Alliance](https://cloudsecurityalliance.org/)

### 2. Tools

- **Static Analysis**: Bandit, Safety
- **Dynamic Analysis**: OWASP ZAP
- **Dependency Scanning**: pip-audit, Safety
- **Vulnerability Scanning**: Trivy, Clair

### 3. Standards

- **ISO 27001**: Information Security Management
- **SOC 2**: Security, Availability, Processing Integrity
- **GDPR**: Data Protection and Privacy
- **HIPAA**: Healthcare Data Protection

---

**Need help with security?** Check our [Troubleshooting Guide](troubleshooting.md) or [open an issue](https://github.com/manikantesh/finopsoptimizer/issues). 
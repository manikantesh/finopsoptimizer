# Web Dashboard Guide

This guide covers the FinOps Optimizer web dashboard, including setup, usage, and customization.

## 📋 Overview

The FinOps Optimizer web dashboard provides a modern, interactive interface for cost monitoring, optimization, and reporting. Built with Flask and Bootstrap, it offers real-time insights into your multi-cloud infrastructure.

## 🚀 Quick Start

### Installation

```bash
# Install web dependencies
pip install flask flask-login werkzeug

# Start dashboard
python -m web.app

# Or use CLI
python cli.py dashboard
```

### Access Dashboard

- **URL**: http://localhost:5000
- **Default Username**: `admin`
- **Default Password**: `admin123`

## 🏗️ Architecture

### Components

```
web/
├── app.py                 # Flask application
├── templates/            # HTML templates
│   ├── dashboard.html    # Main dashboard
│   ├── login.html        # Login page
│   └── components/       # Reusable components
├── static/              # Static assets
│   ├── css/            # Stylesheets
│   ├── js/             # JavaScript
│   └── images/         # Images
└── api/                # API endpoints
```

### Technology Stack

- **Backend**: Flask (Python)
- **Frontend**: Bootstrap 5, Chart.js
- **Authentication**: Flask-Login
- **Charts**: Chart.js
- **Styling**: Bootstrap CSS

## 📊 Dashboard Features

### 1. Real-time Cost Monitoring

The dashboard provides real-time cost monitoring across all cloud providers:

- **Cost Overview**: Total costs and trends
- **Provider Breakdown**: Costs by cloud provider
- **Service Analysis**: Costs by service type
- **Daily Trends**: Cost trends over time

### 2. Interactive Charts

#### Cost Trend Chart

```javascript
// Line chart showing daily costs
const costTrendChart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: dates,
        datasets: [{
            label: 'Daily Cost',
            data: costs,
            borderColor: 'rgb(75, 192, 192)',
            backgroundColor: 'rgba(75, 192, 192, 0.2)'
        }]
    }
});
```

#### Service Breakdown Chart

```javascript
// Doughnut chart showing service costs
const serviceChart = new Chart(ctx, {
    type: 'doughnut',
    data: {
        labels: services,
        datasets: [{
            data: serviceCosts,
            backgroundColor: colors
        }]
    }
});
```

### 3. Provider Status Monitoring

Real-time status of cloud providers:

- **Connection Status**: Online/Offline indicators
- **Credential Validation**: Authentication status
- **API Health**: Service availability
- **Performance Metrics**: Response times

### 4. Optimization Recommendations

Interactive recommendations panel:

- **Rightsizing**: Instance optimization suggestions
- **Autoscaling**: Scaling policy recommendations
- **Cost Allocation**: Tagging and allocation suggestions
- **Priority Levels**: High/Medium/Low priority

### 5. Cost Forecasting

ML-powered cost forecasting:

- **Forecast Periods**: 30, 60, 90 days
- **Confidence Intervals**: Statistical confidence
- **Optimization Impact**: Savings projections
- **Trend Analysis**: Growth patterns

## 🔧 Setup and Configuration

### 1. Basic Setup

```bash
# Install dependencies
pip install flask flask-login werkzeug

# Configure environment
export FLASK_APP=web.app
export FLASK_ENV=development

# Start dashboard
python -m web.app
```

### 2. Production Setup

```bash
# Install production dependencies
pip install gunicorn

# Start with gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 web.app:app

# With SSL
gunicorn -w 4 -b 0.0.0.0:8000 --certfile cert.pem --keyfile key.pem web.app:app
```

### 3. Docker Setup

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

```bash
# Build and run
docker build -t finops-dashboard .
docker run -p 5000:5000 finops-dashboard
```

### 4. Configuration

#### Dashboard Configuration

```yaml
# finops_config.yml
dashboard:
  enabled: true
  host: "0.0.0.0"
  port: 5000
  debug: false
  
  # Authentication
  auth:
    enabled: true
    session_timeout: 3600
    max_login_attempts: 5
  
  # Security
  security:
    secret_key: "your-secret-key"
    ssl_enabled: false
    ssl_cert: "/path/to/cert.pem"
    ssl_key: "/path/to/key.pem"
  
  # Features
  features:
    real_time_updates: true
    interactive_charts: true
    export_reports: true
    notifications: true
```

#### User Management

```python
# Custom user management
from web.app import User

# Add users
users = {
    'admin': User(1, 'admin', generate_password_hash('admin123')),
    'user1': User(2, 'user1', generate_password_hash('password123')),
    'manager': User(3, 'manager', generate_password_hash('manager123'))
}
```

## 📱 User Interface

### 1. Login Page

```html
<!-- login.html -->
<div class="login-card">
    <div class="logo">
        <h2>FinOps Optimizer</h2>
        <p class="text-muted">Cost Optimization Dashboard</p>
    </div>
    
    <form method="POST">
        <div class="mb-3">
            <label for="username" class="form-label">Username</label>
            <input type="text" class="form-control" id="username" name="username" required>
        </div>
        <div class="mb-3">
            <label for="password" class="form-label">Password</label>
            <input type="password" class="form-control" id="password" name="password" required>
        </div>
        <button type="submit" class="btn btn-primary w-100">Login</button>
    </form>
</div>
```

### 2. Main Dashboard

```html
<!-- dashboard.html -->
<div class="container-fluid">
    <div class="row">
        <!-- Sidebar -->
        <nav class="col-md-3 col-lg-2 d-md-block sidebar">
            <ul class="nav flex-column">
                <li class="nav-item">
                    <a class="nav-link" href="#dashboard">Dashboard</a>
                </li>
                <li class="nav-item">
                    <a class="nav-link" href="#costs">Cost Analysis</a>
                </li>
                <li class="nav-item">
                    <a class="nav-link" href="#recommendations">Recommendations</a>
                </li>
                <li class="nav-item">
                    <a class="nav-link" href="#forecast">Cost Forecast</a>
                </li>
                <li class="nav-item">
                    <a class="nav-link" href="#reports">Reports</a>
                </li>
            </ul>
        </nav>
        
        <!-- Main content -->
        <main class="col-md-9 ms-sm-auto col-lg-10 px-md-4">
            <!-- Dashboard content -->
        </main>
    </div>
</div>
```

### 3. Metrics Cards

```html
<!-- Metrics cards -->
<div class="row mb-4">
    <div class="col-xl-3 col-md-6 mb-4">
        <div class="card metric-card">
            <div class="card-body">
                <div class="row no-gutters align-items-center">
                    <div class="col mr-2">
                        <div class="text-xs font-weight-bold text-white-50 text-uppercase mb-1">
                            Total Cost
                        </div>
                        <div class="h5 mb-0 font-weight-bold text-white" id="totalCost">$0</div>
                    </div>
                    <div class="col-auto">
                        <i class="fas fa-dollar-sign fa-2x text-white-50"></i>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
```

## 🔌 API Endpoints

### 1. Cost Analysis

#### GET `/api/costs`

Get cost analysis data.

**Query Parameters:**
- `days` (int): Number of days to analyze. Default: 30

**Response:**
```json
{
  "summary": {
    "total_cost": 2450.75,
    "providers_analyzed": ["aws", "azure", "gcp"],
    "analysis_period": {
      "start_date": "2024-01-01T00:00:00",
      "end_date": "2024-01-31T23:59:59"
    }
  },
  "aws": {
    "total_cost": 1250.50,
    "service_breakdown": {
      "EC2": 750.25,
      "S3": 350.00,
      "RDS": 150.25
    },
    "daily_costs": [...]
  },
  "azure": {
    "total_cost": 800.25,
    "service_breakdown": {...},
    "daily_costs": [...]
  },
  "gcp": {
    "total_cost": 400.00,
    "service_breakdown": {...},
    "daily_costs": [...]
  }
}
```

### 2. Recommendations

#### GET `/api/recommendations`

Get optimization recommendations.

**Response:**
```json
[
  {
    "type": "rightsizing",
    "resource_id": "i-123456",
    "description": "Downsize instance from t3.xlarge to t3.large",
    "potential_savings": 200.00,
    "priority": "high",
    "provider": "aws",
    "confidence": 0.9,
    "implementation_effort": "low"
  }
]
```

### 3. Cost Forecast

#### GET `/api/forecast`

Get cost forecast.

**Query Parameters:**
- `days` (int): Days to forecast. Default: 30

**Response:**
```json
{
  "total_forecast": 2750.00,
  "confidence_interval": [2500.00, 3000.00],
  "forecast_period": 30,
  "provider_forecasts": {
    "aws": {
      "total_forecast": 1375.00,
      "trend_analysis": {
        "trend_direction": "increasing",
        "volatility": 0.1
      }
    }
  },
  "recommendations_impact": {
    "base_forecast": 2750.00,
    "optimized_forecast": 2300.00,
    "total_savings": 450.00,
    "savings_percentage": 16.4
  }
}
```

### 4. Optimization

#### POST `/api/optimize`

Run complete optimization.

**Response:**
```json
{
  "summary": {
    "total_recommendations": 15,
    "total_potential_savings": 450.75,
    "providers_analyzed": ["aws", "azure", "gcp"]
  },
  "recommendations": [...],
  "report_path": "/path/to/report.html"
}
```

### 5. Reports

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

### 6. Provider Status

#### GET `/api/status`

Get provider status.

**Response:**
```json
{
  "aws": true,
  "azure": true,
  "gcp": false,
  "oracle": true
}
```

### 7. Performance Metrics

#### GET `/api/performance`

Get performance metrics.

**Response:**
```json
{
  "cache_hit_rate": 0.85,
  "total_requests": 1250,
  "average_response_time": 0.25,
  "error_rate": 0.004,
  "memory_usage": 0.45,
  "cpu_usage": 0.15
}
```

## 🎨 Customization

### 1. Custom Themes

```css
/* custom-theme.css */
:root {
  --primary-color: #667eea;
  --secondary-color: #764ba2;
  --success-color: #28a745;
  --warning-color: #ffc107;
  --danger-color: #dc3545;
  --dark-color: #343a40;
  --light-color: #f8f9fa;
}

.sidebar {
  background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
}

.metric-card {
  background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
  color: white;
}
```

### 2. Custom Components

```html
<!-- custom-component.html -->
<div class="custom-widget">
    <div class="widget-header">
        <h5>Custom Widget</h5>
    </div>
    <div class="widget-content">
        <!-- Custom content -->
    </div>
</div>
```

### 3. Custom JavaScript

```javascript
// custom-dashboard.js
class CustomDashboard {
    constructor() {
        this.initializeCharts();
        this.setupEventListeners();
        this.startRealTimeUpdates();
    }
    
    initializeCharts() {
        // Custom chart initialization
    }
    
    setupEventListeners() {
        // Custom event handling
    }
    
    startRealTimeUpdates() {
        // Real-time data updates
        setInterval(() => {
            this.updateMetrics();
        }, 30000); // Update every 30 seconds
    }
    
    updateMetrics() {
        fetch('/api/costs')
            .then(response => response.json())
            .then(data => {
                this.updateCharts(data);
                this.updateMetrics(data);
            });
    }
}

// Initialize custom dashboard
document.addEventListener('DOMContentLoaded', () => {
    new CustomDashboard();
});
```

## 🔒 Security Features

### 1. Authentication

```python
# Authentication configuration
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return users.get(int(user_id))
```

### 2. Session Management

```python
# Session configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=1)
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
```

### 3. Rate Limiting

```python
# Rate limiting
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

## 📊 Monitoring and Analytics

### 1. Performance Monitoring

```python
# Performance monitoring
import time
from functools import wraps

def monitor_performance(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = time.time()
        result = f(*args, **kwargs)
        duration = time.time() - start_time
        
        # Log performance metrics
        app.logger.info(f"API call {f.__name__} took {duration:.2f}s")
        
        return result
    return decorated_function

@app.route('/api/costs')
@monitor_performance
@login_required
def get_costs():
    # API endpoint with performance monitoring
    pass
```

### 2. Error Tracking

```python
# Error tracking
@app.errorhandler(Exception)
def handle_error(error):
    app.logger.error(f"Unhandled error: {error}")
    return jsonify({
        'error': 'Internal server error',
        'message': str(error)
    }), 500
```

### 3. Usage Analytics

```python
# Usage analytics
@app.before_request
def track_usage():
    if request.endpoint:
        # Track API usage
        track_api_usage(request.endpoint, request.method)
```

## 🚀 Deployment

### 1. Production Deployment

```bash
# Install production dependencies
pip install gunicorn

# Set environment variables
export FLASK_ENV=production
export SECRET_KEY=your-secret-key

# Start with gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 web.app:app
```

### 2. Docker Deployment

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "web.app:app"]
```

### 3. Kubernetes Deployment

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: finops-dashboard
spec:
  replicas: 3
  selector:
    matchLabels:
      app: finops-dashboard
  template:
    metadata:
      labels:
        app: finops-dashboard
    spec:
      containers:
      - name: finops-dashboard
        image: finops-dashboard:latest
        ports:
        - containerPort: 5000
        env:
        - name: FLASK_ENV
          value: "production"
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: finops-secrets
              key: secret-key
```

## 🔧 Troubleshooting

### 1. Common Issues

#### Dashboard Not Loading

```bash
# Check if Flask app is running
curl http://localhost:5000

# Check logs
tail -f logs/finops.log

# Check configuration
python cli.py validate-config
```

#### Authentication Issues

```bash
# Reset admin password
python -c "
from werkzeug.security import generate_password_hash
print('New password hash:', generate_password_hash('newpassword'))
"

# Check user database
python -c "
from web.app import users
for username, user in users.items():
    print(f'{username}: {user.id}')
"
```

#### Performance Issues

```bash
# Check resource usage
python cli.py health

# Monitor performance
python cli.py metrics

# Optimize cache
python cli.py cleanup --cache
```

### 2. Debug Mode

```bash
# Enable debug mode
export FLASK_ENV=development
export FLASK_DEBUG=1

# Start with debug
python -m web.app
```

### 3. Log Analysis

```bash
# View application logs
tail -f logs/finops.log

# View error logs
tail -f logs/error.log

# View access logs
tail -f logs/access.log
```

## 📈 Performance Optimization

### 1. Caching

```python
# Redis caching
import redis
from functools import wraps

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def cache_result(ttl=300):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            cache_key = f"{f.__name__}:{hash(str(args) + str(kwargs))}"
            result = redis_client.get(cache_key)
            
            if result is None:
                result = f(*args, **kwargs)
                redis_client.setex(cache_key, ttl, result)
            
            return result
        return decorated_function
    return decorator

@app.route('/api/costs')
@cache_result(ttl=300)  # Cache for 5 minutes
@login_required
def get_costs():
    # API endpoint with caching
    pass
```

### 2. Database Optimization

```python
# Database connection pooling
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    'postgresql://user:pass@localhost/finops',
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True
)
```

### 3. CDN Integration

```html
<!-- CDN for static assets -->
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
```

## 🎯 Best Practices

### 1. Security

- Use HTTPS in production
- Implement proper authentication
- Set up rate limiting
- Regular security updates
- Input validation

### 2. Performance

- Enable caching
- Optimize database queries
- Use CDN for static assets
- Monitor resource usage
- Implement lazy loading

### 3. Monitoring

- Set up health checks
- Monitor error rates
- Track performance metrics
- Set up alerts
- Regular backups

### 4. Maintenance

- Regular updates
- Security patches
- Performance tuning
- Log rotation
- Database maintenance

---

**Need help with the dashboard?** Check our [Tutorial Guide](tutorial.md) or [open an issue](https://github.com/manikantesh/finopsoptimizerdocs/issues). 
# FinOps Optimizer

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Documentation](https://img.shields.io/badge/docs-GitHub%20Pages-blue)](https://manikantesh.github.io/finopsoptimizer/)
[![Deploy Documentation](https://github.com/manikantesh/finopsoptimizer/actions/workflows/docs.yml/badge.svg)](https://github.com/manikantesh/finopsoptimizer/actions/workflows/docs.yml)

**AI-Powered Cost Optimization Platform with Real-Time Dashboards and Intelligent Agents for Multi-Cloud Environments**

Transform your cloud costs with intelligent automation, real-time insights, and enterprise-grade security across AWS, Azure, GCP, and Oracle Cloud.

---

## 🚀 Quick Start

### Automated Setup (Recommended)
```bash
# Clone the repository
git clone https://github.com/manikantesh/finopsoptimizer.git
cd finopsoptimizer

# Run automated setup
python quick_start.py

# Validate installation
python validate_setup.py
```

### Basic Usage
```python
from finops import FinOpsOptimizer

# Initialize optimizer
optimizer = FinOpsOptimizer()

# Run complete optimization
results = optimizer.optimize_all()

print(f"Found {len(results['recommendations'])} optimization opportunities")
print(f"Potential savings: ${results['summary']['total_potential_savings']:.2f}")
```

### CLI Usage
```bash
# Initialize configuration
python cli.py init

# Check provider status
python cli.py status

# Analyze costs and generate recommendations
python cli.py analyze

# Run optimization
python cli.py optimize

# Generate comprehensive report
python cli.py report
```

## 📚 Documentation

### 🌐 Live Documentation
- **[📖 Latest Documentation](https://manikantesh.github.io/finopsoptimizer/)** - Always up-to-date
- **[📋 Version 2.1.0](https://manikantesh.github.io/finopsoptimizer/2.1.0/)** - AI Agents & Real-time Dashboards
- **[📋 Version 2.0.0](https://manikantesh.github.io/finopsoptimizer/2.0.0/)** - Multi-Cloud Support

### 📖 Key Documentation Pages
- **[🚀 Installation Guide](https://manikantesh.github.io/finopsoptimizer/installation/)** - Complete setup instructions
- **[🏠 Local Setup Guide](https://manikantesh.github.io/finopsoptimizer/local-setup/)** - Local development setup
- **[⚙️ Configuration Guide](https://manikantesh.github.io/finopsoptimizer/configuration/)** - Configuration options
- **[🤖 AI Agents](https://manikantesh.github.io/finopsoptimizer/ai-agents/)** - AI-powered optimization
- **[📊 Real-Time Dashboards](https://manikantesh.github.io/finopsoptimizer/real-time-dashboards/)** - Interactive dashboards
- **[🔧 CLI Reference](https://manikantesh.github.io/finopsoptimizer/cli-reference/)** - Command-line interface
- **[🔒 Security Guide](https://manikantesh.github.io/finopsoptimizer/security/)** - Security best practices
- **[🛠️ Troubleshooting](https://manikantesh.github.io/finopsoptimizer/troubleshooting/)** - Common issues and solutions

### 📋 Documentation Features
- **Version Selector**: Switch between documentation versions using the dropdown
- **Automatic Updates**: Documentation updates automatically with each release
- **Mobile Responsive**: Perfect viewing on all devices
- **Search Functionality**: Fast search across all documentation

## 🌟 Key Features

### 🤖 AI-Powered Optimization
- **Autonomous Optimization Agent**: Continuously monitors and automatically applies cost optimizations
- **Cost Advisor Agent**: AI-powered cost consultant with natural language processing
- **Machine Learning Models**: Advanced ML for cost forecasting and resource optimization
- **Intelligent Automation**: Smart rightsizing, predictive scaling, and anomaly detection

### 📊 Real-Time Analytics
- **Live Dashboards**: Interactive dashboards with real-time cost monitoring
- **Executive Dashboard**: High-level cost overview for leadership
- **Engineering Dashboard**: Technical insights for development teams
- **Operations Dashboard**: Real-time monitoring for DevOps/SRE teams
- **Advanced Visualizations**: D3.js-powered charts and graphs

### 🏗️ Enterprise Architecture
- **Kubernetes-Native**: Full containerization with Helm charts and auto-scaling
- **Microservices**: Event-driven architecture with message queues
- **High Availability**: 99.9% uptime with distributed caching and load balancing
- **Advanced Data Stack**: Apache Kafka + Flink + Redis + Elasticsearch

### 💾 Advanced Data Management
- **Real-Time Processing**: Apache Kafka + Flink for streaming analytics
- **Search & Analytics**: Elasticsearch for advanced cost data search
- **Distributed Caching**: Redis Cluster for high-performance data access
- **Time-Series Database**: InfluxDB for metrics and cost data storage

### 🔒 Enterprise Security
- **Identity Management**: Keycloak integration for SSO and RBAC
- **Policy Engine**: Open Policy Agent (OPA) for fine-grained access control
- **Secrets Management**: HashiCorp Vault for secure credential storage
- **Audit & Compliance**: Complete audit trails and compliance reporting

### 🌐 Multi-Cloud Excellence
- **Provider Support**: AWS, Azure, GCP, Oracle Cloud with unified APIs
- **Cost Optimization**: Rightsizing, reserved instances, spot instances, unattached resources
- **Real-Time Pricing**: Live pricing data integration for accurate cost calculations
- **Cross-Cloud Analytics**: Compare costs and performance across providers

## 📊 Supported Cloud Providers

| Provider | Cost Analysis | Rightsizing | Reserved Instances | Unattached Resources | Real-Time Pricing |
|----------|---------------|-------------|-------------------|---------------------|-------------------|
| AWS      | ✅            | ✅          | ✅                | ✅                  | ✅                |
| Azure    | ✅            | ✅          | ✅                | ✅                  | ✅                |
| GCP      | ✅            | ✅          | ✅                | ✅                  | ✅                |
| Oracle   | ✅            | ✅          | ✅                | ✅                  | ✅                |

## 🛠️ Installation Options

### Option 1: Automated Setup (Recommended)
```bash
git clone https://github.com/manikantesh/finopsoptimizer.git
cd finopsoptimizer
python quick_start.py
```

### Option 2: Manual Setup
```bash
# Clone repository
git clone https://github.com/manikantesh/finopsoptimizer.git
cd finopsoptimizer

# Create virtual environment
python -m venv finops-env
source finops-env/bin/activate  # On Windows: finops-env\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create configuration
python quick_start.py --config-only

# Validate setup
python validate_setup.py
```

### Option 3: Development Setup
```bash
# Clone and setup for development
git clone https://github.com/manikantesh/finopsoptimizer.git
cd finopsoptimizer

# Install with development dependencies
pip install -e .
pip install pytest pytest-cov black flake8 mypy

# Run tests
pytest tests/
```

## 🧪 Validation & Testing

After installation, validate your setup:

```bash
# Comprehensive validation
python validate_setup.py --full

# Quick validation
python validate_setup.py

# Test basic functionality
python test_finops.py

# Test CLI functionality
python cli.py --help
python cli.py status
```

## ⚙️ Configuration

### Quick Configuration
```bash
# Create default configuration
python quick_start.py --config-only

# Or use CLI
python cli.py init
```

### Cloud Provider Setup
```bash
# AWS
aws configure

# Azure
az login

# Google Cloud
gcloud auth application-default login

# Oracle Cloud
oci setup config
```

For detailed configuration instructions, see the [Configuration Guide](https://manikantesh.github.io/finopsoptimizer/configuration/).

## 🎯 Use Cases

### Cost Optimization
- **VM Rightsizing**: AI-powered instance size recommendations
- **Reserved Instances**: Automated RI analysis and purchase recommendations
- **Unattached Resources**: Identify and clean up unused storage volumes
- **Spot Instances**: Optimize workloads for spot instance usage

### Real-Time Monitoring
- **Live Dashboards**: Monitor costs in real-time across all providers
- **Anomaly Detection**: AI-powered detection of unusual spending patterns
- **Budget Tracking**: Track spending against budgets with alerts
- **Trend Analysis**: Historical cost analysis and forecasting

### Automation & Intelligence
- **Autonomous Agents**: AI agents that optimize costs automatically
- **Predictive Scaling**: Forecast demand and pre-scale resources
- **Intelligent Alerts**: Smart notifications based on spending patterns
- **Natural Language Queries**: Ask questions about costs in plain English

## 🚀 Technology Stack

### Core Platform
- **Backend**: Python with FastAPI and WebSocket support
- **Frontend**: React + D3.js for interactive visualizations
- **Container Platform**: Kubernetes with Helm charts
- **Service Mesh**: Istio for traffic management and security

### Data & Analytics
- **Streaming**: Apache Kafka + Apache Flink
- **Search**: Elasticsearch + Kibana
- **Time-Series**: InfluxDB for metrics storage
- **Cache**: Redis Cluster for high-performance access
- **Object Storage**: MinIO (S3-compatible)

### AI & Machine Learning
- **Agent Framework**: LangChain + Ollama for local AI deployment
- **ML Pipeline**: Apache Airflow for orchestration
- **Model Management**: MLflow for experiment tracking
- **Vector Database**: Chroma for cost optimization knowledge

### Security & Operations
- **Identity**: Keycloak for SSO and RBAC
- **Policy Engine**: Open Policy Agent (OPA)
- **Secrets**: HashiCorp Vault
- **Monitoring**: Prometheus + Grafana + Jaeger

## 📋 Documentation Versioning

### How Versioning Works
- **Latest**: Always reflects the main branch (development)
- **Versioned Releases**: Each GitHub release creates a documentation version
- **Version Selector**: Switch between versions using the dropdown in documentation
- **Automatic Deployment**: Documentation updates automatically with each release

### Creating New Versions
```bash
# Create a new release (triggers automatic documentation deployment)
git tag -a v2.2.0 -m "Release v2.2.0: New Features"
git push origin v2.2.0

# Or use the release helper script
./scripts/create-release.sh -v 2.2.0 -t "Enhanced AI Features"
```

### Available Versions
- **[Latest](https://manikantesh.github.io/finopsoptimizer/)** - Development version
- **[v2.1.0](https://manikantesh.github.io/finopsoptimizer/2.1.0/)** - AI Agents & Real-time Dashboards
- **[v2.0.0](https://manikantesh.github.io/finopsoptimizer/2.0.0/)** - Multi-Cloud Support

## 🤝 Contributing

We welcome contributions! Here's how to get started:

### Development Setup
```bash
# Fork and clone the repository
git clone https://github.com/your-username/finopsoptimizer.git
cd finopsoptimizer

# Set up development environment
python -m venv dev-env
source dev-env/bin/activate

# Install development dependencies
pip install -e .
pip install pytest pytest-cov black flake8 mypy

# Run tests
pytest tests/
```

### Code Standards
- **Black** for code formatting
- **isort** for import sorting
- **flake8** for linting
- **mypy** for type checking
- **pytest** for testing

### Contributing Process
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

For detailed contributing guidelines, see the [Contributing Guide](https://manikantesh.github.io/finopsoptimizer/contributing/).

## 🔒 Security

### Security Features
- **Data Encryption**: AES-256 encryption for sensitive data
- **Authentication**: Secure authentication with multiple providers
- **Rate Limiting**: API protection against abuse
- **Audit Logging**: Complete audit trails for all actions
- **Input Validation**: Protection against injection attacks

### Security Best Practices
- Use least-privilege IAM roles
- Regularly rotate access keys
- Enable audit logging
- Use HTTPS/TLS encryption
- Implement proper access controls

For detailed security information, see the [Security Guide](https://manikantesh.github.io/finopsoptimizer/security/).

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

### Getting Help
- **📖 Documentation**: [GitHub Pages](https://manikantesh.github.io/finopsoptimizer/)
- **🐛 Issues**: [GitHub Issues](https://github.com/manikantesh/finopsoptimizer/issues)
- **💬 Discussions**: [GitHub Discussions](https://github.com/manikantesh/finopsoptimizer/discussions)
- **📧 Email**: support@finopsoptimizer.com

### Troubleshooting
1. **Check Documentation**: [Troubleshooting Guide](https://manikantesh.github.io/finopsoptimizer/troubleshooting/)
2. **Run Validation**: `python validate_setup.py --full`
3. **Check Logs**: Review application logs for errors
4. **Search Issues**: Check existing GitHub issues
5. **Create Issue**: If problem persists, create a new issue

## 🚀 Deployment Options

### Local Development
```bash
python quick_start.py
python cli.py status
```

### Docker Deployment
```bash
docker build -t finopsoptimizer .
docker run -p 8080:8080 finopsoptimizer
```

### Kubernetes Deployment
```bash
helm repo add finops https://charts.finopsoptimizer.com
helm install finops finops/finopsoptimizer
```

### Cloud Deployment
- **AWS**: EKS with Application Load Balancer
- **Azure**: AKS with Azure Application Gateway
- **GCP**: GKE with Google Cloud Load Balancer
- **Oracle**: OKE with Oracle Cloud Infrastructure

For detailed deployment instructions, see the [Deployment Guide](https://manikantesh.github.io/finopsoptimizer/deployment/).

## 📈 Roadmap

### Current Version (v2.1.0)
- ✅ AI Agents for autonomous optimization
- ✅ Real-time dashboards with interactive visualizations
- ✅ Complete setup automation
- ✅ Professional documentation system

### Upcoming Features
- 🔄 Version comparison in documentation
- 🔄 Enhanced AI agent capabilities
- 🔄 Mobile application
- 🔄 Advanced analytics and reporting
- 🔄 Additional cloud provider integrations

### Future Enhancements
- 📋 API Gateway with authentication
- 📋 Advanced ML models for cost prediction
- 📋 Integration with CI/CD pipelines
- 📋 Custom optimization rules engine

For the complete roadmap, see [Future Enhancements](https://manikantesh.github.io/finopsoptimizer/future-roadmap/).

---

**FinOps Optimizer** - Transform your cloud costs with AI-powered optimization, real-time insights, and enterprise-grade automation.

**🎯 Ready to optimize your cloud costs?** Start with `python quick_start.py`!
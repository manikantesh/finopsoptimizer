# FinOps Optimizer

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Documentation](https://img.shields.io/badge/docs-GitHub%20Pages-blue)](https://manikantesh.github.io/finopsoptimizer/)
[![Deploy Documentation](https://github.com/manikantesh/finopsoptimizer/actions/workflows/docs.yml/badge.svg)](https://github.com/manikantesh/finopsoptimizer/actions/workflows/docs.yml)

**Multi-Cloud Cost Optimization Platform for AWS, Azure, GCP, and Oracle Cloud**

Optimize your cloud costs with rightsizing recommendations, reserved instance analysis, and automated resource cleanup across multiple cloud providers.

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
- **[📋 Version 2.1.0](https://manikantesh.github.io/finopsoptimizer/2.1.0/)** - Enhanced Multi-Cloud Support
- **[📋 Version 2.0.0](https://manikantesh.github.io/finopsoptimizer/2.0.0/)** - Multi-Cloud Foundation

### 📖 Key Documentation Pages
- **[🚀 Installation Guide](https://manikantesh.github.io/finopsoptimizer/installation/)** - Complete setup instructions
- **[🏠 Local Setup Guide](https://manikantesh.github.io/finopsoptimizer/local-setup/)** - Local development setup
- **[⚙️ Configuration Guide](https://manikantesh.github.io/finopsoptimizer/configuration/)** - Configuration options
- **[🔧 CLI Reference](https://manikantesh.github.io/finopsoptimizer/cli-reference/)** - Command-line interface
- **[🌐 Web Dashboard](https://manikantesh.github.io/finopsoptimizer/web-dashboard/)** - Web interface guide
- **[� Sec urity Guide](https://manikantesh.github.io/finopsoptimizer/security/)** - Security best practices
- **[�️ eTroubleshooting](https://manikantesh.github.io/finopsoptimizer/troubleshooting/)** - Common issues and solutions

### 📋 Documentation Features
- **Version Selector**: Switch between documentation versions using the dropdown
- **Automatic Updates**: Documentation updates automatically with each release
- **Mobile Responsive**: Perfect viewing on all devices
- **Search Functionality**: Fast search across all documentation

## 🌟 Key Features

### 🌐 Multi-Cloud Cost Optimization
- **Provider Support**: AWS, Azure, GCP, Oracle Cloud with unified APIs
- **VM Rightsizing**: Instance size recommendations based on utilization analysis
- **Reserved Instances**: Analysis and recommendations for RI purchases with ROI calculations
- **Unattached Resources**: Identify and clean up unused storage volumes and snapshots
- **Real-Time Pricing**: Live pricing data integration for accurate cost calculations

### 📊 Cost Analysis & Reporting
- **Cost Forecasting**: Machine learning-powered cost predictions using scikit-learn
- **Trend Analysis**: Historical cost analysis and variance detection
- **Custom Reports**: Flexible reporting with multiple output formats (HTML, JSON, CSV)
- **Interactive Visualizations**: Charts and graphs using matplotlib, plotly, and seaborn
- **Data Export**: Export cost data and recommendations for further analysis

### 🔧 Automation & Scheduling
- **Automated Optimization**: Scheduled cost optimization tasks with configurable intervals
- **Resource Scheduling**: VM start/stop scheduling for development environments
- **Batch Processing**: Large-scale data processing and analysis across multiple accounts
- **CLI Automation**: Comprehensive command-line interface for scripting and automation
- **Configuration Management**: Centralized configuration with YAML-based settings

### 🌐 Web Dashboard
- **Flask-based Interface**: Web dashboard for cost monitoring and management
- **Real-time Updates**: Live cost data and optimization status
- **User Authentication**: Secure login system with Flask-Login
- **Mobile Responsive**: Works on desktop and mobile devices
- **Interactive Reports**: Web-based report viewing and analysis

### 🔒 Security & Performance
- **Data Encryption**: Secure handling of cloud credentials using cryptography
- **Audit Logging**: Complete audit trails for all optimization actions
- **Performance Optimization**: Intelligent caching and parallel processing
- **Rate Limiting**: API protection and usage optimization
- **Input Validation**: Protection against injection attacks and malformed data

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
- **VM Rightsizing**: ML-powered instance size recommendations using scikit-learn
- **Reserved Instances**: Automated RI analysis and purchase recommendations
- **Unattached Resources**: Identify and clean up unused storage volumes
- **Cost Forecasting**: Predict future costs based on historical data

### Monitoring & Reporting
- **Web Dashboard**: Monitor costs through Flask-based web interface
- **Custom Reports**: Generate detailed reports in HTML, JSON, and CSV formats
- **Trend Analysis**: Historical cost analysis and variance detection
- **Data Visualization**: Interactive charts using matplotlib and plotly

### Automation & Scheduling
- **Scheduled Optimization**: Automated cost optimization tasks
- **Resource Scheduling**: VM start/stop scheduling for development environments
- **Batch Processing**: Large-scale analysis across multiple cloud accounts
- **CLI Automation**: Script-friendly command-line interface

## 🚀 Technology Stack

### Core Platform
- **Backend**: Python with Flask web framework
- **CLI**: Click-based command-line interface
- **Data Processing**: Pandas and NumPy for data analysis
- **Machine Learning**: Scikit-learn for cost forecasting

### Cloud Provider SDKs
- **AWS**: Boto3 for AWS API integration
- **Azure**: Azure SDK for Python (azure-mgmt-*)
- **Google Cloud**: Google Cloud Client Libraries
- **Oracle Cloud**: OCI SDK for Python

### Data Visualization & Reporting
- **Charts**: Matplotlib, Plotly, and Seaborn for visualizations
- **Web Dashboard**: Flask with Flask-Login for authentication
- **Reports**: HTML, JSON, and CSV export formats
- **Templates**: Jinja2 for report templating

### Security & Performance
- **Encryption**: Cryptography library for secure data handling
- **Authentication**: BCrypt for password hashing
- **Performance**: Asyncio and aiohttp for async operations
- **Monitoring**: PSUtil for system monitoring

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
./scripts/create-release.sh -v 2.2.0 -t "Enhanced Features"
```

### Available Versions
- **[Latest](https://manikantesh.github.io/finopsoptimizer/)** - Development version
- **[v2.1.0](https://manikantesh.github.io/finopsoptimizer/2.1.0/)** - Enhanced Multi-Cloud Support
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
- ✅ Multi-cloud cost optimization (AWS, Azure, GCP, Oracle)
- ✅ VM rightsizing recommendations
- ✅ Reserved instance analysis
- ✅ Unattached resource cleanup
- ✅ Real-time pricing integration
- ✅ Web dashboard with Flask
- ✅ Complete setup automation
- ✅ Professional documentation system

### Upcoming Features
- 🔄 Version comparison in documentation
- 🔄 Enhanced reporting capabilities
- 🔄 Mobile-responsive improvements
- � Additionwal cloud provider integrations
- � Perfnormance optimizations

### Future Enhancements (Roadmap)
- 📋 **AI Agents**: Autonomous optimization agents with LangChain + Ollama
- 📋 **Real-Time Dashboards**: React + D3.js interactive dashboards
- 📋 **Advanced Data Stack**: Apache Kafka + Flink + Redis + Elasticsearch
- 📋 **Kubernetes-Native**: Helm charts and microservices architecture
- 📋 **Enterprise Security**: Keycloak + OPA + HashiCorp Vault integration
- 📋 **API Gateway**: Authentication and rate limiting
- 📋 **Advanced ML Models**: Enhanced cost prediction and forecasting
- 📋 **Natural Language Processing**: Chat-based cost analysis
- 📋 **Mobile Application**: Native mobile app for cost monitoring
- 📋 **Integration Hub**: CI/CD pipelines and ITSM tool integration

For the complete roadmap, see [Future Enhancements](https://manikantesh.github.io/finopsoptimizer/future-roadmap/).

---

**FinOps Optimizer** - Transform your cloud costs with multi-cloud optimization, rightsizing recommendations, and automated resource cleanup.

**🎯 Ready to optimize your cloud costs?** Start with `python quick_start.py`!
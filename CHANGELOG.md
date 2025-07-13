# Changelog

All notable changes to FinOps Optimizer will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Oracle Cloud provider support
- Web dashboard with Flask interface
- Advanced monitoring and alerting capabilities
- Custom optimization strategies
- Multi-cloud cost comparison features
- Performance optimization modules
- Security scanning and compliance checks
- Comprehensive documentation with MkDocs

### Changed
- Enhanced CLI interface with better error handling
- Improved cost allocation algorithms
- Updated configuration management
- Refactored core optimization engine

### Fixed
- Memory leaks in long-running operations
- Authentication issues with Azure provider
- Cost calculation accuracy improvements
- Documentation link fixes

## [0.2.0] - 2024-01-15

### Added
- Azure Cloud provider support
- GCP Cloud provider support
- Rightsizing recommendations
- Autoscaling optimization
- Cost allocation features
- Basic monitoring capabilities
- CLI interface improvements
- Unit and integration tests

### Changed
- Enhanced AWS provider functionality
- Improved configuration management
- Better error handling and logging

### Fixed
- Cost calculation bugs
- Authentication token refresh issues
- Memory usage optimization

## [0.1.0] - 2024-01-01

### Added
- Initial release
- AWS Cloud provider support
- Basic cost analysis
- Simple optimization recommendations
- Configuration management
- CLI interface
- Basic documentation

## Security

### [0.2.1] - 2024-01-20

#### Fixed
- CVE-2024-XXXX: Authentication bypass vulnerability
- CVE-2024-XXXX: Information disclosure in logs
- CVE-2024-XXXX: Cross-site scripting in web dashboard

### [0.2.0] - 2024-01-15

#### Fixed
- CVE-2024-XXXX: Credential exposure in configuration files
- CVE-2024-XXXX: Insecure default settings

## Migration Guide

### Upgrading from 0.1.0 to 0.2.0

1. **Configuration Changes**
   ```yaml
   # Old format
   aws:
     access_key: "your-key"
     secret_key: "your-secret"
   
   # New format
   providers:
     aws:
       enabled: true
       credentials:
         access_key_id: "your-key"
         secret_access_key: "your-secret"
   ```

2. **API Changes**
   ```python
   # Old API
   optimizer = FinOpsOptimizer(aws_config=config)
   
   # New API
   optimizer = FinOpsOptimizer(config_path="config.yaml")
   ```

3. **CLI Changes**
   ```bash
   # Old CLI
   finops-optimizer analyze --provider aws
   
   # New CLI
   finops-optimizer analyze --config config.yaml
   ```

### Upgrading from 0.2.0 to 0.3.0

1. **New Dependencies**
   ```bash
   pip install flask mkdocs-material
   ```

2. **Web Dashboard**
   ```bash
   # Start web dashboard
   finops-optimizer web --config config.yaml
   ```

3. **Monitoring Setup**
   ```yaml
   # Add monitoring configuration
   monitoring:
     enabled: true
     alert_threshold: 20.0
   ```

## Contributing

Please read [CONTRIBUTING.md](docs/contributing.md) for details on our code of conduct and the process for submitting pull requests.

## Acknowledgments

- AWS Cost Explorer API
- Azure Cost Management API
- Google Cloud Billing API
- Oracle Cloud Infrastructure API
- Flask web framework
- Material for MkDocs
- All contributors and users

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 
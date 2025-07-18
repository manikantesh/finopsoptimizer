# Contributing Guide

Thank you for your interest in contributing to FinOps Optimizer! This guide will help you get started.

## 📋 Table of Contents

- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Code Style](#code-style)
- [Testing](#testing)
- [Documentation](#documentation)
- [Pull Request Process](#pull-request-process)
- [Code of Conduct](#code-of-conduct)

## 🚀 Getting Started

### 1. Fork the Repository

1. Go to [FinOps Optimizer](https://github.com/manikantesh/finopsoptimizer)
2. Click the "Fork" button
3. Clone your fork locally

```bash
git clone https://github.com/manikantesh/finopsoptimizer.git
cd finopsoptimizer
```

### 2. Set Up Development Environment

```bash
# Create virtual environment
python -m venv venv

# Activate environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install development dependencies
pip install -r requirements-dev.txt

# Install package in development mode
pip install -e .
```

### 3. Configure Pre-commit Hooks

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run hooks manually
pre-commit run --all-files
```

## 🔧 Development Setup

### 1. Project Structure

```
finopsoptimizer/
├── finops/                 # Core library
│   ├── aws/               # AWS provider
│   ├── azure/             # Azure provider
│   ├── gcp/               # GCP provider
│   ├── oracle/            # Oracle Cloud provider
│   ├── core.py            # Main optimizer class
│   ├── config.py          # Configuration management
│   ├── performance.py     # Performance optimizations
│   ├── security.py        # Security features
│   ├── monitoring.py      # Health checks and monitoring
│   └── ...
├── web/                   # Web dashboard
├── tests/                 # Test suite
├── docs/                  # Documentation
├── examples/              # Example scripts
└── cli.py                 # Command-line interface
```

### 2. Development Dependencies

```bash
# Install development tools
pip install pytest pytest-cov pytest-mock
pip install black isort flake8 mypy
pip install bandit safety
pip install mkdocs mkdocs-material

# Install cloud provider SDKs
pip install boto3 botocore
pip install azure-mgmt-compute azure-mgmt-costmanagement
pip install google-cloud-compute google-cloud-billing
pip install oci
```

### 3. Configuration for Development

```yaml
# finops_config.yml
aws:
  enabled: true
  region: us-east-1
  # Use test credentials for development

azure:
  enabled: false

gcp:
  enabled: false

oracle:
  enabled: false

optimization:
  cpu_utilization_threshold: 0.7
  memory_utilization_threshold: 0.8

performance:
  max_workers: 2  # Lower for development
  cache_ttl: 60   # Shorter for development

output_dir: "./dev_reports"
log_level: "DEBUG"
```

## 📝 Code Style

### 1. Python Style Guide

We follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) with some modifications:

```python
# Good
def analyze_costs(provider, start_date, end_date):
    """Analyze costs for a specific provider and date range.
    
    Args:
        provider: Cloud provider instance
        start_date: Start date for analysis
        end_date: End date for analysis
    
    Returns:
        Dict containing cost analysis results
    """
    results = {}
    
    try:
        cost_data = provider.get_cost_data(start_date, end_date)
        results['total_cost'] = sum(item['cost'] for item in cost_data)
        results['breakdown'] = group_by_service(cost_data)
    except Exception as e:
        logger.error(f"Cost analysis failed: {e}")
        results['error'] = str(e)
    
    return results

# Bad
def analyzeCosts(provider,startDate,endDate):
    results={}
    try:
        costData=provider.getCostData(startDate,endDate)
        results['totalCost']=sum(item['cost'] for item in costData)
        results['breakdown']=groupByService(costData)
    except Exception as e:
        logger.error(f"Cost analysis failed: {e}")
        results['error']=str(e)
    return results
```

### 2. Import Organization

```python
# Standard library imports
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# Third-party imports
import boto3
import yaml
from flask import Flask, request, jsonify

# Local imports
from finops.core import FinOpsOptimizer
from finops.config import load_config
from finops.exceptions import FinOpsError
```

### 3. Documentation Standards

#### Docstrings

```python
def optimize_costs(cost_data: List[Dict], 
                  threshold: float = 0.7) -> List[Dict]:
    """Optimize costs based on utilization thresholds.
    
    This function analyzes cost data and generates optimization
    recommendations based on resource utilization patterns.
    
    Args:
        cost_data: List of cost data dictionaries
        threshold: Utilization threshold for optimization (default: 0.7)
    
    Returns:
        List of optimization recommendations
        
    Raises:
        ValueError: If cost_data is empty
        FinOpsError: If optimization fails
        
    Example:
        >>> cost_data = [{'resource': 'i-123', 'cost': 100, 'utilization': 0.3}]
        >>> recommendations = optimize_costs(cost_data, threshold=0.5)
        >>> len(recommendations)
        1
    """
    if not cost_data:
        raise ValueError("Cost data cannot be empty")
    
    recommendations = []
    
    for item in cost_data:
        if item['utilization'] < threshold:
            recommendation = create_recommendation(item)
            recommendations.append(recommendation)
    
    return recommendations
```

#### Type Hints

```python
from typing import Dict, List, Optional, Union, Tuple

def analyze_provider_costs(
    provider: 'CloudProvider',
    start_date: datetime,
    end_date: datetime,
    include_forecast: bool = False
) -> Dict[str, Union[float, List[Dict], str]]:
    """Analyze costs for a specific cloud provider.
    
    Args:
        provider: Cloud provider instance
        start_date: Start date for analysis
        end_date: End date for analysis
        include_forecast: Whether to include cost forecasting
    
    Returns:
        Dictionary containing analysis results
    """
    pass
```

### 4. Error Handling

```python
# Good error handling
def process_cost_data(cost_data: List[Dict]) -> Dict:
    """Process cost data with proper error handling."""
    try:
        if not cost_data:
            raise ValueError("Cost data cannot be empty")
        
        results = {
            'total_cost': 0.0,
            'service_breakdown': {},
            'errors': []
        }
        
        for item in cost_data:
            try:
                cost = float(item.get('cost', 0))
                results['total_cost'] += cost
                
                service = item.get('service', 'unknown')
                results['service_breakdown'][service] = \
                    results['service_breakdown'].get(service, 0) + cost
                    
            except (ValueError, TypeError) as e:
                results['errors'].append({
                    'item': item,
                    'error': str(e)
                })
        
        return results
        
    except Exception as e:
        logger.error(f"Failed to process cost data: {e}")
        raise FinOpsError(f"Cost data processing failed: {e}")
```

## 🧪 Testing

### 1. Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=finops --cov-report=html

# Run specific test file
pytest tests/test_core.py

# Run specific test
pytest tests/test_core.py::test_analyze_costs

# Run with verbose output
pytest -v

# Run with parallel execution
pytest -n auto
```

### 2. Writing Tests

#### Unit Tests

```python
# tests/test_core.py
import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

from finops.core import FinOpsOptimizer
from finops.exceptions import FinOpsError

class TestFinOpsOptimizer:
    """Test cases for FinOpsOptimizer class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.optimizer = FinOpsOptimizer()
        self.start_date = datetime.now() - timedelta(days=30)
        self.end_date = datetime.now()
    
    def test_analyze_costs_success(self):
        """Test successful cost analysis."""
        # Arrange
        mock_provider = Mock()
        mock_provider.analyze_costs.return_value = {
            'total_cost': 1000.0,
            'service_breakdown': {'EC2': 600.0, 'S3': 400.0}
        }
        
        # Act
        result = self.optimizer.analyze_costs(
            self.start_date, 
            self.end_date
        )
        
        # Assert
        assert result['summary']['total_cost'] == 1000.0
        assert 'EC2' in result['aws']['service_breakdown']
    
    def test_analyze_costs_empty_data(self):
        """Test cost analysis with empty data."""
        # Arrange
        mock_provider = Mock()
        mock_provider.analyze_costs.return_value = {
            'total_cost': 0.0,
            'service_breakdown': {}
        }
        
        # Act
        result = self.optimizer.analyze_costs(
            self.start_date, 
            self.end_date
        )
        
        # Assert
        assert result['summary']['total_cost'] == 0.0
    
    def test_analyze_costs_provider_error(self):
        """Test cost analysis with provider error."""
        # Arrange
        mock_provider = Mock()
        mock_provider.analyze_costs.side_effect = FinOpsError("Provider error")
        
        # Act & Assert
        with pytest.raises(FinOpsError, match="Provider error"):
            self.optimizer.analyze_costs(self.start_date, self.end_date)
    
    @pytest.mark.parametrize("start_date,end_date", [
        (datetime.now(), datetime.now() - timedelta(days=1)),
        (None, datetime.now()),
        (datetime.now(), None),
    ])
    def test_analyze_costs_invalid_dates(self, start_date, end_date):
        """Test cost analysis with invalid dates."""
        with pytest.raises(ValueError):
            self.optimizer.analyze_costs(start_date, end_date)
```

#### Integration Tests

```python
# tests/test_integration.py
import pytest
from unittest.mock import patch

from finops import FinOpsOptimizer

class TestIntegration:
    """Integration tests for FinOps Optimizer."""
    
    @patch('finops.aws.AWSProvider')
    def test_full_optimization_pipeline(self, mock_aws_provider):
        """Test complete optimization pipeline."""
        # Arrange
        mock_provider = Mock()
        mock_provider.analyze_costs.return_value = {
            'total_cost': 1000.0,
            'resources': [
                {'id': 'i-123', 'cost': 100, 'utilization': 0.3}
            ]
        }
        mock_aws_provider.return_value = mock_provider
        
        optimizer = FinOpsOptimizer()
        
        # Act
        results = optimizer.optimize_all()
        
        # Assert
        assert 'recommendations' in results
        assert 'summary' in results
        assert results['summary']['total_recommendations'] >= 0
    
    def test_configuration_loading(self):
        """Test configuration loading and validation."""
        # Arrange
        config_data = {
            'aws': {'enabled': True, 'region': 'us-east-1'},
            'optimization': {'cpu_utilization_threshold': 0.7}
        }
        
        # Act
        with patch('builtins.open', mock_open(read_data=yaml.dump(config_data))):
            optimizer = FinOpsOptimizer()
        
        # Assert
        assert optimizer.config.aws.enabled is True
        assert optimizer.config.optimization.cpu_utilization_threshold == 0.7
```

#### Performance Tests

```python
# tests/test_performance.py
import pytest
import time
from unittest.mock import Mock

from finops.performance import PerformanceOptimizer

class TestPerformance:
    """Performance tests."""
    
    def test_cache_performance(self):
        """Test cache performance."""
        optimizer = PerformanceOptimizer()
        
        # Test cache hit rate
        start_time = time.time()
        
        for i in range(100):
            optimizer.cache_result(f"test_key_{i}", f"test_value_{i}")
        
        for i in range(100):
            result = optimizer.get_cached_result(f"test_key_{i}")
            assert result == f"test_value_{i}"
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should complete within 1 second
        assert duration < 1.0
    
    def test_parallel_processing(self):
        """Test parallel processing performance."""
        optimizer = PerformanceOptimizer()
        
        def mock_task(data):
            time.sleep(0.1)  # Simulate work
            return data * 2
        
        # Test parallel execution
        data = list(range(10))
        start_time = time.time()
        
        results = optimizer.parallel_execute(
            [lambda: mock_task(i) for i in data]
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should be faster than sequential execution
        assert duration < 1.0
        assert len(results) == 10
        assert all(result == i * 2 for i, result in zip(data, results))
```

### 3. Test Configuration

```ini
# pytest.ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --strict-markers
    --strict-config
    --cov=finops
    --cov-report=html
    --cov-report=term-missing
markers =
    unit: Unit tests
    integration: Integration tests
    performance: Performance tests
    slow: Slow running tests
```

## 📚 Documentation

### 1. Code Documentation

#### Inline Comments

```python
def calculate_cost_savings(current_cost: float, 
                          optimized_cost: float) -> float:
    """Calculate cost savings percentage.
    
    Args:
        current_cost: Current monthly cost
        optimized_cost: Optimized monthly cost
    
    Returns:
        Cost savings as a percentage (0.0 to 1.0)
    """
    if current_cost <= 0:
        return 0.0
    
    # Calculate savings percentage
    savings = (current_cost - optimized_cost) / current_cost
    
    # Ensure result is between 0 and 1
    return max(0.0, min(1.0, savings))
```

#### API Documentation

```python
class FinOpsOptimizer:
    """Main class for FinOps cost optimization.
    
    This class provides methods for analyzing costs, generating
    optimization recommendations, and forecasting future costs
    across multiple cloud providers.
    
    Example:
        >>> optimizer = FinOpsOptimizer()
        >>> results = optimizer.analyze_costs()
        >>> print(f"Total cost: ${results['summary']['total_cost']:.2f}")
    """
    
    def __init__(self, config: Optional[Config] = None):
        """Initialize the FinOps optimizer.
        
        Args:
            config: Configuration object. If None, loads from
                   default locations.
        
        Raises:
            ConfigurationError: If configuration is invalid
        """
        self.config = config or load_config()
        self._validate_config()
        self._initialize_providers()
```

### 2. Documentation Standards

#### Markdown Documentation

```markdown
# Feature Name

Brief description of the feature.

## Usage

```python
from finops import FeatureName

feature = FeatureName()
result = feature.process()
```

## Configuration

```yaml
feature:
  enabled: true
  setting: value
```

## Examples

### Basic Usage

```python
# Example code here
```

### Advanced Usage

```python
# Advanced example here
```

## API Reference

### Class: FeatureName

#### Methods

##### `process() -> Dict`

Process the feature and return results.

**Returns:**
- `Dict`: Processing results

**Raises:**
- `FeatureError`: If processing fails
```

### 3. Documentation Testing

```python
# tests/test_documentation.py
import doctest
import pytest

def test_docstring_examples():
    """Test that all docstring examples work."""
    from finops.core import FinOpsOptimizer
    
    # Run doctests
    doctest.testmod(FinOpsOptimizer)
```

## 🔄 Pull Request Process

### 1. Creating a Pull Request

1. **Create a Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Your Changes**
   - Write code following our style guide
   - Add tests for new functionality
   - Update documentation

3. **Run Tests**
   ```bash
   # Run all tests
   pytest
   
   # Run linting
   black finops/
   isort finops/
   flake8 finops/
   
   # Run security checks
   bandit -r finops/
   safety check
   ```

4. **Commit Your Changes**
   ```bash
   git add .
   git commit -m "feat: add new optimization feature"
   ```

5. **Push and Create PR**
   ```bash
   git push origin feature/your-feature-name
   ```

### 2. Pull Request Template

```markdown
## Description

Brief description of the changes.

## Type of Change

- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing

- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Performance tests pass
- [ ] Documentation tests pass

## Checklist

- [ ] Code follows the style guidelines
- [ ] Self-review of code
- [ ] Code is commented, particularly in hard-to-understand areas
- [ ] Corresponding changes to documentation
- [ ] Tests added for new functionality
- [ ] All tests pass
- [ ] No security vulnerabilities introduced

## Additional Notes

Any additional information or context.
```

### 3. Review Process

1. **Automated Checks**
   - CI/CD pipeline runs tests
   - Code quality checks
   - Security scans

2. **Code Review**
   - At least one maintainer review
   - Address feedback
   - Update PR as needed

3. **Merge**
   - Squash commits if needed
   - Merge to main branch
   - Delete feature branch

## 📋 Issue Reporting

### 1. Bug Reports

When reporting bugs, include:

```markdown
## Bug Description

Clear description of the bug.

## Steps to Reproduce

1. Step 1
2. Step 2
3. Step 3

## Expected Behavior

What you expected to happen.

## Actual Behavior

What actually happened.

## Environment

- OS: [e.g., Ubuntu 20.04]
- Python: [e.g., 3.9.7]
- FinOps Optimizer: [e.g., 2.0.0]

## Additional Information

Any additional context, logs, or screenshots.
```

### 2. Feature Requests

```markdown
## Feature Description

Clear description of the requested feature.

## Use Case

Why this feature is needed.

## Proposed Solution

How you think this should be implemented.

## Alternatives Considered

Other approaches you've considered.

## Additional Information

Any additional context or examples.
```

## 🤝 Code of Conduct

### 1. Our Standards

- Use welcoming and inclusive language
- Be respectful of differing viewpoints
- Gracefully accept constructive criticism
- Focus on what is best for the community
- Show empathy towards other community members

### 2. Unacceptable Behavior

- The use of sexualized language or imagery
- Trolling, insulting/derogatory comments
- Personal or political attacks
- Publishing others' private information
- Other conduct which could reasonably be considered inappropriate

### 3. Enforcement

Violations will be addressed by the project maintainers.

## 🏆 Recognition

### 1. Contributors

All contributors will be recognized in:

- Project contributors list (see GitHub contributors tab)
- Release notes
- Project documentation

### 2. Contribution Levels

- **Bronze**: 1-5 contributions
- **Silver**: 6-20 contributions
- **Gold**: 21+ contributions
- **Platinum**: Major features or long-term maintenance

## 📞 Getting Help

### 1. Development Questions

- **GitHub Discussions**: [Start a discussion](https://github.com/manikantesh/finopsoptimizer/discussions)
- **GitHub Issues**: [Open an issue](https://github.com/manikantesh/finopsoptimizer/issues)
- **Email**: support@finopsoptimizer.com

### 2. Mentorship

New contributors can request mentorship:

1. Open an issue with the `mentorship` label
2. Describe what you'd like to work on
3. A maintainer will be assigned to help

### 3. Development Resources

- **API Reference**: [API Documentation](api-reference.md)
- **CLI Reference**: [CLI Documentation](cli-reference.md)
- **Configuration Guide**: [Configuration Documentation](configuration.md)

---

**Ready to contribute?** Start by [forking the repository](https://github.com/manikantesh/finopsoptimizer/fork) and checking out our [good first issues](https://github.com/manikantesh/finopsoptimizer/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22)! 
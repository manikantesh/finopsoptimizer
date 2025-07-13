"""
Unit tests for the core FinOpsOptimizer class.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import tempfile
import os
import json

from finops import FinOpsOptimizer
from finops.config import Config


class TestFinOpsOptimizer(unittest.TestCase):
    """Test cases for FinOpsOptimizer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = Config()
        self.config.aws.enabled = False
        self.config.azure.enabled = False
        self.config.gcp.enabled = False
        self.config.log_level = "ERROR"
        
        # Create temporary directory for test outputs
        self.test_dir = tempfile.mkdtemp()
        self.config.output_dir = self.test_dir
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_initialization(self):
        """Test FinOpsOptimizer initialization."""
        optimizer = FinOpsOptimizer(self.config)
        
        self.assertIsNotNone(optimizer.config)
        self.assertIsNotNone(optimizer.logger)
        self.assertIsInstance(optimizer.providers, dict)
        self.assertIsInstance(optimizer.cost_data, dict)
        self.assertIsInstance(optimizer.optimization_results, dict)
        self.assertIsInstance(optimizer.recommendations, list)
    
    @patch('finops.core.AWSProvider')
    def test_aws_provider_initialization(self, mock_aws_provider):
        """Test AWS provider initialization."""
        self.config.aws.enabled = True
        mock_aws_provider.return_value = Mock()
        
        optimizer = FinOpsOptimizer(self.config)
        
        self.assertIn('aws', optimizer.providers)
        mock_aws_provider.assert_called_once_with(self.config.aws)
    
    @patch('finops.core.AzureProvider')
    def test_azure_provider_initialization(self, mock_azure_provider):
        """Test Azure provider initialization."""
        self.config.azure.enabled = True
        mock_azure_provider.return_value = Mock()
        
        optimizer = FinOpsOptimizer(self.config)
        
        self.assertIn('azure', optimizer.providers)
        mock_azure_provider.assert_called_once_with(self.config.azure)
    
    @patch('finops.core.GCPProvider')
    def test_gcp_provider_initialization(self, mock_gcp_provider):
        """Test GCP provider initialization."""
        self.config.gcp.enabled = True
        mock_gcp_provider.return_value = Mock()
        
        optimizer = FinOpsOptimizer(self.config)
        
        self.assertIn('gcp', optimizer.providers)
        mock_gcp_provider.assert_called_once_with(self.config.gcp)
    
    def test_analyze_costs_no_providers(self):
        """Test cost analysis with no providers enabled."""
        optimizer = FinOpsOptimizer(self.config)
        
        results = optimizer.analyze_costs()
        
        self.assertIn('summary', results)
        self.assertEqual(results['summary']['total_cost'], 0)
        self.assertEqual(results['summary']['providers_analyzed'], [])
    
    @patch('finops.core.AWSProvider')
    def test_analyze_costs_with_provider(self, mock_aws_provider):
        """Test cost analysis with AWS provider."""
        self.config.aws.enabled = True
        mock_provider = Mock()
        mock_provider.analyze_costs.return_value = {
            'total_cost': 100.0,
            'service_breakdown': {'EC2': 50.0, 'S3': 50.0}
        }
        mock_aws_provider.return_value = mock_provider
        
        optimizer = FinOpsOptimizer(self.config)
        results = optimizer.analyze_costs()
        
        self.assertEqual(results['summary']['total_cost'], 100.0)
        self.assertIn('aws', results)
        self.assertEqual(results['aws']['total_cost'], 100.0)
    
    def test_generate_recommendations_no_data(self):
        """Test recommendation generation with no cost data."""
        optimizer = FinOpsOptimizer(self.config)
        
        recommendations = optimizer.generate_recommendations()
        
        self.assertIsInstance(recommendations, list)
        # Should still generate some recommendations even without cost data
    
    def test_allocate_costs(self):
        """Test cost allocation."""
        optimizer = FinOpsOptimizer(self.config)
        
        allocation_rules = {
            'method': 'tag_based',
            'tags': ['Environment', 'Project']
        }
        
        # Mock cost data
        optimizer.cost_data = {
            'aws': {'total_cost': 100.0},
            'azure': {'total_cost': 50.0}
        }
        
        results = optimizer.allocate_costs(allocation_rules)
        
        self.assertIsInstance(results, dict)
    
    def test_forecast_costs(self):
        """Test cost forecasting."""
        optimizer = FinOpsOptimizer(self.config)
        
        # Mock cost data
        optimizer.cost_data = {
            'aws': {'total_cost': 100.0},
            'azure': {'total_cost': 50.0}
        }
        
        forecast = optimizer.forecast_costs(30)
        
        self.assertIsInstance(forecast, dict)
        self.assertIn('total_forecast', forecast)
    
    def test_generate_report(self):
        """Test report generation."""
        optimizer = FinOpsOptimizer(self.config)
        
        report_path = optimizer.generate_report()
        
        self.assertIsInstance(report_path, str)
        self.assertTrue(os.path.exists(report_path))
    
    def test_optimize_all(self):
        """Test complete optimization pipeline."""
        optimizer = FinOpsOptimizer(self.config)
        
        results = optimizer.optimize_all()
        
        self.assertIsInstance(results, dict)
        self.assertIn('summary', results)
        self.assertIn('recommendations', results)
        self.assertIn('cost_analysis', results)
        self.assertIn('forecast', results)
    
    def test_get_provider_status(self):
        """Test provider status checking."""
        optimizer = FinOpsOptimizer(self.config)
        
        status = optimizer.get_provider_status()
        
        self.assertIsInstance(status, dict)
        self.assertFalse(status.get('aws', False))
        self.assertFalse(status.get('azure', False))
        self.assertFalse(status.get('gcp', False))
    
    def test_validate_credentials(self):
        """Test credential validation."""
        optimizer = FinOpsOptimizer(self.config)
        
        validation = optimizer.validate_credentials()
        
        self.assertIsInstance(validation, dict)
        # Should return validation results for each provider


if __name__ == '__main__':
    unittest.main() 
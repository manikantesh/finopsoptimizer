"""
Unit tests for the configuration module.
"""

import unittest
import tempfile
import os
import yaml
from unittest.mock import patch, mock_open

from finops.config import Config, load_config, validate_config


class TestConfig(unittest.TestCase):
    """Test cases for Config class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_config_initialization(self):
        """Test Config class initialization."""
        config = Config()
        
        self.assertIsNotNone(config.aws)
        self.assertIsNotNone(config.azure)
        self.assertIsNotNone(config.gcp)
        self.assertIsNotNone(config.optimization)
        self.assertIsNotNone(config.output_dir)
        self.assertIsNotNone(config.log_level)
    
    def test_aws_config(self):
        """Test AWS configuration."""
        config = Config()
        
        self.assertFalse(config.aws.enabled)
        self.assertEqual(config.aws.region, "us-east-1")
        self.assertIsNone(config.aws.account_id)
    
    def test_azure_config(self):
        """Test Azure configuration."""
        config = Config()
        
        self.assertFalse(config.azure.enabled)
        self.assertIsNone(config.azure.subscription_id)
    
    def test_gcp_config(self):
        """Test GCP configuration."""
        config = Config()
        
        self.assertFalse(config.gcp.enabled)
        self.assertIsNone(config.gcp.project_id)
    
    def test_optimization_config(self):
        """Test optimization configuration."""
        config = Config()
        
        self.assertEqual(config.optimization.cpu_utilization_threshold, 0.7)
        self.assertEqual(config.optimization.memory_utilization_threshold, 0.8)
        self.assertEqual(config.optimization.cost_savings_threshold, 0.1)
        self.assertEqual(config.optimization.min_instances, 1)
        self.assertEqual(config.optimization.max_instances, 10)
        self.assertEqual(config.optimization.scale_up_threshold, 0.8)
        self.assertEqual(config.optimization.scale_down_threshold, 0.3)
    
    def test_load_config_from_file(self):
        """Test loading configuration from file."""
        config_data = {
            'aws': {
                'enabled': True,
                'region': 'us-west-2',
                'account_id': '123456789012'
            },
            'azure': {
                'enabled': True,
                'subscription_id': 'azure-sub-id'
            },
            'gcp': {
                'enabled': True,
                'project_id': 'gcp-project-id'
            },
            'optimization': {
                'cpu_utilization_threshold': 0.8,
                'memory_utilization_threshold': 0.9
            },
            'output_dir': '/tmp/finops',
            'log_level': 'DEBUG'
        }
        
        config_yaml = yaml.dump(config_data)
        
        with patch('builtins.open', mock_open(read_data=config_yaml)):
            config = load_config('test_config.yml')
        
        self.assertTrue(config.aws.enabled)
        self.assertEqual(config.aws.region, 'us-west-2')
        self.assertEqual(config.aws.account_id, '123456789012')
        self.assertTrue(config.azure.enabled)
        self.assertEqual(config.azure.subscription_id, 'azure-sub-id')
        self.assertTrue(config.gcp.enabled)
        self.assertEqual(config.gcp.project_id, 'gcp-project-id')
        self.assertEqual(config.optimization.cpu_utilization_threshold, 0.8)
        self.assertEqual(config.optimization.memory_utilization_threshold, 0.9)
        self.assertEqual(config.output_dir, '/tmp/finops')
        self.assertEqual(config.log_level, 'DEBUG')
    
    def test_load_config_default(self):
        """Test loading default configuration."""
        config = load_config()
        
        self.assertIsInstance(config, Config)
        self.assertFalse(config.aws.enabled)
        self.assertFalse(config.azure.enabled)
        self.assertFalse(config.gcp.enabled)
    
    def test_validate_config(self):
        """Test configuration validation."""
        config = Config()
        
        # Valid configuration
        validation = validate_config(config)
        self.assertTrue(validation['valid'])
        
        # Invalid configuration - invalid thresholds
        config.optimization.cpu_utilization_threshold = 1.5
        validation = validate_config(config)
        self.assertFalse(validation['valid'])
        self.assertIn('cpu_utilization_threshold', validation['errors'])
    
    def test_validate_config_invalid_thresholds(self):
        """Test validation with invalid thresholds."""
        config = Config()
        
        # Test invalid CPU threshold
        config.optimization.cpu_utilization_threshold = 1.5
        validation = validate_config(config)
        self.assertFalse(validation['valid'])
        
        # Test invalid memory threshold
        config.optimization.memory_utilization_threshold = -0.1
        validation = validate_config(config)
        self.assertFalse(validation['valid'])
        
        # Test invalid cost savings threshold
        config.optimization.cost_savings_threshold = 2.0
        validation = validate_config(config)
        self.assertFalse(validation['valid'])
    
    def test_validate_config_invalid_instances(self):
        """Test validation with invalid instance counts."""
        config = Config()
        
        # Test invalid min instances
        config.optimization.min_instances = -1
        validation = validate_config(config)
        self.assertFalse(validation['valid'])
        
        # Test invalid max instances
        config.optimization.max_instances = 0
        validation = validate_config(config)
        self.assertFalse(validation['valid'])
        
        # Test min > max
        config.optimization.min_instances = 10
        config.optimization.max_instances = 5
        validation = validate_config(config)
        self.assertFalse(validation['valid'])
    
    def test_validate_config_invalid_scaling_thresholds(self):
        """Test validation with invalid scaling thresholds."""
        config = Config()
        
        # Test invalid scale up threshold
        config.optimization.scale_up_threshold = 1.5
        validation = validate_config(config)
        self.assertFalse(validation['valid'])
        
        # Test invalid scale down threshold
        config.optimization.scale_down_threshold = -0.1
        validation = validate_config(config)
        self.assertFalse(validation['valid'])
        
        # Test scale down > scale up
        config.optimization.scale_up_threshold = 0.5
        config.optimization.scale_down_threshold = 0.8
        validation = validate_config(config)
        self.assertFalse(validation['valid'])
    
    def test_environment_variable_loading(self):
        """Test loading configuration from environment variables."""
        env_vars = {
            'AWS_ACCESS_KEY_ID': 'test-access-key',
            'AWS_SECRET_ACCESS_KEY': 'test-secret-key',
            'AWS_DEFAULT_REGION': 'us-west-2',
            'AZURE_CLIENT_ID': 'test-client-id',
            'AZURE_CLIENT_SECRET': 'test-client-secret',
            'AZURE_TENANT_ID': 'test-tenant-id',
            'GOOGLE_APPLICATION_CREDENTIALS': '/path/to/credentials.json'
        }
        
        with patch.dict(os.environ, env_vars):
            config = load_config()
            
            # Note: Environment variables are typically handled by the cloud SDKs
            # This test verifies the config can be loaded with env vars present
            self.assertIsInstance(config, Config)


if __name__ == '__main__':
    unittest.main() 
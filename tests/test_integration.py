"""
Integration tests for FinOpsOptimizer.
"""

import unittest
import tempfile
import os
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

from finops import FinOpsOptimizer
from finops.config import Config


class TestFinOpsIntegration(unittest.TestCase):
    """Integration tests for FinOpsOptimizer."""
    
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
    
    @patch('finops.core.AWSProvider')
    @patch('finops.core.AzureProvider')
    @patch('finops.core.GCPProvider')
    def test_complete_optimization_workflow(self, mock_gcp, mock_azure, mock_aws):
        """Test complete optimization workflow with all providers."""
        # Mock AWS provider
        mock_aws_instance = Mock()
        mock_aws_instance.analyze_costs.return_value = {
            'total_cost': 1000.0,
            'service_breakdown': {'EC2': 600.0, 'S3': 300.0, 'RDS': 100.0},
            'resources': [
                {'id': 'i-123456', 'type': 'EC2', 'cost': 100.0, 'utilization': 0.3},
                {'id': 'i-789012', 'type': 'EC2', 'cost': 200.0, 'utilization': 0.8}
            ]
        }
        mock_aws.return_value = mock_aws_instance
        
        # Mock Azure provider
        mock_azure_instance = Mock()
        mock_azure_instance.analyze_costs.return_value = {
            'total_cost': 800.0,
            'service_breakdown': {'Virtual Machines': 500.0, 'Storage': 200.0, 'SQL': 100.0},
            'resources': [
                {'id': 'vm-123', 'type': 'Virtual Machine', 'cost': 150.0, 'utilization': 0.4},
                {'id': 'vm-456', 'type': 'Virtual Machine', 'cost': 250.0, 'utilization': 0.9}
            ]
        }
        mock_azure.return_value = mock_azure_instance
        
        # Mock GCP provider
        mock_gcp_instance = Mock()
        mock_gcp_instance.analyze_costs.return_value = {
            'total_cost': 600.0,
            'service_breakdown': {'Compute Engine': 400.0, 'Cloud Storage': 150.0, 'Cloud SQL': 50.0},
            'resources': [
                {'id': 'instance-123', 'type': 'Compute Engine', 'cost': 100.0, 'utilization': 0.5},
                {'id': 'instance-456', 'type': 'Compute Engine', 'cost': 200.0, 'utilization': 0.7}
            ]
        }
        mock_gcp.return_value = mock_gcp_instance
        
        # Enable all providers
        self.config.aws.enabled = True
        self.config.azure.enabled = True
        self.config.gcp.enabled = True
        
        optimizer = FinOpsOptimizer(self.config)
        
        # Run complete optimization
        results = optimizer.optimize_all()
        
        # Verify results structure
        self.assertIn('summary', results)
        self.assertIn('recommendations', results)
        self.assertIn('cost_analysis', results)
        self.assertIn('forecast', results)
        self.assertIn('report_path', results)
        
        # Verify summary
        summary = results['summary']
        self.assertGreater(summary['total_recommendations'], 0)
        self.assertGreater(summary['total_potential_savings'], 0)
        self.assertEqual(len(summary['providers_analyzed']), 3)
        
        # Verify cost analysis
        cost_analysis = results['cost_analysis']
        self.assertIn('aws', cost_analysis)
        self.assertIn('azure', cost_analysis)
        self.assertIn('gcp', cost_analysis)
        self.assertEqual(cost_analysis['summary']['total_cost'], 2400.0)
        
        # Verify recommendations
        recommendations = results['recommendations']
        self.assertIsInstance(recommendations, list)
        self.assertGreater(len(recommendations), 0)
        
        # Verify report was generated
        self.assertTrue(os.path.exists(results['report_path']))
    
    @patch('finops.core.AWSProvider')
    def test_cost_analysis_workflow(self, mock_aws):
        """Test cost analysis workflow."""
        # Mock AWS provider
        mock_aws_instance = Mock()
        mock_aws_instance.analyze_costs.return_value = {
            'total_cost': 1000.0,
            'service_breakdown': {'EC2': 600.0, 'S3': 300.0, 'RDS': 100.0},
            'daily_costs': [
                {'date': '2024-01-01', 'cost': 33.33},
                {'date': '2024-01-02', 'cost': 33.33},
                {'date': '2024-01-03', 'cost': 33.34}
            ]
        }
        mock_aws.return_value = mock_aws_instance
        
        self.config.aws.enabled = True
        optimizer = FinOpsOptimizer(self.config)
        
        # Test cost analysis
        results = optimizer.analyze_costs()
        
        self.assertIn('aws', results)
        self.assertEqual(results['aws']['total_cost'], 1000.0)
        self.assertEqual(results['summary']['total_cost'], 1000.0)
        self.assertIn('aws', results['summary']['providers_analyzed'])
        
        # Test with custom date range
        start_date = datetime.now() - timedelta(days=7)
        end_date = datetime.now()
        
        results = optimizer.analyze_costs(start_date, end_date)
        
        self.assertIn('summary', results)
        self.assertIn('analysis_period', results['summary'])
    
    @patch('finops.core.AWSProvider')
    def test_recommendation_generation_workflow(self, mock_aws):
        """Test recommendation generation workflow."""
        # Mock AWS provider with detailed resource data
        mock_aws_instance = Mock()
        mock_aws_instance.analyze_costs.return_value = {
            'total_cost': 1000.0,
            'service_breakdown': {'EC2': 600.0, 'S3': 300.0, 'RDS': 100.0},
            'resources': [
                {
                    'id': 'i-123456',
                    'type': 'EC2',
                    'instance_type': 't3.large',
                    'cost': 100.0,
                    'utilization': 0.3,
                    'region': 'us-east-1',
                    'tags': {'Environment': 'dev', 'Project': 'webapp'}
                },
                {
                    'id': 'i-789012',
                    'type': 'EC2',
                    'instance_type': 't3.xlarge',
                    'cost': 200.0,
                    'utilization': 0.8,
                    'region': 'us-east-1',
                    'tags': {'Environment': 'prod', 'Project': 'webapp'}
                }
            ]
        }
        mock_aws.return_value = mock_aws_instance
        
        self.config.aws.enabled = True
        optimizer = FinOpsOptimizer(self.config)
        
        # Analyze costs first
        cost_results = optimizer.analyze_costs()
        
        # Generate recommendations
        recommendations = optimizer.generate_recommendations()
        
        self.assertIsInstance(recommendations, list)
        self.assertGreater(len(recommendations), 0)
        
        # Verify recommendation structure
        for rec in recommendations:
            self.assertIn('type', rec)
            self.assertIn('description', rec)
            self.assertIn('potential_savings', rec)
            self.assertIn('priority', rec)
            self.assertIn('provider', rec)
    
    @patch('finops.core.AWSProvider')
    def test_cost_forecasting_workflow(self, mock_aws):
        """Test cost forecasting workflow."""
        # Mock AWS provider with historical data
        mock_aws_instance = Mock()
        mock_aws_instance.analyze_costs.return_value = {
            'total_cost': 1000.0,
            'service_breakdown': {'EC2': 600.0, 'S3': 300.0, 'RDS': 100.0},
            'daily_costs': [
                {'date': '2024-01-01', 'cost': 33.33},
                {'date': '2024-01-02', 'cost': 33.33},
                {'date': '2024-01-03', 'cost': 33.34}
            ]
        }
        mock_aws.return_value = mock_aws_instance
        
        self.config.aws.enabled = True
        optimizer = FinOpsOptimizer(self.config)
        
        # Analyze costs first
        cost_results = optimizer.analyze_costs()
        
        # Generate forecast
        forecast = optimizer.forecast_costs(30)
        
        self.assertIn('total_forecast', forecast)
        self.assertIn('provider_forecasts', forecast)
        self.assertIn('aws', forecast['provider_forecasts'])
        
        # Test forecast with recommendations
        forecast_with_recs = optimizer.forecast_costs(30, include_recommendations=True)
        
        self.assertIn('recommendations_impact', forecast_with_recs)
    
    @patch('finops.core.AWSProvider')
    def test_cost_allocation_workflow(self, mock_aws):
        """Test cost allocation workflow."""
        # Mock AWS provider
        mock_aws_instance = Mock()
        mock_aws_instance.analyze_costs.return_value = {
            'total_cost': 1000.0,
            'service_breakdown': {'EC2': 600.0, 'S3': 300.0, 'RDS': 100.0},
            'resources': [
                {
                    'id': 'i-123456',
                    'type': 'EC2',
                    'cost': 100.0,
                    'tags': {'Environment': 'dev', 'Project': 'webapp', 'Team': 'engineering'}
                },
                {
                    'id': 'i-789012',
                    'type': 'EC2',
                    'cost': 200.0,
                    'tags': {'Environment': 'prod', 'Project': 'webapp', 'Team': 'engineering'}
                }
            ]
        }
        mock_aws.return_value = mock_aws_instance
        
        self.config.aws.enabled = True
        optimizer = FinOpsOptimizer(self.config)
        
        # Analyze costs first
        cost_results = optimizer.analyze_costs()
        
        # Test cost allocation
        allocation_rules = {
            'method': 'tag_based',
            'tags': ['Environment', 'Project', 'Team'],
            'departments': ['Engineering', 'Marketing'],
            'projects': ['WebApp', 'MobileApp']
        }
        
        allocation_results = optimizer.allocate_costs(allocation_rules)
        
        self.assertIn('allocated_costs', allocation_results)
        self.assertIn('summary', allocation_results)
        self.assertIn('by_department', allocation_results['allocated_costs'])
        self.assertIn('by_project', allocation_results['allocated_costs'])
    
    @patch('finops.core.AWSProvider')
    def test_report_generation_workflow(self, mock_aws):
        """Test report generation workflow."""
        # Mock AWS provider
        mock_aws_instance = Mock()
        mock_aws_instance.analyze_costs.return_value = {
            'total_cost': 1000.0,
            'service_breakdown': {'EC2': 600.0, 'S3': 300.0, 'RDS': 100.0}
        }
        mock_aws.return_value = mock_aws_instance
        
        self.config.aws.enabled = True
        optimizer = FinOpsOptimizer(self.config)
        
        # Analyze costs first
        cost_results = optimizer.analyze_costs()
        
        # Test different report formats
        html_report = optimizer.generate_report('comprehensive', 'html')
        self.assertTrue(os.path.exists(html_report))
        self.assertTrue(html_report.endswith('.html'))
        
        json_report = optimizer.generate_report('summary', 'json')
        self.assertTrue(os.path.exists(json_report))
        self.assertTrue(json_report.endswith('.json'))
        
        pdf_report = optimizer.generate_report('recommendations', 'pdf')
        self.assertTrue(os.path.exists(pdf_report))
        self.assertTrue(pdf_report.endswith('.pdf'))
    
    def test_error_handling_workflow(self):
        """Test error handling in workflows."""
        # Test with no providers enabled
        optimizer = FinOpsOptimizer(self.config)
        
        # Should handle gracefully
        results = optimizer.analyze_costs()
        self.assertEqual(results['summary']['total_cost'], 0)
        self.assertEqual(results['summary']['providers_analyzed'], [])
        
        recommendations = optimizer.generate_recommendations()
        self.assertIsInstance(recommendations, list)
        
        forecast = optimizer.forecast_costs(30)
        self.assertIn('total_forecast', forecast)
        
        report_path = optimizer.generate_report()
        self.assertTrue(os.path.exists(report_path))


if __name__ == '__main__':
    unittest.main() 
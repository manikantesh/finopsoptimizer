"""
AWS provider implementation for cost optimization.
"""

import boto3
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from botocore.exceptions import ClientError, NoCredentialsError

from ..config import CloudConfig


class AWSProvider:
    """
    AWS provider for cost optimization operations.
    
    Handles AWS-specific cost analysis, rightsizing, and autoscaling optimization.
    """
    
    def __init__(self, config: CloudConfig):
        """
        Initialize AWS provider.
        
        Args:
            config: AWS-specific configuration
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize AWS clients
        self._initialize_clients()
        
        # Initialize analyzers
        from .cost_analyzer import AWSCostAnalyzer
        from .rightsizing import AWSRightsizingAnalyzer
        from .autoscaling import AWSAutoscalingOptimizer
        
        self.cost_analyzer = AWSCostAnalyzer(self)
        self.rightsizing_analyzer = AWSRightsizingAnalyzer(self)
        self.autoscaling_optimizer = AWSAutoscalingOptimizer(self)
    
    def _initialize_clients(self) -> None:
        """Initialize AWS service clients."""
        try:
            # Set up session
            if self.config.region:
                self.session = boto3.Session(region_name=self.config.region)
            else:
                self.session = boto3.Session()
            
            # Initialize service clients
            self.ce_client = self.session.client('ce')  # Cost Explorer
            self.ec2_client = self.session.client('ec2')
            self.rds_client = self.session.client('rds')
            self.elasticache_client = self.session.client('elasticache')
            self.cloudwatch_client = self.session.client('cloudwatch')
            self.autoscaling_client = self.session.client('autoscaling')
            self.organizations_client = self.session.client('organizations')
            
            # Test connection
            self._test_connection()
            
        except NoCredentialsError:
            self.logger.error("AWS credentials not found")
            raise
        except Exception as e:
            self.logger.error(f"Failed to initialize AWS clients: {e}")
            raise
    
    def _test_connection(self) -> None:
        """Test AWS connection by making a simple API call."""
        try:
            # Test with a simple API call
            self.ce_client.get_cost_and_usage(
                TimePeriod={
                    'Start': (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'),
                    'End': datetime.now().strftime('%Y-%m-%d')
                },
                Granularity='DAILY',
                Metrics=['UnblendedCost']
            )
            self.logger.info("AWS connection test successful")
        except Exception as e:
            self.logger.error(f"AWS connection test failed: {e}")
            raise
    
    def is_connected(self) -> bool:
        """Check if AWS provider is properly connected."""
        try:
            self._test_connection()
            return True
        except:
            return False
    
    def analyze_costs(self, 
                     start_date: datetime,
                     end_date: datetime) -> Dict[str, Any]:
        """
        Analyze AWS costs for the specified period.
        
        Args:
            start_date: Start date for cost analysis
            end_date: End date for cost analysis
            
        Returns:
            Dictionary containing cost analysis results
        """
        return self.cost_analyzer.analyze_costs(start_date, end_date)
    
    def get_ec2_instances(self) -> List[Dict[str, Any]]:
        """
        Get all EC2 instances with their details.
        
        Returns:
            List of EC2 instance details
        """
        try:
            response = self.ec2_client.describe_instances()
            instances = []
            
            for reservation in response['Reservations']:
                for instance in reservation['Instances']:
                    instances.append({
                        'instance_id': instance['InstanceId'],
                        'instance_type': instance['InstanceType'],
                        'state': instance['State']['Name'],
                        'launch_time': instance['LaunchTime'],
                        'tags': instance.get('Tags', []),
                        'vpc_id': instance.get('VpcId'),
                        'subnet_id': instance.get('SubnetId'),
                        'availability_zone': instance['Placement']['AvailabilityZone']
                    })
            
            return instances
            
        except ClientError as e:
            self.logger.error(f"Error getting EC2 instances: {e}")
            return []
    
    def get_rds_instances(self) -> List[Dict[str, Any]]:
        """
        Get all RDS instances with their details.
        
        Returns:
            List of RDS instance details
        """
        try:
            response = self.rds_client.describe_db_instances()
            instances = []
            
            for instance in response['DBInstances']:
                instances.append({
                    'db_instance_identifier': instance['DBInstanceIdentifier'],
                    'db_instance_class': instance['DBInstanceClass'],
                    'engine': instance['Engine'],
                    'status': instance['DBInstanceStatus'],
                    'allocated_storage': instance.get('AllocatedStorage'),
                    'storage_type': instance.get('StorageType'),
                    'multi_az': instance.get('MultiAZ', False),
                    'tags': instance.get('TagList', [])
                })
            
            return instances
            
        except ClientError as e:
            self.logger.error(f"Error getting RDS instances: {e}")
            return []
    
    def get_autoscaling_groups(self) -> List[Dict[str, Any]]:
        """
        Get all Auto Scaling groups with their details.
        
        Returns:
            List of Auto Scaling group details
        """
        try:
            response = self.autoscaling_client.describe_auto_scaling_groups()
            groups = []
            
            for group in response['AutoScalingGroups']:
                groups.append({
                    'auto_scaling_group_name': group['AutoScalingGroupName'],
                    'min_size': group['MinSize'],
                    'max_size': group['MaxSize'],
                    'desired_capacity': group['DesiredCapacity'],
                    'instances': [inst['InstanceId'] for inst in group['Instances']],
                    'target_group_arns': group.get('TargetGroupARNs', []),
                    'load_balancer_names': group.get('LoadBalancerNames', [])
                })
            
            return groups
            
        except ClientError as e:
            self.logger.error(f"Error getting Auto Scaling groups: {e}")
            return []
    
    def get_cloudwatch_metrics(self, 
                              namespace: str,
                              metric_name: str,
                              dimensions: List[Dict[str, str]],
                              start_time: datetime,
                              end_time: datetime,
                              period: int = 3600) -> List[Dict[str, Any]]:
        """
        Get CloudWatch metrics for analysis.
        
        Args:
            namespace: CloudWatch namespace
            metric_name: Name of the metric
            dimensions: Metric dimensions
            start_time: Start time for metrics
            end_time: End time for metrics
            period: Metric period in seconds
            
        Returns:
            List of metric data points
        """
        try:
            response = self.cloudwatch_client.get_metric_statistics(
                Namespace=namespace,
                MetricName=metric_name,
                Dimensions=dimensions,
                StartTime=start_time,
                EndTime=end_time,
                Period=period,
                Statistics=['Average', 'Maximum', 'Minimum']
            )
            
            return response['Datapoints']
            
        except ClientError as e:
            self.logger.error(f"Error getting CloudWatch metrics: {e}")
            return []
    
    def get_cost_and_usage(self,
                          start_date: datetime,
                          end_date: datetime,
                          granularity: str = 'DAILY',
                          group_by: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
        """
        Get cost and usage data from AWS Cost Explorer.
        
        Args:
            start_date: Start date for cost data
            end_date: End date for cost data
            granularity: Data granularity (DAILY, MONTHLY, HOURLY)
            group_by: Grouping dimensions
            
        Returns:
            Cost and usage data
        """
        try:
            params = {
                'TimePeriod': {
                    'Start': start_date.strftime('%Y-%m-%d'),
                    'End': end_date.strftime('%Y-%m-%d')
                },
                'Granularity': granularity,
                'Metrics': ['UnblendedCost', 'UsageQuantity']
            }
            
            if group_by:
                params['GroupBy'] = group_by
            
            response = self.ce_client.get_cost_and_usage(**params)
            return response
            
        except ClientError as e:
            self.logger.error(f"Error getting cost and usage data: {e}")
            return {}
    
    def get_rightsizing_recommendations(self) -> List[Dict[str, Any]]:
        """
        Get rightsizing recommendations from AWS Cost Explorer.
        
        Returns:
            List of rightsizing recommendations
        """
        try:
            response = self.ce_client.get_rightsizing_recommendation(
                Service='AmazonEC2'
            )
            
            recommendations = []
            for recommendation in response.get('RightsizingRecommendations', []):
                recommendations.append({
                    'account_id': recommendation.get('AccountId'),
                    'current_instance': recommendation.get('CurrentInstance'),
                    'rightsizing_type': recommendation.get('RightsizingType'),
                    'modify_recommendation': recommendation.get('ModifyRecommendation'),
                    'terminate_recommendation': recommendation.get('TerminateRecommendation')
                })
            
            return recommendations
            
        except ClientError as e:
            self.logger.error(f"Error getting rightsizing recommendations: {e}")
            return []
    
    def get_savings_plans_recommendations(self) -> List[Dict[str, Any]]:
        """
        Get Savings Plans recommendations.
        
        Returns:
            List of Savings Plans recommendations
        """
        try:
            response = self.ce_client.get_savings_plans_recommendation(
                LookbackPeriodInDays=30,
                TermInYears=1,
                SavingsPlansType='COMPUTE_SP'
            )
            
            recommendations = []
            for recommendation in response.get('SavingsPlansRecommendation', []):
                recommendations.append({
                    'estimated_savings_amount': recommendation.get('EstimatedSavingsAmount'),
                    'estimated_savings_percentage': recommendation.get('EstimatedSavingsPercentage'),
                    'hourly_commitment_to_purchase': recommendation.get('HourlyCommitmentToPurchase'),
                    'upfront_cost': recommendation.get('UpfrontCost')
                })
            
            return recommendations
            
        except ClientError as e:
            self.logger.error(f"Error getting Savings Plans recommendations: {e}")
            return [] 
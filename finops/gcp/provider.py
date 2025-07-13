"""
GCP provider implementation for cost optimization.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from google.cloud import billing_v1, compute_v1, monitoring_v3
from google.cloud import resourcemanager_v3
from google.api_core import exceptions as google_exceptions

from ..config import CloudConfig


class GCPProvider:
    """
    GCP provider for cost optimization operations.
    
    Handles GCP-specific cost analysis, rightsizing, and autoscaling optimization.
    """
    
    def __init__(self, config: CloudConfig):
        """
        Initialize GCP provider.
        
        Args:
            config: GCP-specific configuration
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize GCP clients
        self._initialize_clients()
        
        # Initialize analyzers
        from .cost_analyzer import GCPCostAnalyzer
        from .rightsizing import GCPRightsizingAnalyzer
        from .autoscaling import GCPAutoscalingOptimizer
        
        self.cost_analyzer = GCPCostAnalyzer(self)
        self.rightsizing_analyzer = GCPRightsizingAnalyzer(self)
        self.autoscaling_optimizer = GCPAutoscalingOptimizer(self)
    
    def _initialize_clients(self) -> None:
        """Initialize GCP service clients."""
        try:
            # Initialize service clients
            self.billing_client = billing_v1.CloudBillingClient()
            self.compute_client = compute_v1.InstancesClient()
            self.monitoring_client = monitoring_v3.MetricServiceClient()
            self.resource_manager_client = resourcemanager_v3.ProjectsClient()
            
            # Test connection
            self._test_connection()
            
        except Exception as e:
            self.logger.error(f"Failed to initialize GCP clients: {e}")
            raise
    
    def _test_connection(self) -> None:
        """Test GCP connection by making a simple API call."""
        try:
            # Test with a simple API call
            if self.config.project_id:
                self.compute_client.list(project=self.config.project_id, zone="us-central1-a")
            self.logger.info("GCP connection test successful")
        except Exception as e:
            self.logger.error(f"GCP connection test failed: {e}")
            raise
    
    def is_connected(self) -> bool:
        """Check if GCP provider is properly connected."""
        try:
            self._test_connection()
            return True
        except:
            return False
    
    def analyze_costs(self, 
                     start_date: datetime,
                     end_date: datetime) -> Dict[str, Any]:
        """
        Analyze GCP costs for the specified period.
        
        Args:
            start_date: Start date for cost analysis
            end_date: End date for cost analysis
            
        Returns:
            Dictionary containing cost analysis results
        """
        return self.cost_analyzer.analyze_costs(start_date, end_date)
    
    def get_compute_instances(self) -> List[Dict[str, Any]]:
        """
        Get all Compute Engine instances with their details.
        
        Returns:
            List of Compute Engine instance details
        """
        try:
            instances = []
            
            if not self.config.project_id:
                self.logger.error("Project ID not configured for GCP")
                return []
            
            # List instances across all zones
            zones = self._get_zones()
            
            for zone in zones:
                try:
                    request = compute_v1.ListInstancesRequest(
                        project=self.config.project_id,
                        zone=zone
                    )
                    
                    page_result = self.compute_client.list(request=request)
                    
                    for instance in page_result:
                        instance_data = {
                            'id': instance.id,
                            'name': instance.name,
                            'zone': zone,
                            'machine_type': instance.machine_type.split('/')[-1],
                            'status': instance.status,
                            'creation_timestamp': instance.creation_timestamp,
                            'labels': instance.labels or {},
                            'tags': instance.tags.items if instance.tags else []
                        }
                        instances.append(instance_data)
                        
                except google_exceptions.GoogleAPIError as e:
                    self.logger.warning(f"Error getting instances from zone {zone}: {e}")
                    continue
            
            return instances
            
        except Exception as e:
            self.logger.error(f"Error getting Compute Engine instances: {e}")
            return []
    
    def get_sql_instances(self) -> List[Dict[str, Any]]:
        """
        Get all Cloud SQL instances with their details.
        
        Returns:
            List of Cloud SQL instance details
        """
        try:
            # This would use the Cloud SQL Admin API
            # For now, return a placeholder
            return []
            
        except Exception as e:
            self.logger.error(f"Error getting Cloud SQL instances: {e}")
            return []
    
    def get_instance_groups(self) -> List[Dict[str, Any]]:
        """
        Get all Instance Groups with their details.
        
        Returns:
            List of Instance Group details
        """
        try:
            # This would use the Compute Engine API for instance groups
            # For now, return a placeholder
            return []
            
        except Exception as e:
            self.logger.error(f"Error getting Instance Groups: {e}")
            return []
    
    def get_billing_data(self,
                        start_date: datetime,
                        end_date: datetime,
                        project_id: str = None) -> Dict[str, Any]:
        """
        Get billing data from GCP Cloud Billing API.
        
        Args:
            start_date: Start date for billing data
            end_date: End date for billing data
            project_id: Project ID (uses config if not provided)
            
        Returns:
            Billing data from GCP
        """
        try:
            if not project_id:
                project_id = self.config.project_id
            
            if not project_id:
                self.logger.error("Project ID not configured")
                return {}
            
            # Get billing account for the project
            billing_account = self._get_billing_account(project_id)
            
            if not billing_account:
                self.logger.error("No billing account found for project")
                return {}
            
            # Get cost data
            request = billing_v1.GetBillingAccountRequest(
                name=billing_account
            )
            
            billing_account_info = self.billing_client.get_billing_account(request=request)
            
            # Get cost data for the period
            # Note: This is a simplified implementation
            # In practice, you would use the Cloud Billing API to get detailed cost data
            
            return {
                'billing_account': billing_account,
                'billing_account_info': billing_account_info,
                'project_id': project_id,
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting billing data: {e}")
            return {}
    
    def get_monitoring_metrics(self,
                              resource_id: str,
                              metric_type: str,
                              start_time: datetime,
                              end_time: datetime) -> List[Dict[str, Any]]:
        """
        Get Cloud Monitoring metrics for analysis.
        
        Args:
            resource_id: Resource ID to get metrics for
            metric_type: Type of metric to retrieve
            start_time: Start time for metrics
            end_time: End time for metrics
            
        Returns:
            List of metric data points
        """
        try:
            # Construct the metric filter
            metric_filter = f'metric.type = "{metric_type}" AND resource.labels.instance_id = "{resource_id}"'
            
            # Create the time interval
            interval = monitoring_v3.TimeInterval({
                "end_time": {"seconds": int(end_time.timestamp())},
                "start_time": {"seconds": int(start_time.timestamp())}
            })
            
            # Create the request
            request = monitoring_v3.ListTimeSeriesRequest(
                name=f"projects/{self.config.project_id}",
                filter=metric_filter,
                interval=interval,
                view=monitoring_v3.ListTimeSeriesRequest.TimeSeriesView.FULL
            )
            
            # Get the time series
            time_series = self.monitoring_client.list_time_series(request=request)
            
            metrics = []
            for series in time_series:
                for point in series.points:
                    metrics.append({
                        'metric_type': metric_type,
                        'resource_id': resource_id,
                        'timestamp': point.interval.start_time.ToDatetime().isoformat(),
                        'value': point.value.double_value or point.value.int64_value or 0
                    })
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error getting monitoring metrics: {e}")
            return []
    
    def get_rightsizing_recommendations(self) -> List[Dict[str, Any]]:
        """
        Get rightsizing recommendations for GCP resources.
        
        Returns:
            List of rightsizing recommendations
        """
        try:
            recommendations = []
            
            # Get Compute Engine instances and analyze for rightsizing opportunities
            instances = self.get_compute_instances()
            
            for instance in instances:
                if instance['status'] == 'RUNNING':
                    # Get CPU and memory metrics
                    metrics = self.get_monitoring_metrics(
                        resource_id=instance['id'],
                        metric_type='compute.googleapis.com/instance/cpu/utilization',
                        start_time=datetime.now() - timedelta(days=7),
                        end_time=datetime.now()
                    )
                    
                    # Analyze metrics for rightsizing opportunities
                    cpu_usage = self._analyze_cpu_usage(metrics)
                    
                    if cpu_usage < 0.3:  # Low utilization
                        recommendations.append({
                            'resource_id': instance['id'],
                            'resource_name': instance['name'],
                            'resource_type': 'Compute Engine Instance',
                            'current_machine_type': instance['machine_type'],
                            'recommended_action': 'downsize',
                            'cpu_utilization': cpu_usage,
                            'estimated_savings': self._estimate_savings(instance['machine_type'])
                        })
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Error getting rightsizing recommendations: {e}")
            return []
    
    def get_committed_use_discount_recommendations(self) -> List[Dict[str, Any]]:
        """
        Get Committed Use Discount recommendations.
        
        Returns:
            List of Committed Use Discount recommendations
        """
        try:
            # This would use the Cloud Billing API for Committed Use Discounts
            # For now, return a placeholder
            return []
            
        except Exception as e:
            self.logger.error(f"Error getting Committed Use Discount recommendations: {e}")
            return []
    
    def _get_zones(self) -> List[str]:
        """Get list of available zones for the project."""
        try:
            # This would use the Compute Engine API to get zones
            # For now, return common zones
            return [
                "us-central1-a", "us-central1-b", "us-central1-c",
                "us-east1-b", "us-east1-c", "us-east1-d",
                "us-west1-a", "us-west1-b", "us-west1-c"
            ]
        except Exception as e:
            self.logger.error(f"Error getting zones: {e}")
            return []
    
    def _get_billing_account(self, project_id: str) -> str:
        """Get the billing account for a project."""
        try:
            # This would use the Cloud Billing API
            # For now, return a placeholder
            return f"billingAccounts/{project_id}"
        except Exception as e:
            self.logger.error(f"Error getting billing account: {e}")
            return None
    
    def _analyze_cpu_usage(self, metrics: List[Dict[str, Any]]) -> float:
        """Analyze CPU usage from metrics."""
        if not metrics:
            return 0.0
        
        values = [m['value'] for m in metrics]
        return sum(values) / len(values)
    
    def _estimate_savings(self, machine_type: str) -> float:
        """Estimate potential savings from rightsizing."""
        # This is a simplified estimation
        # In practice, you would use actual GCP pricing data
        size_mapping = {
            'n1-standard-1': 30,
            'n1-standard-2': 60,
            'n1-standard-4': 120,
            'n1-standard-8': 240,
            'n1-standard-16': 480
        }
        return size_mapping.get(machine_type, 50) 
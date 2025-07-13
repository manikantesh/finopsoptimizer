"""
Azure provider implementation for cost optimization.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from azure.identity import DefaultAzureCredential, ClientSecretCredential
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.costmanagement import CostManagementClient
from azure.mgmt.monitor import MonitorManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.sql import SqlManagementClient
from azure.core.exceptions import AzureError

from ..config import CloudConfig


class AzureProvider:
    """
    Azure provider for cost optimization operations.
    
    Handles Azure-specific cost analysis, rightsizing, and autoscaling optimization.
    """
    
    def __init__(self, config: CloudConfig):
        """
        Initialize Azure provider.
        
        Args:
            config: Azure-specific configuration
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize Azure clients
        self._initialize_clients()
        
        # Initialize analyzers
        from .cost_analyzer import AzureCostAnalyzer
        from .rightsizing import AzureRightsizingAnalyzer
        from .autoscaling import AzureAutoscalingOptimizer
        
        self.cost_analyzer = AzureCostAnalyzer(self)
        self.rightsizing_analyzer = AzureRightsizingAnalyzer(self)
        self.autoscaling_optimizer = AzureAutoscalingOptimizer(self)
    
    def _initialize_clients(self) -> None:
        """Initialize Azure service clients."""
        try:
            # Set up credentials
            if self.config.credentials_path:
                # Use service principal from file
                self.credential = ClientSecretCredential(
                    tenant_id=self.config.subscription_id,
                    client_id=os.getenv('AZURE_CLIENT_ID'),
                    client_secret=os.getenv('AZURE_CLIENT_SECRET')
                )
            else:
                # Use default credential
                self.credential = DefaultAzureCredential()
            
            # Initialize service clients
            self.compute_client = ComputeManagementClient(
                credential=self.credential,
                subscription_id=self.config.subscription_id
            )
            
            self.resource_client = ResourceManagementClient(
                credential=self.credential,
                subscription_id=self.config.subscription_id
            )
            
            self.cost_client = CostManagementClient(
                credential=self.credential,
                subscription_id=self.config.subscription_id
            )
            
            self.monitor_client = MonitorManagementClient(
                credential=self.credential,
                subscription_id=self.config.subscription_id
            )
            
            self.network_client = NetworkManagementClient(
                credential=self.credential,
                subscription_id=self.config.subscription_id
            )
            
            self.sql_client = SqlManagementClient(
                credential=self.credential,
                subscription_id=self.config.subscription_id
            )
            
            # Test connection
            self._test_connection()
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Azure clients: {e}")
            raise
    
    def _test_connection(self) -> None:
        """Test Azure connection by making a simple API call."""
        try:
            # Test with a simple API call
            self.compute_client.virtual_machines.list_all()
            self.logger.info("Azure connection test successful")
        except Exception as e:
            self.logger.error(f"Azure connection test failed: {e}")
            raise
    
    def is_connected(self) -> bool:
        """Check if Azure provider is properly connected."""
        try:
            self._test_connection()
            return True
        except:
            return False
    
    def analyze_costs(self, 
                     start_date: datetime,
                     end_date: datetime) -> Dict[str, Any]:
        """
        Analyze Azure costs for the specified period.
        
        Args:
            start_date: Start date for cost analysis
            end_date: End date for cost analysis
            
        Returns:
            Dictionary containing cost analysis results
        """
        return self.cost_analyzer.analyze_costs(start_date, end_date)
    
    def get_virtual_machines(self) -> List[Dict[str, Any]]:
        """
        Get all Virtual Machines with their details.
        
        Returns:
            List of VM details
        """
        try:
            vms = []
            
            for vm in self.compute_client.virtual_machines.list_all():
                vm_data = {
                    'id': vm.id,
                    'name': vm.name,
                    'location': vm.location,
                    'vm_size': vm.hardware_profile.vm_size if vm.hardware_profile else None,
                    'os_type': vm.storage_profile.os_disk.os_type.value if vm.storage_profile.os_disk else None,
                    'power_state': self._get_vm_power_state(vm.id),
                    'tags': vm.tags or {},
                    'resource_group': vm.id.split('/')[4]
                }
                vms.append(vm_data)
            
            return vms
            
        except AzureError as e:
            self.logger.error(f"Error getting Virtual Machines: {e}")
            return []
    
    def get_sql_databases(self) -> List[Dict[str, Any]]:
        """
        Get all SQL databases with their details.
        
        Returns:
            List of SQL database details
        """
        try:
            databases = []
            
            for server in self.sql_client.servers.list():
                for database in self.sql_client.databases.list_by_server(
                    resource_group_name=server.id.split('/')[4],
                    server_name=server.name
                ):
                    db_data = {
                        'id': database.id,
                        'name': database.name,
                        'server_name': server.name,
                        'resource_group': server.id.split('/')[4],
                        'location': database.location,
                        'sku': database.sku.name if database.sku else None,
                        'max_size_bytes': database.max_size_bytes,
                        'tags': database.tags or {}
                    }
                    databases.append(db_data)
            
            return databases
            
        except AzureError as e:
            self.logger.error(f"Error getting SQL databases: {e}")
            return []
    
    def get_virtual_machine_scale_sets(self) -> List[Dict[str, Any]]:
        """
        Get all Virtual Machine Scale Sets with their details.
        
        Returns:
            List of VMSS details
        """
        try:
            scale_sets = []
            
            for vmss in self.compute_client.virtual_machine_scale_sets.list_all():
                vmss_data = {
                    'id': vmss.id,
                    'name': vmss.name,
                    'location': vmss.location,
                    'sku': vmss.sku.name if vmss.sku else None,
                    'capacity': vmss.sku.capacity if vmss.sku else None,
                    'min_capacity': vmss.sku.capacity if vmss.sku else None,
                    'max_capacity': vmss.sku.capacity if vmss.sku else None,
                    'tags': vmss.tags or {},
                    'resource_group': vmss.id.split('/')[4]
                }
                scale_sets.append(vmss_data)
            
            return scale_sets
            
        except AzureError as e:
            self.logger.error(f"Error getting Virtual Machine Scale Sets: {e}")
            return []
    
    def get_cost_data(self,
                     start_date: datetime,
                     end_date: datetime,
                     scope: str = None) -> Dict[str, Any]:
        """
        Get cost data from Azure Cost Management.
        
        Args:
            start_date: Start date for cost data
            end_date: End date for cost data
            scope: Resource scope (subscription, resource group, etc.)
            
        Returns:
            Cost data from Azure Cost Management
        """
        try:
            if not scope:
                scope = f"/subscriptions/{self.config.subscription_id}"
            
            # Define the query
            query = {
                "type": "Usage",
                "timeframe": "Custom",
                "timePeriod": {
                    "from": start_date.isoformat(),
                    "to": end_date.isoformat()
                },
                "dataset": {
                    "granularity": "Daily",
                    "aggregation": {
                        "totalCost": {
                            "name": "Cost",
                            "function": "Sum"
                        }
                    },
                    "grouping": [
                        {
                            "type": "Dimension",
                            "column": "ResourceType"
                        }
                    ]
                }
            }
            
            # Execute the query
            result = self.cost_client.query.usage(
                scope=scope,
                parameters=query
            )
            
            return result.as_dict()
            
        except AzureError as e:
            self.logger.error(f"Error getting cost data: {e}")
            return {}
    
    def get_metrics(self,
                   resource_id: str,
                   metric_names: List[str],
                   start_time: datetime,
                   end_time: datetime,
                   interval: str = "PT1H") -> List[Dict[str, Any]]:
        """
        Get Azure Monitor metrics for analysis.
        
        Args:
            resource_id: Resource ID to get metrics for
            metric_names: List of metric names to retrieve
            start_time: Start time for metrics
            end_time: End time for metrics
            interval: Time interval for metrics
            
        Returns:
            List of metric data points
        """
        try:
            metrics = []
            
            for metric_name in metric_names:
                result = self.monitor_client.metrics.list(
                    resource_uri=resource_id,
                    timespan=f"{start_time.isoformat()}/{end_time.isoformat()}",
                    interval=interval,
                    metricnames=metric_name,
                    aggregation="Average"
                )
                
                for metric in result.value:
                    for time_series in metric.timeseries:
                        for data in time_series.data:
                            if data.average is not None:
                                metrics.append({
                                    'metric_name': metric_name,
                                    'timestamp': data.time_stamp.isoformat(),
                                    'value': data.average,
                                    'resource_id': resource_id
                                })
            
            return metrics
            
        except AzureError as e:
            self.logger.error(f"Error getting metrics: {e}")
            return []
    
    def get_rightsizing_recommendations(self) -> List[Dict[str, Any]]:
        """
        Get rightsizing recommendations for Azure resources.
        
        Returns:
            List of rightsizing recommendations
        """
        try:
            recommendations = []
            
            # Get VMs and analyze for rightsizing opportunities
            vms = self.get_virtual_machines()
            
            for vm in vms:
                if vm['power_state'] == 'running':
                    # Get CPU and memory metrics
                    metrics = self.get_metrics(
                        resource_id=vm['id'],
                        metric_names=['Percentage CPU', 'Available Memory Bytes'],
                        start_time=datetime.now() - timedelta(days=7),
                        end_time=datetime.now()
                    )
                    
                    # Analyze metrics for rightsizing opportunities
                    cpu_usage = self._analyze_cpu_usage(metrics, 'Percentage CPU')
                    memory_usage = self._analyze_memory_usage(metrics, 'Available Memory Bytes')
                    
                    if cpu_usage < 0.3 or memory_usage < 0.3:  # Low utilization
                        recommendations.append({
                            'resource_id': vm['id'],
                            'resource_name': vm['name'],
                            'resource_type': 'Virtual Machine',
                            'current_size': vm['vm_size'],
                            'recommended_action': 'downsize',
                            'cpu_utilization': cpu_usage,
                            'memory_utilization': memory_usage,
                            'estimated_savings': self._estimate_savings(vm['vm_size'])
                        })
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Error getting rightsizing recommendations: {e}")
            return []
    
    def get_reserved_instance_recommendations(self) -> List[Dict[str, Any]]:
        """
        Get Reserved Instance recommendations.
        
        Returns:
            List of Reserved Instance recommendations
        """
        try:
            # This would typically use Azure Advisor API
            # For now, return a placeholder
            return []
            
        except Exception as e:
            self.logger.error(f"Error getting Reserved Instance recommendations: {e}")
            return []
    
    def _get_vm_power_state(self, vm_id: str) -> str:
        """Get the power state of a VM."""
        try:
            vm = self.compute_client.virtual_machines.get(
                resource_group_name=vm_id.split('/')[4],
                vm_name=vm_id.split('/')[-1],
                expand='instanceView'
            )
            return vm.instance_view.statuses[-1].display_status
        except:
            return 'unknown'
    
    def _analyze_cpu_usage(self, metrics: List[Dict[str, Any]], metric_name: str) -> float:
        """Analyze CPU usage from metrics."""
        cpu_metrics = [m for m in metrics if m['metric_name'] == metric_name]
        if cpu_metrics:
            values = [m['value'] for m in cpu_metrics]
            return sum(values) / len(values) / 100  # Convert to percentage
        return 0.0
    
    def _analyze_memory_usage(self, metrics: List[Dict[str, Any]], metric_name: str) -> float:
        """Analyze memory usage from metrics."""
        memory_metrics = [m for m in metrics if m['metric_name'] == metric_name]
        if memory_metrics:
            values = [m['value'] for m in memory_metrics]
            # This is a simplified calculation - actual memory usage would need more complex logic
            return 1.0 - (sum(values) / len(values) / (1024**3))  # Convert to percentage
        return 0.0
    
    def _estimate_savings(self, vm_size: str) -> float:
        """Estimate potential savings from rightsizing."""
        # This is a simplified estimation
        # In practice, you would use actual pricing data
        size_mapping = {
            'Standard_D2s_v3': 50,
            'Standard_D4s_v3': 100,
            'Standard_D8s_v3': 200,
            'Standard_D16s_v3': 400
        }
        return size_mapping.get(vm_size, 50) 
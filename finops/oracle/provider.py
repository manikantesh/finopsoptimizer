"""
Oracle Cloud provider implementation for FinOpsOptimizer.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json

from ..config import Config


class OracleProvider:
    """
    Oracle Cloud provider implementation.
    
    Handles cost analysis, resource inventory, and optimization
    for Oracle Cloud Infrastructure (OCI).
    """
    
    def __init__(self, config: Config):
        """
        Initialize Oracle Cloud provider.
        
        Args:
            config: Configuration object
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Oracle Cloud configuration
        self.tenancy_id = config.oracle.get('tenancy_id')
        self.user_id = config.oracle.get('user_id')
        self.fingerprint = config.oracle.get('fingerprint')
        self.private_key_path = config.oracle.get('private_key_path')
        self.region = config.oracle.get('region', 'us-ashburn-1')
        
        # Initialize Oracle Cloud client
        self._initialize_client()
    
    def _initialize_client(self) -> None:
        """Initialize Oracle Cloud client."""
        try:
            import oci
            
            # Configure OCI client
            config = {
                'user': self.user_id,
                'key_file': self.private_key_path,
                'fingerprint': self.fingerprint,
                'tenancy': self.tenancy_id,
                'region': self.region
            }
            
            self.compute_client = oci.core.ComputeClient(config)
            self.blockstorage_client = oci.core.BlockstorageClient(config)
            self.network_client = oci.core.VirtualNetworkClient(config)
            self.database_client = oci.database.DatabaseClient(config)
            self.objectstorage_client = oci.object_storage.ObjectStorageClient(config)
            self.budget_client = oci.budget.BudgetClient(config)
            
            self.logger.info("Oracle Cloud client initialized successfully")
            
        except ImportError:
            self.logger.error("Oracle Cloud SDK not installed. Install with: pip install oci")
            raise
        except Exception as e:
            self.logger.error(f"Failed to initialize Oracle Cloud client: {e}")
            raise
    
    def analyze_costs(self, 
                     start_date: Optional[datetime] = None,
                     end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Analyze costs for Oracle Cloud resources.
        
        Args:
            start_date: Start date for cost analysis
            end_date: End date for cost analysis
            
        Returns:
            Dictionary containing cost analysis results
        """
        if not start_date:
            start_date = datetime.now() - timedelta(days=30)
        if not end_date:
            end_date = datetime.now()
        
        self.logger.info(f"Analyzing Oracle Cloud costs from {start_date} to {end_date}")
        
        try:
            # Get cost data from Oracle Cloud
            cost_data = self._get_cost_data(start_date, end_date)
            
            # Get resource inventory
            resources = self._get_resource_inventory()
            
            # Calculate service breakdown
            service_breakdown = self._calculate_service_breakdown(cost_data)
            
            # Calculate daily costs
            daily_costs = self._calculate_daily_costs(cost_data, start_date, end_date)
            
            total_cost = sum(item['cost'] for item in cost_data)
            
            results = {
                'total_cost': total_cost,
                'service_breakdown': service_breakdown,
                'resources': resources,
                'daily_costs': daily_costs,
                'analysis_period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat()
                }
            }
            
            self.logger.info(f"Oracle Cloud total cost: ${total_cost:.2f}")
            return results
            
        except Exception as e:
            self.logger.error(f"Error analyzing Oracle Cloud costs: {e}")
            return {'error': str(e)}
    
    def _get_cost_data(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """
        Get cost data from Oracle Cloud.
        
        Args:
            start_date: Start date
            end_date: End date
            
        Returns:
            List of cost data items
        """
        try:
            # Use Oracle Cloud Cost Management API
            # This is a simplified implementation
            # In practice, you would use the actual Oracle Cloud APIs
            
            cost_data = []
            
            # Mock cost data for demonstration
            # Replace with actual API calls
            services = ['Compute', 'Block Storage', 'Object Storage', 'Database', 'Networking']
            
            for service in services:
                for i in range((end_date - start_date).days):
                    cost_data.append({
                        'service': service,
                        'cost': 10.0 + (i * 0.5),  # Mock cost
                        'date': (start_date + timedelta(days=i)).isoformat(),
                        'region': self.region
                    })
            
            return cost_data
            
        except Exception as e:
            self.logger.error(f"Error getting Oracle Cloud cost data: {e}")
            return []
    
    def _get_resource_inventory(self) -> List[Dict[str, Any]]:
        """
        Get resource inventory from Oracle Cloud.
        
        Returns:
            List of resources
        """
        try:
            resources = []
            
            # Get compute instances
            instances = self._get_compute_instances()
            resources.extend(instances)
            
            # Get block storage volumes
            volumes = self._get_block_storage_volumes()
            resources.extend(volumes)
            
            # Get databases
            databases = self._get_databases()
            resources.extend(databases)
            
            # Get object storage buckets
            buckets = self._get_object_storage_buckets()
            resources.extend(buckets)
            
            return resources
            
        except Exception as e:
            self.logger.error(f"Error getting Oracle Cloud resource inventory: {e}")
            return []
    
    def _get_compute_instances(self) -> List[Dict[str, Any]]:
        """
        Get compute instances.
        
        Returns:
            List of compute instances
        """
        try:
            instances = []
            
            # List compute instances
            response = self.compute_client.list_instances(
                compartment_id=self.tenancy_id
            )
            
            for instance in response.data:
                # Get instance metrics for utilization
                utilization = self._get_instance_utilization(instance.id)
                
                instances.append({
                    'id': instance.id,
                    'type': 'Compute Instance',
                    'name': instance.display_name,
                    'shape': instance.shape,
                    'state': instance.lifecycle_state,
                    'region': instance.region,
                    'utilization': utilization,
                    'cost': self._estimate_instance_cost(instance),
                    'tags': self._get_instance_tags(instance)
                })
            
            return instances
            
        except Exception as e:
            self.logger.error(f"Error getting compute instances: {e}")
            return []
    
    def _get_block_storage_volumes(self) -> List[Dict[str, Any]]:
        """
        Get block storage volumes.
        
        Returns:
            List of block storage volumes
        """
        try:
            volumes = []
            
            # List block volumes
            response = self.blockstorage_client.list_volumes(
                compartment_id=self.tenancy_id
            )
            
            for volume in response.data:
                volumes.append({
                    'id': volume.id,
                    'type': 'Block Volume',
                    'name': volume.display_name,
                    'size_gb': volume.size_in_gbs,
                    'state': volume.lifecycle_state,
                    'region': volume.region,
                    'cost': self._estimate_volume_cost(volume),
                    'tags': self._get_volume_tags(volume)
                })
            
            return volumes
            
        except Exception as e:
            self.logger.error(f"Error getting block storage volumes: {e}")
            return []
    
    def _get_databases(self) -> List[Dict[str, Any]]:
        """
        Get databases.
        
        Returns:
            List of databases
        """
        try:
            databases = []
            
            # List autonomous databases
            response = self.database_client.list_autonomous_databases(
                compartment_id=self.tenancy_id
            )
            
            for db in response.data:
                databases.append({
                    'id': db.id,
                    'type': 'Autonomous Database',
                    'name': db.display_name,
                    'db_workload': db.db_workload,
                    'state': db.lifecycle_state,
                    'region': db.region,
                    'cost': self._estimate_database_cost(db),
                    'tags': self._get_database_tags(db)
                })
            
            return databases
            
        except Exception as e:
            self.logger.error(f"Error getting databases: {e}")
            return []
    
    def _get_object_storage_buckets(self) -> List[Dict[str, Any]]:
        """
        Get object storage buckets.
        
        Returns:
            List of object storage buckets
        """
        try:
            buckets = []
            
            # List object storage buckets
            response = self.objectstorage_client.list_buckets(
                namespace_name=self.tenancy_id,
                compartment_id=self.tenancy_id
            )
            
            for bucket in response.data:
                buckets.append({
                    'id': bucket.name,
                    'type': 'Object Storage Bucket',
                    'name': bucket.name,
                    'region': bucket.location,
                    'cost': self._estimate_bucket_cost(bucket),
                    'tags': self._get_bucket_tags(bucket)
                })
            
            return buckets
            
        except Exception as e:
            self.logger.error(f"Error getting object storage buckets: {e}")
            return []
    
    def _get_instance_utilization(self, instance_id: str) -> Dict[str, float]:
        """
        Get instance utilization metrics.
        
        Args:
            instance_id: Instance ID
            
        Returns:
            Dictionary with utilization metrics
        """
        try:
            # Get CPU and memory utilization
            # This would use Oracle Cloud Monitoring API
            return {
                'cpu': 0.5,  # Mock value
                'memory': 0.6,  # Mock value
                'network': 0.3  # Mock value
            }
        except Exception as e:
            self.logger.error(f"Error getting instance utilization: {e}")
            return {'cpu': 0.0, 'memory': 0.0, 'network': 0.0}
    
    def _estimate_instance_cost(self, instance) -> float:
        """
        Estimate instance cost.
        
        Args:
            instance: Instance object
            
        Returns:
            Estimated cost
        """
        # Simplified cost estimation
        # In practice, use actual pricing data
        shape_costs = {
            'VM.Standard2.1': 0.05,
            'VM.Standard2.2': 0.10,
            'VM.Standard2.4': 0.20,
            'VM.Standard2.8': 0.40,
            'VM.Standard2.16': 0.80
        }
        
        return shape_costs.get(instance.shape, 0.10) * 24 * 30  # Monthly cost
    
    def _estimate_volume_cost(self, volume) -> float:
        """
        Estimate volume cost.
        
        Args:
            volume: Volume object
            
        Returns:
            Estimated cost
        """
        # $0.025 per GB per month
        return volume.size_in_gbs * 0.025
    
    def _estimate_database_cost(self, database) -> float:
        """
        Estimate database cost.
        
        Args:
            database: Database object
            
        Returns:
            Estimated cost
        """
        # Simplified cost estimation
        return 100.0  # Mock monthly cost
    
    def _estimate_bucket_cost(self, bucket) -> float:
        """
        Estimate bucket cost.
        
        Args:
            bucket: Bucket object
            
        Returns:
            Estimated cost
        """
        # Simplified cost estimation
        return 5.0  # Mock monthly cost
    
    def _get_instance_tags(self, instance) -> Dict[str, str]:
        """Get instance tags."""
        return getattr(instance, 'freeform_tags', {})
    
    def _get_volume_tags(self, volume) -> Dict[str, str]:
        """Get volume tags."""
        return getattr(volume, 'freeform_tags', {})
    
    def _get_database_tags(self, database) -> Dict[str, str]:
        """Get database tags."""
        return getattr(database, 'freeform_tags', {})
    
    def _get_bucket_tags(self, bucket) -> Dict[str, str]:
        """Get bucket tags."""
        return getattr(bucket, 'freeform_tags', {})
    
    def _calculate_service_breakdown(self, cost_data: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Calculate service cost breakdown.
        
        Args:
            cost_data: List of cost data items
            
        Returns:
            Dictionary with service costs
        """
        breakdown = {}
        
        for item in cost_data:
            service = item['service']
            cost = item['cost']
            
            if service in breakdown:
                breakdown[service] += cost
            else:
                breakdown[service] = cost
        
        return breakdown
    
    def _calculate_daily_costs(self, 
                              cost_data: List[Dict[str, Any]],
                              start_date: datetime,
                              end_date: datetime) -> List[Dict[str, Any]]:
        """
        Calculate daily costs.
        
        Args:
            cost_data: List of cost data items
            start_date: Start date
            end_date: End date
            
        Returns:
            List of daily costs
        """
        daily_costs = {}
        
        for item in cost_data:
            date = item['date'][:10]  # Extract date part
            cost = item['cost']
            
            if date in daily_costs:
                daily_costs[date] += cost
            else:
                daily_costs[date] = cost
        
        return [
            {'date': date, 'cost': cost}
            for date, cost in sorted(daily_costs.items())
        ]
    
    def get_rightsizing_recommendations(self, resources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Get rightsizing recommendations for Oracle Cloud resources.
        
        Args:
            resources: List of resources
            
        Returns:
            List of rightsizing recommendations
        """
        recommendations = []
        
        for resource in resources:
            if resource['type'] == 'Compute Instance':
                rec = self._analyze_instance_rightsizing(resource)
                if rec:
                    recommendations.append(rec)
        
        return recommendations
    
    def _analyze_instance_rightsizing(self, instance: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Analyze instance rightsizing.
        
        Args:
            instance: Instance data
            
        Returns:
            Rightsizing recommendation or None
        """
        utilization = instance.get('utilization', {})
        cpu_util = utilization.get('cpu', 0.0)
        memory_util = utilization.get('memory', 0.0)
        
        # Check for underutilized instances
        if cpu_util < 0.3 and memory_util < 0.4:
            return {
                'type': 'rightsizing',
                'resource_id': instance['id'],
                'resource_type': 'Compute Instance',
                'description': f"Instance {instance['name']} is underutilized",
                'current_shape': instance['shape'],
                'recommended_shape': self._get_smaller_shape(instance['shape']),
                'potential_savings': self._calculate_shape_savings(instance),
                'priority': 'medium',
                'provider': 'oracle'
            }
        
        return None
    
    def _get_smaller_shape(self, current_shape: str) -> str:
        """
        Get smaller instance shape.
        
        Args:
            current_shape: Current shape
            
        Returns:
            Smaller shape
        """
        shape_downgrades = {
            'VM.Standard2.16': 'VM.Standard2.8',
            'VM.Standard2.8': 'VM.Standard2.4',
            'VM.Standard2.4': 'VM.Standard2.2',
            'VM.Standard2.2': 'VM.Standard2.1'
        }
        
        return shape_downgrades.get(current_shape, current_shape)
    
    def _calculate_shape_savings(self, instance: Dict[str, Any]) -> float:
        """
        Calculate potential savings from shape change.
        
        Args:
            instance: Instance data
            
        Returns:
            Potential savings
        """
        current_cost = instance.get('cost', 0.0)
        # Estimate 30% savings for rightsizing
        return current_cost * 0.3
    
    def get_autoscaling_recommendations(self, resources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Get autoscaling recommendations for Oracle Cloud resources.
        
        Args:
            resources: List of resources
            
        Returns:
            List of autoscaling recommendations
        """
        recommendations = []
        
        # Oracle Cloud supports Instance Pools for autoscaling
        # This would analyze current resources and recommend autoscaling groups
        
        return recommendations
    
    def validate_credentials(self) -> Dict[str, Any]:
        """
        Validate Oracle Cloud credentials.
        
        Returns:
            Validation results
        """
        try:
            # Test API access
            response = self.compute_client.list_instances(
                compartment_id=self.tenancy_id,
                limit=1
            )
            
            return {
                'valid': True,
                'message': 'Oracle Cloud credentials are valid',
                'tenancy_id': self.tenancy_id,
                'region': self.region
            }
            
        except Exception as e:
            return {
                'valid': False,
                'message': f'Invalid Oracle Cloud credentials: {e}',
                'error': str(e)
            } 
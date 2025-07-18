"""
Oracle Cloud Infrastructure (OCI) provider implementation for cost optimization.
"""

import oci
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

from ..config import CloudConfig


class OracleProvider:
    """
    Oracle Cloud Infrastructure provider for cost optimization operations.
    
    Handles OCI-specific cost analysis, rightsizing, and autoscaling optimization.
    """
    
    def __init__(self, config: CloudConfig):
        """
        Initialize Oracle Cloud provider.
        
        Args:
            config: Oracle Cloud-specific configuration
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize OCI clients
        self._initialize_clients()
        
        # Initialize analyzers
        from .cost_analyzer import OracleCostAnalyzer
        from .rightsizing import OracleRightsizingAnalyzer
        from .autoscaling import OracleAutoscalingOptimizer
        
        self.cost_analyzer = OracleCostAnalyzer(self)
        self.rightsizing_analyzer = OracleRightsizingAnalyzer(self)
        self.autoscaling_optimizer = OracleAutoscalingOptimizer(self)
    
    def _initialize_clients(self) -> None:
        """Initialize OCI service clients."""
        try:
            # Load OCI configuration
            config_file = self.config.credentials_path or "~/.oci/config"
            self.oci_config = oci.config.from_file(config_file)
            
            # Initialize service clients
            self.compute_client = oci.core.ComputeClient(self.oci_config)
            self.block_storage_client = oci.core.BlockstorageClient(self.oci_config)
            self.virtual_network_client = oci.core.VirtualNetworkClient(self.oci_config)
            self.identity_client = oci.identity.IdentityClient(self.oci_config)
            self.monitoring_client = oci.monitoring.MonitoringClient(self.oci_config)
            self.autoscaling_client = oci.autoscaling.AutoScalingClient(self.oci_config)
            
            # Usage API client for cost data
            self.usage_client = oci.usage_api.UsageapiClient(self.oci_config)
            
            # Test connection
            self._test_connection()
            
        except Exception as e:
            self.logger.error(f"Failed to initialize OCI clients: {e}")
            raise
    
    def _test_connection(self) -> None:
        """Test OCI connection by making a simple API call."""
        try:
            # Test with a simple API call
            self.identity_client.get_user(self.oci_config["user"])
            self.logger.info("Oracle Cloud connection test successful")
        except Exception as e:
            self.logger.error(f"Oracle Cloud connection test failed: {e}")
            raise
    
    def is_connected(self) -> bool:
        """Check if Oracle Cloud provider is properly connected."""
        try:
            self._test_connection()
            return True
        except:
            return False
    
    def analyze_costs(self, 
                     start_date: datetime,
                     end_date: datetime) -> Dict[str, Any]:
        """
        Analyze Oracle Cloud costs for the specified period.
        
        Args:
            start_date: Start date for cost analysis
            end_date: End date for cost analysis
            
        Returns:
            Dictionary containing cost analysis results
        """
        return self.cost_analyzer.analyze_costs(start_date, end_date)
    
    def get_compute_instances(self) -> List[Dict[str, Any]]:
        """
        Get all compute instances with their details.
        
        Returns:
            List of compute instance details
        """
        try:
            compartment_id = self.oci_config["tenancy"]
            instances = []
            
            # List all compute instances
            response = self.compute_client.list_instances(compartment_id)
            
            for instance in response.data:
                instance_details = {
                    'id': instance.id,
                    'display_name': instance.display_name,
                    'shape': instance.shape,
                    'lifecycle_state': instance.lifecycle_state,
                    'availability_domain': instance.availability_domain,
                    'compartment_id': instance.compartment_id,
                    'time_created': instance.time_created,
                    'defined_tags': instance.defined_tags,
                    'freeform_tags': instance.freeform_tags
                }
                
                # Get shape configuration if available
                if hasattr(instance, 'shape_config') and instance.shape_config:
                    instance_details['shape_config'] = {
                        'ocpus': instance.shape_config.ocpus,
                        'memory_in_gbs': instance.shape_config.memory_in_gbs
                    }
                
                instances.append(instance_details)
            
            return instances
            
        except Exception as e:
            self.logger.error(f"Error getting compute instances: {e}")
            return []
    
    def get_block_volumes(self) -> List[Dict[str, Any]]:
        """
        Get all block volumes with their details.
        
        Returns:
            List of block volume details
        """
        try:
            compartment_id = self.oci_config["tenancy"]
            volumes = []
            
            # List all block volumes
            response = self.block_storage_client.list_volumes(compartment_id)
            
            for volume in response.data:
                volumes.append({
                    'id': volume.id,
                    'display_name': volume.display_name,
                    'size_in_gbs': volume.size_in_gbs,
                    'lifecycle_state': volume.lifecycle_state,
                    'availability_domain': volume.availability_domain,
                    'compartment_id': volume.compartment_id,
                    'time_created': volume.time_created,
                    'is_encrypted': getattr(volume, 'is_encrypted', False),
                    'defined_tags': volume.defined_tags,
                    'freeform_tags': volume.freeform_tags
                })
            
            return volumes
            
        except Exception as e:
            self.logger.error(f"Error getting block volumes: {e}")
            return []
    
    def get_unattached_volumes(self) -> List[Dict[str, Any]]:
        """
        Get all unattached block volumes.
        
        Returns:
            List of unattached block volume details
        """
        try:
            all_volumes = self.get_block_volumes()
            unattached_volumes = []
            
            for volume in all_volumes:
                # Check if volume is attached to any instance
                try:
                    attachments = self.compute_client.list_volume_attachments(
                        compartment_id=volume['compartment_id'],
                        volume_id=volume['id']
                    )
                    
                    # If no active attachments, it's unattached
                    active_attachments = [
                        att for att in attachments.data 
                        if att.lifecycle_state == 'ATTACHED'
                    ]
                    
                    if not active_attachments:
                        unattached_volumes.append(volume)
                        
                except Exception as e:
                    self.logger.error(f"Error checking attachments for volume {volume['id']}: {e}")
            
            return unattached_volumes
            
        except Exception as e:
            self.logger.error(f"Error getting unattached volumes: {e}")
            return []
    
    def get_autoscaling_configurations(self) -> List[Dict[str, Any]]:
        """
        Get all autoscaling configurations.
        
        Returns:
            List of autoscaling configuration details
        """
        try:
            compartment_id = self.oci_config["tenancy"]
            configurations = []
            
            # List all autoscaling configurations
            response = self.autoscaling_client.list_auto_scaling_configurations(compartment_id)
            
            for config in response.data:
                configurations.append({
                    'id': config.id,
                    'display_name': config.display_name,
                    'compartment_id': config.compartment_id,
                    'time_created': config.time_created,
                    'is_enabled': config.is_enabled,
                    'defined_tags': config.defined_tags,
                    'freeform_tags': config.freeform_tags
                })
            
            return configurations
            
        except Exception as e:
            self.logger.error(f"Error getting autoscaling configurations: {e}")
            return []
    
    def get_cost_and_usage(self,
                          start_date: datetime,
                          end_date: datetime,
                          granularity: str = 'DAILY') -> Dict[str, Any]:
        """
        Get cost and usage data from Oracle Cloud Usage API.
        
        Args:
            start_date: Start date for cost data
            end_date: End date for cost data
            granularity: Data granularity (DAILY, MONTHLY)
            
        Returns:
            Cost and usage data
        """
        try:
            tenancy_id = self.oci_config["tenancy"]
            
            # Create usage request
            request_summarized_usages_details = oci.usage_api.models.RequestSummarizedUsagesDetails(
                tenant_id=tenancy_id,
                time_usage_started=start_date,
                time_usage_ended=end_date,
                granularity=granularity,
                group_by=['service']
            )
            
            response = self.usage_client.request_summarized_usages(
                request_summarized_usages_details
            )
            
            return {
                'items': [item.__dict__ for item in response.data.items],
                'group_by': response.data.group_by,
                'granularity': response.data.granularity
            }
            
        except Exception as e:
            self.logger.error(f"Error getting cost and usage data: {e}")
            return {}
    
    def get_monitoring_metrics(self,
                              namespace: str,
                              metric_name: str,
                              dimensions: Dict[str, str],
                              start_time: datetime,
                              end_time: datetime,
                              resolution: str = "1m") -> List[Dict[str, Any]]:
        """
        Get monitoring metrics for analysis.
        
        Args:
            namespace: Monitoring namespace
            metric_name: Name of the metric
            dimensions: Metric dimensions
            start_time: Start time for metrics
            end_time: End time for metrics
            resolution: Metric resolution
            
        Returns:
            List of metric data points
        """
        try:
            compartment_id = self.oci_config["tenancy"]
            
            # Create metric query
            query = f"{metric_name}[{resolution}]{{namespace=\"{namespace}\""
            for key, value in dimensions.items():
                query += f", {key}=\"{value}\""
            query += "}.mean()"
            
            # Summarize metrics request
            summarize_metrics_data_details = oci.monitoring.models.SummarizeMetricsDataDetails(
                namespace=namespace,
                query=query,
                start_time=start_time,
                end_time=end_time,
                resolution=resolution
            )
            
            response = self.monitoring_client.summarize_metrics_data(
                compartment_id,
                summarize_metrics_data_details
            )
            
            metrics = []
            for item in response.data:
                for datapoint in item.aggregated_datapoints:
                    metrics.append({
                        'timestamp': datapoint.timestamp,
                        'value': datapoint.value,
                        'dimensions': item.dimensions
                    })
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error getting monitoring metrics: {e}")
            return []
    
    def start_instance(self, instance_id: str) -> bool:
        """
        Start a compute instance.
        
        Args:
            instance_id: Instance ID to start
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.compute_client.instance_action(
                instance_id,
                action="START"
            )
            self.logger.info(f"Started instance {instance_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error starting instance {instance_id}: {e}")
            return False
    
    def stop_instance(self, instance_id: str) -> bool:
        """
        Stop a compute instance.
        
        Args:
            instance_id: Instance ID to stop
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.compute_client.instance_action(
                instance_id,
                action="STOP"
            )
            self.logger.info(f"Stopped instance {instance_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error stopping instance {instance_id}: {e}")
            return False
    
    def delete_volume(self, volume_id: str) -> bool:
        """
        Delete a block volume.
        
        Args:
            volume_id: Volume ID to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.block_storage_client.delete_volume(volume_id)
            self.logger.info(f"Deleted volume {volume_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error deleting volume {volume_id}: {e}")
            return False
    
    def create_volume_backup(self, volume_id: str, backup_name: str) -> Optional[str]:
        """
        Create a backup of a block volume.
        
        Args:
            volume_id: Volume ID to backup
            backup_name: Name for the backup
            
        Returns:
            Backup ID if successful, None otherwise
        """
        try:
            create_volume_backup_details = oci.core.models.CreateVolumeBackupDetails(
                volume_id=volume_id,
                display_name=backup_name,
                type="FULL"
            )
            
            response = self.block_storage_client.create_volume_backup(
                create_volume_backup_details
            )
            
            backup_id = response.data.id
            self.logger.info(f"Created backup {backup_id} for volume {volume_id}")
            return backup_id
            
        except Exception as e:
            self.logger.error(f"Error creating backup for volume {volume_id}: {e}")
            return None
    
    def get_rightsizing_recommendations(self) -> List[Dict[str, Any]]:
        """
        Get rightsizing recommendations (placeholder implementation).
        
        Returns:
            List of rightsizing recommendations
        """
        # Oracle Cloud doesn't have a built-in rightsizing API like AWS
        # This would need to be implemented using monitoring data analysis
        recommendations = []
        
        try:
            instances = self.get_compute_instances()
            
            for instance in instances:
                if instance['lifecycle_state'] == 'RUNNING':
                    # Analyze instance utilization (simplified)
                    # In a real implementation, you'd get actual metrics
                    recommendations.append({
                        'instance_id': instance['id'],
                        'current_shape': instance['shape'],
                        'recommendation_type': 'analyze_utilization',
                        'description': f'Analyze utilization for instance {instance["display_name"]}'
                    })
            
        except Exception as e:
            self.logger.error(f"Error getting rightsizing recommendations: {e}")
        
        return recommendations
    
    def get_reserved_instances(self) -> List[Dict[str, Any]]:
        """
        Get reserved instances information (placeholder implementation).
        
        Returns:
            List of reserved instances
        """
        # Oracle Cloud uses different pricing models
        # This would need to be implemented based on actual Oracle Cloud APIs
        return []
    
    def get_savings_plans(self) -> List[Dict[str, Any]]:
        """
        Get savings plans information (placeholder implementation).
        
        Returns:
            List of savings plans
        """
        # Oracle Cloud uses different pricing models
        # This would need to be implemented based on actual Oracle Cloud APIs
        return []
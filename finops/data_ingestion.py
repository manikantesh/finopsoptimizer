"""
Data ingestion pipelines for multi-cloud cost optimization.
Handles data collection from AWS, Azure, GCP, and Oracle Cloud for 365-day analysis.
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd
from dataclasses import dataclass

from .config import Config


@dataclass
class MetricsData:
    """Container for VM metrics data."""
    resource_id: str
    resource_type: str
    provider: str
    timestamp: datetime
    cpu_utilization: float
    memory_utilization: float
    network_in: float
    network_out: float
    disk_read: float
    disk_write: float
    cost: float
    tags: Dict[str, str]


class DataIngestionPipeline:
    """
    Multi-cloud data ingestion pipeline for cost optimization.
    
    Collects VM metrics, cost data, and resource inventory from all cloud providers
    for the last 365 days to enable comprehensive cost optimization analysis.
    """
    
    def __init__(self, config: Config):
        """
        Initialize data ingestion pipeline.
        
        Args:
            config: Configuration object
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.metrics_data: List[MetricsData] = []
        
        # Initialize provider clients
        self.providers = {}
        self._initialize_providers()
    
    def _initialize_providers(self) -> None:
        """Initialize cloud provider clients."""
        if self.config.aws.enabled:
            from .aws import AWSProvider
            self.providers['aws'] = AWSProvider(self.config.aws)
        
        if self.config.azure.enabled:
            from .azure import AzureProvider
            self.providers['azure'] = AzureProvider(self.config.azure)
        
        if self.config.gcp.enabled:
            from .gcp import GCPProvider
            self.providers['gcp'] = GCPProvider(self.config.gcp)
        
        if self.config.oracle.enabled:
            from .oracle import OracleProvider
            self.providers['oracle'] = OracleProvider(self.config.oracle)
    
    async def ingest_all_data(self, days: int = 365) -> Dict[str, Any]:
        """
        Ingest data from all enabled cloud providers.
        
        Args:
            days: Number of days to collect data for
            
        Returns:
            Dictionary containing all ingested data
        """
        self.logger.info(f"Starting data ingestion for {days} days across all providers")
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Collect data from all providers concurrently
        tasks = []
        for provider_name, provider in self.providers.items():
            task = self._ingest_provider_data(provider_name, provider, start_date, end_date)
            tasks.append(task)
        
        # Wait for all tasks to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Combine results
        combined_data = {
            'ingestion_summary': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'providers_processed': len(self.providers),
                'total_metrics_collected': len(self.metrics_data)
            },
            'provider_data': {}
        }
        
        for i, (provider_name, _) in enumerate(self.providers.items()):
            if isinstance(results[i], Exception):
                self.logger.error(f"Error ingesting data from {provider_name}: {results[i]}")
                combined_data['provider_data'][provider_name] = {'error': str(results[i])}
            else:
                combined_data['provider_data'][provider_name] = results[i]
        
        return combined_data
    
    async def _ingest_provider_data(self, 
                                   provider_name: str,
                                   provider,
                                   start_date: datetime,
                                   end_date: datetime) -> Dict[str, Any]:
        """
        Ingest data from a specific cloud provider.
        
        Args:
            provider_name: Name of the provider
            provider: Provider instance
            start_date: Start date for data collection
            end_date: End date for data collection
            
        Returns:
            Provider-specific data
        """
        self.logger.info(f"Ingesting data from {provider_name}")
        
        try:
            # Collect different types of data concurrently
            tasks = [
                self._collect_vm_metrics(provider_name, provider, start_date, end_date),
                self._collect_cost_data(provider_name, provider, start_date, end_date),
                self._collect_resource_inventory(provider_name, provider),
                self._collect_unattached_disks(provider_name, provider),
                self._collect_reserved_instances(provider_name, provider),
                self._collect_savings_plans(provider_name, provider)
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            return {
                'vm_metrics': results[0] if not isinstance(results[0], Exception) else [],
                'cost_data': results[1] if not isinstance(results[1], Exception) else {},
                'resource_inventory': results[2] if not isinstance(results[2], Exception) else {},
                'unattached_disks': results[3] if not isinstance(results[3], Exception) else [],
                'reserved_instances': results[4] if not isinstance(results[4], Exception) else [],
                'savings_plans': results[5] if not isinstance(results[5], Exception) else []
            }
            
        except Exception as e:
            self.logger.error(f"Error ingesting data from {provider_name}: {e}")
            raise
    
    async def _collect_vm_metrics(self,
                                 provider_name: str,
                                 provider,
                                 start_date: datetime,
                                 end_date: datetime) -> List[Dict[str, Any]]:
        """Collect VM metrics for the specified period."""
        self.logger.info(f"Collecting VM metrics from {provider_name}")
        
        metrics = []
        
        try:
            # Get all VMs/instances
            if provider_name == 'aws':
                instances = await self._get_aws_instances(provider)
                for instance in instances:
                    instance_metrics = await self._get_aws_instance_metrics(
                        provider, instance, start_date, end_date
                    )
                    metrics.extend(instance_metrics)
            
            elif provider_name == 'azure':
                vms = await self._get_azure_vms(provider)
                for vm in vms:
                    vm_metrics = await self._get_azure_vm_metrics(
                        provider, vm, start_date, end_date
                    )
                    metrics.extend(vm_metrics)
            
            elif provider_name == 'gcp':
                instances = await self._get_gcp_instances(provider)
                for instance in instances:
                    instance_metrics = await self._get_gcp_instance_metrics(
                        provider, instance, start_date, end_date
                    )
                    metrics.extend(instance_metrics)
            
            elif provider_name == 'oracle':
                instances = await self._get_oracle_instances(provider)
                for instance in instances:
                    instance_metrics = await self._get_oracle_instance_metrics(
                        provider, instance, start_date, end_date
                    )
                    metrics.extend(instance_metrics)
            
            self.logger.info(f"Collected {len(metrics)} metric data points from {provider_name}")
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error collecting VM metrics from {provider_name}: {e}")
            return []
    
    async def _collect_cost_data(self,
                                provider_name: str,
                                provider,
                                start_date: datetime,
                                end_date: datetime) -> Dict[str, Any]:
        """Collect cost data for the specified period."""
        self.logger.info(f"Collecting cost data from {provider_name}")
        
        try:
            if hasattr(provider, 'get_cost_and_usage'):
                cost_data = provider.get_cost_and_usage(start_date, end_date)
                return cost_data
            else:
                return {}
        except Exception as e:
            self.logger.error(f"Error collecting cost data from {provider_name}: {e}")
            return {}
    
    async def _collect_resource_inventory(self,
                                         provider_name: str,
                                         provider) -> Dict[str, Any]:
        """Collect resource inventory."""
        self.logger.info(f"Collecting resource inventory from {provider_name}")
        
        try:
            inventory = {}
            
            if hasattr(provider, 'get_ec2_instances'):
                inventory['ec2_instances'] = provider.get_ec2_instances()
            if hasattr(provider, 'get_rds_instances'):
                inventory['rds_instances'] = provider.get_rds_instances()
            if hasattr(provider, 'get_virtual_machines'):
                inventory['virtual_machines'] = provider.get_virtual_machines()
            if hasattr(provider, 'get_compute_instances'):
                inventory['compute_instances'] = provider.get_compute_instances()
            
            return inventory
            
        except Exception as e:
            self.logger.error(f"Error collecting resource inventory from {provider_name}: {e}")
            return {}
    
    async def _collect_unattached_disks(self,
                                       provider_name: str,
                                       provider) -> List[Dict[str, Any]]:
        """Collect unattached disk information."""
        self.logger.info(f"Collecting unattached disks from {provider_name}")
        
        try:
            if hasattr(provider, 'get_unattached_volumes'):
                return provider.get_unattached_volumes()
            else:
                return []
        except Exception as e:
            self.logger.error(f"Error collecting unattached disks from {provider_name}: {e}")
            return []
    
    async def _collect_reserved_instances(self,
                                         provider_name: str,
                                         provider) -> List[Dict[str, Any]]:
        """Collect reserved instance information."""
        self.logger.info(f"Collecting reserved instances from {provider_name}")
        
        try:
            if hasattr(provider, 'get_reserved_instances'):
                return provider.get_reserved_instances()
            else:
                return []
        except Exception as e:
            self.logger.error(f"Error collecting reserved instances from {provider_name}: {e}")
            return []
    
    async def _collect_savings_plans(self,
                                    provider_name: str,
                                    provider) -> List[Dict[str, Any]]:
        """Collect savings plans information."""
        self.logger.info(f"Collecting savings plans from {provider_name}")
        
        try:
            if hasattr(provider, 'get_savings_plans'):
                return provider.get_savings_plans()
            else:
                return []
        except Exception as e:
            self.logger.error(f"Error collecting savings plans from {provider_name}: {e}")
            return []
    
    # Provider-specific methods for getting instances and metrics
    async def _get_aws_instances(self, provider) -> List[Dict[str, Any]]:
        """Get AWS EC2 instances."""
        return provider.get_ec2_instances()
    
    async def _get_aws_instance_metrics(self,
                                       provider,
                                       instance: Dict[str, Any],
                                       start_date: datetime,
                                       end_date: datetime) -> List[Dict[str, Any]]:
        """Get metrics for an AWS EC2 instance."""
        instance_id = instance['instance_id']
        metrics = []
        
        # Get CloudWatch metrics
        metric_names = ['CPUUtilization', 'NetworkIn', 'NetworkOut', 'DiskReadBytes', 'DiskWriteBytes']
        
        for metric_name in metric_names:
            dimensions = [{'Name': 'InstanceId', 'Value': instance_id}]
            datapoints = provider.get_cloudwatch_metrics(
                'AWS/EC2', metric_name, dimensions, start_date, end_date
            )
            
            for datapoint in datapoints:
                metrics.append({
                    'resource_id': instance_id,
                    'resource_type': 'ec2_instance',
                    'provider': 'aws',
                    'timestamp': datapoint['Timestamp'],
                    'metric_name': metric_name,
                    'value': datapoint.get('Average', 0),
                    'unit': datapoint.get('Unit', ''),
                    'tags': {tag['Key']: tag['Value'] for tag in instance.get('tags', [])}
                })
        
        return metrics
    
    async def _get_azure_vms(self, provider) -> List[Dict[str, Any]]:
        """Get Azure virtual machines."""
        if hasattr(provider, 'get_virtual_machines'):
            return provider.get_virtual_machines()
        return []
    
    async def _get_azure_vm_metrics(self,
                                   provider,
                                   vm: Dict[str, Any],
                                   start_date: datetime,
                                   end_date: datetime) -> List[Dict[str, Any]]:
        """Get metrics for an Azure VM."""
        # This would implement Azure Monitor metrics collection
        # Placeholder implementation
        return []
    
    async def _get_gcp_instances(self, provider) -> List[Dict[str, Any]]:
        """Get GCP Compute Engine instances."""
        if hasattr(provider, 'get_compute_instances'):
            return provider.get_compute_instances()
        return []
    
    async def _get_gcp_instance_metrics(self,
                                       provider,
                                       instance: Dict[str, Any],
                                       start_date: datetime,
                                       end_date: datetime) -> List[Dict[str, Any]]:
        """Get metrics for a GCP Compute Engine instance."""
        # This would implement Google Cloud Monitoring metrics collection
        # Placeholder implementation
        return []
    
    async def _get_oracle_instances(self, provider) -> List[Dict[str, Any]]:
        """Get Oracle Cloud instances."""
        if hasattr(provider, 'get_compute_instances'):
            return provider.get_compute_instances()
        return []
    
    async def _get_oracle_instance_metrics(self,
                                          provider,
                                          instance: Dict[str, Any],
                                          start_date: datetime,
                                          end_date: datetime) -> List[Dict[str, Any]]:
        """Get metrics for an Oracle Cloud instance."""
        # This would implement Oracle Cloud Monitoring metrics collection
        # Placeholder implementation
        return []
    
    def export_metrics_to_dataframe(self) -> pd.DataFrame:
        """Export collected metrics to pandas DataFrame for analysis."""
        if not self.metrics_data:
            return pd.DataFrame()
        
        data = []
        for metric in self.metrics_data:
            data.append({
                'resource_id': metric.resource_id,
                'resource_type': metric.resource_type,
                'provider': metric.provider,
                'timestamp': metric.timestamp,
                'cpu_utilization': metric.cpu_utilization,
                'memory_utilization': metric.memory_utilization,
                'network_in': metric.network_in,
                'network_out': metric.network_out,
                'disk_read': metric.disk_read,
                'disk_write': metric.disk_write,
                'cost': metric.cost,
                'tags': str(metric.tags)
            })
        
        return pd.DataFrame(data)
    
    def save_data_to_file(self, data: Dict[str, Any], filename: str) -> None:
        """Save ingested data to file."""
        import json
        from pathlib import Path
        
        output_dir = Path(self.config.output_dir)
        output_dir.mkdir(exist_ok=True)
        
        filepath = output_dir / filename
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        
        self.logger.info(f"Data saved to {filepath}")
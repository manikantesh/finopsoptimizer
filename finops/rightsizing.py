"""
Rightsizing analyzer for FinOpsOptimizer.
Handles rightsizing recommendations across AWS, Azure, and GCP.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict

from .config import Config


class RightsizingAnalyzer:
    """
    Rightsizing analyzer for multi-cloud environments.
    
    Provides rightsizing recommendations across AWS, Azure, and GCP
    based on resource utilization and cost analysis.
    """
    
    def __init__(self, config: Config):
        """
        Initialize Rightsizing Analyzer.
        
        Args:
            config: Configuration object
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Thresholds from config
        self.cpu_threshold = config.optimization.cpu_utilization_threshold
        self.memory_threshold = config.optimization.memory_utilization_threshold
        self.cost_savings_threshold = config.optimization.cost_savings_threshold
    
    def analyze_provider(self, 
                        provider,
                        cost_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Analyze rightsizing opportunities for a specific provider.
        
        Args:
            provider: Cloud provider instance
            cost_data: Cost data for the provider
            
        Returns:
            List of rightsizing recommendations
        """
        self.logger.info(f"Analyzing rightsizing opportunities for {provider.__class__.__name__}")
        
        recommendations = []
        
        try:
            # Get provider-specific rightsizing recommendations
            if hasattr(provider, 'get_rightsizing_recommendations'):
                provider_recs = provider.get_rightsizing_recommendations()
                recommendations.extend(provider_recs)
            
            # Analyze based on cost data
            cost_based_recs = self._analyze_cost_based_rightsizing(cost_data)
            recommendations.extend(cost_based_recs)
            
            # Analyze based on resource inventory
            inventory_recs = self._analyze_inventory_based_rightsizing(provider, cost_data)
            recommendations.extend(inventory_recs)
            
            # Filter recommendations based on thresholds
            filtered_recs = self._filter_recommendations(recommendations)
            
            return filtered_recs
            
        except Exception as e:
            self.logger.error(f"Error analyzing rightsizing for provider: {e}")
            return []
    
    def _analyze_cost_based_rightsizing(self, cost_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Analyze rightsizing opportunities based on cost data.
        
        Args:
            cost_data: Cost data for the provider
            
        Returns:
            List of cost-based rightsizing recommendations
        """
        recommendations = []
        
        # Analyze instance costs
        if 'instance_breakdown' in cost_data:
            instance_breakdown = cost_data['instance_breakdown']
            instances = instance_breakdown.get('instances', {})
            
            for instance_id, instance_data in instances.items():
                cost = instance_data.get('cost', 0)
                instance_type = instance_data.get('instance_type', 'unknown')
                state = instance_data.get('state', 'unknown')
                
                # Check for stopped instances
                if state == 'stopped' and cost > 0:
                    recommendations.append({
                        'resource_id': instance_id,
                        'resource_type': 'instance',
                        'recommendation_type': 'terminate_stopped',
                        'current_state': state,
                        'current_cost': cost,
                        'recommended_action': 'terminate',
                        'potential_savings': cost,
                        'priority': 'high',
                        'description': f'Stopped instance {instance_id} is still incurring costs'
                    })
                
                # Check for expensive instance types
                expensive_rec = self._check_expensive_instance_types(instance_id, instance_type, cost)
                if expensive_rec:
                    recommendations.append(expensive_rec)
        
        # Analyze storage costs
        if 'storage_breakdown' in cost_data:
            storage_recs = self._analyze_storage_rightsizing(cost_data['storage_breakdown'])
            recommendations.extend(storage_recs)
        
        return recommendations
    
    def _analyze_inventory_based_rightsizing(self, 
                                           provider,
                                           cost_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Analyze rightsizing opportunities based on resource inventory.
        
        Args:
            provider: Cloud provider instance
            cost_data: Cost data for the provider
            
        Returns:
            List of inventory-based rightsizing recommendations
        """
        recommendations = []
        
        try:
            # Get resource inventory
            if hasattr(provider, 'get_ec2_instances'):
                instances = provider.get_ec2_instances()
                for instance in instances:
                    rec = self._analyze_instance_rightsizing(instance)
                    if rec:
                        recommendations.append(rec)
            
            if hasattr(provider, 'get_virtual_machines'):
                vms = provider.get_virtual_machines()
                for vm in vms:
                    rec = self._analyze_vm_rightsizing(vm)
                    if rec:
                        recommendations.append(rec)
            
            if hasattr(provider, 'get_compute_instances'):
                compute_instances = provider.get_compute_instances()
                for instance in compute_instances:
                    rec = self._analyze_compute_instance_rightsizing(instance)
                    if rec:
                        recommendations.append(rec)
            
        except Exception as e:
            self.logger.error(f"Error analyzing inventory-based rightsizing: {e}")
        
        return recommendations
    
    def _analyze_instance_rightsizing(self, instance: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Analyze rightsizing for an EC2 instance.
        
        Args:
            instance: EC2 instance data
            
        Returns:
            Rightsizing recommendation or None
        """
        instance_type = instance.get('instance_type', '')
        state = instance.get('state', '')
        
        # Check for oversized instances
        oversized_types = self._get_oversized_instance_types()
        if instance_type in oversized_types and state == 'running':
            return {
                'resource_id': instance.get('instance_id', ''),
                'resource_type': 'ec2_instance',
                'recommendation_type': 'downsize',
                'current_size': instance_type,
                'recommended_size': self._get_recommended_size(instance_type),
                'potential_savings': self._estimate_instance_savings(instance_type),
                'priority': 'medium',
                'description': f'Consider downsizing {instance_type} instance'
            }
        
        return None
    
    def _analyze_vm_rightsizing(self, vm: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Analyze rightsizing for an Azure VM.
        
        Args:
            vm: Azure VM data
            
        Returns:
            Rightsizing recommendation or None
        """
        vm_size = vm.get('vm_size', '')
        power_state = vm.get('power_state', '')
        
        # Check for oversized VMs
        oversized_sizes = self._get_oversized_vm_sizes()
        if vm_size in oversized_sizes and power_state == 'VM running':
            return {
                'resource_id': vm.get('id', ''),
                'resource_type': 'azure_vm',
                'recommendation_type': 'downsize',
                'current_size': vm_size,
                'recommended_size': self._get_recommended_vm_size(vm_size),
                'potential_savings': self._estimate_vm_savings(vm_size),
                'priority': 'medium',
                'description': f'Consider downsizing {vm_size} VM'
            }
        
        return None
    
    def _analyze_compute_instance_rightsizing(self, instance: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Analyze rightsizing for a GCP Compute Engine instance.
        
        Args:
            instance: GCP instance data
            
        Returns:
            Rightsizing recommendation or None
        """
        machine_type = instance.get('machine_type', '')
        status = instance.get('status', '')
        
        # Check for oversized instances
        oversized_types = self._get_oversized_gcp_types()
        if machine_type in oversized_types and status == 'RUNNING':
            return {
                'resource_id': instance.get('id', ''),
                'resource_type': 'gcp_instance',
                'recommendation_type': 'downsize',
                'current_size': machine_type,
                'recommended_size': self._get_recommended_gcp_size(machine_type),
                'potential_savings': self._estimate_gcp_savings(machine_type),
                'priority': 'medium',
                'description': f'Consider downsizing {machine_type} instance'
            }
        
        return None
    
    def _analyze_storage_rightsizing(self, storage_breakdown: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Analyze storage rightsizing opportunities.
        
        Args:
            storage_breakdown: Storage cost breakdown
            
        Returns:
            List of storage rightsizing recommendations
        """
        recommendations = []
        
        # Check for unused storage
        for storage_type, cost in storage_breakdown.items():
            if storage_type != 'total_storage_cost' and cost > 0:
                # This is a simplified check - in practice, you'd analyze actual usage
                if cost > 100:  # High storage cost threshold
                    recommendations.append({
                        'resource_type': 'storage',
                        'storage_type': storage_type,
                        'recommendation_type': 'storage_optimization',
                        'current_cost': cost,
                        'potential_savings': cost * 0.3,  # Estimate 30% savings
                        'priority': 'low',
                        'description': f'Review {storage_type} storage usage and costs'
                    })
        
        return recommendations
    
    def _check_expensive_instance_types(self, 
                                      instance_id: str,
                                      instance_type: str,
                                      cost: float) -> Optional[Dict[str, Any]]:
        """
        Check for expensive instance types that could be optimized.
        
        Args:
            instance_id: Instance ID
            instance_type: Instance type
            cost: Current cost
            
        Returns:
            Recommendation or None
        """
        expensive_types = self._get_expensive_instance_types()
        
        if instance_type in expensive_types and cost > 100:  # High cost threshold
            return {
                'resource_id': instance_id,
                'resource_type': 'instance',
                'recommendation_type': 'expensive_instance',
                'current_type': instance_type,
                'current_cost': cost,
                'recommended_action': 'review_usage',
                'potential_savings': cost * 0.2,  # Estimate 20% savings
                'priority': 'medium',
                'description': f'Review usage of expensive {instance_type} instance'
            }
        
        return None
    
    def _filter_recommendations(self, recommendations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filter recommendations based on thresholds and priorities.
        
        Args:
            recommendations: List of all recommendations
            
        Returns:
            Filtered list of recommendations
        """
        filtered = []
        
        for rec in recommendations:
            potential_savings = rec.get('potential_savings', 0)
            
            # Filter by savings threshold
            if potential_savings >= self.cost_savings_threshold:
                filtered.append(rec)
        
        # Sort by potential savings (highest first)
        filtered.sort(key=lambda x: x.get('potential_savings', 0), reverse=True)
        
        return filtered
    
    def _get_oversized_instance_types(self) -> List[str]:
        """Get list of potentially oversized EC2 instance types."""
        return [
            'm5.2xlarge', 'm5.4xlarge', 'm5.8xlarge', 'm5.16xlarge',
            'c5.2xlarge', 'c5.4xlarge', 'c5.8xlarge', 'c5.16xlarge',
            'r5.2xlarge', 'r5.4xlarge', 'r5.8xlarge', 'r5.16xlarge'
        ]
    
    def _get_oversized_vm_sizes(self) -> List[str]:
        """Get list of potentially oversized Azure VM sizes."""
        return [
            'Standard_D4s_v3', 'Standard_D8s_v3', 'Standard_D16s_v3',
            'Standard_E4s_v3', 'Standard_E8s_v3', 'Standard_E16s_v3',
            'Standard_F8s_v2', 'Standard_F16s_v2'
        ]
    
    def _get_oversized_gcp_types(self) -> List[str]:
        """Get list of potentially oversized GCP machine types."""
        return [
            'n1-standard-4', 'n1-standard-8', 'n1-standard-16',
            'n1-highmem-4', 'n1-highmem-8', 'n1-highmem-16',
            'n1-highcpu-4', 'n1-highcpu-8', 'n1-highcpu-16'
        ]
    
    def _get_expensive_instance_types(self) -> List[str]:
        """Get list of expensive instance types."""
        return [
            'm5.16xlarge', 'c5.16xlarge', 'r5.16xlarge',
            'p3.2xlarge', 'p3.8xlarge', 'p3.16xlarge',
            'g4dn.xlarge', 'g4dn.2xlarge', 'g4dn.4xlarge'
        ]
    
    def _get_recommended_size(self, current_size: str) -> str:
        """Get recommended size for an EC2 instance type."""
        size_mapping = {
            'm5.2xlarge': 'm5.xlarge',
            'm5.4xlarge': 'm5.2xlarge',
            'm5.8xlarge': 'm5.4xlarge',
            'm5.16xlarge': 'm5.8xlarge',
            'c5.2xlarge': 'c5.xlarge',
            'c5.4xlarge': 'c5.2xlarge',
            'c5.8xlarge': 'c5.4xlarge',
            'c5.16xlarge': 'c5.8xlarge'
        }
        return size_mapping.get(current_size, 'review_required')
    
    def _get_recommended_vm_size(self, current_size: str) -> str:
        """Get recommended size for an Azure VM."""
        size_mapping = {
            'Standard_D4s_v3': 'Standard_D2s_v3',
            'Standard_D8s_v3': 'Standard_D4s_v3',
            'Standard_D16s_v3': 'Standard_D8s_v3',
            'Standard_E4s_v3': 'Standard_E2s_v3',
            'Standard_E8s_v3': 'Standard_E4s_v3',
            'Standard_E16s_v3': 'Standard_E8s_v3'
        }
        return size_mapping.get(current_size, 'review_required')
    
    def _get_recommended_gcp_size(self, current_size: str) -> str:
        """Get recommended size for a GCP instance."""
        size_mapping = {
            'n1-standard-4': 'n1-standard-2',
            'n1-standard-8': 'n1-standard-4',
            'n1-standard-16': 'n1-standard-8',
            'n1-highmem-4': 'n1-highmem-2',
            'n1-highmem-8': 'n1-highmem-4',
            'n1-highmem-16': 'n1-highmem-8'
        }
        return size_mapping.get(current_size, 'review_required')
    
    def _estimate_instance_savings(self, instance_type: str) -> float:
        """Estimate potential savings for EC2 instance rightsizing."""
        savings_mapping = {
            'm5.2xlarge': 50,
            'm5.4xlarge': 100,
            'm5.8xlarge': 200,
            'm5.16xlarge': 400,
            'c5.2xlarge': 60,
            'c5.4xlarge': 120,
            'c5.8xlarge': 240,
            'c5.16xlarge': 480
        }
        return savings_mapping.get(instance_type, 50)
    
    def _estimate_vm_savings(self, vm_size: str) -> float:
        """Estimate potential savings for Azure VM rightsizing."""
        savings_mapping = {
            'Standard_D4s_v3': 40,
            'Standard_D8s_v3': 80,
            'Standard_D16s_v3': 160,
            'Standard_E4s_v3': 50,
            'Standard_E8s_v3': 100,
            'Standard_E16s_v3': 200
        }
        return savings_mapping.get(vm_size, 50)
    
    def _estimate_gcp_savings(self, machine_type: str) -> float:
        """Estimate potential savings for GCP instance rightsizing."""
        savings_mapping = {
            'n1-standard-4': 40,
            'n1-standard-8': 80,
            'n1-standard-16': 160,
            'n1-highmem-4': 50,
            'n1-highmem-8': 100,
            'n1-highmem-16': 200
        }
        return savings_mapping.get(machine_type, 50) 
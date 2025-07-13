"""
Autoscaling optimizer for FinOpsOptimizer.
Handles autoscaling optimization across AWS, Azure, and GCP.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict

from .config import Config


class AutoscalingOptimizer:
    """
    Autoscaling optimizer for multi-cloud environments.
    
    Provides autoscaling optimization recommendations across AWS, Azure, and GCP
    based on usage patterns and cost analysis.
    """
    
    def __init__(self, config: Config):
        """
        Initialize Autoscaling Optimizer.
        
        Args:
            config: Configuration object
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Autoscaling parameters from config
        self.min_instances = config.optimization.min_instances
        self.max_instances = config.optimization.max_instances
        self.scale_up_threshold = config.optimization.scale_up_threshold
        self.scale_down_threshold = config.optimization.scale_down_threshold
    
    def analyze_provider(self, 
                        provider,
                        cost_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Analyze autoscaling opportunities for a specific provider.
        
        Args:
            provider: Cloud provider instance
            cost_data: Cost data for the provider
            
        Returns:
            List of autoscaling optimization recommendations
        """
        self.logger.info(f"Analyzing autoscaling opportunities for {provider.__class__.__name__}")
        
        recommendations = []
        
        try:
            # Get provider-specific autoscaling groups
            if hasattr(provider, 'get_autoscaling_groups'):
                asg_recs = self._analyze_autoscaling_groups(provider)
                recommendations.extend(asg_recs)
            
            if hasattr(provider, 'get_virtual_machine_scale_sets'):
                vmss_recs = self._analyze_vm_scale_sets(provider)
                recommendations.extend(vmss_recs)
            
            if hasattr(provider, 'get_instance_groups'):
                ig_recs = self._analyze_instance_groups(provider)
                recommendations.extend(ig_recs)
            
            # Analyze based on cost data
            cost_based_recs = self._analyze_cost_based_autoscaling(cost_data)
            recommendations.extend(cost_based_recs)
            
            # Filter recommendations
            filtered_recs = self._filter_autoscaling_recommendations(recommendations)
            
            return filtered_recs
            
        except Exception as e:
            self.logger.error(f"Error analyzing autoscaling for provider: {e}")
            return []
    
    def _analyze_autoscaling_groups(self, provider) -> List[Dict[str, Any]]:
        """
        Analyze AWS Auto Scaling groups.
        
        Args:
            provider: AWS provider instance
            
        Returns:
            List of autoscaling recommendations
        """
        recommendations = []
        
        try:
            autoscaling_groups = provider.get_autoscaling_groups()
            
            for asg in autoscaling_groups:
                asg_name = asg.get('auto_scaling_group_name', '')
                min_size = asg.get('min_size', 0)
                max_size = asg.get('max_size', 0)
                desired_capacity = asg.get('desired_capacity', 0)
                instances = asg.get('instances', [])
                
                # Check for optimization opportunities
                rec = self._analyze_single_autoscaling_group(
                    asg_name, min_size, max_size, desired_capacity, len(instances)
                )
                if rec:
                    recommendations.append(rec)
                
                # Check for cost optimization
                cost_rec = self._analyze_autoscaling_cost_optimization(asg)
                if cost_rec:
                    recommendations.append(cost_rec)
                    
        except Exception as e:
            self.logger.error(f"Error analyzing Auto Scaling groups: {e}")
        
        return recommendations
    
    def _analyze_vm_scale_sets(self, provider) -> List[Dict[str, Any]]:
        """
        Analyze Azure Virtual Machine Scale Sets.
        
        Args:
            provider: Azure provider instance
            
        Returns:
            List of autoscaling recommendations
        """
        recommendations = []
        
        try:
            scale_sets = provider.get_virtual_machine_scale_sets()
            
            for vmss in scale_sets:
                vmss_name = vmss.get('name', '')
                min_capacity = vmss.get('min_capacity', 0)
                max_capacity = vmss.get('max_capacity', 0)
                capacity = vmss.get('capacity', 0)
                
                # Check for optimization opportunities
                rec = self._analyze_single_vm_scale_set(
                    vmss_name, min_capacity, max_capacity, capacity
                )
                if rec:
                    recommendations.append(rec)
                    
        except Exception as e:
            self.logger.error(f"Error analyzing VM Scale Sets: {e}")
        
        return recommendations
    
    def _analyze_instance_groups(self, provider) -> List[Dict[str, Any]]:
        """
        Analyze GCP Instance Groups.
        
        Args:
            provider: GCP provider instance
            
        Returns:
            List of autoscaling recommendations
        """
        recommendations = []
        
        try:
            instance_groups = provider.get_instance_groups()
            
            for ig in instance_groups:
                ig_name = ig.get('name', '')
                # GCP instance groups have different structure
                # This would need to be implemented based on actual GCP API response
                
        except Exception as e:
            self.logger.error(f"Error analyzing Instance Groups: {e}")
        
        return recommendations
    
    def _analyze_single_autoscaling_group(self,
                                         asg_name: str,
                                         min_size: int,
                                         max_size: int,
                                         desired_capacity: int,
                                         current_instances: int) -> Optional[Dict[str, Any]]:
        """
        Analyze a single Auto Scaling group for optimization opportunities.
        
        Args:
            asg_name: Name of the Auto Scaling group
            min_size: Minimum size
            max_size: Maximum size
            desired_capacity: Desired capacity
            current_instances: Current number of instances
            
        Returns:
            Recommendation or None
        """
        recommendations = []
        
        # Check for oversized max capacity
        if max_size > self.max_instances:
            recommendations.append({
                'resource_id': asg_name,
                'resource_type': 'autoscaling_group',
                'recommendation_type': 'reduce_max_capacity',
                'current_max': max_size,
                'recommended_max': self.max_instances,
                'potential_savings': self._estimate_max_capacity_savings(max_size),
                'priority': 'medium',
                'description': f'Consider reducing max capacity from {max_size} to {self.max_instances}'
            })
        
        # Check for underutilized min capacity
        if min_size > 1 and current_instances < min_size:
            recommendations.append({
                'resource_id': asg_name,
                'resource_type': 'autoscaling_group',
                'recommendation_type': 'reduce_min_capacity',
                'current_min': min_size,
                'recommended_min': 1,
                'potential_savings': self._estimate_min_capacity_savings(min_size),
                'priority': 'low',
                'description': f'Consider reducing min capacity from {min_size} to 1'
            })
        
        # Check for idle autoscaling groups
        if current_instances == 0 and desired_capacity > 0:
            recommendations.append({
                'resource_id': asg_name,
                'resource_type': 'autoscaling_group',
                'recommendation_type': 'idle_autoscaling_group',
                'current_instances': current_instances,
                'desired_capacity': desired_capacity,
                'recommended_action': 'review_and_terminate_if_unused',
                'potential_savings': self._estimate_idle_asg_savings(),
                'priority': 'high',
                'description': f'Auto Scaling group {asg_name} has 0 instances but desired capacity > 0'
            })
        
        return recommendations[0] if recommendations else None
    
    def _analyze_single_vm_scale_set(self,
                                     vmss_name: str,
                                     min_capacity: int,
                                     max_capacity: int,
                                     capacity: int) -> Optional[Dict[str, Any]]:
        """
        Analyze a single VM Scale Set for optimization opportunities.
        
        Args:
            vmss_name: Name of the VM Scale Set
            min_capacity: Minimum capacity
            max_capacity: Maximum capacity
            capacity: Current capacity
            
        Returns:
            Recommendation or None
        """
        recommendations = []
        
        # Check for oversized max capacity
        if max_capacity > self.max_instances:
            recommendations.append({
                'resource_id': vmss_name,
                'resource_type': 'vm_scale_set',
                'recommendation_type': 'reduce_max_capacity',
                'current_max': max_capacity,
                'recommended_max': self.max_instances,
                'potential_savings': self._estimate_max_capacity_savings(max_capacity),
                'priority': 'medium',
                'description': f'Consider reducing max capacity from {max_capacity} to {self.max_instances}'
            })
        
        # Check for underutilized min capacity
        if min_capacity > 1 and capacity < min_capacity:
            recommendations.append({
                'resource_id': vmss_name,
                'resource_type': 'vm_scale_set',
                'recommendation_type': 'reduce_min_capacity',
                'current_min': min_capacity,
                'recommended_min': 1,
                'potential_savings': self._estimate_min_capacity_savings(min_capacity),
                'priority': 'low',
                'description': f'Consider reducing min capacity from {min_capacity} to 1'
            })
        
        return recommendations[0] if recommendations else None
    
    def _analyze_autoscaling_cost_optimization(self, asg: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Analyze cost optimization opportunities for Auto Scaling groups.
        
        Args:
            asg: Auto Scaling group data
            
        Returns:
            Cost optimization recommendation or None
        """
        asg_name = asg.get('auto_scaling_group_name', '')
        instances = asg.get('instances', [])
        
        # Check for cost optimization opportunities
        if len(instances) > 0:
            # This would analyze instance types and recommend cost optimizations
            return {
                'resource_id': asg_name,
                'resource_type': 'autoscaling_group',
                'recommendation_type': 'cost_optimization',
                'current_instances': len(instances),
                'recommended_action': 'review_instance_types',
                'potential_savings': self._estimate_asg_cost_savings(len(instances)),
                'priority': 'medium',
                'description': f'Review instance types in Auto Scaling group {asg_name} for cost optimization'
            }
        
        return None
    
    def _analyze_cost_based_autoscaling(self, cost_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Analyze autoscaling opportunities based on cost data.
        
        Args:
            cost_data: Cost data for the provider
            
        Returns:
            List of cost-based autoscaling recommendations
        """
        recommendations = []
        
        # Analyze cost patterns that might indicate autoscaling opportunities
        if 'cost_trends' in cost_data:
            trends = cost_data['cost_trends']
            
            # Check for cost spikes that might indicate scaling issues
            if 'cost_variance' in trends:
                variance = trends['cost_variance']
                if variance > 1000:  # High cost variance threshold
                    recommendations.append({
                        'resource_type': 'autoscaling',
                        'recommendation_type': 'cost_variance',
                        'current_variance': variance,
                        'recommended_action': 'review_scaling_policies',
                        'potential_savings': variance * 0.2,  # Estimate 20% savings
                        'priority': 'medium',
                        'description': 'High cost variance detected - review autoscaling policies'
                    })
        
        return recommendations
    
    def _filter_autoscaling_recommendations(self, recommendations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filter autoscaling recommendations based on thresholds and priorities.
        
        Args:
            recommendations: List of all recommendations
            
        Returns:
            Filtered list of recommendations
        """
        filtered = []
        
        for rec in recommendations:
            potential_savings = rec.get('potential_savings', 0)
            
            # Filter by savings threshold
            if potential_savings >= self.config.optimization.cost_savings_threshold:
                filtered.append(rec)
        
        # Sort by potential savings (highest first)
        filtered.sort(key=lambda x: x.get('potential_savings', 0), reverse=True)
        
        return filtered
    
    def _estimate_max_capacity_savings(self, current_max: int) -> float:
        """Estimate potential savings from reducing max capacity."""
        # This is a simplified estimation
        # In practice, you would use actual pricing data
        return (current_max - self.max_instances) * 50  # $50 per instance per month
    
    def _estimate_min_capacity_savings(self, current_min: int) -> float:
        """Estimate potential savings from reducing min capacity."""
        # This is a simplified estimation
        return (current_min - 1) * 100  # $100 per instance per month
    
    def _estimate_idle_asg_savings(self) -> float:
        """Estimate potential savings from terminating idle Auto Scaling groups."""
        # This is a simplified estimation
        return 200  # $200 per month for idle ASG
    
    def _estimate_asg_cost_savings(self, instance_count: int) -> float:
        """Estimate potential savings from ASG cost optimization."""
        # This is a simplified estimation
        return instance_count * 30  # $30 per instance per month 
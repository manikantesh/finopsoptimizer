"""
Cost Allocation module for FinOpsOptimizer.
Handles cost allocation across AWS, Azure, and GCP.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import pandas as pd

from .config import Config


class CostAllocator:
    """
    Cost allocation analyzer for multi-cloud environments.
    
    Provides cost allocation capabilities across AWS, Azure, and GCP
    based on various allocation methods and rules.
    """
    
    def __init__(self, config: Config):
        """
        Initialize Cost Allocator.
        
        Args:
            config: Configuration object
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def allocate_costs(self, 
                      cost_data: Dict[str, Any],
                      allocation_rules: Dict[str, Any]) -> Dict[str, Any]:
        """
        Allocate costs based on provided rules.
        
        Args:
            cost_data: Cost data from all cloud providers
            allocation_rules: Rules for cost allocation
            
        Returns:
            Dictionary containing allocation results
        """
        self.logger.info("Starting cost allocation analysis")
        
        # Extract allocation method and parameters
        method = allocation_rules.get('method', self.config.optimization.default_allocation_method)
        tags = allocation_rules.get('tags', [])
        departments = allocation_rules.get('departments', [])
        projects = allocation_rules.get('projects', [])
        
        results = {
            'allocation_method': method,
            'allocation_rules': allocation_rules,
            'allocated_costs': {},
            'unallocated_costs': {},
            'allocation_summary': {}
        }
        
        # Allocate costs for each provider
        for provider_name, provider_data in cost_data.items():
            if provider_name == 'summary':
                continue
                
            try:
                provider_allocation = self._allocate_provider_costs(
                    provider_name, provider_data, method, tags, departments, projects
                )
                results['allocated_costs'][provider_name] = provider_allocation
                
            except Exception as e:
                self.logger.error(f"Error allocating costs for {provider_name}: {e}")
                results['allocated_costs'][provider_name] = {'error': str(e)}
        
        # Generate summary
        results['allocation_summary'] = self._generate_allocation_summary(results)
        
        return results
    
    def _allocate_provider_costs(self,
                                provider_name: str,
                                provider_data: Dict[str, Any],
                                method: str,
                                tags: List[str],
                                departments: List[str],
                                projects: List[str]) -> Dict[str, Any]:
        """
        Allocate costs for a specific provider.
        
        Args:
            provider_name: Name of the cloud provider
            provider_data: Cost data for the provider
            method: Allocation method to use
            tags: Tags to use for allocation
            departments: Departments to allocate to
            projects: Projects to allocate to
            
        Returns:
            Allocation results for the provider
        """
        if method == 'tag_based':
            return self._allocate_by_tags(provider_data, tags)
        elif method == 'proportional':
            return self._allocate_proportional(provider_data, departments, projects)
        elif method == 'usage_based':
            return self._allocate_by_usage(provider_data, departments, projects)
        elif method == 'hybrid':
            return self._allocate_hybrid(provider_data, tags, departments, projects)
        else:
            self.logger.warning(f"Unknown allocation method: {method}")
            return self._allocate_proportional(provider_data, departments, projects)
    
    def _allocate_by_tags(self,
                          provider_data: Dict[str, Any],
                          tags: List[str]) -> Dict[str, Any]:
        """
        Allocate costs based on resource tags.
        
        Args:
            provider_data: Cost data for the provider
            tags: Tags to use for allocation
            
        Returns:
            Tag-based allocation results
        """
        allocation_results = {
            'method': 'tag_based',
            'allocated': {},
            'unallocated': 0,
            'total_cost': 0
        }
        
        # Extract cost data by resource
        resource_costs = self._extract_resource_costs(provider_data)
        
        for resource_id, cost_info in resource_costs.items():
            resource_tags = cost_info.get('tags', {})
            cost = cost_info.get('cost', 0)
            
            # Find matching allocation tags
            allocated = False
            for tag in tags:
                if tag in resource_tags:
                    tag_value = resource_tags[tag]
                    if tag_value not in allocation_results['allocated']:
                        allocation_results['allocated'][tag_value] = 0
                    allocation_results['allocated'][tag_value] += cost
                    allocated = True
                    break
            
            if not allocated:
                allocation_results['unallocated'] += cost
            
            allocation_results['total_cost'] += cost
        
        return allocation_results
    
    def _allocate_proportional(self,
                              provider_data: Dict[str, Any],
                              departments: List[str],
                              projects: List[str]) -> Dict[str, Any]:
        """
        Allocate costs proportionally across departments/projects.
        
        Args:
            provider_data: Cost data for the provider
            departments: Departments to allocate to
            projects: Projects to allocate to
            
        Returns:
            Proportional allocation results
        """
        allocation_results = {
            'method': 'proportional',
            'allocated': {},
            'unallocated': 0,
            'total_cost': 0
        }
        
        # Calculate total cost
        total_cost = self._calculate_total_cost(provider_data)
        allocation_results['total_cost'] = total_cost
        
        # Allocate proportionally
        entities = departments + projects
        if entities:
            cost_per_entity = total_cost / len(entities)
            for entity in entities:
                allocation_results['allocated'][entity] = cost_per_entity
        else:
            allocation_results['unallocated'] = total_cost
        
        return allocation_results
    
    def _allocate_by_usage(self,
                           provider_data: Dict[str, Any],
                           departments: List[str],
                           projects: List[str]) -> Dict[str, Any]:
        """
        Allocate costs based on resource usage.
        
        Args:
            provider_data: Cost data for the provider
            departments: Departments to allocate to
            projects: Projects to allocate to
            
        Returns:
            Usage-based allocation results
        """
        allocation_results = {
            'method': 'usage_based',
            'allocated': {},
            'unallocated': 0,
            'total_cost': 0
        }
        
        # Extract usage data
        usage_data = self._extract_usage_data(provider_data)
        
        # Calculate allocation based on usage
        total_usage = sum(usage_data.values())
        total_cost = self._calculate_total_cost(provider_data)
        
        allocation_results['total_cost'] = total_cost
        
        if total_usage > 0:
            for entity, usage in usage_data.items():
                allocation_results['allocated'][entity] = (usage / total_usage) * total_cost
        else:
            allocation_results['unallocated'] = total_cost
        
        return allocation_results
    
    def _allocate_hybrid(self,
                         provider_data: Dict[str, Any],
                         tags: List[str],
                         departments: List[str],
                         projects: List[str]) -> Dict[str, Any]:
        """
        Allocate costs using a hybrid approach.
        
        Args:
            provider_data: Cost data for the provider
            tags: Tags to use for allocation
            departments: Departments to allocate to
            projects: Projects to allocate to
            
        Returns:
            Hybrid allocation results
        """
        # Try tag-based allocation first
        tag_allocation = self._allocate_by_tags(provider_data, tags)
        
        # If there are unallocated costs, use proportional allocation
        if tag_allocation['unallocated'] > 0:
            unallocated_cost = tag_allocation['unallocated']
            entities = departments + projects
            
            if entities:
                cost_per_entity = unallocated_cost / len(entities)
                for entity in entities:
                    if entity in tag_allocation['allocated']:
                        tag_allocation['allocated'][entity] += cost_per_entity
                    else:
                        tag_allocation['allocated'][entity] = cost_per_entity
                tag_allocation['unallocated'] = 0
        
        tag_allocation['method'] = 'hybrid'
        return tag_allocation
    
    def _extract_resource_costs(self, provider_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract cost data by resource from provider data."""
        resource_costs = {}
        
        # Handle different provider data structures
        if 'instance_breakdown' in provider_data:
            instances = provider_data['instance_breakdown'].get('instances', {})
            for instance_id, instance_data in instances.items():
                resource_costs[instance_id] = {
                    'cost': instance_data.get('cost', 0),
                    'tags': instance_data.get('tags', {})
                }
        
        return resource_costs
    
    def _extract_usage_data(self, provider_data: Dict[str, Any]) -> Dict[str, float]:
        """Extract usage data from provider data."""
        usage_data = {}
        
        # This would extract actual usage metrics
        # For now, return placeholder data
        if 'resource_inventory' in provider_data:
            inventory = provider_data['resource_inventory']
            if 'ec2_instances' in inventory:
                usage_data['compute'] = inventory['ec2_instances'].get('running', 0)
            if 'rds_instances' in inventory:
                usage_data['database'] = inventory['rds_instances'].get('total', 0)
        
        return usage_data
    
    def _calculate_total_cost(self, provider_data: Dict[str, Any]) -> float:
        """Calculate total cost from provider data."""
        return provider_data.get('total_cost', 0)
    
    def _generate_allocation_summary(self, allocation_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary of allocation results."""
        summary = {
            'total_allocated': 0,
            'total_unallocated': 0,
            'allocation_percentage': 0,
            'providers_allocated': 0,
            'allocation_methods_used': set()
        }
        
        for provider_name, provider_allocation in allocation_results['allocated_costs'].items():
            if 'error' not in provider_allocation:
                summary['total_allocated'] += sum(provider_allocation['allocated'].values())
                summary['total_unallocated'] += provider_allocation.get('unallocated', 0)
                summary['allocation_methods_used'].add(provider_allocation.get('method', 'unknown'))
                summary['providers_allocated'] += 1
        
        total_cost = summary['total_allocated'] + summary['total_unallocated']
        if total_cost > 0:
            summary['allocation_percentage'] = (summary['total_allocated'] / total_cost) * 100
        
        summary['allocation_methods_used'] = list(summary['allocation_methods_used'])
        
        return summary
    
    def generate_recommendations(self, cost_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate cost allocation recommendations.
        
        Args:
            cost_data: Cost data from all providers
            
        Returns:
            List of allocation recommendations
        """
        recommendations = []
        
        # Analyze tagging compliance
        tagging_recommendations = self._analyze_tagging_compliance(cost_data)
        recommendations.extend(tagging_recommendations)
        
        # Analyze cost distribution
        distribution_recommendations = self._analyze_cost_distribution(cost_data)
        recommendations.extend(distribution_recommendations)
        
        return recommendations
    
    def _analyze_tagging_compliance(self, cost_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze tagging compliance and generate recommendations."""
        recommendations = []
        
        for provider_name, provider_data in cost_data.items():
            if provider_name == 'summary':
                continue
            
            # Check for untagged resources
            untagged_cost = 0
            if 'instance_breakdown' in provider_data:
                instances = provider_data['instance_breakdown'].get('instances', {})
                for instance_data in instances.values():
                    if not instance_data.get('tags'):
                        untagged_cost += instance_data.get('cost', 0)
            
            if untagged_cost > 0:
                recommendations.append({
                    'type': 'tagging_compliance',
                    'provider': provider_name,
                    'description': f'Found ${untagged_cost:.2f} in untagged resources',
                    'recommendation': 'Implement consistent tagging strategy for cost allocation',
                    'potential_impact': 'Improved cost visibility and allocation accuracy'
                })
        
        return recommendations
    
    def _analyze_cost_distribution(self, cost_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze cost distribution and generate recommendations."""
        recommendations = []
        
        # Check for cost concentration
        for provider_name, provider_data in cost_data.items():
            if provider_name == 'summary':
                continue
            
            total_cost = provider_data.get('total_cost', 0)
            if total_cost > 0:
                # Check service breakdown for concentration
                service_breakdown = provider_data.get('service_breakdown', {})
                if service_breakdown:
                    max_service_cost = max(service_breakdown.values())
                    max_service_name = max(service_breakdown, key=service_breakdown.get)
                    
                    if max_service_cost / total_cost > 0.8:  # 80% concentration
                        recommendations.append({
                            'type': 'cost_concentration',
                            'provider': provider_name,
                            'description': f'High cost concentration in {max_service_name}',
                            'recommendation': 'Consider cost optimization strategies for this service',
                            'potential_impact': 'Reduce cost concentration risk'
                        })
        
        return recommendations 
"""
Oracle Cloud cost analyzer for FinOpsOptimizer.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict


class OracleCostAnalyzer:
    """
    Oracle Cloud cost analyzer.
    
    Analyzes costs and usage patterns for Oracle Cloud Infrastructure.
    """
    
    def __init__(self, provider):
        """
        Initialize Oracle Cloud cost analyzer.
        
        Args:
            provider: Oracle Cloud provider instance
        """
        self.provider = provider
        self.logger = logging.getLogger(__name__)
    
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
        self.logger.info(f"Analyzing Oracle Cloud costs from {start_date} to {end_date}")
        
        try:
            # Get cost and usage data
            cost_data = self.provider.get_cost_and_usage(start_date, end_date)
            
            # Analyze the data
            analysis_results = {
                'provider': 'oracle',
                'analysis_period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat()
                },
                'total_cost': 0,
                'service_breakdown': {},
                'daily_costs': {},
                'resource_inventory': {},
                'cost_trends': {}
            }
            
            # Process cost data
            if cost_data and 'items' in cost_data:
                analysis_results.update(self._process_cost_data(cost_data['items']))
            
            # Get resource inventory
            analysis_results['resource_inventory'] = self._get_resource_inventory()
            
            # Calculate cost trends
            analysis_results['cost_trends'] = self._calculate_cost_trends(cost_data)
            
            return analysis_results
            
        except Exception as e:
            self.logger.error(f"Error analyzing Oracle Cloud costs: {e}")
            return {
                'provider': 'oracle',
                'error': str(e),
                'total_cost': 0
            }
    
    def _process_cost_data(self, cost_items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process raw cost data from Oracle Cloud Usage API."""
        
        total_cost = 0
        service_breakdown = defaultdict(float)
        daily_costs = defaultdict(float)
        
        for item in cost_items:
            # Extract cost information
            cost = float(item.get('computed_amount', 0))
            service = item.get('service', 'Unknown')
            time_usage_started = item.get('time_usage_started')
            
            total_cost += cost
            service_breakdown[service] += cost
            
            # Group by day
            if time_usage_started:
                if isinstance(time_usage_started, str):
                    date_key = time_usage_started[:10]  # YYYY-MM-DD
                else:
                    date_key = time_usage_started.strftime('%Y-%m-%d')
                daily_costs[date_key] += cost
        
        return {
            'total_cost': total_cost,
            'service_breakdown': dict(service_breakdown),
            'daily_costs': dict(daily_costs)
        }
    
    def _get_resource_inventory(self) -> Dict[str, Any]:
        """Get inventory of Oracle Cloud resources."""
        
        inventory = {}
        
        try:
            # Get compute instances
            compute_instances = self.provider.get_compute_instances()
            inventory['compute_instances'] = {
                'total': len(compute_instances),
                'running': len([i for i in compute_instances if i['lifecycle_state'] == 'RUNNING']),
                'stopped': len([i for i in compute_instances if i['lifecycle_state'] == 'STOPPED']),
                'instances': compute_instances
            }
            
            # Get block volumes
            block_volumes = self.provider.get_block_volumes()
            inventory['block_volumes'] = {
                'total': len(block_volumes),
                'available': len([v for v in block_volumes if v['lifecycle_state'] == 'AVAILABLE']),
                'total_size_gb': sum(v['size_in_gbs'] for v in block_volumes),
                'volumes': block_volumes
            }
            
            # Get unattached volumes
            unattached_volumes = self.provider.get_unattached_volumes()
            inventory['unattached_volumes'] = {
                'total': len(unattached_volumes),
                'total_size_gb': sum(v['size_in_gbs'] for v in unattached_volumes),
                'volumes': unattached_volumes
            }
            
            # Get autoscaling configurations
            autoscaling_configs = self.provider.get_autoscaling_configurations()
            inventory['autoscaling_configurations'] = {
                'total': len(autoscaling_configs),
                'enabled': len([c for c in autoscaling_configs if c['is_enabled']]),
                'configurations': autoscaling_configs
            }
            
        except Exception as e:
            self.logger.error(f"Error getting resource inventory: {e}")
            inventory['error'] = str(e)
        
        return inventory
    
    def _calculate_cost_trends(self, cost_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate cost trends and patterns."""
        
        trends = {
            'cost_variance': 0,
            'average_daily_cost': 0,
            'peak_cost_day': None,
            'lowest_cost_day': None
        }
        
        try:
            if cost_data and 'items' in cost_data:
                daily_costs = defaultdict(float)
                
                for item in cost_data['items']:
                    cost = float(item.get('computed_amount', 0))
                    time_usage_started = item.get('time_usage_started')
                    
                    if time_usage_started:
                        if isinstance(time_usage_started, str):
                            date_key = time_usage_started[:10]
                        else:
                            date_key = time_usage_started.strftime('%Y-%m-%d')
                        daily_costs[date_key] += cost
                
                if daily_costs:
                    costs = list(daily_costs.values())
                    trends['average_daily_cost'] = sum(costs) / len(costs)
                    trends['cost_variance'] = max(costs) - min(costs)
                    
                    # Find peak and lowest cost days
                    max_cost = max(costs)
                    min_cost = min(costs)
                    
                    for date, cost in daily_costs.items():
                        if cost == max_cost:
                            trends['peak_cost_day'] = {'date': date, 'cost': cost}
                        if cost == min_cost:
                            trends['lowest_cost_day'] = {'date': date, 'cost': cost}
        
        except Exception as e:
            self.logger.error(f"Error calculating cost trends: {e}")
            trends['error'] = str(e)
        
        return trends
    
    def get_cost_by_service(self, 
                           start_date: datetime,
                           end_date: datetime) -> Dict[str, float]:
        """
        Get cost breakdown by Oracle Cloud service.
        
        Args:
            start_date: Start date for analysis
            end_date: End date for analysis
            
        Returns:
            Dictionary mapping service names to costs
        """
        try:
            cost_data = self.provider.get_cost_and_usage(start_date, end_date)
            service_costs = defaultdict(float)
            
            if cost_data and 'items' in cost_data:
                for item in cost_data['items']:
                    service = item.get('service', 'Unknown')
                    cost = float(item.get('computed_amount', 0))
                    service_costs[service] += cost
            
            return dict(service_costs)
            
        except Exception as e:
            self.logger.error(f"Error getting cost by service: {e}")
            return {}
    
    def get_cost_by_compartment(self,
                               start_date: datetime,
                               end_date: datetime) -> Dict[str, float]:
        """
        Get cost breakdown by Oracle Cloud compartment.
        
        Args:
            start_date: Start date for analysis
            end_date: End date for analysis
            
        Returns:
            Dictionary mapping compartment names to costs
        """
        try:
            cost_data = self.provider.get_cost_and_usage(start_date, end_date)
            compartment_costs = defaultdict(float)
            
            if cost_data and 'items' in cost_data:
                for item in cost_data['items']:
                    compartment = item.get('compartment_name', 'Unknown')
                    cost = float(item.get('computed_amount', 0))
                    compartment_costs[compartment] += cost
            
            return dict(compartment_costs)
            
        except Exception as e:
            self.logger.error(f"Error getting cost by compartment: {e}")
            return {}
    
    def analyze_compute_costs(self) -> Dict[str, Any]:
        """
        Analyze compute-specific costs and utilization.
        
        Returns:
            Dictionary containing compute cost analysis
        """
        try:
            compute_analysis = {
                'total_instances': 0,
                'running_instances': 0,
                'stopped_instances': 0,
                'instance_breakdown': {},
                'shape_distribution': defaultdict(int),
                'cost_by_shape': defaultdict(float)
            }
            
            instances = self.provider.get_compute_instances()
            compute_analysis['total_instances'] = len(instances)
            
            for instance in instances:
                state = instance['lifecycle_state']
                shape = instance['shape']
                
                if state == 'RUNNING':
                    compute_analysis['running_instances'] += 1
                elif state == 'STOPPED':
                    compute_analysis['stopped_instances'] += 1
                
                compute_analysis['shape_distribution'][shape] += 1
                
                # Estimate cost based on shape (simplified)
                estimated_cost = self._estimate_instance_cost(shape, state)
                compute_analysis['cost_by_shape'][shape] += estimated_cost
                
                compute_analysis['instance_breakdown'][instance['id']] = {
                    'display_name': instance['display_name'],
                    'shape': shape,
                    'state': state,
                    'estimated_monthly_cost': estimated_cost,
                    'availability_domain': instance['availability_domain']
                }
            
            return compute_analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing compute costs: {e}")
            return {'error': str(e)}
    
    def analyze_storage_costs(self) -> Dict[str, Any]:
        """
        Analyze storage-specific costs.
        
        Returns:
            Dictionary containing storage cost analysis
        """
        try:
            storage_analysis = {
                'total_volumes': 0,
                'total_size_gb': 0,
                'unattached_volumes': 0,
                'unattached_size_gb': 0,
                'estimated_monthly_cost': 0,
                'volume_breakdown': {}
            }
            
            # Analyze all volumes
            volumes = self.provider.get_block_volumes()
            storage_analysis['total_volumes'] = len(volumes)
            storage_analysis['total_size_gb'] = sum(v['size_in_gbs'] for v in volumes)
            
            # Analyze unattached volumes
            unattached_volumes = self.provider.get_unattached_volumes()
            storage_analysis['unattached_volumes'] = len(unattached_volumes)
            storage_analysis['unattached_size_gb'] = sum(v['size_in_gbs'] for v in unattached_volumes)
            
            # Estimate costs
            for volume in volumes:
                size_gb = volume['size_in_gbs']
                estimated_cost = self._estimate_volume_cost(size_gb)
                storage_analysis['estimated_monthly_cost'] += estimated_cost
                
                storage_analysis['volume_breakdown'][volume['id']] = {
                    'display_name': volume['display_name'],
                    'size_gb': size_gb,
                    'state': volume['lifecycle_state'],
                    'estimated_monthly_cost': estimated_cost,
                    'is_unattached': volume in unattached_volumes
                }
            
            return storage_analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing storage costs: {e}")
            return {'error': str(e)}
    
    def _estimate_instance_cost(self, shape: str, state: str) -> float:
        """
        Estimate monthly cost for a compute instance.
        
        Args:
            shape: Instance shape
            state: Instance state
            
        Returns:
            Estimated monthly cost in USD
        """
        # Simplified pricing (actual pricing varies by region and commitment)
        shape_pricing = {
            'VM.Standard.E2.1': 25.55,  # 1 OCPU, 8GB RAM
            'VM.Standard.E2.2': 51.10,  # 2 OCPU, 16GB RAM
            'VM.Standard.E2.4': 102.20, # 4 OCPU, 32GB RAM
            'VM.Standard.E2.8': 204.40, # 8 OCPU, 64GB RAM
            'VM.Standard2.1': 25.55,    # 1 OCPU, 15GB RAM
            'VM.Standard2.2': 51.10,    # 2 OCPU, 30GB RAM
            'VM.Standard2.4': 102.20,   # 4 OCPU, 60GB RAM
            'VM.Standard2.8': 204.40,   # 8 OCPU, 120GB RAM
            'VM.Standard.A1.Flex': 15.00,  # ARM-based, flexible
        }
        
        base_cost = shape_pricing.get(shape, 50.0)  # Default cost
        
        # Only charge for running instances
        if state == 'RUNNING':
            return base_cost
        else:
            return 0.0  # Stopped instances don't incur compute costs
    
    def _estimate_volume_cost(self, size_gb: int) -> float:
        """
        Estimate monthly cost for a block volume.
        
        Args:
            size_gb: Volume size in GB
            
        Returns:
            Estimated monthly cost in USD
        """
        # Oracle Cloud block storage pricing (simplified)
        cost_per_gb_month = 0.0255  # USD per GB per month
        return size_gb * cost_per_gb_month
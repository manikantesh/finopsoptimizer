"""
AWS Cost Analyzer for detailed cost analysis and breakdown.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict


class AWSCostAnalyzer:
    """
    AWS-specific cost analyzer that provides detailed cost breakdowns
    and analysis for AWS resources.
    """
    
    def __init__(self, provider):
        """
        Initialize AWS cost analyzer.
        
        Args:
            provider: AWS provider instance
        """
        self.provider = provider
        self.logger = logging.getLogger(__name__)
    
    def analyze_costs(self, 
                     start_date: datetime,
                     end_date: datetime) -> Dict[str, Any]:
        """
        Analyze AWS costs for the specified period.
        
        Args:
            start_date: Start date for cost analysis
            end_date: End date for cost analysis
            
        Returns:
            Dictionary containing detailed cost analysis
        """
        self.logger.info(f"Analyzing AWS costs from {start_date} to {end_date}")
        
        # Get basic cost data
        cost_data = self.provider.get_cost_and_usage(start_date, end_date)
        
        # Get detailed breakdowns
        service_breakdown = self._get_service_breakdown(start_date, end_date)
        region_breakdown = self._get_region_breakdown(start_date, end_date)
        instance_breakdown = self._get_instance_breakdown(start_date, end_date)
        storage_breakdown = self._get_storage_breakdown(start_date, end_date)
        
        # Calculate summary statistics
        total_cost = self._calculate_total_cost(cost_data)
        cost_trends = self._analyze_cost_trends(cost_data)
        
        # Get resource inventory
        resource_inventory = self._get_resource_inventory()
        
        results = {
            'total_cost': total_cost,
            'cost_trends': cost_trends,
            'service_breakdown': service_breakdown,
            'region_breakdown': region_breakdown,
            'instance_breakdown': instance_breakdown,
            'storage_breakdown': storage_breakdown,
            'resource_inventory': resource_inventory,
            'analysis_period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'days': (end_date - start_date).days
            },
            'cost_optimization_opportunities': self._identify_optimization_opportunities()
        }
        
        return results
    
    def _get_service_breakdown(self, 
                              start_date: datetime,
                              end_date: datetime) -> Dict[str, float]:
        """
        Get cost breakdown by AWS service.
        
        Args:
            start_date: Start date for analysis
            end_date: End date for analysis
            
        Returns:
            Dictionary mapping service names to costs
        """
        try:
            response = self.provider.get_cost_and_usage(
                start_date, end_date,
                group_by=[{'Type': 'DIMENSION', 'Key': 'SERVICE'}]
            )
            
            service_costs = {}
            for group in response.get('ResultsByTime', []):
                for group_data in group.get('Groups', []):
                    service_name = group_data['Keys'][0]
                    cost = float(group_data['Metrics']['UnblendedCost']['Amount'])
                    service_costs[service_name] = service_costs.get(service_name, 0) + cost
            
            return service_costs
            
        except Exception as e:
            self.logger.error(f"Error getting service breakdown: {e}")
            return {}
    
    def _get_region_breakdown(self, 
                             start_date: datetime,
                             end_date: datetime) -> Dict[str, float]:
        """
        Get cost breakdown by AWS region.
        
        Args:
            start_date: Start date for analysis
            end_date: End date for analysis
            
        Returns:
            Dictionary mapping region names to costs
        """
        try:
            response = self.provider.get_cost_and_usage(
                start_date, end_date,
                group_by=[{'Type': 'DIMENSION', 'Key': 'REGION'}]
            )
            
            region_costs = {}
            for group in response.get('ResultsByTime', []):
                for group_data in group.get('Groups', []):
                    region_name = group_data['Keys'][0]
                    cost = float(group_data['Metrics']['UnblendedCost']['Amount'])
                    region_costs[region_name] = region_costs.get(region_name, 0) + cost
            
            return region_costs
            
        except Exception as e:
            self.logger.error(f"Error getting region breakdown: {e}")
            return {}
    
    def _get_instance_breakdown(self, 
                               start_date: datetime,
                               end_date: datetime) -> Dict[str, Any]:
        """
        Get detailed instance cost breakdown.
        
        Args:
            start_date: Start date for analysis
            end_date: End date for analysis
            
        Returns:
            Dictionary containing instance cost details
        """
        try:
            # Get EC2 instances
            instances = self.provider.get_ec2_instances()
            
            # Get cost data for instances
            instance_costs = {}
            for instance in instances:
                instance_id = instance['instance_id']
                
                # Get cost data for this instance
                response = self.provider.get_cost_and_usage(
                    start_date, end_date,
                    group_by=[{'Type': 'DIMENSION', 'Key': 'RESOURCE_ID'}]
                )
                
                # Find cost for this instance
                instance_cost = 0
                for group in response.get('ResultsByTime', []):
                    for group_data in group.get('Groups', []):
                        resource_id = group_data['Keys'][0]
                        if resource_id == instance_id:
                            cost = float(group_data['Metrics']['UnblendedCost']['Amount'])
                            instance_cost += cost
                
                instance_costs[instance_id] = {
                    'instance_type': instance['instance_type'],
                    'state': instance['state'],
                    'cost': instance_cost,
                    'region': instance['availability_zone'],
                    'tags': instance['tags']
                }
            
            return {
                'total_instance_cost': sum(inst['cost'] for inst in instance_costs.values()),
                'instances': instance_costs,
                'instance_type_breakdown': self._group_by_instance_type(instance_costs)
            }
            
        except Exception as e:
            self.logger.error(f"Error getting instance breakdown: {e}")
            return {}
    
    def _get_storage_breakdown(self, 
                              start_date: datetime,
                              end_date: datetime) -> Dict[str, Any]:
        """
        Get storage cost breakdown.
        
        Args:
            start_date: Start date for analysis
            end_date: End date for analysis
            
        Returns:
            Dictionary containing storage cost details
        """
        try:
            # Get RDS instances for storage costs
            rds_instances = self.provider.get_rds_instances()
            
            storage_costs = {
                'ebs': 0,
                'rds_storage': 0,
                's3': 0,
                'other_storage': 0
            }
            
            # Get cost data grouped by service
            response = self.provider.get_cost_and_usage(
                start_date, end_date,
                group_by=[{'Type': 'DIMENSION', 'Key': 'SERVICE'}]
            )
            
            for group in response.get('ResultsByTime', []):
                for group_data in group.get('Groups', []):
                    service_name = group_data['Keys'][0]
                    cost = float(group_data['Metrics']['UnblendedCost']['Amount'])
                    
                    if 'Amazon S3' in service_name:
                        storage_costs['s3'] += cost
                    elif 'Amazon EBS' in service_name:
                        storage_costs['ebs'] += cost
                    elif 'Amazon RDS' in service_name:
                        storage_costs['rds_storage'] += cost
                    elif any(storage_service in service_name for storage_service in 
                           ['Amazon EFS', 'Amazon FSx', 'Amazon Glacier']):
                        storage_costs['other_storage'] += cost
            
            storage_costs['total_storage_cost'] = sum(storage_costs.values())
            
            return storage_costs
            
        except Exception as e:
            self.logger.error(f"Error getting storage breakdown: {e}")
            return {}
    
    def _calculate_total_cost(self, cost_data: Dict[str, Any]) -> float:
        """
        Calculate total cost from cost data.
        
        Args:
            cost_data: Cost data from AWS Cost Explorer
            
        Returns:
            Total cost as float
        """
        total_cost = 0
        
        for result in cost_data.get('ResultsByTime', []):
            cost = float(result['Total']['UnblendedCost']['Amount'])
            total_cost += cost
        
        return total_cost
    
    def _analyze_cost_trends(self, cost_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze cost trends over time.
        
        Args:
            cost_data: Cost data from AWS Cost Explorer
            
        Returns:
            Dictionary containing trend analysis
        """
        daily_costs = []
        
        for result in cost_data.get('ResultsByTime', []):
            date = result['TimePeriod']['Start']
            cost = float(result['Total']['UnblendedCost']['Amount'])
            daily_costs.append({'date': date, 'cost': cost})
        
        if not daily_costs:
            return {}
        
        # Calculate trends
        costs = [day['cost'] for day in daily_costs]
        avg_cost = sum(costs) / len(costs)
        max_cost = max(costs)
        min_cost = min(costs)
        
        # Calculate trend direction
        if len(costs) >= 2:
            first_week_avg = sum(costs[:7]) / min(7, len(costs))
            last_week_avg = sum(costs[-7:]) / min(7, len(costs))
            trend_direction = 'increasing' if last_week_avg > first_week_avg else 'decreasing'
        else:
            trend_direction = 'stable'
        
        return {
            'daily_costs': daily_costs,
            'average_daily_cost': avg_cost,
            'max_daily_cost': max_cost,
            'min_daily_cost': min_cost,
            'trend_direction': trend_direction,
            'cost_variance': max_cost - min_cost
        }
    
    def _get_resource_inventory(self) -> Dict[str, Any]:
        """
        Get current resource inventory.
        
        Returns:
            Dictionary containing resource inventory
        """
        try:
            ec2_instances = self.provider.get_ec2_instances()
            rds_instances = self.provider.get_rds_instances()
            autoscaling_groups = self.provider.get_autoscaling_groups()
            
            return {
                'ec2_instances': {
                    'total': len(ec2_instances),
                    'running': len([i for i in ec2_instances if i['state'] == 'running']),
                    'stopped': len([i for i in ec2_instances if i['state'] == 'stopped']),
                    'by_instance_type': self._count_by_instance_type(ec2_instances)
                },
                'rds_instances': {
                    'total': len(rds_instances),
                    'by_engine': self._count_by_engine(rds_instances)
                },
                'autoscaling_groups': {
                    'total': len(autoscaling_groups),
                    'total_instances': sum(len(g['instances']) for g in autoscaling_groups)
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error getting resource inventory: {e}")
            return {}
    
    def _identify_optimization_opportunities(self) -> List[Dict[str, Any]]:
        """
        Identify cost optimization opportunities.
        
        Returns:
            List of optimization opportunities
        """
        opportunities = []
        
        try:
            # Check for stopped instances
            instances = self.provider.get_ec2_instances()
            stopped_instances = [i for i in instances if i['state'] == 'stopped']
            
            if stopped_instances:
                opportunities.append({
                    'type': 'stopped_instances',
                    'description': f'Found {len(stopped_instances)} stopped instances',
                    'potential_savings': len(stopped_instances) * 50,  # Rough estimate
                    'recommendation': 'Consider terminating stopped instances if not needed'
                })
            
            # Check for rightsizing opportunities
            rightsizing_recs = self.provider.get_rightsizing_recommendations()
            if rightsizing_recs:
                opportunities.append({
                    'type': 'rightsizing',
                    'description': f'Found {len(rightsizing_recs)} rightsizing opportunities',
                    'potential_savings': sum(r.get('estimated_savings', 0) for r in rightsizing_recs),
                    'recommendation': 'Review rightsizing recommendations from AWS Cost Explorer'
                })
            
            # Check for Savings Plans opportunities
            savings_plans_recs = self.provider.get_savings_plans_recommendations()
            if savings_plans_recs:
                opportunities.append({
                    'type': 'savings_plans',
                    'description': f'Found {len(savings_plans_recs)} Savings Plans opportunities',
                    'potential_savings': sum(r.get('estimated_savings_amount', 0) for r in savings_plans_recs),
                    'recommendation': 'Consider purchasing Savings Plans for predictable workloads'
                })
            
        except Exception as e:
            self.logger.error(f"Error identifying optimization opportunities: {e}")
        
        return opportunities
    
    def _group_by_instance_type(self, instance_costs: Dict[str, Any]) -> Dict[str, float]:
        """Group instance costs by instance type."""
        instance_type_costs = defaultdict(float)
        
        for instance_data in instance_costs.values():
            instance_type = instance_data['instance_type']
            cost = instance_data['cost']
            instance_type_costs[instance_type] += cost
        
        return dict(instance_type_costs)
    
    def _count_by_instance_type(self, instances: List[Dict[str, Any]]) -> Dict[str, int]:
        """Count instances by instance type."""
        counts = defaultdict(int)
        for instance in instances:
            counts[instance['instance_type']] += 1
        return dict(counts)
    
    def _count_by_engine(self, rds_instances: List[Dict[str, Any]]) -> Dict[str, int]:
        """Count RDS instances by engine."""
        counts = defaultdict(int)
        for instance in rds_instances:
            counts[instance['engine']] += 1
        return dict(counts) 
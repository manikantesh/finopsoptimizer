"""
VM Rightsizing module for multi-cloud cost optimization.
Analyzes VM metrics over 365 days to provide rightsizing recommendations.
"""

import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

from .config import Config
from .data_ingestion import DataIngestionPipeline
from .pricing_engine import RealTimePricingEngine


@dataclass
class RightsizingRecommendation:
    """Container for rightsizing recommendation."""
    resource_id: str
    provider: str
    resource_type: str
    current_size: str
    recommended_size: str
    current_cost: float
    projected_cost: float
    potential_savings: float
    confidence_score: float
    utilization_stats: Dict[str, float]
    recommendation_reason: str
    risk_level: str


class VMRightsizingAnalyzer:
    """
    VM Rightsizing analyzer for multi-cloud environments.
    
    Analyzes VM utilization patterns over 365 days to provide accurate
    rightsizing recommendations across AWS, Azure, GCP, and Oracle Cloud.
    """
    
    def __init__(self, config: Config):
        """
        Initialize VM Rightsizing Analyzer.
        
        Args:
            config: Configuration object
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize real-time pricing engine
        self.pricing_engine = RealTimePricingEngine(config)
        
        # Rightsizing thresholds
        self.cpu_threshold_low = 0.1  # 10% - underutilized
        self.cpu_threshold_high = 0.8  # 80% - well utilized
        self.memory_threshold_low = 0.2  # 20% - underutilized
        self.memory_threshold_high = 0.8  # 80% - well utilized
        
        # Minimum observation period (days)
        self.min_observation_days = 30
        
        # Instance type mappings for each provider (fallback only)
        self._load_instance_type_mappings()
    
    def _load_instance_type_mappings(self) -> None:
        """Load instance type mappings for all cloud providers (specs only, no pricing)."""
        # AWS instance type mappings (specs only - pricing comes from real-time API)
        self.aws_instance_types = {
            't3.nano': {'vcpu': 2, 'memory': 0.5},
            't3.micro': {'vcpu': 2, 'memory': 1},
            't3.small': {'vcpu': 2, 'memory': 2},
            't3.medium': {'vcpu': 2, 'memory': 4},
            't3.large': {'vcpu': 2, 'memory': 8},
            't3.xlarge': {'vcpu': 4, 'memory': 16},
            't3.2xlarge': {'vcpu': 8, 'memory': 32},
            'm5.large': {'vcpu': 2, 'memory': 8},
            'm5.xlarge': {'vcpu': 4, 'memory': 16},
            'm5.2xlarge': {'vcpu': 8, 'memory': 32},
            'm5.4xlarge': {'vcpu': 16, 'memory': 64},
            'm5.8xlarge': {'vcpu': 32, 'memory': 128},
            'c5.large': {'vcpu': 2, 'memory': 4},
            'c5.xlarge': {'vcpu': 4, 'memory': 8},
            'c5.2xlarge': {'vcpu': 8, 'memory': 16},
            'c5.4xlarge': {'vcpu': 16, 'memory': 32},
            'r5.large': {'vcpu': 2, 'memory': 16},
            'r5.xlarge': {'vcpu': 4, 'memory': 32},
            'r5.2xlarge': {'vcpu': 8, 'memory': 64},
            'r5.4xlarge': {'vcpu': 16, 'memory': 128}
        }
        
        # Azure VM size mappings (specs only - pricing comes from real-time API)
        self.azure_vm_sizes = {
            'Standard_B1s': {'vcpu': 1, 'memory': 1},
            'Standard_B1ms': {'vcpu': 1, 'memory': 2},
            'Standard_B2s': {'vcpu': 2, 'memory': 4},
            'Standard_B2ms': {'vcpu': 2, 'memory': 8},
            'Standard_B4ms': {'vcpu': 4, 'memory': 16},
            'Standard_D2s_v3': {'vcpu': 2, 'memory': 8},
            'Standard_D4s_v3': {'vcpu': 4, 'memory': 16},
            'Standard_D8s_v3': {'vcpu': 8, 'memory': 32},
            'Standard_D16s_v3': {'vcpu': 16, 'memory': 64},
            'Standard_E2s_v3': {'vcpu': 2, 'memory': 16},
            'Standard_E4s_v3': {'vcpu': 4, 'memory': 32},
            'Standard_E8s_v3': {'vcpu': 8, 'memory': 64}
        }
        
        # GCP machine type mappings (specs only - pricing comes from real-time API)
        self.gcp_machine_types = {
            'f1-micro': {'vcpu': 1, 'memory': 0.6},
            'g1-small': {'vcpu': 1, 'memory': 1.7},
            'n1-standard-1': {'vcpu': 1, 'memory': 3.75},
            'n1-standard-2': {'vcpu': 2, 'memory': 7.5},
            'n1-standard-4': {'vcpu': 4, 'memory': 15},
            'n1-standard-8': {'vcpu': 8, 'memory': 30},
            'n1-highmem-2': {'vcpu': 2, 'memory': 13},
            'n1-highmem-4': {'vcpu': 4, 'memory': 26},
            'n1-highmem-8': {'vcpu': 8, 'memory': 52}
        }
        
        # Oracle Cloud shape mappings (specs only - pricing comes from real-time API)
        self.oracle_shapes = {
            'VM.Standard.E2.1': {'vcpu': 1, 'memory': 8},
            'VM.Standard.E2.2': {'vcpu': 2, 'memory': 16},
            'VM.Standard.E2.4': {'vcpu': 4, 'memory': 32},
            'VM.Standard.E2.8': {'vcpu': 8, 'memory': 64},
            'VM.Standard2.1': {'vcpu': 1, 'memory': 15},
            'VM.Standard2.2': {'vcpu': 2, 'memory': 30},
            'VM.Standard2.4': {'vcpu': 4, 'memory': 60},
            'VM.Standard2.8': {'vcpu': 8, 'memory': 120}
        }
    
    async def analyze_rightsizing_opportunities(self, 
                                               ingested_data: Dict[str, Any]) -> List[RightsizingRecommendation]:
        """
        Analyze rightsizing opportunities across all cloud providers.
        
        Args:
            ingested_data: Data from DataIngestionPipeline
            
        Returns:
            List of rightsizing recommendations
        """
        self.logger.info("Starting VM rightsizing analysis")
        
        recommendations = []
        
        for provider_name, provider_data in ingested_data.get('provider_data', {}).items():
            if 'error' in provider_data:
                self.logger.error(f"Skipping {provider_name} due to data ingestion error")
                continue
            
            try:
                provider_recommendations = await self._analyze_provider_rightsizing(
                    provider_name, provider_data
                )
                recommendations.extend(provider_recommendations)
                
            except Exception as e:
                self.logger.error(f"Error analyzing rightsizing for {provider_name}: {e}")
        
        # Sort recommendations by potential savings
        recommendations.sort(key=lambda x: x.potential_savings, reverse=True)
        
        self.logger.info(f"Generated {len(recommendations)} rightsizing recommendations")
        return recommendations
    
    async def _analyze_provider_rightsizing(self,
                                           provider_name: str,
                                           provider_data: Dict[str, Any]) -> List[RightsizingRecommendation]:
        """Analyze rightsizing for a specific provider."""
        recommendations = []
        
        vm_metrics = provider_data.get('vm_metrics', [])
        resource_inventory = provider_data.get('resource_inventory', {})
        
        if not vm_metrics:
            self.logger.warning(f"No VM metrics available for {provider_name}")
            return recommendations
        
        # Convert metrics to DataFrame for analysis
        df = pd.DataFrame(vm_metrics)
        
        if df.empty:
            return recommendations
        
        # Group by resource_id for analysis
        for resource_id in df['resource_id'].unique():
            resource_metrics = df[df['resource_id'] == resource_id]
            
            try:
                recommendation = await self._analyze_single_vm_rightsizing(
                    provider_name, resource_id, resource_metrics, resource_inventory
                )
                
                if recommendation:
                    recommendations.append(recommendation)
                    
            except Exception as e:
                self.logger.error(f"Error analyzing VM {resource_id}: {e}")
        
        return recommendations
    
    async def _analyze_single_vm_rightsizing(self,
                                            provider_name: str,
                                            resource_id: str,
                                            metrics_df: pd.DataFrame,
                                            inventory: Dict[str, Any]) -> Optional[RightsizingRecommendation]:
        """Analyze rightsizing for a single VM."""
        
        # Check if we have enough data
        observation_days = (metrics_df['timestamp'].max() - metrics_df['timestamp'].min()).days
        if observation_days < self.min_observation_days:
            self.logger.debug(f"Insufficient data for {resource_id}: {observation_days} days")
            return None
        
        # Calculate utilization statistics
        utilization_stats = self._calculate_utilization_stats(metrics_df)
        
        # Get current instance details
        current_instance = self._get_current_instance_details(
            provider_name, resource_id, inventory
        )
        
        if not current_instance:
            self.logger.warning(f"Could not find instance details for {resource_id}")
            return None
        
        # Determine recommended size
        recommended_size, confidence_score, reason = self._determine_recommended_size(
            provider_name, current_instance, utilization_stats
        )
        
        if not recommended_size or recommended_size == current_instance['size']:
            return None
        
        # Calculate cost savings using real-time pricing
        current_cost = await self._calculate_monthly_cost_realtime(provider_name, current_instance['size'], current_instance.get('region', 'us-east-1'))
        projected_cost = await self._calculate_monthly_cost_realtime(provider_name, recommended_size, current_instance.get('region', 'us-east-1'))
        potential_savings = current_cost - projected_cost
        
        # Determine risk level
        risk_level = self._assess_risk_level(utilization_stats, confidence_score)
        
        return RightsizingRecommendation(
            resource_id=resource_id,
            provider=provider_name,
            resource_type=current_instance['type'],
            current_size=current_instance['size'],
            recommended_size=recommended_size,
            current_cost=current_cost,
            projected_cost=projected_cost,
            potential_savings=potential_savings,
            confidence_score=confidence_score,
            utilization_stats=utilization_stats,
            recommendation_reason=reason,
            risk_level=risk_level
        )
    
    def _calculate_utilization_stats(self, metrics_df: pd.DataFrame) -> Dict[str, float]:
        """Calculate utilization statistics from metrics."""
        stats = {}
        
        # Group metrics by type
        cpu_metrics = metrics_df[metrics_df['metric_name'] == 'CPUUtilization']
        memory_metrics = metrics_df[metrics_df['metric_name'].str.contains('Memory', na=False)]
        network_in_metrics = metrics_df[metrics_df['metric_name'] == 'NetworkIn']
        network_out_metrics = metrics_df[metrics_df['metric_name'] == 'NetworkOut']
        
        if not cpu_metrics.empty:
            stats['cpu_avg'] = cpu_metrics['value'].mean() / 100.0  # Convert to percentage
            stats['cpu_max'] = cpu_metrics['value'].max() / 100.0
            stats['cpu_p95'] = cpu_metrics['value'].quantile(0.95) / 100.0
            stats['cpu_p99'] = cpu_metrics['value'].quantile(0.99) / 100.0
        
        if not memory_metrics.empty:
            stats['memory_avg'] = memory_metrics['value'].mean() / 100.0
            stats['memory_max'] = memory_metrics['value'].max() / 100.0
            stats['memory_p95'] = memory_metrics['value'].quantile(0.95) / 100.0
        
        if not network_in_metrics.empty:
            stats['network_in_avg'] = network_in_metrics['value'].mean()
            stats['network_in_max'] = network_in_metrics['value'].max()
        
        if not network_out_metrics.empty:
            stats['network_out_avg'] = network_out_metrics['value'].mean()
            stats['network_out_max'] = network_out_metrics['value'].max()
        
        return stats
    
    def _get_current_instance_details(self,
                                     provider_name: str,
                                     resource_id: str,
                                     inventory: Dict[str, Any]) -> Optional[Dict[str, str]]:
        """Get current instance details from inventory."""
        
        # Search through different resource types
        resource_types = ['ec2_instances', 'virtual_machines', 'compute_instances']
        
        for resource_type in resource_types:
            if resource_type in inventory:
                for instance in inventory[resource_type]:
                    instance_id = (instance.get('instance_id') or 
                                 instance.get('id') or 
                                 instance.get('name'))
                    
                    if instance_id == resource_id:
                        size = (instance.get('instance_type') or 
                               instance.get('vm_size') or 
                               instance.get('machine_type') or
                               instance.get('shape'))
                        
                        return {
                            'type': resource_type,
                            'size': size,
                            'details': instance
                        }
        
        return None
    
    def _determine_recommended_size(self,
                                   provider_name: str,
                                   current_instance: Dict[str, Any],
                                   utilization_stats: Dict[str, float]) -> Tuple[Optional[str], float, str]:
        """Determine recommended instance size based on utilization."""
        
        current_size = current_instance['size']
        cpu_avg = utilization_stats.get('cpu_avg', 0)
        cpu_p95 = utilization_stats.get('cpu_p95', 0)
        memory_avg = utilization_stats.get('memory_avg', 0)
        memory_p95 = utilization_stats.get('memory_p95', 0)
        
        # Get instance type mappings for the provider
        instance_types = self._get_instance_types_for_provider(provider_name)
        
        if current_size not in instance_types:
            return None, 0.0, "Current instance type not found in mappings"
        
        current_specs = instance_types[current_size]
        
        # Determine if downsizing is possible
        if (cpu_p95 < self.cpu_threshold_low and 
            memory_p95 < self.memory_threshold_low):
            
            # Find smaller instance type
            recommended_size = self._find_smaller_instance_type(
                provider_name, current_size, cpu_p95, memory_p95
            )
            
            if recommended_size:
                confidence = self._calculate_confidence_score(utilization_stats, 'downsize')
                return recommended_size, confidence, "Low utilization detected - downsize recommended"
        
        # Determine if upsizing is needed
        elif (cpu_p95 > self.cpu_threshold_high or 
              memory_p95 > self.memory_threshold_high):
            
            # Find larger instance type
            recommended_size = self._find_larger_instance_type(
                provider_name, current_size, cpu_p95, memory_p95
            )
            
            if recommended_size:
                confidence = self._calculate_confidence_score(utilization_stats, 'upsize')
                return recommended_size, confidence, "High utilization detected - upsize recommended"
        
        return None, 0.0, "Current size is appropriate"
    
    def _get_instance_types_for_provider(self, provider_name: str) -> Dict[str, Dict[str, Any]]:
        """Get instance type mappings for a specific provider."""
        mappings = {
            'aws': self.aws_instance_types,
            'azure': self.azure_vm_sizes,
            'gcp': self.gcp_machine_types,
            'oracle': self.oracle_shapes
        }
        return mappings.get(provider_name, {})
    
    async def _find_smaller_instance_type(self,
                                          provider_name: str,
                                          current_size: str,
                                          cpu_requirement: float,
                                          memory_requirement: float,
                                          region: str = 'us-east-1') -> Optional[str]:
        """Find a smaller instance type that meets requirements using real-time pricing."""
        
        instance_types = self._get_instance_types_for_provider(provider_name)
        current_specs = instance_types[current_size]
        
        # Find instances with lower specs but still meeting requirements
        candidates = []
        
        for size, specs in instance_types.items():
            if (specs['vcpu'] < current_specs['vcpu'] and
                specs['memory'] < current_specs['memory']):
                
                # Check if it can handle the workload (with some buffer)
                cpu_capacity = specs['vcpu'] * 0.8  # 80% utilization target
                memory_capacity = specs['memory'] * 0.8
                
                if (cpu_requirement <= cpu_capacity and
                    memory_requirement <= memory_capacity):
                    
                    # Get real-time pricing for this instance type
                    try:
                        async with self.pricing_engine:
                            pricing_data = await self.pricing_engine.get_instance_pricing(
                                provider=provider_name,
                                region=region,
                                instance_type=size
                            )
                            
                            if pricing_data:
                                hourly_cost = pricing_data.enterprise_price or pricing_data.on_demand_price
                                candidates.append((size, hourly_cost))
                    except Exception as e:
                        self.logger.debug(f"Could not get pricing for {size}: {e}")
                        # Skip this candidate if pricing is unavailable
                        continue
        
        if candidates:
            # Return the cheapest option that meets requirements
            candidates.sort(key=lambda x: x[1])
            return candidates[0][0]
        
        return None
    
    async def _find_larger_instance_type(self,
                                         provider_name: str,
                                         current_size: str,
                                         cpu_requirement: float,
                                         memory_requirement: float,
                                         region: str = 'us-east-1') -> Optional[str]:
        """Find a larger instance type that meets requirements using real-time pricing."""
        
        instance_types = self._get_instance_types_for_provider(provider_name)
        current_specs = instance_types[current_size]
        
        # Find instances with higher specs
        candidates = []
        
        for size, specs in instance_types.items():
            if (specs['vcpu'] > current_specs['vcpu'] or
                specs['memory'] > current_specs['memory']):
                
                # Check if it provides enough capacity
                cpu_capacity = specs['vcpu'] * 0.8  # 80% utilization target
                memory_capacity = specs['memory'] * 0.8
                
                if (cpu_requirement <= cpu_capacity and
                    memory_requirement <= memory_capacity):
                    
                    # Get real-time pricing for this instance type
                    try:
                        async with self.pricing_engine:
                            pricing_data = await self.pricing_engine.get_instance_pricing(
                                provider=provider_name,
                                region=region,
                                instance_type=size
                            )
                            
                            if pricing_data:
                                hourly_cost = pricing_data.enterprise_price or pricing_data.on_demand_price
                                candidates.append((size, hourly_cost))
                    except Exception as e:
                        self.logger.debug(f"Could not get pricing for {size}: {e}")
                        # Skip this candidate if pricing is unavailable
                        continue
        
        if candidates:
            # Return the cheapest option that meets requirements
            candidates.sort(key=lambda x: x[1])
            return candidates[0][0]
        
        return None
    
    def _calculate_confidence_score(self,
                                   utilization_stats: Dict[str, float],
                                   recommendation_type: str) -> float:
        """Calculate confidence score for the recommendation."""
        
        # Base confidence
        confidence = 0.5
        
        # Increase confidence based on data consistency
        cpu_avg = utilization_stats.get('cpu_avg', 0)
        cpu_p95 = utilization_stats.get('cpu_p95', 0)
        
        # Low variance increases confidence
        if abs(cpu_p95 - cpu_avg) < 0.1:  # Low variance
            confidence += 0.2
        
        # Extreme values increase confidence
        if recommendation_type == 'downsize':
            if cpu_p95 < 0.05:  # Very low utilization
                confidence += 0.3
        elif recommendation_type == 'upsize':
            if cpu_p95 > 0.9:  # Very high utilization
                confidence += 0.3
        
        return min(confidence, 1.0)
    
    async def _calculate_monthly_cost_realtime(self, provider_name: str, instance_size: str, region: str) -> float:
        """Calculate monthly cost using real-time pricing."""
        try:
            async with self.pricing_engine:
                pricing_data = await self.pricing_engine.get_instance_pricing(
                    provider=provider_name,
                    region=region,
                    instance_type=instance_size
                )
                
                if pricing_data:
                    # Use enterprise price if available, otherwise on-demand
                    hourly_cost = pricing_data.enterprise_price or pricing_data.on_demand_price
                    return hourly_cost * 24 * 30  # Monthly cost
                else:
                    # Fallback to static pricing
                    return self._calculate_monthly_cost_fallback(provider_name, instance_size)
                    
        except Exception as e:
            self.logger.error(f"Error getting real-time pricing for {instance_size}: {e}")
            return self._calculate_monthly_cost_fallback(provider_name, instance_size)
    
    def _calculate_monthly_cost_fallback(self, provider_name: str, instance_size: str) -> float:
        """Calculate monthly cost using fallback static pricing."""
        instance_types = self._get_instance_types_for_provider(provider_name)
        
        if instance_size not in instance_types:
            return 0.0
        
        hourly_cost = instance_types[instance_size]['cost_per_hour']
        return hourly_cost * 24 * 30  # Approximate monthly cost
    
    def _assess_risk_level(self,
                          utilization_stats: Dict[str, float],
                          confidence_score: float) -> str:
        """Assess risk level of the recommendation."""
        
        cpu_p95 = utilization_stats.get('cpu_p95', 0)
        memory_p95 = utilization_stats.get('memory_p95', 0)
        
        # High risk if utilization is already high
        if cpu_p95 > 0.7 or memory_p95 > 0.7:
            return 'high'
        
        # Low risk if confidence is high and utilization is low
        if confidence_score > 0.8 and cpu_p95 < 0.3:
            return 'low'
        
        return 'medium'
    
    def generate_rightsizing_report(self, 
                                   recommendations: List[RightsizingRecommendation]) -> Dict[str, Any]:
        """Generate a comprehensive rightsizing report."""
        
        if not recommendations:
            return {'message': 'No rightsizing recommendations found'}
        
        # Calculate summary statistics
        total_potential_savings = sum(rec.potential_savings for rec in recommendations)
        total_current_cost = sum(rec.current_cost for rec in recommendations)
        
        # Group by provider
        by_provider = {}
        for rec in recommendations:
            if rec.provider not in by_provider:
                by_provider[rec.provider] = []
            by_provider[rec.provider].append(rec)
        
        # Group by risk level
        by_risk = {'low': [], 'medium': [], 'high': []}
        for rec in recommendations:
            by_risk[rec.risk_level].append(rec)
        
        return {
            'summary': {
                'total_recommendations': len(recommendations),
                'total_potential_savings': total_potential_savings,
                'total_current_cost': total_current_cost,
                'savings_percentage': (total_potential_savings / total_current_cost * 100) if total_current_cost > 0 else 0
            },
            'by_provider': {
                provider: {
                    'count': len(recs),
                    'potential_savings': sum(rec.potential_savings for rec in recs),
                    'recommendations': [rec.__dict__ for rec in recs]
                }
                for provider, recs in by_provider.items()
            },
            'by_risk_level': {
                risk: {
                    'count': len(recs),
                    'potential_savings': sum(rec.potential_savings for rec in recs)
                }
                for risk, recs in by_risk.items()
            },
            'top_recommendations': [
                rec.__dict__ for rec in sorted(recommendations, 
                                             key=lambda x: x.potential_savings, 
                                             reverse=True)[:10]
            ]
        }
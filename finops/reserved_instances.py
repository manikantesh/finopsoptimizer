"""
Reserved Instances and Savings Plans analyzer for multi-cloud cost optimization.
Analyzes RI/SP utilization and provides purchase recommendations across all cloud providers.
"""

import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

from .config import Config


class ReservationType(Enum):
    """Types of reservations."""
    RESERVED_INSTANCE = "reserved_instance"
    SAVINGS_PLAN = "savings_plan"
    COMMITTED_USE_DISCOUNT = "committed_use_discount"
    UNIVERSAL_CREDITS = "universal_credits"


class ReservationTerm(Enum):
    """Reservation terms."""
    ONE_YEAR = "1_year"
    THREE_YEAR = "3_year"


class PaymentOption(Enum):
    """Payment options for reservations."""
    NO_UPFRONT = "no_upfront"
    PARTIAL_UPFRONT = "partial_upfront"
    ALL_UPFRONT = "all_upfront"


@dataclass
class ReservationRecommendation:
    """Container for reservation purchase recommendation."""
    provider: str
    reservation_type: ReservationType
    resource_type: str  # EC2, RDS, etc.
    instance_family: str
    region: str
    term: ReservationTerm
    payment_option: PaymentOption
    recommended_quantity: int
    upfront_cost: float
    monthly_cost: float
    annual_savings: float
    break_even_months: int
    utilization_requirement: float
    confidence_score: float
    risk_level: str
    current_on_demand_cost: float
    projected_reserved_cost: float


@dataclass
class ExistingReservation:
    """Container for existing reservation information."""
    reservation_id: str
    provider: str
    reservation_type: ReservationType
    resource_type: str
    instance_type: str
    region: str
    quantity: int
    term: ReservationTerm
    payment_option: PaymentOption
    start_date: datetime
    end_date: datetime
    utilization_percentage: float
    unused_hours: float
    wasted_cost: float
    status: str


class ReservedInstanceAnalyzer:
    """
    Reserved Instances and Savings Plans analyzer for multi-cloud environments.
    
    Analyzes current RI/SP utilization and provides purchase recommendations
    across AWS, Azure, GCP, and Oracle Cloud based on 365-day usage patterns.
    """
    
    def __init__(self, config: Config):
        """
        Initialize Reserved Instance Analyzer.
        
        Args:
            config: Configuration object
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Analysis parameters
        self.min_utilization_threshold = 0.7  # 70% minimum utilization
        self.analysis_period_days = 365
        self.confidence_threshold = 0.8
        
        # Initialize cloud providers
        self.providers = {}
        self._initialize_providers()
        
        # Load pricing data
        self._load_pricing_data()
    
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
    
    def _load_pricing_data(self) -> None:
        """Load pricing data for reservations (simplified)."""
        # AWS Reserved Instance discounts (approximate)
        self.aws_ri_discounts = {
            ('m5.large', '1_year', 'no_upfront'): 0.31,
            ('m5.large', '1_year', 'partial_upfront'): 0.33,
            ('m5.large', '1_year', 'all_upfront'): 0.35,
            ('m5.large', '3_year', 'no_upfront'): 0.49,
            ('m5.large', '3_year', 'partial_upfront'): 0.52,
            ('m5.large', '3_year', 'all_upfront'): 0.54,
            ('m5.xlarge', '1_year', 'no_upfront'): 0.31,
            ('m5.xlarge', '1_year', 'partial_upfront'): 0.33,
            ('m5.xlarge', '1_year', 'all_upfront'): 0.35,
            ('m5.xlarge', '3_year', 'no_upfront'): 0.49,
            ('m5.xlarge', '3_year', 'partial_upfront'): 0.52,
            ('m5.xlarge', '3_year', 'all_upfront'): 0.54,
        }
        
        # AWS Savings Plans discounts
        self.aws_sp_discounts = {
            ('compute', '1_year', 'no_upfront'): 0.17,
            ('compute', '1_year', 'partial_upfront'): 0.20,
            ('compute', '1_year', 'all_upfront'): 0.23,
            ('compute', '3_year', 'no_upfront'): 0.54,
            ('compute', '3_year', 'partial_upfront'): 0.66,
            ('compute', '3_year', 'all_upfront'): 0.72,
        }
        
        # Azure Reserved VM Instances discounts
        self.azure_ri_discounts = {
            ('Standard_D2s_v3', '1_year'): 0.31,
            ('Standard_D2s_v3', '3_year'): 0.49,
            ('Standard_D4s_v3', '1_year'): 0.31,
            ('Standard_D4s_v3', '3_year'): 0.49,
        }
        
        # GCP Committed Use Discounts
        self.gcp_cud_discounts = {
            ('n1-standard-1', '1_year'): 0.25,
            ('n1-standard-1', '3_year'): 0.52,
            ('n1-standard-2', '1_year'): 0.25,
            ('n1-standard-2', '3_year'): 0.52,
        }
    
    async def analyze_reservation_opportunities(self, 
                                               usage_data: Dict[str, Any]) -> List[ReservationRecommendation]:
        """
        Analyze reservation purchase opportunities across all providers.
        
        Args:
            usage_data: Historical usage data from data ingestion
            
        Returns:
            List of reservation recommendations
        """
        self.logger.info("Starting reservation opportunity analysis")
        
        recommendations = []
        
        for provider_name, provider_data in usage_data.get('provider_data', {}).items():
            if 'error' in provider_data:
                self.logger.error(f"Skipping {provider_name} due to data error")
                continue
            
            try:
                provider_recommendations = await self._analyze_provider_reservations(
                    provider_name, provider_data
                )
                recommendations.extend(provider_recommendations)
                
            except Exception as e:
                self.logger.error(f"Error analyzing reservations for {provider_name}: {e}")
        
        # Sort by annual savings (highest first)
        recommendations.sort(key=lambda x: x.annual_savings, reverse=True)
        
        self.logger.info(f"Generated {len(recommendations)} reservation recommendations")
        return recommendations
    
    async def _analyze_provider_reservations(self,
                                            provider_name: str,
                                            provider_data: Dict[str, Any]) -> List[ReservationRecommendation]:
        """Analyze reservation opportunities for a specific provider."""
        recommendations = []
        
        # Analyze VM/instance usage patterns
        vm_metrics = provider_data.get('vm_metrics', [])
        cost_data = provider_data.get('cost_data', {})
        
        if not vm_metrics:
            self.logger.warning(f"No VM metrics available for {provider_name}")
            return recommendations
        
        # Convert to DataFrame for analysis
        df = pd.DataFrame(vm_metrics)
        
        if df.empty:
            return recommendations
        
        # Analyze usage patterns by instance type and region
        usage_patterns = self._analyze_usage_patterns(df)
        
        # Generate recommendations based on usage patterns
        for pattern in usage_patterns:
            try:
                recommendation = await self._generate_reservation_recommendation(
                    provider_name, pattern, cost_data
                )
                
                if recommendation:
                    recommendations.append(recommendation)
                    
            except Exception as e:
                self.logger.error(f"Error generating recommendation for pattern: {e}")
        
        return recommendations
    
    def _analyze_usage_patterns(self, metrics_df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Analyze usage patterns from VM metrics."""
        patterns = []
        
        # Group by resource type, instance type, and region
        if 'resource_type' in metrics_df.columns:
            grouped = metrics_df.groupby(['resource_type', 'provider'])
            
            for (resource_type, provider), group in grouped:
                # Calculate usage statistics
                total_hours = len(group)
                unique_resources = group['resource_id'].nunique()
                
                # Calculate average utilization
                avg_utilization = group.get('value', pd.Series([0])).mean() / 100.0
                
                # Determine consistent usage (resources running most of the time)
                resource_uptime = group.groupby('resource_id').size()
                consistent_resources = (resource_uptime > total_hours * 0.7).sum()
                
                if consistent_resources > 0:
                    patterns.append({
                        'provider': provider,
                        'resource_type': resource_type,
                        'instance_count': consistent_resources,
                        'total_hours': total_hours,
                        'avg_utilization': avg_utilization,
                        'consistency_score': consistent_resources / unique_resources,
                        'region': 'us-east-1'  # Simplified - would extract from data
                    })
        
        return patterns
    
    async def _generate_reservation_recommendation(self,
                                                  provider_name: str,
                                                  usage_pattern: Dict[str, Any],
                                                  cost_data: Dict[str, Any]) -> Optional[ReservationRecommendation]:
        """Generate reservation recommendation based on usage pattern."""
        
        # Only recommend if usage is consistent enough
        if usage_pattern['consistency_score'] < self.min_utilization_threshold:
            return None
        
        instance_count = usage_pattern['instance_count']
        resource_type = usage_pattern['resource_type']
        region = usage_pattern['region']
        
        # Determine best reservation type and terms
        best_recommendation = None
        best_savings = 0
        
        # Analyze different reservation options
        reservation_options = self._get_reservation_options(provider_name, resource_type)
        
        for option in reservation_options:
            try:
                recommendation = self._calculate_reservation_savings(
                    provider_name, option, usage_pattern, cost_data
                )
                
                if recommendation and recommendation.annual_savings > best_savings:
                    best_savings = recommendation.annual_savings
                    best_recommendation = recommendation
                    
            except Exception as e:
                self.logger.error(f"Error calculating savings for option {option}: {e}")
        
        return best_recommendation
    
    def _get_reservation_options(self, provider_name: str, resource_type: str) -> List[Dict[str, Any]]:
        """Get available reservation options for a provider and resource type."""
        options = []
        
        if provider_name == 'aws':
            # AWS Reserved Instances
            options.extend([
                {
                    'type': ReservationType.RESERVED_INSTANCE,
                    'term': ReservationTerm.ONE_YEAR,
                    'payment': PaymentOption.NO_UPFRONT,
                    'instance_type': 'm5.large'  # Simplified
                },
                {
                    'type': ReservationType.RESERVED_INSTANCE,
                    'term': ReservationTerm.ONE_YEAR,
                    'payment': PaymentOption.PARTIAL_UPFRONT,
                    'instance_type': 'm5.large'
                },
                {
                    'type': ReservationType.RESERVED_INSTANCE,
                    'term': ReservationTerm.THREE_YEAR,
                    'payment': PaymentOption.ALL_UPFRONT,
                    'instance_type': 'm5.large'
                }
            ])
            
            # AWS Savings Plans
            options.extend([
                {
                    'type': ReservationType.SAVINGS_PLAN,
                    'term': ReservationTerm.ONE_YEAR,
                    'payment': PaymentOption.NO_UPFRONT,
                    'plan_type': 'compute'
                },
                {
                    'type': ReservationType.SAVINGS_PLAN,
                    'term': ReservationTerm.THREE_YEAR,
                    'payment': PaymentOption.ALL_UPFRONT,
                    'plan_type': 'compute'
                }
            ])
        
        elif provider_name == 'azure':
            # Azure Reserved VM Instances
            options.extend([
                {
                    'type': ReservationType.RESERVED_INSTANCE,
                    'term': ReservationTerm.ONE_YEAR,
                    'payment': PaymentOption.NO_UPFRONT,
                    'vm_size': 'Standard_D2s_v3'
                },
                {
                    'type': ReservationType.RESERVED_INSTANCE,
                    'term': ReservationTerm.THREE_YEAR,
                    'payment': PaymentOption.NO_UPFRONT,
                    'vm_size': 'Standard_D2s_v3'
                }
            ])
        
        elif provider_name == 'gcp':
            # GCP Committed Use Discounts
            options.extend([
                {
                    'type': ReservationType.COMMITTED_USE_DISCOUNT,
                    'term': ReservationTerm.ONE_YEAR,
                    'payment': PaymentOption.NO_UPFRONT,
                    'machine_type': 'n1-standard-1'
                },
                {
                    'type': ReservationType.COMMITTED_USE_DISCOUNT,
                    'term': ReservationTerm.THREE_YEAR,
                    'payment': PaymentOption.NO_UPFRONT,
                    'machine_type': 'n1-standard-1'
                }
            ])
        
        return options
    
    def _calculate_reservation_savings(self,
                                      provider_name: str,
                                      option: Dict[str, Any],
                                      usage_pattern: Dict[str, Any],
                                      cost_data: Dict[str, Any]) -> Optional[ReservationRecommendation]:
        """Calculate savings for a specific reservation option."""
        
        instance_count = usage_pattern['instance_count']
        resource_type = usage_pattern['resource_type']
        region = usage_pattern['region']
        
        # Get current on-demand cost (simplified)
        current_monthly_cost = self._estimate_current_cost(
            provider_name, resource_type, instance_count
        )
        
        if current_monthly_cost <= 0:
            return None
        
        # Get reservation discount
        discount = self._get_reservation_discount(provider_name, option)
        
        if discount <= 0:
            return None
        
        # Calculate reservation costs
        reserved_monthly_cost = current_monthly_cost * (1 - discount)
        annual_savings = (current_monthly_cost - reserved_monthly_cost) * 12
        
        # Calculate upfront cost based on payment option
        upfront_cost = self._calculate_upfront_cost(
            provider_name, option, current_monthly_cost
        )
        
        # Calculate break-even period
        monthly_savings = current_monthly_cost - reserved_monthly_cost
        break_even_months = upfront_cost / monthly_savings if monthly_savings > 0 else 999
        
        # Calculate confidence score
        confidence_score = self._calculate_confidence_score(usage_pattern)
        
        # Determine risk level
        risk_level = self._assess_risk_level(break_even_months, confidence_score)
        
        return ReservationRecommendation(
            provider=provider_name,
            reservation_type=option['type'],
            resource_type=resource_type,
            instance_family=option.get('instance_type', option.get('vm_size', option.get('machine_type', 'unknown'))),
            region=region,
            term=option['term'],
            payment_option=option['payment'],
            recommended_quantity=instance_count,
            upfront_cost=upfront_cost,
            monthly_cost=reserved_monthly_cost,
            annual_savings=annual_savings,
            break_even_months=int(break_even_months),
            utilization_requirement=self.min_utilization_threshold,
            confidence_score=confidence_score,
            risk_level=risk_level,
            current_on_demand_cost=current_monthly_cost,
            projected_reserved_cost=reserved_monthly_cost
        )
    
    def _estimate_current_cost(self, provider_name: str, resource_type: str, instance_count: int) -> float:
        """Estimate current monthly on-demand cost."""
        # Simplified pricing (would use actual pricing APIs in production)
        base_costs = {
            'aws': {'ec2_instance': 100},  # $100/month per instance
            'azure': {'virtual_machine': 95},  # $95/month per VM
            'gcp': {'compute_instance': 90},  # $90/month per instance
            'oracle': {'compute_instance': 85}  # $85/month per instance
        }
        
        provider_costs = base_costs.get(provider_name, {})
        unit_cost = provider_costs.get(resource_type, 100)
        
        return unit_cost * instance_count
    
    def _get_reservation_discount(self, provider_name: str, option: Dict[str, Any]) -> float:
        """Get discount percentage for a reservation option."""
        
        if provider_name == 'aws':
            if option['type'] == ReservationType.RESERVED_INSTANCE:
                key = (
                    option.get('instance_type', 'm5.large'),
                    option['term'].value,
                    option['payment'].value
                )
                return self.aws_ri_discounts.get(key, 0.0)
            
            elif option['type'] == ReservationType.SAVINGS_PLAN:
                key = (
                    option.get('plan_type', 'compute'),
                    option['term'].value,
                    option['payment'].value
                )
                return self.aws_sp_discounts.get(key, 0.0)
        
        elif provider_name == 'azure':
            key = (
                option.get('vm_size', 'Standard_D2s_v3'),
                option['term'].value
            )
            return self.azure_ri_discounts.get(key, 0.0)
        
        elif provider_name == 'gcp':
            key = (
                option.get('machine_type', 'n1-standard-1'),
                option['term'].value
            )
            return self.gcp_cud_discounts.get(key, 0.0)
        
        return 0.0
    
    def _calculate_upfront_cost(self,
                               provider_name: str,
                               option: Dict[str, Any],
                               monthly_cost: float) -> float:
        """Calculate upfront cost based on payment option."""
        
        payment_option = option['payment']
        term_months = 12 if option['term'] == ReservationTerm.ONE_YEAR else 36
        
        if payment_option == PaymentOption.ALL_UPFRONT:
            # Pay entire term upfront with additional discount
            return monthly_cost * term_months * 0.9  # 10% additional discount
        
        elif payment_option == PaymentOption.PARTIAL_UPFRONT:
            # Pay ~50% upfront
            return monthly_cost * term_months * 0.5
        
        else:  # NO_UPFRONT
            return 0.0
    
    def _calculate_confidence_score(self, usage_pattern: Dict[str, Any]) -> float:
        """Calculate confidence score for the recommendation."""
        
        consistency_score = usage_pattern['consistency_score']
        avg_utilization = usage_pattern['avg_utilization']
        
        # Base confidence on consistency and utilization
        confidence = (consistency_score + avg_utilization) / 2
        
        # Boost confidence for very consistent usage
        if consistency_score > 0.9:
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def _assess_risk_level(self, break_even_months: int, confidence_score: float) -> str:
        """Assess risk level of the recommendation."""
        
        if break_even_months > 24:  # More than 2 years to break even
            return 'high'
        
        if confidence_score < 0.7:
            return 'high'
        
        if break_even_months <= 6 and confidence_score > 0.8:
            return 'low'
        
        return 'medium'
    
    async def analyze_existing_reservations(self) -> List[ExistingReservation]:
        """
        Analyze existing reservations across all providers.
        
        Returns:
            List of existing reservation analysis
        """
        self.logger.info("Analyzing existing reservations")
        
        existing_reservations = []
        
        for provider_name, provider in self.providers.items():
            try:
                provider_reservations = await self._get_provider_reservations(provider_name, provider)
                existing_reservations.extend(provider_reservations)
                
            except Exception as e:
                self.logger.error(f"Error analyzing existing reservations for {provider_name}: {e}")
        
        return existing_reservations
    
    async def _get_provider_reservations(self,
                                        provider_name: str,
                                        provider) -> List[ExistingReservation]:
        """Get existing reservations for a specific provider."""
        reservations = []
        
        try:
            if provider_name == 'aws':
                # Get AWS Reserved Instances
                if hasattr(provider, 'get_reserved_instances'):
                    aws_ris = provider.get_reserved_instances()
                    for ri in aws_ris:
                        reservation = self._create_existing_reservation_from_aws_ri(ri)
                        reservations.append(reservation)
                
                # Get AWS Savings Plans
                if hasattr(provider, 'get_savings_plans'):
                    aws_sps = provider.get_savings_plans()
                    for sp in aws_sps:
                        reservation = self._create_existing_reservation_from_aws_sp(sp)
                        reservations.append(reservation)
            
            # Similar implementations for other providers would go here
            
        except Exception as e:
            self.logger.error(f"Error getting reservations for {provider_name}: {e}")
        
        return reservations
    
    def _create_existing_reservation_from_aws_ri(self, ri: Dict[str, Any]) -> ExistingReservation:
        """Create ExistingReservation from AWS Reserved Instance."""
        # This would be implemented based on actual AWS API response
        return ExistingReservation(
            reservation_id=ri.get('ReservedInstancesId', ''),
            provider='aws',
            reservation_type=ReservationType.RESERVED_INSTANCE,
            resource_type='ec2',
            instance_type=ri.get('InstanceType', ''),
            region=ri.get('AvailabilityZone', '')[:-1],  # Remove AZ letter
            quantity=ri.get('InstanceCount', 0),
            term=ReservationTerm.ONE_YEAR if ri.get('Duration', 0) <= 31536000 else ReservationTerm.THREE_YEAR,
            payment_option=PaymentOption.NO_UPFRONT,  # Simplified
            start_date=ri.get('Start', datetime.now()),
            end_date=ri.get('End', datetime.now()),
            utilization_percentage=0.0,  # Would need to calculate from usage data
            unused_hours=0.0,
            wasted_cost=0.0,
            status=ri.get('State', 'active')
        )
    
    def _create_existing_reservation_from_aws_sp(self, sp: Dict[str, Any]) -> ExistingReservation:
        """Create ExistingReservation from AWS Savings Plan."""
        # This would be implemented based on actual AWS API response
        return ExistingReservation(
            reservation_id=sp.get('savingsPlanId', ''),
            provider='aws',
            reservation_type=ReservationType.SAVINGS_PLAN,
            resource_type='compute',
            instance_type='',  # Savings Plans are flexible
            region='',  # Savings Plans can be region-flexible
            quantity=1,
            term=ReservationTerm.ONE_YEAR if sp.get('termDurationInSeconds', 0) <= 31536000 else ReservationTerm.THREE_YEAR,
            payment_option=PaymentOption.NO_UPFRONT,  # Simplified
            start_date=sp.get('start', datetime.now()),
            end_date=sp.get('end', datetime.now()),
            utilization_percentage=sp.get('utilizationPercentage', 0.0),
            unused_hours=0.0,
            wasted_cost=0.0,
            status=sp.get('state', 'active')
        )
    
    def generate_reservation_report(self,
                                   recommendations: List[ReservationRecommendation],
                                   existing_reservations: List[ExistingReservation]) -> Dict[str, Any]:
        """Generate comprehensive reservation analysis report."""
        
        # Calculate summary statistics
        total_potential_savings = sum(rec.annual_savings for rec in recommendations)
        total_upfront_cost = sum(rec.upfront_cost for rec in recommendations)
        
        # Group recommendations by provider
        by_provider = {}
        for rec in recommendations:
            if rec.provider not in by_provider:
                by_provider[rec.provider] = []
            by_provider[rec.provider].append(rec)
        
        # Group by reservation type
        by_type = {}
        for rec in recommendations:
            type_key = rec.reservation_type.value
            if type_key not in by_type:
                by_type[type_key] = []
            by_type[type_key].append(rec)
        
        # Analyze existing reservations
        existing_analysis = self._analyze_existing_reservations(existing_reservations)
        
        return {
            'summary': {
                'total_recommendations': len(recommendations),
                'total_potential_annual_savings': total_potential_savings,
                'total_upfront_investment': total_upfront_cost,
                'average_break_even_months': np.mean([rec.break_even_months for rec in recommendations]) if recommendations else 0,
                'existing_reservations_count': len(existing_reservations),
                'existing_reservations_utilization': existing_analysis.get('average_utilization', 0)
            },
            'recommendations_by_provider': {
                provider: {
                    'count': len(recs),
                    'potential_savings': sum(rec.annual_savings for rec in recs),
                    'upfront_cost': sum(rec.upfront_cost for rec in recs),
                    'recommendations': [rec.__dict__ for rec in recs]
                }
                for provider, recs in by_provider.items()
            },
            'recommendations_by_type': {
                res_type: {
                    'count': len(recs),
                    'potential_savings': sum(rec.annual_savings for rec in recs)
                }
                for res_type, recs in by_type.items()
            },
            'existing_reservations_analysis': existing_analysis,
            'top_recommendations': [
                rec.__dict__ for rec in sorted(recommendations,
                                             key=lambda x: x.annual_savings,
                                             reverse=True)[:10]
            ]
        }
    
    def _analyze_existing_reservations(self, existing_reservations: List[ExistingReservation]) -> Dict[str, Any]:
        """Analyze existing reservations for utilization and waste."""
        
        if not existing_reservations:
            return {'message': 'No existing reservations found'}
        
        total_reservations = len(existing_reservations)
        total_wasted_cost = sum(res.wasted_cost for res in existing_reservations)
        average_utilization = np.mean([res.utilization_percentage for res in existing_reservations])
        
        # Find underutilized reservations
        underutilized = [res for res in existing_reservations if res.utilization_percentage < 70]
        
        # Group by provider
        by_provider = {}
        for res in existing_reservations:
            if res.provider not in by_provider:
                by_provider[res.provider] = []
            by_provider[res.provider].append(res)
        
        return {
            'total_reservations': total_reservations,
            'average_utilization': average_utilization,
            'total_wasted_cost': total_wasted_cost,
            'underutilized_count': len(underutilized),
            'underutilized_reservations': [res.__dict__ for res in underutilized],
            'by_provider': {
                provider: {
                    'count': len(reservations),
                    'average_utilization': np.mean([res.utilization_percentage for res in reservations]),
                    'wasted_cost': sum(res.wasted_cost for res in reservations)
                }
                for provider, reservations in by_provider.items()
            }
        }
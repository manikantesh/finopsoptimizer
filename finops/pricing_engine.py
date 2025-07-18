"""
Real-time Pricing Engine for FinOpsOptimizer

This module provides real-time pricing data from cloud providers and supports
enterprise discounts, custom pricing, and dynamic rate updates.
"""

import logging
import asyncio
import aiohttp
import json
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import pandas as pd
from pathlib import Path

from .config import Config


class PricingSource(Enum):
    """Sources for pricing data."""
    CLOUD_PROVIDER_API = "cloud_provider_api"
    PRICING_API = "pricing_api"
    CUSTOM_RATES = "custom_rates"
    ENTERPRISE_CONTRACT = "enterprise_contract"
    CACHED = "cached"


@dataclass
class PricingData:
    """Container for pricing information."""
    provider: str
    region: str
    service: str
    resource_type: str
    instance_type: str
    pricing_unit: str  # hour, month, GB, etc.
    on_demand_price: float
    reserved_price: Optional[float] = None
    spot_price: Optional[float] = None
    enterprise_price: Optional[float] = None
    currency: str = "USD"
    effective_date: datetime = field(default_factory=datetime.now)
    source: PricingSource = PricingSource.CLOUD_PROVIDER_API
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EnterpriseDiscount:
    """Container for enterprise discount information."""
    provider: str
    service: str
    resource_type: str
    discount_type: str  # percentage, fixed_amount, custom_rate
    discount_value: float
    minimum_commitment: Optional[float] = None
    valid_from: datetime = field(default_factory=datetime.now)
    valid_until: Optional[datetime] = None
    conditions: Dict[str, Any] = field(default_factory=dict)


class RealTimePricingEngine:
    """
    Real-time pricing engine for multi-cloud cost optimization.
    
    Provides accurate, up-to-date pricing information from cloud providers
    with support for enterprise discounts and custom pricing models.
    """
    
    def __init__(self, config: Config):
        """
        Initialize Real-time Pricing Engine.
        
        Args:
            config: Configuration object
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Pricing cache
        self.pricing_cache: Dict[str, PricingData] = {}
        self.cache_ttl = 3600  # 1 hour cache TTL
        
        # Enterprise discounts
        self.enterprise_discounts: List[EnterpriseDiscount] = []
        
        # Custom pricing rates
        self.custom_rates: Dict[str, float] = {}
        
        # Load configuration
        self._load_pricing_config()
        
        # Initialize HTTP session for API calls
        self.session: Optional[aiohttp.ClientSession] = None
    
    def _load_pricing_config(self) -> None:
        """Load pricing configuration from config file."""
        pricing_config = getattr(self.config, 'pricing', {})
        
        # Load enterprise discounts
        enterprise_discounts = pricing_config.get('enterprise_discounts', [])
        for discount_data in enterprise_discounts:
            discount = EnterpriseDiscount(**discount_data)
            self.enterprise_discounts.append(discount)
        
        # Load custom rates
        self.custom_rates = pricing_config.get('custom_rates', {})
        
        # Cache settings
        self.cache_ttl = pricing_config.get('cache_ttl', 3600)
        
        self.logger.info(f"Loaded {len(self.enterprise_discounts)} enterprise discounts")
        self.logger.info(f"Loaded {len(self.custom_rates)} custom rates")
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def get_instance_pricing(self,
                                  provider: str,
                                  region: str,
                                  instance_type: str,
                                  force_refresh: bool = False) -> Optional[PricingData]:
        """
        Get real-time pricing for a specific instance type.
        
        Args:
            provider: Cloud provider (aws, azure, gcp, oracle)
            region: Cloud region
            instance_type: Instance type/size
            force_refresh: Force refresh from API (bypass cache)
            
        Returns:
            PricingData object with current pricing information
        """
        cache_key = f"{provider}:{region}:{instance_type}"
        
        # Check cache first (unless force refresh)
        if not force_refresh and cache_key in self.pricing_cache:
            cached_data = self.pricing_cache[cache_key]
            if (datetime.now() - cached_data.effective_date).seconds < self.cache_ttl:
                self.logger.debug(f"Using cached pricing for {cache_key}")
                return cached_data
        
        # Fetch real-time pricing
        try:
            pricing_data = await self._fetch_real_time_pricing(provider, region, instance_type)
            
            if pricing_data:
                # Apply enterprise discounts
                pricing_data = self._apply_enterprise_discounts(pricing_data)
                
                # Cache the result
                self.pricing_cache[cache_key] = pricing_data
                
                self.logger.debug(f"Fetched real-time pricing for {cache_key}: ${pricing_data.on_demand_price:.4f}")
                return pricing_data
            
        except Exception as e:
            self.logger.error(f"Error fetching pricing for {cache_key}: {e}")
        
        # Fallback to static pricing if real-time fails
        return self._get_fallback_pricing(provider, region, instance_type)
    
    async def _fetch_real_time_pricing(self,
                                      provider: str,
                                      region: str,
                                      instance_type: str) -> Optional[PricingData]:
        """Fetch real-time pricing from cloud provider APIs."""
        
        if provider == 'aws':
            return await self._fetch_aws_pricing(region, instance_type)
        elif provider == 'azure':
            return await self._fetch_azure_pricing(region, instance_type)
        elif provider == 'gcp':
            return await self._fetch_gcp_pricing(region, instance_type)
        elif provider == 'oracle':
            return await self._fetch_oracle_pricing(region, instance_type)
        else:
            self.logger.warning(f"Unknown provider: {provider}")
            return None
    
    async def _fetch_aws_pricing(self, region: str, instance_type: str) -> Optional[PricingData]:
        """Fetch AWS pricing using AWS Price List API."""
        try:
            # AWS Price List API endpoint
            url = "https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonEC2/current/index.json"
            
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Parse AWS pricing data (simplified)
                    pricing = self._parse_aws_pricing_data(data, region, instance_type)
                    return pricing
                else:
                    self.logger.error(f"AWS Pricing API returned status {response.status}")
                    
        except Exception as e:
            self.logger.error(f"Error fetching AWS pricing: {e}")
        
        return None
    
    def _parse_aws_pricing_data(self, data: Dict, region: str, instance_type: str) -> Optional[PricingData]:
        """Parse AWS pricing data from API response."""
        try:
            # This is a simplified parser - AWS pricing data is complex
            # In production, you'd need more sophisticated parsing
            
            products = data.get('products', {})
            terms = data.get('terms', {})
            
            # Find the product for our instance type and region
            for product_id, product in products.items():
                attributes = product.get('attributes', {})
                
                if (attributes.get('instanceType') == instance_type and
                    attributes.get('location') == self._aws_region_to_location(region)):
                    
                    # Get on-demand pricing
                    on_demand_terms = terms.get('OnDemand', {}).get(product_id, {})
                    
                    for term_id, term_data in on_demand_terms.items():
                        price_dimensions = term_data.get('priceDimensions', {})
                        
                        for dimension_id, dimension in price_dimensions.items():
                            price_per_unit = dimension.get('pricePerUnit', {})
                            usd_price = float(price_per_unit.get('USD', 0))
                            
                            if usd_price > 0:
                                return PricingData(
                                    provider='aws',
                                    region=region,
                                    service='EC2',
                                    resource_type='instance',
                                    instance_type=instance_type,
                                    pricing_unit='hour',
                                    on_demand_price=usd_price,
                                    source=PricingSource.CLOUD_PROVIDER_API,
                                    metadata={'product_id': product_id}
                                )
            
        except Exception as e:
            self.logger.error(f"Error parsing AWS pricing data: {e}")
        
        return None
    
    def _aws_region_to_location(self, region: str) -> str:
        """Convert AWS region code to location name."""
        region_mapping = {
            'us-east-1': 'US East (N. Virginia)',
            'us-west-2': 'US West (Oregon)',
            'eu-west-1': 'Europe (Ireland)',
            'ap-southeast-1': 'Asia Pacific (Singapore)',
            # Add more mappings as needed
        }
        return region_mapping.get(region, region)
    
    async def _fetch_azure_pricing(self, region: str, vm_size: str) -> Optional[PricingData]:
        """Fetch Azure pricing using Azure Retail Prices API."""
        try:
            # Azure Retail Prices API
            base_url = "https://prices.azure.com/api/retail/prices"
            
            # Filter for specific VM size and region
            filter_query = f"serviceName eq 'Virtual Machines' and armSkuName eq '{vm_size}' and armRegionName eq '{region}'"
            url = f"{base_url}?$filter={filter_query}"
            
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    items = data.get('Items', [])
                    
                    if items:
                        item = items[0]  # Take first matching item
                        
                        return PricingData(
                            provider='azure',
                            region=region,
                            service='Virtual Machines',
                            resource_type='vm',
                            instance_type=vm_size,
                            pricing_unit='hour',
                            on_demand_price=float(item.get('unitPrice', 0)),
                            currency=item.get('currencyCode', 'USD'),
                            source=PricingSource.CLOUD_PROVIDER_API,
                            metadata={'sku_id': item.get('skuId')}
                        )
                else:
                    self.logger.error(f"Azure Pricing API returned status {response.status}")
                    
        except Exception as e:
            self.logger.error(f"Error fetching Azure pricing: {e}")
        
        return None
    
    async def _fetch_gcp_pricing(self, region: str, machine_type: str) -> Optional[PricingData]:
        """Fetch GCP pricing using Cloud Billing API."""
        try:
            # GCP Cloud Billing API (requires authentication)
            # This is a simplified example - you'd need proper authentication
            
            # For now, use the public pricing calculator API (unofficial)
            # In production, use the official Cloud Billing API
            
            # Estimate based on machine type
            pricing = self._estimate_gcp_pricing(machine_type)
            
            if pricing:
                return PricingData(
                    provider='gcp',
                    region=region,
                    service='Compute Engine',
                    resource_type='instance',
                    instance_type=machine_type,
                    pricing_unit='hour',
                    on_demand_price=pricing,
                    source=PricingSource.PRICING_API,
                    metadata={'estimated': True}
                )
                
        except Exception as e:
            self.logger.error(f"Error fetching GCP pricing: {e}")
        
        return None
    
    def _estimate_gcp_pricing(self, machine_type: str) -> Optional[float]:
        """Estimate GCP pricing based on machine type."""
        # Simplified GCP pricing estimation
        # In production, use the official Cloud Billing API
        
        gcp_pricing = {
            'f1-micro': 0.0076,
            'g1-small': 0.027,
            'n1-standard-1': 0.0475,
            'n1-standard-2': 0.095,
            'n1-standard-4': 0.19,
            'n1-standard-8': 0.38,
            'n1-highmem-2': 0.1184,
            'n1-highmem-4': 0.2368,
            'n1-highmem-8': 0.4736,
            'n2-standard-2': 0.097,
            'n2-standard-4': 0.194,
            'n2-standard-8': 0.388,
        }
        
        return gcp_pricing.get(machine_type)
    
    async def _fetch_oracle_pricing(self, region: str, shape: str) -> Optional[PricingData]:
        """Fetch Oracle Cloud pricing."""
        try:
            # Oracle Cloud doesn't have a public pricing API
            # Use estimated pricing based on published rates
            
            pricing = self._estimate_oracle_pricing(shape)
            
            if pricing:
                return PricingData(
                    provider='oracle',
                    region=region,
                    service='Compute',
                    resource_type='instance',
                    instance_type=shape,
                    pricing_unit='hour',
                    on_demand_price=pricing,
                    source=PricingSource.PRICING_API,
                    metadata={'estimated': True}
                )
                
        except Exception as e:
            self.logger.error(f"Error fetching Oracle pricing: {e}")
        
        return None
    
    def _estimate_oracle_pricing(self, shape: str) -> Optional[float]:
        """Estimate Oracle Cloud pricing based on shape."""
        oracle_pricing = {
            'VM.Standard.E2.1': 0.0255,
            'VM.Standard.E2.2': 0.051,
            'VM.Standard.E2.4': 0.102,
            'VM.Standard.E2.8': 0.204,
            'VM.Standard2.1': 0.0255,
            'VM.Standard2.2': 0.051,
            'VM.Standard2.4': 0.102,
            'VM.Standard2.8': 0.204,
            'VM.Standard.A1.Flex': 0.01,  # Per OCPU hour
        }
        
        return oracle_pricing.get(shape)
    
    def _get_fallback_pricing(self, provider: str, region: str, instance_type: str) -> Optional[PricingData]:
        """Get fallback pricing when real-time pricing fails."""
        # Use static pricing as fallback
        static_pricing = self._get_static_pricing(provider, instance_type)
        
        if static_pricing:
            return PricingData(
                provider=provider,
                region=region,
                service='compute',
                resource_type='instance',
                instance_type=instance_type,
                pricing_unit='hour',
                on_demand_price=static_pricing,
                source=PricingSource.CACHED,
                metadata={'fallback': True}
            )
        
        return None
    
    def _get_static_pricing(self, provider: str, instance_type: str) -> Optional[float]:
        """Get static pricing as fallback."""
        # This uses the existing static pricing data as fallback
        static_pricing_maps = {
            'aws': {
                't3.nano': 0.0052, 't3.micro': 0.0104, 't3.small': 0.0208,
                't3.medium': 0.0416, 't3.large': 0.0832, 't3.xlarge': 0.1664,
                'm5.large': 0.096, 'm5.xlarge': 0.192, 'm5.2xlarge': 0.384,
                'c5.large': 0.085, 'c5.xlarge': 0.17, 'r5.large': 0.126,
            },
            'azure': {
                'Standard_B1s': 0.0104, 'Standard_B2s': 0.0416,
                'Standard_D2s_v3': 0.096, 'Standard_D4s_v3': 0.192,
                'Standard_E2s_v3': 0.126, 'Standard_E4s_v3': 0.252,
            },
            'gcp': {
                'f1-micro': 0.0076, 'g1-small': 0.027,
                'n1-standard-1': 0.0475, 'n1-standard-2': 0.095,
                'n1-highmem-2': 0.1184, 'n1-highmem-4': 0.2368,
            },
            'oracle': {
                'VM.Standard.E2.1': 0.0255, 'VM.Standard.E2.2': 0.051,
                'VM.Standard2.1': 0.0255, 'VM.Standard2.2': 0.051,
            }
        }
        
        provider_pricing = static_pricing_maps.get(provider, {})
        return provider_pricing.get(instance_type)
    
    def _apply_enterprise_discounts(self, pricing_data: PricingData) -> PricingData:
        """Apply enterprise discounts to pricing data."""
        
        # Find applicable discounts
        applicable_discounts = []
        
        for discount in self.enterprise_discounts:
            if self._is_discount_applicable(discount, pricing_data):
                applicable_discounts.append(discount)
        
        if not applicable_discounts:
            return pricing_data
        
        # Apply discounts (use the best discount)
        best_discount = max(applicable_discounts, key=lambda d: d.discount_value)
        
        if best_discount.discount_type == 'percentage':
            discount_multiplier = 1 - (best_discount.discount_value / 100)
            pricing_data.enterprise_price = pricing_data.on_demand_price * discount_multiplier
        
        elif best_discount.discount_type == 'fixed_amount':
            pricing_data.enterprise_price = max(0, pricing_data.on_demand_price - best_discount.discount_value)
        
        elif best_discount.discount_type == 'custom_rate':
            pricing_data.enterprise_price = best_discount.discount_value
        
        self.logger.debug(f"Applied enterprise discount: {pricing_data.on_demand_price:.4f} -> {pricing_data.enterprise_price:.4f}")
        
        return pricing_data
    
    def _is_discount_applicable(self, discount: EnterpriseDiscount, pricing_data: PricingData) -> bool:
        """Check if a discount is applicable to the pricing data."""
        
        # Check provider match
        if discount.provider != pricing_data.provider:
            return False
        
        # Check service match
        if discount.service != 'all' and discount.service != pricing_data.service:
            return False
        
        # Check resource type match
        if discount.resource_type != 'all' and discount.resource_type != pricing_data.resource_type:
            return False
        
        # Check validity period
        now = datetime.now()
        if now < discount.valid_from:
            return False
        
        if discount.valid_until and now > discount.valid_until:
            return False
        
        # Check conditions (if any)
        # This could include minimum spend, specific regions, etc.
        
        return True
    
    async def get_storage_pricing(self,
                                 provider: str,
                                 region: str,
                                 storage_type: str,
                                 force_refresh: bool = False) -> Optional[PricingData]:
        """Get real-time storage pricing."""
        
        cache_key = f"{provider}:{region}:storage:{storage_type}"
        
        # Check cache first
        if not force_refresh and cache_key in self.pricing_cache:
            cached_data = self.pricing_cache[cache_key]
            if (datetime.now() - cached_data.effective_date).seconds < self.cache_ttl:
                return cached_data
        
        # Fetch storage pricing
        try:
            pricing_data = await self._fetch_storage_pricing(provider, region, storage_type)
            
            if pricing_data:
                pricing_data = self._apply_enterprise_discounts(pricing_data)
                self.pricing_cache[cache_key] = pricing_data
                return pricing_data
                
        except Exception as e:
            self.logger.error(f"Error fetching storage pricing for {cache_key}: {e}")
        
        # Fallback to static pricing
        return self._get_fallback_storage_pricing(provider, region, storage_type)
    
    async def _fetch_storage_pricing(self, provider: str, region: str, storage_type: str) -> Optional[PricingData]:
        """Fetch storage pricing from cloud provider APIs."""
        
        # Simplified storage pricing - would use actual APIs in production
        storage_pricing = {
            'aws': {
                'gp2': 0.10, 'gp3': 0.08, 'io1': 0.125, 'st1': 0.045, 'sc1': 0.025
            },
            'azure': {
                'Standard_LRS': 0.0208, 'Standard_GRS': 0.0416, 'Premium_LRS': 0.1472
            },
            'gcp': {
                'pd-standard': 0.04, 'pd-ssd': 0.17, 'pd-balanced': 0.10
            },
            'oracle': {
                'block': 0.0255, 'object': 0.0255
            }
        }
        
        provider_pricing = storage_pricing.get(provider, {})
        price = provider_pricing.get(storage_type)
        
        if price:
            return PricingData(
                provider=provider,
                region=region,
                service='storage',
                resource_type='volume',
                instance_type=storage_type,
                pricing_unit='GB-month',
                on_demand_price=price,
                source=PricingSource.PRICING_API
            )
        
        return None
    
    def _get_fallback_storage_pricing(self, provider: str, region: str, storage_type: str) -> Optional[PricingData]:
        """Get fallback storage pricing."""
        # Use static pricing as fallback
        price = self._get_static_storage_pricing(provider, storage_type)
        
        if price:
            return PricingData(
                provider=provider,
                region=region,
                service='storage',
                resource_type='volume',
                instance_type=storage_type,
                pricing_unit='GB-month',
                on_demand_price=price,
                source=PricingSource.CACHED,
                metadata={'fallback': True}
            )
        
        return None
    
    def _get_static_storage_pricing(self, provider: str, storage_type: str) -> Optional[float]:
        """Get static storage pricing."""
        static_storage_pricing = {
            'aws': {'gp2': 0.10, 'gp3': 0.08, 'io1': 0.125},
            'azure': {'Standard_LRS': 0.0208, 'Premium_LRS': 0.1472},
            'gcp': {'pd-standard': 0.04, 'pd-ssd': 0.17},
            'oracle': {'block': 0.0255}
        }
        
        provider_pricing = static_storage_pricing.get(provider, {})
        return provider_pricing.get(storage_type)
    
    def add_enterprise_discount(self, discount: EnterpriseDiscount) -> None:
        """Add an enterprise discount."""
        self.enterprise_discounts.append(discount)
        self.logger.info(f"Added enterprise discount for {discount.provider} {discount.service}")
    
    def add_custom_rate(self, key: str, rate: float) -> None:
        """Add a custom pricing rate."""
        self.custom_rates[key] = rate
        self.logger.info(f"Added custom rate: {key} = ${rate:.4f}")
    
    def clear_cache(self) -> None:
        """Clear the pricing cache."""
        self.pricing_cache.clear()
        self.logger.info("Pricing cache cleared")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get pricing cache statistics."""
        now = datetime.now()
        fresh_entries = 0
        stale_entries = 0
        
        for cache_key, pricing_data in self.pricing_cache.items():
            age_seconds = (now - pricing_data.effective_date).seconds
            if age_seconds < self.cache_ttl:
                fresh_entries += 1
            else:
                stale_entries += 1
        
        return {
            'total_entries': len(self.pricing_cache),
            'fresh_entries': fresh_entries,
            'stale_entries': stale_entries,
            'cache_ttl': self.cache_ttl,
            'hit_rate': fresh_entries / len(self.pricing_cache) if self.pricing_cache else 0
        }


# Utility functions for pricing configuration

def create_enterprise_discount(provider: str,
                              service: str,
                              discount_percentage: float,
                              valid_from: Optional[datetime] = None,
                              valid_until: Optional[datetime] = None) -> EnterpriseDiscount:
    """Create an enterprise discount configuration."""
    return EnterpriseDiscount(
        provider=provider,
        service=service,
        resource_type='all',
        discount_type='percentage',
        discount_value=discount_percentage,
        valid_from=valid_from or datetime.now(),
        valid_until=valid_until
    )


def load_enterprise_discounts_from_file(file_path: str) -> List[EnterpriseDiscount]:
    """Load enterprise discounts from a JSON file."""
    discounts = []
    
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        for discount_data in data.get('discounts', []):
            # Convert date strings to datetime objects
            if 'valid_from' in discount_data:
                discount_data['valid_from'] = datetime.fromisoformat(discount_data['valid_from'])
            if 'valid_until' in discount_data:
                discount_data['valid_until'] = datetime.fromisoformat(discount_data['valid_until'])
            
            discount = EnterpriseDiscount(**discount_data)
            discounts.append(discount)
        
        return discounts
        
    except Exception as e:
        logging.error(f"Error loading enterprise discounts from {file_path}: {e}")
        return []
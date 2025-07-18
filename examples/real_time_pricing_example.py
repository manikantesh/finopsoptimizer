#!/usr/bin/env python3
"""
Real-Time Pricing and Enterprise Discounts Example

This example demonstrates how to use the real-time pricing engine with
enterprise discounts and custom pricing configurations.
"""

import asyncio
import json
from datetime import datetime, timedelta
from pathlib import Path

from finops import Config
from finops.pricing_engine import (
    RealTimePricingEngine, 
    EnterpriseDiscount, 
    create_enterprise_discount,
    PricingSource
)
from finops.vm_rightsizing import VMRightsizingAnalyzer


async def main():
    """Main function demonstrating real-time pricing features."""
    
    print("🚀 FinOpsOptimizer - Real-Time Pricing & Enterprise Discounts Demo")
    print("=" * 70)
    
    # Step 1: Create configuration with enterprise discounts
    print("\n📋 Step 1: Setting up Configuration with Enterprise Discounts")
    config = create_sample_config_with_discounts()
    print("✅ Configuration created with enterprise discounts")
    
    # Step 2: Initialize pricing engine
    print("\n💰 Step 2: Initializing Real-Time Pricing Engine")
    
    async with RealTimePricingEngine(config) as pricing_engine:
        
        # Step 3: Check real-time pricing for various instance types
        print("\n🔍 Step 3: Checking Real-Time Pricing")
        
        instance_types_to_check = [
            ('aws', 'us-east-1', 'm5.large'),
            ('aws', 'us-east-1', 'c5.xlarge'),
            ('azure', 'eastus', 'Standard_D2s_v3'),
            ('gcp', 'us-central1', 'n1-standard-2'),
            ('oracle', 'us-ashburn-1', 'VM.Standard.E2.2'),
        ]
        
        pricing_results = []
        
        for provider, region, instance_type in instance_types_to_check:
            try:
                print(f"\n🔍 Checking pricing for {instance_type} in {region} ({provider.upper()})")
                
                pricing_data = await pricing_engine.get_instance_pricing(
                    provider=provider,
                    region=region,
                    instance_type=instance_type,
                    force_refresh=True
                )
                
                if pricing_data:
                    print(f"   On-Demand: ${pricing_data.on_demand_price:.4f}/{pricing_data.pricing_unit}")
                    
                    if pricing_data.enterprise_price:
                        savings = pricing_data.on_demand_price - pricing_data.enterprise_price
                        savings_pct = (savings / pricing_data.on_demand_price) * 100
                        print(f"   Enterprise: ${pricing_data.enterprise_price:.4f}/{pricing_data.pricing_unit}")
                        print(f"   💰 Savings: ${savings:.4f} ({savings_pct:.1f}%)")
                    
                    print(f"   Source: {pricing_data.source.value}")
                    
                    # Calculate monthly cost
                    monthly_cost = pricing_data.enterprise_price or pricing_data.on_demand_price
                    monthly_total = monthly_cost * 24 * 30
                    print(f"   📊 Monthly Cost: ${monthly_total:.2f}")
                    
                    pricing_results.append({
                        'provider': provider,
                        'region': region,
                        'instance_type': instance_type,
                        'on_demand_price': pricing_data.on_demand_price,
                        'enterprise_price': pricing_data.enterprise_price,
                        'monthly_cost': monthly_total,
                        'source': pricing_data.source.value
                    })
                else:
                    print(f"   ❌ Could not retrieve pricing")
                    
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        # Step 4: Demonstrate storage pricing
        print("\n💾 Step 4: Checking Storage Pricing")
        
        storage_types_to_check = [
            ('aws', 'us-east-1', 'gp3'),
            ('azure', 'eastus', 'Premium_LRS'),
            ('gcp', 'us-central1', 'pd-ssd'),
            ('oracle', 'us-ashburn-1', 'block'),
        ]
        
        for provider, region, storage_type in storage_types_to_check:
            try:
                print(f"\n💾 Checking storage pricing for {storage_type} in {region} ({provider.upper()})")
                
                storage_pricing = await pricing_engine.get_storage_pricing(
                    provider=provider,
                    region=region,
                    storage_type=storage_type
                )
                
                if storage_pricing:
                    price = storage_pricing.enterprise_price or storage_pricing.on_demand_price
                    print(f"   Price: ${price:.4f}/{storage_pricing.pricing_unit}")
                    print(f"   📊 1TB Monthly Cost: ${price * 1024:.2f}")
                else:
                    print(f"   ❌ Could not retrieve storage pricing")
                    
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        # Step 5: Show cache statistics
        print("\n📈 Step 5: Pricing Cache Statistics")
        cache_stats = pricing_engine.get_cache_stats()
        print(f"   Total Entries: {cache_stats['total_entries']}")
        print(f"   Fresh Entries: {cache_stats['fresh_entries']}")
        print(f"   Hit Rate: {cache_stats['hit_rate']:.1%}")
        print(f"   Cache TTL: {cache_stats['cache_ttl']} seconds")
        
        # Step 6: Demonstrate adding custom enterprise discounts
        print("\n🏢 Step 6: Adding Custom Enterprise Discounts")
        
        # Add a new enterprise discount
        new_discount = EnterpriseDiscount(
            provider='aws',
            service='EC2',
            resource_type='instance',
            discount_type='percentage',
            discount_value=25.0,  # 25% discount
            valid_from=datetime.now(),
            valid_until=datetime.now() + timedelta(days=365)
        )
        
        pricing_engine.add_enterprise_discount(new_discount)
        print("   ✅ Added 25% enterprise discount for AWS EC2 instances")
        
        # Test the new discount
        print("\n   🧪 Testing new discount on m5.large:")
        pricing_data = await pricing_engine.get_instance_pricing(
            provider='aws',
            region='us-east-1',
            instance_type='m5.large',
            force_refresh=True
        )
        
        if pricing_data and pricing_data.enterprise_price:
            savings = pricing_data.on_demand_price - pricing_data.enterprise_price
            savings_pct = (savings / pricing_data.on_demand_price) * 100
            print(f"   On-Demand: ${pricing_data.on_demand_price:.4f}")
            print(f"   Enterprise: ${pricing_data.enterprise_price:.4f}")
            print(f"   💰 New Savings: ${savings:.4f} ({savings_pct:.1f}%)")
        
        # Step 7: Demonstrate rightsizing with real-time pricing
        print("\n🔧 Step 7: VM Rightsizing with Real-Time Pricing")
        
        # Create sample VM data for rightsizing analysis
        sample_vm_data = create_sample_vm_data()
        
        print("   📊 Analyzing rightsizing with real-time pricing...")
        
        # This would normally use the VMRightsizingAnalyzer
        # For demo purposes, we'll show a simplified example
        for vm in sample_vm_data:
            current_pricing = await pricing_engine.get_instance_pricing(
                provider=vm['provider'],
                region=vm['region'],
                instance_type=vm['current_type']
            )
            
            recommended_pricing = await pricing_engine.get_instance_pricing(
                provider=vm['provider'],
                region=vm['region'],
                instance_type=vm['recommended_type']
            )
            
            if current_pricing and recommended_pricing:
                current_monthly = (current_pricing.enterprise_price or current_pricing.on_demand_price) * 24 * 30
                recommended_monthly = (recommended_pricing.enterprise_price or recommended_pricing.on_demand_price) * 24 * 30
                monthly_savings = current_monthly - recommended_monthly
                
                print(f"\n   🖥️  VM: {vm['vm_id']} ({vm['provider'].upper()})")
                print(f"      Current: {vm['current_type']} → ${current_monthly:.2f}/month")
                print(f"      Recommended: {vm['recommended_type']} → ${recommended_monthly:.2f}/month")
                print(f"      💰 Monthly Savings: ${monthly_savings:.2f}")
        
        # Step 8: Generate pricing report
        print("\n📊 Step 8: Generating Pricing Report")
        
        report = generate_pricing_report(pricing_results, cache_stats)
        
        # Save report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"pricing_report_{timestamp}.json"
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"   📄 Pricing report saved to: {report_file}")
        
        # Step 9: Show cost comparison
        print("\n💡 Step 9: Cost Comparison Summary")
        
        total_on_demand = sum(r['on_demand_price'] * 24 * 30 for r in pricing_results)
        total_enterprise = sum((r['enterprise_price'] or r['on_demand_price']) * 24 * 30 for r in pricing_results)
        total_savings = total_on_demand - total_enterprise
        savings_percentage = (total_savings / total_on_demand) * 100 if total_on_demand > 0 else 0
        
        print(f"   📊 Total Monthly On-Demand Cost: ${total_on_demand:.2f}")
        print(f"   🏢 Total Monthly Enterprise Cost: ${total_enterprise:.2f}")
        print(f"   💰 Total Monthly Savings: ${total_savings:.2f} ({savings_percentage:.1f}%)")
        print(f"   📈 Annual Savings Projection: ${total_savings * 12:.2f}")
    
    # Summary
    print("\n🎉 Real-Time Pricing Demo Completed!")
    print("=" * 70)
    print("Key Features Demonstrated:")
    print("✅ Real-time pricing from cloud provider APIs")
    print("✅ Enterprise discount application")
    print("✅ Custom pricing configurations")
    print("✅ Storage pricing analysis")
    print("✅ Pricing cache management")
    print("✅ VM rightsizing with accurate costs")
    print("✅ Comprehensive cost reporting")
    print("\nNext Steps:")
    print("1. Configure your enterprise discounts in finops_config.yml")
    print("2. Set up real-time pricing for your cloud providers")
    print("3. Run rightsizing analysis with accurate pricing")
    print("4. Monitor and optimize your cloud costs continuously")


def create_sample_config_with_discounts():
    """Create a sample configuration with enterprise discounts."""
    config = Config()
    
    # Enable all providers
    config.aws.enabled = True
    config.azure.enabled = True
    config.gcp.enabled = True
    config.oracle.enabled = True
    
    # Configure pricing settings
    config.pricing.enable_real_time_pricing = True
    config.pricing.cache_ttl = 3600  # 1 hour
    config.pricing.fallback_to_static = True
    
    # Add enterprise discounts
    config.pricing.enterprise_discounts = [
        {
            'provider': 'aws',
            'service': 'all',
            'resource_type': 'all',
            'discount_type': 'percentage',
            'discount_value': 15.0,  # 15% discount
            'valid_from': datetime.now().isoformat(),
            'valid_until': (datetime.now() + timedelta(days=365)).isoformat()
        },
        {
            'provider': 'azure',
            'service': 'Virtual Machines',
            'resource_type': 'vm',
            'discount_type': 'percentage',
            'discount_value': 20.0,  # 20% discount
            'valid_from': datetime.now().isoformat(),
            'valid_until': (datetime.now() + timedelta(days=365)).isoformat()
        },
        {
            'provider': 'gcp',
            'service': 'Compute Engine',
            'resource_type': 'instance',
            'discount_type': 'percentage',
            'discount_value': 18.0,  # 18% discount
            'valid_from': datetime.now().isoformat(),
            'valid_until': (datetime.now() + timedelta(days=365)).isoformat()
        }
    ]
    
    # Add custom rates
    config.pricing.custom_rates = {
        'aws:us-east-1:t3.nano': 0.004,  # Custom rate for t3.nano
        'azure:eastus:Standard_B1s': 0.008,  # Custom rate for B1s
    }
    
    return config


def create_sample_vm_data():
    """Create sample VM data for rightsizing demonstration."""
    return [
        {
            'vm_id': 'i-1234567890abcdef0',
            'provider': 'aws',
            'region': 'us-east-1',
            'current_type': 'm5.xlarge',
            'recommended_type': 'm5.large',
            'cpu_utilization': 25.0,
            'memory_utilization': 30.0
        },
        {
            'vm_id': 'vm-azure-001',
            'provider': 'azure',
            'region': 'eastus',
            'current_type': 'Standard_D4s_v3',
            'recommended_type': 'Standard_D2s_v3',
            'cpu_utilization': 20.0,
            'memory_utilization': 35.0
        },
        {
            'vm_id': 'gcp-instance-001',
            'provider': 'gcp',
            'region': 'us-central1',
            'current_type': 'n1-standard-4',
            'recommended_type': 'n1-standard-2',
            'cpu_utilization': 15.0,
            'memory_utilization': 25.0
        }
    ]


def generate_pricing_report(pricing_results, cache_stats):
    """Generate a comprehensive pricing report."""
    
    total_on_demand = sum(r['on_demand_price'] * 24 * 30 for r in pricing_results)
    total_enterprise = sum((r['enterprise_price'] or r['on_demand_price']) * 24 * 30 for r in pricing_results)
    total_savings = total_on_demand - total_enterprise
    
    return {
        'report_generated': datetime.now().isoformat(),
        'summary': {
            'total_instances_analyzed': len(pricing_results),
            'total_monthly_on_demand_cost': total_on_demand,
            'total_monthly_enterprise_cost': total_enterprise,
            'total_monthly_savings': total_savings,
            'savings_percentage': (total_savings / total_on_demand) * 100 if total_on_demand > 0 else 0,
            'annual_savings_projection': total_savings * 12
        },
        'pricing_details': pricing_results,
        'cache_statistics': cache_stats,
        'recommendations': [
            {
                'type': 'enterprise_discounts',
                'description': 'Configure enterprise discounts to maximize savings',
                'potential_impact': 'High'
            },
            {
                'type': 'real_time_pricing',
                'description': 'Enable real-time pricing for accurate cost calculations',
                'potential_impact': 'Medium'
            },
            {
                'type': 'pricing_cache',
                'description': 'Optimize cache TTL for balance between accuracy and performance',
                'potential_impact': 'Low'
            }
        ]
    }


if __name__ == "__main__":
    # Run the real-time pricing demo
    asyncio.run(main())
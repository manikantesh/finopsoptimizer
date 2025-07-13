#!/usr/bin/env python3
"""
Advanced usage example for FinOpsOptimizer.
"""

from finops import FinOpsOptimizer, load_config
from datetime import datetime, timedelta
import json


def main():
    """Advanced usage example."""
    print("FinOpsOptimizer - Advanced Usage Example")
    print("=" * 50)
    
    # Load configuration
    config = load_config()
    
    # Initialize optimizer
    optimizer = FinOpsOptimizer(config)
    
    # 1. Custom cost analysis with specific date range
    print("\n1. Custom Cost Analysis...")
    end_date = datetime.now()
    start_date = end_date - timedelta(days=60)  # 60 days
    
    cost_results = optimizer.analyze_costs(start_date, end_date)
    
    print(f"   Analysis Period: {start_date.date()} to {end_date.date()}")
    print(f"   Total Cost: ${cost_results['summary']['total_cost']:.2f}")
    
    # 2. Detailed cost allocation
    print("\n2. Cost Allocation Analysis...")
    allocation_rules = {
        'method': 'tag_based',
        'tags': ['Environment', 'Project', 'Team'],
        'departments': ['Engineering', 'Marketing', 'Sales'],
        'projects': ['WebApp', 'MobileApp', 'DataPipeline']
    }
    
    allocation_results = optimizer.allocate_costs(allocation_rules)
    print(f"   Allocation Method: {allocation_results['allocation_method']}")
    
    # 3. Rightsizing analysis
    print("\n3. Rightsizing Analysis...")
    rightsizing_analyzer = optimizer.rightsizing_analyzer
    
    for provider_name, provider in optimizer.providers.items():
        print(f"   Analyzing {provider_name.upper()}...")
        rightsizing_recs = rightsizing_analyzer.analyze_provider(
            provider, cost_results.get(provider_name, {})
        )
        print(f"   Found {len(rightsizing_recs)} rightsizing opportunities")
    
    # 4. Autoscaling optimization
    print("\n4. Autoscaling Optimization...")
    autoscaling_optimizer = optimizer.autoscaling_optimizer
    
    for provider_name, provider in optimizer.providers.items():
        print(f"   Analyzing {provider_name.upper()} autoscaling...")
        autoscaling_recs = autoscaling_optimizer.analyze_provider(
            provider, cost_results.get(provider_name, {})
        )
        print(f"   Found {len(autoscaling_recs)} autoscaling optimization opportunities")
    
    # 5. Cost forecasting with different scenarios
    print("\n5. Advanced Cost Forecasting...")
    
    # Base forecast
    base_forecast = optimizer.forecast_costs(30, include_recommendations=False)
    base_total = base_forecast['total_forecast'].get('total_forecast', 0)
    
    # Optimized forecast
    optimized_forecast = optimizer.forecast_costs(30, include_recommendations=True)
    optimized_total = optimized_forecast['total_forecast'].get('total_forecast', 0)
    
    print(f"   Base Forecast (30 days): ${base_total:.2f}")
    print(f"   Optimized Forecast (30 days): ${optimized_total:.2f}")
    print(f"   Potential Savings: ${base_total - optimized_total:.2f}")
    
    # 6. Generate multiple report formats
    print("\n6. Generating Multiple Report Formats...")
    
    # HTML report
    html_report = optimizer.generate_report(
        cost_data=cost_results,
        recommendations=optimizer.recommendations,
        report_type="comprehensive",
        output_format="html"
    )
    print(f"   HTML Report: {html_report}")
    
    # JSON report
    json_report = optimizer.generate_report(
        cost_data=cost_results,
        recommendations=optimizer.recommendations,
        report_type="comprehensive",
        output_format="json"
    )
    print(f"   JSON Report: {json_report}")
    
    # 7. Save detailed results
    print("\n7. Saving Detailed Results...")
    
    detailed_results = {
        'timestamp': datetime.now().isoformat(),
        'cost_analysis': cost_results,
        'allocation_results': allocation_results,
        'base_forecast': base_forecast,
        'optimized_forecast': optimized_forecast,
        'recommendations': optimizer.recommendations,
        'provider_status': optimizer.get_provider_status(),
        'credentials_status': optimizer.validate_credentials()
    }
    
    with open('detailed_results.json', 'w') as f:
        json.dump(detailed_results, f, indent=2, default=str)
    
    print("   Detailed results saved to: detailed_results.json")
    
    # 8. Performance metrics
    print("\n8. Performance Metrics...")
    
    total_recommendations = len(optimizer.recommendations)
    total_savings = sum(r.get('potential_savings', 0) for r in optimizer.recommendations)
    providers_analyzed = len(optimizer.providers)
    
    print(f"   Total Recommendations: {total_recommendations}")
    print(f"   Total Potential Savings: ${total_savings:.2f}")
    print(f"   Providers Analyzed: {providers_analyzed}")
    print(f"   Average Savings per Recommendation: ${total_savings/total_recommendations:.2f}" if total_recommendations > 0 else "   No recommendations found")
    
    print("\nAdvanced example completed successfully!")


if __name__ == "__main__":
    main() 
#!/usr/bin/env python3
"""
Basic usage example for FinOpsOptimizer.
"""

from finops import FinOpsOptimizer, load_config


def main():
    """Basic usage example."""
    print("FinOpsOptimizer - Basic Usage Example")
    print("=" * 50)
    
    # Load configuration
    config = load_config()
    
    # Initialize optimizer
    optimizer = FinOpsOptimizer(config)
    
    # Check provider status
    print("\n1. Checking provider status...")
    provider_status = optimizer.get_provider_status()
    for provider, connected in provider_status.items():
        status = "Connected" if connected else "Disconnected"
        print(f"   {provider.upper()}: {status}")
    
    # Analyze costs
    print("\n2. Analyzing costs...")
    cost_results = optimizer.analyze_costs()
    
    print(f"   Total Cost: ${cost_results['summary']['total_cost']:.2f}")
    print(f"   Providers Analyzed: {', '.join(cost_results['summary']['providers_analyzed'])}")
    
    # Generate recommendations
    print("\n3. Generating optimization recommendations...")
    recommendations = optimizer.generate_recommendations()
    
    print(f"   Total Recommendations: {len(recommendations)}")
    if recommendations:
        total_savings = sum(r.get('potential_savings', 0) for r in recommendations)
        print(f"   Total Potential Savings: ${total_savings:.2f}")
        
        print("\n   Top 3 Recommendations:")
        for i, rec in enumerate(recommendations[:3], 1):
            print(f"   {i}. {rec['description']}")
            print(f"      Potential Savings: ${rec.get('potential_savings', 0):.2f}")
    
    # Generate forecast
    print("\n4. Forecasting costs...")
    forecast_results = optimizer.forecast_costs(30)
    
    total_forecast = forecast_results['total_forecast'].get('total_forecast', 0)
    print(f"   Next 30 Days Forecast: ${total_forecast:.2f}")
    
    # Generate report
    print("\n5. Generating report...")
    report_path = optimizer.generate_report()
    print(f"   Report generated: {report_path}")
    
    print("\nExample completed successfully!")


if __name__ == "__main__":
    main() 
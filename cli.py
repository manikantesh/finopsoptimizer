#!/usr/bin/env python3
"""
Command-line interface for FinOpsOptimizer.
"""

import click
import logging
import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
import json

from finops import FinOpsOptimizer, load_config


@click.group()
@click.option('--config', '-c', help='Path to configuration file')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
@click.pass_context
def cli(ctx, config, verbose):
    """FinOpsOptimizer - Multi-cloud cost optimization toolkit."""
    # Setup logging
    log_level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Load configuration
    if config:
        ctx.obj = load_config(config)
    else:
        ctx.obj = load_config()
    
    # Store config in context
    ctx.ensure_object(dict)
    ctx.obj['config'] = ctx.obj


@cli.command()
@click.option('--days', '-d', default=30, help='Number of days to analyze')
@click.option('--output', '-o', help='Output file path')
@click.pass_context
def analyze(ctx, days, output):
    """Analyze costs across all cloud providers."""
    try:
        optimizer = FinOpsOptimizer(ctx.obj['config'])
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        click.echo(f"Analyzing costs from {start_date.date()} to {end_date.date()}")
        
        # Analyze costs
        results = optimizer.analyze_costs(start_date, end_date)
        
        # Display results
        click.echo("\n=== Cost Analysis Results ===")
        click.echo(f"Total Cost: ${results['summary']['total_cost']:.2f}")
        click.echo(f"Providers Analyzed: {', '.join(results['summary']['providers_analyzed'])}")
        
        for provider_name, provider_data in results.items():
            if provider_name == 'summary':
                continue
            
            if 'error' in provider_data:
                click.echo(f"\n{provider_name.upper()}: Error - {provider_data['error']}")
            else:
                click.echo(f"\n{provider_name.upper()}:")
                click.echo(f"  Total Cost: ${provider_data.get('total_cost', 0):.2f}")
                
                # Show service breakdown
                service_breakdown = provider_data.get('service_breakdown', {})
                if service_breakdown:
                    click.echo("  Top Services:")
                    for service, cost in sorted(service_breakdown.items(), key=lambda x: x[1], reverse=True)[:5]:
                        click.echo(f"    {service}: ${cost:.2f}")
        
        # Save results if output specified
        if output:
            with open(output, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            click.echo(f"\nResults saved to: {output}")
            
    except Exception as e:
        click.echo(f"Error during analysis: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--output', '-o', help='Output file path')
@click.pass_context
def optimize(ctx, output):
    """Run complete optimization pipeline."""
    try:
        optimizer = FinOpsOptimizer(ctx.obj['config'])
        
        click.echo("Running complete optimization pipeline...")
        
        # Run optimization
        results = optimizer.optimize_all()
        
        # Display results
        click.echo("\n=== Optimization Results ===")
        summary = results['summary']
        click.echo(f"Total Recommendations: {summary['total_recommendations']}")
        click.echo(f"Total Potential Savings: ${summary['total_potential_savings']:.2f}")
        click.echo(f"Providers Analyzed: {', '.join(summary['providers_analyzed'])}")
        
        # Show top recommendations
        recommendations = results['recommendations']
        if recommendations:
            click.echo("\nTop Recommendations:")
            for i, rec in enumerate(recommendations[:5], 1):
                click.echo(f"{i}. {rec['description']}")
                click.echo(f"   Potential Savings: ${rec.get('potential_savings', 0):.2f}")
                click.echo(f"   Priority: {rec.get('priority', 'medium')}")
                click.echo()
        
        # Show report path
        if results.get('report_path'):
            click.echo(f"Report generated: {results['report_path']}")
        
        # Save results if output specified
        if output:
            with open(output, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            click.echo(f"Results saved to: {output}")
            
    except Exception as e:
        click.echo(f"Error during optimization: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--days', '-d', default=30, help='Number of days to forecast')
@click.option('--output', '-o', help='Output file path')
@click.pass_context
def forecast(ctx, days, output):
    """Forecast future costs."""
    try:
        optimizer = FinOpsOptimizer(ctx.obj['config'])
        
        click.echo(f"Forecasting costs for {days} days...")
        
        # Analyze costs first
        cost_data = optimizer.analyze_costs()
        
        # Generate forecast
        forecast_results = optimizer.forecast_costs(days)
        
        # Display results
        click.echo("\n=== Cost Forecast Results ===")
        total_forecast = forecast_results['total_forecast']
        click.echo(f"Total Forecast: ${total_forecast.get('total_forecast', 0):.2f}")
        click.echo(f"Forecast Period: {days} days")
        
        # Show provider forecasts
        for provider_name, provider_forecast in forecast_results['provider_forecasts'].items():
            if 'error' not in provider_forecast:
                click.echo(f"\n{provider_name.upper()}:")
                click.echo(f"  Forecast: ${provider_forecast.get('total_forecast', 0):.2f}")
                
                # Show trend analysis
                trend_analysis = provider_forecast.get('trend_analysis', {})
                if trend_analysis:
                    click.echo(f"  Trend: {trend_analysis.get('trend_direction', 'unknown')}")
                    click.echo(f"  Volatility: {trend_analysis.get('volatility', 0):.2f}")
        
        # Show recommendations impact
        recommendations_impact = forecast_results.get('recommendations_impact', {})
        if recommendations_impact:
            click.echo(f"\nOptimization Impact:")
            click.echo(f"  Base Forecast: ${recommendations_impact.get('base_forecast', 0):.2f}")
            click.echo(f"  Optimized Forecast: ${recommendations_impact.get('optimized_forecast', 0):.2f}")
            click.echo(f"  Potential Savings: ${recommendations_impact.get('total_savings', 0):.2f}")
            click.echo(f"  Savings Percentage: {recommendations_impact.get('savings_percentage', 0):.1f}%")
        
        # Save results if output specified
        if output:
            with open(output, 'w') as f:
                json.dump(forecast_results, f, indent=2, default=str)
            click.echo(f"Forecast saved to: {output}")
            
    except Exception as e:
        click.echo(f"Error during forecasting: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--type', '-t', default='comprehensive', 
              type=click.Choice(['comprehensive', 'summary', 'recommendations']),
              help='Type of report to generate')
@click.option('--format', '-f', default='html',
              type=click.Choice(['html', 'pdf', 'json']),
              help='Output format')
@click.option('--output', '-o', help='Output file path')
@click.pass_context
def report(ctx, type, format, output):
    """Generate optimization report."""
    try:
        optimizer = FinOpsOptimizer(ctx.obj['config'])
        
        click.echo(f"Generating {type} report in {format} format...")
        
        # Run optimization to get data
        results = optimizer.optimize_all(generate_report=False)
        
        # Generate report
        report_path = optimizer.generate_report(
            cost_data=results['cost_analysis'],
            recommendations=results['recommendations'],
            report_type=type,
            output_format=format
        )
        
        click.echo(f"Report generated: {report_path}")
        
        # Copy to specified output if provided
        if output:
            import shutil
            shutil.copy2(report_path, output)
            click.echo(f"Report copied to: {output}")
            
    except Exception as e:
        click.echo(f"Error generating report: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.pass_context
def status(ctx):
    """Check status of cloud providers."""
    try:
        optimizer = FinOpsOptimizer(ctx.obj['config'])
        
        click.echo("Checking cloud provider status...")
        
        # Check credentials
        credentials = optimizer.validate_credentials()
        click.echo("\n=== Credentials Status ===")
        for provider, valid in credentials.items():
            status = "✓ Valid" if valid else "✗ Invalid"
            click.echo(f"{provider.upper()}: {status}")
        
        # Check provider connections
        provider_status = optimizer.get_provider_status()
        click.echo("\n=== Provider Connections ===")
        for provider, connected in provider_status.items():
            status = "✓ Connected" if connected else "✗ Disconnected"
            click.echo(f"{provider.upper()}: {status}")
            
    except Exception as e:
        click.echo(f"Error checking status: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--output', '-o', default='finops_config.yml', help='Output file path')
@click.pass_context
def init(ctx, output):
    """Initialize configuration file."""
    try:
        config = ctx.obj['config']
        
        click.echo(f"Creating configuration file: {output}")
        
        # Save configuration
        config.save_to_file(output)
        
        click.echo("Configuration file created successfully!")
        click.echo("\nNext steps:")
        click.echo("1. Edit the configuration file to set up your cloud credentials")
        click.echo("2. Configure your cloud provider settings")
        click.echo("3. Run 'finops status' to verify connections")
        click.echo("4. Run 'finops analyze' to start cost analysis")
        
    except Exception as e:
        click.echo(f"Error creating configuration: {e}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    cli() 
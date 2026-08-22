#!/usr/bin/env python3
"""
Command-line interface for FinOpsOptimizer.
"""

import click
import logging
import os
import sys
import asyncio
from pathlib import Path
from datetime import datetime, timedelta
import json

from finops import (
    FinOpsOptimizer, 
    DataIngestionPipeline,
    VMRightsizingAnalyzer,
    CostOptimizationScheduler,
    UnattachedDisksRemediator,
    ReservedInstanceAnalyzer
)
from finops.config import load_config


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
@click.option('--days', '-d', default=365, help='Number of days to collect data for')
@click.option('--output', '-o', help='Output file path')
@click.pass_context
def ingest(ctx, days, output):
    """Ingest data from all cloud providers for comprehensive analysis."""
    try:
        config = ctx.obj['config']
        pipeline = DataIngestionPipeline(config)
        
        click.echo(f"Starting data ingestion for {days} days across all providers...")
        
        # Run data ingestion
        data = asyncio.run(pipeline.ingest_all_data(days))
        
        # Display summary
        click.echo("\n=== Data Ingestion Results ===")
        summary = data.get('ingestion_summary', {})
        click.echo(f"Providers Processed: {summary.get('providers_processed', 0)}")
        click.echo(f"Total Metrics Collected: {summary.get('total_metrics_collected', 0)}")
        click.echo(f"Period: {summary.get('start_date', '')} to {summary.get('end_date', '')}")
        
        # Show provider-specific results
        for provider_name, provider_data in data.get('provider_data', {}).items():
            if 'error' in provider_data:
                click.echo(f"\n{provider_name.upper()}: Error - {provider_data['error']}")
            else:
                click.echo(f"\n{provider_name.upper()}:")
                click.echo(f"  VM Metrics: {len(provider_data.get('vm_metrics', []))}")
                click.echo(f"  Unattached Disks: {len(provider_data.get('unattached_disks', []))}")
                click.echo(f"  Reserved Instances: {len(provider_data.get('reserved_instances', []))}")
        
        # Save data
        if output:
            pipeline.save_data_to_file(data, output)
            click.echo(f"\nData saved to: {output}")
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"ingested_data_{timestamp}.json"
            pipeline.save_data_to_file(data, filename)
            click.echo(f"\nData saved to: {filename}")
            
    except Exception as e:
        click.echo(f"Error during data ingestion: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--data-file', '-d', help='Path to ingested data file')
@click.option('--output', '-o', help='Output file path')
@click.pass_context
def rightsizing(ctx, data_file, output):
    """Analyze VM rightsizing opportunities based on 365-day metrics."""
    try:
        config = ctx.obj['config']
        analyzer = VMRightsizingAnalyzer(config)
        
        # Load data
        if data_file:
            with open(data_file, 'r') as f:
                data = json.load(f)
        else:
            # Run data ingestion first
            click.echo("No data file provided. Running data ingestion...")
            pipeline = DataIngestionPipeline(config)
            data = asyncio.run(pipeline.ingest_all_data(365))
        
        click.echo("Analyzing VM rightsizing opportunities...")
        
        # Analyze rightsizing
        recommendations = asyncio.run(analyzer.analyze_rightsizing_opportunities(data))
        
        # Generate report
        report = analyzer.generate_rightsizing_report(recommendations)
        
        # Display results
        click.echo("\n=== VM Rightsizing Analysis ===")
        summary = report.get('summary', {})
        click.echo(f"Total Recommendations: {summary.get('total_recommendations', 0)}")
        click.echo(f"Total Potential Savings: ${summary.get('total_potential_savings', 0):.2f}")
        click.echo(f"Current Cost: ${summary.get('total_current_cost', 0):.2f}")
        click.echo(f"Savings Percentage: {summary.get('savings_percentage', 0):.1f}%")
        
        # Show top recommendations
        top_recs = report.get('top_recommendations', [])
        if top_recs:
            click.echo("\nTop Rightsizing Recommendations:")
            for i, rec in enumerate(top_recs[:5], 1):
                click.echo(f"{i}. {rec['resource_id']} ({rec['provider']})")
                click.echo(f"   Current: {rec['current_size']} → Recommended: {rec['recommended_size']}")
                click.echo(f"   Savings: ${rec['potential_savings']:.2f}/month")
                click.echo(f"   Risk: {rec['risk_level']}")
                click.echo()
        
        # Save results
        if output:
            with open(output, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            click.echo(f"Rightsizing report saved to: {output}")
            
    except Exception as e:
        click.echo(f"Error during rightsizing analysis: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--dry-run', is_flag=True, help='Simulate actions without executing')
@click.option('--output', '-o', help='Output file path')
@click.pass_context
def cleanup_disks(ctx, dry_run, output):
    """Find and remediate unattached disks across all providers."""
    try:
        config = ctx.obj['config']
        remediator = UnattachedDisksRemediator(config)
        
        click.echo("Scanning for unattached disks...")
        
        # Scan for unattached disks
        unattached_disks = asyncio.run(remediator.scan_unattached_disks())
        
        # Generate report
        report = remediator.generate_unattached_disks_report(unattached_disks)
        
        # Display results
        click.echo("\n=== Unattached Disks Analysis ===")
        summary = report.get('summary', {})
        click.echo(f"Total Unattached Disks: {summary.get('total_unattached_disks', 0)}")
        click.echo(f"Total Size: {summary.get('total_size_gb', 0)} GB")
        click.echo(f"Total Monthly Cost: ${summary.get('total_monthly_cost', 0):.2f}")
        click.echo(f"Potential Savings: ${summary.get('total_potential_savings', 0):.2f}")
        
        # Show by provider
        by_provider = report.get('by_provider', {})
        for provider, provider_data in by_provider.items():
            click.echo(f"\n{provider.upper()}:")
            click.echo(f"  Count: {provider_data['count']}")
            click.echo(f"  Size: {provider_data['total_size_gb']} GB")
            click.echo(f"  Cost: ${provider_data['total_cost']:.2f}")
        
        # Show recommended actions
        by_action = report.get('by_recommended_action', {})
        if by_action:
            click.echo("\nRecommended Actions:")
            for action, action_data in by_action.items():
                click.echo(f"  {action}: {action_data['count']} disks (${action_data['potential_savings']:.2f} savings)")
        
        # Execute remediation if requested
        if not dry_run:
            confirm = click.confirm("Do you want to execute remediation actions?")
            if confirm:
                click.echo("Executing remediation...")
                remediation_results = asyncio.run(
                    remediator.execute_remediation(unattached_disks, dry_run=False)
                )
                
                click.echo(f"\nRemediation completed:")
                click.echo(f"Total Disks Processed: {remediation_results['total_disks']}")
                click.echo(f"Total Potential Savings: ${remediation_results['total_potential_savings']:.2f}")
                
                for action, results in remediation_results['actions_taken'].items():
                    click.echo(f"  {action}: {results['successful']} successful, {results['failed']} failed")
        
        # Save results
        if output:
            with open(output, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            click.echo(f"Unattached disks report saved to: {output}")
            
    except Exception as e:
        click.echo(f"Error during disk cleanup: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--data-file', '-d', help='Path to ingested data file')
@click.option('--output', '-o', help='Output file path')
@click.pass_context
def reservations(ctx, data_file, output):
    """Analyze reserved instances and savings plans opportunities."""
    try:
        config = ctx.obj['config']
        analyzer = ReservedInstanceAnalyzer(config)
        
        # Load data
        if data_file:
            with open(data_file, 'r') as f:
                data = json.load(f)
        else:
            # Run data ingestion first
            click.echo("No data file provided. Running data ingestion...")
            pipeline = DataIngestionPipeline(config)
            data = asyncio.run(pipeline.ingest_all_data(365))
        
        click.echo("Analyzing reservation opportunities...")
        
        # Analyze reservation opportunities
        recommendations = asyncio.run(analyzer.analyze_reservation_opportunities(data))
        
        # Analyze existing reservations
        existing_reservations = asyncio.run(analyzer.analyze_existing_reservations())
        
        # Generate report
        report = analyzer.generate_reservation_report(recommendations, existing_reservations)
        
        # Display results
        click.echo("\n=== Reserved Instances & Savings Plans Analysis ===")
        summary = report.get('summary', {})
        click.echo(f"Total Recommendations: {summary.get('total_recommendations', 0)}")
        click.echo(f"Potential Annual Savings: ${summary.get('total_potential_annual_savings', 0):.2f}")
        click.echo(f"Total Upfront Investment: ${summary.get('total_upfront_investment', 0):.2f}")
        click.echo(f"Average Break-even: {summary.get('average_break_even_months', 0):.1f} months")
        
        # Show by provider
        by_provider = report.get('recommendations_by_provider', {})
        for provider, provider_data in by_provider.items():
            click.echo(f"\n{provider.upper()}:")
            click.echo(f"  Recommendations: {provider_data['count']}")
            click.echo(f"  Potential Savings: ${provider_data['potential_savings']:.2f}")
            click.echo(f"  Upfront Cost: ${provider_data['upfront_cost']:.2f}")
        
        # Show top recommendations
        top_recs = report.get('top_recommendations', [])
        if top_recs:
            click.echo("\nTop Reservation Recommendations:")
            for i, rec in enumerate(top_recs[:5], 1):
                click.echo(f"{i}. {rec['provider']} - {rec['reservation_type']}")
                click.echo(f"   Term: {rec['term']}, Payment: {rec['payment_option']}")
                click.echo(f"   Annual Savings: ${rec['annual_savings']:.2f}")
                click.echo(f"   Break-even: {rec['break_even_months']} months")
                click.echo(f"   Risk: {rec['risk_level']}")
                click.echo()
        
        # Show existing reservations analysis
        existing_analysis = report.get('existing_reservations_analysis', {})
        if existing_analysis and 'message' not in existing_analysis:
            click.echo(f"\nExisting Reservations:")
            click.echo(f"  Total: {existing_analysis.get('total_reservations', 0)}")
            click.echo(f"  Average Utilization: {existing_analysis.get('average_utilization', 0):.1f}%")
            click.echo(f"  Wasted Cost: ${existing_analysis.get('total_wasted_cost', 0):.2f}")
            click.echo(f"  Underutilized: {existing_analysis.get('underutilized_count', 0)}")
        
        # Save results
        if output:
            with open(output, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            click.echo(f"Reservations report saved to: {output}")
            
    except Exception as e:
        click.echo(f"Error during reservations analysis: {e}", err=True)
        sys.exit(1)


@cli.group()
def schedule():
    """Manage cost optimization schedules."""
    pass


@schedule.command()
@click.option('--provider', '-p', required=True, help='Cloud provider (aws, azure, gcp, oracle)')
@click.option('--instances', '-i', required=True, help='Comma-separated list of instance IDs')
@click.option('--start-time', '-s', required=True, help='Start time (HH:MM)')
@click.option('--stop-time', '-t', required=True, help='Stop time (HH:MM)')
@click.option('--days', '-d', default='monday,tuesday,wednesday,thursday,friday', help='Days of week')
@click.pass_context
def vm_schedule(ctx, provider, instances, start_time, stop_time, days):
    """Create VM start/stop schedule."""
    try:
        config = ctx.obj['config']
        scheduler = CostOptimizationScheduler(config)
        
        instance_list = [i.strip() for i in instances.split(',')]
        days_list = [d.strip() for d in days.split(',')]
        
        task_id = scheduler.create_vm_schedule(
            provider=provider,
            resource_ids=instance_list,
            start_time=start_time,
            stop_time=stop_time,
            days_of_week=days_list
        )
        
        click.echo(f"VM schedule created with ID: {task_id}")
        click.echo(f"Instances: {', '.join(instance_list)}")
        click.echo(f"Schedule: {start_time} - {stop_time} on {', '.join(days_list)}")
        
    except Exception as e:
        click.echo(f"Error creating VM schedule: {e}", err=True)
        sys.exit(1)


@schedule.command()
@click.option('--frequency', '-f', default='daily', 
              type=click.Choice(['daily', 'weekly', 'monthly']),
              help='Analysis frequency')
@click.option('--time', '-t', default='06:00', help='Time to run (HH:MM)')
@click.pass_context
def cost_analysis(ctx, frequency, time):
    """Schedule regular cost analysis."""
    try:
        config = ctx.obj['config']
        scheduler = CostOptimizationScheduler(config)
        
        task_id = scheduler.create_cost_analysis_schedule(
            frequency=frequency,
            time=time,
            include_recommendations=True
        )
        
        click.echo(f"Cost analysis schedule created with ID: {task_id}")
        click.echo(f"Frequency: {frequency} at {time}")
        
    except Exception as e:
        click.echo(f"Error creating cost analysis schedule: {e}", err=True)
        sys.exit(1)


@schedule.command()
@click.option('--resource-type', '-r', default='unattached_disks',
              type=click.Choice(['unattached_disks', 'unused_snapshots']),
              help='Resource type to clean up')
@click.option('--frequency', '-f', default='weekly',
              type=click.Choice(['daily', 'weekly', 'monthly']),
              help='Cleanup frequency')
@click.option('--time', '-t', default='02:00', help='Time to run (HH:MM)')
@click.pass_context
def cleanup(ctx, resource_type, frequency, time):
    """Schedule resource cleanup."""
    try:
        config = ctx.obj['config']
        scheduler = CostOptimizationScheduler(config)
        
        task_id = scheduler.create_cleanup_schedule(
            resource_type=resource_type,
            frequency=frequency,
            time=time
        )
        
        click.echo(f"Cleanup schedule created with ID: {task_id}")
        click.echo(f"Resource: {resource_type}")
        click.echo(f"Frequency: {frequency} at {time}")
        
    except Exception as e:
        click.echo(f"Error creating cleanup schedule: {e}", err=True)
        sys.exit(1)


@schedule.command()
@click.pass_context
def list(ctx):
    """List all scheduled tasks."""
    try:
        config = ctx.obj['config']
        scheduler = CostOptimizationScheduler(config)
        
        tasks = scheduler.get_scheduled_tasks()
        
        if not tasks:
            click.echo("No scheduled tasks found.")
            return
        
        click.echo("=== Scheduled Tasks ===")
        for task_id, task_data in tasks.items():
            status = "✓ Enabled" if task_data['enabled'] else "✗ Disabled"
            click.echo(f"\nTask ID: {task_id}")
            click.echo(f"  Type: {task_data['task_type']}")
            click.echo(f"  Provider: {task_data['provider']}")
            click.echo(f"  Schedule: {task_data['schedule_expression']}")
            click.echo(f"  Status: {status}")
            click.echo(f"  Runs: {task_data['success_count']}/{task_data['run_count']}")
            if task_data['last_run']:
                click.echo(f"  Last Run: {task_data['last_run']}")
        
    except Exception as e:
        click.echo(f"Error listing scheduled tasks: {e}", err=True)
        sys.exit(1)


@schedule.command()
@click.argument('task_id')
@click.pass_context
def enable(ctx, task_id):
    """Enable a scheduled task."""
    try:
        config = ctx.obj['config']
        scheduler = CostOptimizationScheduler(config)
        
        if scheduler.enable_task(task_id):
            click.echo(f"Task {task_id} enabled successfully.")
        else:
            click.echo(f"Task {task_id} not found.", err=True)
        
    except Exception as e:
        click.echo(f"Error enabling task: {e}", err=True)
        sys.exit(1)


@schedule.command()
@click.argument('task_id')
@click.pass_context
def disable(ctx, task_id):
    """Disable a scheduled task."""
    try:
        config = ctx.obj['config']
        scheduler = CostOptimizationScheduler(config)
        
        if scheduler.disable_task(task_id):
            click.echo(f"Task {task_id} disabled successfully.")
        else:
            click.echo(f"Task {task_id} not found.", err=True)
        
    except Exception as e:
        click.echo(f"Error disabling task: {e}", err=True)
        sys.exit(1)


@cli.group()
def pricing():
    """Manage pricing and enterprise discounts."""
    pass


@pricing.command()
@click.option('--provider', '-p', required=True, help='Cloud provider (aws, azure, gcp, oracle)')
@click.option('--region', '-r', default='us-east-1', help='Cloud region')
@click.option('--instance-type', '-i', required=True, help='Instance type to check')
@click.option('--force-refresh', is_flag=True, help='Force refresh from API')
@click.pass_context
def check_price(ctx, provider, region, instance_type, force_refresh):
    """Check real-time pricing for an instance type."""
    try:
        from finops.pricing_engine import RealTimePricingEngine
        
        config = ctx.obj['config']
        
        async def get_pricing():
            async with RealTimePricingEngine(config) as pricing_engine:
                pricing_data = await pricing_engine.get_instance_pricing(
                    provider=provider,
                    region=region,
                    instance_type=instance_type,
                    force_refresh=force_refresh
                )
                
                if pricing_data:
                    click.echo(f"\n=== Pricing for {instance_type} in {region} ({provider.upper()}) ===")
                    click.echo(f"On-Demand Price: ${pricing_data.on_demand_price:.4f}/{pricing_data.pricing_unit}")
                    
                    if pricing_data.enterprise_price:
                        click.echo(f"Enterprise Price: ${pricing_data.enterprise_price:.4f}/{pricing_data.pricing_unit}")
                        savings = pricing_data.on_demand_price - pricing_data.enterprise_price
                        savings_pct = (savings / pricing_data.on_demand_price) * 100
                        click.echo(f"Enterprise Savings: ${savings:.4f} ({savings_pct:.1f}%)")
                    
                    if pricing_data.reserved_price:
                        click.echo(f"Reserved Price: ${pricing_data.reserved_price:.4f}/{pricing_data.pricing_unit}")
                    
                    click.echo(f"Currency: {pricing_data.currency}")
                    click.echo(f"Source: {pricing_data.source.value}")
                    click.echo(f"Last Updated: {pricing_data.effective_date}")
                    
                    # Monthly cost estimate
                    monthly_cost = pricing_data.enterprise_price or pricing_data.on_demand_price
                    click.echo(f"\nEstimated Monthly Cost: ${monthly_cost * 24 * 30:.2f}")
                else:
                    click.echo(f"❌ Could not retrieve pricing for {instance_type}")
        
        asyncio.run(get_pricing())
        
    except Exception as e:
        click.echo(f"Error checking pricing: {e}", err=True)
        sys.exit(1)


@pricing.command()
@click.option('--provider', '-p', required=True, help='Cloud provider')
@click.option('--service', '-s', default='all', help='Service name (default: all)')
@click.option('--discount', '-d', required=True, type=float, help='Discount percentage')
@click.option('--valid-from', help='Valid from date (YYYY-MM-DD)')
@click.option('--valid-until', help='Valid until date (YYYY-MM-DD)')
@click.pass_context
def add_discount(ctx, provider, service, discount, valid_from, valid_until):
    """Add enterprise discount."""
    try:
        from finops.pricing_engine import EnterpriseDiscount
        from datetime import datetime
        
        # Parse dates
        valid_from_date = datetime.fromisoformat(valid_from) if valid_from else datetime.now()
        valid_until_date = datetime.fromisoformat(valid_until) if valid_until else None
        
        # Create discount
        enterprise_discount = EnterpriseDiscount(
            provider=provider,
            service=service,
            resource_type='all',
            discount_type='percentage',
            discount_value=discount,
            valid_from=valid_from_date,
            valid_until=valid_until_date
        )
        
        # Add to configuration
        config = ctx.obj['config']
        
        # Convert to dict for storage
        discount_dict = {
            'provider': enterprise_discount.provider,
            'service': enterprise_discount.service,
            'resource_type': enterprise_discount.resource_type,
            'discount_type': enterprise_discount.discount_type,
            'discount_value': enterprise_discount.discount_value,
            'valid_from': enterprise_discount.valid_from.isoformat(),
            'valid_until': enterprise_discount.valid_until.isoformat() if enterprise_discount.valid_until else None
        }
        
        config.pricing.enterprise_discounts.append(discount_dict)
        
        # Save configuration
        config.save_to_file('finops_config.yml')
        
        click.echo(f"✅ Added {discount}% enterprise discount for {provider} {service}")
        click.echo(f"Valid from: {valid_from_date}")
        if valid_until_date:
            click.echo(f"Valid until: {valid_until_date}")
        
    except Exception as e:
        click.echo(f"Error adding discount: {e}", err=True)
        sys.exit(1)


@pricing.command()
@click.pass_context
def list_discounts(ctx):
    """List all enterprise discounts."""
    try:
        config = ctx.obj['config']
        discounts = config.pricing.enterprise_discounts
        
        if not discounts:
            click.echo("No enterprise discounts configured.")
            return
        
        click.echo("=== Enterprise Discounts ===")
        for i, discount in enumerate(discounts, 1):
            click.echo(f"\n{i}. {discount['provider'].upper()} - {discount['service']}")
            click.echo(f"   Discount: {discount['discount_value']}% ({discount['discount_type']})")
            click.echo(f"   Valid from: {discount['valid_from']}")
            if discount.get('valid_until'):
                click.echo(f"   Valid until: {discount['valid_until']}")
            else:
                click.echo(f"   Valid until: No expiration")
        
    except Exception as e:
        click.echo(f"Error listing discounts: {e}", err=True)
        sys.exit(1)


@pricing.command()
@click.option('--provider', '-p', help='Filter by provider')
@click.pass_context
def cache_stats(ctx, provider):
    """Show pricing cache statistics."""
    try:
        from finops.pricing_engine import RealTimePricingEngine
        
        config = ctx.obj['config']
        
        async def get_stats():
            async with RealTimePricingEngine(config) as pricing_engine:
                stats = pricing_engine.get_cache_stats()
                
                click.echo("=== Pricing Cache Statistics ===")
                click.echo(f"Total Entries: {stats['total_entries']}")
                click.echo(f"Fresh Entries: {stats['fresh_entries']}")
                click.echo(f"Stale Entries: {stats['stale_entries']}")
                click.echo(f"Cache TTL: {stats['cache_ttl']} seconds")
                click.echo(f"Hit Rate: {stats['hit_rate']:.1%}")
        
        asyncio.run(get_stats())
        
    except Exception as e:
        click.echo(f"Error getting cache stats: {e}", err=True)
        sys.exit(1)


@pricing.command()
@click.pass_context
def clear_cache(ctx):
    """Clear pricing cache."""
    try:
        from finops.pricing_engine import RealTimePricingEngine
        
        config = ctx.obj['config']
        
        async def clear():
            async with RealTimePricingEngine(config) as pricing_engine:
                pricing_engine.clear_cache()
                click.echo("✅ Pricing cache cleared")
        
        asyncio.run(clear())
        
    except Exception as e:
        click.echo(f"Error clearing cache: {e}", err=True)
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
        click.echo("2. Configure your cloud provider settings (AWS, Azure, GCP, Oracle)")
        click.echo("3. Run 'finops status' to verify connections")
        click.echo("4. Run 'finops ingest' to collect 365 days of data")
        click.echo("5. Run 'finops rightsizing' to analyze VM rightsizing opportunities")
        click.echo("6. Run 'finops cleanup-disks' to find unattached disks")
        click.echo("7. Run 'finops reservations' to analyze RI/SP opportunities")
        
    except Exception as e:
        click.echo(f"Error creating configuration: {e}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    cli() 
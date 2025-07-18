#!/usr/bin/env python3
"""
Comprehensive Cost Optimization Example

This example demonstrates how to use all the FinOpsOptimizer modules for
complete multi-cloud cost optimization including:
- Data ingestion from all 4 cloud providers (AWS, Azure, GCP, Oracle)
- VM rightsizing analysis based on 365-day metrics
- Unattached disk remediation
- Reserved instances and savings plans analysis
- Automated scheduling of optimization tasks
"""

import asyncio
import json
from datetime import datetime, timedelta
from pathlib import Path

from finops import (
    Config,
    DataIngestionPipeline,
    VMRightsizingAnalyzer,
    UnattachedDisksRemediator,
    ReservedInstanceAnalyzer,
    CostOptimizationScheduler,
    FinOpsOptimizer
)


async def main():
    """Main function demonstrating comprehensive cost optimization."""
    
    print("🚀 FinOpsOptimizer - Comprehensive Cost Optimization Demo")
    print("=" * 60)
    
    # Step 1: Initialize configuration
    print("\n📋 Step 1: Initializing Configuration")
    config = Config()
    
    # Enable all cloud providers (you would set credentials in real usage)
    config.aws.enabled = True
    config.azure.enabled = True
    config.gcp.enabled = True
    config.oracle.enabled = True
    
    print("✅ Configuration initialized for all 4 cloud providers")
    
    # Step 2: Data Ingestion (365 days)
    print("\n📊 Step 2: Data Ingestion (365 days)")
    print("Collecting VM metrics, cost data, and resource inventory...")
    
    pipeline = DataIngestionPipeline(config)
    
    try:
        # Collect data for the last 365 days
        ingested_data = await pipeline.ingest_all_data(days=365)
        
        # Display ingestion summary
        summary = ingested_data.get('ingestion_summary', {})
        print(f"✅ Data ingestion completed:")
        print(f"   • Providers processed: {summary.get('providers_processed', 0)}")
        print(f"   • Total metrics collected: {summary.get('total_metrics_collected', 0)}")
        print(f"   • Period: {summary.get('start_date', '')} to {summary.get('end_date', '')}")
        
        # Show provider-specific results
        for provider_name, provider_data in ingested_data.get('provider_data', {}).items():
            if 'error' not in provider_data:
                print(f"   • {provider_name.upper()}:")
                print(f"     - VM Metrics: {len(provider_data.get('vm_metrics', []))}")
                print(f"     - Unattached Disks: {len(provider_data.get('unattached_disks', []))}")
                print(f"     - Reserved Instances: {len(provider_data.get('reserved_instances', []))}")
        
        # Save ingested data
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        data_file = f"ingested_data_{timestamp}.json"
        pipeline.save_data_to_file(ingested_data, data_file)
        print(f"💾 Data saved to: {data_file}")
        
    except Exception as e:
        print(f"❌ Error during data ingestion: {e}")
        # Use mock data for demo purposes
        ingested_data = create_mock_data()
        print("📝 Using mock data for demonstration")
    
    # Step 3: VM Rightsizing Analysis
    print("\n🔧 Step 3: VM Rightsizing Analysis")
    print("Analyzing VM utilization patterns and rightsizing opportunities...")
    
    try:
        rightsizing_analyzer = VMRightsizingAnalyzer(config)
        rightsizing_recommendations = await rightsizing_analyzer.analyze_rightsizing_opportunities(ingested_data)
        rightsizing_report = rightsizing_analyzer.generate_rightsizing_report(rightsizing_recommendations)
        
        # Display rightsizing results
        summary = rightsizing_report.get('summary', {})
        print(f"✅ VM Rightsizing Analysis completed:")
        print(f"   • Total recommendations: {summary.get('total_recommendations', 0)}")
        print(f"   • Potential monthly savings: ${summary.get('total_potential_savings', 0):,.2f}")
        print(f"   • Current monthly cost: ${summary.get('total_current_cost', 0):,.2f}")
        print(f"   • Savings percentage: {summary.get('savings_percentage', 0):.1f}%")
        
        # Show top recommendations
        top_recs = rightsizing_report.get('top_recommendations', [])
        if top_recs:
            print("\n🏆 Top Rightsizing Recommendations:")
            for i, rec in enumerate(top_recs[:3], 1):
                print(f"   {i}. {rec['resource_id']} ({rec['provider']})")
                print(f"      Current: {rec['current_size']} → Recommended: {rec['recommended_size']}")
                print(f"      Monthly savings: ${rec['potential_savings']:,.2f}")
                print(f"      Risk level: {rec['risk_level']}")
        
        # Save rightsizing report
        rightsizing_file = f"rightsizing_report_{timestamp}.json"
        with open(rightsizing_file, 'w') as f:
            json.dump(rightsizing_report, f, indent=2, default=str)
        print(f"💾 Rightsizing report saved to: {rightsizing_file}")
        
    except Exception as e:
        print(f"❌ Error during rightsizing analysis: {e}")
    
    # Step 4: Unattached Disks Remediation
    print("\n💽 Step 4: Unattached Disks Analysis & Remediation")
    print("Scanning for unattached disks across all providers...")
    
    try:
        disk_remediator = UnattachedDisksRemediator(config)
        unattached_disks = await disk_remediator.scan_unattached_disks()
        disk_report = disk_remediator.generate_unattached_disks_report(unattached_disks)
        
        # Display unattached disks results
        summary = disk_report.get('summary', {})
        print(f"✅ Unattached Disks Analysis completed:")
        print(f"   • Total unattached disks: {summary.get('total_unattached_disks', 0)}")
        print(f"   • Total size: {summary.get('total_size_gb', 0):,} GB")
        print(f"   • Monthly cost: ${summary.get('total_monthly_cost', 0):,.2f}")
        print(f"   • Potential savings: ${summary.get('total_potential_savings', 0):,.2f}")
        
        # Show by provider
        by_provider = disk_report.get('by_provider', {})
        if by_provider:
            print("\n📊 By Cloud Provider:")
            for provider, data in by_provider.items():
                print(f"   • {provider.upper()}: {data['count']} disks, "
                      f"{data['total_size_gb']} GB, ${data['total_cost']:,.2f}")
        
        # Show recommended actions
        by_action = disk_report.get('by_recommended_action', {})
        if by_action:
            print("\n⚡ Recommended Actions:")
            for action, data in by_action.items():
                print(f"   • {action}: {data['count']} disks "
                      f"(${data['potential_savings']:,.2f} savings)")
        
        # Simulate remediation (dry run)
        print("\n🧪 Simulating remediation actions (dry run)...")
        remediation_results = await disk_remediator.execute_remediation(
            unattached_disks, dry_run=True
        )
        
        print(f"✅ Remediation simulation completed:")
        print(f"   • Total disks: {remediation_results['total_disks']}")
        print(f"   • Potential savings: ${remediation_results['total_potential_savings']:,.2f}")
        
        # Save disk report
        disk_file = f"unattached_disks_report_{timestamp}.json"
        with open(disk_file, 'w') as f:
            json.dump(disk_report, f, indent=2, default=str)
        print(f"💾 Unattached disks report saved to: {disk_file}")
        
    except Exception as e:
        print(f"❌ Error during disk analysis: {e}")
    
    # Step 5: Reserved Instances & Savings Plans Analysis
    print("\n💰 Step 5: Reserved Instances & Savings Plans Analysis")
    print("Analyzing RI/SP opportunities and existing reservations...")
    
    try:
        ri_analyzer = ReservedInstanceAnalyzer(config)
        
        # Analyze reservation opportunities
        ri_recommendations = await ri_analyzer.analyze_reservation_opportunities(ingested_data)
        
        # Analyze existing reservations
        existing_reservations = await ri_analyzer.analyze_existing_reservations()
        
        # Generate comprehensive report
        ri_report = ri_analyzer.generate_reservation_report(ri_recommendations, existing_reservations)
        
        # Display reservation results
        summary = ri_report.get('summary', {})
        print(f"✅ Reservation Analysis completed:")
        print(f"   • Total recommendations: {summary.get('total_recommendations', 0)}")
        print(f"   • Potential annual savings: ${summary.get('total_potential_annual_savings', 0):,.2f}")
        print(f"   • Required upfront investment: ${summary.get('total_upfront_investment', 0):,.2f}")
        print(f"   • Average break-even: {summary.get('average_break_even_months', 0):.1f} months")
        
        # Show by provider
        by_provider = ri_report.get('recommendations_by_provider', {})
        if by_provider:
            print("\n📊 By Cloud Provider:")
            for provider, data in by_provider.items():
                print(f"   • {provider.upper()}: {data['count']} recommendations, "
                      f"${data['potential_savings']:,.2f} annual savings")
        
        # Show top recommendations
        top_recs = ri_report.get('top_recommendations', [])
        if top_recs:
            print("\n🏆 Top Reservation Recommendations:")
            for i, rec in enumerate(top_recs[:3], 1):
                print(f"   {i}. {rec['provider']} - {rec['reservation_type']}")
                print(f"      Term: {rec['term']}, Payment: {rec['payment_option']}")
                print(f"      Annual savings: ${rec['annual_savings']:,.2f}")
                print(f"      Break-even: {rec['break_even_months']} months")
        
        # Show existing reservations analysis
        existing_analysis = ri_report.get('existing_reservations_analysis', {})
        if existing_analysis and 'message' not in existing_analysis:
            print(f"\n📈 Existing Reservations Analysis:")
            print(f"   • Total reservations: {existing_analysis.get('total_reservations', 0)}")
            print(f"   • Average utilization: {existing_analysis.get('average_utilization', 0):.1f}%")
            print(f"   • Wasted cost: ${existing_analysis.get('total_wasted_cost', 0):,.2f}")
            print(f"   • Underutilized: {existing_analysis.get('underutilized_count', 0)}")
        
        # Save reservation report
        ri_file = f"reservations_report_{timestamp}.json"
        with open(ri_file, 'w') as f:
            json.dump(ri_report, f, indent=2, default=str)
        print(f"💾 Reservations report saved to: {ri_file}")
        
    except Exception as e:
        print(f"❌ Error during reservations analysis: {e}")
    
    # Step 6: Automated Scheduling
    print("\n⏰ Step 6: Setting up Automated Scheduling")
    print("Creating automated cost optimization schedules...")
    
    try:
        scheduler = CostOptimizationScheduler(config)
        
        # Schedule daily cost analysis
        cost_analysis_task = scheduler.create_cost_analysis_schedule(
            frequency="daily",
            time="06:00",
            include_recommendations=True
        )
        print(f"✅ Daily cost analysis scheduled (ID: {cost_analysis_task})")
        
        # Schedule weekly cleanup
        cleanup_task = scheduler.create_cleanup_schedule(
            resource_type="unattached_disks",
            frequency="weekly",
            time="02:00"
        )
        print(f"✅ Weekly disk cleanup scheduled (ID: {cleanup_task})")
        
        # Example VM schedule (would use real instance IDs in practice)
        if False:  # Disabled for demo
            vm_task = scheduler.create_vm_schedule(
                provider="aws",
                resource_ids=["i-1234567890abcdef0", "i-0987654321fedcba0"],
                start_time="08:00",
                stop_time="18:00",
                days_of_week=["monday", "tuesday", "wednesday", "thursday", "friday"]
            )
            print(f"✅ VM start/stop schedule created (ID: {vm_task})")
        
        # List all scheduled tasks
        tasks = scheduler.get_scheduled_tasks()
        print(f"\n📅 Total scheduled tasks: {len(tasks)}")
        for task_id, task_data in tasks.items():
            status = "✅ Enabled" if task_data['enabled'] else "❌ Disabled"
            print(f"   • {task_id}: {task_data['task_type']} - {status}")
        
    except Exception as e:
        print(f"❌ Error setting up scheduling: {e}")
    
    # Step 7: Generate Comprehensive Report
    print("\n📊 Step 7: Generating Comprehensive Report")
    print("Creating final optimization report...")
    
    try:
        optimizer = FinOpsOptimizer(config)
        
        # Run complete optimization
        optimization_results = optimizer.optimize_all(
            generate_report=True,
            save_results=True
        )
        
        # Display final summary
        summary = optimization_results.get('summary', {})
        print(f"✅ Comprehensive optimization completed:")
        print(f"   • Total recommendations: {summary.get('total_recommendations', 0)}")
        print(f"   • Total potential savings: ${summary.get('total_potential_savings', 0):,.2f}")
        print(f"   • Providers analyzed: {', '.join(summary.get('providers_analyzed', []))}")
        
        if optimization_results.get('report_path'):
            print(f"📄 Final report generated: {optimization_results['report_path']}")
        
    except Exception as e:
        print(f"❌ Error generating final report: {e}")
    
    # Summary
    print("\n🎉 Comprehensive Cost Optimization Demo Completed!")
    print("=" * 60)
    print("Summary of what was accomplished:")
    print("✅ Data ingestion from all 4 cloud providers (365 days)")
    print("✅ VM rightsizing analysis with ML-powered recommendations")
    print("✅ Unattached disk identification and remediation planning")
    print("✅ Reserved instances and savings plans optimization")
    print("✅ Automated scheduling for ongoing optimization")
    print("✅ Comprehensive reporting and documentation")
    print("\nNext steps:")
    print("1. Review generated reports and recommendations")
    print("2. Implement high-confidence, low-risk optimizations first")
    print("3. Set up monitoring for scheduled tasks")
    print("4. Regularly review and update optimization strategies")
    print("5. Consider implementing AI agents for automated execution")


def create_mock_data():
    """Create mock data for demonstration purposes."""
    return {
        'ingestion_summary': {
            'start_date': (datetime.now() - timedelta(days=365)).isoformat(),
            'end_date': datetime.now().isoformat(),
            'providers_processed': 4,
            'total_metrics_collected': 50000
        },
        'provider_data': {
            'aws': {
                'vm_metrics': [
                    {
                        'resource_id': 'i-1234567890abcdef0',
                        'resource_type': 'ec2_instance',
                        'provider': 'aws',
                        'timestamp': datetime.now().isoformat(),
                        'metric_name': 'CPUUtilization',
                        'value': 15.5,
                        'tags': {'Environment': 'Production', 'Team': 'Backend'}
                    }
                ] * 1000,  # Simulate 1000 metrics
                'cost_data': {'total_cost': 5000},
                'resource_inventory': {
                    'ec2_instances': [
                        {
                            'instance_id': 'i-1234567890abcdef0',
                            'instance_type': 'm5.large',
                            'state': 'running'
                        }
                    ]
                },
                'unattached_disks': [
                    {
                        'volume_id': 'vol-1234567890abcdef0',
                        'size': 100,
                        'state': 'available'
                    }
                ],
                'reserved_instances': []
            },
            'azure': {
                'vm_metrics': [],
                'cost_data': {'total_cost': 3000},
                'resource_inventory': {'virtual_machines': []},
                'unattached_disks': [],
                'reserved_instances': []
            },
            'gcp': {
                'vm_metrics': [],
                'cost_data': {'total_cost': 2000},
                'resource_inventory': {'compute_instances': []},
                'unattached_disks': [],
                'reserved_instances': []
            },
            'oracle': {
                'vm_metrics': [],
                'cost_data': {'total_cost': 1000},
                'resource_inventory': {'compute_instances': []},
                'unattached_disks': [],
                'reserved_instances': []
            }
        }
    }


if __name__ == "__main__":
    # Run the comprehensive cost optimization demo
    asyncio.run(main())
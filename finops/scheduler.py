"""
Scheduler module for automated cost optimization tasks.
Handles scheduling of VM start/stop, scaling operations, and optimization tasks.
"""

import logging
import asyncio
import schedule
import time
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import json
from pathlib import Path

from .config import Config


class ScheduleType(Enum):
    """Types of scheduled operations."""
    VM_START_STOP = "vm_start_stop"
    AUTO_SCALING = "auto_scaling"
    COST_ANALYSIS = "cost_analysis"
    RIGHTSIZING_ANALYSIS = "rightsizing_analysis"
    UNATTACHED_DISK_CLEANUP = "unattached_disk_cleanup"
    RESERVED_INSTANCE_ANALYSIS = "reserved_instance_analysis"
    REPORT_GENERATION = "report_generation"


@dataclass
class ScheduledTask:
    """Container for scheduled task information."""
    task_id: str
    task_type: ScheduleType
    provider: str
    resource_ids: List[str]
    schedule_expression: str  # cron-like expression
    action: str  # start, stop, scale_up, scale_down, etc.
    parameters: Dict[str, Any]
    enabled: bool
    created_at: datetime
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    run_count: int = 0
    success_count: int = 0
    failure_count: int = 0


class CostOptimizationScheduler:
    """
    Scheduler for automated cost optimization tasks.
    
    Handles scheduling of various cost optimization operations including:
    - VM start/stop based on usage patterns
    - Auto-scaling adjustments
    - Regular cost analysis and reporting
    - Cleanup of unused resources
    """
    
    def __init__(self, config: Config):
        """
        Initialize Cost Optimization Scheduler.
        
        Args:
            config: Configuration object
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Storage for scheduled tasks
        self.scheduled_tasks: Dict[str, ScheduledTask] = {}
        self.running = False
        
        # Initialize cloud providers
        self.providers = {}
        self._initialize_providers()
        
        # Load existing schedules
        self._load_schedules()
    
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
    
    def create_vm_schedule(self,
                          provider: str,
                          resource_ids: List[str],
                          start_time: str,
                          stop_time: str,
                          days_of_week: List[str],
                          timezone: str = "UTC") -> str:
        """
        Create a VM start/stop schedule.
        
        Args:
            provider: Cloud provider name
            resource_ids: List of VM/instance IDs
            start_time: Start time in HH:MM format
            stop_time: Stop time in HH:MM format
            days_of_week: List of days (monday, tuesday, etc.)
            timezone: Timezone for the schedule
            
        Returns:
            Task ID of the created schedule
        """
        task_id = f"vm_schedule_{provider}_{int(time.time())}"
        
        # Create start task
        start_task = ScheduledTask(
            task_id=f"{task_id}_start",
            task_type=ScheduleType.VM_START_STOP,
            provider=provider,
            resource_ids=resource_ids,
            schedule_expression=f"{start_time} on {','.join(days_of_week)}",
            action="start",
            parameters={"timezone": timezone},
            enabled=True,
            created_at=datetime.now()
        )
        
        # Create stop task
        stop_task = ScheduledTask(
            task_id=f"{task_id}_stop",
            task_type=ScheduleType.VM_START_STOP,
            provider=provider,
            resource_ids=resource_ids,
            schedule_expression=f"{stop_time} on {','.join(days_of_week)}",
            action="stop",
            parameters={"timezone": timezone},
            enabled=True,
            created_at=datetime.now()
        )
        
        # Add to scheduled tasks
        self.scheduled_tasks[start_task.task_id] = start_task
        self.scheduled_tasks[stop_task.task_id] = stop_task
        
        # Schedule the tasks
        self._schedule_task(start_task)
        self._schedule_task(stop_task)
        
        # Save schedules
        self._save_schedules()
        
        self.logger.info(f"Created VM schedule for {len(resource_ids)} resources in {provider}")
        return task_id
    
    def create_autoscaling_schedule(self,
                                   provider: str,
                                   autoscaling_group_id: str,
                                   scale_up_time: str,
                                   scale_down_time: str,
                                   min_capacity: int,
                                   max_capacity: int,
                                   days_of_week: List[str]) -> str:
        """
        Create an auto-scaling schedule.
        
        Args:
            provider: Cloud provider name
            autoscaling_group_id: Auto-scaling group ID
            scale_up_time: Scale up time in HH:MM format
            scale_down_time: Scale down time in HH:MM format
            min_capacity: Minimum capacity during scale down
            max_capacity: Maximum capacity during scale up
            days_of_week: List of days
            
        Returns:
            Task ID of the created schedule
        """
        task_id = f"autoscaling_schedule_{provider}_{int(time.time())}"
        
        # Create scale up task
        scale_up_task = ScheduledTask(
            task_id=f"{task_id}_scale_up",
            task_type=ScheduleType.AUTO_SCALING,
            provider=provider,
            resource_ids=[autoscaling_group_id],
            schedule_expression=f"{scale_up_time} on {','.join(days_of_week)}",
            action="scale_up",
            parameters={"max_capacity": max_capacity},
            enabled=True,
            created_at=datetime.now()
        )
        
        # Create scale down task
        scale_down_task = ScheduledTask(
            task_id=f"{task_id}_scale_down",
            task_type=ScheduleType.AUTO_SCALING,
            provider=provider,
            resource_ids=[autoscaling_group_id],
            schedule_expression=f"{scale_down_time} on {','.join(days_of_week)}",
            action="scale_down",
            parameters={"min_capacity": min_capacity},
            enabled=True,
            created_at=datetime.now()
        )
        
        # Add to scheduled tasks
        self.scheduled_tasks[scale_up_task.task_id] = scale_up_task
        self.scheduled_tasks[scale_down_task.task_id] = scale_down_task
        
        # Schedule the tasks
        self._schedule_task(scale_up_task)
        self._schedule_task(scale_down_task)
        
        # Save schedules
        self._save_schedules()
        
        self.logger.info(f"Created auto-scaling schedule for {autoscaling_group_id} in {provider}")
        return task_id
    
    def create_cost_analysis_schedule(self,
                                     frequency: str = "daily",
                                     time: str = "06:00",
                                     include_recommendations: bool = True) -> str:
        """
        Create a cost analysis schedule.
        
        Args:
            frequency: Frequency (daily, weekly, monthly)
            time: Time to run in HH:MM format
            include_recommendations: Whether to include recommendations
            
        Returns:
            Task ID of the created schedule
        """
        task_id = f"cost_analysis_{int(time.time())}"
        
        # Determine schedule expression
        if frequency == "daily":
            schedule_expr = f"{time} every day"
        elif frequency == "weekly":
            schedule_expr = f"{time} on monday"
        elif frequency == "monthly":
            schedule_expr = f"{time} on 1st day of month"
        else:
            schedule_expr = f"{time} every day"
        
        task = ScheduledTask(
            task_id=task_id,
            task_type=ScheduleType.COST_ANALYSIS,
            provider="all",
            resource_ids=[],
            schedule_expression=schedule_expr,
            action="analyze_costs",
            parameters={"include_recommendations": include_recommendations},
            enabled=True,
            created_at=datetime.now()
        )
        
        self.scheduled_tasks[task_id] = task
        self._schedule_task(task)
        self._save_schedules()
        
        self.logger.info(f"Created cost analysis schedule: {frequency} at {time}")
        return task_id
    
    def create_cleanup_schedule(self,
                               resource_type: str = "unattached_disks",
                               frequency: str = "weekly",
                               time: str = "02:00") -> str:
        """
        Create a cleanup schedule for unused resources.
        
        Args:
            resource_type: Type of resource to clean up
            frequency: Frequency (daily, weekly, monthly)
            time: Time to run in HH:MM format
            
        Returns:
            Task ID of the created schedule
        """
        task_id = f"cleanup_{resource_type}_{int(time.time())}"
        
        # Determine schedule expression
        if frequency == "daily":
            schedule_expr = f"{time} every day"
        elif frequency == "weekly":
            schedule_expr = f"{time} on sunday"
        elif frequency == "monthly":
            schedule_expr = f"{time} on 1st day of month"
        else:
            schedule_expr = f"{time} every week"
        
        task = ScheduledTask(
            task_id=task_id,
            task_type=ScheduleType.UNATTACHED_DISK_CLEANUP,
            provider="all",
            resource_ids=[],
            schedule_expression=schedule_expr,
            action="cleanup",
            parameters={"resource_type": resource_type},
            enabled=True,
            created_at=datetime.now()
        )
        
        self.scheduled_tasks[task_id] = task
        self._schedule_task(task)
        self._save_schedules()
        
        self.logger.info(f"Created cleanup schedule for {resource_type}: {frequency} at {time}")
        return task_id
    
    def _schedule_task(self, task: ScheduledTask) -> None:
        """Schedule a task using the schedule library."""
        
        # Parse schedule expression and create schedule
        if "every day" in task.schedule_expression:
            time_part = task.schedule_expression.split()[0]
            schedule.every().day.at(time_part).do(self._execute_task, task.task_id)
        
        elif "on monday" in task.schedule_expression:
            time_part = task.schedule_expression.split()[0]
            schedule.every().monday.at(time_part).do(self._execute_task, task.task_id)
        
        elif "on tuesday" in task.schedule_expression:
            time_part = task.schedule_expression.split()[0]
            schedule.every().tuesday.at(time_part).do(self._execute_task, task.task_id)
        
        elif "on wednesday" in task.schedule_expression:
            time_part = task.schedule_expression.split()[0]
            schedule.every().wednesday.at(time_part).do(self._execute_task, task.task_id)
        
        elif "on thursday" in task.schedule_expression:
            time_part = task.schedule_expression.split()[0]
            schedule.every().thursday.at(time_part).do(self._execute_task, task.task_id)
        
        elif "on friday" in task.schedule_expression:
            time_part = task.schedule_expression.split()[0]
            schedule.every().friday.at(time_part).do(self._execute_task, task.task_id)
        
        elif "on saturday" in task.schedule_expression:
            time_part = task.schedule_expression.split()[0]
            schedule.every().saturday.at(time_part).do(self._execute_task, task.task_id)
        
        elif "on sunday" in task.schedule_expression:
            time_part = task.schedule_expression.split()[0]
            schedule.every().sunday.at(time_part).do(self._execute_task, task.task_id)
        
        elif "every week" in task.schedule_expression:
            time_part = task.schedule_expression.split()[0]
            schedule.every().week.at(time_part).do(self._execute_task, task.task_id)
    
    def _execute_task(self, task_id: str) -> None:
        """Execute a scheduled task."""
        if task_id not in self.scheduled_tasks:
            self.logger.error(f"Task {task_id} not found")
            return
        
        task = self.scheduled_tasks[task_id]
        
        if not task.enabled:
            self.logger.debug(f"Task {task_id} is disabled, skipping")
            return
        
        self.logger.info(f"Executing scheduled task: {task_id}")
        
        try:
            # Update task statistics
            task.run_count += 1
            task.last_run = datetime.now()
            
            # Execute based on task type
            if task.task_type == ScheduleType.VM_START_STOP:
                self._execute_vm_start_stop_task(task)
            
            elif task.task_type == ScheduleType.AUTO_SCALING:
                self._execute_autoscaling_task(task)
            
            elif task.task_type == ScheduleType.COST_ANALYSIS:
                self._execute_cost_analysis_task(task)
            
            elif task.task_type == ScheduleType.RIGHTSIZING_ANALYSIS:
                self._execute_rightsizing_analysis_task(task)
            
            elif task.task_type == ScheduleType.UNATTACHED_DISK_CLEANUP:
                self._execute_cleanup_task(task)
            
            elif task.task_type == ScheduleType.RESERVED_INSTANCE_ANALYSIS:
                self._execute_reserved_instance_analysis_task(task)
            
            elif task.task_type == ScheduleType.REPORT_GENERATION:
                self._execute_report_generation_task(task)
            
            task.success_count += 1
            self.logger.info(f"Successfully executed task: {task_id}")
            
        except Exception as e:
            task.failure_count += 1
            self.logger.error(f"Error executing task {task_id}: {e}")
        
        finally:
            # Save updated task statistics
            self._save_schedules()
    
    def _execute_vm_start_stop_task(self, task: ScheduledTask) -> None:
        """Execute VM start/stop task."""
        provider = self.providers.get(task.provider)
        if not provider:
            raise ValueError(f"Provider {task.provider} not available")
        
        for resource_id in task.resource_ids:
            if task.action == "start":
                if hasattr(provider, 'start_instance'):
                    provider.start_instance(resource_id)
                    self.logger.info(f"Started instance {resource_id}")
            
            elif task.action == "stop":
                if hasattr(provider, 'stop_instance'):
                    provider.stop_instance(resource_id)
                    self.logger.info(f"Stopped instance {resource_id}")
    
    def _execute_autoscaling_task(self, task: ScheduledTask) -> None:
        """Execute auto-scaling task."""
        provider = self.providers.get(task.provider)
        if not provider:
            raise ValueError(f"Provider {task.provider} not available")
        
        asg_id = task.resource_ids[0]
        
        if task.action == "scale_up":
            max_capacity = task.parameters.get("max_capacity", 10)
            if hasattr(provider, 'update_autoscaling_group'):
                provider.update_autoscaling_group(asg_id, max_size=max_capacity)
                self.logger.info(f"Scaled up ASG {asg_id} to max capacity {max_capacity}")
        
        elif task.action == "scale_down":
            min_capacity = task.parameters.get("min_capacity", 1)
            if hasattr(provider, 'update_autoscaling_group'):
                provider.update_autoscaling_group(asg_id, min_size=min_capacity)
                self.logger.info(f"Scaled down ASG {asg_id} to min capacity {min_capacity}")
    
    def _execute_cost_analysis_task(self, task: ScheduledTask) -> None:
        """Execute cost analysis task."""
        from .core import FinOpsOptimizer
        
        optimizer = FinOpsOptimizer(self.config)
        
        # Run cost analysis
        results = optimizer.analyze_costs()
        
        # Generate recommendations if requested
        if task.parameters.get("include_recommendations", True):
            recommendations = optimizer.generate_recommendations()
            results['recommendations'] = recommendations
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"scheduled_cost_analysis_{timestamp}.json"
        
        output_dir = Path(self.config.output_dir)
        output_dir.mkdir(exist_ok=True)
        
        with open(output_dir / filename, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        self.logger.info(f"Cost analysis completed and saved to {filename}")
    
    def _execute_rightsizing_analysis_task(self, task: ScheduledTask) -> None:
        """Execute rightsizing analysis task."""
        from .data_ingestion import DataIngestionPipeline
        from .vm_rightsizing import VMRightsizingAnalyzer
        
        # Collect data
        pipeline = DataIngestionPipeline(self.config)
        data = asyncio.run(pipeline.ingest_all_data(days=30))  # Last 30 days for scheduled analysis
        
        # Analyze rightsizing
        analyzer = VMRightsizingAnalyzer(self.config)
        recommendations = asyncio.run(analyzer.analyze_rightsizing_opportunities(data))
        
        # Generate report
        report = analyzer.generate_rightsizing_report(recommendations)
        
        # Save report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"scheduled_rightsizing_analysis_{timestamp}.json"
        
        output_dir = Path(self.config.output_dir)
        output_dir.mkdir(exist_ok=True)
        
        with open(output_dir / filename, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        self.logger.info(f"Rightsizing analysis completed and saved to {filename}")
    
    def _execute_cleanup_task(self, task: ScheduledTask) -> None:
        """Execute cleanup task."""
        resource_type = task.parameters.get("resource_type", "unattached_disks")
        
        cleanup_results = {}
        
        for provider_name, provider in self.providers.items():
            try:
                if resource_type == "unattached_disks":
                    if hasattr(provider, 'cleanup_unattached_volumes'):
                        result = provider.cleanup_unattached_volumes()
                        cleanup_results[provider_name] = result
                
                elif resource_type == "unused_snapshots":
                    if hasattr(provider, 'cleanup_unused_snapshots'):
                        result = provider.cleanup_unused_snapshots()
                        cleanup_results[provider_name] = result
                
            except Exception as e:
                self.logger.error(f"Error cleaning up {resource_type} in {provider_name}: {e}")
                cleanup_results[provider_name] = {"error": str(e)}
        
        # Save cleanup results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"scheduled_cleanup_{resource_type}_{timestamp}.json"
        
        output_dir = Path(self.config.output_dir)
        output_dir.mkdir(exist_ok=True)
        
        with open(output_dir / filename, 'w') as f:
            json.dump(cleanup_results, f, indent=2, default=str)
        
        self.logger.info(f"Cleanup task completed for {resource_type}")
    
    def _execute_reserved_instance_analysis_task(self, task: ScheduledTask) -> None:
        """Execute reserved instance analysis task."""
        # This would analyze reserved instance utilization and recommendations
        # Placeholder implementation
        self.logger.info("Reserved instance analysis task executed")
    
    def _execute_report_generation_task(self, task: ScheduledTask) -> None:
        """Execute report generation task."""
        from .core import FinOpsOptimizer
        
        optimizer = FinOpsOptimizer(self.config)
        
        # Generate comprehensive report
        report_path = optimizer.generate_report(
            report_type="comprehensive",
            output_format="html"
        )
        
        self.logger.info(f"Scheduled report generated: {report_path}")
    
    def start_scheduler(self) -> None:
        """Start the scheduler."""
        self.running = True
        self.logger.info("Cost optimization scheduler started")
        
        while self.running:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    def stop_scheduler(self) -> None:
        """Stop the scheduler."""
        self.running = False
        self.logger.info("Cost optimization scheduler stopped")
    
    def get_scheduled_tasks(self) -> Dict[str, Dict[str, Any]]:
        """Get all scheduled tasks."""
        return {
            task_id: {
                'task_type': task.task_type.value,
                'provider': task.provider,
                'resource_ids': task.resource_ids,
                'schedule_expression': task.schedule_expression,
                'action': task.action,
                'enabled': task.enabled,
                'created_at': task.created_at.isoformat(),
                'last_run': task.last_run.isoformat() if task.last_run else None,
                'run_count': task.run_count,
                'success_count': task.success_count,
                'failure_count': task.failure_count
            }
            for task_id, task in self.scheduled_tasks.items()
        }
    
    def enable_task(self, task_id: str) -> bool:
        """Enable a scheduled task."""
        if task_id in self.scheduled_tasks:
            self.scheduled_tasks[task_id].enabled = True
            self._save_schedules()
            return True
        return False
    
    def disable_task(self, task_id: str) -> bool:
        """Disable a scheduled task."""
        if task_id in self.scheduled_tasks:
            self.scheduled_tasks[task_id].enabled = False
            self._save_schedules()
            return True
        return False
    
    def delete_task(self, task_id: str) -> bool:
        """Delete a scheduled task."""
        if task_id in self.scheduled_tasks:
            del self.scheduled_tasks[task_id]
            self._save_schedules()
            return True
        return False
    
    def _load_schedules(self) -> None:
        """Load schedules from file."""
        schedule_file = Path(self.config.output_dir) / "schedules.json"
        
        if schedule_file.exists():
            try:
                with open(schedule_file, 'r') as f:
                    data = json.load(f)
                
                for task_data in data.get('tasks', []):
                    task = ScheduledTask(
                        task_id=task_data['task_id'],
                        task_type=ScheduleType(task_data['task_type']),
                        provider=task_data['provider'],
                        resource_ids=task_data['resource_ids'],
                        schedule_expression=task_data['schedule_expression'],
                        action=task_data['action'],
                        parameters=task_data['parameters'],
                        enabled=task_data['enabled'],
                        created_at=datetime.fromisoformat(task_data['created_at']),
                        last_run=datetime.fromisoformat(task_data['last_run']) if task_data.get('last_run') else None,
                        run_count=task_data.get('run_count', 0),
                        success_count=task_data.get('success_count', 0),
                        failure_count=task_data.get('failure_count', 0)
                    )
                    
                    self.scheduled_tasks[task.task_id] = task
                    
                    # Re-schedule the task
                    if task.enabled:
                        self._schedule_task(task)
                
                self.logger.info(f"Loaded {len(self.scheduled_tasks)} scheduled tasks")
                
            except Exception as e:
                self.logger.error(f"Error loading schedules: {e}")
    
    def _save_schedules(self) -> None:
        """Save schedules to file."""
        schedule_file = Path(self.config.output_dir) / "schedules.json"
        schedule_file.parent.mkdir(exist_ok=True)
        
        data = {
            'tasks': [
                {
                    'task_id': task.task_id,
                    'task_type': task.task_type.value,
                    'provider': task.provider,
                    'resource_ids': task.resource_ids,
                    'schedule_expression': task.schedule_expression,
                    'action': task.action,
                    'parameters': task.parameters,
                    'enabled': task.enabled,
                    'created_at': task.created_at.isoformat(),
                    'last_run': task.last_run.isoformat() if task.last_run else None,
                    'run_count': task.run_count,
                    'success_count': task.success_count,
                    'failure_count': task.failure_count
                }
                for task in self.scheduled_tasks.values()
            ]
        }
        
        try:
            with open(schedule_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving schedules: {e}")
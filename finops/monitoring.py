"""
Monitoring and health check module for FinOpsOptimizer.
"""

import time
import logging
import threading
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json
import os
from pathlib import Path
import psutil

from .config import Config


class HealthChecker:
    """
    Health checker for FinOpsOptimizer components.
    """
    
    def __init__(self, config: Config):
        """
        Initialize HealthChecker.
        
        Args:
            config: Configuration object
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Health check results
        self.health_status = {
            'overall': 'healthy',
            'checks': {},
            'last_check': None,
            'uptime': time.time()
        }
        
        # Monitoring metrics
        self.metrics = {
            'requests_total': 0,
            'requests_successful': 0,
            'requests_failed': 0,
            'average_response_time': 0.0,
            'memory_usage': 0.0,
            'cpu_usage': 0.0
        }
        
        # Start background monitoring
        self.monitoring_thread = threading.Thread(target=self._monitor_background, daemon=True)
        self.monitoring_thread.start()
    
    def check_health(self) -> Dict[str, Any]:
        """
        Perform comprehensive health check.
        
        Returns:
            Health check results
        """
        self.logger.info("Performing health check")
        
        checks = {}
        
        # Check system resources
        checks['system'] = self._check_system_resources()
        
        # Check cloud provider connectivity
        checks['providers'] = self._check_provider_connectivity()
        
        # Check configuration
        checks['configuration'] = self._check_configuration()
        
        # Check disk space
        checks['disk'] = self._check_disk_space()
        
        # Check memory usage
        checks['memory'] = self._check_memory_usage()
        
        # Determine overall health
        overall_health = 'healthy'
        if any(check['status'] == 'critical' for check in checks.values()):
            overall_health = 'critical'
        elif any(check['status'] == 'warning' for check in checks.values()):
            overall_health = 'warning'
        
        self.health_status = {
            'overall': overall_health,
            'checks': checks,
            'last_check': datetime.now().isoformat(),
            'uptime': time.time() - self.health_status['uptime']
        }
        
        return self.health_status
    
    def _check_system_resources(self) -> Dict[str, Any]:
        """
        Check system resource usage.
        
        Returns:
            System resource check results
        """
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            status = 'healthy'
            if cpu_percent > 90 or memory.percent > 90 or disk.percent > 90:
                status = 'critical'
            elif cpu_percent > 70 or memory.percent > 70 or disk.percent > 70:
                status = 'warning'
            
            return {
                'status': status,
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'disk_percent': disk.percent,
                'memory_available': memory.available,
                'disk_free': disk.free
            }
        except Exception as e:
            return {
                'status': 'critical',
                'error': str(e)
            }
    
    def _check_provider_connectivity(self) -> Dict[str, Any]:
        """
        Check cloud provider connectivity.
        
        Returns:
            Provider connectivity check results
        """
        providers = {}
        
        # Check AWS
        if self.config.aws.enabled:
            providers['aws'] = self._check_aws_connectivity()
        
        # Check Azure
        if self.config.azure.enabled:
            providers['azure'] = self._check_azure_connectivity()
        
        # Check GCP
        if self.config.gcp.enabled:
            providers['gcp'] = self._check_gcp_connectivity()
        
        overall_status = 'healthy'
        if any(p['status'] == 'critical' for p in providers.values()):
            overall_status = 'critical'
        elif any(p['status'] == 'warning' for p in providers.values()):
            overall_status = 'warning'
        
        return {
            'status': overall_status,
            'providers': providers
        }
    
    def _check_aws_connectivity(self) -> Dict[str, Any]:
        """
        Check AWS connectivity.
        
        Returns:
            AWS connectivity check results
        """
        try:
            import boto3
            
            # Test basic AWS connectivity
            sts = boto3.client('sts')
            response = sts.get_caller_identity()
            
            return {
                'status': 'healthy',
                'account_id': response['Account'],
                'user_id': response['UserId'],
                'arn': response['Arn']
            }
        except Exception as e:
            return {
                'status': 'critical',
                'error': str(e)
            }
    
    def _check_azure_connectivity(self) -> Dict[str, Any]:
        """
        Check Azure connectivity.
        
        Returns:
            Azure connectivity check results
        """
        try:
            from azure.identity import DefaultAzureCredential
            from azure.mgmt.subscription import SubscriptionClient
            
            # Test basic Azure connectivity
            credential = DefaultAzureCredential()
            client = SubscriptionClient(credential)
            subscriptions = list(client.subscriptions.list())
            
            return {
                'status': 'healthy',
                'subscriptions_count': len(subscriptions)
            }
        except Exception as e:
            return {
                'status': 'critical',
                'error': str(e)
            }
    
    def _check_gcp_connectivity(self) -> Dict[str, Any]:
        """
        Check GCP connectivity.
        
        Returns:
            GCP connectivity check results
        """
        try:
            from google.cloud import storage
            
            # Test basic GCP connectivity
            client = storage.Client()
            buckets = list(client.list_buckets(max_results=1))
            
            return {
                'status': 'healthy',
                'project_id': client.project
            }
        except Exception as e:
            return {
                'status': 'critical',
                'error': str(e)
            }
    
    def _check_configuration(self) -> Dict[str, Any]:
        """
        Check configuration validity.
        
        Returns:
            Configuration check results
        """
        try:
            # Validate configuration
            from .config import validate_config
            validation = validate_config(self.config)
            
            return {
                'status': 'healthy' if validation['valid'] else 'critical',
                'valid': validation['valid'],
                'errors': validation.get('errors', [])
            }
        except Exception as e:
            return {
                'status': 'critical',
                'error': str(e)
            }
    
    def _check_disk_space(self) -> Dict[str, Any]:
        """
        Check disk space.
        
        Returns:
            Disk space check results
        """
        try:
            disk = psutil.disk_usage(self.config.output_dir)
            percent_used = disk.percent
            
            status = 'healthy'
            if percent_used > 90:
                status = 'critical'
            elif percent_used > 70:
                status = 'warning'
            
            return {
                'status': status,
                'percent_used': percent_used,
                'free_gb': disk.free / (1024**3),
                'total_gb': disk.total / (1024**3)
            }
        except Exception as e:
            return {
                'status': 'critical',
                'error': str(e)
            }
    
    def _check_memory_usage(self) -> Dict[str, Any]:
        """
        Check memory usage.
        
        Returns:
            Memory usage check results
        """
        try:
            memory = psutil.virtual_memory()
            percent_used = memory.percent
            
            status = 'healthy'
            if percent_used > 90:
                status = 'critical'
            elif percent_used > 70:
                status = 'warning'
            
            return {
                'status': status,
                'percent_used': percent_used,
                'available_gb': memory.available / (1024**3),
                'total_gb': memory.total / (1024**3)
            }
        except Exception as e:
            return {
                'status': 'critical',
                'error': str(e)
            }
    
    def _monitor_background(self) -> None:
        """
        Background monitoring thread.
        """
        while True:
            try:
                # Update system metrics
                self.metrics['memory_usage'] = psutil.virtual_memory().percent
                self.metrics['cpu_usage'] = psutil.cpu_percent(interval=1)
                
                # Log metrics periodically
                self.logger.debug(f"System metrics: CPU={self.metrics['cpu_usage']}%, "
                                f"Memory={self.metrics['memory_usage']}%")
                
                time.sleep(60)  # Check every minute
                
            except Exception as e:
                self.logger.error(f"Error in background monitoring: {e}")
                time.sleep(60)
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get current metrics.
        
        Returns:
            Current metrics
        """
        return {
            **self.metrics,
            'health_status': self.health_status,
            'timestamp': datetime.now().isoformat()
        }
    
    def record_request(self, success: bool, response_time: float) -> None:
        """
        Record request metrics.
        
        Args:
            success: Whether the request was successful
            response_time: Response time in seconds
        """
        self.metrics['requests_total'] += 1
        
        if success:
            self.metrics['requests_successful'] += 1
        else:
            self.metrics['requests_failed'] += 1
        
        # Update average response time
        total_requests = self.metrics['requests_total']
        current_avg = self.metrics['average_response_time']
        self.metrics['average_response_time'] = (
            (current_avg * (total_requests - 1) + response_time) / total_requests
        )
    
    def get_alerts(self) -> List[Dict[str, Any]]:
        """
        Get current alerts.
        
        Returns:
            List of alerts
        """
        alerts = []
        
        # Check health status
        if self.health_status['overall'] == 'critical':
            alerts.append({
                'level': 'critical',
                'message': 'System health is critical',
                'timestamp': datetime.now().isoformat()
            })
        
        # Check metrics
        if self.metrics['memory_usage'] > 90:
            alerts.append({
                'level': 'warning',
                'message': f"High memory usage: {self.metrics['memory_usage']:.1f}%",
                'timestamp': datetime.now().isoformat()
            })
        
        if self.metrics['cpu_usage'] > 90:
            alerts.append({
                'level': 'warning',
                'message': f"High CPU usage: {self.metrics['cpu_usage']:.1f}%",
                'timestamp': datetime.now().isoformat()
            })
        
        return alerts


class MetricsCollector:
    """
    Metrics collector for FinOpsOptimizer.
    """
    
    def __init__(self, config: Config):
        """
        Initialize MetricsCollector.
        
        Args:
            config: Configuration object
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Metrics storage
        self.metrics_file = Path(config.output_dir) / "metrics.json"
        self.metrics_file.parent.mkdir(exist_ok=True)
        
        # Load existing metrics
        self.metrics = self._load_metrics()
    
    def _load_metrics(self) -> Dict[str, Any]:
        """
        Load metrics from file.
        
        Returns:
            Loaded metrics
        """
        if self.metrics_file.exists():
            try:
                with open(self.metrics_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.error(f"Error loading metrics: {e}")
        
        return {
            'cost_analysis': [],
            'optimizations': [],
            'performance': [],
            'errors': []
        }
    
    def _save_metrics(self) -> None:
        """Save metrics to file."""
        try:
            with open(self.metrics_file, 'w') as f:
                json.dump(self.metrics, f, indent=2, default=str)
        except Exception as e:
            self.logger.error(f"Error saving metrics: {e}")
    
    def record_cost_analysis(self, 
                           provider: str,
                           total_cost: float,
                           duration: float,
                           success: bool) -> None:
        """
        Record cost analysis metrics.
        
        Args:
            provider: Cloud provider
            total_cost: Total cost
            duration: Analysis duration
            success: Whether analysis was successful
        """
        metric = {
            'timestamp': datetime.now().isoformat(),
            'provider': provider,
            'total_cost': total_cost,
            'duration': duration,
            'success': success
        }
        
        self.metrics['cost_analysis'].append(metric)
        
        # Keep only last 1000 entries
        if len(self.metrics['cost_analysis']) > 1000:
            self.metrics['cost_analysis'] = self.metrics['cost_analysis'][-1000:]
        
        self._save_metrics()
    
    def record_optimization(self,
                          provider: str,
                          recommendations_count: int,
                          potential_savings: float,
                          duration: float,
                          success: bool) -> None:
        """
        Record optimization metrics.
        
        Args:
            provider: Cloud provider
            recommendations_count: Number of recommendations
            potential_savings: Potential savings
            duration: Optimization duration
            success: Whether optimization was successful
        """
        metric = {
            'timestamp': datetime.now().isoformat(),
            'provider': provider,
            'recommendations_count': recommendations_count,
            'potential_savings': potential_savings,
            'duration': duration,
            'success': success
        }
        
        self.metrics['optimizations'].append(metric)
        
        # Keep only last 1000 entries
        if len(self.metrics['optimizations']) > 1000:
            self.metrics['optimizations'] = self.metrics['optimizations'][-1000:]
        
        self._save_metrics()
    
    def record_performance(self, operation: str, duration: float) -> None:
        """
        Record performance metrics.
        
        Args:
            operation: Operation name
            duration: Operation duration
        """
        metric = {
            'timestamp': datetime.now().isoformat(),
            'operation': operation,
            'duration': duration
        }
        
        self.metrics['performance'].append(metric)
        
        # Keep only last 1000 entries
        if len(self.metrics['performance']) > 1000:
            self.metrics['performance'] = self.metrics['performance'][-1000:]
        
        self._save_metrics()
    
    def record_error(self, error: str, context: str) -> None:
        """
        Record error metrics.
        
        Args:
            error: Error message
            context: Error context
        """
        metric = {
            'timestamp': datetime.now().isoformat(),
            'error': error,
            'context': context
        }
        
        self.metrics['errors'].append(metric)
        
        # Keep only last 1000 entries
        if len(self.metrics['errors']) > 1000:
            self.metrics['errors'] = self.metrics['errors'][-1000:]
        
        self._save_metrics()
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """
        Get metrics summary.
        
        Returns:
            Metrics summary
        """
        if not self.metrics['cost_analysis']:
            return {}
        
        # Calculate averages
        total_costs = [m['total_cost'] for m in self.metrics['cost_analysis'] if m['success']]
        durations = [m['duration'] for m in self.metrics['cost_analysis'] if m['success']]
        
        return {
            'total_analyses': len(self.metrics['cost_analysis']),
            'successful_analyses': len([m for m in self.metrics['cost_analysis'] if m['success']]),
            'average_cost': sum(total_costs) / len(total_costs) if total_costs else 0,
            'average_duration': sum(durations) / len(durations) if durations else 0,
            'total_optimizations': len(self.metrics['optimizations']),
            'total_errors': len(self.metrics['errors'])
        } 
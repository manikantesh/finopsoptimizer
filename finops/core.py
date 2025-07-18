"""
Core FinOpsOptimizer class that orchestrates cost optimization across cloud providers.
"""

import os
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from pathlib import Path

from .config import Config, load_config
from .cost_allocation import CostAllocator
from .rightsizing import RightsizingAnalyzer
from .autoscaling import AutoscalingOptimizer
from .forecasting import CostForecaster
from .reporting import ReportGenerator
from .aws import AWSProvider
from .azure import AzureProvider
from .gcp import GCPProvider
from .oracle import OracleProvider


class FinOpsOptimizer:
    """
    Main class for FinOps cost optimization across AWS, Azure, and GCP.
    
    This class provides a unified interface for cost optimization operations
    across multiple cloud providers.
    """
    
    def __init__(self, config: Optional[Config] = None):
        """
        Initialize FinOpsOptimizer.
        
        Args:
            config: Configuration object. If None, loads from default locations.
        """
        self.config = config or load_config()
        self.logger = self._setup_logging()
        
        # Initialize cloud providers
        self.providers = {}
        self._initialize_providers()
        
        # Initialize optimization components
        self.cost_allocator = CostAllocator(self.config)
        self.rightsizing_analyzer = RightsizingAnalyzer(self.config)
        self.autoscaling_optimizer = AutoscalingOptimizer(self.config)
        self.cost_forecaster = CostForecaster(self.config)
        self.report_generator = ReportGenerator(self.config)
        
        # Results storage
        self.cost_data = {}
        self.optimization_results = {}
        self.recommendations = []
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration."""
        logger = logging.getLogger("FinOpsOptimizer")
        logger.setLevel(getattr(logging, self.config.log_level))
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _initialize_providers(self) -> None:
        """Initialize cloud provider clients."""
        if self.config.aws.enabled:
            try:
                self.providers['aws'] = AWSProvider(self.config.aws)
                self.logger.info("AWS provider initialized successfully")
            except Exception as e:
                self.logger.error(f"Failed to initialize AWS provider: {e}")
        
        if self.config.azure.enabled:
            try:
                self.providers['azure'] = AzureProvider(self.config.azure)
                self.logger.info("Azure provider initialized successfully")
            except Exception as e:
                self.logger.error(f"Failed to initialize Azure provider: {e}")
        
        if self.config.gcp.enabled:
            try:
                self.providers['gcp'] = GCPProvider(self.config.gcp)
                self.logger.info("GCP provider initialized successfully")
            except Exception as e:
                self.logger.error(f"Failed to initialize GCP provider: {e}")
        
        if self.config.oracle.enabled:
            try:
                self.providers['oracle'] = OracleProvider(self.config.oracle)
                self.logger.info("Oracle Cloud provider initialized successfully")
            except Exception as e:
                self.logger.error(f"Failed to initialize Oracle Cloud provider: {e}")
    
    def analyze_costs(self, 
                     start_date: Optional[datetime] = None,
                     end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Analyze costs across all enabled cloud providers.
        
        Args:
            start_date: Start date for cost analysis
            end_date: End date for cost analysis
            
        Returns:
            Dictionary containing cost analysis results
        """
        if not start_date:
            start_date = datetime.now() - timedelta(days=30)
        if not end_date:
            end_date = datetime.now()
        
        self.logger.info(f"Starting cost analysis from {start_date} to {end_date}")
        
        results = {}
        total_cost = 0
        
        for provider_name, provider in self.providers.items():
            try:
                self.logger.info(f"Analyzing costs for {provider_name}")
                provider_results = provider.analyze_costs(start_date, end_date)
                results[provider_name] = provider_results
                total_cost += provider_results.get('total_cost', 0)
                
                self.logger.info(f"{provider_name} total cost: ${provider_results.get('total_cost', 0):.2f}")
                
            except Exception as e:
                self.logger.error(f"Error analyzing costs for {provider_name}: {e}")
                results[provider_name] = {'error': str(e)}
        
        results['summary'] = {
            'total_cost': total_cost,
            'providers_analyzed': list(self.providers.keys()),
            'analysis_period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat()
            }
        }
        
        self.cost_data = results
        return results
    
    def generate_recommendations(self) -> List[Dict[str, Any]]:
        """
        Generate optimization recommendations across all providers.
        
        Returns:
            List of optimization recommendations
        """
        self.logger.info("Generating optimization recommendations")
        
        recommendations = []
        
        # Rightsizing recommendations
        for provider_name, provider in self.providers.items():
            try:
                rightsizing_recs = self.rightsizing_analyzer.analyze_provider(
                    provider, self.cost_data.get(provider_name, {})
                )
                recommendations.extend(rightsizing_recs)
                
            except Exception as e:
                self.logger.error(f"Error generating rightsizing recommendations for {provider_name}: {e}")
        
        # Autoscaling recommendations
        for provider_name, provider in self.providers.items():
            try:
                autoscaling_recs = self.autoscaling_optimizer.analyze_provider(
                    provider, self.cost_data.get(provider_name, {})
                )
                recommendations.extend(autoscaling_recs)
                
            except Exception as e:
                self.logger.error(f"Error generating autoscaling recommendations for {provider_name}: {e}")
        
        # Cost allocation recommendations
        allocation_recs = self.cost_allocator.generate_recommendations(self.cost_data)
        recommendations.extend(allocation_recs)
        
        # Sort recommendations by potential savings
        recommendations.sort(key=lambda x: x.get('potential_savings', 0), reverse=True)
        
        self.recommendations = recommendations
        return recommendations
    
    def allocate_costs(self, allocation_rules: Dict[str, Any]) -> Dict[str, Any]:
        """
        Allocate costs based on provided rules.
        
        Args:
            allocation_rules: Rules for cost allocation
            
        Returns:
            Cost allocation results
        """
        return self.cost_allocator.allocate_costs(self.cost_data, allocation_rules)
    
    def forecast_costs(self, 
                      forecast_period: int = 30,
                      include_recommendations: bool = True) -> Dict[str, Any]:
        """
        Forecast future costs based on historical data.
        
        Args:
            forecast_period: Number of days to forecast
            include_recommendations: Whether to include optimization impact
            
        Returns:
            Cost forecast results
        """
        return self.cost_forecaster.forecast(
            self.cost_data, 
            forecast_period, 
            include_recommendations
        )
    
    def generate_report(self, 
                       report_type: str = "comprehensive",
                       output_format: str = "html") -> str:
        """
        Generate optimization report.
        
        Args:
            report_type: Type of report (comprehensive, summary, recommendations)
            output_format: Output format (html, pdf, json)
            
        Returns:
            Path to generated report
        """
        return self.report_generator.generate_report(
            cost_data=self.cost_data,
            recommendations=self.recommendations,
            report_type=report_type,
            output_format=output_format
        )
    
    def optimize_all(self, 
                    generate_report: bool = True,
                    save_results: bool = True) -> Dict[str, Any]:
        """
        Run complete optimization pipeline.
        
        Args:
            generate_report: Whether to generate a report
            save_results: Whether to save results to file
            
        Returns:
            Complete optimization results
        """
        self.logger.info("Starting complete optimization pipeline")
        
        # Step 1: Analyze costs
        cost_analysis = self.analyze_costs()
        
        # Step 2: Generate recommendations
        recommendations = self.generate_recommendations()
        
        # Step 3: Forecast costs
        forecast = self.forecast_costs()
        
        # Step 4: Generate report if requested
        report_path = None
        if generate_report:
            report_path = self.generate_report()
        
        # Step 5: Save results if requested
        if save_results:
            self._save_results(cost_analysis, recommendations, forecast)
        
        results = {
            'cost_analysis': cost_analysis,
            'recommendations': recommendations,
            'forecast': forecast,
            'report_path': report_path,
            'summary': {
                'total_recommendations': len(recommendations),
                'total_potential_savings': sum(r.get('potential_savings', 0) for r in recommendations),
                'providers_analyzed': list(self.providers.keys())
            }
        }
        
        self.optimization_results = results
        return results
    
    def _save_results(self, 
                     cost_analysis: Dict[str, Any],
                     recommendations: List[Dict[str, Any]],
                     forecast: Dict[str, Any]) -> None:
        """Save optimization results to file."""
        import json
        
        output_dir = Path(self.config.output_dir)
        output_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        results = {
            'timestamp': timestamp,
            'cost_analysis': cost_analysis,
            'recommendations': recommendations,
            'forecast': forecast
        }
        
        results_file = output_dir / f"optimization_results_{timestamp}.json"
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        self.logger.info(f"Results saved to {results_file}")
    
    def get_provider_status(self) -> Dict[str, bool]:
        """Get status of all cloud providers."""
        return {
            name: provider.is_connected() 
            for name, provider in self.providers.items()
        }
    
    def validate_credentials(self) -> Dict[str, bool]:
        """Validate credentials for all providers."""
        return self.config.validate_credentials() 
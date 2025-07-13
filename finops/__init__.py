"""
FinOpsOptimizer - A comprehensive cost optimization toolkit for AWS, Azure, and GCP.

This library provides end-to-end cost optimization capabilities including:
- Cost allocation and tagging
- Rightsizing recommendations
- Autoscaling optimization
- Multi-cloud cost analysis
- Cost forecasting and budgeting
- Resource optimization recommendations

Quick Start:
    from finops import FinOpsOptimizer
    
    optimizer = FinOpsOptimizer()
    optimizer.analyze_costs()
    optimizer.generate_recommendations()
"""

from .core import FinOpsOptimizer
from .cost_allocation import CostAllocator
from .rightsizing import RightsizingAnalyzer
from .autoscaling import AutoscalingOptimizer
from .forecasting import CostForecaster
from .reporting import ReportGenerator
from .config import Config

# Version info
__version__ = "1.0.0"
__author__ = "FinOpsOptimizer Team"
__email__ = "support@finopsoptimizer.com"

# Main exports
__all__ = [
    "FinOpsOptimizer",
    "CostAllocator", 
    "RightsizingAnalyzer",
    "AutoscalingOptimizer",
    "CostForecaster",
    "ReportGenerator",
    "Config",
    "__version__",
] 
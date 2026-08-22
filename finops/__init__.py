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

Attributes below are loaded lazily (PEP 562) so that importing an unrelated
submodule -- e.g. ``finops.agentops``, which has its own much lighter
dependency set (no pandas/boto3/azure/gcp/scikit-learn) -- doesn't pull in
every cloud-provider SDK just to execute this file.
"""

import importlib
from typing import Any

__version__ = "2.0.0"
__author__ = "FinOpsOptimizer Team"
__email__ = "support@finopsoptimizer.com"

_LAZY_ATTRS = {
    "FinOpsOptimizer": (".core", "FinOpsOptimizer"),
    "CostAllocator": (".cost_allocation", "CostAllocator"),
    "RightsizingAnalyzer": (".rightsizing", "RightsizingAnalyzer"),
    "AutoscalingOptimizer": (".autoscaling", "AutoscalingOptimizer"),
    "CostForecaster": (".forecasting", "CostForecaster"),
    "ReportGenerator": (".reporting", "ReportGenerator"),
    "Config": (".config", "Config"),
    "DataIngestionPipeline": (".data_ingestion", "DataIngestionPipeline"),
    "VMRightsizingAnalyzer": (".vm_rightsizing", "VMRightsizingAnalyzer"),
    "CostOptimizationScheduler": (".scheduler", "CostOptimizationScheduler"),
    "UnattachedDisksRemediator": (".unattached_disks", "UnattachedDisksRemediator"),
    "ReservedInstanceAnalyzer": (".reserved_instances", "ReservedInstanceAnalyzer"),
    "RealTimePricingEngine": (".pricing_engine", "RealTimePricingEngine"),
    "EnterpriseDiscount": (".pricing_engine", "EnterpriseDiscount"),
}

__all__ = list(_LAZY_ATTRS) + ["__version__"]


def __getattr__(name: str) -> Any:
    target = _LAZY_ATTRS.get(name)
    if target is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    module_name, attr_name = target
    module = importlib.import_module(module_name, __name__)
    value = getattr(module, attr_name)
    globals()[name] = value
    return value

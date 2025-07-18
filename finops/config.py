"""
Configuration management for FinOpsOptimizer.
Handles settings for AWS, Azure, GCP, and optimization parameters.
"""

import os
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from pathlib import Path
import yaml
from pydantic import BaseModel, Field


class CloudConfig(BaseModel):
    """Configuration for a specific cloud provider."""
    enabled: bool = True
    credentials_path: Optional[str] = None
    region: Optional[str] = None
    project_id: Optional[str] = None  # For GCP
    subscription_id: Optional[str] = None  # For Azure
    account_id: Optional[str] = None  # For AWS


class OptimizationConfig(BaseModel):
    """Configuration for optimization parameters."""
    # Rightsizing thresholds
    cpu_utilization_threshold: float = 0.7
    memory_utilization_threshold: float = 0.8
    cost_savings_threshold: float = 0.1  # 10% minimum savings
    
    # Autoscaling parameters
    min_instances: int = 1
    max_instances: int = 10
    scale_up_threshold: float = 0.8
    scale_down_threshold: float = 0.3
    
    # Cost allocation
    default_allocation_method: str = "proportional"
    tag_based_allocation: bool = True
    
    # Reporting
    report_format: str = "html"  # html, pdf, json
    include_charts: bool = True
    include_recommendations: bool = True


class PricingConfig(BaseModel):
    """Configuration for pricing engine."""
    # Real-time pricing settings
    enable_real_time_pricing: bool = True
    cache_ttl: int = 3600  # 1 hour
    fallback_to_static: bool = True
    
    # Enterprise discounts
    enterprise_discounts: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Custom rates
    custom_rates: Dict[str, float] = Field(default_factory=dict)
    
    # Pricing sources priority
    pricing_sources: List[str] = Field(default_factory=lambda: [
        "enterprise_contract", "cloud_provider_api", "pricing_api", "cached"
    ])


class Config(BaseModel):
    """Main configuration class for FinOpsOptimizer."""
    
    # Cloud provider configurations
    aws: CloudConfig = Field(default_factory=CloudConfig)
    azure: CloudConfig = Field(default_factory=CloudConfig)
    gcp: CloudConfig = Field(default_factory=CloudConfig)
    oracle: CloudConfig = Field(default_factory=CloudConfig)
    
    # Optimization settings
    optimization: OptimizationConfig = Field(default_factory=OptimizationConfig)
    
    # Pricing settings
    pricing: PricingConfig = Field(default_factory=PricingConfig)
    
    # General settings
    output_dir: str = "./finops_reports"
    log_level: str = "INFO"
    enable_notifications: bool = False
    notification_webhook: Optional[str] = None
    
    # Data retention
    data_retention_days: int = 90
    
    @classmethod
    def from_file(cls, config_path: str) -> "Config":
        """Load configuration from YAML file."""
        if not os.path.exists(config_path):
            return cls()
        
        with open(config_path, 'r') as f:
            config_data = yaml.safe_load(f)
        
        return cls(**config_data)
    
    def save_to_file(self, config_path: str) -> None:
        """Save configuration to YAML file."""
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        
        with open(config_path, 'w') as f:
            yaml.dump(self.dict(), f, default_flow_style=False, indent=2)
    
    def validate_credentials(self) -> Dict[str, bool]:
        """Validate cloud provider credentials."""
        results = {}
        
        # AWS credentials
        if self.aws.enabled:
            aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
            aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
            results['aws'] = bool(aws_access_key and aws_secret_key)
        
        # Azure credentials
        if self.azure.enabled:
            azure_client_id = os.getenv('AZURE_CLIENT_ID')
            azure_client_secret = os.getenv('AZURE_CLIENT_SECRET')
            azure_tenant_id = os.getenv('AZURE_TENANT_ID')
            results['azure'] = bool(azure_client_id and azure_client_secret and azure_tenant_id)
        
        # GCP credentials
        if self.gcp.enabled:
            gcp_credentials = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
            results['gcp'] = bool(gcp_credentials and os.path.exists(gcp_credentials))
        
        # Oracle Cloud credentials
        if self.oracle.enabled:
            oci_config_file = os.getenv('OCI_CONFIG_FILE', '~/.oci/config')
            oci_profile = os.getenv('OCI_PROFILE', 'DEFAULT')
            results['oracle'] = bool(os.path.exists(os.path.expanduser(oci_config_file)))
        
        return results


def get_default_config() -> Config:
    """Get default configuration."""
    return Config()


def load_config(config_path: Optional[str] = None) -> Config:
    """Load configuration from file or return default."""
    if config_path and os.path.exists(config_path):
        return Config.from_file(config_path)
    
    # Try to load from default locations
    default_paths = [
        "./finops_config.yml",
        "./config/finops.yml",
        os.path.expanduser("~/.finops/config.yml")
    ]
    
    for path in default_paths:
        if os.path.exists(path):
            return Config.from_file(path)
    
    return get_default_config() 
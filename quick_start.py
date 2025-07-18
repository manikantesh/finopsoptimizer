#!/usr/bin/env python3
"""
FinOps Optimizer - Quick Start Setup Script

This script provides automated setup for the FinOps Optimizer platform with:
- Dependency installation and validation
- Virtual environment setup (optional)
- Configuration file creation
- Cloud provider credential setup
- Initial testing and validation

Usage:
    python quick_start.py [--venv] [--skip-deps] [--config-only]
"""

import os
import sys
import subprocess
import json
import yaml
from pathlib import Path
import argparse
import platform

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(60)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")

def print_success(text):
    print(f"{Colors.OKGREEN}✅ {text}{Colors.ENDC}")

def print_info(text):
    print(f"{Colors.OKBLUE}ℹ️  {text}{Colors.ENDC}")

def print_warning(text):
    print(f"{Colors.WARNING}⚠️  {text}{Colors.ENDC}")

def print_error(text):
    print(f"{Colors.FAIL}❌ {text}{Colors.ENDC}")

def check_python_version():
    """Check if Python version is compatible."""
    print_info("Checking Python version...")
    
    if sys.version_info < (3, 8):
        print_error(f"Python 3.8+ required. Current version: {sys.version}")
        print_info("Please upgrade Python and try again.")
        return False
    
    print_success(f"Python {sys.version.split()[0]} - Compatible")
    return True

def check_system_requirements():
    """Check system requirements and dependencies."""
    print_info("Checking system requirements...")
    
    system = platform.system()
    print_info(f"Operating System: {system} {platform.release()}")
    
    # Check for required system tools
    required_tools = ['git', 'pip']
    missing_tools = []
    
    for tool in required_tools:
        try:
            subprocess.run([tool, '--version'], capture_output=True, check=True)
            print_success(f"{tool} is available")
        except (subprocess.CalledProcessError, FileNotFoundError):
            missing_tools.append(tool)
            print_error(f"{tool} is not available")
    
    if missing_tools:
        print_error(f"Missing required tools: {', '.join(missing_tools)}")
        print_info("Please install missing tools and try again.")
        return False
    
    return True

def create_virtual_environment():
    """Create and activate virtual environment."""
    print_info("Setting up virtual environment...")
    
    venv_path = Path("venv")
    if venv_path.exists():
        print_warning("Virtual environment already exists")
        return True
    
    try:
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print_success("Virtual environment created")
        
        # Provide activation instructions
        system = platform.system()
        if system == "Windows":
            activate_cmd = "venv\\Scripts\\activate"
        else:
            activate_cmd = "source venv/bin/activate"
        
        print_info(f"To activate: {activate_cmd}")
        return True
        
    except subprocess.CalledProcessError as e:
        print_error(f"Failed to create virtual environment: {e}")
        return False

def install_dependencies():
    """Install required Python packages."""
    print_info("Installing dependencies...")
    
    # Core dependencies
    dependencies = [
        "boto3>=1.26.0",
        "azure-identity>=1.12.0",
        "azure-mgmt-compute>=29.0.0",
        "azure-mgmt-monitor>=5.0.0",
        "google-cloud-compute>=1.8.0",
        "google-cloud-monitoring>=2.11.0",
        "oci>=2.88.0",
        "requests>=2.28.0",
        "pyyaml>=6.0",
        "click>=8.0.0",
        "rich>=12.0.0",
        "pandas>=1.5.0",
        "numpy>=1.21.0",
        "matplotlib>=3.5.0",
        "plotly>=5.11.0",
        "jinja2>=3.0.0",
        "schedule>=1.2.0",
        "python-dateutil>=2.8.0"
    ]
    
    # Optional dependencies for enhanced features
    optional_dependencies = [
        "mkdocs-material>=8.5.0",
        "mike>=1.1.0",
        "jupyter>=1.0.0",
        "scikit-learn>=1.1.0",
        "flask>=2.2.0"
    ]
    
    try:
        # Install core dependencies
        print_info("Installing core dependencies...")
        for dep in dependencies:
            print_info(f"Installing {dep.split('>=')[0]}...")
            subprocess.run([sys.executable, "-m", "pip", "install", dep], 
                         check=True, capture_output=True)
        
        print_success("Core dependencies installed")
        
        # Install optional dependencies (non-critical)
        print_info("Installing optional dependencies...")
        for dep in optional_dependencies:
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", dep], 
                             check=True, capture_output=True)
                print_success(f"Installed {dep.split('>=')[0]}")
            except subprocess.CalledProcessError:
                print_warning(f"Optional dependency {dep.split('>=')[0]} failed to install")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print_error(f"Failed to install dependencies: {e}")
        return False

def create_config_file():
    """Create default configuration file."""
    print_info("Creating configuration file...")
    
    config_path = Path("finops_config.yml")
    if config_path.exists():
        print_warning("Configuration file already exists")
        response = input("Overwrite existing config? (y/N): ").lower()
        if response != 'y':
            return True
    
    config = {
        'general': {
            'log_level': 'INFO',
            'output_format': 'json',
            'cache_ttl': 3600,
            'max_workers': 4
        },
        'providers': {
            'aws': {
                'enabled': True,
                'regions': ['us-east-1', 'us-west-2'],
                'profile': 'default',
                'assume_role_arn': None
            },
            'azure': {
                'enabled': True,
                'subscription_id': None,
                'tenant_id': None,
                'client_id': None,
                'client_secret': None
            },
            'gcp': {
                'enabled': True,
                'project_id': None,
                'credentials_path': None,
                'regions': ['us-central1', 'us-east1']
            },
            'oracle': {
                'enabled': True,
                'config_file': '~/.oci/config',
                'profile': 'DEFAULT',
                'compartment_id': None
            }
        },
        'optimization': {
            'rightsizing': {
                'enabled': True,
                'cpu_threshold': 80,
                'memory_threshold': 80,
                'observation_days': 30
            },
            'reserved_instances': {
                'enabled': True,
                'minimum_usage': 70,
                'term_length': 12
            },
            'unattached_resources': {
                'enabled': True,
                'age_threshold_days': 7
            }
        },
        'reporting': {
            'output_directory': './reports',
            'formats': ['html', 'json', 'csv'],
            'email_notifications': False
        }
    }
    
    try:
        with open(config_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False, indent=2)
        
        print_success(f"Configuration file created: {config_path}")
        print_info("Edit finops_config.yml to customize settings")
        return True
        
    except Exception as e:
        print_error(f"Failed to create configuration file: {e}")
        return False

def setup_cloud_credentials():
    """Guide user through cloud provider credential setup."""
    print_info("Setting up cloud provider credentials...")
    print_info("This step is optional but required for live cost optimization")
    
    setup_aws = input("\nSetup AWS credentials? (y/N): ").lower() == 'y'
    if setup_aws:
        print_info("\nAWS Setup Options:")
        print_info("1. AWS CLI: Run 'aws configure'")
        print_info("2. Environment variables: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY")
        print_info("3. IAM roles (for EC2 instances)")
        print_info("4. AWS profiles in ~/.aws/credentials")
        
    setup_azure = input("\nSetup Azure credentials? (y/N): ").lower() == 'y'
    if setup_azure:
        print_info("\nAzure Setup Options:")
        print_info("1. Azure CLI: Run 'az login'")
        print_info("2. Service Principal: Set AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, AZURE_TENANT_ID")
        print_info("3. Managed Identity (for Azure VMs)")
        
    setup_gcp = input("\nSetup Google Cloud credentials? (y/N): ").lower() == 'y'
    if setup_gcp:
        print_info("\nGoogle Cloud Setup Options:")
        print_info("1. gcloud CLI: Run 'gcloud auth application-default login'")
        print_info("2. Service Account: Set GOOGLE_APPLICATION_CREDENTIALS")
        print_info("3. Compute Engine default service account")
        
    setup_oracle = input("\nSetup Oracle Cloud credentials? (y/N): ").lower() == 'y'
    if setup_oracle:
        print_info("\nOracle Cloud Setup Options:")
        print_info("1. OCI CLI: Run 'oci setup config'")
        print_info("2. Config file: ~/.oci/config")
        print_info("3. Instance principal (for OCI instances)")
    
    print_info("\n📚 For detailed credential setup, see:")
    print_info("   - docs/installation.md")
    print_info("   - docs/configuration.md")

def run_basic_tests():
    """Run basic functionality tests."""
    print_info("Running basic functionality tests...")
    
    try:
        # Test imports
        print_info("Testing module imports...")
        import finops
        from finops.core import FinOpsOptimizer
        from finops.config import Config
        print_success("Core modules imported successfully")
        
        # Test configuration loading
        print_info("Testing configuration loading...")
        config = Config()
        print_success("Configuration loaded successfully")
        
        # Test optimizer initialization
        print_info("Testing optimizer initialization...")
        optimizer = FinOpsOptimizer()
        print_success("Optimizer initialized successfully")
        
        return True
        
    except ImportError as e:
        print_error(f"Import error: {e}")
        print_info("Try running: python validate_setup.py")
        return False
    except Exception as e:
        print_error(f"Test failed: {e}")
        return False

def create_example_script():
    """Create a simple example script for testing."""
    print_info("Creating example script...")
    
    example_path = Path("test_finops.py")
    
    example_code = '''#!/usr/bin/env python3
"""
FinOps Optimizer - Basic Test Script

This script demonstrates basic functionality without requiring cloud credentials.
"""

from finops.core import FinOpsOptimizer
from finops.config import Config
import json

def main():
    print("🚀 FinOps Optimizer - Basic Test")
    print("=" * 40)
    
    try:
        # Initialize configuration
        print("\\n1. Loading configuration...")
        config = Config()
        print("✅ Configuration loaded")
        
        # Initialize optimizer
        print("\\n2. Initializing optimizer...")
        optimizer = FinOpsOptimizer()
        print("✅ Optimizer initialized")
        
        # Test configuration access
        print("\\n3. Testing configuration access...")
        providers = config.get_enabled_providers()
        print(f"✅ Enabled providers: {', '.join(providers)}")
        
        # Test basic functionality
        print("\\n4. Testing basic functionality...")
        status = optimizer.get_status()
        print("✅ Status check completed")
        
        print("\\n🎉 All basic tests passed!")
        print("\\n📚 Next steps:")
        print("   - Configure cloud provider credentials")
        print("   - Run: python cli.py status")
        print("   - See documentation for advanced usage")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\\n🔍 Troubleshooting:")
        print("   - Run: python validate_setup.py")
        print("   - Check finops_config.yml")
        print("   - See docs/troubleshooting.md")

if __name__ == "__main__":
    main()
'''
    
    try:
        with open(example_path, 'w') as f:
            f.write(example_code)
        
        # Make executable on Unix systems
        if platform.system() != "Windows":
            os.chmod(example_path, 0o755)
        
        print_success(f"Example script created: {example_path}")
        return True
        
    except Exception as e:
        print_error(f"Failed to create example script: {e}")
        return False

def main():
    """Main setup function."""
    parser = argparse.ArgumentParser(description="FinOps Optimizer Quick Start Setup")
    parser.add_argument("--venv", action="store_true", help="Create virtual environment")
    parser.add_argument("--skip-deps", action="store_true", help="Skip dependency installation")
    parser.add_argument("--config-only", action="store_true", help="Only create configuration file")
    
    args = parser.parse_args()
    
    print_header("FinOps Optimizer - Quick Start Setup")
    print_info("This script will set up FinOps Optimizer on your system")
    
    # Basic system checks
    if not check_python_version():
        sys.exit(1)
    
    if not check_system_requirements():
        sys.exit(1)
    
    # Configuration-only mode
    if args.config_only:
        if create_config_file():
            print_success("Configuration file created successfully!")
        sys.exit(0)
    
    # Virtual environment setup
    if args.venv:
        if not create_virtual_environment():
            print_error("Virtual environment setup failed")
            sys.exit(1)
    
    # Dependency installation
    if not args.skip_deps:
        if not install_dependencies():
            print_error("Dependency installation failed")
            sys.exit(1)
    
    # Configuration file creation
    if not create_config_file():
        print_error("Configuration file creation failed")
        sys.exit(1)
    
    # Cloud credentials setup (optional)
    setup_cloud_credentials()
    
    # Basic functionality tests
    if not run_basic_tests():
        print_warning("Basic tests failed - setup may be incomplete")
    
    # Create example script
    create_example_script()
    
    # Final success message
    print_header("Setup Complete!")
    print_success("FinOps Optimizer has been set up successfully!")
    
    print("\n📚 Next Steps:")
    print_info("1. 🔍 Validate installation: python validate_setup.py")
    print_info("2. 🧪 Test basic functionality: python test_finops.py")
    print_info("3. ⚙️ Configure cloud credentials (see docs/configuration.md)")
    print_info("4. 🚀 Run CLI: python cli.py status")
    print_info("5. 📖 Read documentation: docs/index.md")
    
    print("\n📚 Documentation:")
    print_info("   - docs/installation.md - Detailed installation guide")
    print_info("   - docs/configuration.md - Configuration options")
    print_info("   - docs/tutorial.md - Getting started tutorial")
    print_info("   - examples/ - Usage examples")
    
    print(f"\n{Colors.OKGREEN}{Colors.BOLD}🎉 Ready to optimize your cloud costs!{Colors.ENDC}")

if __name__ == "__main__":
    main()
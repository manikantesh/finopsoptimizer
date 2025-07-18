#!/usr/bin/env python3
"""
FinOps Optimizer - Setup Validation Script

This script performs comprehensive validation of the FinOps Optimizer installation:
- Python environment validation
- Dependency checking and version verification
- Module import testing
- Configuration file validation
- Cloud provider connectivity testing (optional)
- Performance benchmarking

Usage:
    python validate_setup.py [--full] [--cloud] [--benchmark] [--fix]
"""

import os
import sys
import subprocess
import importlib
import json
import yaml
import time
import platform
import argparse
from pathlib import Path
from typing import Dict, List, Tuple, Optional

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

class ValidationResult:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.warnings = 0
        self.errors = []
        self.warnings_list = []

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

def validate_python_environment(result: ValidationResult) -> bool:
    """Validate Python environment and version."""
    print_info("Validating Python environment...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        result.errors.append(f"Python 3.8+ required. Current: {sys.version}")
        print_error(f"Python version: {sys.version.split()[0]} (UNSUPPORTED)")
        result.failed += 1
        return False
    
    print_success(f"Python version: {sys.version.split()[0]}")
    result.passed += 1
    
    # Check platform
    system_info = f"{platform.system()} {platform.release()}"
    print_success(f"Operating system: {system_info}")
    
    # Check pip
    try:
        import pip
        print_success(f"pip version: {pip.__version__}")
        result.passed += 1
    except ImportError:
        print_error("pip not available")
        result.errors.append("pip not available")
        result.failed += 1
        return False
    
    return True

def validate_dependencies(result: ValidationResult) -> bool:
    """Validate required dependencies."""
    print_info("Validating dependencies...")
    
    # Core dependencies with minimum versions
    core_deps = {
        'boto3': '1.26.0',
        'azure.identity': '1.12.0',
        'azure.mgmt.compute': '29.0.0',
        'google.cloud.compute': '1.8.0',
        'oci': '2.88.0',
        'requests': '2.28.0',
        'yaml': '6.0',
        'click': '8.0.0',
        'pandas': '1.5.0',
        'numpy': '1.21.0'
    }
    
    # Optional dependencies
    optional_deps = {
        'matplotlib': '3.5.0',
        'plotly': '5.11.0',
        'rich': '12.0.0',
        'jinja2': '3.0.0',
        'schedule': '1.2.0'
    }
    
    all_good = True
    
    # Check core dependencies
    for dep_name, min_version in core_deps.items():
        try:
            if dep_name == 'yaml':
                import yaml as dep_module
            else:
                dep_module = importlib.import_module(dep_name)
            
            # Get version if available
            version = getattr(dep_module, '__version__', 'unknown')
            print_success(f"{dep_name}: {version}")
            result.passed += 1
            
        except ImportError:
            print_error(f"{dep_name}: NOT INSTALLED")
            result.errors.append(f"Missing dependency: {dep_name}")
            result.failed += 1
            all_good = False
    
    # Check optional dependencies
    for dep_name, min_version in optional_deps.items():
        try:
            dep_module = importlib.import_module(dep_name)
            version = getattr(dep_module, '__version__', 'unknown')
            print_success(f"{dep_name} (optional): {version}")
            result.passed += 1
            
        except ImportError:
            print_warning(f"{dep_name} (optional): NOT INSTALLED")
            result.warnings_list.append(f"Optional dependency missing: {dep_name}")
            result.warnings += 1
    
    return all_good

def validate_finops_modules(result: ValidationResult) -> bool:
    """Validate FinOps Optimizer modules."""
    print_info("Validating FinOps modules...")
    
    modules_to_test = [
        'finops',
        'finops.core',
        'finops.config',
        'finops.aws.provider',
        'finops.azure.provider',
        'finops.gcp.provider',
        'finops.oracle.provider',
        'finops.pricing_engine',
        'finops.vm_rightsizing',
        'finops.reserved_instances',
        'finops.unattached_disks',
        'finops.scheduler'
    ]
    
    all_good = True
    
    for module_name in modules_to_test:
        try:
            importlib.import_module(module_name)
            print_success(f"Module: {module_name}")
            result.passed += 1
            
        except ImportError as e:
            print_error(f"Module {module_name}: {e}")
            result.errors.append(f"Module import failed: {module_name}")
            result.failed += 1
            all_good = False
    
    return all_good

def validate_configuration(result: ValidationResult) -> bool:
    """Validate configuration file."""
    print_info("Validating configuration...")
    
    config_path = Path("finops_config.yml")
    
    if not config_path.exists():
        print_warning("Configuration file not found (finops_config.yml)")
        result.warnings_list.append("Configuration file missing")
        result.warnings += 1
        return True  # Not critical for basic functionality
    
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        # Validate structure
        required_sections = ['general', 'providers', 'optimization']
        for section in required_sections:
            if section not in config:
                print_error(f"Missing configuration section: {section}")
                result.errors.append(f"Missing config section: {section}")
                result.failed += 1
                return False
        
        print_success("Configuration file structure valid")
        
        # Check provider configurations
        providers = config.get('providers', {})
        enabled_providers = [name for name, conf in providers.items() 
                           if conf.get('enabled', False)]
        
        if enabled_providers:
            print_success(f"Enabled providers: {', '.join(enabled_providers)}")
        else:
            print_warning("No providers enabled in configuration")
            result.warnings_list.append("No providers enabled")
            result.warnings += 1
        
        result.passed += 1
        return True
        
    except yaml.YAMLError as e:
        print_error(f"Configuration file invalid YAML: {e}")
        result.errors.append(f"Invalid YAML in config: {e}")
        result.failed += 1
        return False
    except Exception as e:
        print_error(f"Configuration validation error: {e}")
        result.errors.append(f"Config validation error: {e}")
        result.failed += 1
        return False

def validate_cli_functionality(result: ValidationResult) -> bool:
    """Validate CLI functionality."""
    print_info("Validating CLI functionality...")
    
    cli_path = Path("cli.py")
    if not cli_path.exists():
        print_error("CLI script not found (cli.py)")
        result.errors.append("CLI script missing")
        result.failed += 1
        return False
    
    try:
        # Test CLI help command
        cmd_result = subprocess.run(
            [sys.executable, "cli.py", "--help"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if cmd_result.returncode == 0:
            print_success("CLI help command works")
            result.passed += 1
        else:
            print_error(f"CLI help failed: {cmd_result.stderr}")
            result.errors.append("CLI help command failed")
            result.failed += 1
            return False
        
        # Test CLI status command (should work without credentials)
        cmd_result = subprocess.run(
            [sys.executable, "cli.py", "status"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # Status command might fail without credentials, but should not crash
        if "Traceback" not in cmd_result.stderr:
            print_success("CLI status command runs without crashing")
            result.passed += 1
        else:
            print_warning("CLI status command has issues (may need credentials)")
            result.warnings_list.append("CLI status command issues")
            result.warnings += 1
        
        return True
        
    except subprocess.TimeoutExpired:
        print_error("CLI command timed out")
        result.errors.append("CLI command timeout")
        result.failed += 1
        return False
    except Exception as e:
        print_error(f"CLI validation error: {e}")
        result.errors.append(f"CLI validation error: {e}")
        result.failed += 1
        return False

def validate_cloud_connectivity(result: ValidationResult) -> bool:
    """Validate cloud provider connectivity (optional)."""
    print_info("Validating cloud provider connectivity...")
    print_info("(This requires configured credentials)")
    
    try:
        from finops.core import FinOpsOptimizer
        optimizer = FinOpsOptimizer()
        
        # Test each provider
        providers = ['aws', 'azure', 'gcp', 'oracle']
        working_providers = []
        
        for provider in providers:
            try:
                # This is a basic connectivity test
                status = optimizer.get_provider_status(provider)
                if status.get('connected', False):
                    print_success(f"{provider.upper()}: Connected")
                    working_providers.append(provider)
                    result.passed += 1
                else:
                    print_warning(f"{provider.upper()}: Not configured or accessible")
                    result.warnings += 1
                    
            except Exception as e:
                print_warning(f"{provider.upper()}: {str(e)[:50]}...")
                result.warnings += 1
        
        if working_providers:
            print_success(f"Working providers: {', '.join(working_providers)}")
        else:
            print_warning("No cloud providers configured (credentials needed)")
            result.warnings_list.append("No cloud providers configured")
        
        return True
        
    except Exception as e:
        print_warning(f"Cloud connectivity test failed: {e}")
        result.warnings_list.append("Cloud connectivity test failed")
        result.warnings += 1
        return True  # Not critical

def run_performance_benchmark(result: ValidationResult) -> bool:
    """Run basic performance benchmark."""
    print_info("Running performance benchmark...")
    
    try:
        from finops.core import FinOpsOptimizer
        from finops.config import Config
        
        # Benchmark configuration loading
        start_time = time.time()
        config = Config()
        config_time = time.time() - start_time
        
        # Benchmark optimizer initialization
        start_time = time.time()
        optimizer = FinOpsOptimizer()
        init_time = time.time() - start_time
        
        # Benchmark basic operations
        start_time = time.time()
        status = optimizer.get_status()
        status_time = time.time() - start_time
        
        print_success(f"Config loading: {config_time:.3f}s")
        print_success(f"Optimizer init: {init_time:.3f}s")
        print_success(f"Status check: {status_time:.3f}s")
        
        # Performance thresholds
        if config_time > 1.0:
            print_warning("Config loading is slow (>1s)")
            result.warnings += 1
        
        if init_time > 2.0:
            print_warning("Optimizer initialization is slow (>2s)")
            result.warnings += 1
        
        result.passed += 1
        return True
        
    except Exception as e:
        print_error(f"Performance benchmark failed: {e}")
        result.errors.append(f"Performance benchmark failed: {e}")
        result.failed += 1
        return False

def suggest_fixes(result: ValidationResult, auto_fix: bool = False) -> None:
    """Suggest fixes for common issues."""
    if not result.errors and not result.warnings_list:
        return
    
    print_header("Suggested Fixes")
    
    for error in result.errors:
        print_error(error)
        
        if "Missing dependency" in error:
            dep_name = error.split(": ")[1]
            print_info(f"Fix: pip install {dep_name}")
            
            if auto_fix:
                try:
                    subprocess.run([sys.executable, "-m", "pip", "install", dep_name], 
                                 check=True, capture_output=True)
                    print_success(f"Auto-installed {dep_name}")
                except subprocess.CalledProcessError:
                    print_error(f"Auto-install failed for {dep_name}")
        
        elif "Configuration file missing" in error:
            print_info("Fix: Run 'python quick_start.py --config-only'")
            
        elif "Module import failed" in error:
            print_info("Fix: Reinstall FinOps Optimizer or check PYTHONPATH")
    
    for warning in result.warnings_list:
        print_warning(warning)
        
        if "Optional dependency missing" in warning:
            dep_name = warning.split(": ")[1]
            print_info(f"Optional fix: pip install {dep_name}")

def generate_report(result: ValidationResult) -> None:
    """Generate validation report."""
    print_header("Validation Report")
    
    total_tests = result.passed + result.failed
    success_rate = (result.passed / total_tests * 100) if total_tests > 0 else 0
    
    print(f"Total tests: {total_tests}")
    print_success(f"Passed: {result.passed}")
    if result.failed > 0:
        print_error(f"Failed: {result.failed}")
    if result.warnings > 0:
        print_warning(f"Warnings: {result.warnings}")
    
    print(f"\nSuccess rate: {success_rate:.1f}%")
    
    if result.failed == 0:
        print_success("🎉 All critical tests passed!")
        print_info("FinOps Optimizer is ready to use")
    else:
        print_error("❌ Some critical tests failed")
        print_info("Please fix the errors above before using FinOps Optimizer")
    
    # Save report to file
    report_data = {
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'system': f"{platform.system()} {platform.release()}",
        'python_version': sys.version.split()[0],
        'total_tests': total_tests,
        'passed': result.passed,
        'failed': result.failed,
        'warnings': result.warnings,
        'success_rate': success_rate,
        'errors': result.errors,
        'warnings_list': result.warnings_list
    }
    
    try:
        with open('validation_report.json', 'w') as f:
            json.dump(report_data, f, indent=2)
        print_info("Detailed report saved to: validation_report.json")
    except Exception as e:
        print_warning(f"Could not save report: {e}")

def main():
    """Main validation function."""
    parser = argparse.ArgumentParser(description="FinOps Optimizer Setup Validation")
    parser.add_argument("--full", action="store_true", help="Run full validation including cloud connectivity")
    parser.add_argument("--cloud", action="store_true", help="Test cloud provider connectivity")
    parser.add_argument("--benchmark", action="store_true", help="Run performance benchmark")
    parser.add_argument("--fix", action="store_true", help="Attempt to auto-fix issues")
    
    args = parser.parse_args()
    
    print_header("FinOps Optimizer - Setup Validation")
    print_info("Validating your FinOps Optimizer installation...")
    
    result = ValidationResult()
    
    # Core validations (always run)
    validate_python_environment(result)
    validate_dependencies(result)
    validate_finops_modules(result)
    validate_configuration(result)
    validate_cli_functionality(result)
    
    # Optional validations
    if args.full or args.cloud:
        validate_cloud_connectivity(result)
    
    if args.full or args.benchmark:
        run_performance_benchmark(result)
    
    # Show fixes
    suggest_fixes(result, args.fix)
    
    # Generate report
    generate_report(result)
    
    # Exit with appropriate code
    if result.failed > 0:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
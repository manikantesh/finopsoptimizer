#!/usr/bin/env python3
"""
Setup Validation Script for FinOpsOptimizer

This script validates that the FinOpsOptimizer installation is working correctly
and all modules can be imported and used properly.
"""

import sys
import importlib
import traceback
from pathlib import Path

def print_header(title):
    """Print a formatted header."""
    print("\n" + "=" * 60)
    print(f"🔍 {title}")
    print("=" * 60)

def print_test(test_name, success, details=""):
    """Print test result."""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} {test_name}")
    if details:
        print(f"    {details}")

def test_python_version():
    """Test Python version compatibility."""
    version = sys.version_info
    success = version.major >= 3 and version.minor >= 8
    details = f"Python {version.major}.{version.minor}.{version.micro}"
    print_test("Python Version (>=3.8)", success, details)
    return success

def test_core_imports():
    """Test core module imports."""
    print_header("Testing Core Module Imports")
    
    modules_to_test = [
        ("finops", "Main package"),
        ("finops.core", "Core orchestration"),
        ("finops.config", "Configuration management"),
        ("finops.data_ingestion", "Data ingestion pipeline"),
        ("finops.vm_rightsizing", "VM rightsizing analyzer"),
        ("finops.scheduler", "Task scheduler"),
        ("finops.unattached_disks", "Disk remediation"),
        ("finops.reserved_instances", "RI/SP analyzer"),
    ]
    
    all_success = True
    for module_name, description in modules_to_test:
        try:
            importlib.import_module(module_name)
            print_test(f"{module_name}", True, description)
        except ImportError as e:
            print_test(f"{module_name}", False, f"Import error: {e}")
            all_success = False
        except Exception as e:
            print_test(f"{module_name}", False, f"Unexpected error: {e}")
            all_success = False
    
    return all_success

def test_cloud_provider_imports():
    """Test cloud provider module imports."""
    print_header("Testing Cloud Provider Module Imports")
    
    providers = [
        ("finops.aws", "AWS provider"),
        ("finops.azure", "Azure provider"),
        ("finops.gcp", "GCP provider"),
        ("finops.oracle", "Oracle Cloud provider"),
    ]
    
    all_success = True
    for provider_module, description in providers:
        try:
            importlib.import_module(provider_module)
            print_test(f"{provider_module}", True, description)
        except ImportError as e:
            print_test(f"{provider_module}", False, f"Import error: {e}")
            all_success = False
        except Exception as e:
            print_test(f"{provider_module}", False, f"Unexpected error: {e}")
            all_success = False
    
    return all_success

def test_main_classes():
    """Test main class instantiation."""
    print_header("Testing Main Class Instantiation")
    
    tests = []
    
    # Test FinOpsOptimizer
    try:
        from finops import FinOpsOptimizer
        optimizer = FinOpsOptimizer()
        tests.append(("FinOpsOptimizer", True, "Core optimizer class"))
    except Exception as e:
        tests.append(("FinOpsOptimizer", False, f"Error: {e}"))
    
    # Test DataIngestionPipeline
    try:
        from finops import DataIngestionPipeline, Config
        config = Config()
        pipeline = DataIngestionPipeline(config)
        tests.append(("DataIngestionPipeline", True, "Data ingestion pipeline"))
    except Exception as e:
        tests.append(("DataIngestionPipeline", False, f"Error: {e}"))
    
    # Test VMRightsizingAnalyzer
    try:
        from finops import VMRightsizingAnalyzer, Config
        config = Config()
        analyzer = VMRightsizingAnalyzer(config)
        tests.append(("VMRightsizingAnalyzer", True, "VM rightsizing analyzer"))
    except Exception as e:
        tests.append(("VMRightsizingAnalyzer", False, f"Error: {e}"))
    
    # Test UnattachedDisksRemediator
    try:
        from finops import UnattachedDisksRemediator, Config
        config = Config()
        remediator = UnattachedDisksRemediator(config)
        tests.append(("UnattachedDisksRemediator", True, "Disk remediation system"))
    except Exception as e:
        tests.append(("UnattachedDisksRemediator", False, f"Error: {e}"))
    
    # Test ReservedInstanceAnalyzer
    try:
        from finops import ReservedInstanceAnalyzer, Config
        config = Config()
        ri_analyzer = ReservedInstanceAnalyzer(config)
        tests.append(("ReservedInstanceAnalyzer", True, "RI/SP analyzer"))
    except Exception as e:
        tests.append(("ReservedInstanceAnalyzer", False, f"Error: {e}"))
    
    # Test CostOptimizationScheduler
    try:
        from finops import CostOptimizationScheduler, Config
        config = Config()
        scheduler = CostOptimizationScheduler(config)
        tests.append(("CostOptimizationScheduler", True, "Task scheduler"))
    except Exception as e:
        tests.append(("CostOptimizationScheduler", False, f"Error: {e}"))
    
    all_success = True
    for test_name, success, details in tests:
        print_test(test_name, success, details)
        if not success:
            all_success = False
    
    return all_success

def test_cli_functionality():
    """Test CLI functionality."""
    print_header("Testing CLI Functionality")
    
    try:
        import subprocess
        result = subprocess.run([sys.executable, "cli.py", "--help"], 
                              capture_output=True, text=True, timeout=30)
        success = result.returncode == 0
        details = "CLI help command executed successfully" if success else f"Exit code: {result.returncode}"
        print_test("CLI Help Command", success, details)
        return success
    except subprocess.TimeoutExpired:
        print_test("CLI Help Command", False, "Command timed out")
        return False
    except Exception as e:
        print_test("CLI Help Command", False, f"Error: {e}")
        return False

def test_configuration():
    """Test configuration system."""
    print_header("Testing Configuration System")
    
    try:
        from finops.config import Config, load_config
        
        # Test default config creation
        config = Config()
        print_test("Default Config Creation", True, "Default configuration created")
        
        # Test config loading
        loaded_config = load_config()
        print_test("Config Loading", True, "Configuration loaded successfully")
        
        # Test config validation
        validation_result = config.validate_credentials()
        print_test("Config Validation", True, f"Validation completed: {len(validation_result)} providers checked")
        
        return True
    except Exception as e:
        print_test("Configuration System", False, f"Error: {e}")
        return False

def test_dependencies():
    """Test critical dependencies."""
    print_header("Testing Critical Dependencies")
    
    critical_deps = [
        ("pandas", "Data manipulation"),
        ("numpy", "Numerical computing"),
        ("scikit-learn", "Machine learning"),
        ("click", "CLI framework"),
        ("pydantic", "Data validation"),
        ("yaml", "YAML parsing"),
        ("schedule", "Task scheduling"),
    ]
    
    all_success = True
    for dep_name, description in critical_deps:
        try:
            if dep_name == "yaml":
                import yaml
            else:
                importlib.import_module(dep_name)
            print_test(f"{dep_name}", True, description)
        except ImportError:
            print_test(f"{dep_name}", False, f"Missing dependency: {dep_name}")
            all_success = False
        except Exception as e:
            print_test(f"{dep_name}", False, f"Error: {e}")
            all_success = False
    
    return all_success

def test_file_structure():
    """Test file structure."""
    print_header("Testing File Structure")
    
    required_files = [
        ("cli.py", "CLI interface"),
        ("requirements.txt", "Dependencies"),
        ("finops/__init__.py", "Main package"),
        ("finops/core.py", "Core module"),
        ("finops/config.py", "Configuration"),
        ("examples/comprehensive_cost_optimization.py", "Example script"),
        ("LOCAL_SETUP_GUIDE.md", "Setup guide"),
        ("quick_start.py", "Quick start script"),
    ]
    
    all_success = True
    for file_path, description in required_files:
        path = Path(file_path)
        success = path.exists()
        print_test(f"{file_path}", success, description)
        if not success:
            all_success = False
    
    return all_success

def run_comprehensive_validation():
    """Run comprehensive validation."""
    print_header("FinOpsOptimizer Setup Validation")
    print("This script validates that FinOpsOptimizer is properly installed and configured.")
    
    tests = [
        ("Python Version", test_python_version),
        ("File Structure", test_file_structure),
        ("Critical Dependencies", test_dependencies),
        ("Core Module Imports", test_core_imports),
        ("Cloud Provider Imports", test_cloud_provider_imports),
        ("Main Classes", test_main_classes),
        ("Configuration System", test_configuration),
        ("CLI Functionality", test_cli_functionality),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ FAIL {test_name}: Unexpected error: {e}")
            traceback.print_exc()
            results.append((test_name, False))
    
    # Summary
    print_header("Validation Summary")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    print(f"Tests Passed: {passed}/{total}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n🎉 All tests passed! FinOpsOptimizer is ready to use.")
        print("\nNext steps:")
        print("1. Configure your cloud provider credentials")
        print("2. Run 'python cli.py status' to check provider connections")
        print("3. Try 'python cli.py analyze --days 7' for a basic analysis")
        print("4. Run 'python examples/comprehensive_cost_optimization.py' for a full demo")
    else:
        print(f"\n⚠️  {total - passed} tests failed. Please review the errors above.")
        print("\nTroubleshooting:")
        print("1. Ensure all dependencies are installed: pip install -r requirements.txt")
        print("2. Install in development mode: pip install -e .")
        print("3. Check Python version (3.8+ required)")
        print("4. Review LOCAL_SETUP_GUIDE.md for detailed instructions")
    
    return passed == total

if __name__ == "__main__":
    try:
        success = run_comprehensive_validation()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Validation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error during validation: {e}")
        traceback.print_exc()
        sys.exit(1)
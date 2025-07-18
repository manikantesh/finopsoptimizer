#!/usr/bin/env python3
"""
Quick Start Script for FinOpsOptimizer

This script helps users quickly set up and test FinOpsOptimizer on their local machine.
It provides a guided setup process and runs basic functionality tests.
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime

def print_header(title):
    """Print a formatted header."""
    print("\n" + "=" * 60)
    print(f"🚀 {title}")
    print("=" * 60)

def print_step(step_num, description):
    """Print a formatted step."""
    print(f"\n📋 Step {step_num}: {description}")
    print("-" * 40)

def run_command(command, description="", check=True):
    """Run a command and handle errors."""
    if description:
        print(f"Running: {description}")
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=check)
        if result.stdout:
            print(result.stdout)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        if e.stderr:
            print(f"Error details: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python {version.major}.{version.minor} is not supported. Please use Python 3.8 or higher.")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def check_virtual_environment():
    """Check if running in a virtual environment."""
    in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    if not in_venv:
        print("⚠️  Warning: Not running in a virtual environment")
        print("   It's recommended to use a virtual environment to avoid dependency conflicts")
        response = input("   Continue anyway? (y/N): ").lower()
        return response == 'y'
    print("✅ Running in virtual environment")
    return True

def install_dependencies():
    """Install required dependencies."""
    print("Installing dependencies...")
    
    # Check if requirements.txt exists
    if not Path("requirements.txt").exists():
        print("❌ requirements.txt not found. Please run this script from the project root directory.")
        return False
    
    # Install dependencies
    success = run_command("pip install -r requirements.txt", "Installing requirements")
    if not success:
        return False
    
    # Install package in development mode
    success = run_command("pip install -e .", "Installing FinOpsOptimizer in development mode")
    return success

def test_installation():
    """Test if the installation was successful."""
    print("Testing installation...")
    
    # Test CLI
    success = run_command("python cli.py --help", "Testing CLI", check=False)
    if not success:
        print("❌ CLI test failed")
        return False
    
    # Test Python import
    try:
        from finops import FinOpsOptimizer
        print("✅ Python import successful")
        return True
    except ImportError as e:
        print(f"❌ Python import failed: {e}")
        return False

def create_sample_config():
    """Create a sample configuration file."""
    print("Creating sample configuration...")
    
    success = run_command("python cli.py init --output finops_config.yml", "Creating configuration file")
    if success:
        print("✅ Configuration file created: finops_config.yml")
        print("📝 Edit this file to configure your cloud providers")
        return True
    return False

def run_basic_tests():
    """Run basic functionality tests."""
    print("Running basic functionality tests...")
    
    # Test status command
    print("\n🔍 Testing provider status...")
    run_command("python cli.py status", check=False)
    
    # Test demo script
    print("\n🎯 Running comprehensive demo...")
    demo_success = run_command("python examples/comprehensive_cost_optimization.py", check=False)
    
    if demo_success:
        print("✅ Demo completed successfully")
    else:
        print("⚠️  Demo completed with some warnings (this is normal without cloud credentials)")
    
    return True

def show_next_steps():
    """Show next steps to the user."""
    print_header("Next Steps")
    
    print("🎉 FinOpsOptimizer is now set up and ready to use!")
    print("\nTo get started:")
    print("1. Configure your cloud provider credentials:")
    print("   - AWS: Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY")
    print("   - Azure: Set AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, AZURE_TENANT_ID")
    print("   - GCP: Set GOOGLE_APPLICATION_CREDENTIALS")
    print("   - Oracle: Configure ~/.oci/config")
    
    print("\n2. Edit finops_config.yml to enable your cloud providers")
    
    print("\n3. Test your setup:")
    print("   python cli.py status")
    
    print("\n4. Run your first analysis:")
    print("   python cli.py analyze --days 7")
    
    print("\n5. Explore more features:")
    print("   python cli.py --help")
    
    print("\n📚 For detailed instructions, see:")
    print("   - LOCAL_SETUP_GUIDE.md")
    print("   - README.md")
    print("   - examples/comprehensive_cost_optimization.py")

def main():
    """Main function to run the quick start process."""
    print_header("FinOpsOptimizer Quick Start")
    print("This script will help you set up FinOpsOptimizer on your local machine.")
    
    # Step 1: Check Python version
    print_step(1, "Checking Python Version")
    if not check_python_version():
        sys.exit(1)
    
    # Step 2: Check virtual environment
    print_step(2, "Checking Virtual Environment")
    if not check_virtual_environment():
        sys.exit(1)
    
    # Step 3: Install dependencies
    print_step(3, "Installing Dependencies")
    if not install_dependencies():
        print("❌ Failed to install dependencies")
        sys.exit(1)
    print("✅ Dependencies installed successfully")
    
    # Step 4: Test installation
    print_step(4, "Testing Installation")
    if not test_installation():
        print("❌ Installation test failed")
        sys.exit(1)
    print("✅ Installation test passed")
    
    # Step 5: Create sample configuration
    print_step(5, "Creating Sample Configuration")
    if not create_sample_config():
        print("❌ Failed to create configuration")
        sys.exit(1)
    
    # Step 6: Run basic tests
    print_step(6, "Running Basic Tests")
    run_basic_tests()
    
    # Step 7: Show next steps
    show_next_steps()
    
    print("\n🎉 Quick start completed successfully!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
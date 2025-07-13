#!/usr/bin/env python3
"""
Script to test local deployment and branch-specific builds.
This helps test documentation deployment before pushing to GitHub.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

def get_current_branch():
    """Get current git branch."""
    try:
        result = subprocess.run(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], 
                              capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return 'main'

def build_docs(branch_name=None):
    """Build documentation for testing."""
    if not branch_name:
        branch_name = get_current_branch()
    
    print(f"🔨 Building documentation for branch: {branch_name}")
    
    # Build documentation
    try:
        subprocess.run(['mkdocs', 'build', '--clean'], check=True)
        print("✅ Documentation built successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        return False
    
    # Create version selector
    try:
        subprocess.run(['python', 'scripts/create_version_selector.py'], check=True)
        print("✅ Version selector created")
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Version selector failed: {e}")
    
    return True

def create_branch_preview(branch_name):
    """Create branch-specific preview."""
    site_dir = Path('site')
    branch_dir = site_dir / branch_name
    
    if branch_name != 'main':
        print(f"📁 Creating branch preview for: {branch_name}")
        
        # Create branch directory
        branch_dir.mkdir(exist_ok=True)
        
        # Copy all files to branch directory
        import shutil
        for item in site_dir.iterdir():
            if item.name != branch_name:
                if item.is_dir():
                    shutil.copytree(item, branch_dir / item.name, dirs_exist_ok=True)
                else:
                    shutil.copy2(item, branch_dir / item.name)
        
        # Update base URLs in HTML files
        base_url = f"https://manikantesh.github.io/finopsoptimizerdocs/{branch_name}/"
        for html_file in branch_dir.rglob("*.html"):
            try:
                with open(html_file, 'r') as f:
                    content = f.read()
                
                # Replace base URL
                content = content.replace(
                    'https://manikantesh.github.io/finopsoptimizerdocs/',
                    base_url
                )
                
                with open(html_file, 'w') as f:
                    f.write(content)
            except Exception as e:
                print(f"⚠️  Could not update {html_file}: {e}")
        
        print(f"✅ Branch preview created at: site/{branch_name}/")
    
    return True

def serve_local(port=8000):
    """Serve documentation locally."""
    print(f"🌐 Starting local server on port {port}")
    print(f"📖 Documentation available at: http://localhost:{port}")
    print("Press Ctrl+C to stop the server")
    
    try:
        subprocess.run(['mkdocs', 'serve', '--dev-addr', f'0.0.0.0:{port}'])
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")

def main():
    parser = argparse.ArgumentParser(description='Test documentation deployment')
    parser.add_argument('--branch', help='Branch name for testing')
    parser.add_argument('--serve', action='store_true', help='Serve documentation locally')
    parser.add_argument('--port', type=int, default=8000, help='Port for local server')
    parser.add_argument('--preview', action='store_true', help='Create branch preview')
    
    args = parser.parse_args()
    
    branch_name = args.branch or get_current_branch()
    
    print("🚀 FinOps Optimizer Documentation Test Deployment")
    print(f"📍 Current branch: {branch_name}")
    print(f"📂 Working directory: {os.getcwd()}")
    print()
    
    # Build documentation
    if not build_docs(branch_name):
        sys.exit(1)
    
    # Create branch preview if requested
    if args.preview:
        create_branch_preview(branch_name)
    
    # Serve locally if requested
    if args.serve:
        serve_local(args.port)
    
    print("\n✅ Deployment test completed successfully!")
    print(f"📁 Documentation built in: site/")
    if args.preview and branch_name != 'main':
        print(f"📁 Branch preview in: site/{branch_name}/")

if __name__ == '__main__':
    main() 
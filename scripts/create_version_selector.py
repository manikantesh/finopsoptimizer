#!/usr/bin/env python3
"""
Script to create version selector for documentation.
This creates a version selector that allows users to switch between different versions.
"""

import os
import json
import subprocess
from pathlib import Path

def get_git_tags():
    """Get all git tags sorted by version."""
    try:
        result = subprocess.run(['git', 'tag', '--sort=-version:refname'], 
                              capture_output=True, text=True, check=True)
        tags = result.stdout.strip().split('\n')
        return [tag for tag in tags if tag]
    except subprocess.CalledProcessError:
        return []

def get_current_branch():
    """Get current git branch."""
    try:
        result = subprocess.run(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], 
                              capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return 'main'

def create_version_selector():
    """Create version selector HTML and JavaScript."""
    tags = get_git_tags()
    current_branch = get_current_branch()
    
    # Add current branch if it's not in tags
    versions = []
    if current_branch not in tags:
        versions.append({
            'name': current_branch,
            'url': f'https://manikantesh.github.io/finopsoptimizerdocs/',
            'current': True
        })
    
    # Add tagged versions
    for tag in tags:
        versions.append({
            'name': tag,
            'url': f'https://manikantesh.github.io/finopsoptimizerdocs/{tag}/',
            'current': False
        })
    
    # Create version selector HTML
    selector_html = '''
<div class="version-selector">
    <label for="version-select">Version:</label>
    <select id="version-select" onchange="changeVersion(this.value)">
'''
    
    for version in versions:
        selected = 'selected' if version['current'] else ''
        selector_html += f'        <option value="{version["url"]}" {selected}>{version["name"]}</option>\n'
    
    selector_html += '''
    </select>
</div>

<script>
function changeVersion(url) {
    if (url) {
        window.location.href = url;
    }
}

// Add version selector to page
document.addEventListener('DOMContentLoaded', function() {
    const header = document.querySelector('.md-header');
    if (header) {
        const selector = document.querySelector('.version-selector');
        if (selector) {
            header.appendChild(selector);
        }
    }
});
</script>

<style>
.version-selector {
    display: flex;
    align-items: center;
    margin-left: 20px;
    color: var(--md-primary-fg-color);
}

.version-selector label {
    margin-right: 8px;
    font-size: 14px;
}

.version-selector select {
    background: transparent;
    border: 1px solid var(--md-primary-fg-color);
    color: var(--md-primary-fg-color);
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 14px;
}

.version-selector select:focus {
    outline: none;
    border-color: var(--md-accent-fg-color);
}
</style>
'''
    
    # Write to site directory
    site_dir = Path('site')
    site_dir.mkdir(exist_ok=True)
    
    with open(site_dir / 'version-selector.html', 'w') as f:
        f.write(selector_html)
    
    # Create versions.json for API
    versions_data = {
        'versions': versions,
        'latest': versions[0]['name'] if versions else current_branch,
        'current': current_branch
    }
    
    with open(site_dir / 'versions.json', 'w') as f:
        json.dump(versions_data, f, indent=2)
    
    print(f"Created version selector with {len(versions)} versions")
    print(f"Current version: {current_branch}")
    print(f"Available versions: {[v['name'] for v in versions]}")

if __name__ == '__main__':
    create_version_selector() 
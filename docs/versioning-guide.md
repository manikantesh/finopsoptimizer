# Documentation Versioning Guide

This guide explains how the FinOps Optimizer documentation versioning system works and how to manage different versions.

## 🎯 Overview

Our documentation uses a sophisticated versioning system that allows users to:
- **Switch between versions** using a dropdown selector
- **Access historical documentation** for older releases
- **Always see the latest** development version
- **Maintain consistency** across different releases

## 🏗️ Architecture

### Version Management
- **Mike Plugin**: Uses `mike` for MkDocs version management
- **GitHub Actions**: Automated deployment for each version
- **Version Selector**: JavaScript-powered dropdown in the header
- **Smart Routing**: Maintains current page when switching versions

### Version Types
- **`latest`**: Always points to the main branch (development)
- **`v2.1.0`**: Stable release with AI agents and real-time dashboards
- **`v2.0.0`**: Multi-cloud support release
- **`v1.5.0`**: Oracle Cloud integration
- **`v1.0.0`**: Initial release

## 🚀 For Users

### Switching Versions
1. **Locate the version selector** in the top navigation bar
2. **Click on the current version** to open the dropdown
3. **Select your desired version** from the list
4. **Wait for the page to load** - you'll stay on the same page in the new version

### Version Information
Each version includes:
- **Version number** (e.g., v2.1.0)
- **Release title** describing key features
- **Current badge** for the active version
- **Smooth transitions** between versions

### Bookmarking
- URLs include the version path: `/finopsoptimizer/v2.1.0/ai-agents/`
- **Bookmarks work correctly** and maintain version context
- **Direct links** to specific versions are supported

## 🔧 For Developers

### Deployment Workflow

#### Automatic Deployment
```yaml
# Triggered by:
- Push to main branch → deploys as 'latest'
- Push tag 'v*' → deploys as versioned release
- Pull request → builds preview (no deployment)
```

#### Manual Deployment
```bash
# Deploy latest from main
./scripts/deploy-docs.sh latest

# Deploy specific version
./scripts/deploy-docs.sh version 2.1.0

# List all versions
./scripts/deploy-docs.sh list

# Delete a version
./scripts/deploy-docs.sh delete 1.0.0

# Serve locally
./scripts/deploy-docs.sh serve
```

### Creating a New Version

#### 1. Prepare Release
```bash
# Ensure main branch is ready
git checkout main
git pull origin main

# Update version in relevant files
# - Update CHANGELOG.md
# - Update version numbers in code
# - Update documentation if needed
```

#### 2. Create Release Tag
```bash
# Create and push tag
git tag -a v2.2.0 -m "Release v2.2.0: New Features"
git push origin v2.2.0
```

#### 3. Automatic Deployment
The GitHub Actions workflow will automatically:
- Detect the new tag
- Build documentation for that version
- Deploy it to GitHub Pages
- Update the version selector

#### 4. Update Version List
```bash
# Update versions.json (optional - can be done manually)
./scripts/deploy-docs.sh update-versions
```

### Configuration Files

#### `mkdocs.yml`
```yaml
extra:
  version:
    provider: mike
    default: latest
```

#### `versions.json`
```json
[
  {
    "version": "latest",
    "title": "Latest (Main)",
    "aliases": ["main", "dev"]
  },
  {
    "version": "v2.1.0",
    "title": "v2.1.0 - AI Agents & Real-time Dashboards",
    "aliases": []
  }
]
```

#### GitHub Actions Workflow
```yaml
# .github/workflows/docs.yml
- name: Deploy latest version (main branch)
  if: github.ref == 'refs/heads/main'
  run: |
    mike deploy --push --update-aliases latest main
    mike set-default --push latest

- name: Deploy tagged version
  if: startsWith(github.ref, 'refs/tags/v')
  run: |
    VERSION=${GITHUB_REF#refs/tags/v}
    mike deploy --push --update-aliases $VERSION
```

## 🎨 Customization

### Version Selector Styling
The version selector integrates seamlessly with Material theme:
- **Matches theme colors** (light/dark mode)
- **Responsive design** for mobile devices
- **Smooth animations** and transitions
- **Keyboard navigation** support

### Custom Styling
```css
/* Custom version selector styles */
.md-version {
  /* Your custom styles here */
}
```

### JavaScript Customization
```javascript
// Modify version selector behavior
// File: docs/javascripts/version-selector.js
```

## 📊 Analytics & Monitoring

### Version Usage Tracking
- **Google Analytics**: Track version switching events
- **User Preferences**: Store user's preferred version
- **Popular Versions**: Monitor which versions are most accessed

### Performance Monitoring
- **Load Times**: Monitor version switching performance
- **Error Tracking**: Catch and report version-related errors
- **User Experience**: Ensure smooth transitions

## 🔍 Troubleshooting

### Common Issues

#### Version Not Found (404)
```bash
# Check if version exists
mike list

# Redeploy if missing
./scripts/deploy-docs.sh version 2.1.0
```

#### Version Selector Not Working
1. **Check JavaScript console** for errors
2. **Verify versions.json** is accessible
3. **Clear browser cache** and reload
4. **Check network requests** in developer tools

#### Deployment Failures
```bash
# Check GitHub Actions logs
# Verify mike installation
pip install mike

# Test local deployment
mike serve
```

### Debug Mode
```bash
# Enable verbose logging
export MKDOCS_VERBOSE=1
mkdocs build --verbose
```

## 🚀 Best Practices

### Version Naming
- **Use semantic versioning**: v2.1.0, v2.1.1, etc.
- **Descriptive titles**: Include key features in version titles
- **Consistent format**: Maintain consistent naming across versions

### Documentation Maintenance
- **Keep versions updated**: Regularly update older versions for critical fixes
- **Archive old versions**: Remove very old versions to reduce maintenance
- **Clear migration guides**: Provide upgrade paths between versions

### User Experience
- **Preserve context**: Keep users on the same page when switching versions
- **Clear indicators**: Show which version is currently active
- **Fast switching**: Optimize for quick version transitions

## 🏷️ Creating a GitHub Release

Beyond pushing a tag (above), releases are usually cut from the GitHub UI:

1. Go to the repository's **Releases** page and click **Create a new release**.
2. **Tag**: use semantic versioning, e.g. `v2.2.0` (the `v` prefix is stripped automatically).
3. **Title**: a short, descriptive summary, e.g. `v2.2.0 - Oracle Cloud Integration`.
4. **Description**: group notes under headings (`New Features`, `Improvements`, `Bug Fixes`) -- the first line becomes the version's description in the dropdown.
5. Check **Set as the latest release** if applicable, then **Publish release**.

Publishing triggers the same GitHub Actions workflow as pushing a tag: the version is built, deployed to `https://manikantesh.github.io/finopsoptimizer/<version>/`, and added to the version dropdown within a couple of minutes.

### Release checklist

- [ ] All features tested, `pytest` passing
- [ ] `CHANGELOG.md` and version numbers updated
- [ ] Tag follows semantic versioning
- [ ] Release published (not left as a draft)
- [ ] Version appears in the live dropdown after deploy

## 🌐 Custom Domain (Optional)

To serve docs from your own domain instead of `github.io`:

1. Add a `CNAME` file to `docs/` containing the domain, e.g. `docs.yourdomain.com`.
2. Point DNS at GitHub Pages: `docs.yourdomain.com CNAME manikantesh.github.io`.
3. Set `site_url` in `mkdocs.yml` to match.

## 📈 Future Enhancements

### Planned Features
- **Version comparison**: Side-by-side version comparisons
- **Change highlights**: Show what's new in each version
- **Search across versions**: Search content across all versions
- **Version recommendations**: Suggest appropriate version for user needs

### Integration Opportunities
- **API versioning**: Link documentation versions to API versions
- **Release notes**: Integrate with GitHub releases
- **Feedback system**: Collect user feedback on version experience

---

*This versioning system ensures that users always have access to the right documentation for their version of FinOps Optimizer, while maintaining a smooth and professional user experience.*
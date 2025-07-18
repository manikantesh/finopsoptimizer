# Documentation Versioning Setup Guide

This guide will help you set up the complete versioning system for your FinOps Optimizer documentation.

## 🎯 Quick Setup

### 1. Install Dependencies

```bash
# Install mike for version management
pip install mike

# Install other required packages
pip install mkdocs-material mkdocs-git-revision-date-localized-plugin mkdocs-minify-plugin pymdown-extensions
```

### 2. Initialize Versioning

```bash
# Make deployment script executable
chmod +x scripts/deploy-docs.sh

# Deploy current main as latest
./scripts/deploy-docs.sh latest
```

### 3. Create Your First Version

```bash
# Create a version tag
git tag -a v2.1.0 -m "Release v2.1.0: AI Agents and Real-time Dashboards"
git push origin v2.1.0

# Deploy the version (will be automatic via GitHub Actions)
# Or manually: ./scripts/deploy-docs.sh version 2.1.0
```

## 🏗️ What's Included

### ✅ Version Management System

- **Mike integration** for MkDocs versioning
- **GitHub Actions workflow** for automatic deployment
- **Version selector dropdown** in the documentation header
- **Smart routing** that preserves current page when switching versions

### ✅ Enhanced User Experience

- **Smooth version switching** with loading indicators
- **Responsive design** that works on mobile
- **Dark/light theme integration** with Material theme
- **Keyboard navigation** support
- **User preference storage** in localStorage

### ✅ Developer Tools

- **Deployment script** (`scripts/deploy-docs.sh`) for easy version management
- **Comprehensive documentation** in `docs/versioning-guide.md`
- **Automated workflows** for CI/CD integration
- **Version configuration** in `versions.json`

## 🚀 How It Works

### Version Structure

```
https://manikantesh.github.io/finopsoptimizer/
├── latest/          # Always points to main branch
├── v2.1.0/         # Stable release with AI features
├── v2.0.0/         # Multi-cloud support release
```

### Automatic Deployment

```yaml
# GitHub Actions triggers:
Push to main → Deploy as 'latest'
Push tag v* → Deploy as versioned release
Pull request → Build preview only
```

### Version Selector

- **Location**: Top navigation bar
- **Functionality**: Dropdown with all available versions
- **Features**: Current version highlighting, smooth transitions
- **Persistence**: Remembers user's version preference

## 📋 Usage Examples

### For End Users

1. **Visit documentation**: https://manikantesh.github.io/finopsoptimizer/
2. **Click version selector** in the top navigation
3. **Choose desired version** from dropdown
4. **Stay on same page** in the new version

### For Developers

```bash
# List all deployed versions
./scripts/deploy-docs.sh list

# Deploy latest from main
./scripts/deploy-docs.sh latest

# Deploy specific version
./scripts/deploy-docs.sh version 2.1.0

# Delete old version
./scripts/deploy-docs.sh delete 1.0.0

# Serve locally for testing
./scripts/deploy-docs.sh serve
```

## 🔧 Configuration Files

### `mkdocs.yml` - Main Configuration

```yaml
extra:
  version:
    provider: mike
    default: latest

extra_javascript:
  - javascripts/version-selector.js
```

### `versions.json` - Version Metadata

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

### `.github/workflows/docs.yml` - Automation

```yaml
# Automatic deployment on:
- Push to main branch
- Push version tags (v*)
- Pull requests (preview only)
```

## 🎨 Customization

### Styling

The version selector automatically adapts to your Material theme:

- **Colors**: Matches primary and accent colors
- **Dark mode**: Automatically switches with theme
- **Mobile**: Responsive design for all screen sizes

### Behavior

```javascript
// Customize in docs/javascripts/version-selector.js
const CONFIG = {
  versionsUrl: "../versions.json",
  currentVersion: getCurrentVersion(),
  storageKey: "finops-docs-version-preference",
};
```

## 🔍 Troubleshooting

### Common Issues

#### Version Selector Not Appearing

1. Check if `javascripts/version-selector.js` is loaded
2. Verify `versions.json` is accessible
3. Check browser console for JavaScript errors

#### 404 Errors on Version Switch

1. Ensure version is properly deployed: `./scripts/deploy-docs.sh list`
2. Check if page exists in target version
3. Verify GitHub Pages is properly configured

#### Deployment Failures

1. Check GitHub Actions logs
2. Verify mike is installed: `pip install mike`
3. Test locally: `./scripts/deploy-docs.sh serve`

### Debug Commands

```bash
# Check deployed versions
mike list

# Test local build
mkdocs build --clean --strict

# Serve locally
mike serve

# Check git configuration
git config --list | grep user
```

## 📈 Best Practices

### Version Management

- **Use semantic versioning**: v2.1.0, v2.1.1, etc.
- **Tag releases properly**: Include descriptive commit messages
- **Keep versions updated**: Regularly update for critical fixes
- **Archive old versions**: Remove very old versions to reduce maintenance

### User Experience

- **Test version switching**: Ensure smooth transitions
- **Maintain consistency**: Keep navigation structure similar across versions
- **Provide migration guides**: Help users understand version differences
- **Monitor usage**: Track which versions are most popular

### Development Workflow

```bash
# 1. Develop on main branch
git checkout main
git pull origin main

# 2. Create release
git tag -a v2.2.0 -m "Release v2.2.0: New Features"
git push origin v2.2.0

# 3. Automatic deployment via GitHub Actions
# 4. Verify deployment
./scripts/deploy-docs.sh list
```

## 🚀 Next Steps

### Immediate Actions

1. **Test the setup**: Deploy latest version and verify it works
2. **Create first version**: Tag and deploy your first stable release
3. **Verify functionality**: Test version switching in browser
4. **Update team**: Share versioning guide with your team

### Future Enhancements

- **Version comparison**: Side-by-side version comparisons
- **Change highlights**: Show what's new in each version
- **Search across versions**: Search content across all versions
- **Analytics integration**: Track version usage patterns

## 📞 Support

If you encounter issues:

1. **Check the logs**: GitHub Actions and browser console
2. **Review documentation**: `docs/versioning-guide.md`
3. **Test locally**: Use `./scripts/deploy-docs.sh serve`
4. **Check configuration**: Verify all config files are correct

---

**Your documentation versioning system is now ready!** 🎉

Users can seamlessly switch between versions while developers have powerful tools for managing documentation releases.

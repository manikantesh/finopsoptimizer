# Deployment Guide

This guide explains how to deploy FinOps Optimizer documentation to GitHub Pages with versioning support.

## Overview

The documentation is automatically deployed to GitHub Pages whenever:
- Code is pushed to the `main` branch
- A new release is created
- A pull request is opened (preview deployment)

## Deployment Process

### 1. Automatic Deployment

The deployment is handled by GitHub Actions workflows:

- **Main Deployment**: `/.github/workflows/deploy-docs.yml`
- **Release Deployment**: `/.github/workflows/release.yml`

### 2. Manual Deployment

To deploy manually:

```bash
# Install dependencies
pip install mkdocs-material mkdocs-git-revision-date-localized-plugin mkdocs-minify-plugin

# Build documentation
mkdocs build --clean

# Create version selector
python scripts/create_version_selector.py

# Deploy to GitHub Pages (requires GitHub CLI)
gh pages deploy site --branch gh-pages
```

## Versioning

### How Versioning Works

1. **Main Branch**: Always deploys to `https://manikantesh.github.io/finopsoptimizer/`
2. **Releases**: Deploy to `https://manikantesh.github.io/finopsoptimizer/v1.0.0/`
3. **Version Selector**: Allows users to switch between versions

### Creating a New Version

1. **Create a Release**:
   ```bash
   # Create and push a new tag
   git tag v1.1.0
   git push origin v1.1.0
   ```

2. **GitHub Actions will automatically**:
   - Build the documentation
   - Create a release on GitHub
   - Deploy to the versioned URL
   - Update the version selector

### Version Selector

The version selector appears in the top navigation and includes:
- Current development version (main branch)
- All released versions
- Easy switching between versions

## Configuration

### GitHub Pages Settings

1. Go to your repository settings
2. Navigate to "Pages"
3. Set source to "GitHub Actions"
4. Ensure the repository is public

### Custom Domain (Optional)

To use a custom domain:

1. Add a `CNAME` file to the `docs/` directory:
   ```
   docs.yourdomain.com
   ```

2. Configure DNS:
   ```
   docs.yourdomain.com CNAME manikantesh.github.io
   ```

3. Update `mkdocs.yml`:
   ```yaml
   site_url: https://docs.yourdomain.com/
   ```

## Troubleshooting

### Common Issues

1. **Build Failures**
   - Check GitHub Actions logs
   - Verify all dependencies are installed
   - Ensure markdown files are valid

2. **Version Selector Not Working**
   - Verify git tags exist
   - Check the version selector script
   - Ensure proper permissions

3. **Custom Domain Issues**
   - Verify DNS configuration
   - Check CNAME file
   - Wait for DNS propagation

### Debugging

```bash
# Test build locally
mkdocs build --clean

# Check for broken links
mkdocs build --strict

# Validate configuration
mkdocs build --verbose
```

## Advanced Configuration

### Custom Styling

Add custom CSS to `docs/stylesheets/extra.css`:

```css
/* Custom version selector styling */
.version-selector {
    /* Your custom styles */
}
```

### Analytics

Add Google Analytics to `mkdocs.yml`:

```yaml
extra_javascript:
  - https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID
  - javascripts/analytics.js
```

### Search Configuration

Configure search in `mkdocs.yml`:

```yaml
plugins:
  - search:
      lang: en
      separator: '[\s\-,:!=\[\]()"/`|]+'
      prebuild_index: true
```

## Security Considerations

1. **Repository Visibility**: Keep the repository public for GitHub Pages
2. **Secrets**: Don't commit sensitive information
3. **Dependencies**: Regularly update dependencies
4. **Access Control**: Limit who can deploy

## Performance Optimization

1. **Image Optimization**: Compress images before committing
2. **Minification**: Enable HTML minification
3. **Caching**: Configure proper cache headers
4. **CDN**: Consider using a CDN for better performance

## Monitoring

### Health Checks

- Monitor deployment success rates
- Track page load times
- Check for broken links
- Monitor user engagement

### Alerts

Set up alerts for:
- Failed deployments
- High error rates
- Performance degradation

## Support

For deployment issues:

1. Check GitHub Actions logs
2. Review this documentation
3. Open an issue on GitHub
4. Contact the maintainers

## Best Practices

1. **Regular Updates**: Keep documentation current
2. **Version Control**: Use semantic versioning
3. **Testing**: Test locally before deploying
4. **Backup**: Keep backups of important content
5. **Documentation**: Document deployment changes

For more information, see the [Configuration Guide](configuration.md) and [Troubleshooting Guide](troubleshooting.md). 
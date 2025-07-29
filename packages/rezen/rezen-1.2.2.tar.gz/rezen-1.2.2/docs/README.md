# ReZEN Python Client Documentation

This directory contains the complete documentation for the ReZEN Python API client, built with [MkDocs](https://mkdocs.org) and the [Material theme](https://squidfunk.github.io/mkdocs-material/).

## 📁 Structure

```
docs/
├── README.md                 # This file
├── index.md                  # Home page
├── installation.md           # Installation guide
├── quickstart.md            # Quick start guide
├── examples.md              # Usage examples and patterns
├── api-reference.md         # Complete API reference
├── troubleshooting.md       # Troubleshooting guide
├── contributing.md          # Contributing guidelines
├── changelog.md             # Version history
├── deployment.md            # Deployment guide
└── requirements.txt         # Documentation dependencies
```

## 🚀 Quick Start

### Local Development

```bash
# Install dependencies
pip install -r docs/requirements.txt

# Serve documentation locally
mkdocs serve

# Open http://127.0.0.1:8000 in your browser
```

### Using the Deployment Script

```bash
# Make script executable
chmod +x scripts/deploy_docs.sh

# Check if ready for deployment
./scripts/deploy_docs.sh check

# Test build
./scripts/deploy_docs.sh test

# Serve locally
./scripts/deploy_docs.sh serve

# Deploy to GitHub Pages (if configured)
./scripts/deploy_docs.sh deploy
```

## 🛠️ Configuration

### MkDocs Configuration

The documentation is configured via [`mkdocs.yml`](../mkdocs.yml) in the project root:

- **Theme**: Material Design with dark/light mode
- **Features**: Navigation tabs, search, code copying
- **Extensions**: Code highlighting, diagrams, admonitions
- **Navigation**: Organized into logical sections

### Dependencies

Documentation dependencies are defined in [`requirements.txt`](requirements.txt):

- `mkdocs` - Static site generator
- `mkdocs-material` - Material Design theme
- `mkdocs-minify-plugin` - HTML/CSS/JS minification
- `pymdown-extensions` - Enhanced Markdown features

## 🚀 Deployment Options

### 1. GitHub Pages (Recommended)

Automatic deployment via GitHub Actions:

- **Workflow**: [`.github/workflows/docs.yml`](../.github/workflows/docs.yml)
- **Triggers**: Push to main, docs changes, manual
- **Features**: Build caching, PR previews, strict validation

**Setup**:
1. Go to repository **Settings** → **Pages**
2. Set **Source** to "GitHub Actions"
3. Push to main branch to trigger deployment

### 2. Netlify

Alternative deployment with enhanced features:

- **Workflow**: [`.github/workflows/deploy-netlify.yml`](../.github/workflows/deploy-netlify.yml)
- **Features**: Branch previews, form handling, edge functions

**Setup**:
1. Set `NETLIFY_AUTH_TOKEN` and `NETLIFY_SITE_ID` secrets
2. Enable the workflow
3. Push to main branch

### 3. Vercel

High-performance deployment with global CDN:

- **Config**: [`vercel.json`](../vercel.json)
- **Features**: Zero-config, preview URLs, analytics

**Setup**:
1. Connect repository in Vercel dashboard
2. Automatic deployment on push

### 4. Read the Docs

Documentation-focused hosting with multiple formats:

- **Config**: [`.readthedocs.yml`](../.readthedocs.yml)
- **Features**: PDF/ePub, versioning, search

**Setup**:
1. Import project on readthedocs.org
2. Automatic builds on push

## 📝 Writing Documentation

### Markdown Guidelines

- Use clear, concise language
- Include working code examples
- Add type hints and docstrings
- Use admonitions for important notes

### Code Examples

```python
# ✅ Good: Complete, runnable example
from rezen import RezenClient

client = RezenClient()
teams = client.teams.search_teams(status="ACTIVE")
print(f"Found {len(teams)} teams")
```

### Admonitions

```markdown
!!! tip "Pro Tip"
    Use environment variables for API keys

!!! warning "Important"
    Always validate input data before API calls

!!! note "Note"
    This feature requires Python 3.7+
```

### Cross-References

```markdown
# Internal links
[API Reference](api-reference.md)
[Installation Guide](installation.md#setup)

# External links
[MkDocs Documentation](https://mkdocs.org)
```

## 🔧 Maintenance

### Adding New Pages

1. Create the Markdown file in `docs/`
2. Add to navigation in `mkdocs.yml`
3. Test locally with `mkdocs serve`
4. Update cross-references as needed

### Updating Navigation

Edit the `nav` section in [`mkdocs.yml`](../mkdocs.yml):

```yaml
nav:
  - Home: index.md
  - Getting Started:
    - Installation: installation.md
    - Quick Start: quickstart.md
  - Your New Section:
    - New Page: new-page.md
```

### Troubleshooting

Common issues and solutions:

```bash
# Build errors
mkdocs build --strict  # Shows all warnings/errors

# Missing dependencies
pip install -r docs/requirements.txt

# Navigation issues
# Ensure all nav files exist in docs/

# Broken links
# Check relative paths and file names
```

## 📊 Analytics

### Google Analytics

Add your GA4 tracking ID to `mkdocs.yml`:

```yaml
extra:
  analytics:
    provider: google
    property: G-XXXXXXXXXX
```

### Custom Analytics

Add custom tracking code to `docs/javascripts/extra.js`.

## 🤝 Contributing

### Documentation Changes

1. Edit Markdown files in `docs/`
2. Test locally: `mkdocs serve`
3. Create pull request
4. CI will test the build automatically

### Style Guide

- Follow the [Contributing Guide](contributing.md)
- Use consistent formatting
- Include examples for code changes
- Update relevant documentation

---

## 📞 Support

- **Documentation Issues**: [GitHub Issues](https://github.com/your-org/rezen-python-client/issues)
- **MkDocs Help**: [MkDocs Documentation](https://mkdocs.org)
- **Material Theme**: [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/)

---

**Happy documenting!** 📚

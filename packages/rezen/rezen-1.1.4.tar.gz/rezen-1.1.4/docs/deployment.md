# ReZEN Deployment Guide

This document consolidates all deployment processes for the ReZEN Python client, including documentation deployment, package publishing, and CI/CD workflows.

## Overview

The ReZEN project supports multiple deployment targets:

### Documentation Deployment
- **GitHub Pages** (Primary)
- **Read the Docs** (Secondary)
- **Vercel** (Alternative)
- **Netlify** (Alternative)
- **Local Development** (Testing)

### Package Publishing
- **PyPI** (Production)
- **Test PyPI** (Testing)

### CI/CD
- **GitHub Actions** (Primary CI/CD)
- **Continuous Integration** (Testing & Quality Checks)

---

## Documentation Deployment

### 1. GitHub Pages (Primary - Automated)

**Configuration**: `.github/workflows/docs.yml`

**Triggers**:
- Push to `main`/`master` with changes to docs, mkdocs.yml, or rezen code
- Pull requests (build test only)
- Manual workflow dispatch

**Process**:
1. Builds documentation with MkDocs
2. Runs tests with coverage
3. Uploads coverage to Codecov
4. Deploys to GitHub Pages (on main branch only)
5. Comments on PRs with build status

**Setup Required**:
```bash
# GitHub repository settings
Settings → Pages → Source: GitHub Actions
```

**Recent Updates** (v1.1.2):
- Enhanced workflow with debugging steps
- Fixed GitHub Pages configuration with `actions/configure-pages@v4`
- Improved error handling for Codecov uploads
- Added verbose MkDocs build output for troubleshooting

**Manual Deployment**:
```bash
# Using the provided script
./scripts/deploy_docs.sh deploy

# Or directly with MkDocs
mkdocs gh-deploy --clean
```

### 2. Read the Docs (Secondary - Automated)

**Configuration**: `.readthedocs.yml`

**Features**:
- Automatic builds on git pushes
- PDF and ePub format generation
- Search functionality
- Multiple Python version support

**Setup Required**:
1. Connect repository to Read the Docs
2. Configure webhook in GitHub repository
3. Set environment variables if needed

### 3. Vercel (Alternative - Automated)

**Configuration**: `vercel.json`

**Features**:
- Automatic deployment on git pushes
- CDN distribution
- Custom domain support
- Build caching

**Setup Required**:
1. Connect repository to Vercel
2. Configure build settings
3. Set environment variables

### 4. Netlify (Alternative - Manual Trigger)

**Configuration**: `.github/workflows/deploy-netlify.yml`

**Triggers**:
- Push to `main` with docs changes
- Manual workflow dispatch

**Setup Required**:
Set GitHub secrets:
```
NETLIFY_AUTH_TOKEN=your_netlify_token
NETLIFY_SITE_ID=your_site_id
```

### 5. Local Development

**Configuration**: `scripts/deploy_docs.sh`

**Commands**:
```bash
# Install dependencies
./scripts/deploy_docs.sh install

# Serve locally (development)
./scripts/deploy_docs.sh serve

# Build locally (testing)
./scripts/deploy_docs.sh build

# Validate configuration
./scripts/deploy_docs.sh validate

# Check deployment readiness
./scripts/deploy_docs.sh check
```

---

## Package Publishing

### 1. PyPI (Production - Automated)

**Configuration**: `.github/workflows/release.yml`

**Triggers**:
- Git tags matching `v*` pattern (e.g., `v1.0.0`)

**Process**:
1. **Testing**: Runs tests across Python 3.8-3.12
2. **Version Verification**: Ensures consistency across:
   - Git tag
   - `pyproject.toml`
   - `rezen/__init__.py`
3. **Build**: Creates source and wheel distributions
4. **Publish**: Uploads to PyPI using trusted publishing
5. **GitHub Release**: Creates release with changelog
6. **Artifacts**: Attaches build files to release

**Manual Release Process**:
```bash
# 1. Update version in all files
./scripts/bump_version.py 1.0.8

# 2. Commit and tag
git add .
git commit -m "Bump version to 1.0.8"
git tag v1.0.8

# 3. Push with tags
git push origin main --tags
```

**Setup Required**:
Set GitHub secrets:
```
PYPI_API_TOKEN=your_pypi_token
REZEN_API_KEY=your_rezen_api_key
```

### 2. Manual Publishing

**Local Build and Upload**:
```bash
# Install build tools
pip install build twine

# Build package
python -m build

# Check package
twine check dist/*

# Upload to PyPI
twine upload dist/*

# Upload to Test PyPI (testing)
twine upload --repository-url https://test.pypi.org/legacy/ dist/*
```

---

## Continuous Integration

### 1. CI Workflow (Automated)

**Configuration**: `.github/workflows/ci.yml`

**Triggers**:
- Push to `main`/`develop`
- Pull requests to `main`/`develop`

**Process**:
1. **Testing**: Multi-version Python testing (3.8-3.12)
2. **Linting**: Flake8 code quality checks
3. **Formatting**: Black code formatting validation
4. **Import Sorting**: isort validation
5. **Type Checking**: MyPy static analysis
6. **Security**: Safety vulnerability scanning
7. **Coverage**: Test coverage reporting to Codecov
8. **Build**: Package build verification

**Local Development Commands**:
```bash
# Run all checks locally
black --check .
isort --check-only .
flake8 .
mypy rezen/
pytest --cov=rezen
safety check
```

---

## Environment Configuration

### Required GitHub Secrets

```bash
# PyPI Publishing
PYPI_API_TOKEN=pypi-...

# API Testing
REZEN_API_KEY=real_v2neAIGs...

# Netlify (if using)
NETLIFY_AUTH_TOKEN=...
NETLIFY_SITE_ID=...
```

### Local Environment

**`.env` file**:
```env
REZEN_API_KEY=real_v2neAIGs2QEYJ14ck8uypMsBqOquT9TgmMzf
```

**Development Dependencies**:
```bash
pip install -r requirements-dev.txt
pip install -e ".[dev]"
```

---

## Deployment Checklist

### Before Release

- [ ] All tests passing locally
- [ ] Code formatted with Black
- [ ] Version updated in all locations
- [ ] Documentation updated
- [ ] CHANGELOG updated
- [ ] Security scan clean

### Documentation Deployment

- [ ] MkDocs configuration valid
- [ ] All documentation files present
- [ ] Links working correctly
- [ ] Examples tested

### Package Release

- [ ] Version numbers consistent
- [ ] Build artifacts clean
- [ ] Dependencies up to date
- [ ] Tests cover new features

---

## Troubleshooting

### Common Issues

1. **Documentation Build Fails**:
   ```bash
   # Check configuration
   mkdocs build --strict
   
   # Validate locally
   ./scripts/deploy_docs.sh validate
   ```

2. **Release Workflow Fails**:
   ```bash
   # Check version consistency
   grep version pyproject.toml
   grep __version__ rezen/__init__.py
   git tag --list | tail -5
   ```

3. **Test Failures**:
   ```bash
   # Run specific test suite
   pytest tests/ -v
   
   # Check coverage
   pytest --cov=rezen --cov-report=html
   ```

### Emergency Procedures

1. **Rollback Release**:
   ```bash
   # Delete tag and release
   git tag -d v1.0.x
   git push origin :refs/tags/v1.0.x
   ```

2. **Force Documentation Rebuild**:
   ```bash
   # Trigger manual workflow
   gh workflow run docs.yml
   ```

---

## Migration Notes

This deployment guide consolidates what were previously scattered across:
- Multiple GitHub Actions workflows
- Various configuration files
- Manual deployment scripts
- Platform-specific setups

All deployment processes are now documented in this single location for easier maintenance and troubleshooting. 
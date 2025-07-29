# Shared Content Includes

This directory contains shared content files that are included in both `README.md` and various documentation files to avoid duplicate maintenance.

## Files

- **`description.md`** - Main project description
- **`quick-start.md`** - Quick start installation and usage example
- **`features.md`** - Key features list
- **`installation.md`** - Installation instructions
- **`api-coverage.md`** - API endpoint coverage table (auto-generated)

## Usage

Include these files using the MkDocs include syntax:

```markdown
{!_includes/filename.md!}
```

## Maintenance

To keep content in sync:

```bash
# Validate includes are working
python scripts/sync_docs.py validate

# Update API coverage from actual code
python scripts/sync_docs.py update

# Build and validate documentation
python scripts/sync_docs.py build
```

The build process automatically updates shared content, so API coverage numbers stay accurate.

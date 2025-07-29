# Flort Documentation

This directory contains the complete documentation for Flort, built with [MkDocs](https://www.mkdocs.org/) and the [Material theme](https://squidfunk.github.io/mkdocs-material/).

## 📖 Documentation Structure

```
docs/
├── index.md              # Homepage
├── installation.md       # Installation guide  
├── quickstart.md         # Quick start tutorial
├── usage.md              # Complete command reference
├── ui-guide.md           # Interactive UI guide
├── filtering.md          # File filtering documentation
├── output-formats.md     # Output format details
├── examples.md           # Usage examples
├── api/                  # API reference
│   ├── overview.md       # API overview
│   ├── core.md          # Core functions
│   ├── files.md         # File operations
│   └── utils.md         # Utilities
├── contributing.md       # Contributing guidelines
├── troubleshooting.md    # Common issues and solutions
├── changelog.md          # Version history
└── requirements.txt      # Documentation dependencies
```

## 🚀 Quick Start

### View Documentation Locally

```bash
# Install dependencies
pip install -r docs/requirements.txt

# Serve documentation
mkdocs serve

# Open http://127.0.0.1:8000 in your browser
```

### Using Make Commands

```bash
# Serve documentation
make docs

# Build static site
make docs-build

# Deploy to GitHub Pages
make docs-deploy
```

## 🛠️ Development

### Live Editing

The documentation supports live reload during development:

```bash
# Start development server with live reload
make dev

# Or directly with mkdocs
mkdocs serve --livereload
```

Changes to markdown files, the configuration, or Python docstrings will automatically rebuild and refresh the browser.

### Building Documentation

```bash
# Build static site
mkdocs build

# Build with strict checking (fails on warnings)
mkdocs build --strict

# Clean build
mkdocs build --clean
```

## 🎨 Features

### Material Theme Features

- **Dark/Light mode toggle**
- **Mobile responsive design**
- **Search functionality**
- **Navigation with tabs**
- **Code syntax highlighting**
- **Admonitions and callouts**
- **Social links integration**

### Custom Extensions

- **Git revision dates** - Shows last modified dates
- **Git contributors** - Shows page contributors
- **API documentation** - Auto-generated from Python docstrings
- **Minification** - Optimized for fast loading
- **Link checking** - Validates internal links

### Interactive Elements

- **Tabbed code examples**
- **Copy to clipboard buttons**
- **Expandable sections**
- **Tooltips and annotations**
- **Keyboard navigation**

## 📝 Writing Guidelines

### Markdown Style

Use standard Markdown with these extensions:

```markdown
# Headers use sentence case
## Like this example

# Code blocks with language
```bash
flort . --extensions py
```

# Admonitions
!!! tip "Pro Tip"
    Use admonitions for important information

# Tabbed content
=== "Tab 1"
    Content for tab 1

=== "Tab 2"  
    Content for tab 2
```

### API Documentation

API docs are auto-generated from Python docstrings:

```python
def example_function(param: str) -> bool:
    """
    Brief description of the function.
    
    Args:
        param: Description of parameter
        
    Returns:
        Description of return value
        
    Example:
        ```python
        result = example_function("value")
        ```
    """
    pass
```

### Code Examples

Always provide working examples:

```markdown
# Show the command
```bash
flort . --extensions py --output project.txt
```

# Show expected output
```
Processing 15 files from 3 directories -> project.txt
✅ Flort completed successfully!
```
```

## 🚀 Deployment

### GitHub Pages

Documentation is automatically deployed to GitHub Pages via GitHub Actions:

1. **Push to main** - Triggers build and deploy
2. **Pull requests** - Builds preview for testing
3. **Manual deploy** - Can be triggered via `make docs-deploy`

### Custom Domain

To use a custom domain:

1. Add `CNAME` file to `docs/` directory
2. Configure DNS settings
3. Update `site_url` in `mkdocs.yml`

## 🔧 Configuration

### Main Configuration

The documentation is configured in `mkdocs.yml`:

```yaml
site_name: Flort Documentation
site_url: https://watkinslabs.github.io/flort/
repo_url: https://github.com/watkinslabs/flort

theme:
  name: material
  # ... theme configuration

plugins:
  - search
  - mkdocstrings
  - git-revision-date-localized
  # ... other plugins
```

### Dependencies

Documentation dependencies are in `docs/requirements.txt`:

```text
mkdocs>=1.5.0
mkdocs-material>=9.4.0
mkdocstrings[python]>=0.24.0
# ... other dependencies
```

## 📊 Analytics and Monitoring

### GitHub Pages Analytics

GitHub provides basic analytics for Pages sites. Advanced analytics can be added via:

- Google Analytics (add tracking ID to `mkdocs.yml`)
- Plausible Analytics (privacy-focused alternative)
- GitHub Insights (repository-level statistics)

### Link Checking

Validate all documentation links:

```bash
# Check internal links
make docs-check

# Manual link checking
mkdocs build --strict
```

## 🤝 Contributing to Documentation

### Quick Edits

1. **GitHub Web Editor** - Click "Edit this page" on any documentation page
2. **Local Development** - Clone repo and edit markdown files
3. **Pull Requests** - Submit changes for review

### Adding New Pages

1. Create markdown file in appropriate directory
2. Add to navigation in `mkdocs.yml`
3. Follow existing style and structure
4. Test locally before submitting

### Style Guide

- Use **sentence case** for headings
- Include **code examples** for all features
- Add **screenshots** for UI features
- Use **admonitions** for important notes
- Keep **paragraphs short** and scannable
- Include **cross-references** to related sections

## 🆘 Troubleshooting

### Build Errors

```bash
# Clear cache and rebuild
rm -rf site/
mkdocs build --clean

# Check for syntax errors
mkdocs build --strict
```

### Plugin Issues

```bash
# Reinstall dependencies
pip install -r docs/requirements.txt --force-reinstall

# Check plugin versions
pip list | grep mkdocs
```

### Missing Dependencies

```bash
# Install all documentation dependencies
make install-docs

# Or install manually
pip install -r docs/requirements.txt
```

## 📞 Support

- **Documentation Issues**: [GitHub Issues](https://github.com/watkinslabs/flort/issues)
- **General Questions**: [GitHub Discussions](https://github.com/watkinslabs/flort/discussions)
- **Contributing**: See [Contributing Guide](contributing.md)

---

**Happy documenting! 📚✨**
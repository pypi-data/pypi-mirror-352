# Changelog

All notable changes to Flort will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.25] - 2025-06-02

### Added
- Initial release of Flort
- File concatenation and project overview functionality
- Interactive UI with curses support
- Python code outline generation
- Advanced file filtering system
- Directory tree generation
- Token counting and analysis
- Archive creation (ZIP/TAR.GZ)
- Comprehensive documentation with MkDocs
- GitHub Pages integration

### Features
- **File Discovery**: Intelligent file scanning with include/exclude filtering
- **Extension Filtering**: Support for multiple file types with exclusion patterns
- **Pattern Matching**: Glob patterns for advanced file selection
- **Directory Management**: Ignore directories and limit traversal depth
- **Interactive UI**: Curses-based file selector with mouse support
- **Python Analysis**: Extract class/function signatures and docstrings
- **Output Formats**: Standard, tree-only, outline, and manifest modes
- **Performance**: Optimized for large codebases
- **Cross-Platform**: Linux, macOS, and Windows support

## [0.1.24] - 2025-06-01

### Added
- Complete rewrite with modular architecture
- Interactive file selector with curses interface
- Python code outline generation
- Advanced filtering pipeline
- Archive creation support
- Comprehensive test suite
- Professional documentation site

### Changed
- Improved performance for large projects
- Better error handling and user feedback
- Cleaner command-line interface
- Enhanced file type detection

### Fixed
- Binary file detection issues
- Memory usage optimization
- Cross-platform compatibility

## [0.1.0] - 2025-01-05 Initial Release

### Added
- Basic file concatenation functionality
- Directory tree generation
- Simple file filtering
- Command-line interface

---

## Release Guidelines

### Version Numbers
- **Major** (X.0.0): Breaking changes, major new features
- **Minor** (X.Y.0): New features, backward compatible
- **Patch** (X.Y.Z): Bug fixes, minor improvements

### Release Process
1. Update version in `setup.py` and `flort/__init__.py`
2. Update CHANGELOG.md with new version
3. Create git tag: `git tag -a v2.0.0 -m "Release v2.0.0"`
4. Push tags: `git push origin --tags`
5. GitHub Actions will automatically build and deploy

### Categories
- **Added**: New features
- **Changed**: Changes in existing functionality
- **Deprecated**: Soon-to-be removed features
- **Removed**: Removed features
- **Fixed**: Bug fixes
- **Security**: Security vulnerability fixes
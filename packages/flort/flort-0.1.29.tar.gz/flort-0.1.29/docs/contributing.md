# Contributing to Flort

Thank you for your interest in contributing to Flort! This guide will help you get started with development and explain our contribution process.

## 🚀 Getting Started

### Development Setup

1. **Fork and Clone**

```bash
# Fork the repository on GitHub, then:
git clone https://github.com/yourusername/flort.git
cd flort
```

2. **Create Virtual Environment**

```bash
# Create environment
python -m venv venv

# Activate (Linux/macOS)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate
```

3. **Install Development Dependencies**

```bash
# Install in development mode
pip install -e .

# Install development dependencies
pip install -e .[dev]

# Install documentation dependencies
pip install -r docs/requirements.txt
```

4. **Verify Installation**

```bash
# Test installation
flort --version
python -m pytest tests/ -v
```

## 🛠️ Development Workflow

### Making Changes

1. **Create Feature Branch**

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/issue-description
```

2. **Make Your Changes**

Follow the [coding standards](#coding-standards) and add tests for new functionality.

3. **Test Your Changes**

```bash
# Run all tests
make test

# Run specific tests
python -m pytest tests/test_specific.py -v

# Test with coverage
python -m pytest tests/ --cov=flort --cov-report=html
```

4. **Update Documentation**

```bash
# Update relevant documentation
# docs/usage.md, docs/examples.md, etc.

# Test documentation locally
make docs

# Check documentation build
make docs-build
```

5. **Commit and Push**

```bash
git add .
git commit -m "feat: add new filtering option"
git push origin feature/your-feature-name
```

6. **Create Pull Request**

Open a pull request on GitHub with a clear description of your changes.

## 📋 Contribution Types

### 🐛 Bug Fixes

1. **Find or Create Issue**
   - Search [existing issues](https://github.com/watkinslabs/flort/issues)
   - Create new issue with [bug report template](https://github.com/watkinslabs/flort/issues/new?template=bug_report.yml)

2. **Fix the Bug**
   - Write a failing test that reproduces the bug
   - Fix the bug
   - Ensure the test now passes
   - Add regression test if appropriate

3. **Example Bug Fix**

```python
# tests/test_bug_fix.py
def test_extension_filtering_bug():
    """Test that extensions with dots are handled correctly."""
    # This test would fail before the fix
    result = parse_extensions([".py", "js"])
    assert result == ["py", "js"]  # Should normalize extensions
```

### ✨ New Features

1. **Discussion First**
   - Open a [feature request](https://github.com/watkinslabs/flort/issues/new?template=feature_request.yml)
   - Discuss the approach before implementing

2. **Implementation Guidelines**
   - Follow existing patterns and architecture
   - Add comprehensive tests
   - Update documentation
   - Consider backward compatibility

3. **Example Feature Addition**

```python
# flort/new_feature.py
def new_filtering_option(file_list, criteria):
    """
    New filtering functionality.
    
    Args:
        file_list: List of file dictionaries
        criteria: Filtering criteria
        
    Returns:
        Filtered file list
    """
    # Implementation here
    pass

# tests/test_new_feature.py
def test_new_filtering_option():
    """Test the new filtering functionality."""
    # Test implementation
    pass
```

### 📖 Documentation

1. **Types of Documentation**
   - Code comments and docstrings
   - User guides and examples
   - API documentation
   - README and setup instructions

2. **Documentation Standards**
   - Use clear, concise language
   - Include code examples
   - Update relevant sections
   - Test documentation builds

### 🧪 Testing

1. **Test Types**
   - Unit tests for individual functions
   - Integration tests for workflows
   - UI tests for interactive features
   - Performance tests for large files

2. **Writing Tests**

```python
# tests/test_example.py
import pytest
from pathlib import Path
from flort.utils import example_function

class TestExampleFunction:
    """Test suite for example_function."""
    
    def test_basic_functionality(self):
        """Test basic use case."""
        result = example_function("input")
        assert result == "expected_output"
    
    def test_edge_cases(self):
        """Test edge cases and error conditions."""
        with pytest.raises(ValueError):
            example_function("")
    
    def test_with_fixtures(self, tmp_path):
        """Test using pytest fixtures."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")
        
        result = example_function(test_file)
        assert result is not None
```

## 📏 Coding Standards

### Python Style

We follow [PEP 8](https://pep8.org/) with some modifications:

```python
# Use snake_case for functions and variables
def process_file_list(file_list):
    processed_count = 0
    return processed_count

# Use descriptive names
def get_filtered_files(extensions, exclude_patterns):
    # Not: get_files(ext, exc)
    pass

# Add type hints where helpful
def count_tokens(text: str) -> int:
    """Count tokens in text."""
    return len(text.split())

# Use docstrings for public functions
def public_function(param: str) -> bool:
    """
    Brief description of what this function does.
    
    Args:
        param: Description of parameter
        
    Returns:
        Description of return value
        
    Example:
        ```python
        result = public_function("value")
        ```
    """
    pass
```

### Code Formatting

We use automated tools for consistent formatting:

```bash
# Format code with black
black flort/ tests/

# Sort imports with isort  
isort flort/ tests/

# Check style with flake8
flake8 flort/ tests/

# Type checking with mypy
mypy flort/ --ignore-missing-imports

# Run all checks
make check-all
```

### Commit Messages

Use [Conventional Commits](https://www.conventionalcommits.org/):

```bash
# Feature addition
git commit -m "feat: add new file filtering option"

# Bug fix
git commit -m "fix: handle empty directory gracefully"

# Documentation
git commit -m "docs: update installation guide"

# Tests
git commit -m "test: add tests for file filtering"

# Refactoring
git commit -m "refactor: simplify path handling logic"
```

## 🧪 Testing Guidelines

### Test Structure

```
tests/
├── __init__.py
├── test_utils.py           # Test utility functions
├── test_traverse.py        # Test file discovery
├── test_concatenate.py     # Test file concatenation
├── test_cli.py            # Test command-line interface
├── test_ui.py             # Test interactive UI
└── fixtures/              # Test data and fixtures
    ├── sample_project/
    └── test_files/
```

### Writing Good Tests

```python
# Good test example
def test_file_filtering_with_extensions(tmp_path):
    """Test file filtering with specific extensions."""
    # Setup
    (tmp_path / "main.py").write_text("print('hello')")
    (tmp_path / "style.css").write_text("body { }")
    (tmp_path / "README.md").write_text("# Project")
    
    # Execute
    file_list = get_paths(
        directories=[str(tmp_path)],
        extensions=['py', 'md']
    )
    
    # Verify
    files = [f for f in file_list if f['type'] == 'file']
    file_names = [f['path'].name for f in files]
    
    assert 'main.py' in file_names
    assert 'README.md' in file_names
    assert 'style.css' not in file_names
```

### Test Coverage

Aim for high test coverage, especially for:

- Core functionality
- Error handling
- Edge cases
- User-facing APIs

```bash
# Run tests with coverage
python -m pytest tests/ --cov=flort --cov-report=html

# View coverage report
open htmlcov/index.html
```

## 📚 Documentation Guidelines

### Code Documentation

```python
def complex_function(param1: str, param2: List[int], param3: bool = False) -> Dict[str, Any]:
    """
    Brief one-line description.
    
    Longer description explaining the purpose, behavior, and any important
    details about the function.
    
    Args:
        param1: Description of first parameter
        param2: Description of second parameter  
        param3: Description of optional parameter (default: False)
        
    Returns:
        Description of return value and its structure
        
    Raises:
        ValueError: When param1 is empty
        IOError: When file operations fail
        
    Example:
        ```python
        result = complex_function("input", [1, 2, 3], True)
        print(result['status'])
        ```
        
    Note:
        Any additional notes or warnings
    """
    pass
```

### User Documentation

1. **Keep it practical** - Focus on real-world usage
2. **Include examples** - Show working code snippets
3. **Explain why** - Not just how, but when and why to use features
4. **Update together** - Update docs with code changes

### Documentation Testing

```bash
# Test documentation builds
make docs-build

# Test documentation locally
make docs

# Check for broken links
make docs-check
```

## 🔍 Code Review Process

### Submitting Pull Requests

1. **Clear Description**
   - Explain what changes you made and why
   - Reference any related issues
   - Include screenshots for UI changes

2. **Checklist Before Submitting**
   - [ ] Tests pass locally
   - [ ] New tests added for new functionality
   - [ ] Documentation updated
   - [ ] Code follows style guidelines
   - [ ] Commit messages follow convention

3. **Pull Request Template**

```markdown
## Description
Brief description of changes made.

## Related Issues
Fixes #123

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Refactoring

## Testing
- [ ] All tests pass
- [ ] New tests added
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
```

### Review Process

1. **Automated Checks**
   - Tests must pass
   - Code style checks
   - Documentation builds

2. **Human Review**
   - Code quality and clarity
   - Test coverage and quality
   - Documentation accuracy
   - User experience impact

3. **Addressing Feedback**
   - Respond to review comments
   - Make requested changes
   - Update based on suggestions

## 🏗️ Architecture Guidelines

### Project Structure

```
flort/
├── flort/              # Main package
│   ├── __init__.py     # Public API exports
│   ├── cli.py          # Command-line interface
│   ├── traverse.py     # File discovery logic
│   ├── concatenate_files.py  # File processing
│   ├── utils.py        # Utility functions
│   └── ...
├── tests/              # Test suite
├── docs/               # Documentation
└── examples/           # Usage examples
```

### Design Principles

1. **Modularity** - Keep functions and classes focused
2. **Testability** - Design for easy testing
3. **Extensibility** - Allow for future enhancements
4. **User-Friendly** - Prioritize user experience
5. **Performance** - Consider efficiency for large projects

### Adding New Features

1. **Plan the Architecture**
   - Where does the feature fit?
   - What existing code needs changes?
   - How will it be tested?

2. **Implement Incrementally**
   - Start with core functionality
   - Add tests early
   - Build up complexity gradually

3. **Consider Backward Compatibility**
   - Don't break existing APIs
   - Deprecate features gracefully
   - Document breaking changes

## 🎯 Specific Areas for Contribution

### High-Priority Areas

1. **Performance Optimization**
   - Large file handling
   - Memory usage optimization
   - Faster file discovery

2. **Platform Support**
   - Windows-specific improvements
   - macOS compatibility
   - Linux distribution testing

3. **New File Types**
   - Additional language support
   - Binary file handling improvements
   - Custom file processors

4. **User Experience**
   - Interactive UI enhancements
   - Better error messages
   - Progress indicators

### Good First Issues

Look for issues labeled:
- `good first issue`
- `help wanted`
- `documentation`
- `tests`

## 🙋 Getting Help

### Communication Channels

1. **GitHub Issues** - Bug reports and feature requests
2. **GitHub Discussions** - Questions and general discussion
3. **Code Reviews** - Feedback on pull requests

### Questions?

- Check existing documentation first
- Search closed issues for similar questions
- Ask in GitHub Discussions
- Be specific about what you're trying to do

## 📜 License

By contributing to Flort, you agree that your contributions will be licensed under the BSD 3-Clause License.

---

**Thank you for contributing to Flort! Every contribution, no matter how small, helps make the project better for everyone. 🎉**
# Contributing to Kalakan TTS

Thank you for your interest in contributing to Kalakan TTS! This guide will help you understand how to contribute to the project, from reporting bugs to submitting code changes.

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [How to Contribute](#how-to-contribute)
4. [Development Workflow](#development-workflow)
5. [Pull Request Process](#pull-request-process)
6. [Coding Standards](#coding-standards)
7. [Testing Guidelines](#testing-guidelines)
8. [Documentation Guidelines](#documentation-guidelines)
9. [Community](#community)
10. [Recognition](#recognition)

## Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct. Please read it before contributing.

We are committed to providing a welcoming and inclusive environment for all contributors regardless of gender, sexual orientation, disability, physical appearance, body size, race, ethnicity, age, religion, or nationality.

Examples of behavior that contributes to creating a positive environment include:

- Using welcoming and inclusive language
- Being respectful of differing viewpoints and experiences
- Gracefully accepting constructive criticism
- Focusing on what is best for the community
- Showing empathy towards other community members

Examples of unacceptable behavior include:

- The use of sexualized language or imagery
- Personal attacks or derogatory comments
- Trolling, insulting/derogatory comments, and personal or political attacks
- Public or private harassment
- Publishing others' private information without explicit permission
- Other conduct which could reasonably be considered inappropriate in a professional setting

## Getting Started

### Prerequisites

Before you begin, ensure you have the following installed:

- Python 3.9+
- Git
- PyTorch 2.0+
- A code editor (VS Code, PyCharm, etc.)

### Setting Up the Development Environment

1. Fork the repository on GitHub.

2. Clone your fork locally:
```bash
git clone https://github.com/your-username/kalakan-tts.git
cd kalakan-tts
```

3. Add the original repository as an upstream remote:
```bash
git remote add upstream https://github.com/kalakan-ai/kalakan-tts.git
```

4. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

5. Install the package in development mode:
```bash
pip install -e ".[dev,api,training]"
```

6. Install pre-commit hooks:
```bash
pre-commit install
```

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported by searching the [GitHub Issues](https://github.com/kalakan-ai/kalakan-tts/issues).

2. If the bug hasn't been reported, create a new issue. Include:
   - A clear title and description
   - Steps to reproduce the bug
   - Expected behavior
   - Actual behavior
   - System information (OS, Python version, etc.)
   - Any relevant logs or screenshots

### Suggesting Enhancements

1. Check if the enhancement has already been suggested by searching the [GitHub Issues](https://github.com/kalakan-ai/kalakan-tts/issues).

2. If the enhancement hasn't been suggested, create a new issue. Include:
   - A clear title and description
   - The rationale for the enhancement
   - Potential implementation details
   - Any relevant examples or references

### Contributing Code

1. Find an issue to work on or create a new one.

2. Comment on the issue to let others know you're working on it.

3. Create a new branch for your changes:
```bash
git checkout -b feature/your-feature-name
```

4. Make your changes, following the [Coding Standards](#coding-standards).

5. Add tests for your changes, following the [Testing Guidelines](#testing-guidelines).

6. Update documentation as needed, following the [Documentation Guidelines](#documentation-guidelines).

7. Commit your changes with a descriptive commit message:
```bash
git commit -m "Add feature: your feature description"
```

8. Push your changes to your fork:
```bash
git push origin feature/your-feature-name
```

9. Create a pull request following the [Pull Request Process](#pull-request-process).

### Contributing Documentation

1. Find documentation that needs improvement or create a new documentation file.

2. Create a new branch for your changes:
```bash
git checkout -b docs/your-docs-change
```

3. Make your changes, following the [Documentation Guidelines](#documentation-guidelines).

4. Commit your changes with a descriptive commit message:
```bash
git commit -m "Docs: your documentation change description"
```

5. Push your changes to your fork:
```bash
git push origin docs/your-docs-change
```

6. Create a pull request following the [Pull Request Process](#pull-request-process).

## Development Workflow

### Keeping Your Fork Updated

1. Fetch changes from the upstream repository:
```bash
git fetch upstream
```

2. Update your main branch:
```bash
git checkout main
git merge upstream/main
```

3. Push the changes to your fork:
```bash
git push origin main
```

### Creating a Feature Branch

1. Create a new branch for your feature or bug fix:
```bash
git checkout -b feature/your-feature-name
```

2. Make your changes, commit them, and push to your fork:
```bash
git add .
git commit -m "Add feature: your feature description"
git push origin feature/your-feature-name
```

### Running Tests

1. Run the test suite:
```bash
pytest
```

2. Run specific tests:
```bash
pytest tests/unit/test_text.py
```

3. Run tests with coverage:
```bash
pytest --cov=kalakan
```

### Checking Code Quality

1. Run linting checks:
```bash
flake8 kalakan tests
```

2. Run type checking:
```bash
mypy kalakan
```

3. Run code formatting:
```bash
black kalakan tests
isort kalakan tests
```

## Pull Request Process

1. Create a pull request from your feature branch to the main repository's `main` branch.

2. Fill out the pull request template, including:
   - A clear title and description
   - Reference to the issue(s) being addressed
   - Changes made
   - Testing performed
   - Screenshots or examples (if applicable)

3. Wait for the CI checks to pass.

4. Address any feedback from reviewers.

5. Once approved, a maintainer will merge your pull request.

### Pull Request Checklist

Before submitting a pull request, ensure:

- [ ] The code follows the [Coding Standards](#coding-standards)
- [ ] Tests have been added or updated
- [ ] Documentation has been updated
- [ ] The code passes all CI checks
- [ ] The branch is up to date with the main repository

## Coding Standards

### Python Style Guide

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) guidelines
- Use [Black](https://black.readthedocs.io/) for code formatting
- Use [isort](https://pycqa.github.io/isort/) for import sorting
- Maximum line length: 88 characters
- Use type hints for all function parameters and return values

### Docstrings

- Use Google-style docstrings:
```python
def function(param1, param2):
    """
    Function description.
    
    Args:
        param1: Description of param1.
        param2: Description of param2.
        
    Returns:
        Description of return value.
        
    Raises:
        ExceptionType: When and why this exception is raised.
    """
    pass
```

### Imports

- Group imports in the following order:
  1. Standard library imports
  2. Related third-party imports
  3. Local application/library-specific imports
- Use absolute imports for external packages
- Use relative imports for internal modules

### Naming Conventions

- **Modules**: lowercase with underscores (e.g., `text_processing.py`)
- **Classes**: CamelCase (e.g., `TwiTokenizer`)
- **Functions/Methods**: lowercase with underscores (e.g., `process_text()`)
- **Variables**: lowercase with underscores (e.g., `phoneme_sequence`)
- **Constants**: UPPERCASE with underscores (e.g., `MAX_SEQUENCE_LENGTH`)

## Testing Guidelines

### Test Structure

- Place tests in the `tests/` directory
- Mirror the package structure in the test directory
- Name test files with the `test_` prefix
- Name test functions with the `test_` prefix

### Test Types

1. **Unit Tests**:
   - Test individual components in isolation
   - Mock external dependencies
   - Fast to run

2. **Integration Tests**:
   - Test interactions between components
   - May require more resources
   - May take longer to run

3. **Performance Tests**:
   - Test system performance and resource usage
   - Run on specific hardware configurations
   - May take significant time to run

### Test Coverage

- Aim for high test coverage (>80%)
- Focus on testing edge cases and error conditions
- Include both positive and negative test cases

### Test Fixtures

- Use pytest fixtures for test setup
- Share fixtures across test files when appropriate
- Clean up resources after tests

## Documentation Guidelines

### Code Documentation

- Document all public modules, classes, and functions
- Include parameter descriptions, return values, and examples
- Document exceptions that may be raised
- Keep docstrings up-to-date with code changes

### User Documentation

- Write clear, concise, and accurate documentation
- Include examples for common use cases
- Use proper Markdown formatting
- Include diagrams or screenshots when helpful

### Documentation Structure

- Place documentation in the `docs/` directory
- Use descriptive filenames
- Include a table of contents for longer documents
- Link related documents together

## Community

### Communication Channels

- **GitHub Issues**: For bug reports, feature requests, and discussions
- **GitHub Discussions**: For general questions and community discussions
- **Slack Channel**: For real-time communication (invitation available upon request)
- **Mailing List**: For announcements and broader discussions

### Community Meetings

- We hold monthly community meetings to discuss project direction and progress
- Meeting schedules are announced on the mailing list and Slack
- Meeting notes are posted in the GitHub repository

## Recognition

We value all contributions to the project, including:

- Code contributions
- Documentation improvements
- Bug reports
- Feature suggestions
- Community support

Contributors are recognized in the following ways:

- Listed in the CONTRIBUTORS.md file
- Mentioned in release notes for significant contributions
- Opportunity to become a project maintainer after sustained contributions

---

Thank you for contributing to Kalakan TTS! Your efforts help improve the project for everyone.
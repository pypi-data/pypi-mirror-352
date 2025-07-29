# Contributing to Todo.txt MCP Server

Thank you for your interest in contributing to the Todo.txt MCP Server! This project aims to provide a robust, extensible MCP server for todo.txt file management with AI assistants.

## 🚀 Getting Started

### Prerequisites

- **Python 3.10+** - Required for the project
- **uv** - Package manager (recommended) or pip
- **Git** - Version control
- **Node.js** (optional) - For testing Claude Desktop integration

### Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/yourusername/todo-txt-mcp.git
   cd todo-txt-mcp
   ```

2. **Set up Environment**
   ```bash
   # Using uv (recommended)
   uv install --dev
   
   # Or using pip
   pip install -e ".[dev]"
   ```

3. **Verify Installation**
   ```bash
   # Run tests
   uv run pytest
   
   # Check code quality
   uv run ruff check
   uv run black --check .
   uv run mypy .
   ```

4. **Test the Server**
   ```bash
   # Start the server
   uv run todo-txt-mcp
   
   # Or test with MCP Inspector
   uv run mcp dev src/todo_txt_mcp/server.py
   ```

## 📋 How to Contribute

### 1. Issues and Feature Requests

- **Bug Reports**: Use the bug report template
- **Feature Requests**: Use the feature request template
- **Questions**: Use GitHub Discussions for general questions

### 2. Pull Request Process

1. **Create a Branch**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/issue-description
   ```

2. **Make Changes**
   - Follow the coding standards below
   - Add tests for new functionality
   - Update documentation as needed

3. **Test Your Changes**
   ```bash
   # Run full test suite
   uv run pytest -v --cov=src/todo_txt_mcp --cov-report=html
   
   # Check code quality
   uv run ruff check
   uv run black .
   uv run mypy .
   ```

4. **Commit and Push**
   ```bash
   git add .
   git commit -m "feat: add new feature description"
   git push origin feature/your-feature-name
   ```

5. **Create Pull Request**
   - Fill out the PR template
   - Link related issues
   - Ensure all checks pass

## 🏗️ Architecture Guidelines

### Project Structure
```
src/todo_txt_mcp/
├── __init__.py          # Package initialization
├── server.py            # Main MCP server
├── models/              # Data models
│   ├── config.py        # Configuration model
│   └── todo.py          # Todo item and list models
├── services/            # Business logic
│   ├── file_service.py  # File I/O operations
│   └── todo_service.py  # Todo business logic
└── tools/               # MCP tools
    ├── crud_tools.py    # Create/Update/Delete tools
    └── list_tools.py    # List/Query tools
```

### Design Principles

1. **Separation of Concerns**: Keep models, services, and tools separated
2. **Type Safety**: Use Pydantic models and type hints throughout
3. **Error Handling**: Provide meaningful error messages
4. **Testability**: Write testable, pure functions where possible
5. **MCP Compliance**: Follow MCP specification strictly

### Adding New Features

#### Adding a New MCP Tool

1. **Define the Tool**
   ```python
   # In appropriate tools file
   from fastmcp import FastMCP
   
   @mcp.tool()
   def your_new_tool(param: str) -> str:
       """
       Tool description for the AI.
       
       Args:
           param: Description of parameter
           
       Returns:
           Description of return value
       """
       # Implementation
       return result
   ```

2. **Add Tests**
   ```python
   # In tests/unit/test_tools.py
   def test_your_new_tool():
       result = your_new_tool("test_input")
       assert result == "expected_output"
   ```

3. **Update Documentation**
   - Add tool to README.md
   - Update API documentation if needed

#### Adding a New Service Method

1. **Add to Service Class**
   ```python
   # In services/todo_service.py
   class TodoService:
       def new_method(self, param: str) -> ReturnType:
           """Method description."""
           # Implementation
   ```

2. **Add Tests**
   ```python
   # In tests/unit/test_todo_service.py
   def test_new_method():
       service = TodoService()
       result = service.new_method("test")
       assert result == expected
   ```

## 🧪 Testing

### Test Structure
```
tests/
├── unit/                # Unit tests
│   ├── test_models.py
│   ├── test_services.py
│   └── test_tools.py
├── integration/         # Integration tests
│   └── test_server.py
└── fixtures/            # Test data
    └── sample_todos.txt
```

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src/todo_txt_mcp --cov-report=html

# Run specific test file
uv run pytest tests/unit/test_todo_service.py

# Run with verbose output
uv run pytest -v
```

### Writing Tests

- **Unit Tests**: Test individual functions/methods
- **Integration Tests**: Test MCP server integration
- **Use Fixtures**: Provide reusable test data
- **Mock External Dependencies**: Use pytest fixtures for file operations

## 🎨 Code Style

### Formatting and Linting

We use several tools to maintain code quality:

```bash
# Format code
uv run black .

# Lint code
uv run ruff check

# Type checking
uv run mypy .

# Run all checks
uv run ruff check && uv run black --check . && uv run mypy .
```

### Style Guidelines

1. **Python Style**: Follow PEP 8 with Black formatting
2. **Type Hints**: Use type hints for all function parameters and returns
3. **Docstrings**: Use Google-style docstrings
4. **Naming**: Use descriptive variable and function names
5. **Comments**: Explain complex logic, not obvious code

### Example Code Style

```python
from typing import List, Optional
from pydantic import BaseModel

class TodoItem(BaseModel):
    """Represents a single todo item."""
    
    id: str
    text: str
    priority: Optional[str] = None
    projects: List[str] = []
    contexts: List[str] = []
    
    def is_completed(self) -> bool:
        """Check if the todo item is marked as completed.
        
        Returns:
            True if the todo is completed, False otherwise.
        """
        return self.text.startswith('x ')
```

## 📚 Documentation

### What to Document

1. **New Features**: Update README.md with usage examples
2. **API Changes**: Update tool descriptions and examples
3. **Configuration**: Document new configuration options
4. **Breaking Changes**: Clearly mark in CHANGELOG.md

### Documentation Style

- Use clear, concise language
- Provide code examples
- Include expected outputs
- Link to related documentation

## 🐛 Bug Reports

When reporting bugs, please include:

1. **Environment Details**
   - Python version
   - Operating system
   - Package version
   - MCP client (Claude Desktop, etc.)

2. **Reproduction Steps**
   - Minimal code to reproduce
   - Input data that causes the issue
   - Expected vs actual behavior

3. **Error Messages**
   - Full stack traces
   - Log output if available

## 💡 Feature Requests

For feature requests, please:

1. **Describe the Use Case**: What problem does this solve?
2. **Proposed Solution**: How should it work?
3. **Alternatives Considered**: What other approaches did you consider?
4. **Implementation Ideas**: Any thoughts on how to implement it?

## 🚀 Release Process

### Version Numbering

We follow [Semantic Versioning](https://semver.org/):
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Checklist

1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md`
3. Run full test suite
4. Create release PR
5. Tag release after merge
6. Publish to PyPI (automated)

## 🤝 Community

### Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). Please read it before participating.

### Getting Help

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions and community support
- **Documentation**: Check README.md and inline documentation

### Recognition

Contributors are recognized in:
- GitHub contributors list
- Release notes for significant contributions
- README.md acknowledgments section

## 📄 License

By contributing to this project, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to Todo.txt MCP Server! 🎉 
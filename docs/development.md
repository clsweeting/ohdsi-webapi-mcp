# Development

### Prerequisites

- Python 3.11+
- Poetry
- Access to an OHDSI WebAPI instance

### Setup

```bash
# Clone the repository
git clone https://github.com/clsweeting/ohdsi-webapi-mcp.git
cd ohdsi-webapi-mcp

# Install dependencies
poetry install

# Run tests
poetry run pytest

# Format code
poetry run black src tests
poetry run isort src tests
```

### Configuration

Create a `.env` file or set environment variables:

```bash
WEBAPI_BASE_URL=https://atlas-demo.ohdsi.org/WebAPI
```

### Running the Server

```bash
# Start the MCP server
poetry run ohdsi-webapi-mcp

# Or run directly
poetry run python -m ohdsi_webapi_mcp.server
```

### Testing

The best way to test the MCP server is using the [MCP Inspector](https://github.com/modelcontextprotocol/inspector) tool, which provides an interactive web interface for testing MCP servers:

```bash
# Install MCP Inspector globally
npm install -g @modelcontextprotocol/inspector

# Test the server with your WebAPI instance
WEBAPI_BASE_URL=https://your-webapi-instance.org/WebAPI WEBAPI_SOURCE_KEY=your-source-key mcp-inspector poetry run ohdsi-webapi-mcp
```

This will open a web interface where you can:
- View all available tools and their schemas
- Test individual tools with different parameters
- See real-time request/response data
- Verify tool outputs are properly formatted for LLMs

The Inspector is particularly useful for:
- Debugging tool implementations
- Testing different parameter combinations
- Validating that outputs work well with LLM agents
- Understanding the MCP protocol flow

## Testing Methodology

This project follows a comprehensive testing strategy with multiple layers:

### Test Organization

```
tests/
├── conftest.py              # Shared fixtures and configuration
├── unit/                    # Fast, isolated tests with mocked dependencies
│   ├── test_concepts.py     # Test individual tool functions
│   └── test_server.py       # Test configuration and server setup
└── integration/             # Full server lifecycle tests
    └── test_integration.py  # Test actual server process startup/shutdown
```

### Testing Layers

#### 1. **Unit Tests** (`tests/unit/`)
Fast tests that focus on individual functions with mocked external dependencies:

```bash
# Run only unit tests
poetry run pytest tests/unit/ -v

# Run with coverage
poetry run pytest tests/unit/ --cov=src --cov-report=html
```

**Principles:**
- ✅ Mock all external dependencies (WebAPI, databases)
- ✅ Test individual tool functions in isolation
- ✅ Test configuration validation and error handling
- ✅ Verify output format is LLM-compatible (`List[TextContent]`)
- ✅ Fast execution (< 1 second per test)

#### 2. **Integration Tests** (`tests/integration/`)
Tests that verify the full MCP server process and protocol compliance:

```bash
# Run only integration tests
poetry run pytest tests/integration/ -v
```

**Principles:**
- ✅ Test actual server process startup and shutdown
- ✅ Verify MCP protocol compliance
- ✅ Test CLI entry points work correctly
- ✅ Test error handling for missing environment variables
- ✅ Test server responsiveness and performance

#### 3. **Interactive Testing** (MCP Inspector)
Manual testing using the MCP Inspector for development and debugging:

```bash
# Interactive testing with Inspector
WEBAPI_BASE_URL=https://atlas-demo.ohdsi.org/WebAPI WEBAPI_SOURCE_KEY=EUNOMIA mcp-inspector poetry run ohdsi-webapi-mcp
```

**Use Cases:**
- 🔍 Debugging tool implementations
- 🧪 Testing different parameter combinations
- 🎯 Validating outputs work well with LLM agents
- 📋 Understanding MCP protocol message flow

### Running All Tests

```bash
# Run all tests
poetry run pytest

# Run with coverage report
poetry run pytest --cov=src --cov-report=html --cov-report=term

# Run specific test types
poetry run pytest tests/unit/                    # Unit tests only
poetry run pytest tests/integration/             # Integration tests only
poetry run pytest -k "test_search_concepts"      # Tests matching pattern
```

### Testing Best Practices

#### ✅ **Do This:**
- **Mock external dependencies** in unit tests for speed and reliability
- **Test configuration handling** including missing environment variables
- **Test error conditions** like network failures and invalid inputs
- **Verify output format** ensures LLM compatibility
- **Use integration tests** for full server lifecycle validation
- **Test both success and failure paths**

#### ❌ **Avoid This:**
- **Don't test against live APIs** in unit tests (slow and unreliable)
- **Don't ignore async/await patterns** in test functions
- **Don't skip error case testing**
- **Don't test MCP protocol internals** (use MCP Inspector instead)
- **Don't write slow unit tests** (use integration tests for full workflows)

### Continuous Integration

The test suite is designed for CI/CD environments:

```bash
# CI-friendly test command
poetry run pytest --cov=src --cov-report=xml --cov-fail-under=80
```

This ensures:
- All tests pass before deployment
- Code coverage meets minimum thresholds
- Both unit and integration tests are validated


## Contributing

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Make your changes and add tests
3. Ensure all tests pass: `make`
4. Lint & format code: `make lint`, `make fix` and `make format`
5. Submit a pull request

## Building and Publishing

### Local Development Build

```bash
# Clean previous builds
make clean

# Build the package
make build
# or: poetry build

# This creates:
# - dist/ohdsi_webapi_mcp-*.whl (wheel)
# - dist/ohdsi-webapi-mcp-*.tar.gz (source distribution)
```

### Testing the Built Package

Before publishing, test the built package locally:

```bash
# Install from the built wheel in a fresh environment
pip install dist/ohdsi_webapi_mcp-*.whl

# Test that the command works
ohdsi-webapi-mcp --help

# Test installation with pipx
pipx install dist/ohdsi_webapi_mcp-*.whl
```

### Publishing to PyPI

**Prerequisites:**
- PyPI account with access to the `ohdsi-webapi-mcp` package
- Poetry configured with PyPI credentials: `poetry config pypi-token.pypi <your-token>`

**Release Process:**

1. **Update version** in `pyproject.toml` and `src/ohdsi_webapi_mcp/__init__.py`
2. **Update CHANGELOG.md** with new features and fixes
3. **Run full test suite:**
   ```bash
   make test-all
   make check-all
   ```
4. **Build and publish:**
   ```bash
   # Build the package
   make build
   
   # Publish to PyPI
   make publish
   # or: poetry publish
   ```
5. **Create GitHub release** with the same version tag
6. **Update Docker images** (triggered automatically by GitHub Actions)

### Publishing to Test PyPI (Recommended for testing)

Before publishing to the main PyPI, test with Test PyPI:

```bash
# Configure test PyPI
poetry config repositories.test-pypi https://test.pypi.org/legacy/
poetry config pypi-token.test-pypi <your-test-token>

# Publish to test PyPI
poetry publish -r test-pypi

# Test installation from test PyPI
pip install -i https://test.pypi.org/simple/ ohdsi-webapi-mcp
```

### Automated Publishing (CI/CD)

The project uses GitHub Actions for automated publishing:

- **On push to main:** Builds and tests the package
- **On version tag:** Automatically publishes to PyPI and builds Docker images
- **On pull request:** Runs full test suite and checks

**To trigger a release:**

```bash
# Tag a new version (must match pyproject.toml version)
git tag v0.1.0
git push origin v0.1.0

# This automatically:
# 1. Runs all tests
# 2. Builds the package
# 3. Publishes to PyPI
# 4. Builds and pushes Docker images
# 5. Creates a GitHub release
```

### Verification After Publishing

After publishing, verify the package works correctly:

```bash
# Test installation from PyPI
pipx install ohdsi-webapi-mcp

# Test the command
ohdsi-webapi-mcp --help

# Test with MCP Inspector
WEBAPI_BASE_URL=https://atlas-demo.ohdsi.org/WebAPI mcp-inspector ohdsi-webapi-mcp
```

### Package Metadata Maintenance

Keep these files updated for PyPI:

- **`pyproject.toml`**: Version, description, keywords, classifiers
- **`README.md`**: Installation instructions, badges, examples
- **`CHANGELOG.md`**: Version history and changes
- **`LICENSE`**: License file for PyPI display

### Distribution Strategy

This MCP server uses multiple distribution channels:

1. **PyPI** (primary): `pip install ohdsi-webapi-mcp`
2. **pipx** (recommended): `pipx install ohdsi-webapi-mcp`
3. **Docker**: `docker run ghcr.io/clsweeting/ohdsi-webapi-mcp`
4. **GitHub**: `pip install git+https://github.com/clsweeting/ohdsi-webapi-mcp.git`

This ensures users can install the MCP server using their preferred method.


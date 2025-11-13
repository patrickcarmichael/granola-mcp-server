# Contributing to Granola MCP Server

Thank you for your interest in contributing to the Granola MCP Server! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [Development Setup](#development-setup)
4. [Making Changes](#making-changes)
5. [Testing](#testing)
6. [Code Style](#code-style)
7. [Submitting Changes](#submitting-changes)
8. [Review Process](#review-process)

---

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive environment for all contributors. Please be respectful and constructive in all interactions.

### Expected Behavior

- Use welcoming and inclusive language
- Be respectful of differing viewpoints and experiences
- Gracefully accept constructive criticism
- Focus on what is best for the community
- Show empathy towards other community members

---

## Getting Started

### Prerequisites

- Python 3.10 or higher
- Git
- pip or poetry for dependency management
- Familiarity with MCP (Model Context Protocol)
- Basic understanding of FastMCP framework

### Finding Work

1. **Check the Issues**: Browse the [issue tracker](../../issues) for:
   - `good first issue` - Great for newcomers
   - `help wanted` - Community contributions welcome
   - `bug` - Known issues that need fixing
   - `enhancement` - New features or improvements

2. **Propose New Ideas**: Open an issue to discuss new features before starting work

3. **Ask Questions**: Don't hesitate to ask for clarification in issue comments

---

## Development Setup

### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then clone your fork
git clone https://github.com/YOUR_USERNAME/granola-mcp-server.git
cd granola-mcp-server

# Add upstream remote
git remote add upstream https://github.com/ORIGINAL_OWNER/granola-mcp-server.git
```

### 2. Create Virtual Environment

```bash
# Using venv
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Using poetry (alternative)
poetry install
poetry shell
```

### 3. Install Dependencies

```bash
# Install all dependencies including dev tools
pip install -e ".[dev,mcp]"

# Install pre-commit hooks
pre-commit install
```

### 4. Verify Installation

```bash
# Run tests to ensure everything works
pytest tests/

# Check code quality
black --check src/
isort --check src/
ruff check src/
mypy src/
```

### 5. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your Granola API token (optional for testing)
export GRANOLA_API_TOKEN="your_token_here"
export GRANOLA_DOCUMENT_SOURCE=remote
```

---

## Making Changes

### Branching Strategy

We follow a simplified Git Flow:

1. **main** - Production-ready code
2. **feature/*** - New features
3. **fix/*** - Bug fixes
4. **docs/*** - Documentation updates
5. **refactor/*** - Code refactoring

### Creating a Branch

```bash
# Update your local main branch
git checkout main
git pull upstream main

# Create a feature branch
git checkout -b feature/your-feature-name

# Or for a bug fix
git checkout -b fix/issue-123-description
```

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**

```bash
# Good commit messages
git commit -m "feat(tools): add batch get meetings tool"
git commit -m "fix(api): handle 429 rate limit errors correctly"
git commit -m "docs(readme): update installation instructions"
git commit -m "test(parser): add edge case tests for date parsing"

# Detailed commit with body
git commit -m "feat(cache): implement in-memory LRU cache

Add an in-memory LRU cache layer with configurable TTL to reduce
API calls and improve response times. The cache sits between the
adapter and document source layers.

- Implements 5-minute default TTL
- Maximum 1000 entries
- Automatic eviction of oldest entries

Closes #123"
```

---

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_tools.py

# Run specific test function
pytest tests/test_tools.py::test_list_and_get_and_export

# Run with verbose output
pytest -v

# Run and stop on first failure
pytest -x
```

### Writing Tests

#### 1. Unit Tests

Test individual functions in isolation:

```python
# tests/unit/test_date_parser.py
import pytest
from granola_mcp_server.utils.date_parser import parse_iso8601

def test_parse_valid_iso8601():
    """Test parsing valid ISO 8601 dates."""
    result = parse_iso8601("2025-11-13T10:00:00Z")
    assert result.year == 2025
    assert result.month == 11
    assert result.day == 13

def test_parse_invalid_iso8601():
    """Test parsing invalid dates raises ValueError."""
    with pytest.raises(ValueError):
        parse_iso8601("not-a-date")

def test_parse_none_returns_none():
    """Test parsing None returns None."""
    assert parse_iso8601(None) is None
```

#### 2. Integration Tests

Test multiple components working together:

```python
# tests/integration/test_workflow.py
import pytest
from granola_mcp_server.config import load_config
from granola_mcp_server.sources import create_document_source
from granola_mcp_server.sources.adapter import DocumentSourceAdapter

@pytest.fixture
def adapter(tmp_path):
    """Create adapter with temporary cache."""
    config = load_config()
    config.cache_path = tmp_path / "cache.json"
    source = create_document_source(config)
    return DocumentSourceAdapter(source)

def test_list_search_get_workflow(adapter):
    """Test complete workflow: list → search → get."""
    # List meetings
    from granola_mcp_server.tools import list_meetings
    from granola_mcp_server.schemas import ListMeetingsInput

    result = list_meetings(config, adapter, ListMeetingsInput(limit=5))
    assert len(result.items) > 0

    # Search for first meeting
    first_meeting = result.items[0]
    # ... continue workflow
```

#### 3. Test Coverage Requirements

- **New Features**: Must include tests (100% coverage of new code)
- **Bug Fixes**: Must include regression test
- **Overall Target**: 80% coverage
- **Critical Paths**: 95% coverage (tools, API, parser)

### Test Fixtures

Use fixtures for reusable test data:

```python
# tests/conftest.py
import pytest

@pytest.fixture
def sample_meeting():
    """Sample meeting data for testing."""
    return {
        "id": "test-123",
        "title": "Test Meeting",
        "start_ts": "2025-11-13T10:00:00Z",
        "participants": ["Alice", "Bob"],
        "notes": "Test notes content"
    }

@pytest.fixture
def mock_config(tmp_path):
    """Mock configuration for testing."""
    from granola_mcp_server.config import GranolaConfig
    return GranolaConfig(
        cache_path=tmp_path / "cache.json",
        document_source="local"
    )
```

---

## Code Style

### Python Style Guide

We follow [PEP 8](https://pep8.org/) with these tools:

#### Black (Code Formatter)

```bash
# Format all code
black src/ tests/

# Check formatting without changes
black --check src/

# Format specific file
black src/granola_mcp_server/tools/meetings.py
```

**Configuration** (pyproject.toml):
```toml
[tool.black]
line-length = 88
target-version = ["py310", "py311", "py312"]
```

#### isort (Import Sorting)

```bash
# Sort imports
isort src/ tests/

# Check import sorting
isort --check src/
```

**Configuration** (pyproject.toml):
```toml
[tool.isort]
profile = "black"
line_length = 88
```

#### Ruff (Fast Linter)

```bash
# Lint code
ruff check src/

# Auto-fix issues
ruff check --fix src/

# Check specific rules
ruff check --select E,F,W src/
```

**Configuration** (pyproject.toml):
```toml
[tool.ruff]
line-length = 88
select = ["E", "F", "W", "C", "N", "D", "I"]
ignore = ["D100", "D104"]  # Allow missing docstrings in some cases
```

#### MyPy (Type Checking)

```bash
# Type check code
mypy src/

# Check specific file
mypy src/granola_mcp_server/tools/meetings.py
```

**Configuration** (pyproject.toml):
```toml
[tool.mypy]
python_version = "3.10"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
```

### Code Quality Guidelines

#### Type Hints

Always use type hints for function signatures:

```python
# Good
def list_meetings(
    config: GranolaConfig,
    adapter: DocumentSourceAdapter,
    params: ListMeetingsInput
) -> ListMeetingsOutput:
    """List meetings with filters."""
    pass

# Bad
def list_meetings(config, adapter, params):
    """List meetings with filters."""
    pass
```

#### Docstrings

Use Google-style docstrings:

```python
def parse_meeting(data: dict) -> MeetingDict:
    """Parse raw meeting data into normalized format.

    This function takes raw meeting data from the API or cache and
    converts it into a standardized MeetingDict format with validated
    fields and proper type conversions.

    Args:
        data: Raw meeting data dictionary containing at minimum:
            - id: Meeting identifier (required)
            - title: Meeting title (required)
            - start_ts: ISO 8601 timestamp (required)
            Additional optional fields include participants, notes, etc.

    Returns:
        Normalized MeetingDict with all fields validated and typed.
        Missing optional fields are set to None or empty lists.

    Raises:
        ValueError: If required fields (id, title, start_ts) are missing.
        KeyError: If data structure is invalid.

    Examples:
        >>> data = {
        ...     "id": "abc-123",
        ...     "title": "Team Sync",
        ...     "start_ts": "2025-11-13T10:00:00Z"
        ... }
        >>> meeting = parse_meeting(data)
        >>> print(meeting["title"])
        'Team Sync'

    See Also:
        - MeetingDict: TypedDict definition for meeting data
        - validate_meeting: Validation function for parsed meetings
    """
    # Implementation...
```

#### Error Handling

Use specific exceptions and provide context:

```python
# Good
from granola_mcp_server.errors import GranolaNotFoundError

def get_meeting_by_id(meeting_id: str) -> MeetingDict:
    meeting = find_meeting(meeting_id)
    if not meeting:
        raise GranolaNotFoundError("meeting", meeting_id)
    return meeting

# Bad
def get_meeting_by_id(meeting_id: str) -> MeetingDict:
    meeting = find_meeting(meeting_id)
    if not meeting:
        raise Exception("Not found")
    return meeting
```

#### Function Length

Keep functions focused and short:

- **Ideal**: 20-30 lines
- **Maximum**: 50 lines
- If longer, consider extracting helper functions

#### Naming Conventions

- **Functions/Variables**: `snake_case`
- **Classes**: `PascalCase`
- **Constants**: `UPPER_SNAKE_CASE`
- **Private**: `_leading_underscore`

---

## Submitting Changes

### Before Submitting

1. **Run All Checks**:
   ```bash
   # Format code
   black src/ tests/
   isort src/ tests/

   # Run linters
   ruff check src/
   mypy src/

   # Run tests
   pytest --cov=src
   ```

2. **Update Documentation**:
   - Update README.md if adding features
   - Update API_REFERENCE.md for new tools
   - Add docstrings to new functions

3. **Update CHANGELOG.md**:
   ```markdown
   ## [Unreleased]

   ### Added
   - New batch get meetings tool (#123)

   ### Fixed
   - Handle 429 rate limit errors correctly (#124)
   ```

### Creating a Pull Request

1. **Push Your Branch**:
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Open Pull Request**:
   - Go to GitHub and click "New Pull Request"
   - Select your branch
   - Fill in the PR template

3. **PR Title Format**:
   ```
   feat(tools): add batch get meetings tool
   fix(api): handle rate limit errors
   docs(readme): update installation steps
   ```

4. **PR Description Template**:
   ```markdown
   ## Description
   Brief description of changes

   ## Type of Change
   - [ ] Bug fix (non-breaking change fixing an issue)
   - [ ] New feature (non-breaking change adding functionality)
   - [ ] Breaking change (fix or feature causing existing functionality to change)
   - [ ] Documentation update

   ## Testing
   - [ ] All existing tests pass
   - [ ] New tests added for new functionality
   - [ ] Manual testing completed

   ## Checklist
   - [ ] Code follows project style guidelines
   - [ ] Self-review of code completed
   - [ ] Comments added for complex code
   - [ ] Documentation updated
   - [ ] No new warnings generated
   - [ ] Tests added that prove fix/feature works
   - [ ] CHANGELOG.md updated

   ## Related Issues
   Closes #123
   ```

---

## Review Process

### What to Expect

1. **Automated Checks**: CI/CD will run tests, linters, and type checks
2. **Code Review**: Maintainers will review your code
3. **Feedback**: You may receive requests for changes
4. **Iteration**: Make requested changes and push updates
5. **Approval**: Once approved, PR will be merged

### Review Criteria

Reviewers will check for:

- ✅ Code quality and style compliance
- ✅ Test coverage (80%+ for new code)
- ✅ Documentation completeness
- ✅ No breaking changes (unless discussed)
- ✅ Performance implications
- ✅ Security considerations

### Responding to Feedback

- Be open to constructive criticism
- Ask questions if feedback is unclear
- Make requested changes or explain why you disagree
- Update your branch and push changes
- Notify reviewers when ready for re-review

---

## Additional Guidelines

### Adding New MCP Tools

1. **Define Schema** (`src/granola_mcp_server/schemas.py`):
   ```python
   class NewToolInput(BaseModel):
       """Input for new tool."""
       param1: str
       param2: Optional[int] = None

   class NewToolOutput(BaseModel):
       """Output from new tool."""
       result: str
   ```

2. **Implement Tool** (`src/granola_mcp_server/tools/`):
   ```python
   def new_tool(
       config: GranolaConfig,
       adapter: DocumentSourceAdapter,
       params: NewToolInput
   ) -> NewToolOutput:
       """Implement the new tool."""
       # Implementation
       return NewToolOutput(result="...")
   ```

3. **Register Tool** (`src/granola_mcp_server/server.py`):
   ```python
   def _new_tool_wrapper(param1: str, param2: Optional[int] = None):
       params = NewToolInput(param1=param1, param2=param2)
       return new_tool(_config, _adapter, params)

   app.tool("granola.category.new_tool")(_new_tool_wrapper)
   ```

4. **Add Tests**:
   ```python
   def test_new_tool():
       """Test new tool functionality."""
       # Test implementation
   ```

5. **Update Documentation**:
   - Add to API_REFERENCE.md
   - Update README.md
   - Add usage examples

### Performance Considerations

- Profile code for bottlenecks (use `cProfile`)
- Avoid N+1 queries
- Use caching appropriately
- Consider memory usage for large datasets
- Add benchmarks for critical paths

### Security Guidelines

- Never commit API tokens or secrets
- Sanitize all user inputs
- Use parameterized queries (if adding SQL)
- Follow OWASP security guidelines
- Report security issues privately

---

## Getting Help

- **Questions**: Open a discussion on GitHub
- **Bugs**: Open an issue with reproduction steps
- **Features**: Open an issue to discuss before implementing
- **Chat**: Join our community chat (if available)

---

## License

By contributing, you agree that your contributions will be licensed under the same license as the project (MIT License).

---

## Thank You!

Thank you for contributing to the Granola MCP Server! Your contributions make this project better for everyone. 🎉

**Happy coding!** 🚀

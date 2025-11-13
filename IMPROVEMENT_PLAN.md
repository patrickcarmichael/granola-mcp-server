# Granola MCP Server - Comprehensive Improvement Plan

**Date**: 2025-11-13
**Version**: 0.1.0
**Status**: Production-Ready with Improvement Opportunities

---

## Executive Summary

The Granola MCP Server is **functionally complete and working**, with all 9 MCP tools operational. This document outlines strategic improvements across 6 key dimensions to elevate the project from "working" to "production-grade enterprise-ready."

### Current State
- ✅ All 9 MCP tools functional
- ✅ Remote API with pagination (286+ meetings)
- ✅ Token auto-refresh
- ✅ FastMCP 2.13.0 integration
- ✅ Basic documentation

### Target State
- 🎯 Enterprise-grade reliability
- 🎯 Comprehensive test coverage (80%+)
- 🎯 Production monitoring & observability
- 🎯 Advanced features & optimizations
- 🎯 Developer experience excellence

---

## Improvement Dimensions

### 1. Code Quality & Architecture (Priority: HIGH)
### 2. Testing & Quality Assurance (Priority: CRITICAL)
### 3. Documentation & Developer Experience (Priority: HIGH)
### 4. Performance & Optimization (Priority: MEDIUM)
### 5. Security & Reliability (Priority: CRITICAL)
### 6. Features & Capabilities (Priority: LOW-MEDIUM)

---

## 1. Code Quality & Architecture

### 1.1 Type Safety & Validation

**Current Issues:**
- Some functions lack complete type hints
- Optional error handling could be more robust
- Missing input validation in some tool functions

**Improvements:**

```python
# BEFORE
def list_meetings(config, adapter, params):
    meetings = adapter.get_meetings()
    # ...

# AFTER
def list_meetings(
    config: GranolaConfig,
    adapter: DocumentSourceAdapter,
    params: ListMeetingsInput
) -> ListMeetingsOutput:
    """List meetings with comprehensive validation.

    Args:
        config: Server configuration
        adapter: Document source adapter
        params: Validated input parameters

    Returns:
        Paginated meeting list with cursor

    Raises:
        GranolaParseError: If cache is invalid
        ValueError: If parameters are invalid
    """
    # Validate inputs
    if params.limit and not 1 <= params.limit <= 500:
        raise ValueError("limit must be between 1 and 500")

    meetings = adapter.get_meetings()
    # ...
```

**Action Items:**
- [ ] Add `mypy` strict mode to CI/CD
- [ ] Complete type hints across all modules
- [ ] Add comprehensive docstrings with examples
- [ ] Implement input validation decorators

### 1.2 Error Handling Enhancement

**Current State:**
- Basic error handling exists
- Some edge cases not covered
- Error messages could be more user-friendly

**Proposed Error Hierarchy:**

```python
# src/granola_mcp_server/errors.py

class GranolaError(Exception):
    """Base exception for all Granola errors."""
    pass

class GranolaConfigError(GranolaError):
    """Configuration-related errors."""
    pass

class GranolaAuthError(GranolaError):
    """Authentication/authorization errors."""
    pass

class GranolaAPIError(GranolaError):
    """Remote API errors."""
    def __init__(self, message: str, status_code: int = None, retry_after: int = None):
        super().__init__(message)
        self.status_code = status_code
        self.retry_after = retry_after

class GranolaCacheError(GranolaError):
    """Cache-related errors."""
    pass

class GranolaNotFoundError(GranolaError):
    """Resource not found errors."""
    def __init__(self, resource_type: str, resource_id: str):
        super().__init__(f"{resource_type} not found: {resource_id}")
        self.resource_type = resource_type
        self.resource_id = resource_id
```

**Action Items:**
- [ ] Implement comprehensive error hierarchy
- [ ] Add error context and suggestions
- [ ] Create error recovery strategies
- [ ] Add structured logging with error tracking

### 1.3 Code Organization

**Current State:**
- Good separation of concerns
- Some duplication between tool functions
- Could benefit from shared utilities

**Proposed Refactoring:**

```python
# src/granola_mcp_server/utils/pagination.py
class PaginationHelper:
    """Utility for consistent pagination across tools."""

    @staticmethod
    def paginate(
        items: List[T],
        limit: int,
        cursor: Optional[str] = None
    ) -> Tuple[List[T], Optional[str]]:
        """Apply pagination with cursor support."""
        # Shared pagination logic
        pass

# src/granola_mcp_server/utils/validation.py
def validate_meeting_id(meeting_id: str) -> str:
    """Validate and normalize meeting ID."""
    if not meeting_id or not isinstance(meeting_id, str):
        raise ValueError("Invalid meeting ID")
    return meeting_id.strip()

def validate_date_range(from_ts: str, to_ts: str) -> Tuple[datetime, datetime]:
    """Validate and parse date range."""
    pass
```

**Action Items:**
- [ ] Extract shared utilities
- [ ] Create pagination helper
- [ ] Implement validation utilities
- [ ] Add caching decorators

---

## 2. Testing & Quality Assurance

### 2.1 Test Coverage Analysis

**Current State:**
```
Tests: 4 tests total
Coverage: Unknown (no coverage reports)
```

**Target Coverage:**
- Overall: 80%+
- Critical paths: 95%+
- Tool functions: 100%

**Missing Test Areas:**

1. **Unit Tests Needed:**
   - [ ] Remote API error scenarios (401, 403, 429, 500)
   - [ ] Pagination edge cases (empty results, single page, many pages)
   - [ ] Token refresh failures
   - [ ] Cache expiration handling
   - [ ] Gzip decompression errors
   - [ ] Schema validation failures
   - [ ] Date parsing edge cases
   - [ ] Search query edge cases

2. **Integration Tests Needed:**
   - [ ] End-to-end MCP tool execution
   - [ ] Multi-page pagination flow
   - [ ] Cache refresh and invalidation
   - [ ] Token auto-refresh from supabase.json
   - [ ] Error propagation through layers

3. **Performance Tests Needed:**
   - [ ] Large dataset handling (1000+ meetings)
   - [ ] Concurrent request handling
   - [ ] Cache performance under load
   - [ ] Memory usage with large exports

### 2.2 Proposed Test Structure

```python
# tests/unit/test_remote_api.py
class TestRemoteAPIErrorHandling:
    def test_401_unauthorized(self, mock_api):
        """Test handling of expired tokens."""
        pass

    def test_429_rate_limit_retry(self, mock_api):
        """Test exponential backoff on rate limits."""
        pass

    def test_network_timeout_retry(self, mock_api):
        """Test retry logic on network timeouts."""
        pass

# tests/integration/test_mcp_tools.py
class TestMCPToolsIntegration:
    def test_list_search_get_export_flow(self):
        """Test complete workflow: list → search → get → export."""
        pass

    def test_pagination_exhaustion(self):
        """Test paginating through all meetings."""
        pass

# tests/performance/test_load.py
class TestPerformance:
    def test_large_meeting_list(self):
        """Test performance with 1000+ meetings."""
        pass

    def test_concurrent_requests(self):
        """Test concurrent tool invocations."""
        pass
```

**Action Items:**
- [ ] Set up pytest-cov for coverage reporting
- [ ] Add unit tests for all modules (target: 80% coverage)
- [ ] Create integration test suite
- [ ] Add performance benchmarks
- [ ] Set up CI/CD with automated testing
- [ ] Add mutation testing (mutmut)

### 2.3 Test Fixtures & Mocking

```python
# tests/fixtures/meetings.py
@pytest.fixture
def sample_meetings() -> List[MeetingDict]:
    """Generate realistic test meetings."""
    return [
        {
            "id": "test-001",
            "title": "Engineering All-Hands",
            "start_ts": "2025-11-13T10:00:00Z",
            "participants": ["Alice", "Bob", "Charlie"],
            # ...
        },
        # ... more test data
    ]

@pytest.fixture
def mock_remote_api(mocker):
    """Mock remote API with configurable responses."""
    api = mocker.Mock(spec=RemoteApiDocumentSource)
    # Configure mock behavior
    return api

@pytest.fixture
def temp_cache_dir(tmp_path):
    """Provide temporary cache directory for tests."""
    cache_dir = tmp_path / "cache"
    cache_dir.mkdir()
    return cache_dir
```

**Action Items:**
- [ ] Create comprehensive test fixtures
- [ ] Add mock data generators
- [ ] Implement API mocking utilities
- [ ] Create test data factories

---

## 3. Documentation & Developer Experience

### 3.1 Documentation Gaps

**Current Documentation:**
- ✅ README.md (basic)
- ✅ GRANOLA_MCP_COMPLETE_GUIDE.md (comprehensive)
- ✅ Private Gist (user guide)

**Missing Documentation:**
- ❌ ARCHITECTURE.md (copy from ~/dev)
- ❌ CONTRIBUTING.md
- ❌ API_REFERENCE.md (copy from ~/dev)
- ❌ TROUBLESHOOTING.md
- ❌ DEPLOYMENT.md
- ❌ CHANGELOG.md (copy from ~/dev)
- ❌ Code-level docstrings
- ❌ Type stub files (.pyi)

### 3.2 Proposed Documentation Structure

```
docs/
├── README.md                    # Documentation index
├── getting-started/
│   ├── installation.md         # Installation guide
│   ├── configuration.md        # Configuration options
│   └── quickstart.md          # Quick start tutorial
├── guides/
│   ├── mcp-integration.md     # MCP integration guide
│   ├── remote-api.md          # Remote API usage
│   ├── local-cache.md         # Local cache mode
│   └── cli-usage.md           # CLI tool usage
├── reference/
│   ├── api.md                 # Complete API reference
│   ├── tools.md               # MCP tools reference
│   ├── schemas.md             # Data schemas
│   └── errors.md              # Error codes & handling
├── development/
│   ├── contributing.md        # Contribution guidelines
│   ├── architecture.md        # Architecture docs
│   ├── testing.md             # Testing guide
│   └── release.md             # Release process
└── troubleshooting/
    ├── common-issues.md       # Common problems
    ├── debugging.md           # Debugging guide
    └── faq.md                 # Frequently asked questions
```

### 3.3 Code Documentation

**Add Comprehensive Docstrings:**

```python
def list_meetings(
    config: GranolaConfig,
    adapter: DocumentSourceAdapter,
    params: ListMeetingsInput
) -> ListMeetingsOutput:
    """List meetings with optional filtering and pagination.

    This function retrieves meetings from the configured document source
    (local cache or remote API) and applies filters specified in the
    parameters. Results are paginated using cursor-based pagination.

    Args:
        config: Server configuration containing cache settings and API details.
        adapter: Document source adapter for accessing meeting data.
        params: Input parameters for filtering and pagination:
            - q: Optional search query for filtering by title/content
            - from_ts: Optional ISO 8601 start date filter
            - to_ts: Optional ISO 8601 end date filter
            - participants: Optional list of participant names to filter by
            - limit: Maximum number of results (1-500, default 50)
            - cursor: Pagination cursor from previous response

    Returns:
        ListMeetingsOutput containing:
            - items: List of MeetingSummary objects
            - next_cursor: Cursor for next page, or None if last page

    Raises:
        GranolaParseError: If cache cannot be loaded or parsed.
        ValueError: If parameters are invalid (e.g., limit out of range).
        GranolaAPIError: If remote API request fails.

    Examples:
        >>> # List recent 10 meetings
        >>> result = list_meetings(config, adapter, ListMeetingsInput(limit=10))
        >>> print(f"Found {len(result.items)} meetings")

        >>> # Filter by date range
        >>> result = list_meetings(
        ...     config, adapter,
        ...     ListMeetingsInput(
        ...         from_ts="2025-11-01T00:00:00Z",
        ...         to_ts="2025-11-30T23:59:59Z",
        ...         limit=50
        ...     )
        ... )

        >>> # Paginate through results
        >>> cursor = None
        >>> while True:
        ...     result = list_meetings(config, adapter,
        ...         ListMeetingsInput(limit=50, cursor=cursor))
        ...     process_meetings(result.items)
        ...     if not result.next_cursor:
        ...         break
        ...     cursor = result.next_cursor

    See Also:
        - search_meetings: For full-text search across meetings
        - get_meeting: For retrieving full meeting details
        - ListMeetingsInput: Input schema documentation
        - MeetingSummary: Output schema documentation
    """
    # Implementation...
```

**Action Items:**
- [ ] Port ARCHITECTURE.md from ~/dev
- [ ] Port CHANGELOG.md from ~/dev
- [ ] Port docs/ directory from ~/dev
- [ ] Add comprehensive docstrings to all functions
- [ ] Create CONTRIBUTING.md
- [ ] Generate API documentation with Sphinx
- [ ] Add usage examples to README
- [ ] Create video tutorials

### 3.4 Developer Tooling

**Proposed Additions:**

```toml
# pyproject.toml additions

[project.optional-dependencies]
dev = [
  # Existing
  "pytest>=8.0.0",
  "pytest-cov>=5.0.0",
  "black>=24.0.0",
  "isort>=5.12.0",
  "mypy>=1.8.0",

  # New
  "ruff>=0.1.0",              # Fast linter
  "pre-commit>=3.5.0",        # Git hooks
  "pytest-asyncio>=0.21.0",   # Async testing
  "pytest-benchmark>=4.0.0",  # Performance testing
  "pytest-mock>=3.12.0",      # Mocking utilities
  "coverage[toml]>=7.3.0",    # Coverage reporting
  "sphinx>=7.2.0",            # Documentation generation
  "sphinx-rtd-theme>=2.0.0",  # Read the Docs theme
  "mutmut>=2.4.0",            # Mutation testing
]

[tool.ruff]
line-length = 88
target-version = "py310"
select = ["E", "F", "W", "C", "N", "D", "I"]

[tool.coverage.run]
source = ["src"]
omit = ["tests/*", "**/__pycache__/*"]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
]
```

**Pre-commit Configuration:**

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files

  - repo: https://github.com/psf/black
    rev: 24.1.0
    hooks:
      - id: black

  - repo: https://github.com/pycqa/isort
    rev: 5.13.0
    hooks:
      - id: isort

  - repo: https://github.com/charliermarsh/ruff-pre-commit
    rev: v0.1.9
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.8.0
    hooks:
      - id: mypy
        additional_dependencies: [pydantic>=2.7]
```

**Action Items:**
- [ ] Add ruff linter
- [ ] Configure pre-commit hooks
- [ ] Set up Sphinx documentation
- [ ] Add performance benchmarking
- [ ] Create development container (devcontainer.json)

---

## 4. Performance & Optimization

### 4.1 Caching Optimizations

**Current State:**
- Basic caching with 24-hour TTL
- No in-memory caching
- No cache warming

**Proposed Enhancements:**

```python
# src/granola_mcp_server/cache/memory_cache.py
from functools import lru_cache
from typing import Optional
import time

class MemoryCache:
    """In-memory LRU cache for frequently accessed data."""

    def __init__(self, ttl_seconds: int = 300, max_size: int = 1000):
        self.ttl = ttl_seconds
        self.max_size = max_size
        self._cache = {}
        self._timestamps = {}

    def get(self, key: str) -> Optional[Any]:
        """Get cached value if not expired."""
        if key in self._cache:
            if time.time() - self._timestamps[key] < self.ttl:
                return self._cache[key]
            # Expired, remove
            del self._cache[key]
            del self._timestamps[key]
        return None

    def set(self, key: str, value: Any) -> None:
        """Set cached value with TTL."""
        # Evict oldest if at capacity
        if len(self._cache) >= self.max_size:
            oldest_key = min(self._timestamps, key=self._timestamps.get)
            del self._cache[oldest_key]
            del self._timestamps[oldest_key]

        self._cache[key] = value
        self._timestamps[key] = time.time()

# Usage in adapter
class DocumentSourceAdapter:
    def __init__(self, source: DocumentSource):
        self._source = source
        self._memory_cache = MemoryCache(ttl_seconds=300)  # 5 min TTL

    def get_meeting_by_id(self, meeting_id: str) -> Optional[MeetingDict]:
        # Check memory cache first
        cached = self._memory_cache.get(f"meeting:{meeting_id}")
        if cached:
            return cached

        # Fetch from source
        meeting = self._fetch_meeting(meeting_id)
        if meeting:
            self._memory_cache.set(f"meeting:{meeting_id}", meeting)

        return meeting
```

**Action Items:**
- [ ] Implement in-memory LRU cache
- [ ] Add cache warming on startup
- [ ] Implement intelligent cache invalidation
- [ ] Add cache metrics and monitoring

### 4.2 API Request Optimization

**Batch Operations:**

```python
# src/granola_mcp_server/tools/batch.py
def batch_get_meetings(
    config: GranolaConfig,
    adapter: DocumentSourceAdapter,
    params: BatchGetMeetingsInput
) -> BatchGetMeetingsOutput:
    """Get multiple meetings in a single operation.

    More efficient than multiple get_meeting calls.
    """
    meeting_ids = params.ids

    # Batch fetch from source
    meetings = adapter.batch_get_meetings(meeting_ids)

    return BatchGetMeetingsOutput(meetings=meetings)
```

**Parallel Processing:**

```python
# src/granola_mcp_server/sources/remote_api.py
import asyncio
import aiohttp

class AsyncRemoteApiDocumentSource:
    """Async version for parallel requests."""

    async def get_all_documents_async(self) -> List[Dict]:
        """Fetch all pages in parallel."""
        # Determine total pages
        first_page = await self._fetch_page_async(offset=0)
        total_count = first_page.get("total", 0)
        batch_size = 100
        num_pages = (total_count + batch_size - 1) // batch_size

        # Fetch remaining pages in parallel
        tasks = [
            self._fetch_page_async(offset=i * batch_size)
            for i in range(1, num_pages)
        ]

        results = await asyncio.gather(*tasks)
        all_docs = first_page.get("docs", [])
        for result in results:
            all_docs.extend(result.get("docs", []))

        return all_docs
```

**Action Items:**
- [ ] Add in-memory caching layer
- [ ] Implement batch operations
- [ ] Add async/parallel API fetching
- [ ] Optimize JSON parsing

### 4.3 Query Optimization

**Indexing for Search:**

```python
# src/granola_mcp_server/search/index.py
from whoosh.index import create_in
from whoosh.fields import Schema, TEXT, ID, DATETIME

class MeetingSearchIndex:
    """Full-text search index for meetings."""

    def __init__(self, index_dir: Path):
        schema = Schema(
            id=ID(stored=True),
            title=TEXT(stored=True),
            notes=TEXT,
            summary=TEXT,
            participants=TEXT,
            start_ts=DATETIME(stored=True)
        )
        self.index = create_in(index_dir, schema)

    def index_meetings(self, meetings: List[MeetingDict]):
        """Index all meetings for fast search."""
        writer = self.index.writer()
        for meeting in meetings:
            writer.add_document(
                id=meeting["id"],
                title=meeting["title"],
                notes=meeting.get("notes", ""),
                summary=meeting.get("summary", ""),
                participants=" ".join(meeting.get("participants", [])),
                start_ts=parse_datetime(meeting["start_ts"])
            )
        writer.commit()

    def search(self, query: str, limit: int = 50) -> List[str]:
        """Fast full-text search returning meeting IDs."""
        with self.index.searcher() as searcher:
            results = searcher.search(query, limit=limit)
            return [hit["id"] for hit in results]
```

**Action Items:**
- [ ] Add full-text search indexing (Whoosh/Elasticsearch)
- [ ] Implement query caching
- [ ] Add search result ranking
- [ ] Optimize date filtering

---

## 5. Security & Reliability

### 5.1 Security Enhancements

**Token Security:**

```python
# src/granola_mcp_server/security/token_manager.py
import keyring
from cryptography.fernet import Fernet

class SecureTokenManager:
    """Secure token storage using system keyring."""

    def __init__(self, service_name: str = "granola-mcp-server"):
        self.service_name = service_name
        self._cipher = None

    def store_token(self, token: str) -> None:
        """Store token securely in system keyring."""
        # Encrypt token before storing
        encrypted = self._encrypt(token)
        keyring.set_password(self.service_name, "api_token", encrypted)

    def get_token(self) -> Optional[str]:
        """Retrieve and decrypt token from keyring."""
        encrypted = keyring.get_password(self.service_name, "api_token")
        if encrypted:
            return self._decrypt(encrypted)
        return None

    def _encrypt(self, data: str) -> str:
        """Encrypt sensitive data."""
        if not self._cipher:
            self._cipher = Fernet(Fernet.generate_key())
        return self._cipher.encrypt(data.encode()).decode()

    def _decrypt(self, data: str) -> str:
        """Decrypt sensitive data."""
        if not self._cipher:
            raise ValueError("Cipher not initialized")
        return self._cipher.decrypt(data.encode()).decode()
```

**Input Sanitization:**

```python
# src/granola_mcp_server/security/sanitization.py
import bleach
import re

def sanitize_search_query(query: str) -> str:
    """Sanitize search query to prevent injection attacks."""
    # Remove potentially dangerous characters
    query = re.sub(r'[^\w\s\-]', '', query)
    # Limit length
    query = query[:500]
    return query.strip()

def sanitize_meeting_id(meeting_id: str) -> str:
    """Validate and sanitize meeting ID."""
    # UUID format validation
    if not re.match(r'^[a-f0-9\-]{36}$', meeting_id):
        raise ValueError("Invalid meeting ID format")
    return meeting_id

def sanitize_markdown_export(content: str) -> str:
    """Sanitize markdown content for safe export."""
    # Allow only safe markdown tags
    allowed_tags = ['p', 'h1', 'h2', 'h3', 'ul', 'ol', 'li', 'code', 'pre']
    return bleach.clean(content, tags=allowed_tags, strip=True)
```

**Action Items:**
- [ ] Implement secure token storage (keyring)
- [ ] Add input sanitization for all user inputs
- [ ] Implement rate limiting for MCP tools
- [ ] Add audit logging for security events
- [ ] Set up security scanning (bandit, safety)

### 5.2 Reliability Improvements

**Circuit Breaker Pattern:**

```python
# src/granola_mcp_server/reliability/circuit_breaker.py
from enum import Enum
import time

class CircuitState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if recovered

class CircuitBreaker:
    """Circuit breaker for API calls."""

    def __init__(
        self,
        failure_threshold: int = 5,
        timeout: int = 60,
        expected_exception: type = Exception
    ):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.expected_exception = expected_exception

        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED

    def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection."""
        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time > self.timeout:
                self.state = CircuitState.HALF_OPEN
            else:
                raise Exception("Circuit breaker is OPEN")

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception as e:
            self._on_failure()
            raise

    def _on_success(self):
        """Handle successful call."""
        self.failure_count = 0
        self.state = CircuitState.CLOSED

    def _on_failure(self):
        """Handle failed call."""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
```

**Retry with Exponential Backoff:**

```python
# src/granola_mcp_server/reliability/retry.py
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type((ConnectionError, TimeoutError)),
    reraise=True
)
def fetch_with_retry(url: str, headers: dict) -> dict:
    """Fetch data with automatic retry."""
    # Implementation
    pass
```

**Health Checks:**

```python
# src/granola_mcp_server/health.py
from dataclasses import dataclass
from enum import Enum

class HealthStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"

@dataclass
class HealthCheck:
    status: HealthStatus
    cache_available: bool
    api_reachable: bool
    token_valid: bool
    last_check: str
    details: dict

def check_health(config: GranolaConfig, adapter: DocumentSourceAdapter) -> HealthCheck:
    """Comprehensive health check."""
    cache_ok = adapter.validate_cache_structure()

    # Test API connectivity
    api_ok = False
    token_ok = False
    try:
        # Simple API ping
        api_ok = test_api_connection(config)
        token_ok = True
    except GranolaAuthError:
        token_ok = False
    except Exception:
        api_ok = False

    # Determine overall status
    if cache_ok and api_ok and token_ok:
        status = HealthStatus.HEALTHY
    elif cache_ok or api_ok:
        status = HealthStatus.DEGRADED
    else:
        status = HealthStatus.UNHEALTHY

    return HealthCheck(
        status=status,
        cache_available=cache_ok,
        api_reachable=api_ok,
        token_valid=token_ok,
        last_check=datetime.now().isoformat(),
        details=adapter.get_cache_info()
    )
```

**Action Items:**
- [ ] Implement circuit breaker for API calls
- [ ] Add comprehensive retry logic
- [ ] Create health check endpoint
- [ ] Add graceful degradation
- [ ] Implement request timeout handling

---

## 6. Features & Capabilities

### 6.1 New MCP Tools

**Proposed Additional Tools:**

```python
# 1. Batch operations
@app.tool("granola.meetings.batch_get")
def batch_get_meetings(ids: List[str]) -> BatchGetOutput:
    """Get multiple meetings in one request."""
    pass

# 2. Meeting templates
@app.tool("granola.meetings.create_template")
def create_meeting_template(template: TemplateInput) -> TemplateOutput:
    """Create reusable meeting export templates."""
    pass

# 3. Advanced analytics
@app.tool("granola.analytics.trends")
def analyze_trends(params: TrendsInput) -> TrendsOutput:
    """Analyze meeting trends and patterns."""
    pass

# 4. Participant insights
@app.tool("granola.participants.stats")
def participant_stats(participant: str) -> ParticipantStatsOutput:
    """Get statistics for specific participant."""
    pass

# 5. Topic extraction
@app.tool("granola.meetings.topics")
def extract_topics(meeting_id: str) -> TopicsOutput:
    """Extract key topics from meeting notes."""
    pass

# 6. Smart summaries
@app.tool("granola.meetings.ai_summary")
def generate_ai_summary(meeting_id: str) -> AISummaryOutput:
    """Generate AI-powered meeting summary."""
    pass

# 7. Action items extraction
@app.tool("granola.meetings.action_items")
def extract_action_items(meeting_id: str) -> ActionItemsOutput:
    """Extract action items from meeting notes."""
    pass

# 8. Meeting comparison
@app.tool("granola.meetings.compare")
def compare_meetings(id1: str, id2: str) -> ComparisonOutput:
    """Compare two meetings."""
    pass
```

### 6.2 CLI Enhancements

**Interactive CLI Mode:**

```python
# granola-cli.py enhancements
import click
from rich.console import Console
from rich.table import Table

@click.group()
def cli():
    """Granola MCP Server CLI."""
    pass

@cli.command()
@click.option('--interactive', '-i', is_flag=True)
def search(interactive):
    """Interactive search mode."""
    if interactive:
        console = Console()
        console.print("[bold]Granola Interactive Search[/bold]")

        while True:
            query = console.input("\n[cyan]Search:[/cyan] ")
            if query.lower() in ['exit', 'quit']:
                break

            results = perform_search(query)
            display_results_table(results)

@cli.command()
def dashboard():
    """Launch interactive dashboard."""
    from textual.app import App
    # Rich terminal dashboard
    pass
```

**Action Items:**
- [ ] Add new MCP tools (batch, analytics, AI features)
- [ ] Implement interactive CLI mode
- [ ] Create rich terminal dashboard
- [ ] Add meeting templates
- [ ] Implement smart search with NLP

### 6.3 Advanced Features

**Webhook Support:**

```python
# src/granola_mcp_server/webhooks.py
class WebhookManager:
    """Manage webhooks for meeting events."""

    def register_webhook(self, url: str, events: List[str]) -> str:
        """Register webhook for specific events."""
        pass

    def trigger_webhook(self, event: str, data: dict):
        """Trigger registered webhooks."""
        pass

# Events:
# - meeting.created
# - meeting.updated
# - meeting.exported
# - cache.refreshed
```

**Plugin System:**

```python
# src/granola_mcp_server/plugins/base.py
class GranolaPlugin:
    """Base class for plugins."""

    def on_meeting_load(self, meeting: MeetingDict) -> MeetingDict:
        """Hook: Called when meeting is loaded."""
        return meeting

    def on_export(self, markdown: str) -> str:
        """Hook: Called before export."""
        return markdown

# Example plugin
class CustomFormatterPlugin(GranolaPlugin):
    def on_export(self, markdown: str) -> str:
        # Add custom formatting
        return markdown.replace("##", "###")
```

**Action Items:**
- [ ] Implement webhook system
- [ ] Create plugin architecture
- [ ] Add export templates
- [ ] Implement smart notifications

---

## Implementation Roadmap

### Phase 1: Foundation (Week 1-2)
**Priority: CRITICAL**

- [ ] Set up comprehensive testing (pytest-cov, fixtures)
- [ ] Achieve 60% test coverage
- [ ] Add type hints to all functions
- [ ] Configure pre-commit hooks
- [ ] Port documentation from ~/dev

**Deliverables:**
- Test coverage report
- Complete type annotations
- Development environment setup

### Phase 2: Quality & Reliability (Week 3-4)
**Priority: HIGH**

- [ ] Implement error handling hierarchy
- [ ] Add circuit breaker and retry logic
- [ ] Achieve 80% test coverage
- [ ] Add comprehensive docstrings
- [ ] Set up CI/CD pipeline

**Deliverables:**
- Robust error handling
- High test coverage
- Automated testing pipeline

### Phase 3: Performance & Security (Week 5-6)
**Priority: MEDIUM-HIGH**

- [ ] Implement in-memory caching
- [ ] Add security features (token encryption, sanitization)
- [ ] Optimize API requests (async, batching)
- [ ] Add health checks
- [ ] Implement monitoring

**Deliverables:**
- Performance improvements
- Security hardening
- Monitoring dashboard

### Phase 4: Features & Polish (Week 7-8)
**Priority: MEDIUM**

- [ ] Add new MCP tools (batch, analytics)
- [ ] Implement CLI enhancements
- [ ] Add plugin system
- [ ] Create webhook support
- [ ] Polish documentation

**Deliverables:**
- New features
- Enhanced CLI
- Complete documentation

### Phase 5: Production Readiness (Week 9-10)
**Priority: HIGH**

- [ ] Load testing and benchmarking
- [ ] Security audit
- [ ] Documentation review
- [ ] Release preparation
- [ ] Migration guides

**Deliverables:**
- Production-ready release
- Comprehensive documentation
- Deployment guides

---

## Success Metrics

### Code Quality
- [ ] Test coverage: 80%+
- [ ] Type coverage: 95%+
- [ ] Code complexity: <10 (cyclomatic)
- [ ] Documentation: 100% of public APIs

### Performance
- [ ] API response time: <100ms (p95)
- [ ] Cache hit rate: >90%
- [ ] Memory usage: <100MB under normal load
- [ ] Concurrent requests: 10+ without degradation

### Reliability
- [ ] Uptime: 99.9%
- [ ] Error rate: <0.1%
- [ ] Recovery time: <5 seconds
- [ ] Data consistency: 100%

### Developer Experience
- [ ] Setup time: <5 minutes
- [ ] Time to first successful tool call: <2 minutes
- [ ] Documentation completeness: 100%
- [ ] Issue resolution time: <24 hours

---

## Quick Wins (Can Implement Today)

1. **Port Documentation** (30 min)
   ```bash
   cp ~/dev/granola-mcp-server/ARCHITECTURE.md .
   cp ~/dev/granola-mcp-server/CHANGELOG.md .
   cp -r ~/dev/granola-mcp-server/docs .
   ```

2. **Add Pre-commit Hooks** (15 min)
   ```bash
   pip install pre-commit
   # Create .pre-commit-config.yaml
   pre-commit install
   ```

3. **Set Up Coverage** (10 min)
   ```bash
   pip install pytest-cov
   pytest --cov=src tests/
   ```

4. **Add Ruff Linter** (10 min)
   ```bash
   pip install ruff
   ruff check src/
   ```

5. **Create CONTRIBUTING.md** (20 min)
   - Guidelines for contributors
   - Development setup
   - Code standards

---

## Conclusion

The Granola MCP Server is **production-ready** with working functionality. This improvement plan provides a roadmap to transform it from "working" to "enterprise-grade" with:

- 🎯 80%+ test coverage
- 🔒 Enterprise security
- ⚡ Optimized performance
- 📚 Comprehensive documentation
- 🚀 Advanced features

**Next Steps:**
1. Review and prioritize improvements
2. Begin Phase 1 (Foundation)
3. Track progress with TodoWrite
4. Iterate based on feedback

**Generated**: 2025-11-13
**Status**: Ready for Implementation ✅

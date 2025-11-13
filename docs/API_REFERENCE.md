# Granola MCP Server - API Reference

Complete technical reference for the Granola MCP Server, including Remote API specifications, configuration options, and integration patterns.

---

## Table of Contents

1. [Granola Remote API](#granola-remote-api)
2. [Document Sources](#document-sources)
3. [MCP Tools](#mcp-tools)
4. [Configuration Reference](#configuration-reference)
5. [CLI Commands](#cli-commands)
6. [Python API](#python-api)

---

## Granola Remote API

### Base URL
```
https://api.granola.ai
```

### Authentication
All API requests require Bearer token authentication using WorkOS access tokens.

```http
Authorization: Bearer <access_token>
```

**Token Location**: Tokens are stored in:
```
~/Library/Application Support/Granola/supabase.json
```

**Token Format**: JSON structure containing WorkOS tokens:
```json
{
  "workos_tokens": "{\"access_token\":\"eyJ...\",\"refresh_token\":\"...\"}"
}
```

### Endpoints

#### POST /v2/get-documents

Fetches meeting documents with pagination support.

**Request Headers**:
```http
POST /v2/get-documents HTTP/1.1
Host: api.granola.ai
Authorization: Bearer <token>
Content-Type: application/json
Accept: */*
User-Agent: Granola/1.0.0
```

**Important**: The `User-Agent` header **must** be set to `Granola/1.0.0` or the API will return `{"message": "Unsupported client"}`.

**Request Body**:
```json
{
  "limit": 100,
  "offset": 0,
  "include_last_viewed_panel": true
}
```

**Parameters**:
- `limit` (integer, optional): Number of documents to return. Default: 100, Maximum: 100
- `offset` (integer, optional): Number of documents to skip for pagination. Default: 0
- `include_last_viewed_panel` (boolean, optional): Include last viewed panel data. Default: true

**Response**:
```json
{
  "docs": [
    {
      "id": "uuid",
      "title": "Meeting Title",
      "notes": "Full meeting notes...",
      "overview": "Brief overview...",
      "summary": "Meeting summary...",
      "start_ts": "2025-11-13T16:01:58.142Z",
      "end_ts": "2025-11-13T17:01:58.142Z",
      "participants": ["Speaker A", "Speaker B"],
      "platform": "zoom",
      "folder_id": "folder-uuid",
      "folder_name": "Project Alpha",
      "metadata": {...}
    }
  ],
  "total": 284
}
```

**Response Encoding**:
- Responses may be gzipped or plain JSON
- The server handles both formats automatically
- Content-Encoding header indicates compression

**Status Codes**:
- `200 OK`: Success
- `400 Bad Request`: Invalid parameters
- `401 Unauthorized`: Invalid or expired token
- `403 Forbidden`: Unsupported client (wrong User-Agent)
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error

**Rate Limits**:
- No documented rate limits
- Recommended: 10 requests per second maximum

**Pagination**:

To fetch all documents:
```python
all_docs = []
offset = 0
batch_size = 100

while True:
    response = fetch_documents(limit=batch_size, offset=offset)
    docs = response['docs']

    if not docs:
        break

    all_docs.extend(docs)

    if len(docs) < batch_size:
        break

    offset += batch_size
```

**Caching Strategy**:

The server implements local caching with TTL:
- Cache directory: `~/.granola/remote_cache/`
- Default TTL: 24 hours (86400 seconds)
- Cache key: SHA256 hash of request parameters
- Cache format: Decompressed JSON files

---

## Document Sources

### Remote API Source

Fetches documents directly from the Granola API with caching.

**Class**: `RemoteApiDocumentSource`

**Features**:
- Token-based authentication
- Automatic gzip decompression
- Local caching with TTL
- Retry logic with exponential backoff (3 attempts)
- Pagination support

**Configuration**:
```python
from granola_mcp_server.sources.remote_api import RemoteApiDocumentSource

source = RemoteApiDocumentSource(
    token="your_bearer_token",
    api_base="https://api.granola.ai",
    cache_dir="~/.granola/remote_cache",
    cache_ttl_seconds=86400  # 24 hours
)
```

**Methods**:

```python
# Fetch specific batch
docs = source.get_documents(
    limit=100,
    offset=0,
    include_last_viewed_panel=True,
    force=False  # Skip cache if True
)

# Fetch ALL documents (with pagination)
all_docs = source.get_all_documents(
    include_last_viewed_panel=True,
    force=False
)
```

**Cache Behavior**:
- Cache files named: `docs_<hash>.json`
- Hash based on: `limit:offset:include_last_viewed_panel`
- Cache checked before each API request
- Force refresh bypasses cache

### Local File Source

Reads from Granola's local cache file.

**Class**: `LocalFileDocumentSource`

**Features**:
- Reads from Granola app's local cache
- Double-JSON decoding support
- No network requirements
- Instant access (no API calls)

**Configuration**:
```python
from granola_mcp_server.sources.local_file import LocalFileDocumentSource

source = LocalFileDocumentSource(
    cache_path="~/Library/Application Support/Granola/cache-v3.json"
)
```

**Methods**:
```python
docs = source.get_documents(force=False)
```

**Limitations**:
- Only contains meetings synced by Granola app
- No pagination support (returns all cached meetings)
- Requires Granola app to be installed and logged in
- Cache may be stale if app hasn't synced recently

**File Format**:
```json
{
  "conversations": [
    {
      "doc": "{\"id\":\"...\",\"title\":\"...\",\"notes\":\"...\"}"
    }
  ]
}
```

Note: The `doc` field contains a JSON string that must be parsed twice.

---

## MCP Tools

The server exposes 9 MCP tools through the Model Context Protocol.

### Tool: granola.meetings.list

List meetings with optional filtering and pagination.

**Input Schema**:
```typescript
{
  limit?: number;           // Max results (default: 50)
  offset?: number;          // Pagination offset (default: 0)
  q?: string;              // Search query (optional)
  from_ts?: string;        // ISO 8601 start date (optional)
  to_ts?: string;          // ISO 8601 end date (optional)
  participants?: string[]; // Filter by participants (optional)
}
```

**Output Schema**:
```typescript
{
  items: MeetingSummary[];  // Array of meeting summaries
  total: number;            // Total count
  next_cursor?: number;     // Next pagination offset
}
```

**MeetingSummary**:
```typescript
{
  id: string;
  title: string;
  start_ts: string;
  end_ts?: string;
  participants: string[];
  platform?: "zoom" | "meet" | "teams" | "other";
  metadata?: object;
}
```

### Tool: granola.meetings.get

Get full meeting details by ID.

**Input Schema**:
```typescript
{
  id: string;              // Meeting ID (required)
  include?: string[];      // ["notes", "metadata"] (optional)
}
```

**Output Schema**:
```typescript
{
  meeting: Meeting;        // Full meeting object
}
```

**Meeting** (extends MeetingSummary):
```typescript
{
  // All MeetingSummary fields, plus:
  notes?: string;
  overview?: string;
  summary?: string;
  folder_id?: string;
  folder_name?: string;
}
```

### Tool: granola.meetings.search

Full-text search across meeting content.

**Input Schema**:
```typescript
{
  q: string;               // Search query (required)
  limit?: number;          // Max results (default: 20)
  offset?: number;         // Pagination offset (default: 0)
  filters?: {
    after?: string;        // ISO 8601 date
    before?: string;       // ISO 8601 date
    participants?: string[];
    platform?: string;
  };
}
```

**Output Schema**:
```typescript
{
  results: MeetingSummary[];
  total: number;
  next_cursor?: number;
}
```

### Tool: granola.meetings.export_markdown

Export meeting to markdown format.

**Input Schema**:
```typescript
{
  id: string;                    // Meeting ID (required)
  sections?: string[];           // ["header", "notes", "attendees", "links"]
}
```

**Output Schema**:
```typescript
{
  markdown: string;              // Formatted markdown content
  metadata: {
    title: string;
    date: string;
    participants: string[];
  };
}
```

### Tool: granola.meetings.stats

Get meeting statistics and analytics.

**Input Schema**:
```typescript
{
  window?: "7d" | "30d" | "90d";  // Time window (default: "30d")
  group_by?: "day" | "week";      // Aggregation (default: "day")
}
```

**Output Schema**:
```typescript
{
  total_meetings: number;
  by_period: {
    [date: string]: number;    // e.g., "2025-11-13": 5
  };
  by_platform?: {
    [platform: string]: number;
  };
  by_participant?: {
    [participant: string]: number;
  };
}
```

### Tool: granola.cache.status

Check cache health and status.

**Input Schema**: None

**Output Schema**:
```typescript
{
  source: "remote_api" | "local";
  cache_path: string;
  cache_size_bytes: number;
  cache_files_count?: number;    // Remote API only
  meeting_count: number;
  last_refresh?: string;         // ISO 8601 timestamp
  ttl_seconds?: number;          // Remote API only
}
```

### Tool: granola.cache.refresh

Force refresh cached data.

**Input Schema**:
```typescript
{
  force?: boolean;               // Bypass TTL (default: false)
}
```

**Output Schema**:
```typescript
{
  refreshed: boolean;
  meetings_fetched: number;
  cache_updated: boolean;
  timestamp: string;             // ISO 8601
}
```

### Tool Aliases

For backward compatibility, the following aliases exist:

- `granola.conversations.list` → `granola.meetings.list`
- `granola.conversations.get` → `granola.meetings.get`

---

## Configuration Reference

### Environment Variables

All configuration is done via environment variables prefixed with `GRANOLA_`.

#### Document Source Configuration

```bash
# Document source type (required)
GRANOLA_DOCUMENT_SOURCE=remote|local

# Remote API configuration
GRANOLA_API_TOKEN=<bearer_token>
GRANOLA_API_BASE=https://api.granola.ai

# Local file configuration
GRANOLA_CACHE_PATH=~/Library/Application Support/Granola/cache-v3.json
```

#### Cache Configuration

```bash
# Cache directory for remote API (default: ~/.granola/remote_cache)
GRANOLA_CACHE_DIR=~/.granola/remote_cache

# Cache TTL in seconds (default: 86400 = 24 hours)
GRANOLA_CACHE_TTL_SECONDS=86400

# Enable/disable caching (default: true)
GRANOLA_CACHE_ENABLED=true
```

#### Advanced Options

```bash
# Network timeout (default: 15 seconds)
GRANOLA_TIMEOUT_SECONDS=15

# Max retry attempts (default: 3)
GRANOLA_MAX_RETRIES=3

# Force stdlib-only mode (default: true)
GRANOLA_STDLIB_ONLY=true

# Enable SQLite indexing (default: false, requires STDLIB_ONLY=false)
GRANOLA_USE_SQLITE=false
GRANOLA_DB_PATH=~/.granola/granola.db
```

### .env File

Create a `.env` file in the project root:

```bash
# Remote API mode (recommended)
GRANOLA_DOCUMENT_SOURCE=remote
GRANOLA_API_TOKEN=your_token_here
GRANOLA_CACHE_TTL_SECONDS=86400

# OR: Local mode (fallback)
# GRANOLA_DOCUMENT_SOURCE=local
# GRANOLA_CACHE_PATH=~/Library/Application Support/Granola/cache-v3.json
```

### Configuration Priority

1. Environment variables (highest)
2. `.env` file
3. Default values (lowest)

### Auto Token Loading

The wrapper scripts (`granola`, `granola-mcp-remote`) automatically load fresh tokens:

```bash
# Token extracted from:
~/Library/Application Support/Granola/supabase.json

# Parsed structure:
workos_tokens → JSON parse → access_token
```

---

## CLI Commands

The CLI tool provides direct access to Granola meetings without MCP.

### Installation

```bash
cd ~/dev/granola-mcp-server
chmod +x granola granola-cli.py
```

### Commands

#### list

List meetings with optional search and pagination.

```bash
./granola list [--limit N] [--search QUERY]

# Examples:
./granola list                      # List 50 meetings
./granola list --limit 10           # List 10 meetings
./granola list --search "product"   # Search for "product"
```

**Output**:
```
Found 3 meetings
================================================================================

ID: 1468da54-6156-42eb-8ae9-876ce3b1693a
Title: 1st GCS All-Hands Meeting
Date: 2025-11-13T16:01:58.142Z
Participants: Patrick
--------------------------------------------------------------------------------
```

#### search

Full-text search across meeting content.

```bash
./granola search <query> [--limit N]

# Examples:
./granola search "product roadmap"
./granola search "Q4" --limit 5
```

#### get

Get full meeting details by ID.

```bash
./granola get <meeting_id>

# Example:
./granola get 1468da54-6156-42eb-8ae9-876ce3b1693a
```

**Output**:
```json
{
  "id": "1468da54-6156-42eb-8ae9-876ce3b1693a",
  "title": "1st GCS All-Hands Meeting",
  "notes": "Full meeting notes...",
  "start_ts": "2025-11-13T16:01:58.142Z",
  "participants": ["Patrick"]
}
```

#### export

Export meeting to markdown format.

```bash
./granola export <meeting_id> [--output FILE]

# Examples:
./granola export 1468da54...
./granola export 1468da54... --output notes.md
```

#### stats

Display meeting statistics.

```bash
./granola stats [--window 7d|30d|90d]

# Examples:
./granola stats              # Last 30 days
./granola stats --window 7d  # Last 7 days
```

**Output**:
```
Meeting Statistics (last 30d)
================================================================================

by_period:
  2025-11-13: 2 meetings
  2025-11-12: 5 meetings
  2025-11-11: 2 meetings
  ...
```

#### cache

Manage cache status and refresh.

```bash
./granola cache status   # Check cache status
./granola cache refresh  # Force refresh cache

# Examples:
./granola cache status
```

**Output**:
```
Cache Status
================================================================================
Path: /Users/user/.granola/remote_cache
Profile: stdlib
Size: 10027635 bytes
Last loaded: 2025-11-13T17:10:26.948910+00:00
```

---

## Python API

### Basic Usage

```python
from granola_mcp_server.config import load_config
from granola_mcp_server.sources import create_document_source
from granola_mcp_server.sources.adapter import DocumentSourceAdapter

# Load configuration
config = load_config()

# Create document source
source = create_document_source(config)

# Wrap in adapter
adapter = DocumentSourceAdapter(source)

# Fetch documents
docs = adapter.get_documents(force=False)
```

### Using Remote API Directly

```python
from granola_mcp_server.sources.remote_api import RemoteApiDocumentSource

# Initialize source
source = RemoteApiDocumentSource(
    token="your_bearer_token",
    api_base="https://api.granola.ai",
    cache_ttl_seconds=86400
)

# Fetch specific batch
batch = source.get_documents(limit=50, offset=0)

# Fetch ALL documents with pagination
all_docs = source.get_all_documents()

print(f"Fetched {len(all_docs)} total documents")
```

### Using Local Cache

```python
from granola_mcp_server.sources.local_file import LocalFileDocumentSource

source = LocalFileDocumentSource(
    cache_path="~/Library/Application Support/Granola/cache-v3.json"
)

docs = source.get_documents()
```

### Using MCP Tools

```python
from granola_mcp_server.tools import list_meetings, search_meetings
from granola_mcp_server.schemas import ListMeetingsInput, SearchMeetingsInput

# List meetings
params = ListMeetingsInput(limit=10, q="product")
result = list_meetings(config, adapter, params)

for meeting in result.items:
    print(f"{meeting.title} - {meeting.start_ts}")

# Search meetings
search_params = SearchMeetingsInput(q="roadmap", limit=5)
search_result = search_meetings(config, adapter, search_params)
```

### Custom Document Processing

```python
# Fetch and process all documents
all_docs = source.get_all_documents()

# Filter by date
from datetime import datetime, timedelta
cutoff = datetime.now() - timedelta(days=7)

recent_docs = [
    doc for doc in all_docs
    if datetime.fromisoformat(doc['start_ts'].replace('Z', '+00:00')) > cutoff
]

# Group by participant
from collections import defaultdict
by_participant = defaultdict(list)

for doc in all_docs:
    for participant in doc.get('participants', []):
        by_participant[participant].append(doc)

print(f"Meetings with Patrick: {len(by_participant['Patrick'])}")
```

### Error Handling

```python
from granola_mcp_server.errors import GranolaParseError

try:
    source = RemoteApiDocumentSource(token="invalid_token")
    docs = source.get_documents()
except GranolaParseError as e:
    print(f"API error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

---

## Appendix

### Common Issues

#### "Unsupported client" Error

**Cause**: Incorrect User-Agent header

**Solution**: Ensure User-Agent is set to `Granola/1.0.0`

```python
headers = {
    "User-Agent": "Granola/1.0.0"  # Required!
}
```

#### Token Expired

**Cause**: WorkOS access tokens expire

**Solution**: Use wrapper scripts that auto-load fresh tokens from `supabase.json`

```bash
# Use wrapper instead of direct CLI
./granola list  # Auto-loads fresh token
```

#### Cache Stale

**Cause**: Cache TTL exceeded

**Solution**: Force refresh or reduce TTL

```bash
./granola cache refresh
```

Or:
```bash
export GRANOLA_CACHE_TTL_SECONDS=3600  # 1 hour
```

### Performance Tips

1. **Use pagination for large datasets**
   - Fetch in batches of 100
   - Process incrementally

2. **Enable caching**
   - Reduces API calls
   - Improves response times

3. **Optimize cache TTL**
   - Longer TTL = fewer API calls
   - Shorter TTL = fresher data

4. **Use local cache for offline work**
   - No network dependency
   - Instant access

### Migration Guide

#### From Local to Remote

```bash
# Old configuration
export GRANOLA_DOCUMENT_SOURCE=local
export GRANOLA_CACHE_PATH=~/Library/Application Support/Granola/cache-v3.json

# New configuration
export GRANOLA_DOCUMENT_SOURCE=remote
export GRANOLA_API_TOKEN=<your_token>
export GRANOLA_CACHE_TTL_SECONDS=86400
```

#### From Manual Token to Auto-Loading

1. Remove `GRANOLA_API_TOKEN` from `.env`
2. Use wrapper scripts: `./granola` instead of `./granola-cli.py`
3. Ensure `supabase.json` exists with valid tokens

---

**Last Updated**: 2025-11-13
**Version**: 0.1.0
**Author**: Enhanced by Claude Code

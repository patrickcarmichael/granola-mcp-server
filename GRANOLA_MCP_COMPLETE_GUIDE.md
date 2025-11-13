# Granola MCP Server - Complete Usage Guide

A comprehensive guide to using the Granola MCP (Model Context Protocol) Server for accessing and managing your Granola meeting notes through Claude Code and other MCP clients.

## Table of Contents

1. [Overview](#overview)
2. [Installation & Setup](#installation--setup)
3. [Available Tools](#available-tools)
4. [Tool Reference](#tool-reference)
5. [Usage Examples](#usage-examples)
6. [Advanced Patterns](#advanced-patterns)
7. [Troubleshooting](#troubleshooting)
8. [API Reference](#api-reference)

---

## Overview

The Granola MCP Server provides **9 tools** to interact with your Granola meetings:

- **Cache Management**: Status and refresh operations
- **Meeting Listing**: List and paginate through meetings
- **Meeting Search**: Full-text search across meetings
- **Meeting Details**: Get detailed information about specific meetings
- **Export**: Export meetings as Markdown
- **Analytics**: Get meeting statistics and trends

### Key Features

- ✅ **286+ meetings** accessible through the API
- ✅ **Remote API mode** with automatic caching
- ✅ **Pagination support** for large datasets
- ✅ **Full-text search** across meeting titles and content
- ✅ **Flexible exports** with customizable sections
- ✅ **Statistics** by day/week with configurable windows

---

## Installation & Setup

### Prerequisites

```bash
# Install the Granola MCP Server
pip install granola-mcp-server[mcp]

# Or install from source
git clone <repository>
cd granola-mcp-server
pip install -e ".[mcp]"
```

### Configuration

The server supports two modes:

#### 1. Remote API Mode (Recommended)

Set environment variables:

```bash
export GRANOLA_DOCUMENT_SOURCE=remote
export GRANOLA_API_TOKEN="your_access_token"
```

Create a wrapper script (`granola-mcp-remote`):

```bash
#!/usr/bin/env bash
# Load token from Granola's supabase.json
SUPABASE_JSON="$HOME/Library/Application Support/Granola/supabase.json"
if [ -f "$SUPABASE_JSON" ]; then
    export GRANOLA_API_TOKEN=$(python3 -c "import json; s=json.load(open('$SUPABASE_JSON')); print(json.loads(s['workos_tokens'])['access_token'])" 2>/dev/null)
fi

export GRANOLA_DOCUMENT_SOURCE=remote
exec granola-mcp "$@"
```

#### 2. Local Cache Mode

```bash
export GRANOLA_DOCUMENT_SOURCE=local
export GRANOLA_CACHE_PATH="$HOME/Library/Application Support/Granola/cache-v3.json"
```

### Add to Claude Code

```bash
claude mcp add --transport stdio granola -- /path/to/granola-mcp-remote
```

Or configure in `.claude/mcp.json`:

```json
{
  "mcpServers": {
    "granola": {
      "command": "/path/to/granola-mcp-remote",
      "args": [],
      "env": {}
    }
  }
}
```

---

## Available Tools

| Tool Name | Purpose | Parameters |
|-----------|---------|------------|
| `granola.cache.status` | Get cache information | None |
| `granola.cache.refresh` | Force cache refresh | None |
| `granola.meetings.list` | List meetings with filters | `q`, `from_ts`, `to_ts`, `participants`, `limit`, `cursor` |
| `granola.conversations.list` | Alias for meetings.list | Same as above |
| `granola.meetings.get` | Get meeting details | `id`, `include` |
| `granola.conversations.get` | Alias for meetings.get | Same as above |
| `granola.meetings.search` | Search meetings | `q`, `filters`, `limit`, `cursor` |
| `granola.meetings.export_markdown` | Export as Markdown | `id`, `sections` |
| `granola.meetings.stats` | Get meeting statistics | `window`, `group_by` |

---

## Tool Reference

### 1. Cache Status

**Tool**: `granola.cache.status`

Get information about the current cache state.

**Parameters**: None

**Returns**:
```json
{
  "path": "/Users/you/.granola/remote_cache",
  "size_bytes": 10027635,
  "last_loaded_ts": "2025-11-13T17:10:26.948910+00:00",
  "profile": "stdlib"
}
```

**Example**:
```python
from mcp import use_mcp_tool

result = use_mcp_tool("granola.cache.status")
print(f"Cache size: {result.size_bytes / 1024 / 1024:.2f} MB")
```

---

### 2. Cache Refresh

**Tool**: `granola.cache.refresh`

Force a refresh of the cache from the remote API.

**Parameters**: None

**Returns**:
```json
{
  "success": true,
  "message": "Cache refreshed successfully",
  "meeting_count": 286,
  "cache_info": {
    "source": "remote_api",
    "api_base": "https://api.granola.ai",
    "cache_dir": "/Users/you/.granola/remote_cache",
    "cache_files_count": 3,
    "total_cache_size_bytes": 6469741
  }
}
```

---

### 3. List Meetings

**Tool**: `granola.meetings.list` or `granola.conversations.list`

List meetings with optional filtering and pagination.

**Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `q` | string | No | Search query for filtering |
| `from_ts` | string | No | ISO 8601 start date (e.g., "2025-11-01T00:00:00Z") |
| `to_ts` | string | No | ISO 8601 end date |
| `participants` | array | No | Filter by participant names |
| `limit` | integer | No | Max results (1-500, default 50) |
| `cursor` | string | No | Pagination cursor from previous response |

**Returns**:
```json
{
  "items": [
    {
      "id": "1468da54-6156-42eb-8ae9-876ce3b1693a",
      "title": "1st GCS All-Hands Meeting",
      "start_ts": "2025-11-13T16:01:58.142Z",
      "end_ts": null,
      "participants": ["Patrick"],
      "platform": null,
      "metadata": null
    }
  ],
  "next_cursor": "5"
}
```

**Examples**:

```python
# Get recent 10 meetings
result = use_mcp_tool("granola.meetings.list", limit=10)

# Get meetings from last week
from datetime import datetime, timedelta
week_ago = (datetime.now() - timedelta(days=7)).isoformat() + "Z"
result = use_mcp_tool("granola.meetings.list", from_ts=week_ago, limit=20)

# Pagination
page1 = use_mcp_tool("granola.meetings.list", limit=10)
if page1.next_cursor:
    page2 = use_mcp_tool("granola.meetings.list", limit=10, cursor=page1.next_cursor)

# Filter by participant
result = use_mcp_tool("granola.meetings.list",
    participants=["Patrick", "Jane"],
    limit=20
)
```

---

### 4. Search Meetings

**Tool**: `granola.meetings.search`

Full-text search across meeting titles and content.

**Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `q` | string | **Yes** | Search query |
| `filters` | object | No | Additional filters (participants, platform, before, after) |
| `limit` | integer | No | Max results (1-500, default 50) |
| `cursor` | string | No | Pagination cursor |

**Filter Object**:
```json
{
  "participants": ["Name1", "Name2"],
  "platform": "zoom",
  "before": "2025-11-01T00:00:00Z",
  "after": "2025-10-01T00:00:00Z"
}
```

**Examples**:

```python
# Simple search
result = use_mcp_tool("granola.meetings.search", q="FreeWheel", limit=10)

# Search with filters
result = use_mcp_tool("granola.meetings.search",
    q="weekly sync",
    filters={
        "participants": ["Patrick"],
        "after": "2025-11-01T00:00:00Z"
    },
    limit=20
)
```

---

### 5. Get Meeting Details

**Tool**: `granola.meetings.get` or `granola.conversations.get`

Get detailed information about a specific meeting.

**Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string | **Yes** | Meeting ID |
| `include` | array | No | Additional fields: `["notes", "metadata"]` |

**Returns**:
```json
{
  "meeting": {
    "id": "1468da54-6156-42eb-8ae9-876ce3b1693a",
    "title": "1st GCS All-Hands Meeting",
    "start_ts": "2025-11-13T16:01:58.142Z",
    "participants": ["Patrick"],
    "notes": "Full meeting notes content...",
    "overview": "Brief overview of the meeting",
    "summary": "AI-generated summary",
    "folder_id": null,
    "folder_name": null
  }
}
```

**Examples**:

```python
# Basic meeting info
result = use_mcp_tool("granola.meetings.get",
    id="1468da54-6156-42eb-8ae9-876ce3b1693a"
)

# Include notes and metadata
result = use_mcp_tool("granola.meetings.get",
    id="1468da54-6156-42eb-8ae9-876ce3b1693a",
    include=["notes", "metadata"]
)

# Access meeting data
meeting = result.meeting
print(f"Title: {meeting.title}")
print(f"Notes: {meeting.notes[:200]}...")
```

---

### 6. Export Meeting as Markdown

**Tool**: `granola.meetings.export_markdown`

Export a meeting in Markdown format with customizable sections.

**Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string | **Yes** | Meeting ID |
| `sections` | array | No | Sections to include: `["header", "notes", "attendees", "links"]` |

**Returns**:
```json
{
  "markdown": "# Meeting Title\n\n- ID: `abc123`\n- When: 2025-11-13\n\n## Attendees\n- Patrick\n\n## Notes\n..."
}
```

**Examples**:

```python
# Export full meeting
result = use_mcp_tool("granola.meetings.export_markdown",
    id="1468da54-6156-42eb-8ae9-876ce3b1693a"
)

with open("meeting.md", "w") as f:
    f.write(result.markdown)

# Export only notes section
result = use_mcp_tool("granola.meetings.export_markdown",
    id="1468da54-6156-42eb-8ae9-876ce3b1693a",
    sections=["notes"]
)

# Export header and attendees only
result = use_mcp_tool("granola.meetings.export_markdown",
    id="1468da54-6156-42eb-8ae9-876ce3b1693a",
    sections=["header", "attendees"]
)
```

---

### 7. Meeting Statistics

**Tool**: `granola.meetings.stats`

Get aggregated meeting statistics over time windows.

**Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `window` | string | No | Time window: `"7d"`, `"30d"`, `"90d"` |
| `group_by` | string | No | Grouping: `"day"` or `"week"` |

**Returns**:
```json
{
  "counts": {
    "by_period": [
      {"period": "2025-11-13", "meetings": 2},
      {"period": "2025-11-12", "meetings": 5}
    ]
  },
  "participants": null
}
```

**Examples**:

```python
# Last 7 days by day
result = use_mcp_tool("granola.meetings.stats",
    window="7d",
    group_by="day"
)

for period in result.counts["by_period"]:
    print(f"{period.period}: {period.meetings} meetings")

# Last 30 days by week
result = use_mcp_tool("granola.meetings.stats",
    window="30d",
    group_by="week"
)

# Last 90 days by week (for trends)
result = use_mcp_tool("granola.meetings.stats",
    window="90d",
    group_by="week"
)
```

---

## Usage Examples

### Example 1: Find and Export Recent Team Meetings

```python
# Search for team meetings in the last 30 days
from datetime import datetime, timedelta

thirty_days_ago = (datetime.now() - timedelta(days=30)).isoformat() + "Z"

# Search
results = use_mcp_tool("granola.meetings.search",
    q="team meeting",
    filters={"after": thirty_days_ago},
    limit=10
)

# Export each meeting
for meeting in results.items:
    export = use_mcp_tool("granola.meetings.export_markdown",
        id=meeting.id,
        sections=["header", "notes", "attendees"]
    )

    filename = f"{meeting.id[:8]}_{meeting.title.replace(' ', '_')}.md"
    with open(filename, "w") as f:
        f.write(export.markdown)

    print(f"Exported: {filename}")
```

### Example 2: Generate Weekly Meeting Report

```python
# Get last week's statistics
stats = use_mcp_tool("granola.meetings.stats",
    window="7d",
    group_by="day"
)

# Get all meetings from last week
seven_days_ago = (datetime.now() - timedelta(days=7)).isoformat() + "Z"
meetings = use_mcp_tool("granola.meetings.list",
    from_ts=seven_days_ago,
    limit=100
)

# Generate report
report = f"# Weekly Meeting Report\n\n"
report += f"Total Meetings: {len(meetings.items)}\n\n"

report += "## Daily Breakdown\n\n"
for period in stats.counts["by_period"]:
    report += f"- {period.period}: {period.meetings} meetings\n"

report += "\n## Meeting List\n\n"
for meeting in meetings.items:
    report += f"- **{meeting.title}** ({meeting.start_ts})\n"
    report += f"  - Participants: {', '.join(meeting.participants)}\n"

print(report)
```

### Example 3: Find Meetings with Specific Participant

```python
# List all meetings with a specific participant
meetings = use_mcp_tool("granola.meetings.list",
    participants=["Patrick"],
    limit=50
)

print(f"Found {len(meetings.items)} meetings with Patrick")

# Get detailed info for each
for summary in meetings.items[:5]:  # First 5
    details = use_mcp_tool("granola.meetings.get",
        id=summary.id,
        include=["notes"]
    )

    print(f"\n{details.meeting.title}")
    print(f"Date: {details.meeting.start_ts}")
    if details.meeting.notes:
        print(f"Notes preview: {details.meeting.notes[:100]}...")
```

### Example 4: Track Meeting Trends

```python
# Get 90-day trend data
stats_90d = use_mcp_tool("granola.meetings.stats",
    window="90d",
    group_by="week"
)

# Find busiest week
max_meetings = 0
busiest_week = None

for period in stats_90d.counts["by_period"]:
    if period.meetings > max_meetings:
        max_meetings = period.meetings
        busiest_week = period.period

print(f"Busiest week: {busiest_week} with {max_meetings} meetings")

# Calculate average
total = sum(p.meetings for p in stats_90d.counts["by_period"])
avg = total / len(stats_90d.counts["by_period"])
print(f"Average meetings per week: {avg:.1f}")
```

### Example 5: Pagination Through All Meetings

```python
all_meetings = []
cursor = None

while True:
    # Fetch page
    result = use_mcp_tool("granola.meetings.list",
        limit=50,
        cursor=cursor
    )

    all_meetings.extend(result.items)

    # Check if more pages
    if not result.next_cursor:
        break

    cursor = result.next_cursor
    print(f"Loaded {len(all_meetings)} meetings so far...")

print(f"Total meetings loaded: {len(all_meetings)}")
```

---

## Advanced Patterns

### Pattern 1: Caching Strategy

```python
import time

# Check cache age
cache_status = use_mcp_tool("granola.cache.status")
print(f"Cache last loaded: {cache_status.last_loaded_ts}")

# Refresh if needed (cache TTL is 24 hours by default)
from datetime import datetime
last_loaded = datetime.fromisoformat(cache_status.last_loaded_ts.replace('Z', '+00:00'))
age_hours = (datetime.now(last_loaded.tzinfo) - last_loaded).total_seconds() / 3600

if age_hours > 12:  # Refresh if older than 12 hours
    print("Refreshing cache...")
    refresh_result = use_mcp_tool("granola.cache.refresh")
    print(f"Refreshed: {refresh_result.meeting_count} meetings")
```

### Pattern 2: Error Handling

```python
def safe_get_meeting(meeting_id):
    """Safely get meeting with error handling."""
    try:
        result = use_mcp_tool("granola.meetings.get",
            id=meeting_id,
            include=["notes", "metadata"]
        )
        return result.meeting
    except Exception as e:
        print(f"Error fetching meeting {meeting_id}: {e}")
        return None

# Use it
meeting = safe_get_meeting("abc123")
if meeting:
    print(f"Got meeting: {meeting.title}")
else:
    print("Meeting not found or error occurred")
```

### Pattern 3: Batch Export

```python
def batch_export_meetings(meeting_ids, output_dir="exports"):
    """Export multiple meetings to a directory."""
    import os
    os.makedirs(output_dir, exist_ok=True)

    for mid in meeting_ids:
        try:
            # Get meeting info
            info = use_mcp_tool("granola.meetings.get", id=mid)

            # Export
            export = use_mcp_tool("granola.meetings.export_markdown", id=mid)

            # Save
            filename = f"{mid[:8]}_{info.meeting.title.replace(' ', '_')[:50]}.md"
            filepath = os.path.join(output_dir, filename)

            with open(filepath, "w") as f:
                f.write(export.markdown)

            print(f"✓ {filename}")
        except Exception as e:
            print(f"✗ {mid}: {e}")

# Use it
meeting_ids = ["id1", "id2", "id3"]
batch_export_meetings(meeting_ids)
```

---

## Troubleshooting

### Issue: "Input validation error: not of type 'object'"

**Solution**: Upgrade FastMCP to 2.13.0+

```bash
pip install --upgrade fastmcp
```

This was fixed in commit `9d7d905` by refactoring tool signatures to accept individual parameters instead of wrapper objects.

### Issue: Cache not refreshing

**Solution**: Force a cache refresh

```python
result = use_mcp_tool("granola.cache.refresh")
print(f"Refreshed {result.meeting_count} meetings")
```

### Issue: Missing meetings

**Solution**: Check pagination and increase limit

```python
# Increase limit
result = use_mcp_tool("granola.meetings.list", limit=100)

# Or paginate through all
while True:
    result = use_mcp_tool("granola.meetings.list",
        limit=50,
        cursor=cursor
    )
    # Process...
    if not result.next_cursor:
        break
    cursor = result.next_cursor
```

### Issue: Token expired (401 error)

**Solution**: Update your API token

```bash
# If using the wrapper script, ensure supabase.json is up to date
# Otherwise, update GRANOLA_API_TOKEN environment variable
export GRANOLA_API_TOKEN="new_token_here"
```

---

## API Reference

### Data Types

#### MeetingSummary
```python
{
    "id": str,
    "title": str,
    "start_ts": str,  # ISO 8601
    "end_ts": Optional[str],
    "participants": List[str],
    "platform": Optional[str],  # "zoom" | "meet" | "teams" | "other"
    "metadata": Optional[Dict]
}
```

#### Meeting (extends MeetingSummary)
```python
{
    # ... MeetingSummary fields ...
    "notes": Optional[str],
    "overview": Optional[str],
    "summary": Optional[str],
    "folder_id": Optional[str],
    "folder_name": Optional[str]
}
```

#### StatsByPeriod
```python
{
    "period": str,  # "2025-11-13" or "2025-W45"
    "meetings": int
}
```

### Response Formats

All tools return structured Pydantic models that can be accessed as objects or dictionaries.

---

## Performance Tips

1. **Use pagination** for large datasets (`limit` + `cursor`)
2. **Cache results** locally when iterating over the same data
3. **Use specific queries** in search to reduce result set
4. **Batch operations** when exporting multiple meetings
5. **Monitor cache age** and refresh strategically

---

## Demonstration Results

From a comprehensive test run on 2025-11-13:

- **Total Meetings**: 286
- **Cache Size**: 9.56 MB
- **Recent Activity**: 2 meetings on 2025-11-13, 5 on 2025-11-12
- **Busiest Week**: Week 45 (2025-W45) with 24 meetings
- **Busiest Day**: Multiple days with 8 meetings

Sample meetings:
- "1st GCS All-Hands Meeting"
- "FreeWheel November Global Check-in"
- "Patrick x Jade: AM Role"
- "Supply AM Bi-Weekly Meeting"
- "FW|Roku Ops Weekly Sync"

---

## Resources

- **Repository**: [GitHub URL]
- **FastMCP Documentation**: https://gofastmcp.com
- **MCP Protocol**: https://modelcontextprotocol.io
- **Granola**: https://granola.ai

---

## Version History

- **v1.1.0** (2025-11-13): Fixed parameter validation, upgraded FastMCP to 2.13.0
- **v1.0.0**: Initial release with 9 tools

---

**Created**: 2025-11-13
**Last Updated**: 2025-11-13
**Status**: All tools fully functional ✅

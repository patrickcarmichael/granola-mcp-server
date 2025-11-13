# Granola MCP Server - Complete Usage Guide

A comprehensive guide to installing, configuring, and using the Granola MCP Server with Claude Code.

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [MCP Server Usage](#mcp-server-usage)
5. [CLI Tool Usage](#cli-tool-usage)
6. [Integration Examples](#integration-examples)
7. [Troubleshooting](#troubleshooting)

---

## Quick Start

Get up and running in 5 minutes:

```bash
# 1. Clone the repository
cd ~/dev
git clone <your-repo-url> granola-mcp-server
cd granola-mcp-server

# 2. Install dependencies
pip install -e ".[dev,mcp]"

# 3. Make scripts executable
chmod +x granola granola-cli.py granola-mcp-remote

# 4. Configure Claude Code (update path in ~/.claude.json)
{
  "mcpServers": {
    "granola": {
      "type": "stdio",
      "command": "/path/to/granola-mcp-server/granola-mcp-remote"
    }
  }
}

# 5. Test the connection
claude mcp list | grep granola
# Should show: granola: .../granola-mcp-remote - ✓ Connected
```

---

## Installation

### Prerequisites

- **Python 3.12+** (tested on 3.12.11)
- **Claude Code** installed and configured
- **Granola app** with an active account (for token generation)
- **macOS** (tested on macOS 15.1)

### Step 1: Clone Repository

```bash
cd ~/dev
git clone https://github.com/patrickcarmichael/granola-mcp-server-enhanced.git granola-mcp-server
cd granola-mcp-server
```

### Step 2: Install Python Dependencies

```bash
# Install with MCP and development dependencies
pip install -e ".[dev,mcp]"

# Or install minimal (no dev tools)
pip install -e ".[mcp]"

# Verify installation
python3 -c "from granola_mcp_server import __version__; print(__version__)"
```

**Dependencies Installed**:
- `fastmcp` - MCP server framework
- `pydantic` - Data validation
- `pydantic-settings` - Configuration management

### Step 3: Make Scripts Executable

```bash
chmod +x granola
chmod +x granola-cli.py
chmod +x granola-mcp-remote
```

### Step 4: Verify Granola Tokens

The wrapper scripts automatically load tokens from:
```
~/Library/Application Support/Granola/supabase.json
```

**Verify token file exists**:
```bash
ls -la ~/Library/Application\ Support/Granola/supabase.json
```

If the file doesn't exist:
1. Open Granola app
2. Log in with your account
3. Token file will be created automatically

---

## Configuration

### Remote API Mode (Recommended)

The default configuration uses the remote Granola API with auto-refreshing tokens.

**No configuration needed!** The wrapper scripts handle everything.

**Optional `.env` file** (for custom settings):

```bash
# Remote API configuration
GRANOLA_DOCUMENT_SOURCE=remote
GRANOLA_API_BASE=https://api.granola.ai

# Cache configuration
GRANOLA_CACHE_DIR=~/.granola/remote_cache
GRANOLA_CACHE_TTL_SECONDS=86400  # 24 hours

# Network configuration
GRANOLA_TIMEOUT_SECONDS=15
GRANOLA_MAX_RETRIES=3
```

### Local Cache Mode (Fallback)

Use Granola's local cache file instead of API.

**Create `.env` file**:
```bash
# Local cache configuration
GRANOLA_DOCUMENT_SOURCE=local
GRANOLA_CACHE_PATH=~/Library/Application Support/Granola/cache-v3.json
```

**Limitations**:
- Only contains meetings synced by Granola app
- May be stale if app hasn't synced recently
- No pagination (returns all cached meetings)

### Manual Token Configuration

If you can't use auto-loading, set the token manually:

```bash
# Extract token from supabase.json
export GRANOLA_API_TOKEN=$(python3 -c "
import json
s = json.load(open('$HOME/Library/Application Support/Granola/supabase.json'))
tokens = json.loads(s['workos_tokens'])
print(tokens['access_token'])
")

# Or set in .env
echo "GRANOLA_API_TOKEN=$GRANOLA_API_TOKEN" >> .env
```

### Environment Variables Reference

| Variable | Default | Description |
|----------|---------|-------------|
| `GRANOLA_DOCUMENT_SOURCE` | `remote` | Source type: `remote` or `local` |
| `GRANOLA_API_TOKEN` | Auto-loaded | Bearer token for API auth |
| `GRANOLA_API_BASE` | `https://api.granola.ai` | API base URL |
| `GRANOLA_CACHE_DIR` | `~/.granola/remote_cache` | Cache directory |
| `GRANOLA_CACHE_TTL_SECONDS` | `86400` | Cache TTL (24 hours) |
| `GRANOLA_CACHE_PATH` | `~/Library/Application Support/Granola/cache-v3.json` | Local cache path |
| `GRANOLA_TIMEOUT_SECONDS` | `15` | Network timeout |
| `GRANOLA_MAX_RETRIES` | `3` | Max retry attempts |

---

## MCP Server Usage

### Starting the Server

The MCP server is started automatically by Claude Code when configured.

**Manual test**:
```bash
./granola-mcp-remote
```

You should see:
```
╭─ FastMCP 2.0 ────────────────────────────────────────╮
│  🖥️  Server name:     granola-mcp-server              │
│  📦 Transport:       STDIO                            │
│  🏎️  FastMCP version: 2.10.2                          │
│  🤝 MCP version:     1.11.0                           │
╰──────────────────────────────────────────────────────╯
```

**Stop the server**: `Ctrl+C`

### Configure Claude Code

#### Option 1: Manual Configuration

Edit `~/.claude.json`:

```json
{
  "mcpServers": {
    "granola": {
      "type": "stdio",
      "command": "/Users/yourusername/dev/granola-mcp-server/granola-mcp-remote",
      "args": [],
      "env": {}
    }
  }
}
```

**Replace** `/Users/yourusername/` with your actual home directory path.

#### Option 2: Using Claude CLI

```bash
# Remove existing configuration (if any)
claude mcp remove granola

# Add new configuration
claude mcp add --transport stdio granola -- \
  ~/dev/granola-mcp-server/granola-mcp-remote

# Verify connection
claude mcp list | grep granola
```

Expected output:
```
granola: ~/dev/granola-mcp-server/granola-mcp-remote - ✓ Connected
```

### Verify Tools Are Available

```bash
# List all MCP tools (requires jq)
claude mcp tools | grep granola
```

You should see 9 tools:
- `granola.meetings.list`
- `granola.meetings.get`
- `granola.meetings.search`
- `granola.meetings.export_markdown`
- `granola.meetings.stats`
- `granola.cache.status`
- `granola.cache.refresh`
- `granola.conversations.list` (alias)
- `granola.conversations.get` (alias)

### Using Tools in Claude Code

Once configured, you can use Granola tools naturally in conversation:

**Example prompts**:

```
"Show me my recent meetings"
→ Uses granola.meetings.list

"Search for meetings about product roadmap"
→ Uses granola.meetings.search

"Get details for meeting ID abc-123"
→ Uses granola.meetings.get

"Export meeting xyz-789 to markdown"
→ Uses granola.meetings.export_markdown

"Show meeting statistics for this week"
→ Uses granola.meetings.stats

"Check Granola cache status"
→ Uses granola.cache.status
```

### Tool Examples

#### List Recent Meetings

```typescript
// Claude Code will invoke:
granola.meetings.list({
  limit: 10,
  offset: 0
})

// Returns:
{
  items: [
    {
      id: "uuid",
      title: "Team Standup",
      start_ts: "2025-11-13T10:00:00Z",
      participants: ["Alice", "Bob"]
    },
    // ...
  ],
  total: 284,
  next_cursor: 10
}
```

#### Search for Meetings

```typescript
// Prompt: "Find meetings about Q4 planning"
granola.meetings.search({
  q: "Q4 planning",
  limit: 5
})

// Returns matching meetings
```

#### Get Meeting Details

```typescript
// Prompt: "Get full details for meeting abc-123"
granola.meetings.get({
  id: "abc-123",
  include: ["notes", "metadata"]
})

// Returns full meeting with notes
```

#### Export to Markdown

```typescript
// Prompt: "Export meeting xyz-789 to markdown"
granola.meetings.export_markdown({
  id: "xyz-789",
  sections: ["header", "notes", "attendees"]
})

// Returns formatted markdown
```

### MCP Server Lifecycle

**Startup**:
1. Claude Code reads `~/.claude.json`
2. Executes `granola-mcp-remote` script
3. Script loads token from `supabase.json`
4. FastMCP server initializes
5. Tools registered and ready

**Runtime**:
- Server runs as long as Claude Code is open
- Handles JSON-RPC requests from Claude
- Caches responses locally
- Auto-refreshes tokens as needed

**Shutdown**:
- Server stops when Claude Code closes
- Cache persists across sessions
- No manual cleanup needed

---

## CLI Tool Usage

The CLI provides direct access to Granola meetings without MCP.

### Basic Commands

#### List Meetings

```bash
# List 50 most recent meetings
./granola list

# List with custom limit
./granola list --limit 10

# Search while listing
./granola list --search "product"
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

#### Search Meetings

```bash
# Basic search
./granola search "roadmap"

# Search with limit
./granola search "Q4 planning" --limit 5

# Search with quotes for exact phrases
./granola search "sprint retrospective"
```

#### Get Meeting Details

```bash
# Get full meeting as JSON
./granola get 1468da54-6156-42eb-8ae9-876ce3b1693a

# Pipe to jq for pretty formatting
./granola get 1468da54... | jq '.'

# Extract specific fields
./granola get 1468da54... | jq '.title, .notes'
```

#### Export to Markdown

```bash
# Export to stdout
./granola export 1468da54-6156-42eb-8ae9-876ce3b1693a

# Export to file
./granola export 1468da54... --output meeting-notes.md

# Export multiple meetings
for id in $(./granola list --limit 10 | grep "ID:" | awk '{print $2}'); do
  ./granola export $id --output "$id.md"
done
```

#### View Statistics

```bash
# Default: last 30 days
./granola stats

# Last 7 days
./granola stats --window 7d

# Last 90 days
./granola stats --window 90d
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

#### Cache Management

```bash
# Check cache status
./granola cache status

# Force refresh cache
./granola cache refresh
```

### Advanced Usage

#### Pipeline Processing

```bash
# Get all meeting IDs
./granola list --limit 1000 | grep "ID:" | awk '{print $2}'

# Export meetings from last week
./granola list --limit 100 | grep "2025-11-" | \
  grep "ID:" | awk '{print $2}' | \
  xargs -I {} ./granola export {} --output {}.md

# Count meetings by day
./granola stats | grep "2025-11-" | wc -l
```

#### Scripting Examples

**Batch export**:
```bash
#!/bin/bash
# Export all meetings to markdown

mkdir -p meeting-exports

./granola list --limit 1000 | grep "ID:" | awk '{print $2}' | while read id; do
  echo "Exporting $id..."
  ./granola export "$id" --output "meeting-exports/$id.md"
done

echo "Export complete!"
```

**Daily summary**:
```bash
#!/bin/bash
# Generate daily meeting summary

TODAY=$(date +%Y-%m-%d)
echo "=== Meetings for $TODAY ===" > daily-summary.txt

./granola list --limit 50 | grep "$TODAY" -A 3 >> daily-summary.txt

cat daily-summary.txt
```

---

## Integration Examples

### Using with Python

```python
#!/usr/bin/env python3
"""Example: Fetch and analyze meetings."""

from granola_mcp_server.config import load_config
from granola_mcp_server.sources import create_document_source
from datetime import datetime, timedelta

# Initialize
config = load_config()
source = create_document_source(config)

# Fetch all meetings
meetings = source.get_all_documents()

# Filter last 7 days
cutoff = datetime.now() - timedelta(days=7)
recent = [
    m for m in meetings
    if datetime.fromisoformat(m['start_ts'].replace('Z', '+00:00')) > cutoff
]

print(f"Meetings in last 7 days: {len(recent)}")

# Group by participant
from collections import defaultdict
by_participant = defaultdict(int)

for meeting in recent:
    for participant in meeting.get('participants', []):
        by_participant[participant] += 1

print("\nMeetings by participant:")
for participant, count in sorted(by_participant.items(), key=lambda x: -x[1]):
    print(f"  {participant}: {count}")
```

### Using with Shell Scripts

```bash
#!/bin/bash
# Weekly meeting report

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CLI="$SCRIPT_DIR/granola"

echo "=== Weekly Meeting Report ==="
echo ""

# Get stats
echo "Statistics:"
$CLI stats --window 7d | grep "2025-" | tail -7

echo ""
echo "Recent meetings:"
$CLI list --limit 10 | grep -E "(Title|Date)" | head -20

echo ""
echo "Total meetings this week: $($CLI stats --window 7d | grep $(date +%Y-%m) | wc -l)"
```

### Using with Claude Code

You can combine MCP tools with Claude Code's other capabilities:

**Example prompt**:
```
"Analyze my last 5 meetings and create a summary document with:
1. Key topics discussed
2. Action items
3. Follow-up needed

Then save it as meeting-summary.md"
```

Claude will:
1. Use `granola.meetings.list` to get recent meetings
2. Use `granola.meetings.get` to fetch full details
3. Analyze the content
4. Create a markdown summary
5. Save using file tools

---

## Troubleshooting

### MCP Connection Issues

#### Problem: "Failed to connect" error

**Check 1**: Verify MCP configuration
```bash
cat ~/.claude.json | grep -A 5 granola
```

**Check 2**: Test wrapper script manually
```bash
cd ~/dev/granola-mcp-server
./granola-mcp-remote
```

Should show FastMCP welcome screen. If error:
- Check Python installation: `python3 --version`
- Verify dependencies: `pip list | grep fastmcp`
- Check file permissions: `ls -la granola-mcp-remote`

**Check 3**: Update configuration path
```bash
claude mcp remove granola
claude mcp add --transport stdio granola -- ~/dev/granola-mcp-server/granola-mcp-remote
```

#### Problem: "Unsupported client" error

**Cause**: Incorrect User-Agent header in API requests

**Solution**: This is already fixed in the enhanced version. If you see this:
1. Verify you're using code from `~/dev/granola-mcp-server`
2. Check `src/granola_mcp_server/sources/remote_api.py:125` has `User-Agent: Granola/1.0.0`

### Token Issues

#### Problem: "Invalid token" or "Unauthorized"

**Check 1**: Verify token file exists
```bash
ls -la ~/Library/Application\ Support/Granola/supabase.json
```

**Check 2**: Check token format
```bash
python3 -c "
import json
path = '$HOME/Library/Application Support/Granola/supabase.json'
data = json.load(open(path))
tokens = json.loads(data['workos_tokens'])
print('Token length:', len(tokens['access_token']))
print('Token starts with:', tokens['access_token'][:20])
"
```

Should show:
```
Token length: 881
Token starts with: eyJhbGciOiJSUzI1NiI...
```

**Check 3**: Refresh token by logging into Granola app
1. Open Granola app
2. Log out
3. Log back in
4. Token file will be refreshed

#### Problem: Token expired

Tokens expire periodically. The wrapper scripts auto-reload fresh tokens, but manual use may fail.

**Solution**: Always use wrapper scripts:
```bash
./granola list           # ✓ Auto-loads fresh token
./granola-cli.py list    # ✗ May use stale token
```

### Cache Issues

#### Problem: Stale data

**Check cache age**:
```bash
./granola cache status
```

**Force refresh**:
```bash
./granola cache refresh
```

**Or reduce TTL**:
```bash
export GRANOLA_CACHE_TTL_SECONDS=3600  # 1 hour
./granola cache refresh
```

#### Problem: Large cache size

**Check cache size**:
```bash
du -sh ~/.granola/remote_cache
```

**Clean up old cache files**:
```bash
# Remove files older than 7 days
find ~/.granola/remote_cache -name "*.json" -mtime +7 -delete

# Or remove all cache
rm -rf ~/.granola/remote_cache/*
./granola cache refresh
```

### CLI Issues

#### Problem: Command not found

**Solution**: Make scripts executable
```bash
chmod +x granola granola-cli.py granola-mcp-remote
```

#### Problem: Import errors

**Solution**: Reinstall dependencies
```bash
pip install -e ".[dev,mcp]"
```

### Performance Issues

#### Problem: Slow API responses

**Check 1**: Network latency
```bash
time curl -I https://api.granola.ai
```

**Check 2**: Enable caching (if not already)
```bash
export GRANOLA_CACHE_ENABLED=true
```

**Check 3**: Increase timeout
```bash
export GRANOLA_TIMEOUT_SECONDS=30
```

#### Problem: High memory usage

If fetching many meetings (1000+):

**Solution**: Use pagination
```python
# Instead of:
all_docs = source.get_all_documents()  # Loads everything

# Use batches:
for offset in range(0, 1000, 100):
    batch = source.get_documents(limit=100, offset=offset)
    process_batch(batch)  # Process incrementally
```

### Getting Help

1. **Check logs**:
   ```bash
   claude mcp logs granola
   ```

2. **Test individual components**:
   ```bash
   # Test config
   python3 -c "from granola_mcp_server.config import load_config; print(load_config())"

   # Test source
   python3 -c "
   from granola_mcp_server.config import load_config
   from granola_mcp_server.sources import create_document_source
   config = load_config()
   source = create_document_source(config)
   docs = source.get_documents(limit=1)
   print(f'Success: {len(docs)} docs')
   "
   ```

3. **Report issues**: Include:
   - Error message
   - Python version: `python3 --version`
   - OS version: `sw_vers`
   - MCP configuration: `cat ~/.claude.json | grep -A 5 granola`

---

## Next Steps

- Read [API_REFERENCE.md](API_REFERENCE.md) for detailed API documentation
- Check [TEST_REPORT.md](TEST_REPORT.md) for performance metrics
- Explore [examples/](../examples/) for more integration patterns

---

**Last Updated**: 2025-11-13
**Version**: 0.1.0

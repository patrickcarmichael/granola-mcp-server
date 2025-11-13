# Granola MCP Server - Documentation Index

Complete documentation for the enhanced Granola MCP Server with remote API support, pagination, and CLI tools.

---

## Quick Links

- [Getting Started](#getting-started)
- [Documentation Files](#documentation-files)
- [Examples](#examples)
- [Support](#support)

---

## Getting Started

### 5-Minute Quickstart

1. **Clone and Install**
   ```bash
   cd ~/dev
   git clone <repo-url> granola-mcp-server
   cd granola-mcp-server
   pip install -e ".[dev,mcp]"
   chmod +x granola granola-cli.py granola-mcp-remote
   ```

2. **Configure Claude Code**
   ```bash
   claude mcp add --transport stdio granola -- ~/dev/granola-mcp-server/granola-mcp-remote
   ```

3. **Verify Connection**
   ```bash
   claude mcp list | grep granola
   # Should show: granola: ... - ✓ Connected
   ```

4. **Test CLI**
   ```bash
   ./granola list --limit 5
   ```

---

## Documentation Files

### Core Documentation

#### [MCP_GUIDE.md](MCP_GUIDE.md) - Complete Usage Guide
**Start here!** Comprehensive guide covering:
- Installation and setup
- Configuration (remote API & local cache)
- MCP server usage with Claude Code
- CLI tool commands
- Integration examples
- Troubleshooting

**When to read**: First-time setup, learning how to use the tools

---

#### [API_REFERENCE.md](API_REFERENCE.md) - Technical Reference
Detailed technical documentation including:
- Granola Remote API specifications
- Endpoint details (/v2/get-documents)
- Authentication and token management
- Document source implementations
- MCP tool schemas
- Python API reference
- Configuration options

**When to read**: Building integrations, debugging issues, understanding internals

---

#### [TEST_REPORT.md](reports/TEST_REPORT.md) - Quality Assurance
Test results and quality metrics:
- Remote API connection tests
- Pagination and data quality tests
- CLI tool functionality tests
- MCP server connection tests
- Performance benchmarks
- Known issues and recommendations

**When to read**: Evaluating reliability, checking performance, troubleshooting

---

### Additional Documentation

#### [README.md](../README.md) - Project Overview
High-level overview with:
- What's new in this enhanced version
- Feature comparison table
- Quick installation guide
- Key improvements documented

**When to read**: Understanding what makes this version better

---

#### [ARCHITECTURE.md](../ARCHITECTURE.md) - System Design
Technical architecture documentation:
- Component structure
- Data flow diagrams
- Design decisions
- Extension points

**When to read**: Contributing to the project, understanding design

---

#### [CHANGELOG.md](../CHANGELOG.md) - Version History
Release notes and version history:
- Version changes
- Bug fixes
- New features
- Breaking changes

**When to read**: Upgrading versions, tracking changes

---

## Examples

### Python Integration

**File**: [examples/python_integration.py](../examples/python_integration.py)

**What it demonstrates**:
- Fetching all meetings with pagination
- Filtering meetings by date range
- Grouping meetings by participant
- Searching meeting content
- Generating reports
- Exporting to markdown

**How to run**:
```bash
cd ~/dev/granola-mcp-server
python3 examples/python_integration.py
```

**Output**:
- Meeting reports in current directory
- Markdown exports in `meeting_exports/`
- Console output with statistics

---

### Shell Script Automation

**File**: [examples/shell_scripts.sh](../examples/shell_scripts.sh)

**What it demonstrates**:
- Weekly meeting reports
- Search and export automation
- Daily summary generation
- Participant attendance tracking
- Bulk meeting backup
- Cache management
- Monthly statistics
- Advanced search patterns

**How to run**:
```bash
cd ~/dev/granola-mcp-server
./examples/shell_scripts.sh
```

**Output**:
- Text reports (*.txt)
- Export directories (exports_*)
- Backup directories (backup_*)

---

### Remote API Example

**File**: [examples/remote_source_example.py](../examples/remote_source_example.py)

**What it demonstrates**:
- Direct Remote API usage
- Token management
- Cache behavior
- Error handling
- Performance measurement

**How to run**:
```bash
cd ~/dev/granola-mcp-server
python3 examples/remote_source_example.py
```

---

## Documentation by Use Case

### I want to...

#### Set up the MCP server for the first time
→ Read [MCP_GUIDE.md - Installation](MCP_GUIDE.md#installation)

#### Understand the Granola API
→ Read [API_REFERENCE.md - Granola Remote API](API_REFERENCE.md#granola-remote-api)

#### Use the CLI tool
→ Read [MCP_GUIDE.md - CLI Tool Usage](MCP_GUIDE.md#cli-tool-usage)

#### Integrate with Python
→ Read [API_REFERENCE.md - Python API](API_REFERENCE.md#python-api)
→ Run [examples/python_integration.py](../examples/python_integration.py)

#### Automate with shell scripts
→ Run [examples/shell_scripts.sh](../examples/shell_scripts.sh)

#### Fix connection issues
→ Read [MCP_GUIDE.md - Troubleshooting](MCP_GUIDE.md#troubleshooting)

#### Check performance metrics
→ Read [TEST_REPORT.md](reports/TEST_REPORT.md)

#### Understand configuration options
→ Read [API_REFERENCE.md - Configuration Reference](API_REFERENCE.md#configuration-reference)

#### Migrate from local to remote mode
→ Read [API_REFERENCE.md - Migration Guide](API_REFERENCE.md#migration-guide)

#### Contribute to the project
→ Read [ARCHITECTURE.md](../ARCHITECTURE.md)

---

## Common Workflows

### Workflow 1: First-Time Setup

1. Read: [MCP_GUIDE.md - Installation](MCP_GUIDE.md#installation)
2. Follow: Installation steps
3. Test: `./granola list --limit 5`
4. Configure: [MCP_GUIDE.md - Configure Claude Code](MCP_GUIDE.md#configure-claude-code)
5. Verify: `claude mcp list | grep granola`

---

### Workflow 2: Building an Integration

1. Read: [API_REFERENCE.md - Python API](API_REFERENCE.md#python-api)
2. Study: [examples/python_integration.py](../examples/python_integration.py)
3. Reference: [API_REFERENCE.md - MCP Tools](API_REFERENCE.md#mcp-tools)
4. Test: Run your integration
5. Debug: [MCP_GUIDE.md - Troubleshooting](MCP_GUIDE.md#troubleshooting)

---

### Workflow 3: Troubleshooting Issues

1. Check: [MCP_GUIDE.md - Troubleshooting](MCP_GUIDE.md#troubleshooting)
2. Review: [TEST_REPORT.md - Known Issues](../TEST_REPORT.md#issues--recommendations)
3. Verify: Run test commands from troubleshooting guide
4. Reference: [API_REFERENCE.md - Common Issues](API_REFERENCE.md#common-issues)

---

### Workflow 4: Understanding Performance

1. Read: [TEST_REPORT.md - Performance Metrics](reports/TEST_REPORT.md#performance-metrics)
2. Check: [API_REFERENCE.md - Performance Tips](API_REFERENCE.md#performance-tips)
3. Optimize: Follow recommendations
4. Measure: Re-run tests

---

## Document Versions

| Document | Last Updated | Version |
|----------|-------------|---------|
| MCP_GUIDE.md | 2025-11-13 | 0.1.0 |
| API_REFERENCE.md | 2025-11-13 | 0.1.0 |
| TEST_REPORT.md | 2025-11-13 | 0.1.0 |
| README.md | 2025-11-13 | 0.1.0 |

---

## Support

### Getting Help

1. **Check Documentation**: Start with relevant guide above
2. **Run Examples**: Try example scripts to understand usage
3. **Review Tests**: Check TEST_REPORT.md for known issues
4. **Check Logs**: `claude mcp logs granola`

### Reporting Issues

When reporting issues, include:
- Error message (full traceback)
- Python version: `python3 --version`
- OS version: `sw_vers` (macOS) or `uname -a` (Linux)
- Configuration: `cat ~/.claude.json | grep -A 5 granola`
- Steps to reproduce

### Contributing

See [ARCHITECTURE.md](../ARCHITECTURE.md) for:
- Component structure
- Development setup
- Testing guidelines
- Code style

---

## Quick Reference

### Essential Commands

```bash
# MCP Server
claude mcp list                    # Check connection status
claude mcp logs granola            # View server logs

# CLI Tool
./granola list --limit 10          # List recent meetings
./granola search "query"           # Search meetings
./granola get <id>                 # Get meeting details
./granola stats                    # View statistics
./granola cache status             # Check cache

# Testing
python3 examples/python_integration.py    # Run Python examples
./examples/shell_scripts.sh               # Run shell examples
```

### Configuration Files

```bash
~/.claude.json                     # Claude Code MCP config
.env                               # Environment variables
~/Library/Application Support/Granola/supabase.json  # Token source
~/.granola/remote_cache/           # Remote API cache
```

### Environment Variables

```bash
GRANOLA_DOCUMENT_SOURCE=remote     # Use remote API
GRANOLA_API_TOKEN=<token>          # API token (auto-loaded)
GRANOLA_CACHE_TTL_SECONDS=86400    # Cache TTL (24h)
```

---

## Documentation Roadmap

### Planned Documentation

- [ ] Video tutorials for setup and usage
- [ ] Advanced integration patterns
- [ ] Performance optimization guide
- [ ] Security best practices
- [ ] API rate limiting guide
- [ ] Multi-user deployment guide

### Recent Updates

- ✅ Complete MCP usage guide
- ✅ Comprehensive API reference
- ✅ Test report with benchmarks
- ✅ Python integration examples
- ✅ Shell script automation examples
- ✅ Troubleshooting guide

---

**Documentation Version**: 0.1.0
**Last Updated**: 2025-11-13
**Maintained By**: Enhanced Granola MCP Server Team

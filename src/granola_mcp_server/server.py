"""FastMCP server entrypoint.

Registers tools for the Granola MCP Server. This module intentionally
keeps the tool implementations decoupled so they can be unit-tested
without the runtime.

Note: We import FastMCP lazily to keep stdlib-only profile lightweight
until the MCP runtime is actually used.
"""

# NOTE: Removed 'from __future__ import annotations' to avoid Pydantic type resolution issues
# FastMCP/Pydantic needs actual type objects in the global namespace

import sys
from typing import Optional

from .config import load_config
from .parser import GranolaParser
from .schemas import (
    CacheStatusOutput,
    ExportMarkdownInput,
    ExportMarkdownOutput,
    GetMeetingInput,
    GetMeetingOutput,
    ListMeetingsInput,
    ListMeetingsOutput,
    RefreshCacheInput,
    RefreshCacheOutput,
    SearchMeetingsInput,
    SearchMeetingsOutput,
    StatsInput,
    StatsOutput,
)
from .sources import create_document_source
from .sources.adapter import DocumentSourceAdapter
from .tools import (
    cache_status,
    export_markdown,
    get_meeting,
    list_meetings,
    meetings_stats,
    refresh_cache,
    search_meetings,
)

# Module-level globals for config and adapter
_config = None
_adapter = None


# Tool wrapper functions defined at module level so type hints can resolve
def _meetings_list_conversations(
    q: Optional[str] = None,
    from_ts: Optional[str] = None,
    to_ts: Optional[str] = None,
    participants: Optional[list[str]] = None,
    limit: Optional[int] = 50,
    cursor: Optional[str] = None
) -> ListMeetingsOutput:
    params = ListMeetingsInput(
        q=q, from_ts=from_ts, to_ts=to_ts,
        participants=participants, limit=limit, cursor=cursor
    )
    return list_meetings(_config, _adapter, params)


def _meetings_list(
    q: Optional[str] = None,
    from_ts: Optional[str] = None,
    to_ts: Optional[str] = None,
    participants: Optional[list[str]] = None,
    limit: Optional[int] = 50,
    cursor: Optional[str] = None
) -> ListMeetingsOutput:
    params = ListMeetingsInput(
        q=q, from_ts=from_ts, to_ts=to_ts,
        participants=participants, limit=limit, cursor=cursor
    )
    return list_meetings(_config, _adapter, params)


def _meetings_get_conversations(
    id: str,
    include: Optional[list[str]] = None
) -> GetMeetingOutput:
    params = GetMeetingInput(id=id, include=include)
    return get_meeting(_config, _adapter, params)


def _meetings_get(
    id: str,
    include: Optional[list[str]] = None
) -> GetMeetingOutput:
    params = GetMeetingInput(id=id, include=include)
    return get_meeting(_config, _adapter, params)


def _meetings_search(
    q: str,
    filters: Optional[dict] = None,
    limit: Optional[int] = 50,
    cursor: Optional[str] = None
) -> SearchMeetingsOutput:
    from .schemas import SearchFilters
    filters_obj = SearchFilters(**filters) if filters else None
    params = SearchMeetingsInput(q=q, filters=filters_obj, limit=limit, cursor=cursor)
    return search_meetings(_config, _adapter, params)


def _meetings_export_md(
    id: str,
    sections: Optional[list[str]] = None
) -> ExportMarkdownOutput:
    params = ExportMarkdownInput(id=id, sections=sections)
    return export_markdown(_config, _adapter, params)


def _meetings_stats_tool(
    window: Optional[str] = None,
    group_by: Optional[str] = None
) -> StatsOutput:
    params = StatsInput(window=window, group_by=group_by)
    return meetings_stats(_config, _adapter, params)


def _cache_status_tool() -> CacheStatusOutput:
    return cache_status(_config, _adapter)


def _cache_refresh_tool() -> RefreshCacheOutput:
    params = RefreshCacheInput()
    return refresh_cache(_config, _adapter, params)


def _register_fastmcp_tools(app, config, adapter):
    # Store config and adapter in module globals
    global _config, _adapter
    _config = config
    _adapter = adapter

    # Register tools with FastMCP
    app.tool("granola.conversations.list")(_meetings_list_conversations)
    app.tool("granola.meetings.list")(_meetings_list)
    app.tool("granola.conversations.get")(_meetings_get_conversations)
    app.tool("granola.meetings.get")(_meetings_get)
    app.tool("granola.meetings.search")(_meetings_search)
    app.tool("granola.meetings.export_markdown")(_meetings_export_md)
    app.tool("granola.meetings.stats")(_meetings_stats_tool)
    app.tool("granola.cache.status")(_cache_status_tool)
    app.tool("granola.cache.refresh")(_cache_refresh_tool)


def main(argv = None):
    """Run the FastMCP application.

    This function loads configuration, creates a document source (local or remote),
    wraps it in an adapter, and registers all tools with the FastMCP runtime.
    It is safe to import and call `main()` from other entrypoints.
    """

    argv = argv if argv is not None else sys.argv[1:]
    config = load_config()
    
    # Create document source based on configuration
    try:
        source = create_document_source(config)
        adapter = DocumentSourceAdapter(source)
    except Exception as exc:
        print(f"Error creating document source: {exc}", file=sys.stderr)
        sys.exit(1)

    try:
        from fastmcp import FastMCP
    except Exception as exc:  # pragma: no cover - optional dependency
        raise RuntimeError(
            "fastmcp is not installed. Install with 'pip install granola-mcp-server[mcp]'"
        ) from exc

    app = FastMCP("granola-mcp-server")
    _register_fastmcp_tools(app, config, adapter)

    # Run the FastMCP app (serves until interrupted)
    app.run()


if __name__ == "__main__":  # pragma: no cover
    main()

"""Web search tool (the workers' primary tool) and a tool-call logger.

When the ``AGENT_TRACE_DIR`` env var points at a directory, every
``internet_search`` call (with its query and a compact result summary) is
appended as one JSONL line to ``<AGENT_TRACE_DIR>/tool_calls.jsonl`` -- used
by the eval harness to grade individual pipeline stages after the run.
Persistence lives on the tool function itself (not on the middleware) because
subagent tool calls do not pass through the parent agent's middleware.
"""

import json
import logging
import os
from typing import Literal

from dotenv import load_dotenv
from langchain.agents.middleware import wrap_tool_call
from tavily import TavilyClient

load_dotenv()

logger = logging.getLogger(__name__)

tavily_client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])


def internet_search(
    query: str,
    max_results: int = 5,
    topic: Literal["general", "news", "finance"] = "general",
    include_raw_content: bool = False,
):
    """Run a web search and return results (title, url, content snippet).

    Use specific, narrow queries. For pricing or funding, prefer the
    competitor's own domain or `topic="finance"`.
    """
    response = tavily_client.search(
        query,
        max_results=max_results,
        include_raw_content=include_raw_content,
        topic=topic,
    )
    # Subagent tool calls do not pass through the parent's middleware, so
    # persist searches at the function level to ensure they always land in the
    # trace, regardless of which agent invoked them.
    _persist_search_call(query, max_results, topic, response)
    return response


def _persist_search_call(query, max_results, topic, response):
    trace_dir = os.environ.get("AGENT_TRACE_DIR")
    if not trace_dir:
        return
    entry = {
        "tool": "internet_search",
        "args": {"query": query, "max_results": max_results, "topic": topic},
        "response": _summarize_for_trace("internet_search", response),
    }
    with open(os.path.join(trace_dir, "tool_calls.jsonl"), "a") as f:
        f.write(json.dumps(entry, default=str) + "\n")


def _summarize_for_trace(tool_name, response):
    """Return a JSON-safe summary of a tool response for the trace log."""
    payload = getattr(response, "content", response)

    if tool_name == "internet_search" and isinstance(payload, dict):
        return {
            "query": payload.get("query"),
            "results": [
                {
                    "title": r.get("title"),
                    "url": r.get("url"),
                    "score": r.get("score"),
                    "content": (r.get("content") or "")[:400],
                }
                for r in payload.get("results", [])
            ],
        }

    if isinstance(payload, (dict, list)):
        try:
            s = json.dumps(payload, default=str)
        except TypeError:
            s = str(payload)
    else:
        s = str(payload)
    return s if len(s) <= 800 else s[:799] + "…"


@wrap_tool_call
def log_tool_calls(request, handler):
    tool_call = getattr(request, "tool_call", None)
    if isinstance(tool_call, dict):
        tool_name = tool_call.get("name", "tool")
        tool_args = tool_call.get("args")
    else:
        tool_name = getattr(request, "name", "tool")
        tool_args = getattr(request, "args", None)

    if tool_args:
        summary = str(tool_args)
        if len(summary) > 200:
            summary = summary[:199] + "…"
        logger.info("→ %s(%s)", tool_name, summary)
    else:
        logger.info("→ %s", tool_name)
    return handler(request)

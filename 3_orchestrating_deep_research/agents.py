"""Subagent definitions and the lead-agent builder.

Orchestrator-worker pattern (Anthropic's multi-agent research system):
  - lead agent           -> plans, delegates, synthesizes the comparison.
  - competitor-scout      -> discovers WHO the competitors are.
  - competitor-researcher -> deep-dives ONE competitor each, in parallel.
  - fact-checker          -> audits every sourced claim before it ships.
"""

from deepagents import create_deep_agent

from models import LEAD_MODEL, WORKER_MODEL
from prompts import (
    COMPETITOR_RESEARCHER_PROMPT,
    COMPETITOR_SCOUT_PROMPT,
    FACT_CHECKER_PROMPT,
    LEAD_AGENT_PROMPT,
)
from tools import internet_search, log_tool_calls

competitor_scout_subagent = {
    "name": "competitor-scout",
    "description": (
        "Use FIRST when the competitor set is not already given. Delegate the "
        "task of identifying WHO the competitors are for a subject company/"
        "product in a market. Your instruction MUST include: (1) the subject "
        "and market/category, (2) the buyer/segment that matters, and (3) a "
        "`findings_file` path (e.g. `findings/scout.md`). It returns a ranked "
        "shortlist of competitors with homepage URLs and one-line reasons."
    ),
    "system_prompt": COMPETITOR_SCOUT_PROMPT,
    "tools": [internet_search],
    "model": WORKER_MODEL,
}

competitor_researcher_subagent = {
    "name": "competitor-researcher",
    "description": (
        "Delegate a deep-dive on ONE named competitor. Your task instruction "
        "MUST include: (1) the single competitor name (and homepage URL if "
        "known), (2) the subject/market it is being compared within, (3) the "
        "exact comparison dimensions to fill (keep these identical across "
        "sibling agents), (4) explicit boundaries naming the other competitors "
        "so no two agents overlap, and (5) a unique `findings_file` path (e.g. "
        "`findings/<competitor-slug>.md`). It searches the web, writes detailed "
        "sourced findings to that file, and returns a short synthesis plus the "
        "path. Dispatch several in parallel, one per competitor."
    ),
    "system_prompt": COMPETITOR_RESEARCHER_PROMPT,
    "tools": [internet_search],
    "model": WORKER_MODEL,
}

# No tools key: audits only what was already gathered into findings/.
fact_checker_subagent = {
    "name": "fact-checker",
    "description": (
        "Use this AFTER drafting the final analysis and BEFORE returning it. "
        "Give it the `notes.md` draft plus a pointer to the `findings/` "
        "directory. It verifies every claim -- especially prices, features, "
        "and funding figures -- is sourced, dated, and not overstated."
    ),
    "system_prompt": FACT_CHECKER_PROMPT,
    "model": WORKER_MODEL,
}


def build_agent(backend):
    """Wire the lead agent to its subagents and backend."""
    return create_deep_agent(
        model=LEAD_MODEL,
        tools=[internet_search],
        system_prompt=LEAD_AGENT_PROMPT,
        subagents=[
            competitor_scout_subagent,
            competitor_researcher_subagent,
            fact_checker_subagent,
        ],
        middleware=[log_tool_calls],
        backend=backend,
    )

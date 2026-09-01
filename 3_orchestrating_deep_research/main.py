"""Competitor research agent built on `deepagents`.

A lead agent plans and delegates to subagents (scout, researchers, fact-checker)
that fan out over the web, then synthesizes a comparison matrix + analysis.

Each run gets its own folder under `runs/<run_id>/` holding the agent's files
(plan.md, notes.md, findings/), so you can inspect exactly what happened.

Usage:
    python main.py "Analyze the competitors of Notion in the docs space"
    python main.py "Compare Linear against Jira and Asana"
"""

import logging
import os
import sys
import uuid

from deepagents.backends import FilesystemBackend

from agents import build_agent

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

RUNS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "runs")


def main():
    question = " ".join(sys.argv[1:]) or (
        "Analyze the main competitors of Notion in the productivity and "
        "collaborative-docs space, and where Notion is differentiated vs. exposed."
    )
    run_id = f"competitor-{uuid.uuid4().hex[:12]}"

    run_dir = os.path.join(RUNS_DIR, run_id)
    os.makedirs(run_dir, exist_ok=True)

    # virtual_mode anchors every agent path under run_dir and blocks traversal.
    backend = FilesystemBackend(root_dir=run_dir, virtual_mode=True)
    agent = build_agent(backend)

    logger.info("Competitor research: %s", question)
    logger.info("Run folder: %s", run_dir)

    agent_input = {
        "messages": [{"role": "user", "content": question}]
    }

    try:
        result = agent.invoke(agent_input)
        final = result["messages"][-1].content
        print(final if isinstance(final, str) else str(final))
    except Exception:
        logger.exception("Agent run failed")


if __name__ == "__main__":
    main()

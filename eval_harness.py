"""Evaluation harness for the deep-research pipeline demo notebook.

Everything mechanical lives here so the teaching notebook only shows:
  - Data (GOLD_SOURCES, GOLD_FACTS)
  - Prompts (RECOMMENDATION_PROMPT)
  - Top-level calls (set_config, run_deep_research, grade_saved_run,
    print_config_comparison)

Typical usage in the notebook:

    from eval_harness import (
        set_config, run_deep_research, grade_saved_run,
        print_config_comparison,
    )

    # model constants (GEMMA, NANO, SUPER) live in the notebook, not here

    set_config("baseline", lead=SUPER, worker=NANO, judge=NANO)
    run_dir = run_deep_research(RECOMMENDATION_PROMPT)
    scores  = grade_saved_run(run_dir, GOLD_SOURCES, GOLD_FACTS)
    ...
    print_config_comparison()

`grade_saved_run` grades retrieval and recommendation from `run_dir`'s
saved artifacts. Only the judge LLM is called; the agent is not
re-invoked.

Requires NEBIUS_API_KEY in the environment before import (the pricing
lookup runs at import time). TAVILY_API_KEY is needed only when the
agent actually runs.
"""

import importlib
import json
import os
import uuid
from pathlib import Path
from typing import Literal
from urllib.parse import urlparse

import httpx
from openai import APITimeoutError
from pydantic import BaseModel, Field
from tqdm import tqdm

from deepagents.backends import FilesystemBackend
from langchain_core.callbacks import UsageMetadataCallbackHandler
from langchain_nebius import ChatNebius


# =============================================================================
# Pricing & cost tracking
# =============================================================================
_r = httpx.get(
    "https://api.studio.nebius.com/v1/models?verbose=true",
    headers={"Authorization": f"Bearer {os.environ['NEBIUS_API_KEY']}"},
    timeout=30,
)
_r.raise_for_status()
NEBIUS_PRICING = {m["id"]: m["pricing"] for m in _r.json()["data"]}
print(f"Fetched pricing for {len(NEBIUS_PRICING)} Nebius models")

TAVILY_PRICE_PER_CREDIT = 0.008


def total_cost(callback, tavily_searches=0):
    """Return (nebius_cost, tavily_cost) in USD from a UsageMetadataCallbackHandler."""
    nebius = 0.0
    for model_id, um in callback.usage_metadata.items():
        p = NEBIUS_PRICING.get(model_id)
        if p is None:
            print(f"  (no pricing for {model_id})")
            continue
        nebius += um["input_tokens"]  * float(p["prompt"])
        nebius += um["output_tokens"] * float(p["completion"])
    tavily = tavily_searches * TAVILY_PRICE_PER_CREDIT
    return nebius, tavily


STAGE_COST = {}


# =============================================================================
# Running the deep-research agent
# =============================================================================
RUNS_DIR = Path("runs")
RUNS_DIR.mkdir(exist_ok=True)


def run_agent_on(prompt, name, callbacks=None):
    """Run the deep-research agent on a prompt. Returns a pathlib.Path.

    Deferred import of `build_agent` so `set_config`'s reload of the `agents`
    module takes effect for subsequent calls.
    """
    from agents import build_agent

    run_id = f"{name}-{uuid.uuid4().hex[:8]}"
    run_dir = RUNS_DIR / run_id
    run_dir.mkdir(parents=True)

    backend = FilesystemBackend(root_dir=str(run_dir), virtual_mode=True)
    agent = build_agent(backend)
    config = {"configurable": {"thread_id": run_id}, "callbacks": callbacks or []}

    os.environ["AGENT_TRACE_DIR"] = str(run_dir)
    try:
        try:
            result = agent.invoke(
                {"messages": [{"role": "user", "content": prompt}]},
                config=config,
            )
        except APITimeoutError:
            result = agent.invoke(None, config=config)
    finally:
        os.environ.pop("AGENT_TRACE_DIR", None)

    (run_dir / "messages.json").write_text(
        json.dumps([m.model_dump() for m in result["messages"]], indent=2, default=str)
    )
    final = result["messages"][-1].content
    if not isinstance(final, str):
        final = str(final)
    (run_dir / "final_answer.md").write_text(final)
    return run_dir


# =============================================================================
# Grading: retrieval (programmatic, no LLM)
# =============================================================================
def grade_retrieval(run_dir, gold):
    """Coverage of gold competitor domains in the agent's search trace."""
    trace_path = run_dir / "tool_calls.jsonl"
    calls = ([json.loads(l) for l in trace_path.read_text().splitlines() if l.strip()]
             if trace_path.exists() else [])
    search_calls = [c for c in calls if c["tool"] == "internet_search"]

    all_urls = []
    for c in search_calls:
        resp = c.get("response")
        if isinstance(resp, dict):
            for r in resp.get("results") or []:
                if r.get("url"):
                    all_urls.append(r["url"])

    def netloc_matches(netloc, root):
        n = netloc.lower().split(":")[0]
        return n == root or n.endswith("." + root)

    per_competitor = {}
    for competitor, info in gold.items():
        found = False
        for url in all_urls:
            try:
                netloc = urlparse(url).netloc
            except ValueError:
                continue
            if netloc_matches(netloc, info["domain_root"]):
                found = True
                break
        per_competitor[competitor] = found

    hits = sum(per_competitor.values())
    total = len(per_competitor)
    return {
        "tool_calls_valid": len(search_calls) > 0,
        "num_search_calls": len(search_calls),
        "coverage":         hits / total if total else 0.0,
        "hits":             hits,
        "total":            total,
        "per_competitor":   per_competitor,
    }


# =============================================================================
# Grading: recommendation (LLM judge, rubric + fact recall)
# =============================================================================
class RubricAnswer(BaseModel):
    top_3_given_answer:                        Literal["yes", "no"]
    top_3_given_why:                           str
    evidence_corresponds_to_retrieved_answer:  Literal["yes", "no"]
    evidence_corresponds_to_retrieved_why:     str
    recommendation_grounded_answer:            Literal["yes", "no"]
    recommendation_grounded_why:               str


class FactContainment(BaseModel):
    competitor_in_scope: bool = Field(
        description=(
            "True if the report actually analyzes this competitor: gives it "
            "its own section, includes it in a comparison table, or names it "
            "in the top-3. False if the competitor only appears in a passing "
            "list of alternatives without individual analysis."
        )
    )
    contains: bool = Field(description="Only relevant if competitor_in_scope is true.")
    why: str = Field(default="")


def _load_findings(run_dir):
    parts = []
    for name in ("plan.md", "notes.md"):
        p = run_dir / name
        if p.exists():
            parts.append(f"--- {name} ---\n{p.read_text()}")
    findings_dir = run_dir / "findings"
    if findings_dir.exists():
        for p in sorted(findings_dir.glob("*.md")):
            parts.append(f"--- findings/{p.name} ---\n{p.read_text()}")
    text = "\n\n".join(parts) or "(no findings)"
    return text[:120_000]


def grade_synthesis(run_dir, gold_facts, cb):
    """Rubric + fact-recall grading of the recommendation report."""
    report = (run_dir / "final_answer.md").read_text()
    findings = _load_findings(run_dir)
    judge = ChatNebius(model=os.environ["JUDGE_MODEL"], temperature=0.0, timeout=180)

    rubric_prompt = f"""You are grading the final report of a deep-research agent.

Two inputs:
  1. RETRIEVED FINDINGS -- what the pipeline gathered before synthesis.
  2. FINAL REPORT.

Answer each rubric item YES or NO. YES only if clearly yes; ambiguous or
partial cases are NO.

Rubric:
- top_3_given: does the report give a specific top-3 recommendation the
  reader can identify?
- evidence_corresponds_to_retrieved: for every factual claim in the report,
  does supporting evidence appear in the retrieved findings? NO if the
  synthesis stage hallucinated content the pipeline never retrieved.
- recommendation_grounded: does the top-3 follow from the facts the report
  itself presents?

--- RETRIEVED FINDINGS ---
{findings}
--- FINAL REPORT ---
{report}
"""
    rubric = judge.with_structured_output(RubricAnswer).invoke(
        rubric_prompt, config={"callbacks": [cb]}
    )

    rubric_scores = {
        "top_3_given":                        rubric.top_3_given_answer == "yes",
        "evidence_corresponds_to_retrieved":  rubric.evidence_corresponds_to_retrieved_answer == "yes",
        "recommendation_grounded":            rubric.recommendation_grounded_answer == "yes",
    }
    rubric_reasons = {
        "top_3_given":                        rubric.top_3_given_why,
        "evidence_corresponds_to_retrieved":  rubric.evidence_corresponds_to_retrieved_why,
        "recommendation_grounded":            rubric.recommendation_grounded_why,
    }

    struct = judge.with_structured_output(FactContainment)
    per_fact = []
    for gf in tqdm(gold_facts, desc="fact-recall"):
        p = f"""Reference fact ({gf['competitor']}, {gf['dimension']}): {gf['claim']}

Answer two questions about the report below.

1. competitor_in_scope: does the report actually analyze {gf['competitor']} --
   give it its own section, include it in the comparison table, or name it
   in the top-3? Say NO if the report only mentions {gf['competitor']} in a
   passing list of alternatives without individual analysis.
2. contains: only if in scope. Does the report substantively state a claim
   equivalent to the reference? Same numbers/names as reference.

--- REPORT ---
{report}
"""
        j = struct.invoke(p, config={"callbacks": [cb]})
        if j is None:
            per_fact.append({**gf, "in_scope": False, "contains": False})
        else:
            per_fact.append({**gf, "in_scope": j.competitor_in_scope,
                                    "contains": j.contains})

    in_scope = [pf for pf in per_fact if pf["in_scope"]]
    hits = sum(pf["contains"] for pf in in_scope)

    return {
        "rubric_scores":  rubric_scores,
        "rubric_reasons": rubric_reasons,
        "fact_recall":    hits / len(in_scope) if in_scope else 0.0,
        "facts_hit":      hits,
    }


# =============================================================================
# Multi-config runner
# =============================================================================
# Model-name constants (GEMMA, NANO, SUPER) live in the notebook, not here --
# they're part of what students read and choose from.

CURRENT_CONFIG = None


def set_config(name, lead, worker, judge):
    """Swap the model roster and reload the deep-agent module."""
    global CURRENT_CONFIG
    os.environ["LEAD_MODEL"]   = lead
    os.environ["WORKER_MODEL"] = worker
    os.environ["JUDGE_MODEL"]  = judge
    import models, agents
    importlib.reload(models); importlib.reload(agents)
    CURRENT_CONFIG = name
    print(f"Config '{name}':  LEAD={lead}  |  WORKER={worker}  |  JUDGE={judge}")


def _record_cost(stage, cost):
    STAGE_COST[(CURRENT_CONFIG, stage)] = cost
    total = sum(v for v in STAGE_COST.values())
    print(f"  spent this stage: ${cost:.4f}   |   running total: ${total:.4f}")


def run_deep_research(prompt):
    """Run the deep-research agent ONCE on `prompt` under the current config.
    Returns run_dir. Grading happens separately from the saved artifacts."""
    assert CURRENT_CONFIG, "call set_config(...) first"
    cb = UsageMetadataCallbackHandler()
    run_dir = run_agent_on(prompt, f"deep-{CURRENT_CONFIG}", callbacks=[cb])
    trace_path = run_dir / "tool_calls.jsonl"
    n_searches = sum(1 for l in (trace_path.read_text().splitlines() if trace_path.exists() else [])
                     if l.strip() and json.loads(l)["tool"] == "internet_search")
    nebius, tavily_cost = total_cost(cb, tavily_searches=n_searches)
    print(f"\nRun folder: {run_dir}")
    _record_cost("deep_research", nebius + tavily_cost)
    return run_dir


def grade_saved_run(run_dir, gold_sources, gold_facts):
    """Grade retrieval and recommendation for the current config, from the
    saved artifacts of a single deep-research run. Only the judge LLM is
    called here; the agent is not re-invoked."""
    assert CURRENT_CONFIG, "call set_config(...) first"

    ret = grade_retrieval(run_dir, gold_sources)
    print(f"\n--- Retrieval ---")
    print(f"  tool_calls_valid: {ret['tool_calls_valid']}   num_search_calls: {ret['num_search_calls']}")
    print(f"  coverage:         {100*ret['coverage']:.0f}%   ({ret['hits']}/{ret['total']})")
    for comp, hit in ret["per_competitor"].items():
        print(f"    {comp:20s}  {'found' if hit else 'MISSED'}")
    # Retrieval grading is programmatic (no LLM). Nothing to record.

    cb = UsageMetadataCallbackHandler()
    rec = grade_synthesis(run_dir, gold_facts, cb)
    nebius, _ = total_cost(cb)
    print(f"\n--- Recommendation ---")
    print("  Rubric:")
    for k, v in rec["rubric_scores"].items():
        print(f"    {'YES' if v else ' NO'}  {k}: {rec['rubric_reasons'][k][:110]}")
    print(f"  Fact recall: {rec['facts_hit']} correctly stated   ({100*rec['fact_recall']:.0f}%)")
    _record_cost("recommendation_grading", nebius)

    return {"retrieval": ret, "recommendation": rec}


def print_config_comparison():
    """Side-by-side per-config totals from STAGE_COST."""
    entries = {k: v for k, v in STAGE_COST.items() if isinstance(k, tuple) and len(k) == 2}
    if not entries:
        print("(no per-config entries yet -- call set_config + stage helpers first)")
        return
    configs = sorted({c for c, _ in entries})
    stages  = sorted({s for _, s in entries})
    w = max(20, max(len(c) for c in configs) + 2)
    print(f"  {'stage':<22}  " + "  ".join(f"{c:>{w}}" for c in configs))
    print(f"  {'-'*22}  " + "  ".join(f"{'-'*w}" for _ in configs))
    for stage in stages:
        row = "  ".join(f"${entries.get((c, stage), 0.0):>{w-1}.4f}" for c in configs)
        print(f"  {stage:<22}  {row}")
    print(f"  {'-'*22}  " + "  ".join(f"{'-'*w}" for _ in configs))
    totals = "  ".join(f"${sum(v for (cc,_),v in entries.items() if cc==c):>{w-1}.4f}" for c in configs)
    print(f"  {'TOTAL':<22}  {totals}")

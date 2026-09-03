"""Per-role LLM routing on Nebius Token Factory.
"""

import os

from dotenv import load_dotenv
from langchain_nebius import ChatNebius

load_dotenv()

LEAD_MODEL_NAME = os.environ.get("LEAD_MODEL", "nvidia/Nemotron-3-Ultra-550b-a55b")
WORKER_MODEL_NAME = os.environ.get("WORKER_MODEL", "nvidia/nemotron-3-super-120b-a12b")

LEAD_MODEL = ChatNebius(
    model=LEAD_MODEL_NAME,
    reasoning_effort="high",
)

WORKER_MODEL = ChatNebius(
    model=WORKER_MODEL_NAME,
    reasoning_effort="medium",
)

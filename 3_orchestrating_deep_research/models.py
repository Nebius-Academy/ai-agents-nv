"""Per-role LLM routing on Nebius Token Factory.
"""

import os

from dotenv import load_dotenv
from langchain_nebius import ChatNebius

load_dotenv()

LEAD_MODEL_NAME = os.environ.get("LEAD_MODEL", "MiniMaxAI/MiniMax-M2.5")
WORKER_MODEL_NAME = os.environ.get("WORKER_MODEL", "MiniMaxAI/MiniMax-M2.5")

LEAD_MODEL = ChatNebius(
    model=LEAD_MODEL_NAME,
    reasoning_effort="high",
)

WORKER_MODEL = ChatNebius(
    model=WORKER_MODEL_NAME,
    reasoning_effort="medium",
)

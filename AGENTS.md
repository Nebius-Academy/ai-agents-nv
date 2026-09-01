We are making a course about how to create agents in Python. Lesson code lives under numbered folders, one per lesson — e.g. `3_orchestrating_deep_research/` holds the competitor research agent, built on the `deepagents` library, using Tavily for web search and Nebius Token Factory for LLM APIs.

## Local environment

A local virtual environment lives in `.venv` (Python 3.13). Always use it when running or installing anything — do not use the system Python.

Setup (already done, only needed on a fresh clone):

```bash
python3.13 -m venv .venv
.venv/bin/python -m pip install -r 3_orchestrating_deep_research/requirements.txt
```

Running commands — always go through the venv, e.g.:

```bash
.venv/bin/python 3_orchestrating_deep_research/main.py
.venv/bin/python -m pip install <package>
```

Or activate it first: `source .venv/bin/activate`.

Copy `.env.example` to `.env` and fill in `NEBIUS_API_KEY` and `TAVILY_API_KEY` before running.

---
theme: nebius-agents
title: Giving an LLM tools to access the web
info: |
  Module 02 — Web search with Tavily and your first agentic loop.
author: Nebius AI Agents Course
colorSchema: dark
aspectRatio: 16/9
canvasWidth: 1600
transition: fade
lineNumbers: false
drawings:
  persist: false
layout: course-cover
---

<div class="deck-kicker">AI Agents · Module 02</div>
<h1>Give an LLM the web<br>with a first <span>agent loop</span></h1>
<p>You already called a simple tool. Now: Tavily Search + Extract inside a Python loop — the primitive under competitor research, not the finished agent.</p>

::provider::

<div class="cover-provider-lockup">
  <img class="tavily" src="/tavily-logo.svg" alt="Tavily" />
  <span class="sep">+</span>
  <img class="tf-mark" src="/token-factory-mark.svg" alt="" />
  <span>Nebius Token Factory</span>
</div>

<!--
Notebook: 02_web_search_tools.ipynb
-->

---
class: neb-slide
---

<div class="deck-kicker">The problem</div>
<h1>Competitor research cannot run<br>on <span class="lime-text">frozen knowledge</span></h1>

<div class="problem-layout">
  <div class="problem-stake">
    <div class="eyebrow">Course project</div>
    <h2>A competitor matrix goes stale in weeks</h2>
    <p>Pricing changes. Features ship. Funding lands. Your agent has to fetch current facts — not invent them.</p>
    <ul>
      <li>Who competes with us right now?</li>
      <li>What do they charge this quarter?</li>
      <li>What shipped since the model was trained?</li>
    </ul>
  </div>

  <div class="cutoff-card">
    <div class="eyebrow">Knowledge cutoff</div>
    <div class="cutoff-model">Nemotron 3 Nano</div>
    <div class="cutoff-date">June 25, 2025</div>
    <p>Pre-training data freshness on Hugging Face. After that date, retrieve — don’t guess.</p>
  </div>
</div>

<CourseTakeaway text="If a fact can change after the cutoff, require a URL before you trust the answer." />

<!--
Cutoff caveat (which TF revision): confirm with Alex.
Source: NVIDIA-Nemotron-3-Nano-30B-A3B-Base-BF16 Data Freshness.
-->

---
class: neb-slide
---

<div class="deck-kicker">Why tools?</div>

<div class="hero-statement">
<div class="display">Why does an LLM need<br><span class="lime">web search?</span></div>
<p class="prompt-line">Ask a model (no search): <em>“What were the biggest AI model releases this month?”</em></p>
<div class="grid-2">
<CompareCard
  number="LLM"
  eyebrow="Model knowledge"
  title="Strong reasoning, frozen facts"
  :items="['Excellent language and reasoning', 'Training ends; the world keeps moving', 'Recent releases and news go stale']"
/>
<CompareCard
  number="WEB"
  eyebrow="External evidence"
  title="Current, citable, checkable"
  variant="lime"
  :items="['News, docs, releases, and prices', 'URLs you can verify and cite', 'Fresh context the model can reason over']"
/>
</div>
<CourseTakeaway text="For anything that changes after training, the model needs a retrieval tool — not a longer prompt." />
</div>

<!--
Optional live demo: fail the no-tools prompt, then continue.
-->

---
class: neb-slide
---

<div class="deck-kicker">The solution</div>
<h1>Search finds sources. Extract reads them.</h1>

<div class="grid-2">
  <CompareCard
    number="01"
    eyebrow="Discover"
    title="Search"
    description="Ask a question. Get ranked pages — title, URL, query-relevant snippet, and a relevance score."
    badge="QUERY → SOURCES"
    variant="light"
  />
  <CompareCard
    number="02"
    eyebrow="Read"
    title="Extract"
    description="Pass one or more URLs. Get the cleaned full page as markdown or text."
    badge="URLS → CONTENT"
    variant="lime"
  />
</div>

<CourseTakeaway text="Search first to shortlist. Extract only when the snippet cannot support the claim." />

---
class: neb-slide
---

<div class="deck-kicker">The research pattern</div>
<h1>Two tools. One loop.</h1>

<div class="flow-row pattern-3">
  <ProcessStep v-click number="01" label="Search" title="Discover" description="Find ranked sources for a current question." />
  <div class="flow-arrow" v-click>→</div>
  <ProcessStep v-click number="02" label="Extract" title="Read" description="Load a full page only when the snippet is thin." />
  <div class="flow-arrow" v-click>→</div>
  <ProcessStep v-click number="03" label="Answer" title="Cite" description="Answer from evidence — or search again." />
</div>

<CourseTakeaway v-click text="The model chooses the next step." />

---
class: neb-slide
---

<div class="deck-kicker">Setup</div>
<h1>Sign up for Tavily — free API key in two minutes</h1>

<div class="signup-grid">
  <article class="signup-card">
    <div class="signup-meta"><span>01</span> Open</div>
    <div class="signup-shot">
      <img src="/screenshots/tavily-01-homepage.jpg" alt="Tavily homepage — Try it for free" />
    </div>
    <strong>Go to tavily.com</strong>
    <p>Click <span class="lime-text">Try it for free</span>.</p>
  </article>

  <article class="signup-card">
    <div class="signup-meta"><span>02</span> Sign up</div>
    <div class="signup-shot">
      <img src="/screenshots/tavily-02-signup.jpg" alt="Tavily create account screen" />
    </div>
    <strong>Create an account</strong>
    <p>Email, or continue with Google / GitHub.</p>
  </article>

  <article class="signup-card">
    <div class="signup-meta"><span>03</span> Copy key</div>
    <div class="signup-shot signup-key-panel">
      <div class="key-mock">
        <div class="key-mock-head">Dashboard · API Keys</div>
        <div class="key-mock-row">
          <code>tvly-••••••••••••••••</code>
          <span class="key-mock-copy">Copy</span>
        </div>
        <div class="key-mock-env">
          <div class="key-mock-file">lesson/.env</div>
          <pre>TAVILY_API_KEY=tvly-...</pre>
        </div>
      </div>
    </div>
    <strong>Paste into <code>.env</code></strong>
    <p>1,000 free credits / month — no credit card.</p>
  </article>
</div>

<CourseTakeaway text="Put TAVILY_API_KEY in lesson/.env before you run the notebook. Keys always start with tvly-." />

<!--
Screencast of the Tavily UI can replace or sit beside this in recording.
-->

---
class: neb-slide
---

<div class="deck-kicker">No framework required</div>
<h1>Underneath, every tool is an HTTP call</h1>

<div class="split-code">

```python
response = requests.post(
    "https://api.tavily.com/search",
    headers={"Authorization": f"Bearer {TAVILY_API_KEY}"},
    json={
        "query": "biggest AI model releases this month",
        "search_depth": "advanced",
        "max_results": 5,
        "time_range": "month",
    },
    timeout=30,
)
data = response.json()
```

<div class="api-stack">
  <CodeAsideItem label="Endpoint"><strong>POST</strong> /search</CodeAsideItem>
  <CodeAsideItem label="Send" value="query + runtime parameters" />
  <CodeAsideItem label="Receive" value="Scored results with URLs and snippets" />
  <CodeAsideItem label="Next"><strong>POST</strong> /extract on chosen URLs</CodeAsideItem>
</div>

</div>

<CourseTakeaway text="SDKs cut boilerplate. They do not change the model: request in, structured evidence out." />

---
class: neb-slide
---

<div class="deck-kicker">Structured evidence</div>
<h1>What Search returns to the model</h1>

<div class="result-shell">
  <div class="result-card">
    <span class="score">0.96</span>
    <div class="pill">01 RESULT</div>
    <h2>Latest AI Model Releases — July 2026</h2>
    <div class="url">https://aireleasetracker.com/latest</div>
    <p>Kimi K3 (Jul 16), Muse Spark 1.1 (Jul 9), Grok 4.5 (Jul 8) — a query-focused snippet so the model can skim without loading the full page.</p>
  </div>

  <div class="anatomy-list">
    <div class="anatomy-item"><code>title</code><span>What the page claims to cover</span></div>
    <div class="anatomy-item"><code>url</code><span>What you cite — or pass to Extract</span></div>
    <div class="anatomy-item"><code>content</code><span>Snippet ranked for this query</span></div>
    <div class="anatomy-item"><code>score</code><span>Relative relevance, 0 → 1</span></div>
  </div>
</div>

<CourseTakeaway text="These fields are small enough for context. Full pages wait for Extract — or never load." />

---
class: neb-slide
---

<div class="deck-kicker">From API to tool</div>
<h1>A tool is a function the model can request</h1>

<div class="function-slide">

```python
def internet_search(
    query: str,
    search_depth: str = "advanced",
    max_results: int = 5,
) -> str:
    """Search the web for current, factual sources."""
    data = tavily_client.search(
        query,
        search_depth=search_depth,
        max_results=max_results,
    )
    return format_results(data["results"])


def extract_content(
    urls: list[str],
    query: str | None = None,
) -> str:
    """Read full pages when snippets are not enough."""
    data = tavily_client.extract(
        urls=urls,
        query=query,
        extract_depth="advanced",
        format="markdown",
    )
    return format_extractions(data)
```

<div class="principles">
  <div class="principle">
    <strong>Clear purpose</strong>
    <span>Name and docstring tell the model when to use it.</span>
  </div>
  <div class="principle">
    <strong>Typed inputs</strong>
    <span>Arguments become the schema the model must follow.</span>
  </div>
  <div class="principle">
    <strong>Compact output</strong>
    <span>Return titles, URLs, and evidence — not raw API objects.</span>
  </div>
</div>

</div>

<CourseTakeaway text="Test the function like any other Python. Only then wire it into an agent loop." />

<!--
Notebook: section 3 and format_results.
-->

---
class: neb-slide
---

<div class="deck-kicker">Tool calling</div>
<h1>Same schema pattern — now for Tavily</h1>
<p class="slide-lead">You saw tool calling earlier. Here is Search exposed the same way.</p>

<div class="schema-layout">

<div>

```python
def internet_search(
    query: str,
    search_depth: str = "advanced",
    max_results: int = 5,
) -> str:
    ...
```

<div class="schema-points">
  <div class="schema-point">Your app must call this function directly.</div>
  <div class="schema-point">The model never reads the Python source.</div>
</div>

</div>

<div class="schema-arrow">→</div>

<div>

```json
{
  "type": "function",
  "function": {
    "name": "internet_search",
    "description": "Search the web for current, factual information. Use this first to discover sources.",
    "parameters": {
      "type": "object",
      "properties": {
        "query": { "type": "string" },
        "search_depth": {
          "type": "string",
          "enum": ["basic", "fast", "advanced"]
        },
        "max_results": { "type": "integer" }
      },
      "required": ["query"]
    }
  }
}
```

<div class="schema-points">
  <div class="schema-point"><code>name</code> — which function to invoke</div>
  <div class="schema-point"><code>description</code> — when to choose Search vs Extract</div>
  <div class="schema-point"><code>parameters</code> — what arguments are valid</div>
</div>

</div>

</div>

<CourseTakeaway text="Write the description as policy: use Search first; Extract only when snippets are thin." />

---
class: neb-slide
---

<div class="deck-kicker">Execution boundary</div>
<h1>The model proposes. Your code runs.</h1>

<div class="cycle-entry" v-click>
<span class="cycle-entry-label">01 · User</span>
<span class="cycle-entry-q">What were the biggest AI model releases this month?</span>
</div>

<div class="cycle-ring">
<div class="cycle-node lime" v-click>
<div class="cycle-num">02</div>
<div class="cycle-who">LLM</div>
<div class="cycle-body mono">internet_search(...)</div>
</div>
<div class="cycle-edge" v-click>→</div>
<div class="cycle-node dark" v-click>
<div class="cycle-num">03</div>
<div class="cycle-who">Your Python</div>
<div class="cycle-body">Run <span class="lime-text">TOOLS[name]</span></div>
</div>
<div class="cycle-edge" v-click>→</div>
<div class="cycle-node" v-click>
<div class="cycle-num">04</div>
<div class="cycle-who">Tavily</div>
<div class="cycle-body">URLs + snippets</div>
</div>
<div class="cycle-edge" v-click>→</div>
<div class="cycle-node dark" v-click>
<div class="cycle-num">05</div>
<div class="cycle-who">Your Python</div>
<div class="cycle-body">Append <span class="lime-text">role: tool</span></div>
</div>
<div class="cycle-edge" v-click>→</div>
<div class="cycle-node lime" v-click>
<div class="cycle-num">06</div>
<div class="cycle-who">LLM</div>
<div class="cycle-body">Answer, or loop</div>
</div>
</div>

<div class="cycle-return" v-click>
<span class="cycle-return-arrow">↺</span>
<span>If the model emits more <code>tool_calls</code>, return to step 02 — that is the agent loop.</span>
</div>

<CourseTakeaway v-click text="The LLM never runs Python. It emits a structured request; the application chooses what to execute." />

<!--
Notebook: cells 20–22.
-->

---
class: neb-slide
---

<div class="deck-kicker">Your first agent</div>
<h1>A minimal agent is a control loop</h1>

<div class="loop-layout">

```python
def run_agent(question: str, max_steps: int = 10):
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": question},
    ]
    for step in range(1, max_steps + 1):
        msg = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=AGENT_TOOLS,
        ).choices[0].message
        messages.append(msg.model_dump(exclude_none=True))

        if not msg.tool_calls:
            return msg.content

        for tc in msg.tool_calls:
            args = json.loads(tc.function.arguments)
            result = TOOLS[tc.function.name](**args)
            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": result,
            })
    return "Stopped: reached max_steps."
```

<div class="loop-diagram">
  <div class="loop-steps">
    <div class="loop-step"><span>01</span>Ask the model</div>
    <div class="loop-step"><span>02</span>Execute tools</div>
    <div class="loop-step"><span>03</span>Append results</div>
    <div class="loop-step"><span>04</span>Answer or repeat</div>
  </div>
  <div class="loop-cycle">
    <div class="loop-badge">AGENT LOOP</div>
    <p>Stop when there are no <code>tool_calls</code>, or when <code>max_steps</code> is hit.</p>
  </div>
</div>

</div>

<CourseTakeaway text="This is the loop DeepAgents will wrap next. Frameworks do not replace it." />

<!--
Show ToolTracer in the notebook.
-->

---
class: neb-slide
---

<div class="deck-kicker">Scope of the example</div>
<h1>What this minimal loop still lacks</h1>

<div class="grid-4 failure-grid">
  <div class="card dark">
    <div class="index">01</div>
    <h3>No plan</h3>
    <p>It reacts call-by-call instead of decomposing a hard question up front.</p>
  </div>
  <div class="card dark">
    <div class="index">02</div>
    <h3>Duplicate work</h3>
    <p>Nothing stops a repeated query or a second extract of the same URL.</p>
  </div>
  <div class="card dark">
    <div class="index">03</div>
    <h3>Blind ranking</h3>
    <p>A high score is not the same as an authoritative source.</p>
  </div>
  <div class="card dark">
    <div class="index">04</div>
    <h3>Context bloat</h3>
    <p>Full pages pile into message history until the window is full.</p>
  </div>
</div>

<CourseTakeaway text="Next: Orchestrating deep research — turn this loop into a full search pipeline with DeepAgents." />

---
layout: course-summary
---

<div class="deck-kicker">Summary</div>
<h1>Key ideas from<br><span>this module</span></h1>
<p>Two retrieval tools plus a Python-owned loop — the primitive under competitor research.</p>

<div class="recap-row">
  <SummaryItem number="01" label="Search" detail="Discover sources" />
  <SummaryItem number="02" label="Extract" detail="Read full pages" />
  <SummaryItem number="03" label="Schema" detail="Expose the tool" />
  <SummaryItem number="04" label="Loop" detail="Call until done" />
</div>

::footer::

NEXT · <code>02_web_search_tools.ipynb</code> · THEN ORCHESTRATING DEEP RESEARCH

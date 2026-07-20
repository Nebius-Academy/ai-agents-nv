---
theme: nebius-agents
title: Giving an LLM the Web
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
<p>Tavily retrieves current sources. Token Factory runs the model. Plain Python decides when to call each tool.</p>

::provider::

<div class="cover-provider-lockup">
  <img class="tavily" src="/tavily-logo.svg" alt="Tavily" />
  <span class="sep">+</span>
  <img class="tf-mark" src="/token-factory-mark.svg" alt="" />
  <span>Nebius Token Factory</span>
</div>

<!--
Open with the outcome: by the end, a small research agent that searches, reads, and cites fresh sources.

Notebook: 02_web_search_tools.ipynb
-->

---
class: neb-slide
---

<div class="deck-kicker">Why tools?</div>

<div class="hero-statement">
<div class="display">Why does an LLM need<br><span class="lime">web search?</span></div>
<div class="grid-2">
<CompareCard
  number="LLM"
  eyebrow="Model knowledge"
  title="Strong reasoning, frozen facts"
  :items="['Excellent language and reasoning', 'Cutoff ends at training time', 'Recent events can be guessed or stale']"
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
Hook with a current question: “What were the biggest AI advancements this week?” A base model cannot answer that reliably without the web.
-->

---
class: neb-slide
---

<div class="deck-kicker">Tavily primitives</div>
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
    description="Pass one or more URLs. Get the cleaned full page as markdown or text, ready for deeper reading."
    badge="URLS → CONTENT"
    variant="lime"
  />
</div>

<CourseTakeaway text="Search first to shortlist. Extract only when the snippet is not enough to support a claim." />


<!--
Search = source discovery. Extract = source reading. Snippets often suffice; extract when details or caveats live deeper in the page.
-->

---
class: neb-slide
---

<div class="deck-kicker">The research pattern</div>
<h1>Five decisions every research agent makes</h1>

<div class="flow-row">
  <ProcessStep v-click number="01" label="Question" title="Frame" description="What must be current and verifiable?" />
  <div class="flow-arrow" v-click>→</div>
  <ProcessStep v-click number="02" label="Search" title="Discover" description="Cast a wide net for useful sources." />
  <div class="flow-arrow" v-click>→</div>
  <ProcessStep v-click number="03" label="Rank" title="Shortlist" description="Keep the strongest, most relevant pages." />
  <div class="flow-arrow" v-click>→</div>
  <ProcessStep v-click number="04" label="Extract" title="Read" description="Fetch full pages only when needed." />
  <div class="flow-arrow" v-click>→</div>
  <ProcessStep v-click number="05" label="Answer" title="Cite" description="Synthesize from evidence; cite every claim." />
</div>

<CourseTakeaway v-click text="The agent decides when to search again, when to extract, and when it has enough to answer." />


<!--
Reveal one stage at a time. Search and extract are separate decisions — that is the key conceptual move.
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
        "query": "AI advancements this week",
        "search_depth": "advanced",
        "max_results": 5,
        "time_range": "week",
    },
    timeout=30,
)
data = response.json()
```

<div class="api-stack">
  <CodeAsideItem label="Endpoint"><strong>POST</strong> /search</CodeAsideItem>
  <CodeAsideItem label="Send" value="query · depth · recency · limit" />
  <CodeAsideItem label="Receive" value="title · url · content · score" />
  <CodeAsideItem label="Next"><strong>POST</strong> /extract on chosen URLs</CodeAsideItem>
</div>

</div>

<CourseTakeaway text="SDKs cut boilerplate. They do not change the mental model: request in, structured evidence out." />


<!--
Notebook: raw HTTP Search and Extract cells (sections 1, cells 5–12). Point at Authorization, JSON body, and response fields.
-->

---
class: neb-slide
---

<div class="deck-kicker">Structured evidence</div>
<h1>What Search returns to the model</h1>

<div class="result-shell">
  <div class="result-card">
    <span class="score">0.94</span>
    <div class="pill">RESULT 01</div>
    <h2>Lab ships new open model for agentic workflows</h2>
    <div class="url">https://news.example.com/ai/model-release</div>
    <p>A query-focused snippet — navigation, ads, and page chrome already stripped — so the model can skim evidence without ingesting the whole page.</p>
  </div>

  <div class="anatomy-list">
    <div class="anatomy-item"><code>title</code><span>What the page claims to cover</span></div>
    <div class="anatomy-item"><code>url</code><span>What you cite — or pass to Extract</span></div>
    <div class="anatomy-item"><code>content</code><span>Snippet ranked for this query</span></div>
    <div class="anatomy-item"><code>score</code><span>Relative relevance, 0 → 1</span></div>
  </div>
</div>

<CourseTakeaway text="These fields are small enough to put in context. Full pages wait for Extract — or they never get loaded." />


<!--
Contrast Search content with Extract raw_content. Do not dump full articles onto slides.
-->

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
    <span>Name and docstring tell the model when the tool helps.</span>
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
Notebook: section 3 and format_results. Emphasize unit-testability before any LLM is involved.
-->

---
class: neb-slide
---

<div class="deck-kicker">Tool calling</div>
<h1>The schema is how the model sees your function</h1>

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
  <div class="schema-point">Your app can call this directly.</div>
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
  <div class="schema-point"><code>description</code> — when to choose it</div>
  <div class="schema-point"><code>parameters</code> — what arguments are valid</div>
</div>

</div>

</div>

<CourseTakeaway text="Write the description as agent policy: “use Search first; Extract only when snippets are thin.”" />


<!--
Description is behavior. “Use this first to discover sources” separates Search from Extract.
-->

---
class: neb-slide
---

<div class="deck-kicker">Execution boundary</div>
<h1>The model proposes. Your code disposes.</h1>

<div class="turn-grid">
  <div class="turn-step" v-click>
    <div class="turn-num">01</div>
    <div class="turn-who">User</div>
    <div class="turn-body">What were the biggest AI advancements this week?</div>
  </div>
  <div class="turn-step lime" v-click>
    <div class="turn-num">02</div>
    <div class="turn-who">LLM</div>
    <div class="turn-body mono">internet_search(query="AI advancements this week")</div>
  </div>
  <div class="turn-step dark" v-click>
    <div class="turn-num">03</div>
    <div class="turn-who">Your Python</div>
    <div class="turn-body">Parse args → <span class="lime-text">TOOLS[name](**args)</span></div>
  </div>
  <div class="turn-step" v-click>
    <div class="turn-num">04</div>
    <div class="turn-who">Tavily</div>
    <div class="turn-body">Ranked results with URLs and snippets</div>
  </div>
  <div class="turn-step dark" v-click>
    <div class="turn-num">05</div>
    <div class="turn-who">Your Python</div>
    <div class="turn-body">Append a <span class="lime-text">role: tool</span> message with the result</div>
  </div>
  <div class="turn-step lime" v-click>
    <div class="turn-num">06</div>
    <div class="turn-who">LLM</div>
    <div class="turn-body">Search again, extract a page, or answer with citations</div>
  </div>
</div>

<CourseTakeaway v-click text="The LLM never runs Python. It emits a structured request; the application chooses what to execute." />


<!--
Notebook: single tool-call example (sections 4, cells 20–22). Show empty content + populated tool_calls.
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

<CourseTakeaway text="Frameworks wrap this loop. They do not replace it." />


<!--
Notebook: final implementation (sections 5, cells 24–26). Walk: model call → stop check → execute → append.
-->

---
class: neb-slide
---

<div class="deck-kicker">Observability</div>
<h1>Every run should leave a trace</h1>

<div class="trace-line">
  <div class="trace-event" v-click>
    <div class="num">01 · SEARCH</div>
    <h3>Cast a net</h3>
    <p><span class="mono">query:</span><br>“AI advancements this week”</p>
  </div>
  <div class="trace-arrow" v-click>→</div>
  <div class="trace-event" v-click>
    <div class="num">02 · SEARCH</div>
    <h3>Narrow the focus</h3>
    <p><span class="mono">query:</span><br>“new AI model releases July 2026”</p>
  </div>
  <div class="trace-arrow" v-click>→</div>
  <div class="trace-event" v-click>
    <div class="num">03 · EXTRACT</div>
    <h3>Read the best pages</h3>
    <p><span class="mono">urls:</span><br>two strongest primary sources</p>
  </div>
  <div class="trace-arrow" v-click>→</div>
  <div class="trace-event final" v-click>
    <div class="num">04 · ANSWER</div>
    <h3>Cite every claim</h3>
    <p>Grounded synthesis with a URL on each factual statement.</p>
  </div>
</div>

<CourseTakeaway v-click text="A stored trace shows tool choice, arguments, evidence, and why the loop stopped — after the run is over." />


<!--
Show ToolTracer.events and ToolTracer.show() in the notebook. Tracing is how you debug tool choice.
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
    <p>A high score is not the same as an authoritative or trustworthy source.</p>
  </div>
  <div class="card dark">
    <div class="index">04</div>
    <h3>Context bloat</h3>
    <p>Full pages pile into message history until the window is full.</p>
  </div>
</div>

<CourseTakeaway text="Next module: query planning, deduplication, source filtering, and summarization." />


<!--
These gaps motivate the search pipeline — not failures of tool calling, but missing orchestration.
-->

---
layout: course-summary
---

<div class="deck-kicker">Summary</div>
<h1>Key ideas from<br><span>this module</span></h1>
<p>Two retrieval tools plus an application-owned loop turn a frozen LLM into a research agent that can cite the live web.</p>

<div class="recap-row">
  <SummaryItem number="01" label="Search" detail="Discover sources" />
  <SummaryItem number="02" label="Extract" detail="Read full pages" />
  <SummaryItem number="03" label="Schema" detail="Expose the tool" />
  <SummaryItem number="04" label="Loop" detail="Call until done" />
</div>

::footer::

NEXT · BUILDING A SEARCH PIPELINE

<!--
Close on the transferable idea: an agent is a model inside an application-controlled loop; tools supply fresh evidence.
-->

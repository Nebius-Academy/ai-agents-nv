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
<h1>Web search tools<br>and a first <span>agent loop</span></h1>
<p>Using Tavily and plain Python to give an LLM access to current, citable information.</p>

::provider::

<div class="cover-provider-lockup">
  <img class="tavily" src="/tavily-logo.svg" alt="Tavily" />
  <span class="sep">+</span>
  <img class="tf-mark" src="/token-factory-mark.svg" alt="" />
  <span>Nebius Token Factory</span>
</div>

<!--
Open with the outcome rather than setup details: by the end, we will have a small research agent that searches, reads, and cites fresh sources.

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
  title="Useful, but bounded in time"
  :items="['Strong reasoning and language skills', 'Knowledge ends at training time', 'Answers about recent events may be stale']"
/>
<CompareCard
  number="WEB"
  eyebrow="External information"
  title="Current and sourceable"
  variant="lime"
  :items="['News, releases, prices, and documentation', 'Evidence from identifiable sources', 'Fresh context for the model to reason over']"
/>
</div>
<CourseTakeaway text="For questions about what is happening now, the model needs a way to retrieve external evidence." />
</div>


<!--
Use a current question as the hook: “What were the biggest AI advancements this week?” A base model cannot know this reliably without external information.
-->

---
class: neb-slide
---

<div class="deck-kicker">Tavily primitives</div>
<h1>Search and Extract serve different purposes</h1>

<div class="grid-2">
  <CompareCard
    number="01"
    eyebrow="Discover"
    title="Search"
    description="Start with a question. Get ranked pages with titles, URLs, relevant snippets, and relevance scores."
    badge="QUERY → SOURCES"
    variant="light"
  />
  <CompareCard
    number="02"
    eyebrow="Read"
    title="Extract"
    description="Start with one or more URLs. Get the full cleaned page content as markdown or text."
    badge="URLS → CONTENT"
    variant="lime"
  />
</div>

<CourseTakeaway text="Use Search to discover candidate sources; use Extract when the snippets do not provide enough detail." />


<!--
Search is source discovery. Extract is source reading. Search snippets are often enough for quick answers; extraction matters when details, caveats, or exact claims live deeper in the page.
-->

---
class: neb-slide
---

<div class="deck-kicker">The research pattern</div>
<h1>A simple research workflow</h1>

<div class="flow-row">
  <ProcessStep v-click number="01" label="Question" title="Define" description="What information must be current and verifiable?" />
  <div class="flow-arrow" v-click>→</div>
  <ProcessStep v-click number="02" label="Search" title="Discover" description="Find a broad set of potentially useful sources." />
  <div class="flow-arrow" v-click>→</div>
  <ProcessStep v-click number="03" label="Rank" title="Shortlist" description="Keep the strongest and most relevant pages." />
  <div class="flow-arrow" v-click>→</div>
  <ProcessStep v-click number="04" label="Extract" title="Read" description="Pull full content only where snippets are insufficient." />
  <div class="flow-arrow" v-click>→</div>
  <ProcessStep v-click number="05" label="Answer" title="Synthesize" description="Reason over evidence and cite every factual claim." />
</div>

<CourseTakeaway v-click text="Our agent will decide when to repeat the middle of this sequence." />


<!--
Reveal the pipeline one stage at a time. The important conceptual move is that search and extraction are separate decisions.
-->

---
class: neb-slide
---

<div class="deck-kicker">No framework required</div>
<h1>Underneath, each tool is an HTTP request</h1>

<div class="split-code">

```python
response = requests.post(
    "https://api.tavily.com/search",
    headers={
        "Authorization": f"Bearer {TAVILY_API_KEY}"
    },
    json={
        "query": "advancements in AI this week",
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
  <CodeAsideItem label="Input" value="query · depth · recency · limit" />
  <CodeAsideItem label="Output" value="title · url · content · score" />
  <CodeAsideItem label="Then"><strong>POST</strong> /extract for selected URLs</CodeAsideItem>
</div>

</div>

<CourseTakeaway text="Client libraries reduce boilerplate. They do not change the mental model." />


<!--
Notebook handoff: run the raw HTTP Search and Extract cells (sections 1, cells 5–12). Point out the Authorization header, JSON body, and response fields. API key setup should happen before recording or in a short aside.
-->

---
class: neb-slide
---

<div class="deck-kicker">Structured evidence</div>
<h1>What comes back from Search?</h1>

<div class="result-shell">
  <div class="result-card">
    <span class="score">0.94</span>
    <div class="pill">RESULT 01</div>
    <h2>New model release advances agentic reasoning</h2>
    <div class="url">https://example.com/research/model-release</div>
    <p>A clean, relevant snippet appears here — already stripped of navigation, ads, and unrelated page chrome...</p>
  </div>

  <div class="anatomy-list">
    <div class="anatomy-item"><code>title</code><span>What the page is about</span></div>
    <div class="anatomy-item"><code>url</code><span>The source we can cite or extract</span></div>
    <div class="anatomy-item"><code>content</code><span>Relevant text for the current query</span></div>
    <div class="anatomy-item"><code>score</code><span>Relative relevance from 0 to 1</span></div>
  </div>
</div>

<div class="takeaway">Structured search results are compact enough to place directly into the model’s working context.</div>


<!--
Contrast the short Search content snippet with Extract's raw_content field, which contains the cleaned full page. Avoid dumping complete articles into slides.
-->

---
class: neb-slide
---

<div class="deck-kicker">From API to tool</div>
<h1>A “tool” is just a function</h1>

<div class="function-slide">

```python
def internet_search(
    query: str,
    search_depth: str = "advanced",
    max_results: int = 5,
) -> str:
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
    <span>The name and docstring communicate when the function is useful.</span>
  </div>
  <div class="principle">
    <strong>Predictable inputs</strong>
    <span>Typed arguments become constraints the model can follow.</span>
  </div>
  <div class="principle">
    <strong>Model-friendly output</strong>
    <span>Return compact text with titles, URLs, and evidence—not noisy objects.</span>
  </div>
</div>

</div>

<div class="takeaway">The function remains independently testable; later, an agent framework can orchestrate when it is called.</div>


<!--
Notebook handoff: show section 3 and the format_results helper. Emphasize that the function can be tested normally before an LLM is involved.
-->

---
class: neb-slide
---

<div class="deck-kicker">Tool calling</div>
<h1>The schema makes a function visible to the model</h1>

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
  <div class="schema-point">Your code can execute this function.</div>
  <div class="schema-point">The model cannot inspect Python directly.</div>
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
        }
      },
      "required": ["query"]
    }
  }
}
```

<div class="schema-points">
  <div class="schema-point"><code>name</code> chooses the function.</div>
  <div class="schema-point"><code>description</code> teaches when to use it.</div>
  <div class="schema-point"><code>parameters</code> constrain valid arguments.</div>
</div>

</div>

</div>


<!--
The description is part of the agent behavior. “Use this first to discover sources” helps the model distinguish Search from Extract.
-->

---
class: neb-slide
---

<div class="deck-kicker">Execution boundary</div>
<h1>The model requests; the application executes</h1>

<div class="sequence">
  <div class="lane">
    <div class="lane-title">User</div>
    <div class="message">
      <div class="n">1 · Question</div>
      What were the biggest AI advancements this week?
    </div>
  </div>

  <div class="lane">
    <div class="lane-title">LLM</div>
    <div class="message lime" v-click>
      <div class="n">2 · Tool request</div>
      internet_search({<br>&nbsp;&nbsp;"query": "AI advancements this week"<br>})
    </div>
    <div class="message" v-click>
      <div class="n">6 · Continue</div>
      Search again, extract a page, or produce the final answer.
    </div>
  </div>

  <div class="lane">
    <div class="lane-title">Your Python</div>
    <div class="message dark" v-click>
      <div class="n">3 · Execute</div>
      Parse arguments and call <span class="lime-text">TOOLS[name](**args)</span>
    </div>
    <div class="message dark" v-click>
      <div class="n">5 · Append</div>
      Add a <span class="lime-text">role: tool</span> message with the result.
    </div>
  </div>

  <div class="lane">
    <div class="lane-title">Tavily</div>
    <div class="message" v-click>
      <div class="n">4 · Evidence</div>
      Ranked results with URLs and relevant content.
    </div>
  </div>
</div>

<div class="takeaway">The LLM does not execute Python. It emits a structured request, and the application decides how to handle it.</div>


<!--
Notebook handoff: run the single tool-call example in sections 4 and the manual turn in cells 20–22. Show that assistant_msg.content is often empty while tool_calls is populated.
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
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=AGENT_TOOLS,
        )
        msg = response.choices[0].message
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
  <div class="orbit-node one">Ask the model</div>
  <div class="orbit-node two">Execute tools</div>
  <div class="orbit-node three">Append results</div>
  <div class="orbit-node four">Answer or repeat</div>
  <div class="orbit-arrow a">↘</div>
  <div class="orbit-arrow b">↙</div>
  <div class="orbit-arrow c">↖</div>
  <div class="orbit-arrow d">↗</div>
  <div class="loop-center">AGENT<br>LOOP</div>
</div>

</div>

<div class="takeaway">Agent frameworks add capabilities around this loop, but the basic control flow remains the same.</div>


<!--
Notebook handoff: run the final implementation in sections 5, cells 24–26. Walk the loop in exactly this order: model call, termination check, tool execution, tool-result append.
-->

---
class: neb-slide
---

<div class="deck-kicker">Observability</div>
<h1>A run should leave a trace</h1>

<div class="trace-line">
  <div class="trace-event" v-click>
    <div class="num">01 · STEP 1</div>
    <h3>Search</h3>
    <p><span class="mono">query:</span><br>“AI advancements this week”</p>
  </div>
  <div class="trace-arrow" v-click>→</div>
  <div class="trace-event" v-click>
    <div class="num">02 · STEP 2</div>
    <h3>Search again</h3>
    <p><span class="mono">query:</span><br>“new AI model releases July 2026”</p>
  </div>
  <div class="trace-arrow" v-click>→</div>
  <div class="trace-event" v-click>
    <div class="num">03 · STEP 3</div>
    <h3>Extract</h3>
    <p><span class="mono">urls:</span><br>the two strongest primary sources</p>
  </div>
  <div class="trace-arrow" v-click>→</div>
  <div class="trace-event final" v-click>
    <div class="num">04 · STEP 4</div>
    <h3>Final answer</h3>
    <p>Grounded synthesis with a URL attached to every factual claim.</p>
  </div>
</div>

<div class="takeaway" v-click>A stored trace lets us inspect tool choice, arguments, returned evidence, and stopping behavior after the run.</div>


<!--
Show ToolTracer.events and ToolTracer.show() in the notebook. Tracing is how we debug which tool was chosen, with which arguments, and what evidence came back.
-->

---
class: neb-slide
---

<div class="deck-kicker">Scope of the example</div>
<h1>Limitations of the minimal loop</h1>

<div class="grid-4 failure-grid">
  <div class="card dark">
    <div class="index">01</div>
    <h3>No planning</h3>
    <p>It reacts one call at a time instead of decomposing a complex question.</p>
  </div>
  <div class="card dark">
    <div class="index">02</div>
    <h3>Redundant calls</h3>
    <p>Nothing prevents repeating a query or extracting the same URL twice.</p>
  </div>
  <div class="card dark">
    <div class="index">03</div>
    <h3>Weak source control</h3>
    <p>High ranking does not automatically mean authoritative or trustworthy.</p>
  </div>
  <div class="card dark">
    <div class="index">04</div>
    <h3>Context bloat</h3>
    <p>Full pages accumulate in the message history until the context window fills.</p>
  </div>
</div>

<div class="takeaway">Next: query planning, deduplication, source filtering, and summarization.</div>


<!--
These limitations motivate the next chapter's search pipeline and eventually the competitor-research agent. Do not frame them as failures of tool calling; they are missing orchestration layers.
-->

---
layout: course-summary
---

<div class="deck-kicker">Summary</div>
<h1>Key ideas from<br><span>this module</span></h1>
<p>We used two retrieval tools and a small application-controlled loop to produce answers grounded in current web sources.</p>

<div class="recap-row">
  <SummaryItem number="01" label="Search" />
  <SummaryItem number="02" label="Extract" />
  <SummaryItem number="03" label="Tool call" />
  <SummaryItem number="04" label="Loop" />
</div>

::footer::

NEXT · BUILDING A SEARCH PIPELINE

<!--
Close by restating the transferable idea: an agent is a model inside an application-controlled loop, with tools providing fresh evidence.
-->

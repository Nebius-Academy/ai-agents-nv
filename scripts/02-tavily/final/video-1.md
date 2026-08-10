# Video 1 — General intro to web search

- **Module:** 02 — Give an LLM the web
- **Length:** 4–6 min

---

**[Slide 1 — title]**

Hi, I'm Lakshya, a Forward Deployed Engineer at Tavily.

In this video, we'll look at why an LLM needs access to the live web, and how web search turns a model with frozen knowledge into one that can answer questions about what's happening right now.

We'll cover the limits of a model's training data, the two tools that connect it to the web — Search and Extract — and the agent loop that ties them together.

By the end of this video, you'll be able to identify which questions need live web retrieval, and describe the search-and-extract pattern that powers a research agent.

---

**[Slide 2 — Competitor research cannot run on frozen knowledge]**

Why does this matter? Let's make it concrete with the project you'll build in this course: a **competitor research agent**. You give it a company name, and it tracks what's happening with them — pricing changes, product launches, funding rounds — and writes up a report with sources.

Now here's the problem. Pricing changes. Features ship. Funding lands. Anything the agent builds from the model's memory alone goes stale in weeks.

The model we're using — Nemotron — has a knowledge cutoff of June 2025, more than a year ago. The model does not have access to any information after that date. If we ask the model about the weather in Toronto for example, it will not be able to answer that accurately.

Apply that to our question — *What were the advancements in AI this week?* Can the model answer that from memory? No. It needs the web to get the latest information.

---

**[Slide 3 — The model reasons. The web supplies the evidence.]**

Here's the mental model I want you to keep for the rest of the course.

On one side: the Large Language Model (LLM). It's a reasoning engine. It's great at planning, comparing, and synthesizing — but only over what it can see. It cannot fetch what changed since training.

On the other side: the web. Current news, docs, releases, prices. Fresh context that happens as the world moves.

Division of labor: reasoning is the model's job; current facts are the web's job. Tools connect the two.

---

**[Slide 4 — Search finds sources. Extract reads them.]**

So how do we get that evidence? Two tools. Two jobs.

First: Search. You ask a question. You get back ranked results, with content and metadata, optimized for the LLM to consume.

Second: Extract. You already have one or more URLs. Extract pulls the cleaned full page as markdown. It allows the LLM to choose what to read further.

For example, your can use search first to narrow down a set of articles and then extract the most important ones.

---

**[Slide 5 — Two tools. One loop.]**

Now put them together. This is the research pattern.

You Search. Then the model decides: is the evidence enough? If yes — answer with citations. If not — pick the next step. Extract a promising URL, or Search again. Then decide once more.

Any step can repeat, in any order.

Choosing the next step — and repeating it — is what makes this an agent loop, not a predefined pipeline.

---

**[Summary / closing]**

To recap: in this video, you learned why a model's memory alone can't answer questions about the present, and how web tools fix that.

You saw the division of labor — the model reasons, the web supplies evidence — the two tools, Search and Extract, and the agent loop that lets the model choose its next step.

Together, these give you a repeatable pattern: when a question needs facts the model was never trained on — this week's news, current pricing, anything after the cutoff — don't trust memory. Go get evidence from the web.

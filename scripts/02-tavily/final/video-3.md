# Video 3 — Search and Extract as tools

- **Module:** 02 — Give an LLM the web
- **Length:** 4–6 min

---
**[Talking head / notebook open]**

Every tool an agent uses is, at its core, just an HTTP call — request in, response out. In this video, we'll look at Tavily's Search and Extract endpoints and how to turn them into plain Python tools.

We'll cover calling Search over raw HTTP, switching to the Python client, reading a full page with Extract, and wrapping both as testable functions — no language model involved yet.

By the end of this video, you'll be able to implement Search and Extract as Python functions and verify they work on their own.

We'll use one running question throughout: *What were the advancements in AI this week?*

---

**[Notebook §1 — Search over HTTP]**

First, call Search by hand with `requests`.

We POST to `https://api.tavily.com/search`, put the API key in an Authorization header, and send a JSON body with our query.

A few parameters that matter here are:

- `query` is required.
- `search_depth` — we'll use `advanced` for deeper results.
- `max_results` — how many pages to return.
- `time_range` set to `week`, because our question is about *this week*.
- `include_answer` is set to `True` to get the a Tavily-generated answer to the question.

Run the cell. You should get a JSON response back.

One note before we look inside: since this is a live search for information from *this week*, your exact results will depend on when you run the notebook. Here, I want you to focus on the response structure, rather than the exact results.

---

**[Notebook — print results]**

Look at what comes back. The important part is `results` — a ranked list.

Each result has a title, a URL, a content snippet, and a relevance score. That snippet is the key idea: it's short, relevant to the query, and sized so an LLM can read it without loading the full page.

---

**[Notebook §2 — Python client + Extract]**

Writing the HTTP call by hand is great once. In practice, we use the Python client — same parameters, less boilerplate.

Run Search again through `TavilyClient`. Same question, same shape of results.

Now take the top URL and call Extract on it. This is the two-step research pattern: Search to shortlist, Extract to read in full.

Extract returns the cleaned page as markdown. This is a much longer and dense output that the model can use.

---

**[Notebook §3 — wrap as tool functions]**

Last step: wrap both endpoints as normal Python functions.

`internet_search` takes a query and returns a compact string of titles, URLs, and snippets. `extract_content` takes a list of URLs and returns the page text.

Test both functions right here, like any other Python. If they print sensible output, the tools work — before any model touches them.

---

**[Closing]**

To recap: in this video, you learned how to call Search over HTTP, switch to the Python client, read a full page with Extract, and wrap both endpoints as testable Python functions.

You now have two working tools — tested before any model touches them — that you can hand to an LLM.

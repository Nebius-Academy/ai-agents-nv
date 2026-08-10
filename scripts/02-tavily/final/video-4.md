# Video 4 — The agentic loop: your first agent

- **Module:** 02 — Give an LLM the web
- **Length:** 4–6 min

---

**[Talking head / notebook open]**

A function sitting in a notebook isn't an agent — something has to decide when to call it. In this video, we hand that decision to the model and build a loop that executes its requests until it can answer.

We'll cover describing tools to the model with JSON schemas, running one tool-call turn by hand, and wrapping it all in an agent loop.

By the end of this video, you'll have a small research agent that answers questions with real, cited sources.

---

**[Notebook §4 — tool schemas + Nebius client]**

First, describe the tools to the model.

Here, an important distinction is that the model never sees the actual logic of the functions we defined.

The model is only provided with a JSON schema of the functions — the name, a description, and the parameters.

Look at the descriptions carefully.

- For Search we say: use this first to discover sources.
- For Extract we say: use after search when a snippet is not enough.

We'll drive the model through Nebius Token Factory, using the OpenAI-compatible client and a Nemotron model.

---

**[Notebook §4 — one turn by hand]**

Now let's send our question with both tools attached.

The question here is: *What were the advancements in AI this week?*

Watch what comes back. The model doesn't answer yet. It returns a tool call — please run `internet_search` with these arguments.

That's the core contract: the model proposes, your code runs. The model never executes Python itself in this case.

So we do three things.

1. Record the model's request in the conversation.
2. Run the function and get the result.
3. Append the result as a tool message, tied to the same tool call id from step #1.
4. Ask the model again.

Now it can see the search results. It may answer — or request another tool. Either way, you've seen one full turn of the loop, step-by-step.

---

**[Notebook §5 — run_agent]**

Wrap that in a loop and you have an agent.

`run_agent` is a `for` loop over a growing list of messages. Ask the model. If it returns tool calls — execute them, append the results, loop again. If it returns plain text — that's the answer; stop.

We also set a `max_steps` guard, so we ensure that the loop doesn't run indefinitely.

Run it on our question, with verbose printing on.

Watch the trace. The model searches. It judges whether the snippets are enough. If not, it extracts a promising URL. Then it answers — with citations.

---

**[Closing]**

To recap: in this video, you built your first agent. You described Search and Extract as JSON schemas, ran one tool-call turn by hand to see the contract — the model proposes, your code runs — and wrapped it in a loop with a safety guard.

You now have a repeatable approach for turning any set of tested functions into an agent that decides for itself when to use them.

# Video 2 — Exploring the Tavily platform: account and API key

- **Module:** 02 — Give an LLM the web
- **Length:** 4–6 min

---

**[Talking head / title]**

Let's take a closer look at the Tavily platform and how to set it up for your project.

Before we can make any web search calls, we need credentials. In this video, we'll create a Tavily account, generate an API key, and add it to your project's `.env` file so the notebook can run.

This is a two-minute setup. You do it once. By the end, you'll have a working API key and a verified project configuration, ready to make real search calls.

---

**[Screen: tavily.com]**

Go to tavily.com and click Try it for free. Sign up with email, Google, or GitHub — whichever you prefer.

The free tier gives you 1,000 credits a month, enough to try out the course.

Once you're in, you're looking at the dashboard. This is where your keys, usage, and logs live.

---

**[Screen: Dashboard → API Keys]**

Open API Keys and copy a key.

Every Search and Extract call we make later authenticates with this key. Treat it like a password — don't commit it to git, don't paste it into chat.

Quick sanity check: the key should start with `tvly-`. If it does, you copied the right thing.

---

**[Screen: code editor — lesson/.env]**

Now open the project. Copy `.env.example` to a new file named `.env`, and paste your key:

`TAVILY_API_KEY=tvly-...`

The notebook loads keys from this file — we never hardcode them in code.

---

**[Screen: notebook — key-check cell]**

Run the key-check cell. If this passes, both environment variables have been loaded — the first API call will confirm that the keys are valid.

To recap: in this video, you created a Tavily account, generated an API key, and stored it in your project's `.env` file — then confirmed both keys are loaded with the key-check cell. You now have a repeatable setup process you can reuse for any project that needs web search.
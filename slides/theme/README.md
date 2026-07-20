# Nebius AI Agents Slidev theme

Reusable visual system, layouts, and teaching components for the course decks.

## Install in a deck

Add the local theme package to the deck's `package.json`:

```json
{
  "devDependencies": {
    "slidev-theme-nebius-agents": "file:../theme"
  }
}
```

Then select it in `slides.md`:

```yaml
---
theme: nebius-agents
title: Module title
---
```

The theme supplies the dark Nebius palette, typography, spacing, code treatment, cards, cover/summary layouts, and reusable Vue components. Keep only lesson-specific diagrams in the deck's own `style.css`.

## Standard layouts

### Course cover

```md
---
layout: course-cover
---

<div class="deck-kicker">AI Agents · Module 03</div>
<h1>Build a <span>search pipeline</span></h1>
<p>A short outcome-oriented description.</p>

::provider::

<div class="cover-provider-lockup">Provider lockup</div>
```

### Course summary

```md
---
layout: course-summary
---

<div class="deck-kicker">Summary</div>
<h1>Key ideas from<br><span>this module</span></h1>
<p>One-sentence recap.</p>

<div class="recap-row">
  <SummaryItem number="01" label="Plan" />
  <SummaryItem number="02" label="Search" />
</div>

::footer::

NEXT · MODULE NAME
```

## Reusable components

### Header and takeaway

```md
<CourseHeader kicker="The research pattern" title="A simple workflow" />
<CourseTakeaway text="The one sentence learners should retain." />
```

### Comparison card

```md
<div class="grid-2">
  <CompareCard
    number="01"
    eyebrow="Discover"
    title="Search"
    description="Find candidate sources."
    badge="QUERY → SOURCES"
    variant="light"
  />
  <CompareCard
    number="02"
    eyebrow="Read"
    title="Extract"
    description="Retrieve full page content."
    badge="URLS → CONTENT"
    variant="lime"
  />
</div>
```

Variants are `dark`, `light`, and `lime`. Cards also accept an `items` array for short bullet comparisons.

### Process step

```md
<div class="flow-row">
  <ProcessStep number="01" label="Question" title="Define" description="Clarify what must be current." />
  <div class="flow-arrow">→</div>
  <ProcessStep number="02" label="Search" title="Discover" description="Find candidate sources." />
</div>
```

### Code-side annotation

```md
<div class="api-stack">
  <CodeAsideItem label="Endpoint"><strong>POST</strong> /search</CodeAsideItem>
  <CodeAsideItem label="Input" value="query · depth · limit" />
</div>
```

## Shared primitives

- Layout: `grid-2`, `grid-3`, `grid-4`
- Surfaces: `card`, `card light`, `card lime`
- Labels: `deck-kicker`, `pill`, `pill ghost`
- Emphasis: `takeaway`, `lime-text`, `muted`, `mono`
- Templates: `course-cover`, `course-summary`

## Design rules

1. One message per slide; state it explicitly in the takeaway.
2. Prefer 2–4 large elements over dense lists.
3. Keep body copy at the shared scale; only reduce code locally when necessary.
4. Use lime for orientation and emphasis, not large text blocks.
5. Put reusable colors, spacing, type, cards, and chrome in this theme.
6. Put content-specific diagrams and visualizations in the deck stylesheet.
7. Use `global-top.vue` and `global-bottom.vue` for module chrome; never number slides manually.
8. Build and export after layout changes:

```bash
cd slides/<deck>
pnpm install
pnpm run build
pnpm run export:png
```

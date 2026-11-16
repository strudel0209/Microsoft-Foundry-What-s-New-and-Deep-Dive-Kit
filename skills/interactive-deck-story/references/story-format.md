# Story format 1.0 (`story.json`)

One JSON file holds all content of one interactive story page. The engine never changes per
deck; only this file (and, rarely, a topic renderer file) does. Start from
`examples/template/story.json`; the full worked example is
`examples/latency-optimization/story.json` (+ `renderers.js`).

The stage is a fixed 1600 × 900 canvas scaled to the window. Every scene type has a fixed
layout, so **counts and text lengths are limited** — `story_check.py` enforces the counts and
warns on lengths; `render_check.js` measures real overflow.

## Top level

| Key | Content |
|-----|---------|
| `meta` | page-level text (below) |
| `strategies` | the lenses of the main decision tree: `{key: {label, line, color}}` — 3 to 5 keys plus optional `measure`; colours from the palette below |
| `sections` | chapter groups: `[{id, num, name}]`; `num` `"00"` is the opening group (title, problem, main tree) |
| `sources` | link table: `{key: {label, url}}` — Microsoft Learn (`/en-us/`) and public GitHub only; scenes cite keys |
| `scenes` | ordered list of scenes; the story order is the list order |

### `meta`

| Key | Use |
|-----|-----|
| `lang` | `"en"` |
| `brand` | top-left label, e.g. `"Latency optimization · Microsoft Foundry"` |
| `title`, `subtitle`, `kicker` | title scene; `subtitle` is also the page description |
| `footer` | bottom-right of every scene, e.g. `"Latency optimization · November 2026"` |
| `edition`, `checked` | deck edition (`"November 2026"`) and the date facts were checked (`"14 November 2026"`) |
| `deck` | exact kit file name of the paired deck |
| `previewNote` | `"* preview — no service level agreement."` (shown on scenes with `preview: true`) |
| `editorial` | sentence that says the grouping of the main tree is an editorial aid |
| `labels` | optional: `hub`, `hubShort`, `jumpHub` (texts of the main-tree buttons) |

### Palette (dark theme, kit deck colours)

`#34D399` green · `#38BDF8` sky · `#A78BFA` violet · `#FBBF24` amber · `#C7D2EC` grey ·
`#00B39F` teal (brand) · `#7C8FE0` Azure blue. Named colour keys usable anywhere a colour key is
asked: every strategy key, `teal`, `tealhi`, `client`, `azure`, `foundry`, `measure`.

## Fields every scene has

| Key | Rule |
|-----|------|
| `id` | unique, kebab case; used in links (`page.html#tree-model`) |
| `type` | one of the types below, or a topic renderer type |
| `section` | a `sections[].id` |
| `short` | 1–4 words: chapter list, progress tooltip, "Open … ›" buttons |
| `slide` | deck slide number, or a list `[7, 9]`; every deck slide is covered by some scene |
| `kicker` | small capitals line above the title, e.g. `"02 · MODEL CALLS"` |
| `title` | the deck slide title — a short noun phrase, ≤ 60 characters |
| `subtitle` | one plain sentence, ≤ 125 characters |
| `tags` | strategy keys shown as chips (top right) and as dots in the chapter list |
| `sources` | source keys for the footer |
| `notes` | the deck slide's speaker notes, presenter-verify sentences removed; "A likely question:" is shown in bold |
| `preview` | `true` when anything on the scene is marked `*`; shows `meta.previewNote` |

Beats (the → steps inside a scene) are set by the renderer; content never sets `beats`.

## Core scene types

Limits: **count** limits are enforced (FAIL); **length** limits (characters) are design targets (WARN).

### `title` — opening scene
`chapters`: up to 6 × `[number, text ≤ 70, sceneId]`. No kicker/title fields — it uses `meta`.

### `turn` — the problem (where the time, cost or risk goes)
- `bar`: segments `[label, fraction, segKey, colour?]`, fractions add up to 1; `segKey` one of
  `hop`, `model`, `tool`, `ttft`, `gen` (colours) or give a 4th element colour. Label it illustrative with `barLabel`.
- `marker` (optional): `{after: segKey or index, text}` — a ▲ note under the bar after that segment.
- `cards`: up to 6 × `{t, d ≤ 95, lever ≤ 44, tag, go?, detail, src}`; selecting a card opens the drawer.
- `principle` (+ `principleLabel`), `cardKicker`, `leverLabel` optional.

### `map` — the main decision tree (the hub; at most one, early in the story)
- `root`: `{t ≤ 24, d}` — the starting situation.
- `questions`: **3 to 5** × `{k: strategyKey, q ≤ 55, d ≤ 60, leaves}`; each question is one beat.
- `leaves`: **1 to 5** per question × `{t ≤ 70, go: sceneId, focus?, detail, src}`.
  `focus` = index of the row (tree) / panel / column to highlight in the target scene.
- `measure`, `govern` (optional framing bands above and below): `{t, d, go}`.
- `order` (optional): why the questions come in this order (+ `orderLabel`). `leafWord` (default "levers").

### `path` — a request path of 3 to 6 isometric blocks
- `hops`: `{t, d ≤ 50, kind: client|azure|foundry|colour key, lev: up to 4 chips ≤ 58, detail, optional: bool}`.
- `chain` (default all hops): how many hops form the main line; `loop: [from, to]` draws a side
  loop above (for example agent → tool). `obs` + `obsLabel`: band at the end. `legend`: `[[label, colourKey]]`.

### `table` — a comparison table with optional illustrative jitter sparklines
`cols`, `widths` (pixels, sum ≤ 1460), `rows` (≤ 6; a cell is text, `{text}` or
`{jitter: 0–1, drop?, gaps?}` for an illustrative variance sparkline), `band: [label, text]`.

### `tree` — a deck decision tree (Yes → recommendation, No → next question)
- `qs`: **2 to 6** × `{q ≤ 90, t ≤ 52 (end with * when preview), s ≤ 70, detail, src}`.
- `other`: `{t, s, detail, src}` — the "Otherwise" fallback.
- `aside`: `{h, items: up to 5 × [term, text ≤ 60]}`. `next`: `{t, go}` link to the following tree.
- Walk mode (W) asks the questions one by one; selecting any box opens the drawer.

### `spectrum` — patterns from simple to complex, each with an animated mini diagram
`cols`: 2 to 6 × `{t, calls, dg, cap ≤ 55, detail}`; `dg` is a preset (`direct`, `single`,
`seq`, `conc`, `hand`, `group`) or an inline diagram `{n: [[x, y, label, app|ag|mt]], e: [[from, to, bend]], seq: [[edgeIdx…]]}`
inside a 228 × 180 box. `arrow` (text of the simple → complex arrow), `band`, `callsLabel`.

### `trace` — an illustrative trace waterfall
`spans`: up to 7 × `[spanName, label, start 0–1, end 0–1, agent|model|tool|colour key]`;
`ft` (0–1, optional) + `ftLabel`: dashed marker; `caption`; `monitor`: up to 5 × `[term, text]`; `band`.

### `compare` — features × questions, with column spotlight
`feats`: 2 to 5 × `[label, strategyKey]`; `rows`: up to 6 × `[question, cell per feature ≤ 55]`; `band`.

### `phases` — an adoption or optimization path
`phases`: 3 to 6 × `[name, colourKey, up to 4 bullets ≤ 60]`; `prove`: up to 6 checks (+ `proveLabel`).

### `status` — status and recent changes, with preview filter
`rows`: up to 14 × `[capability, note, isPreview: bool]`; set `preview: true` when any row is preview.
`cols` (optional): three header texts.

### `refs` — references
`groups`: 1 to 4 × `[heading, [sourceKey…]]`; `current`: source keys for "staying current" (+ `currentLabel`).

## Topic renderers (only when no core type can show a slide)

A slide whose diagram is specific to the topic (the latency example has `anatomy` — an
interactive model-call timeline — and `features` — four animated feature panels) gets a
renderer in a separate file passed with `--extra-js`. It is injected inside the engine closure,
so all helpers are in scope:

```js
R.mytype = function (s, root, svg) {          // s = scene JSON, root = scene <div>, svg = wire layer
  var b = box(70, 196, 700, 400, "card", 0);   // x, y, w, h on the 1600×900 stage, class, beat
  add(b, el("h3", {text: s.heading}));          // el(tag, attrs, ...children); never innerHTML with content
  clickable(b, function () { openDrawer({kicker: "…", title: s.heading, body: s.detail, src: s.src}); }, s.heading);
  add(root, b);
  var p = wire(svg, curve(770, 400, 900, 400), 1, .2);   // animated connector shown at beat 1
  flow(p, {every: 900, speed: 240});                       // particles along it (skipped with reduced motion)
  s.beats = 1;                                             // last beat index
};
```

Rules: elements reveal with `data-b` (beat) through `box`/`wire`; timers via `later`/`every`
(cleared on scene change); respect `RM` (reduced motion); no network, no external assets, no
inline `on…` attributes in HTML strings; keep every box inside 1600 × 900. Run
`story_check.py --extra-js` so the new type is accepted.

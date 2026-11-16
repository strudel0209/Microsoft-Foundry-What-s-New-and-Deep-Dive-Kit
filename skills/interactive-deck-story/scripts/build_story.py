#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Assemble one self-contained interactive story page.

    python build_story.py <story.json> <out.html> [--extra-js renderers.js ...]

Inputs
  story.json    the story content (format: references/story-format.md)
  --extra-js    optional topic renderers, injected inside the engine closure at the
                TOPIC RENDERERS marker (every core helper is in scope there)

The engine (assets/engine.css, assets/engine.js) and the shell (assets/shell.html) are
read from the skill folder next to this script. Source keys used in scenes ("sources",
"src", "current" and the link lists of a refs scene) are resolved against the story's
top-level "sources" table; an unknown key stops the build.
"""
import argparse
import html
import json
import pathlib
import re
import sys

ENGINE_VERSION = "1.0.1"
HERE = pathlib.Path(__file__).resolve().parent
ASSETS = HERE.parent / "assets"
SRC_FIELDS = ("sources", "src", "current")
MARKER = "/*@@TOPIC_RENDERERS@@*/"


def fail(msg):
    print("BUILD FAILED: " + msg, file=sys.stderr)
    sys.exit(2)


def resolve(story):
    table = story.get("sources", {})
    missing = set()

    def link(item):
        if isinstance(item, str):
            if item not in table:
                missing.add(item)
                return {"label": item, "url": "#"}
            return {"label": table[item]["label"], "url": table[item]["url"]}
        return item

    def walk(o):
        if isinstance(o, dict):
            for k, v in list(o.items()):
                if k in SRC_FIELDS and isinstance(v, list):
                    o[k] = [link(x) for x in v]
                else:
                    walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)

    for sc in story["scenes"]:
        walk(sc)
        if sc.get("type") == "refs":
            sc["groups"] = [[g[0], [link(x) for x in g[1]]] for g in sc.get("groups", [])]
    if missing:
        fail("unknown source keys: " + ", ".join(sorted(missing)))
    story.pop("sources", None)
    return story


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("story")
    ap.add_argument("out")
    ap.add_argument("--extra-js", action="append", default=[], help="topic renderer file(s)")
    a = ap.parse_args()

    story = json.loads(pathlib.Path(a.story).read_text(encoding="utf-8"))
    for k in ("meta", "sections", "scenes"):
        if k not in story:
            fail("story.json has no '%s'" % k)
    story.setdefault("strategies", {})
    story = resolve(story)
    m = story["meta"]

    css = (ASSETS / "engine.css").read_text(encoding="utf-8")
    js = (ASSETS / "engine.js").read_text(encoding="utf-8")
    shell = (ASSETS / "shell.html").read_text(encoding="utf-8")
    if MARKER not in js:
        fail("engine.js has no topic-renderer marker")
    extra = "\n".join(pathlib.Path(p).read_text(encoding="utf-8") for p in a.extra_js)
    js = js.replace(MARKER, extra)

    data = json.dumps(story, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    hub = next((s for s in story["scenes"] if s.get("type") == "map"), None)
    fills = {
        "{{LANG}}": html.escape(m.get("lang", "en")),
        "{{DESCRIPTION}}": html.escape(m.get("subtitle", "")),
        "{{ENGINE_VERSION}}": ENGINE_VERSION,
        "{{TITLE}}": html.escape(m.get("title", "")),
        "{{BRAND}}": html.escape(m.get("brand", m.get("title", ""))),
        "{{HUB_SHORT}}": html.escape((m.get("labels") or {}).get("hubShort", "Main tree" if hub else "Overview")),
    }
    fills.update({"{{CSS}}": css, "{{DATA}}": data, "{{JS}}": js})
    # one pass, so inserted text is never scanned for placeholders
    page = re.sub(r"\{\{[A-Z_]+\}\}", lambda mt: fills.get(mt.group(0), mt.group(0)), shell)

    out = pathlib.Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page, encoding="utf-8")
    print("%s  %d bytes  %d scenes" % (out, len(page.encode("utf-8")), len(story["scenes"])))


if __name__ == "__main__":
    main()

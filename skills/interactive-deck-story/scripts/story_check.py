#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Check a story.json before it is built: structure, links, coverage and wording.

    python story_check.py <story.json> [--deck deck.json] [--extra-js renderers.js ...] [--json report.json]

FAIL (exit 1)  broken structure, unknown scene type, dangling "go" target or source key,
               slide number outside the deck, second-person wording, "Learn says/lists",
               "agent team", leaked presenter-verify text, preview item without the footnote.
WARN           title style, likely overflow (text longer than the box was designed for),
               measured-result wording, pitch words, deck slides with no scene.
The headless render check (render_check.js) stays the authority on overflow.
"""
import argparse
import json
import pathlib
import re
import sys

CORE = {"title", "turn", "map", "path", "table", "tree", "spectrum", "trace", "compare", "phases", "status", "refs"}
DG_PRESETS = {"direct", "single", "seq", "conc", "hand", "group"}
NON_TEXT_KEYS = {"id", "go", "type", "section", "url", "k", "tag", "kind", "dg", "anim", "sources", "src", "current",
                 "$schema_note", "lang", "color", "after", "focus"}
PITCH = ["unlock", "empower", "seamless", "game-changing", "game changing", "supercharge", "revolutionary",
         "cutting-edge", "best-in-class", "world-class", "next-generation"]
# soft limits (characters) — the lengths the layout was designed for
LIMITS = {
    ("map", "q"): 55, ("map", "d"): 60, ("map", "leaf"): 70, ("map", "root"): 24,
    ("tree", "q"): 90, ("tree", "t"): 52, ("tree", "s"): 70, ("tree", "aside"): 60,
    ("turn", "card"): 95, ("turn", "lever"): 44, ("path", "d"): 50, ("path", "lev"): 58,
    ("spectrum", "cap"): 55, ("compare", "cell"): 55, ("phases", "bullet"): 60, ("title", "chapter"): 70,
    ("scene", "title"): 60, ("scene", "subtitle"): 125,
}

fails, warns = [], []


def F(where, msg):
    fails.append("%s: %s" % (where, msg))


def W(where, msg):
    warns.append("%s: %s" % (where, msg))


def texts(o, key=None):
    """Yield every visible string in a scene (skips ids, links and keys)."""
    if isinstance(o, str):
        if key not in NON_TEXT_KEYS:
            yield o
    elif isinstance(o, dict):
        for k, v in o.items():
            if k not in NON_TEXT_KEYS:
                yield from texts(v, k)
    elif isinstance(o, list):
        for v in o:
            yield from texts(v, key)


def gos(o):
    if isinstance(o, dict):
        for k, v in o.items():
            if k == "go" and isinstance(v, str):
                yield v
            else:
                yield from gos(v)
    elif isinstance(o, list):
        for v in o:
            yield from gos(v)


def srckeys(o, key=None):
    if isinstance(o, dict):
        for k, v in o.items():
            if k in ("sources", "src", "current") and isinstance(v, list):
                for x in v:
                    if isinstance(x, str):
                        yield x
            else:
                yield from srckeys(v, k)
    elif isinstance(o, list):
        for v in o:
            yield from srckeys(v, key)


def need(where, obj, *keys):
    for k in keys:
        if k not in obj or obj[k] in (None, "", []):
            F(where, "missing '%s'" % k)


def length(where, kind, text):
    lim = LIMITS.get(kind)
    if lim and isinstance(text, str) and len(text) > lim:
        W(where, "%s text is %d characters (designed for %d) — check the render: \"%s…\"" % (kind[1], len(text), lim, text[:40]))


def check_scene(s, ids, strategies):
    t, w = s.get("type"), "scene %s (%s)" % (s.get("id"), s.get("type"))
    if t != "title":
        need(w, s, "kicker", "title", "subtitle", "short")
        length(w, ("scene", "title"), s.get("title"))
        length(w, ("scene", "subtitle"), s.get("subtitle"))
        ti = s.get("title", "")
        if ti.rstrip().endswith((".", ":", "!")):
            W(w, "title ends with punctuation; slide titles are short noun phrases")
        if len(ti.split()) > 9:
            W(w, "title has %d words; keep it a short noun phrase" % len(ti.split()))
    if t == "title":
        need(w, s, "chapters")
        for c in s.get("chapters", []):
            if len(c) != 3:
                F(w, "chapter entries are [number, text, sceneId]")
            elif c[2] not in ids:
                F(w, "chapter points to unknown scene '%s'" % c[2])
            else:
                length(w, ("title", "chapter"), c[1])
    elif t == "turn":
        need(w, s, "bar", "cards")
        tot = sum(b[1] for b in s.get("bar", []))
        if s.get("bar") and not 0.97 <= tot <= 1.03:
            F(w, "bar fractions add up to %.2f, not 1" % tot)
        if len(s.get("cards", [])) > 6:
            F(w, "more than 6 cards")
        mk = s.get("marker")
        if mk and not any(b[2] == mk.get("after") for b in s.get("bar", [])) and not isinstance(mk.get("after"), int):
            F(w, "marker.after matches no bar segment")
        for c in s.get("cards", []):
            need(w, c, "t", "d", "lever", "detail")
            length(w, ("turn", "card"), c.get("d"))
            length(w, ("turn", "lever"), c.get("lever"))
            if c.get("tag") and c["tag"] not in strategies:
                F(w, "card tag '%s' is not a strategy" % c["tag"])
    elif t == "map":
        q = s.get("questions", [])
        if not 3 <= len(q) <= 5:
            F(w, "the main tree needs 3 to 5 questions, has %d" % len(q))
        need(w, s, "root")
        length(w, ("map", "root"), (s.get("root") or {}).get("t"))
        for i, qq in enumerate(q):
            need("%s question %d" % (w, i + 1), qq, "k", "q", "d", "leaves")
            if qq.get("k") not in strategies:
                F(w, "question %d strategy '%s' not in strategies" % (i + 1, qq.get("k")))
            length(w, ("map", "q"), qq.get("q"))
            length(w, ("map", "d"), qq.get("d"))
            if not 1 <= len(qq.get("leaves", [])) <= 5:
                F(w, "question %d needs 1 to 5 leaves" % (i + 1))
            for lf in qq.get("leaves", []):
                need("%s leaf" % w, lf, "t", "go", "detail")
                length(w, ("map", "leaf"), lf.get("t"))
        for k in ("measure", "govern"):
            if s.get(k):
                need("%s %s" % (w, k), s[k], "t", "d", "go")
    elif t == "path":
        h = s.get("hops", [])
        if not 3 <= len(h) <= 6:
            F(w, "path needs 3 to 6 hops, has %d" % len(h))
        ch = s.get("chain", len(h))
        if ch > len(h):
            F(w, "chain is longer than the hop list")
        if s.get("loop") and (len(s["loop"]) != 2 or max(s["loop"]) >= len(h)):
            F(w, "loop must be [fromIndex, toIndex] inside the hop list")
        for x in h:
            need("%s hop" % w, x, "t", "d", "kind", "lev", "detail")
            length(w, ("path", "d"), x.get("d"))
            if len(x.get("lev", [])) > 4:
                F(w, "hop '%s' has more than 4 lever chips" % x.get("t"))
            for lv in x.get("lev", []):
                length(w, ("path", "lev"), lv)
    elif t == "table":
        need(w, s, "cols", "widths", "rows")
        if len(s.get("rows", [])) > 6:
            F(w, "more than 6 rows")
        if sum(s.get("widths", [])) > 1460:
            F(w, "column widths exceed 1460")
        for r in s.get("rows", []):
            if len(r) != len(s.get("cols", [])):
                F(w, "row length differs from the column count: %s" % str(r[0])[:40])
    elif t == "tree":
        qs = s.get("qs", [])
        if not 2 <= len(qs) <= 6:
            F(w, "decision tree needs 2 to 6 questions, has %d" % len(qs))
        need(w, s, "other", "aside")
        for qq in qs:
            need("%s question" % w, qq, "q", "t", "s", "detail")
            length(w, ("tree", "q"), qq.get("q"))
            length(w, ("tree", "t"), qq.get("t"))
            length(w, ("tree", "s"), qq.get("s"))
        if s.get("other"):
            need("%s otherwise" % w, s["other"], "t", "s", "detail")
        if len((s.get("aside") or {}).get("items", [])) > 5:
            F(w, "aside has more than 5 items")
        for it in (s.get("aside") or {}).get("items", []):
            length(w, ("tree", "aside"), it[1] if len(it) > 1 else "")
    elif t == "spectrum":
        if not 2 <= len(s.get("cols", [])) <= 6:
            F(w, "spectrum needs 2 to 6 columns")
        for c in s.get("cols", []):
            need("%s column" % w, c, "t", "calls", "dg", "cap", "detail")
            if isinstance(c.get("dg"), str) and c["dg"] not in DG_PRESETS:
                F(w, "unknown diagram preset '%s' (presets: %s)" % (c["dg"], ", ".join(sorted(DG_PRESETS))))
            length(w, ("spectrum", "cap"), c.get("cap"))
    elif t == "trace":
        sp = s.get("spans", [])
        if not 1 <= len(sp) <= 7:
            F(w, "trace needs 1 to 7 spans")
        for x in sp:
            if len(x) != 5 or not (0 <= x[2] < x[3] <= 1):
                F(w, "span must be [code, label, start 0-1, end 0-1, kind] with start < end: %s" % str(x)[:60])
        if s.get("ft") is not None and not 0 < s["ft"] < 1:
            F(w, "ft must be between 0 and 1")
    elif t == "compare":
        f = s.get("feats", [])
        if not 2 <= len(f) <= 5:
            F(w, "compare needs 2 to 5 feature columns")
        if len(s.get("rows", [])) > 6:
            F(w, "more than 6 rows")
        for r in s.get("rows", []):
            if len(r) != len(f) + 1:
                F(w, "row needs a question and one cell per feature: %s" % str(r[0])[:40])
            for c in r[1:]:
                length(w, ("compare", "cell"), c)
    elif t == "phases":
        p = s.get("phases", [])
        if not 3 <= len(p) <= 6:
            F(w, "phases needs 3 to 6 phases")
        for x in p:
            if len(x) != 3 or len(x[2]) > 4:
                F(w, "phase must be [name, colorKey, up to 4 bullets]")
            else:
                for b in x[2]:
                    length(w, ("phases", "bullet"), b)
        if len(s.get("prove", [])) > 6:
            F(w, "more than 6 'prove first' items")
    elif t == "status":
        if len(s.get("rows", [])) > 14:
            F(w, "more than 14 status rows")
        for r in s.get("rows", []):
            if len(r) != 3 or not isinstance(r[2], bool):
                F(w, "status row must be [capability, note, isPreview]")
        if any(r[2] for r in s.get("rows", []) if len(r) == 3) and not s.get("preview"):
            F(w, "preview rows present but 'preview': true is missing (footnote)")
    elif t == "refs":
        g = s.get("groups", [])
        if not 1 <= len(g) <= 4:
            F(w, "refs needs 1 to 4 groups")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("story")
    ap.add_argument("--deck")
    ap.add_argument("--extra-js", action="append", default=[])
    ap.add_argument("--json")
    a = ap.parse_args()
    st = json.loads(pathlib.Path(a.story).read_text(encoding="utf-8"))
    types = set(CORE)
    for p in a.extra_js:
        types |= set(re.findall(r"\bR\.(\w+)\s*=\s*function", pathlib.Path(p).read_text(encoding="utf-8")))

    meta = st.get("meta", {})
    need("meta", meta, "title", "subtitle", "footer", "deck", "edition", "checked", "previewNote")
    sections = {x.get("id") for x in st.get("sections", [])}
    strategies = st.get("strategies", {})
    table = st.get("sources", {})
    scenes = st.get("scenes", [])
    ids = [s.get("id") for s in scenes]
    for d in {i for i in ids if ids.count(i) > 1}:
        F("scenes", "duplicate scene id '%s'" % d)
    if not scenes or scenes[0].get("type") != "title":
        F("scenes", "the first scene must be the title scene")
    maps = [s for s in scenes if s.get("type") == "map"]
    if len(maps) > 1:
        F("scenes", "more than one main decision tree (map) scene")
    if maps and ids.index(maps[0]["id"]) > 4:
        W("scenes", "the main decision tree comes late (scene %d); the story unfolds from it" % (ids.index(maps[0]["id"]) + 1))
    if maps and not meta.get("editorial"):
        W("meta", "no 'editorial' note: say that the grouping of the main tree is an editorial aid")
    for k, v in strategies.items():
        if not v.get("label"):
            F("strategies", "'%s' has no label" % k)

    deck = json.loads(pathlib.Path(a.deck).read_text(encoding="utf-8")) if a.deck else None
    covered = set()
    for s in scenes:
        w = "scene %s" % s.get("id")
        if s.get("type") not in types:
            F(w, "unknown scene type '%s' (add a topic renderer with --extra-js)" % s.get("type"))
            continue
        if s.get("section") not in sections:
            F(w, "section '%s' is not defined" % s.get("section"))
        for g in gos(s):
            if g not in ids:
                F(w, "'go' points to unknown scene '%s'" % g)
        keys = list(srckeys(s))
        if s.get("type") == "refs":
            keys += [x for grp in s.get("groups", []) for x in grp[1] if isinstance(x, str)]
        for k in keys:
            if k not in table:
                F(w, "unknown source key '%s'" % k)
        sl = s.get("slide")
        if sl is not None:
            for n in (sl if isinstance(sl, list) else [sl]):
                covered.add(n)
                if deck and not 1 <= n <= deck["slide_count"]:
                    F(w, "slide %s is outside the deck (1-%d)" % (n, deck["slide_count"]))
        elif s.get("type") not in ("title", "map"):
            W(w, "no deck slide number")
        check_scene(s, ids, strategies)
        # wording
        alltext = list(texts(s))
        blob = "\n".join(alltext)
        for rx, msg in ((r"\byou(r|rs|rself|'re|'ll|'ve)?\b", "second person ('you/your') — write in the third person"),
                        (r"\bLearn (says|lists)\b", "'Learn says/lists' — write 'as per official documentation' or drop it"),
                        (r"\bagent team\b", "'agent team' — name the actor, e.g. 'development team'"),
                        (r"Presenter note", "presenter-verify text leaked onto the page")):
            m = re.search(rx, blob, re.I)
            if m:
                ctx = blob[max(0, m.start() - 30): m.end() + 30].replace("\n", " ")
                F(w, "%s: \"…%s…\"" % (msg, ctx))
        for p in PITCH:
            if re.search(r"\b%s\b" % re.escape(p), blob, re.I):
                W(w, "pitch word '%s'" % p)
        if re.search(r"\b\d+(\.\d+)?\s?(ms|milliseconds|%|x faster|times faster)\b", blob, re.I):
            W(w, "number with a unit — keep the page conceptual (no measured results); keep only documented thresholds")
        if any(x.rstrip().endswith("*") for x in alltext) and not s.get("preview"):
            F(w, "item marked '*' (preview) but the scene has no 'preview': true, so the footnote is missing")
    if deck:
        missing = [x["n"] for x in deck["slides"] if x["n"] not in covered]
        if missing:
            W("coverage", "deck slides with no scene: %s (title and agenda slides are usually covered by the title scene)" % missing)
    used = set()
    for s in scenes:
        used |= set(srckeys(s))
        if s.get("type") == "refs":
            used |= {x for grp in s.get("groups", []) for x in grp[1] if isinstance(x, str)}
    for k in sorted(set(table) - used):
        W("sources", "source '%s' is never used" % k)
    res = {"status": "fail" if fails else ("warn" if warns else "pass"), "fails": fails, "warns": warns,
           "scenes": len(scenes)}
    if a.json:
        pathlib.Path(a.json).write_text(json.dumps(res, indent=1, ensure_ascii=False), encoding="utf-8")
    print("story check: %s · %d scenes · %d FAIL · %d WARN" % (res["status"].upper(), len(scenes), len(fails), len(warns)))
    for f in fails:
        print("  FAIL " + f)
    for x in warns:
        print("  WARN " + x)
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()

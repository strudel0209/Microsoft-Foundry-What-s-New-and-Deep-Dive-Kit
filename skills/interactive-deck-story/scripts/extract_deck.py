#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Extract the content of a kit deck for an interactive story.

    python extract_deck.py <deck.pptx> <deck.json> [--md <deck.md>]

Writes, per slide: number, title, every text line (shapes, groups and tables, in reading
order), preview items (text ending in "*"), hyperlinks and URLs, and the speaker notes.
Notes are split into "notes" (presenter-verify sentences removed, ready for the page) and
"verify" (the removed "Presenter note: verify ..." sentences, which never go on the page).
The optional Markdown file is a compact reading copy for planning the story.
"""
import argparse
import json
import re
import sys

try:
    from pptx import Presentation
    from pptx.enum.shapes import MSO_SHAPE_TYPE
except ImportError:  # pragma: no cover
    sys.exit("python-pptx is required (it is part of the pptx skill environment)")

URL = re.compile(r"https?://[^\s)\]>\"']+")
SENT = re.compile(r"(?<=[.?!])\s+(?=[A-Z])")


def split_notes(notes):
    """Return (page notes, presenter verify sentences). A sentence that starts with
    'Presenter note:' and mentions verifying never goes on the page."""
    keep, verify = [], []
    for para in notes.split("\n"):
        for s in SENT.split(para.strip()):
            if not s:
                continue
            (verify if re.match(r"presenter note:", s, re.I) and "verif" in s.lower() else keep).append(s)
        keep.append("\n")
    clean = re.sub(r" ?\n ?", "\n", " ".join(keep)).strip()
    return re.sub(r"\n{2,}", "\n", clean), verify


def shape_texts(shape, out, links):
    if shape.shape_type == MSO_SHAPE_TYPE.GROUP:
        for s in sorted(shape.shapes, key=lambda s: (s.top or 0, s.left or 0)):
            shape_texts(s, out, links)
        return
    if getattr(shape, "has_table", False) and shape.has_table:
        for row in shape.table.rows:
            out.append(" | ".join(c.text.strip() for c in row.cells))
        return
    if getattr(shape, "has_text_frame", False) and shape.has_text_frame:
        for p in shape.text_frame.paragraphs:
            t = "".join(r.text for r in p.runs).strip()
            if t:
                out.append(t)
            for r in p.runs:
                if r.hyperlink and r.hyperlink.address:
                    links.append({"text": r.text.strip(), "url": r.hyperlink.address})
    try:
        if shape.click_action and shape.click_action.hyperlink.address:
            links.append({"text": "", "url": shape.click_action.hyperlink.address})
    except Exception:
        pass


def title_of(slide, texts):
    try:
        if slide.shapes.title is not None and slide.shapes.title.text.strip():
            return slide.shapes.title.text.strip()
    except Exception:
        pass
    # kit decks draw titles as text boxes: take the largest-font short line near the top
    best = None
    for sh in slide.shapes:
        if not getattr(sh, "has_text_frame", False) or not sh.has_text_frame or not sh.text_frame.text.strip():
            continue
        size = 0
        for p in sh.text_frame.paragraphs:
            for r in p.runs:
                if r.font.size:
                    size = max(size, r.font.size.pt)
        key = (-(size or 0), sh.top or 0)
        if best is None or key < best[0]:
            best = (key, sh.text_frame.text.strip().split("\n")[0])
    return best[1] if best else (texts[0] if texts else "")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("deck")
    ap.add_argument("out")
    ap.add_argument("--md")
    a = ap.parse_args()
    prs = Presentation(a.deck)
    slides = []
    for i, slide in enumerate(prs.slides, 1):
        texts, links = [], []
        for sh in sorted(slide.shapes, key=lambda s: (s.top or 0, s.left or 0)):
            shape_texts(sh, texts, links)
        notes = ""
        if slide.has_notes_slide:
            notes = slide.notes_slide.notes_text_frame.text.strip()
        clean, verify = split_notes(notes)
        urls = sorted(set(URL.findall("\n".join(texts) + "\n" + notes)) | {l["url"] for l in links if l["url"].startswith("http")})
        slides.append({
            "n": i,
            "title": title_of(slide, texts),
            "texts": texts,
            "preview_items": [t for t in texts if t.rstrip().endswith("*") and len(t) > 2],
            "links": links,
            "urls": urls,
            "notes": clean,
            "verify": verify,
        })
    deck = {"file": a.deck.replace("\\", "/").split("/")[-1], "slide_count": len(slides),
            "width_emu": prs.slide_width, "height_emu": prs.slide_height, "slides": slides}
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump(deck, f, ensure_ascii=False, indent=1)
    if a.md:
        with open(a.md, "w", encoding="utf-8") as f:
            f.write("# %s\n\n%d slides\n" % (deck["file"], len(slides)))
            for s in slides:
                f.write("\n## Slide %d · %s\n\n" % (s["n"], s["title"]))
                for t in s["texts"]:
                    f.write("- %s\n" % t)
                if s["verify"]:
                    f.write("\n**Presenter verify items (never on the page):** %s\n" % " / ".join(s["verify"]))
                if s["notes"]:
                    f.write("\n**Notes:** %s\n" % s["notes"])
    print("%s: %d slides, %d with notes, %d verify items, %d preview items" % (
        deck["file"], len(slides), sum(1 for s in slides if s["notes"]),
        sum(len(s["verify"]) for s in slides), sum(len(s["preview_items"]) for s in slides)))


if __name__ == "__main__":
    main()

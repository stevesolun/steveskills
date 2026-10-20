#!/usr/bin/env python3
"""criteria-map: how much of a draft answers each criterion it will be judged on.

Usage:
  criteria-map.py CRITERIA.txt DRAFT.md [--placeholders]

CRITERIA.txt holds one criterion per line: a name, optionally followed by a
colon and keywords (`Broader impacts: outreach, training, society`). The
draft is split into sections by its headings. A section is mapped to a
criterion when its heading shares a word with the criterion's name, or when
the criterion's keywords appear in it. Prints, per criterion, the sections
mapped, the words devoted, and the placeholders left ([PRELIMINARY DATA],
[BUDGET], [CITATION], TODO, TBD, XXX, ???), then the criteria with no
section at all. Exit 1 when any criterion is unmapped or any placeholder
remains; a draft ships when the map is full and the placeholders are gone.
"""
import argparse
import re
import sys

STOP = {"the", "and", "of", "for", "to", "a", "an", "in", "on", "with", "by", "or", "its", "this", "that", "is", "are"}
PLACEHOLDER = re.compile(r"\[(?:PRELIMINARY DATA|BUDGET|CITATION|CITE|TBD|TODO|PLACEHOLDER|INSERT[^\]]*|XX+)[^\]]*\]|\bTODO\b|\bTBD\b|\bXXX\b|\?\?\?|<<\[?[^<>\n]{1,40}\]?>>|\[\[[^\]\n]{1,40}\]\]|\{\{[^}\n]{1,40}\}\}", re.I)


def words(s):
    return {w for w in re.findall(r"[a-z][a-z-]+", s.lower()) if w not in STOP and len(w) > 2}


def sections(text):
    """(title, body) per heading; a body includes every subsection under it,
    so a criterion mapped to a heading is credited with the whole subtree."""
    raw = []; title = "(preamble)"; level = 0; buf = []
    for line in text.splitlines():
        m = re.match(r"^(#{1,6})\s+(.+?)\s*$", line)
        b = re.match(r"^\*\*([^*]{3,80})\*\*\s*$", line)
        if m or b:
            raw.append((title, level, "\n".join(buf)))
            title = (m.group(2) if m else b.group(1)).strip(); level = len(m.group(1)) if m else 7; buf = []
        else:
            buf.append(line)
    raw.append((title, level, "\n".join(buf)))
    out = []
    for i, (t, lv, body) in enumerate(raw):
        full = [body]
        for t2, lv2, body2 in raw[i + 1:]:
            if lv2 <= lv:
                break
            full.append(body2)
        if t != "(preamble)" or body.strip():
            out.append((t, "\n".join(full)))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("criteria"); ap.add_argument("draft")
    ap.add_argument("--placeholders", action="store_true", help="list every placeholder with its line")
    ap.add_argument("--thin", type=int, default=40, help="words under which a mapped criterion is flagged THIN (default 40)")
    a = ap.parse_args()
    crit = []
    for line in open(a.criteria, encoding="utf-8"):
        line = line.strip().lstrip("-*0123456789. ")
        if not line:
            continue
        name, _, kw = line.partition(":")
        crit.append((name.strip(), [k.strip().lower() for k in kw.split(",") if k.strip()]))
    text = open(a.draft, encoding="utf-8", errors="replace").read()
    secs = sections(text)
    total_words = len(text.split())
    print(f"draft: {len(secs)} sections, {total_words} words; criteria: {len(crit)}")
    print(f"{'criterion':34s} {'words':>6s} {'share':>6s} {'holes':>5s}  sections")
    unmapped = []; thin = []; holes_total = 0
    for name, kws in crit:
        nw = words(name)
        scored = [((len(nw & words(t)) / max(len(nw), 1)), t, b) for t, b in secs if nw & words(t)]
        best = max((sc for sc, _, _ in scored), default=0)
        hits = [(t, b) for sc, t, b in scored if sc == best]       # the headings that name the criterion best
        if not hits:                                                  # else sections carrying its keywords
            hits = [(t, b) for t, b in secs if any(re.search(r"\b" + re.escape(k) + r"\b", (t + " " + b).lower()) for k in kws)]
        wc = sum(len(b.split()) for _, b in hits)
        holes = sum(len(PLACEHOLDER.findall(b)) for _, b in hits)
        holes_total += holes
        share = wc / total_words * 100 if total_words else 0
        flag = "NONE" if not hits else ("THIN" if wc < a.thin else "")
        print(f"{name[:34]:34s} {wc:>6d} {share:>5.0f}% {holes:>5d}  {flag:4s} {'; '.join(t[:28] for t, _ in hits)[:66]}")
        if not hits:
            unmapped.append(name)
        elif wc < a.thin:
            thin.append(name)
    all_holes = [(ln, m.group(0)) for ln, line in enumerate(text.splitlines(), 1) for m in PLACEHOLDER.finditer(line)]
    print(f"\nunmapped criteria: {len(unmapped)}" + (f" ({', '.join(unmapped)})" if unmapped else "") + f"; thin: {len(thin)}" + (f" ({', '.join(thin)})" if thin else ""))
    print(f"placeholders left in the draft: {len(all_holes)}")
    if a.placeholders:
        for ln, ph in all_holes:
            print(f"  L{ln}: {ph}")
    sys.exit(1 if unmapped or thin or all_holes else 0)


if __name__ == "__main__":
    main()

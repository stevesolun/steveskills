#!/usr/bin/env python3
"""source-bound: a memo or literature map cites only the sources it was given.

Usage:
  source-bound.py inventory SOURCES_DIR
      one row per file: id, type, pages, characters of text extracted, and
      READABLE or UNREADABLE (a PDF with no text layer, an empty or binary
      file). Nothing is summarised from an UNREADABLE source.

  source-bound.py check DOC.md --sources SOURCES_DIR [--sentences]
      every citation in the doc ([id], [file.pdf], [file#section], (Author,
      2020), (Author 2020), {{id}}) is resolved against the inventory by file
      stem, by filename, or by an author surname plus year found in the file
      name or its first page. Prints: resolved citations, UNRESOLVED ones
      (references from memory, or to a source that was not provided),
      provided sources never cited, and the sentences that rest on exactly
      one source. Exit 1 when any citation is unresolved.
"""
import argparse
import os
import re
import subprocess
import sys

TEXT_EXT = (".txt", ".md", ".csv", ".json", ".html", ".tex", ".rst")
CITE = re.compile(r"\[([^\[\]\n]{1,80})\]|\(([A-Z][\w'’-]+(?: et al\.?| and [A-Z][\w'’-]+)?),? (\d{4}[a-z]?)\)|\{\{([^}\n]{1,80})\}\}")
YEAR = re.compile(r"\b(19|20)\d{2}[a-z]?\b")


def extract(path):
    low = path.lower()
    if low.endswith(".pdf"):
        pages = 0
        try:
            from pypdf import PdfReader
            r = PdfReader(path); pages = len(r.pages)
        except Exception:  # noqa: BLE001
            pass
        try:
            out = subprocess.run(["pdftotext", "-l", "3", path, "-"], capture_output=True, text=True, timeout=120).stdout
        except (OSError, subprocess.SubprocessError):
            out = ""
        if not out.strip() and pages:
            try:
                out = "\n".join((p.extract_text() or "") for p in r.pages[:3])
            except Exception:  # noqa: BLE001
                out = ""
        return "pdf", pages, out
    if low.endswith((".docx",)):
        try:
            import docx
            d = docx.Document(path)
            return "docx", 0, "\n".join(p.text for p in d.paragraphs)
        except Exception:  # noqa: BLE001
            return "docx", 0, ""
    if low.endswith(TEXT_EXT):
        with open(path, encoding="utf-8", errors="replace") as fh:
            return low.rsplit(".", 1)[-1], 0, fh.read()
    return "other", 0, ""


def inventory(d):
    rows = []
    for root, _, files in os.walk(d):
        for f in sorted(files):
            if f.startswith("."):
                continue
            p = os.path.join(root, f)
            kind, pages, text = extract(p)
            stem = os.path.splitext(f)[0]
            rows.append({"id": stem, "file": os.path.relpath(p, d), "kind": kind, "pages": pages, "chars": len(text.strip()),
                         "readable": len(text.strip()) >= 200, "head": text[:3000].lower()})
    return rows


def cmd_inventory(a):
    rows = inventory(a.sources)
    print(f"{'id':36s} {'kind':5s} {'pages':>5s} {'chars':>8s}  status")
    for r in rows:
        print(f"{r['id'][:36]:36s} {r['kind']:5s} {r['pages']:>5d} {r['chars']:>8d}  {'READABLE' if r['readable'] else 'UNREADABLE'}")
    n = len(rows); u = sum(1 for r in rows if not r["readable"])
    print(f"\nsources: {n} provided, {n - u} readable, {u} unreadable")
    return 0


def resolve(cite, rows):
    c = cite.strip().lower()
    key = c.split("#")[0].split("§")[0].strip()
    for r in rows:
        if key in (r["id"].lower(), r["file"].lower()) or key == os.path.splitext(r["file"].lower())[0]:
            return r["id"]
    m = re.match(r"([a-z][\w'’-]+)(?: et al\.?| and [a-z][\w'’-]+)?,? (\d{4})", c)
    if m:
        sur, yr = m.group(1), m.group(2)
        for r in rows:
            name = r["file"].lower()
            if sur in name and yr in name:
                return r["id"]
            if sur in r["head"] and yr in r["head"]:
                return r["id"]
    return None


def cmd_check(a):
    rows = inventory(a.sources)
    doc = open(a.doc, encoding="utf-8", errors="replace").read()
    cites = []
    for m in CITE.finditer(doc):
        if m.group(1) is not None:
            raw = m.group(1)
            if re.fullmatch(r"\d+", raw) or raw.lower().startswith(("x", " ", "http")) or len(raw) < 2:
                continue  # numbered footnotes and markdown link text are not source citations here
            cites.append(raw)
        elif m.group(2):
            cites.append(f"{m.group(2)} {m.group(3)}")
        else:
            cites.append(m.group(4))
    resolved, unresolved = {}, []
    for c in cites:
        r = resolve(c, rows)
        if r:
            resolved.setdefault(r, []).append(c)
        else:
            unresolved.append(c)
    used = set(resolved)
    never = [r["id"] for r in rows if r["id"] not in used]
    print(f"citations in doc: {len(cites)}; resolved to {len(used)} provided source(s); unresolved {len(set(unresolved))}")
    for sid, cs in resolved.items():
        print(f"  ok          {sid}  ({len(cs)} citation{'s' if len(cs) != 1 else ''})")
    for c in sorted(set(unresolved)):
        print(f"  UNRESOLVED  [{c}]  (not among the provided sources)")
    for sid in never:
        print(f"  unused      {sid}")
    # single-source sentences
    singles = []
    for sent in re.split(r"(?<=[.!?])\s+|\n+", doc):
        found = {resolve(c, rows) for c in [m.group(1) or (f"{m.group(2)} {m.group(3)}" if m.group(2) else m.group(4)) for m in CITE.finditer(sent)]}
        found.discard(None)
        if len(found) == 1 and len(sent.split()) > 6:
            singles.append((next(iter(found)), sent.strip()))
    print(f"\nsentences resting on a single source: {len(singles)}")
    if a.sentences:
        for sid, s in singles:
            print(f"  [{sid}] {s[:110]}")
    return 1 if unresolved else 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("inventory"); p.add_argument("sources"); p.set_defaults(fn=cmd_inventory)
    p = sub.add_parser("check"); p.add_argument("doc"); p.add_argument("--sources", required=True); p.add_argument("--sentences", action="store_true"); p.set_defaults(fn=cmd_check)
    a = ap.parse_args()
    sys.exit(a.fn(a))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""number-trace: every number in a summary or write-up traces back to a source.

Usage:
  number-trace.py --doc SUMMARY.md SOURCE [SOURCE ...]

Sources are .txt, .md, .csv, .log (read as text) or .pdf (text layer via
pdftotext, then pypdf). The doc's numbers are extracted with the unit that
follows them (10 ms, 45%, 2.5 GB/s, 3 million) and each is searched for in
the sources as a whole number with that unit, thousands separators and the
percent sign spelled both ways. Dates, version strings, list numbering,
section, figure, table and reference numbers are skipped: they are labels,
not quantities.

A number the doc marks as its own is counted apart from the source's:
write `(computed ...)`, `(assumed ...)`, `(estimated ...)` or `(from
memory)` after it in the same sentence. Prints one row per number with where
it was found and the source line it matched, then
`numbers: N in doc, F found, L labelled, M not found`. Exit 1 when any number
is neither found nor labelled: it must be quoted, labelled or removed.
"""
import argparse
import os
import re
import subprocess
import sys

UNIT = r"(%|percent|million|billion|thousand|points?|pts|pp|ns|us|µs|ms|s|secs?|seconds?|min|minutes?|hours?|h|days?|weeks?|months?|years?|[KMGT]i?B(?:/s)?|[kmgt]b(?:ps)?|[KMG]bps|[kKMB]|x|×|rows?|users?|requests?|items?|files?|lines?|commits?|tests?|samples?|cases?|patients?|participants?)"
NUM = re.compile(r"(?<![\w.:])(\d{1,3}(?:,\d{3})+|\d+(?:\.\d+)?)(?:\s?" + UNIT + r")?(?![\w:])(?!\.\d)", re.I)
RANGE = re.compile(r"(?<![\w.:])(\d+(?:\.\d+)?)\s?(?:-|–|to)\s?(\d+(?:\.\d+)?)(?:\s?" + UNIT + r")?(?![\w:])(?!\.\d)", re.I)
LABEL_RX = re.compile(r"\((?:computed|calculated|derived|assumed|assumption|estimated|estimate|approx\w*|from memory|my (?:own )?(?:estimate|assumption))[^)]*\)", re.I)
SKIP_LINE_BITS = [
    re.compile(r"\b\d{4}-\d{2}-\d{2}\b"), re.compile(r"\b\d{1,2}/\d{1,2}/\d{2,4}\b"),           # dates
    re.compile(r"\bv?\d+\.\d+\.\d+\b"),                                                          # versions
    re.compile(r"\b(?:Section|Sec\.|Figure|Fig\.|Table|Tab\.|Equation|Eq\.|Chapter|Appendix|ref\.?|footnote|page|p\.|pp\.|step|phase|round|Q)\s?\d+\b", re.I),
    re.compile(r"\[\d+(?:[,–-]\s?\d+)*\]"), re.compile(r"\(\d{4}[a-z]?\)"), re.compile(r"#\d+\b"),
    re.compile(r"^\s*\d+[.)]\s"),                                                                # list numbering
]


def read_source(path):
    low = path.lower()
    if low.endswith(".pdf"):
        try:
            out = subprocess.run(["pdftotext", "-layout", path, "-"], capture_output=True, text=True, timeout=120).stdout
            if out.strip():
                return out
        except (OSError, subprocess.SubprocessError):
            pass
        try:
            from pypdf import PdfReader
            return "\n".join((p.extract_text() or "") for p in PdfReader(path).pages)
        except Exception:  # noqa: BLE001
            return ""
    with open(path, encoding="utf-8", errors="replace") as fh:
        return fh.read()


def norm(s):
    """Lower-case, commas and thin spaces out; the line count is unchanged so a match maps back to its source line."""
    return s.replace(",", "").replace(" ", "").replace(" ", " ").lower()


WORD = re.compile(r"[a-z]{3,}")


def overlap(doc_line, src_line):
    """Words a doc sentence and a candidate source line share: picks the right line when a number recurs."""
    return len(set(WORD.findall(doc_line.lower())) & set(WORD.findall(src_line.lower())))


def unit_forms(u):
    u = (u or "").lower()
    if not u:
        return [""]  # a bare number matches a bare number
    if u in ("%", "percent"):
        return [r"\s*%", r"\s*percent"]
    return [r"\s*" + re.escape(u)]


def value_forms(v):
    v = v.replace(",", "")
    forms = {v}
    if "." in v:
        forms.add(v.rstrip("0").rstrip("."))
    elif len(v) > 3:
        forms.add(f"{int(v):,}".replace(",", ""))  # already comma-free; kept for symmetry
    return forms


def find(value, unit, srcs, doc_line, value2=None):
    """Return (source name, matched source line) or None. A unit in the doc must appear in the source match.

    When the number occurs in several places, the source line sharing the most words with the doc
    sentence is reported, so the eye check lands on the right line."""
    cands = []
    for vf in value_forms(value):
        for uf in unit_forms(unit):
            core = re.escape(vf)
            if value2 is not None:
                core += r"\s*(?:-|–|to)\s*" + re.escape(value2.replace(",", ""))
            # a bare number must stand alone (not the 60 in a hash like bc60a3); a unit may run on (GB/sec)
            post = r"(?![\d.])" if uf else r"(?![\w.])"
            pat = re.compile(r"(?<![\w.])" + core + uf + post)
            for name, text, lines in srcs:
                for m in pat.finditer(text):
                    ln = text.count("\n", 0, m.start())
                    line = lines[ln].strip() if ln < len(lines) else ""
                    cands.append((overlap(doc_line, line), -len(cands), name, line))
    if not cands:
        return None
    best = max(cands)
    return best[2], best[3]


def blank_skips(line):
    """Blank out the label-like numbers so the extractor never sees them."""
    out = line
    for rx in SKIP_LINE_BITS:
        out = rx.sub(lambda m: " " * len(m.group(0)), out)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--doc", required=True)
    ap.add_argument("sources", nargs="+")
    a = ap.parse_args()
    doc = open(a.doc, encoding="utf-8", errors="replace").read()
    srcs = []
    for p in a.sources:
        raw_text = read_source(p)
        t = norm(raw_text)
        srcs.append((os.path.basename(p), t, raw_text.splitlines()))
        if not t.strip():
            print(f"warning: no text in {p} (scanned PDF or empty file)")
    found = labelled = missing = 0
    seen = set()
    print(f"{'number':>14s}  {'where':24s} {'source line':40s} doc context")
    for line_no, raw in enumerate(doc.splitlines(), 1):
        line = blank_skips(raw)
        items = []  # (value, value2 or None, unit, end)
        # a range found whole in a source is one quantity; otherwise its ends are traced one by one
        for m in RANGE.finditer(line):
            v1, v2, unit = m.group(1), m.group(2), (m.group(3) or "")
            if find(v1, unit, srcs, raw, value2=v2):
                items.append((v1, v2, unit, m.end()))
                line = line[:m.start()] + " " * (m.end() - m.start()) + line[m.end():]
        for m in NUM.finditer(line):
            items.append((m.group(1), None, (m.group(2) or ""), m.end()))
        for value, value2, unit, end in sorted(items, key=lambda x: x[3]):
            key = (value.replace(",", ""), value2, unit.lower())
            if key in seen:
                continue
            seen.add(key)
            shown = value + (f"-{value2}" if value2 else "")
            label = f"{shown}{(' ' + unit) if unit and unit != '%' else unit}"
            ctx = raw.strip()[:50]
            # a label in the rest of the sentence, after the number
            tail = raw[end:].split(". ")[0]
            lab = LABEL_RX.search(tail)
            hit = find(value, unit, srcs, raw, value2=value2)
            if hit:
                found += 1
                print(f"{label:>14s}  {hit[0][:24]:24s} {hit[1][:40]:40s} L{line_no}: {ctx}")
            elif lab:
                labelled += 1
                kind = lab.group(0)[1:-1].split()[0].rstrip(",").lower()
                print(f"{label:>14s}  {'labelled: ' + kind:24s} {'':40s} L{line_no}: {ctx}")
            else:
                missing += 1
                print(f"{label:>14s}  {'NOT FOUND':24s} {'':40s} L{line_no}: {ctx}")
    print(f"\nnumbers: {found + labelled + missing} in doc, {found} found, {labelled} labelled, {missing} not found")
    sys.exit(1 if missing else 0)


if __name__ == "__main__":
    main()

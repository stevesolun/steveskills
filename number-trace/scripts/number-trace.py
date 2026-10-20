#!/usr/bin/env python3
"""number-trace: every number in a summary or write-up traces back to a source.

Usage:
  number-trace.py --doc SUMMARY.md SOURCE [SOURCE ...]

Sources are .txt, .md, .csv, .log (read as text) or .pdf (text layer via
pdftotext, then pypdf). The doc's numbers are extracted (integers, decimals,
percentages, numbers with k/M/B/million/billion, years) and each is searched
for in the sources, with thousands separators and % spelled out both ways.
Prints one row per number with where it was found, then
`numbers: N in doc, F found, M not found`. Exit 1 when any number is not
found: it was computed, remembered or invented, and the doc must say which.
"""
import argparse
import os
import re
import subprocess
import sys

NUM = re.compile(r"(?<![\w.])(\d{1,3}(?:,\d{3})+|\d+(?:\.\d+)?)\s?(%|percent|million|billion|thousand|[kKMB](?![a-zA-Z]))?")
SKIP_CONTEXT = re.compile(r"(?:^|\s)(?:\[\d+\]|\(\d{4}\)|#\d+|v\d+(?:\.\d+)*|\d+\.\s)")


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
    return s.replace(",", "").replace(" ", "").lower()


def variants(value, unit):
    v = value.replace(",", "")
    forms = {v}
    if "." in v:
        forms.add(v.rstrip("0").rstrip("."))
    else:
        if len(v) > 3:
            forms.add(f"{int(v):,}")
    out = set()
    for f in forms:
        if unit in ("%", "percent"):
            out.update({f + "%", f + " %", f + " percent", f + "percent"})
        elif unit:
            out.update({f + unit.lower(), f + " " + unit.lower()})
            if unit.lower() in ("k", "thousand"):
                out.add(str(int(float(f) * 1000)) if f.replace(".", "").isdigit() else f)
            if unit.lower() in ("m", "million"):
                out.add(str(int(float(f) * 1_000_000)) if f.replace(".", "").isdigit() else f)
        else:
            out.add(f)
    return {norm(x) for x in out}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--doc", required=True)
    ap.add_argument("sources", nargs="+")
    ap.add_argument("--min", type=float, default=0, help="ignore numbers below this (default 0, so single digits count too)")
    a = ap.parse_args()
    doc = open(a.doc, encoding="utf-8", errors="replace").read()
    srcs = []
    for p in a.sources:
        t = read_source(p)
        srcs.append((os.path.basename(p), norm(t), len(t)))
        if not t.strip():
            print(f"warning: no text in {p} (scanned PDF or empty file)")
    found = missing = 0
    seen = set()
    print(f"{'number':>14s}  {'where':28s} context")
    for line_no, line in enumerate(doc.splitlines(), 1):
        for m in NUM.finditer(line):
            value, unit = m.group(1), (m.group(2) or "")
            if SKIP_CONTEXT.search(line[max(0, m.start() - 2):m.end() + 2]):
                continue
            try:
                if float(value.replace(",", "")) < a.min:
                    continue
            except ValueError:
                continue
            key = (value, unit.lower())
            if key in seen:
                continue
            seen.add(key)
            forms = variants(value, unit)
            hit = None
            for name, text, _ in srcs:
                if any(re.search(r"(?<![\d.])" + re.escape(f) + r"(?![\d.])", text) for f in forms):
                    hit = name; break
            ctx = line.strip()[:70]
            label = f"{value}{unit}"
            if hit:
                found += 1; print(f"{label:>14s}  {hit[:28]:28s} L{line_no}: {ctx}")
            else:
                missing += 1; print(f"{label:>14s}  {'NOT FOUND':28s} L{line_no}: {ctx}")
    print(f"\nnumbers: {found + missing} in doc, {found} found, {missing} not found")
    sys.exit(1 if missing else 0)


if __name__ == "__main__":
    main()

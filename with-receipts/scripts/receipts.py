#!/usr/bin/env python3
"""receipts: the checks behind a number reported from data. Standard library only.

  receipts.py freshness DATA.csv --date-col COL
      rows, max date in the data, days between max date and today. Freshness
      is the max date in the data, never "yesterday".

  receipts.py compare A.csv B.csv --key KEY --value VALUE [--tolerance 0.5%]
      the same number computed two ways (two queries, two sources, a compiled
      metric and raw SQL): per-key delta, agree/disagree counts. Exit 1 on any
      disagreement beyond tolerance or any key present on one side only.

  receipts.py sum PARTS.csv --value VALUE --total N [--tolerance 0.5%]
      a decomposition: the parts add up to the reported total. Exit 1 if not.

  receipts.py footer ANSWER.md
      the answer ends with a receipt footer carrying every field below.
      Exit 1 on a missing or empty field.

Footer fields: question, source, freshness, query, cross-check, delta,
reviewed. A tolerance is a percentage ("0.5%") or an absolute number ("2").
"""
import argparse
import csv
import datetime as dt
import re
import sys

FIELDS = ("question", "source", "freshness", "query", "cross-check", "delta", "reviewed")


def num(s):
    s = (s or "").strip().replace(",", "")
    if s.endswith("%"):
        s = s[:-1]
    try:
        return float(s)
    except ValueError:
        return None


def tol(spec, reference):
    spec = (spec or "0").strip()
    if spec.endswith("%"):
        return abs(reference) * float(spec[:-1]) / 100.0
    return float(spec)


def parse_date(s):
    s = (s or "").strip()
    for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y/%m/%d", "%d/%m/%Y", "%m/%d/%Y", "%Y-%m"):
        try:
            return dt.datetime.strptime(s[:len(fmt) + 2] if fmt == "%Y-%m-%dT%H:%M:%S" else s, fmt).date()
        except ValueError:
            continue
    try:
        return dt.date.fromisoformat(s[:10])
    except ValueError:
        return None


def read(path):
    with open(path, newline="", encoding="utf-8", errors="replace") as f:
        return list(csv.DictReader(f))


def cmd_freshness(a):
    rows = read(a.data)
    dates = [d for d in (parse_date(r.get(a.date_col)) for r in rows) if d]
    if not dates:
        print(f"freshness: no parsable dates in column {a.date_col!r} ({len(rows)} rows)")
        return 1
    mx = max(dates)
    age = (dt.date.today() - mx).days
    print(f"freshness: {len(rows)} rows, {len(dates)} dated, max {a.date_col} = {mx.isoformat()}, {age} days before today")
    return 0


def cmd_compare(a):
    A = {r[a.key]: num(r.get(a.value)) for r in read(a.a)}
    B = {r[a.key]: num(r.get(a.value)) for r in read(a.b)}
    keys = sorted(set(A) | set(B), key=str)
    agree = disagree = missing = 0
    print(f"{'key':24s} {'A':>14s} {'B':>14s} {'delta':>12s}  verdict")
    for k in keys:
        x, y = A.get(k), B.get(k)
        if x is None or y is None:
            missing += 1
            print(f"{str(k)[:24]:24s} {x if x is not None else '-':>14} {y if y is not None else '-':>14} {'':>12}  only on one side")
            continue
        d = y - x
        ok = abs(d) <= tol(a.tolerance, x)
        agree += ok; disagree += (not ok)
        print(f"{str(k)[:24]:24s} {x:>14g} {y:>14g} {d:>+12g}  {'agree' if ok else 'DISAGREE'}")
    print(f"\ncross-check: {agree} agree, {disagree} disagree, {missing} only on one side (tolerance {a.tolerance})")
    return 0 if disagree == 0 and missing == 0 and agree > 0 else 1


def cmd_sum(a):
    parts = [num(r.get(a.value)) for r in read(a.parts)]
    parts = [p for p in parts if p is not None]
    s = sum(parts)
    d = s - a.total
    ok = abs(d) <= tol(a.tolerance, a.total)
    print(f"sum of {len(parts)} parts = {s:g}; reported total = {a.total:g}; delta {d:+g}; {'parts add up' if ok else 'PARTS DO NOT ADD UP'} (tolerance {a.tolerance})")
    return 0 if ok else 1


def cmd_footer(a):
    text = open(a.answer, encoding="utf-8", errors="replace").read()
    tail = text[-3000:]
    found = {}
    for f in FIELDS:
        m = re.search(rf"^\s*[-*]?\s*\**{re.escape(f)}\**\s*:\s*(.+?)\s*$", tail, re.I | re.M)
        found[f] = m.group(1).strip() if m else ""
    missing = [f for f in FIELDS if not found[f]]
    for f in FIELDS:
        print(f"  {f:12s} {'ok   ' if found[f] else 'MISSING'} {found[f][:90]}")
    print(f"receipt: {len(FIELDS) - len(missing)} of {len(FIELDS)} fields present" + (f"; missing {', '.join(missing)}" if missing else ""))
    return 1 if missing else 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("freshness"); p.add_argument("data"); p.add_argument("--date-col", required=True); p.set_defaults(fn=cmd_freshness)
    p = sub.add_parser("compare"); p.add_argument("a"); p.add_argument("b"); p.add_argument("--key", required=True); p.add_argument("--value", required=True); p.add_argument("--tolerance", default="0"); p.set_defaults(fn=cmd_compare)
    p = sub.add_parser("sum"); p.add_argument("parts"); p.add_argument("--value", required=True); p.add_argument("--total", type=float, required=True); p.add_argument("--tolerance", default="0"); p.set_defaults(fn=cmd_sum)
    p = sub.add_parser("footer"); p.add_argument("answer"); p.set_defaults(fn=cmd_footer)
    a = ap.parse_args()
    sys.exit(a.fn(a))


if __name__ == "__main__":
    main()

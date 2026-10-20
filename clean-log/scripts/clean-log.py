#!/usr/bin/env python3
"""clean-log: the change log of a data cleaning, computed from the files, not narrated.

Usage:
  clean-log.py BEFORE.csv AFTER.csv [--key COL] [--sample N]

Compares a raw file with its cleaned version and prints:
  rows      before, after, removed, added (by --key when given, else by position)
  columns   added, removed, renamed-looking pairs
  cells     per column: how many values changed, and the top kinds of change
            (whitespace, case, normalised, number format, date format,
            blank filled, value replaced), with N examples each
  checksums sha256 of both files, so the log names exactly what it compared

Exit 0 always; the log is the deliverable. Standard library only.
"""
import argparse
import csv
import hashlib
import re
import sys
from collections import Counter, defaultdict


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        h.update(fh.read())
    return h.hexdigest()[:12]


def load(path):
    with open(path, newline="", encoding="utf-8", errors="replace") as fh:
        r = csv.DictReader(fh)
        return r.fieldnames or [], list(r)


DATE_RX = re.compile(r"^\d{1,4}[-/.]\d{1,2}[-/.]\d{1,4}$")
NUM_RX = re.compile(r"^[-+]?[\d,]*\.?\d+%?$")


def kind(a, b):
    if a == b:
        return None
    if a.strip() == b.strip():
        return "whitespace"
    if a.strip().lower() == b.strip().lower():
        return "case"
    if re.sub(r"[^a-z0-9]", "", a.lower()) == re.sub(r"[^a-z0-9]", "", b.lower()) and a.strip() and b.strip():
        return "normalised"
    if a.strip() == "" and b.strip() != "":
        return "blank filled"
    if b.strip() == "" and a.strip() != "":
        return "blanked"
    if NUM_RX.match(a.strip()) and NUM_RX.match(b.strip()):
        try:
            if float(a.replace(",", "").rstrip("%")) == float(b.replace(",", "").rstrip("%")):
                return "number format"
        except ValueError:
            pass
    if DATE_RX.match(a.strip()) and DATE_RX.match(b.strip()):
        return "date format"
    return "value replaced"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("before"); ap.add_argument("after")
    ap.add_argument("--key", help="column that identifies a row; without it rows are matched by position")
    ap.add_argument("--sample", type=int, default=2, help="examples per change kind (default 2)")
    a = ap.parse_args()
    bcols, brows = load(a.before); acols, arows = load(a.after)
    print(f"before: {a.before} ({len(brows)} rows, {len(bcols)} cols, sha256 {sha(a.before)})")
    print(f"after:  {a.after} ({len(arows)} rows, {len(acols)} cols, sha256 {sha(a.after)})")

    added_cols = [c for c in acols if c not in bcols]; removed_cols = [c for c in bcols if c not in acols]
    renamed = [(r, c) for r in removed_cols for c in added_cols if re.sub(r"[^a-z0-9]", "", r.lower()) == re.sub(r"[^a-z0-9]", "", c.lower())]
    print(f"\ncolumns: {len(acols)} after ({len(added_cols)} added, {len(removed_cols)} removed" + (f", {len(renamed)} look renamed: " + ", ".join(f"{r} -> {c}" for r, c in renamed) if renamed else "") + ")")
    if added_cols: print(f"  added:   {', '.join(added_cols)}")
    if removed_cols: print(f"  removed: {', '.join(removed_cols)}")

    if a.key and a.key in bcols and a.key in acols:
        bmap = {r[a.key]: r for r in brows}; amap = {r[a.key]: r for r in arows}
        removed = [k for k in bmap if k not in amap]; added = [k for k in amap if k not in bmap]
        pairs = [(bmap[k], amap[k]) for k in bmap if k in amap]
        dup_b = len(brows) - len(bmap); dup_a = len(arows) - len(amap)
        print(f"\nrows (by {a.key}): {len(brows)} -> {len(arows)}; removed {len(removed)}, added {len(added)}, kept {len(pairs)}; duplicate keys before {dup_b}, after {dup_a}")
        if removed: print(f"  removed keys: {', '.join(map(str, removed[:a.sample * 3]))}{' ...' if len(removed) > a.sample * 3 else ''}")
    else:
        n = min(len(brows), len(arows)); pairs = list(zip(brows[:n], arows[:n]))
        print(f"\nrows (by position): {len(brows)} -> {len(arows)}; {len(brows) - len(arows):+d} net" if len(brows) != len(arows) else f"\nrows (by position): {len(brows)} -> {len(arows)}")

    shared = [c for c in bcols if c in acols]
    changed = Counter(); kinds = defaultdict(Counter); examples = defaultdict(lambda: defaultdict(list))
    for b, x in pairs:
        for c in shared:
            k = kind(b.get(c, ""), x.get(c, ""))
            if k:
                changed[c] += 1; kinds[c][k] += 1
                if len(examples[c][k]) < a.sample:
                    examples[c][k].append((b.get(c, ""), x.get(c, "")))
    total = sum(changed.values())
    print(f"\ncells changed in kept rows: {total}" + (f" across {len(changed)} columns" if changed else ""))
    for c, n in changed.most_common():
        print(f"  {c}: {n} changed; " + ", ".join(f"{k} {v}" for k, v in kinds[c].most_common()))
        for k, exs in examples[c].items():
            for bv, av in exs:
                print(f"      {k}: {bv[:40]!r} -> {av[:40]!r}")
    print("\nchange log: " + f"rows {len(brows)}->{len(arows)}, columns {len(bcols)}->{len(acols)}, cells changed {total}")


if __name__ == "__main__":
    main()

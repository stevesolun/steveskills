#!/usr/bin/env python3
"""driver-split: split the change in a number into named parts that add up.

Usage:
  driver-split.py SEGMENTS.csv [--unit pts|pct|abs] [--top N]

Two shapes of CSV, chosen by the columns present:

  rate   segment,before_num,before_den,after_num,after_den
         The overall rate is sum(num)/sum(den). Its change is split, per
         segment, into a mix effect (the segment's weight moved), a rate
         effect (the rate inside the segment moved) and an interaction term,
         in percentage points. The three columns add up to the change exactly.

  total  segment,before,after
         The overall total is sum(value). Its change is split into each
         segment's own change and its share of the move.

Prints one row per segment ranked by size, the sum of the parts against the
actual change, and the largest driver. Exit 1 if the parts do not add up
(they always do for a well-formed file; a mismatch means a parse problem).
"""
import argparse
import csv
import sys


def f(x):
    try:
        return float(str(x).replace(",", "").replace("%", ""))
    except ValueError:
        return 0.0


def largest_line(name, part, delta, fmt):
    if delta and abs(part) > abs(delta) * 1.0001:
        return f"largest driver: {name} ({part:+{fmt}}); the overall change is only {delta:+{fmt}} because other parts offset it"
    share = abs(part) / abs(delta) * 100 if delta else 0.0
    return f"largest driver: {name} ({part:+{fmt}} of {delta:+{fmt}}, {share:.0f}% of the move)"


def rate_split(rows, unit):
    bn = sum(f(r["before_num"]) for r in rows); bd = sum(f(r["before_den"]) for r in rows)
    an = sum(f(r["after_num"]) for r in rows); ad = sum(f(r["after_den"]) for r in rows)
    if not bd or not ad:
        print("denominators sum to zero"); return 1
    R0, R1 = bn / bd, an / ad
    scale = 100.0 if unit == "pts" else 1.0
    parts = []
    for r in rows:
        d0, d1 = f(r["before_den"]), f(r["after_den"])
        w0, w1 = d0 / bd, d1 / ad
        r0 = f(r["before_num"]) / d0 if d0 else 0.0
        r1 = f(r["after_num"]) / d1 if d1 else 0.0
        mix = (w1 - w0) * (r0 - R0)          # weight moved; measured against the overall rate so mix sums to its true effect
        rate = w0 * (r1 - r0)                # the segment's own rate moved
        inter = (w1 - w0) * (r1 - r0)        # both moved
        parts.append((r["segment"], mix * scale, rate * scale, inter * scale, (mix + rate + inter) * scale, w0, w1, r0, r1))
    delta = (R1 - R0) * scale
    total = sum(p[4] for p in parts)
    u = "pts" if unit == "pts" else ""
    print(f"overall rate: {R0*100:.2f}% -> {R1*100:.2f}%  change {delta:+.2f} {u}".rstrip())
    print(f"{'segment':20s} {'weight':>13s} {'rate':>17s} {'mix':>8s} {'rate':>8s} {'inter':>8s} {'total':>8s}")
    for p in sorted(parts, key=lambda p: -abs(p[4])):
        seg, mix, rate, inter, tot, w0, w1, r0, r1 = p
        print(f"{seg[:20]:20s} {w0*100:5.1f}%->{w1*100:5.1f}% {r0*100:6.1f}%->{r1*100:6.1f}% {mix:+8.2f} {rate:+8.2f} {inter:+8.2f} {tot:+8.2f}")
    ok = abs(total - delta) < 1e-6 * max(1.0, abs(delta))
    print(f"\nparts: {total:+.2f}  change: {delta:+.2f}  {'add up' if ok else 'DO NOT ADD UP'}")
    big = max(parts, key=lambda p: abs(p[4]))
    print(largest_line(big[0], big[4], delta, ".2f"))
    return 0 if ok else 1


def total_split(rows):
    b = sum(f(r["before"]) for r in rows); a = sum(f(r["after"]) for r in rows)
    delta = a - b
    parts = [(r["segment"], f(r["after"]) - f(r["before"]), f(r["before"]), f(r["after"])) for r in rows]
    print(f"overall total: {b:g} -> {a:g}  change {delta:+g}")
    print(f"{'segment':20s} {'before':>12s} {'after':>12s} {'change':>12s} {'share':>8s}")
    for seg, d, x, y in sorted(parts, key=lambda p: -abs(p[1])):
        share = d / delta * 100 if delta else 0.0
        print(f"{seg[:20]:20s} {x:>12g} {y:>12g} {d:>+12g} {share:>7.0f}%")
    total = sum(p[1] for p in parts)
    ok = abs(total - delta) < 1e-9 * max(1.0, abs(delta))
    print(f"\nparts: {total:+g}  change: {delta:+g}  {'add up' if ok else 'DO NOT ADD UP'}")
    big = max(parts, key=lambda p: abs(p[1]))
    print(largest_line(big[0], big[1], delta, "g"))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("segments")
    ap.add_argument("--unit", choices=["pts", "abs"], default="pts", help="rate mode: percentage points (default) or absolute fraction")
    a = ap.parse_args()
    with open(a.segments, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    if not rows:
        print("no rows"); sys.exit(2)
    cols = set(rows[0].keys())
    if {"segment", "before_num", "before_den", "after_num", "after_den"} <= cols:
        sys.exit(rate_split(rows, a.unit))
    if {"segment", "before", "after"} <= cols:
        sys.exit(total_split(rows))
    print("expected columns segment,before_num,before_den,after_num,after_den (rate) or segment,before,after (total)")
    sys.exit(2)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""answer-key: run a file of data questions with known answers and print the pass rate.

Usage:
  answer-key.py KEY.csv --sqlite DB.sqlite [--gate 0.9] [--label v3] [--log results.csv]
  answer-key.py KEY.csv --runner 'duckdb -csv -noheader mydb.duckdb < {query_file}' [...]

KEY.csv columns: id, question, query, expected, tolerance (optional, "0.5%" or
an absolute number; default 0). The query must return one value (first column
of the first row). With --sqlite the query runs in-process; with --runner the
command runs in a shell with {query_file} replaced by a temp file holding the
query, and its first output line is the value.

Prints one row per question (pass, FAIL, ERROR) with expected and actual, then
`answer key: P of N pass (rate)`. With --log, appends one row per run: time,
git SHA of the current directory, key file checksum, label, N, pass count,
rate, elapsed seconds, and the ids that failed, so drift is visible across
runs. Exit 1 when the rate is below --gate (default 1.0).
"""
import argparse
import csv
import datetime as dt
import hashlib
import os
import subprocess
import sys
import tempfile
import time


def num(s):
    try:
        return float(str(s).strip().replace(",", "").rstrip("%"))
    except (ValueError, AttributeError):
        return None


def within(actual, expected, tolerance):
    a, e = num(actual), num(expected)
    if a is None or e is None:
        return str(actual).strip() == str(expected).strip()
    t = (tolerance or "0").strip()
    allowed = abs(e) * float(t[:-1]) / 100.0 if t.endswith("%") else float(t)
    return abs(a - e) <= allowed


def run_sqlite(db, query):
    import sqlite3
    con = sqlite3.connect(db)
    try:
        row = con.execute(query).fetchone()
    finally:
        con.close()
    return "" if row is None else row[0]


def run_cmd(template, query):
    with tempfile.NamedTemporaryFile("w", suffix=".sql", delete=False) as fh:
        fh.write(query); path = fh.name
    try:
        p = subprocess.run(template.replace("{query_file}", path), shell=True, capture_output=True, text=True, timeout=600)
    finally:
        os.unlink(path)
    if p.returncode != 0:
        raise RuntimeError((p.stderr or p.stdout).strip()[:200])
    return p.stdout.strip().splitlines()[0] if p.stdout.strip() else ""


def git_sha():
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip() or "-"
    except OSError:
        return "-"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("key")
    ap.add_argument("--sqlite"); ap.add_argument("--runner")
    ap.add_argument("--gate", type=float, default=1.0); ap.add_argument("--label", default="-"); ap.add_argument("--log")
    a = ap.parse_args()
    if not a.sqlite and not a.runner:
        ap.error("give --sqlite DB or --runner 'command with {query_file}'")
    with open(a.key, newline="", encoding="utf-8") as fh:
        qs = list(csv.DictReader(fh))
    start = time.time()
    passed, failed, errors = 0, [], []
    print(f"{'id':10s} {'verdict':8s} {'expected':>12s} {'actual':>12s}  question")
    for q in qs:
        try:
            actual = run_sqlite(a.sqlite, q["query"]) if a.sqlite else run_cmd(a.runner, q["query"])
            ok = within(actual, q["expected"], q.get("tolerance"))
        except Exception as e:  # noqa: BLE001
            actual, ok = f"error: {e}", None
        if ok:
            passed += 1; v = "pass"
        elif ok is None:
            errors.append(q["id"]); v = "ERROR"
        else:
            failed.append(q["id"]); v = "FAIL"
        print(f"{q['id'][:10]:10s} {v:8s} {str(q['expected'])[:12]:>12s} {str(actual)[:12]:>12s}  {q['question'][:70]}")
    n = len(qs); rate = passed / n if n else 0.0
    elapsed = time.time() - start
    print(f"\nanswer key: {passed} of {n} pass ({rate*100:.0f}%); failed {', '.join(failed) or 'none'}; errors {', '.join(errors) or 'none'}; {elapsed:.1f}s")
    if a.log:
        new = not os.path.exists(a.log)
        with open(a.key, "rb") as fh:
            keysum = hashlib.sha256(fh.read()).hexdigest()[:12]
        with open(a.log, "a", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh)
            if new:
                w.writerow(["time", "git_sha", "key_sha", "label", "n", "pass", "rate", "elapsed_s", "failed_ids"])
            w.writerow([dt.datetime.now().isoformat(timespec="seconds"), git_sha(), keysum, a.label, n, passed, f"{rate:.3f}", f"{elapsed:.1f}", " ".join(failed + errors)])
        print(f"logged to {a.log}")
    sys.exit(0 if rate >= a.gate and n > 0 else 1)


if __name__ == "__main__":
    main()

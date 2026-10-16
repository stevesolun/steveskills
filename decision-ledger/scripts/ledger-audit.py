#!/usr/bin/env python3
"""ledger-audit: prove every live decision in a ledger is honoured by an artifact.

Usage:
  ledger-audit.py LEDGER.md ARTIFACT [ARTIFACT ...]
  ledger-audit.py LEDGER.md spec.md issues/*.md --min-words 4

The ledger holds one entry per line:
  D<n> | <source> | <decision> | supersedes D<m>
An entry is live until a later entry supersedes it. For each live entry the
script searches the artifacts for a hit and reports the file and line:
  - an explicit reference to the entry, such as "(D7)" or "ledger D7", or
  - a literal run of the decision's words (the whole sentence when short,
    otherwise at least --min-words consecutive words, case and punctuation
    ignored).
Verdicts: honoured (hit shown), superseded (skipped), missing. Exit code is 0
when nothing is missing, else 1, so it can gate a publish.
"""
import argparse
import re
import sys

ENTRY = re.compile(r"^\s*D(\d+)\s*\|\s*(.*?)\s*\|\s*(.*?)(?:\s*\|\s*supersedes\s+D(\d+))?\s*$", re.I)


def norm(s):
    return re.sub(r"[^a-z0-9 ]+", " ", s.lower()).split()


def parse_ledger(text):
    entries = []
    for raw in text.splitlines():
        m = ENTRY.match(raw)
        if m:
            entries.append({
                "id": int(m.group(1)),
                "source": m.group(2),
                "decision": m.group(3).strip(),
                "supersedes": int(m.group(4)) if m.group(4) else None,
            })
    superseded = {e["supersedes"] for e in entries if e["supersedes"]}
    for e in entries:
        e["live"] = e["id"] not in superseded
    return entries


def find_hit(entry, files, min_words):
    did = entry["id"]
    ref = re.compile(rf"\bD{did}\b")
    words = norm(entry["decision"])
    need = min(len(words), max(min_words, 1))
    # every window of `need` consecutive words, longest first keeps the report readable
    windows = [" ".join(words[i:i + need]) for i in range(len(words) - need + 1)] or [" ".join(words)]
    for path, lines in files:
        for lineno, line in enumerate(lines, 1):
            if ref.search(line):
                return path, lineno, f"reference D{did}", line.strip()
    for path, lines in files:
        for lineno, line in enumerate(lines, 1):
            nl = " " + " ".join(norm(line)) + " "
            for w in windows:
                if f" {w} " in nl:
                    return path, lineno, f'"{w}"', line.strip()
    return None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("ledger")
    ap.add_argument("artifacts", nargs="+")
    ap.add_argument("--min-words", type=int, default=5, help="consecutive words that count as a literal hit (default 5)")
    args = ap.parse_args()

    entries = parse_ledger(open(args.ledger, encoding="utf-8", errors="replace").read())
    if not entries:
        print(f"no ledger entries found in {args.ledger} (expected lines like 'D1 | source | decision')")
        sys.exit(2)
    files = [(p, open(p, encoding="utf-8", errors="replace").read().splitlines()) for p in args.artifacts]

    live = [e for e in entries if e["live"]]
    honoured, missing = [], []
    for e in live:
        hit = find_hit(e, files, args.min_words)
        (honoured if hit else missing).append((e, hit))

    label = ", ".join(args.artifacts) if len(args.artifacts) <= 3 else f"{args.artifacts[0]} +{len(args.artifacts) - 1} files"
    print(f"ledger audit: {label}")
    print(f"honoured {len(honoured)} of {len(live)} live; superseded {len(entries) - len(live)}; missing {len(missing)}")
    for e, hit in honoured:
        path, lineno, how, line = hit
        print(f"  D{e['id']:<3} honoured  {path}:{lineno}  {how}")
    for e, _ in missing:
        print(f"  D{e['id']:<3} MISSING   {e['decision'][:110]}")
    sys.exit(1 if missing else 0)


if __name__ == "__main__":
    main()

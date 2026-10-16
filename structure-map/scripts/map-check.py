#!/usr/bin/env python3
"""map-check: run every proof in a structure map and report confirmed and stale.

Usage:
  map-check.py docs/STRUCTURE.md [options]

Options:
  --cap N        line cap for the map file (default 60)
  --timeout SEC  per proof command (default 60)
  --root DIR     directory to run the proofs in (default: the git top level
                 of the map file's directory)

The map is a markdown file whose entries are list items of the form
  - <fact, one sentence> | proof: `<command>` | expect: <output>
Each proof runs through bash in the repository root, read-only: a command
that could write, move, delete, install or push is refused and counts as
stale. The expect field is matched against the command's output like this:
  `fragment`        every backticked fragment appears in the output,
                    whitespace collapsed, case kept
  42                a bare integer equals the whole output, or the number
                    of non-empty output lines
  empty             the output is empty
  exit 1            the command's exit code is 1 (combines with the others)
  anything else     the whole text appears in the output
An entry with no proof, no expect, a refused command, a timeout or an output
that does not match is stale, and its command and actual output are printed
under it.

Output ends with:
  confirmed C, stale S
Exit code: 0 when stale is 0, the map has at least one entry and is within
the line cap; 1 otherwise; 2 when the map file is missing.
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

ENTRY = re.compile(r"^\s*[-*]\s+(?P<fact>.+?)\s*\|\s*proof:\s*(?P<proof>.+?)\s*\|\s*expect:\s*(?P<expect>.+?)\s*$")
LOOSE_ENTRY = re.compile(r"^\s*[-*]\s+(?P<fact>.+)$")
FENCE = re.compile(r"^\s*(```|~~~)")
WRITES = re.compile(
    r"(?<![\w./-])(?:rm|rmdir|mv|cp|dd|mkfs|chmod|chown|truncate|tee|sudo|curl|wget|pip3?|npm|npx|yarn|apt(?:-get)?|kill|shred|ln|eval|exec)\b"
    r"|\bsed\s+(?:-[a-zA-Z]*i|--in-place)"
    r"|\bgit\s+(?:add|am|apply|branch\s+-[dDmM]|checkout|clean|commit|fetch|merge|pull|push|rebase|reset|restore|rm|stash|switch|worktree)\b"
    r"|(?<![2&<])>(?!\s*/dev/null)|>>|&>"
)
WRITES_IN_CODE = re.compile(r"open\([^)]*['\"][wa]|os\.(?:remove|unlink|rename|rmdir|makedirs|mkdir)|shutil\.|write_text|write_bytes|subprocess")
QUOTED = re.compile(r"\"(?:[^\"\\]|\\.)*\"|'[^']*'")
EXIT = re.compile(r"\bexit\s+(\d+)\b")


def squeeze(s: str) -> str:
    return " ".join(s.split())


INTERPRETER = re.compile(r"(?<![\w./-])(?:python[0-9.]*|node|ruby|perl|php)\b|\b(?:bash|sh|zsh|dash)\s+-[a-z]*c\b")


def refused(cmd: str) -> bool:
    """A command that could write, move, delete, install or push is not a proof."""
    if WRITES.search(QUOTED.sub(" ", cmd)):
        return True
    return bool(INTERPRETER.search(cmd) and WRITES_IN_CODE.search(cmd))


def matches(expect: str, out: str, code: int) -> tuple[bool, str]:
    """Does the output satisfy the expect field? Returns (ok, reason)."""
    e = expect.strip()
    text = squeeze(out)
    lines = [ln for ln in out.splitlines() if ln.strip()]
    reasons: list[str] = []
    rest = e
    for m in EXIT.finditer(e):
        if code != int(m.group(1)):
            reasons.append(f"exit code was {code}")
    rest = EXIT.sub(" ", rest)
    fragments = re.findall(r"`([^`]+)`", rest)
    rest = re.sub(r"`[^`]+`", " ", rest)
    for frag in fragments:
        if squeeze(frag) not in text:
            reasons.append(f"`{frag}` not in output")
    plain = squeeze(re.sub(r"\b(?:and|then|or|,)\b", " ", rest)).strip(" ,;")
    if plain:
        if re.fullmatch(r"\d+", plain):
            n = int(plain)
            if not (text == str(n) or len(lines) == n):
                reasons.append(f"expected {n}, output was {text[:60]!r} ({len(lines)} lines)")
        elif re.fullmatch(r"(?:empty|no output|nothing)", plain, re.I):
            if text:
                reasons.append("expected empty output")
        elif not fragments and not EXIT.search(e):
            if plain not in text:
                reasons.append(f"{plain!r} not in output")
    return (not reasons), "; ".join(reasons)


def main() -> int:
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("map", nargs="?")
    ap.add_argument("--cap", type=int, default=60)
    ap.add_argument("--timeout", type=int, default=60)
    ap.add_argument("--root")
    ap.add_argument("-h", "--help", action="store_true")
    args = ap.parse_args()
    if args.help or not args.map:
        print(__doc__.strip())
        return 0 if args.help else 2
    path = Path(args.map)
    if not path.is_file():
        print(f"map-check: no such file: {path}", file=sys.stderr)
        return 2
    if args.root:
        root = Path(args.root)
    else:
        top = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=path.resolve().parent, capture_output=True, text=True, check=False)
        root = Path(top.stdout.strip()) if top.returncode == 0 else path.resolve().parent
    text = path.read_text(encoding="utf-8")
    total_lines = len(text.splitlines())
    print(f"map: {path} ({total_lines} lines, cap {args.cap})")

    env = dict(os.environ, GIT_PAGER="cat", PAGER="cat", TERM="dumb")
    confirmed = stale = 0
    in_fence = False
    for lineno, line in enumerate(text.splitlines(), 1):
        if FENCE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        m = ENTRY.match(line)
        loose = LOOSE_ENTRY.match(line)
        if not m and not loose:
            continue
        if not m:
            fact = loose.group("fact")
            head = squeeze(re.split(r"\s*\|\s*", fact)[0])[:70]
            why = "no proof command" if "proof:" not in fact else "no expect field"
            print(f"STALE      L{lineno:<4} {head}")
            print(f"  reason: {why}")
            stale += 1
            continue
        fact, proof, expect = m.group("fact"), m.group("proof"), m.group("expect")
        cmd = " ; ".join(c.strip() for c in re.findall(r"`([^`]+)`", proof)) or proof.strip()
        head = squeeze(fact)[:70]
        if refused(cmd):
            print(f"STALE      L{lineno:<4} {head}")
            print(f"  proof:  {cmd}")
            print(f"  reason: refused, the command could change the tree or the network")
            stale += 1
            continue
        try:
            proc = subprocess.run(["bash", "-c", cmd], cwd=root, env=env, capture_output=True, text=True, timeout=args.timeout, check=False)
            out, code = proc.stdout + (("\n" + proc.stderr) if proc.stderr.strip() else ""), proc.returncode
            ok, reason = matches(expect, out, code)
        except subprocess.TimeoutExpired:
            out, code, ok, reason = "", -1, False, f"timed out after {args.timeout}s"
        if ok:
            print(f"confirmed  L{lineno:<4} {head}")
            confirmed += 1
            continue
        stale += 1
        print(f"STALE      L{lineno:<4} {head}")
        print(f"  proof:  {cmd}")
        print(f"  expect: {expect}")
        shown = [ln for ln in out.splitlines() if ln.strip()][:6]
        print(f"  actual: {shown[0] if shown else '(empty)'}" + (f"  [exit {code}]" if code else ""))
        for extra in shown[1:]:
            print(f"          {extra}")
        print(f"  reason: {reason}")

    print()
    print(f"confirmed {confirmed}, stale {stale}")
    over = total_lines > args.cap
    if over:
        print(f"map is {total_lines} lines, over the cap of {args.cap}")
    return 0 if stale == 0 and confirmed > 0 and not over else 1


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Rank a session's tool results by size, repeats and errors.

Usage:
  rank-tool-results.py [--log PATH] [--top N] [--json]

Without --log, picks the newest session log it can find for the current
directory: Claude Code (~/.claude/projects/<cwd-slug>/*.jsonl) or Codex
(~/.codex/sessions/**/*.jsonl). Any JSONL whose records carry
tool_use/tool_result (Anthropic shape) or function_call/function_call_output
(OpenAI shape) blocks works; wrapper fields around them are ignored.

Tokens are estimated at four characters per token. Stdlib only.
"""

import argparse
import glob
import json
import os
import sys
from collections import defaultdict

CHARS_PER_TOKEN = 4
TRUNCATION_MARKERS = ("Output too large", "persisted-output", "[truncated]")
SIGNATURE_KEYS = ("file_path", "command", "pattern", "query", "url", "path",
                  "notebook_path", "skill", "prompt", "cmd", "old_string",
                  "offset", "limit")


def find_log():
    """Newest Claude Code log for this cwd, else newest Codex rollout."""
    home = os.path.expanduser("~")
    slug = os.getcwd().replace("/", "-").replace("\\", "-")
    candidates = glob.glob(os.path.join(home, ".claude", "projects", slug, "*.jsonl"))
    candidates += glob.glob(os.path.join(home, ".codex", "sessions", "**", "*.jsonl"),
                            recursive=True)
    if not candidates:
        return None
    return max(candidates, key=os.path.getmtime)


def text_size(content):
    """Characters of text in a result payload (string, list of blocks, or other)."""
    if content is None:
        return 0
    if isinstance(content, str):
        return len(content)
    if isinstance(content, list):
        total = 0
        for block in content:
            if isinstance(block, dict):
                total += len(block.get("text") or "")
                if block.get("type") == "image":
                    total += 1500 * CHARS_PER_TOKEN  # images cost real tokens too
            else:
                total += len(str(block))
        return total
    return len(json.dumps(content))


def text_sample(content, limit=400):
    if isinstance(content, str):
        return content[:limit]
    if isinstance(content, list):
        return " ".join((b.get("text") or "") if isinstance(b, dict) else str(b)
                        for b in content)[:limit]
    return json.dumps(content)[:limit]


def signature(name, inputs):
    """Tool name plus the one input that identifies the call (full value, so
    two calls only count as a repeat when they really are the same call)."""
    if isinstance(inputs, str):
        try:
            inputs = json.loads(inputs)
        except ValueError:
            return f"{name} {inputs}"
    if not isinstance(inputs, dict):
        return name
    parts = [f"{key}={inputs[key]}" for key in SIGNATURE_KEYS
             if isinstance(inputs.get(key), (str, int)) and inputs.get(key) != ""]
    if parts:
        return f"{name} {' '.join(parts)}"
    for value in inputs.values():
        if isinstance(value, str) and value:
            return f"{name} {value}"
    return name


def walk(node, calls, results):
    """Collect tool calls and results from any nesting of dicts and lists."""
    if isinstance(node, dict):
        kind = node.get("type")
        if kind == "tool_use" and "id" in node:
            calls[node["id"]] = (node.get("name", "?"), node.get("input"))
        elif kind == "function_call" and "call_id" in node:
            calls[node["call_id"]] = (node.get("name", "?"), node.get("arguments"))
        elif kind == "tool_result" and "tool_use_id" in node:
            results.append((node["tool_use_id"], node.get("content"),
                            bool(node.get("is_error"))))
        elif kind == "function_call_output" and "call_id" in node:
            results.append((node["call_id"], node.get("output"), False))
        for value in node.values():
            walk(value, calls, results)
    elif isinstance(node, list):
        for item in node:
            walk(item, calls, results)


def load(path):
    calls, results = {}, []
    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                walk(json.loads(line), calls, results)
            except json.JSONDecodeError:
                continue
    return calls, results


def analyse(calls, results):
    rows = []
    for call_id, content, is_error in results:
        name, inputs = calls.get(call_id, ("?", None))
        sample = text_sample(content)
        rows.append({
            "tokens": text_size(content) // CHARS_PER_TOKEN,
            "tool": name,
            "call": signature(name, inputs),
            "error": is_error,
            "truncated": any(m in sample for m in TRUNCATION_MARKERS),
        })
    by_call, by_tool = defaultdict(list), defaultdict(list)
    for row in rows:
        by_call[row["call"]].append(row["tokens"])
        by_tool[row["tool"]].append(row["tokens"])
    for row in rows:
        row["repeats"] = len(by_call[row["call"]])
    total = sum(r["tokens"] for r in rows) or 1
    return {
        "calls": len(rows),
        "total_tokens": total,
        "results": sorted(rows, key=lambda r: r["tokens"], reverse=True),
        "repeated": sorted(
            [{"call": c, "count": len(t), "tokens": sum(t)}
             for c, t in by_call.items() if len(t) > 1],
            key=lambda r: r["tokens"], reverse=True),
        "by_tool": sorted(
            [{"tool": n, "calls": len(t), "tokens": sum(t), "share": sum(t) / total}
             for n, t in by_tool.items()],
            key=lambda r: r["tokens"], reverse=True),
    }


def flags(row):
    out = []
    if row["repeats"] > 1:
        out.append(f"repeat x{row['repeats']}")
    if row["error"]:
        out.append("error")
    if row["truncated"]:
        out.append("truncated+persisted")
    return ", ".join(out)


def report(path, data, top):
    print(f"Log: {path}")
    print(f"Tool results: {data['calls']}  Estimated tokens: {data['total_tokens']:,}")
    head = data["results"][:top]
    print(f"\nLargest results (top {len(head)}, "
          f"{sum(r['tokens'] for r in head) / data['total_tokens']:.0%} of all result tokens)")
    print(f"{'tokens':>8}  {'tool':<16} {'flags':<22} call")
    for row in head:
        print(f"{row['tokens']:>8,}  {row['tool'][:16]:<16} {flags(row):<22} {row['call'][:70]}")
    if data["repeated"]:
        print("\nRepeated calls (same call, same input)")
        for row in data["repeated"][:top]:
            print(f"{row['tokens']:>8,}  x{row['count']:<3} {row['call'][:80]}")
    truncated = [r for r in data["results"] if r["truncated"]]
    if truncated:
        print("\nTruncated results (the full output was saved to a file, so reading it pays twice)")
        for row in truncated[:top]:
            print(f"{row['tokens']:>8,}  {row['tool'][:16]:<16} {row['call'][:70]}")
    print("\nBy tool")
    for row in data["by_tool"][:top]:
        print(f"{row['tokens']:>8,}  {row['share']:>5.0%}  {row['calls']:>4} calls  {row['tool']}")


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--log", help="session log (JSONL); default: newest found")
    parser.add_argument("--top", type=int, default=15, help="rows per table (default 15)")
    parser.add_argument("--json", action="store_true", help="emit JSON instead of text")
    args = parser.parse_args()

    if args.log and not os.path.isfile(args.log):
        sys.exit(f"No file at {args.log}.")
    path = args.log or find_log()
    if not path:
        sys.exit("No session log found for this directory. Pass --log PATH (a JSONL session log).")
    calls, results = load(path)
    if not results:
        sys.exit(f"No tool results recognised in {path}. "
                 "Expected tool_use/tool_result or function_call/function_call_output records.")
    data = analyse(calls, results)
    if args.json:
        data["log"] = path
        json.dump(data, sys.stdout, indent=2)
        print()
    else:
        report(path, data, args.top)


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:  # output piped into head or similar
        sys.exit(0)

#!/usr/bin/env python3
"""whose-red: say whose red a failing test is, from runs rather than words.

Usage:
  whose-red.py BASE [TEST_ID ...] [options]

  BASE       the commit the change grew from (sha, branch, tag, "main", ...)
  TEST_ID    failing test ids in the runner's file::name form; with none
             given, the script runs the suite itself (see --paths) and takes
             every FAILED and ERROR id from that run

Options:
  --paths P [P ...]   files or directories for the suite run that finds the
                      failing ids (default: the runner's configured paths)
  --runs N            isolated runs per test at the working tree (default 3)
  --import-root DIR   directory the project imports from, relative to the
                      repository root (default: src when it holds a package,
                      else the root)
  --runner-arg ARG    extra runner argument, repeatable
  --timeout SEC       per runner invocation (default 1800)

Verdicts, one per failing test:
  mine          fails at the working tree, passes at BASE in a throwaway
                worktree (or did not exist at BASE and names no environment
                cause): the change broke it, or the change wrote it broken
  pre-existing  fails at BASE too, for a reason the code owns
  flaky         N isolated runs at the working tree do not agree with each
                other, or all pass although the suite run failed it
  environment   the failure text names a missing binary, module, network,
                permission or sandbox, and BASE fails or lacks the test too

The base run uses the base implementation with the working tree's test
files copied over it, the import path pinned to the worktree and the
project module's resolved path printed, so the verdict is about the code
and not about an editable install pointing elsewhere.

Output: one table row per test, then
  failing N: mine a, pre-existing b, flaky c, environment d
Exit code: 1 when any row says mine, 0 otherwise, 2 on setup errors.
Needs: python3, git, and the test runner (pytest) on the path.
"""
from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

TEST_FILE = re.compile(r"(?:^|/)(?:tests?|testing)/.*\.py$|(?:^|/)(?:test_[^/]*|[^/]*_test|conftest)\.py$")
VERBOSE_LINE = re.compile(r"^(\S+::\S+)\s+(PASSED|FAILED|ERROR|SKIPPED|XFAIL|XPASS)\b")
SUMMARY_LINE = re.compile(r"^(FAILED|ERROR)\s+(\S+)(?:\s+-\s+(.*))?$")
ENVIRONMENT_CAUSES = [
    (re.compile(r"ModuleNotFoundError|No module named"), "missing module"),
    (re.compile(r"command not found|not found in PATH|No such file or directory: '[^/']*'|executable .* not found"), "missing binary"),
    (re.compile(r"PermissionError|Permission denied|Operation not permitted|EACCES|EPERM|Read-only file system"), "permission"),
    (re.compile(r"Connection refused|Name or service not known|Network is unreachable|Temporary failure in name resolution|ConnectionError|certificate verify failed|getaddrinfo"), "network"),
    (re.compile(r"sandbox|bwrap|Bubblewrap|container|docker", re.I), "sandbox"),
    (re.compile(r"is unavailable|not installed|is not available|not supported on this platform"), "unavailable"),
]


def sh(cmd: list[str], cwd: Path, env: dict[str, str] | None = None, timeout: int = 1800) -> subprocess.CompletedProcess:
    full = dict(os.environ)
    if env:
        full.update(env)
    return subprocess.run(cmd, cwd=str(cwd), env=full, capture_output=True, text=True, timeout=timeout, check=False)


def git(cwd: Path, *args: str) -> str:
    return sh(["git", *args], cwd).stdout


def die(msg: str) -> None:
    print(f"whose-red: {msg}", file=sys.stderr)
    sys.exit(2)


def guess_import_root(root: Path) -> str:
    src = root / "src"
    if src.is_dir() and any(p.is_dir() and (p / "__init__.py").is_file() for p in src.iterdir()):
        return "src"
    return "."


def run_one(cwd: Path, test_id: str, env: dict[str, str], runner_args: list[str], timeout: int) -> tuple[str, str]:
    """(status, runner text) for one id in its own runner process.

    status is PASSED, FAILED (an assertion, an error, or a file that would not
    collect), SKIPPED, or ABSENT (the runner knows no such test here)."""
    proc = sh([sys.executable, "-m", "pytest", "-p", "no:cacheprovider", "-v", "-rfE", "--tb=short", "--no-header", *runner_args, test_id], cwd, env, timeout)
    combined = proc.stdout + "\n" + proc.stderr
    status = ""
    for line in proc.stdout.splitlines():
        m = VERBOSE_LINE.match(line.strip())
        if m and m.group(1) == test_id:
            status = m.group(2)
    if status in ("PASSED", "XPASS"):
        return "PASSED", combined
    if status in ("FAILED", "ERROR"):
        return "FAILED", combined
    if status in ("SKIPPED", "XFAIL"):
        return "SKIPPED", combined
    if re.search(r"ERROR: not found|no collectors|no tests ran", combined):
        return "ABSENT", combined
    return "FAILED", combined


def environment_cause(text: str) -> str:
    """The first environment cause the failure text names, with the words around it."""
    for pattern, label in ENVIRONMENT_CAUSES:
        for line in text.splitlines():
            m = pattern.search(line)
            if m:
                clean = re.sub(r"^E\s+", "", line.strip())
                at = max(m.start() - 40, 0)
                snippet = ("..." if at else "") + clean[at:at + 100].strip()
                return f"{label}: {snippet}"
    return ""


def failing_ids_from_suite(root: Path, paths: list[str], env: dict[str, str], runner_args: list[str], timeout: int) -> list[str]:
    proc = sh([sys.executable, "-m", "pytest", "-p", "no:cacheprovider", "-q", "-rfE", "--no-header", *runner_args, *paths], root, env, timeout)
    ids: list[str] = []
    for line in proc.stdout.splitlines():
        m = SUMMARY_LINE.match(line.strip())
        if m and "::" in m.group(2) and m.group(2) not in ids:
            ids.append(m.group(2))
    tail = proc.stdout.strip().splitlines()[-1] if proc.stdout.strip() else proc.stderr.strip()[-200:]
    print(f"suite run at the working tree: {tail.strip('= ')}")
    return ids


def main() -> int:
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("base", nargs="?")
    ap.add_argument("ids", nargs="*")
    ap.add_argument("--paths", nargs="+", default=[])
    ap.add_argument("--runs", type=int, default=3)
    ap.add_argument("--import-root")
    ap.add_argument("--runner-arg", action="append", default=[])
    ap.add_argument("--timeout", type=int, default=1800)
    ap.add_argument("-h", "--help", action="store_true")
    args = ap.parse_args()
    if args.help or not args.base:
        print(__doc__.strip())
        return 0 if args.help else 2

    top = sh(["git", "rev-parse", "--show-toplevel"], Path.cwd())
    if top.returncode != 0:
        die("not inside a git repository")
    root = Path(top.stdout.strip())
    sha_proc = sh(["git", "rev-parse", "--verify", "-q", f"{args.base}^{{commit}}"], root)
    if sha_proc.returncode != 0:
        die(f"unknown base commit: {args.base}")
    sha = sha_proc.stdout.strip()
    short = sha[:8]
    import_root = args.import_root or guess_import_root(root)
    head_env = {"PYTHONPATH": str(root / import_root)}

    ids = list(args.ids) or failing_ids_from_suite(root, args.paths, head_env, args.runner_arg, args.timeout)
    if not ids:
        print(f"failing 0: mine 0, pre-existing 0, flaky 0, environment 0")
        return 0

    # Isolated runs at the working tree.
    head_runs: dict[str, list[str]] = {}
    head_text: dict[str, str] = {}
    for tid in ids:
        outcomes: list[str] = []
        for _ in range(max(args.runs, 1)):
            status, text = run_one(root, tid, head_env, args.runner_arg, args.timeout)
            outcomes.append(status)
            if status != "PASSED":
                head_text[tid] = text
        head_runs[tid] = outcomes

    # One base worktree for every test that still needs it.
    need_base = [tid for tid in ids if all(o == "FAILED" for o in head_runs[tid])]
    base_status: dict[str, str] = {}
    base_text: dict[str, str] = {}
    if need_base:
        wt = Path(tempfile.mkdtemp(prefix="whose-red-"))
        added = sh(["git", "worktree", "add", "--detach", str(wt), sha], root)
        if added.returncode != 0:
            shutil.rmtree(wt, ignore_errors=True)
            die(f"could not add a worktree at {short}: {added.stderr.strip()}")
        try:
            touched = {p for p in git(root, "diff", "--name-only", sha).split("\n") if p.strip()}
            touched |= {p for p in git(root, "ls-files", "--others", "--exclude-standard").split("\n") if p.strip()}
            for f in sorted(p for p in touched if TEST_FILE.search(p)):
                src, dst = root / f, wt / f
                if src.is_file():
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(src, dst)
                elif dst.exists():
                    dst.unlink()
            wt_env = {"PYTHONPATH": str(wt / import_root)}
            packages = sorted(p.name for p in (wt / import_root).iterdir() if p.is_dir() and (p / "__init__.py").is_file() and p.name not in ("tests", "test", "testing"))[:1]
            for name in packages:
                probe = sh([sys.executable, "-c", "import importlib,sys; print(importlib.import_module(sys.argv[1]).__file__)", name], wt, wt_env)
                where = probe.stdout.strip() or "import failed"
                print(f"base worktree {short}: module {name} resolves to {where}")
                if where.startswith("/") and not where.startswith(str(wt) + os.sep):
                    die(f"{name} imports from outside the worktree; the base run would grade the wrong code")
            for tid in need_base:
                base_status[tid], base_text[tid] = run_one(wt, tid, wt_env, args.runner_arg, args.timeout)
        finally:
            sh(["git", "worktree", "remove", "--force", str(wt)], root)
            shutil.rmtree(wt, ignore_errors=True)
            sh(["git", "worktree", "prune"], root)

    # Verdicts.
    rows: list[tuple[str, str, str, str, str]] = []
    counts = {"mine": 0, "pre-existing": 0, "flaky": 0, "environment": 0}
    for tid in ids:
        outcomes = head_runs[tid]
        fails = sum(1 for o in outcomes if o == "FAILED")
        head_col = f"{fails}/{len(outcomes)} fail"
        if fails == 0:
            verdict, base_col, note = "flaky", "not run", f"passed {len(outcomes)} of {len(outcomes)} alone, failed in the suite run"
        elif fails < len(outcomes):
            verdict, base_col, note = "flaky", "not run", "outcomes " + ",".join(o[0] for o in outcomes)
        else:
            at_base = base_status.get(tid, "not run")
            cause = environment_cause(head_text.get(tid, ""))
            if at_base == "PASSED":
                verdict, note = "mine", "passes at base, fails here"
            elif at_base == "FAILED":
                verdict, note = ("environment", cause) if cause else ("pre-existing", "fails at base too")
            else:
                verdict, note = ("environment", cause) if cause else ("mine", f"{at_base.lower()} at base: the test is this change's")
            base_col = {"PASSED": "pass", "FAILED": "fail", "SKIPPED": "skipped", "ABSENT": "absent"}.get(at_base, at_base)
        counts[verdict] += 1
        rows.append((verdict, tid, head_col, base_col, note))

    print()
    print("| verdict | test | head | base | note |")
    print("| --- | --- | --- | --- | --- |")
    for verdict, tid, head_col, base_col, note in rows:
        print(f"| {verdict} | {tid} | {head_col} | {base_col} | {note} |")
    print()
    print(f"failing {len(ids)}: mine {counts['mine']}, pre-existing {counts['pre-existing']}, flaky {counts['flaky']}, environment {counts['environment']}")
    return 1 if counts["mine"] else 0


if __name__ == "__main__":
    sys.exit(main())

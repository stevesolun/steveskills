#!/usr/bin/env python3
"""red-at-base: rerun every new or changed test at the base commit, in a
throwaway worktree, and count how many fail there.

Usage:
  red-at-base.py BASE [PATH ...] [options]

  BASE          the commit the change grew from: a sha, a branch, a tag, or
                an expression such as "main" or "HEAD~3"
  PATH          test files or directories to restrict the set to; default is
                every test file changed or added since BASE (working tree,
                uncommitted work included)

Options:
  --import-root DIR   directory the project's packages import from, relative
                      to the repository root (default: src when it holds a
                      package, else the root)
  --runner-arg ARG    extra argument for the test runner, repeatable
                      (for example --runner-arg=--no-cov)
  --timeout SEC       per runner invocation (default 1800)
  --keep              leave the worktree in place for inspection

What it does, in order:
  1. lists the test files the diff touches, collects test ids at the working
     tree and at BASE, and strips parametrised suffixes such as "[case-1]"
     before comparing, so a parametrised test counts once;
  2. names M: ids that are new at the working tree, plus ids whose body a
     diff hunk lands in;
  3. adds a worktree at BASE, copies the working tree's test files and
     helpers over it, pins the import path to the worktree, and prints where
     the project module resolves; a module that resolves outside the
     worktree aborts the run (exit 2) instead of grading the wrong code;
  4. runs exactly M there, by id, and reads each verdict from the runner:
     red (assertion failed), error (could not run at BASE), green (passed);
  5. removes the worktree and prints the headline and the id list.

Headline:
  N of M new or changed tests fail at base (<sha>): R red, E error, G green

Exit code: 0 only when G is 0 (a test that is green at base is a finding),
1 when any test is green at base, 2 on usage or setup errors.
Needs: python3, git, and the test runner (pytest) on the path.
"""
from __future__ import annotations

import argparse
import ast
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

TEST_FILE = re.compile(r"(?:^|/)(?:tests?|testing)/.*\.py$|(?:^|/)(?:test_[^/]*|[^/]*_test|conftest)\.py$")
TEST_CASE_FILE = re.compile(r"(?:^|/)(?:test_[^/]*|[^/]*_test)\.py$")
VERBOSE_LINE = re.compile(r"^(\S+::\S+)\s+(PASSED|FAILED|ERROR|SKIPPED|XFAIL|XPASS)\b")
SUMMARY_LINE = re.compile(r"^(FAILED|ERROR)\s+(\S+)(?:\s+-\s+(.*))?$")
IMPORT_LINE = re.compile(r"^\s*(?:from\s+([A-Za-z_][\w]*)|import\s+([A-Za-z_][\w]*))", re.M)


def sh(cmd: list[str], cwd: Path, env: dict[str, str] | None = None, timeout: int = 1800) -> subprocess.CompletedProcess:
    full = dict(os.environ)
    if env:
        full.update(env)
    return subprocess.run(cmd, cwd=str(cwd), env=full, capture_output=True, text=True, timeout=timeout, check=False)


def git(cwd: Path, *args: str) -> str:
    proc = sh(["git", *args], cwd)
    return proc.stdout


def die(msg: str, code: int = 2) -> None:
    print(f"red-at-base: {msg}", file=sys.stderr)
    sys.exit(code)


def bare_id(test_id: str) -> str:
    """The id with its parametrised suffix removed: a[x-1] and a[x-2] are one test."""
    return re.sub(r"\[.*\]$", "", test_id)


def worktree_count(root: Path) -> int:
    return sum(1 for ln in git(root, "worktree", "list", "--porcelain").splitlines() if ln.startswith("worktree "))


def changed_paths(root: Path, base: str) -> list[str]:
    tracked = git(root, "diff", "--name-only", base).split("\n")
    untracked = git(root, "ls-files", "--others", "--exclude-standard").split("\n")
    return sorted({p for p in tracked + untracked if p.strip()})


def collect_ids(cwd: Path, files: list[str], env: dict[str, str], runner_args: list[str], timeout: int) -> tuple[list[str], str]:
    present = [f for f in files if (cwd / f).is_file()]
    if not present:
        return [], ""
    proc = sh([sys.executable, "-m", "pytest", "-p", "no:cacheprovider", "--collect-only", "-q", *runner_args, *present], cwd, env, timeout)
    ids = [ln.strip() for ln in proc.stdout.splitlines() if "::" in ln and not ln.startswith(" ")]
    note = ""
    if proc.returncode not in (0, 5):
        note = next((ln.strip() for ln in (proc.stdout + proc.stderr).splitlines() if "rror" in ln), "collection failed")
    return ids, note


def hunk_ranges(root: Path, base: str, path: str) -> list[tuple[int, int]]:
    """Line ranges on the working-tree side of each diff hunk for one file."""
    out = git(root, "diff", "-U0", base, "--", path)
    ranges: list[tuple[int, int]] = []
    for m in re.finditer(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@", out, re.M):
        start = int(m.group(1))
        count = int(m.group(2)) if m.group(2) is not None else 1
        ranges.append((start, start + max(count, 1) - 1))
    return ranges


def test_spans(root: Path, path: str) -> dict[str, tuple[int, int]]:
    """file::[Class::]name -> (first line, last line) at the working tree."""
    try:
        tree = ast.parse((root / path).read_text(encoding="utf-8"))
    except (SyntaxError, OSError):
        return {}
    spans: dict[str, tuple[int, int]] = {}

    def walk(node: ast.AST, prefix: str) -> None:
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)) and child.name.startswith("test"):
                first = min([child.lineno, *[d.lineno for d in child.decorator_list]])
                spans[f"{path}::{prefix}{child.name}"] = (first, child.end_lineno or child.lineno)
            elif isinstance(child, ast.ClassDef) and child.name.startswith("Test"):
                walk(child, f"{prefix}{child.name}::")

    walk(tree, "")
    return spans


def project_modules(root: Path, files: list[str], import_root: Path) -> list[str]:
    """Top-level names the test files import that live under the import root."""
    names: list[str] = []
    for f in files:
        try:
            text = (root / f).read_text(encoding="utf-8")
        except OSError:
            continue
        for m in IMPORT_LINE.finditer(text):
            name = m.group(1) or m.group(2)
            if name not in names and ((import_root / name / "__init__.py").is_file() or (import_root / f"{name}.py").is_file()):
                names.append(name)
    if not names:
        # The tests reach the project through a subprocess or a fixture: resolve its packages instead.
        names = sorted(p.name for p in import_root.iterdir() if p.is_dir() and (p / "__init__.py").is_file() and p.name not in ("tests", "test", "testing"))[:2]
    return names


def guess_import_root(root: Path) -> str:
    src = root / "src"
    if src.is_dir() and any(p.is_dir() and (p / "__init__.py").is_file() for p in src.iterdir()):
        return "src"
    return "."


def main() -> int:
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("base", nargs="?")
    ap.add_argument("paths", nargs="*")
    ap.add_argument("--import-root")
    ap.add_argument("--runner-arg", action="append", default=[])
    ap.add_argument("--timeout", type=int, default=1800)
    ap.add_argument("--keep", action="store_true")
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
    import_root_rel = args.import_root or guess_import_root(root)

    # 1. The test files the diff touches (and helpers), restricted to PATH when given.
    touched = changed_paths(root, sha)
    test_files = [p for p in touched if TEST_FILE.search(p)]
    if args.paths:
        wanted = [os.path.relpath(os.path.abspath(p), root) for p in args.paths]
        test_files = [p for p in test_files if any(p == w or p.startswith(w.rstrip("/") + "/") for w in wanted)]
    case_files = [p for p in test_files if TEST_CASE_FILE.search(p) and (root / p).is_file()]
    print(f"base: {short}  test files in diff: {len(test_files)}  ({', '.join(test_files) or 'none'})")
    if not case_files:
        print(f"no new or changed tests since {short}")
        print(f"0 of 0 new or changed tests fail at base ({short}): 0 red, 0 error, 0 green")
        return 0

    head_env = {"PYTHONPATH": str(root / import_root_rel)}
    head_ids, head_note = collect_ids(root, case_files, head_env, args.runner_arg, args.timeout)
    if head_note:
        print(f"collection at the working tree: {head_note}")

    before = worktree_count(root)
    wt = Path(tempfile.mkdtemp(prefix="red-at-base-"))
    added = sh(["git", "worktree", "add", "--detach", "-q", str(wt), sha], root)
    if added.returncode != 0:
        shutil.rmtree(wt, ignore_errors=True)
        die(f"could not add a worktree at {short}: {added.stderr.strip()}")
    try:
        wt_env = {"PYTHONPATH": str(wt / import_root_rel)}

        # 2. M: new ids (absent at base, parametrisation stripped) plus changed ids (a hunk in the body).
        base_ids, _ = collect_ids(wt, case_files, wt_env, args.runner_arg, args.timeout)
        base_bare = {bare_id(i) for i in base_ids}
        new_ids = [i for i in head_ids if bare_id(i) not in base_bare]
        changed_ids: list[str] = []
        for f in case_files:
            if not (wt / f).is_file():
                continue
            hunks = hunk_ranges(root, sha, f)
            for tid, (lo, hi) in test_spans(root, f).items():
                if tid in base_bare and any(h_lo <= hi and h_hi >= lo for h_lo, h_hi in hunks):
                    changed_ids.extend(i for i in head_ids if bare_id(i) == tid)
        changed_ids = sorted(set(changed_ids) - set(new_ids))
        m_ids = sorted(set(new_ids) | set(changed_ids))
        print(f"M = {len(m_ids)} ({len(new_ids)} new, {len(changed_ids)} changed)")

        # 3. The working tree's test files on top of the base implementation; import path pinned.
        for f in test_files:
            src, dst = root / f, wt / f
            if src.is_file():
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(src, dst)
            elif dst.exists():
                dst.unlink()
        print(f"import path pinned: PYTHONPATH={wt_env['PYTHONPATH']}")
        for name in project_modules(root, case_files, root / import_root_rel) or []:
            probe = sh([sys.executable, "-c", "import importlib,sys; print(importlib.import_module(sys.argv[1]).__file__)", name], wt, wt_env)
            where = probe.stdout.strip() or (probe.stderr.strip().splitlines() or ["import failed"])[-1]
            print(f"module {name} resolves to {where}")
            if where.startswith("/") and not where.startswith(str(wt) + os.sep):
                die(f"{name} imports from outside the worktree; the base run would grade the wrong code")

        # 4. Run exactly M at base, one runner process per file so a file that
        #    cannot be collected at base errors alone, and read each verdict.
        verdicts: dict[str, tuple[str, str]] = {}
        tails: list[str] = []
        for f in sorted({t.split("::")[0] for t in m_ids}):
            ids = [t for t in m_ids if t.split("::")[0] == f]
            proc = sh([sys.executable, "-m", "pytest", "-p", "no:cacheprovider", "-v", "-rfE", "--no-header", *args.runner_arg, *ids], wt, wt_env, args.timeout)
            status: dict[str, str] = {}
            notes: dict[str, str] = {}
            file_note = ""
            for line in proc.stdout.splitlines():
                m = VERBOSE_LINE.match(line.strip())
                if m:
                    status[m.group(1)] = m.group(2)
                sm = SUMMARY_LINE.match(line.strip())
                if sm and sm.group(3):
                    notes[sm.group(2)] = sm.group(3)
                if not file_note and line.startswith("E   "):
                    file_note = line[4:].strip()
            for tid in ids:
                st = status.get(tid)
                if st in ("PASSED", "XPASS"):
                    verdicts[tid] = ("green", st)
                elif st in ("SKIPPED", "XFAIL"):
                    verdicts[tid] = ("green", f"{st} at base, so it proved nothing")
                elif st == "FAILED":
                    verdicts[tid] = ("red", notes.get(tid, "assertion failed"))
                elif st == "ERROR":
                    verdicts[tid] = ("error", notes.get(tid, file_note or "could not run at base"))
                else:
                    verdicts[tid] = ("error", notes.get(tid) or file_note or "not collected at base")
            tail = proc.stdout.strip().splitlines()[-1] if proc.stdout.strip() else proc.stderr.strip()[-200:]
            tails.append(f"{f}: {tail.strip('= ')}")
        for t in tails:
            print(f"runner at base: {t}")
    finally:
        if args.keep:
            print(f"worktree kept at {wt}")
        else:
            sh(["git", "worktree", "remove", "--force", str(wt)], root)
            shutil.rmtree(wt, ignore_errors=True)
            sh(["git", "worktree", "prune"], root)
    after = worktree_count(root)

    # 5. Headline and list.
    red = [t for t, (v, _) in verdicts.items() if v == "red"]
    err = [t for t, (v, _) in verdicts.items() if v == "error"]
    green = [t for t, (v, _) in verdicts.items() if v == "green"]
    print()
    print(f"{len(red) + len(err)} of {len(m_ids)} new or changed tests fail at base ({short}): {len(red)} red, {len(err)} error, {len(green)} green")
    for t in red:
        print(f"red:   {t}")
    for t in err:
        print(f"error: {t}: {verdicts[t][1]}")
    for t in green:
        print(f"green: {t}" + (f" ({verdicts[t][1]})" if verdicts[t][1] != "PASSED" else ""))
    print(f"worktrees: {before} before, {after} after")
    return 0 if not green else 1


if __name__ == "__main__":
    sys.exit(main())

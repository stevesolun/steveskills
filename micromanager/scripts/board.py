#!/usr/bin/env python3
"""The micromanager's board: who holds which ticket, and whether their diff moved.

Usage:
  board.py init   (--from-dir DIR | --from-gh LABEL | --from-json FILE) [--seats N]
  board.py frontier                      # open tickets whose blockers are all closed
  board.py assign ID --worker NAME --worktree PATH
  board.py check [--stale-minutes M]     # fingerprint every worktree; exit 1 if anyone is stale
  board.py nudge ID [--note TEXT]        # record a nudge (rung 1), re-brief (2) or replacement (3)
  board.py claim-done ID                 # the worker says it is done; nothing closes yet
  board.py verify ID (--pass | --fail "REASON")
  board.py report                        # the numbers

State lives in .micromanager/board.json (override with --board). Progress is a
fingerprint of the worker's worktree (HEAD, index, working-tree diff), never the
worker's own words. Stdlib only.
"""

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import subprocess
import sys

STATUSES = ("open", "assigned", "claimed-done", "closed", "blocked-on-human")
DEFAULT_BOARD = os.path.join(".micromanager", "board.json")


def now():
    return dt.datetime.now(dt.timezone.utc)


def iso(t):
    return t.strftime("%Y-%m-%dT%H:%M:%SZ")


def parse(s):
    return dt.datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=dt.timezone.utc)


def minutes_since(s):
    return (now() - parse(s)).total_seconds() / 60 if s else None


# ---------------------------------------------------------------- state

def load(path):
    if not os.path.isfile(path):
        sys.exit(f"No board at {path}. Run: board.py init ...")
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def save(path, board):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(board, fh, indent=2)
    os.replace(tmp, path)


def ticket(board, tid):
    for t in board["tickets"]:
        if t["id"] == str(tid):
            return t
    sys.exit(f"No ticket {tid} on the board.")


def log(board, tid, event, **extra):
    board["events"].append({"at": iso(now()), "ticket": str(tid), "event": event, **extra})


# ---------------------------------------------------------------- tickets in

BLOCKED_RE = re.compile(r"blocked\s*by\s*:?\s*(.+)", re.I)


def blockers_from(text):
    """Ticket ids named on a 'Blocked by:' line: '#12', '01', '12-slug', 'none'."""
    ids = []
    for line in text.splitlines():
        m = BLOCKED_RE.search(line)
        if not m:
            continue
        rest = re.sub(r"[*_`]", "", m.group(1)).split("(")[0]
        for tok in re.findall(r"#?([A-Za-z0-9][\w-]*)", rest):
            if tok.lower() in ("none", "nothing", "and"):
                continue
            ids.append(re.match(r"\d+", tok).group(0).lstrip("0") or "0" if tok[0].isdigit() else tok)
    return ids


def from_dir(d):
    out = []
    for name in sorted(os.listdir(d)):
        if not name.endswith(".md"):
            continue
        with open(os.path.join(d, name), encoding="utf-8") as fh:
            text = fh.read()
        if not name[0].isdigit() and not BLOCKED_RE.search(text):
            continue  # README.md, STATE.md and the like are notes, not tickets
        title = next((l.lstrip("# ").strip() for l in text.splitlines() if l.startswith("#")), name)
        tid = re.match(r"(\d+)", name).group(1).lstrip("0") or "0" if re.match(r"\d", name) else name[:-3]
        out.append({"id": tid, "title": title, "source": os.path.join(d, name),
                    "blocked_by": blockers_from(text)})
    return out


def from_gh(label):
    cmd = ["gh", "issue", "list", "--label", label, "--state", "open", "--limit", "200",
           "--json", "number,title,body,url"]
    try:
        raw = subprocess.run(cmd, check=True, capture_output=True, text=True).stdout
    except (OSError, subprocess.CalledProcessError) as e:
        sys.exit(f"gh failed: {getattr(e, 'stderr', e)}")
    return [{"id": str(i["number"]), "title": i["title"], "source": i["url"],
             "blocked_by": blockers_from(i.get("body") or "")} for i in json.loads(raw)]


def from_json(path):
    with open(path, encoding="utf-8") as fh:
        items = json.load(fh)
    return [{"id": str(i["id"]), "title": i.get("title", ""), "source": i.get("source", path),
             "blocked_by": [str(b) for b in i.get("blocked_by", [])]} for i in items]


# ---------------------------------------------------------------- progress

def git(path, *args):
    return subprocess.run(["git", "-C", path, *args], capture_output=True, text=True).stdout


def fingerprint(path):
    """What the worker has actually changed: HEAD, staged, and unstaged work."""
    if not os.path.isdir(path):
        return None
    if git(path, "rev-parse", "--is-inside-work-tree").strip() == "true":
        parts = [git(path, "rev-parse", "HEAD"), git(path, "status", "--porcelain"),
                 git(path, "diff"), git(path, "diff", "--cached")]
    else:  # not a repo: file sizes and mtimes
        parts = []
        for root, dirs, files in os.walk(path):
            dirs[:] = [d for d in dirs if d not in (".git", "node_modules", ".venv", "__pycache__")]
            for f in files:
                p = os.path.join(root, f)
                try:
                    st = os.stat(p)
                except OSError:
                    continue
                parts.append(f"{p}:{st.st_size}:{int(st.st_mtime)}")
    return hashlib.sha1("\n".join(parts).encode("utf-8", "replace")).hexdigest()[:12]


def head(path):
    return git(path, "rev-parse", "HEAD").strip() or None


def changed_lines(path, base_sha):
    """Lines added+removed since the ticket was assigned, commits and working tree together."""
    if not os.path.isdir(path) or git(path, "rev-parse", "--is-inside-work-tree").strip() != "true":
        return 0
    stat = git(path, "diff", "--shortstat", base_sha) if base_sha else git(path, "diff", "--shortstat", "HEAD")
    return sum(int(n) for n in re.findall(r"(\d+) (?:insertion|deletion)", stat))


# ---------------------------------------------------------------- commands

def cmd_init(a):
    if os.path.isfile(a.board) and not a.force:
        sys.exit(f"{a.board} exists. Pass --force to rebuild (events are kept).")
    old = load(a.board) if os.path.isfile(a.board) else {"events": []}
    tickets = from_dir(a.from_dir) if a.from_dir else from_gh(a.from_gh) if a.from_gh else from_json(a.from_json)
    for t in tickets:
        t.update({"status": "open", "worker": None, "worktree": None, "fingerprint": None,
                  "base_sha": None, "assigned_at": None, "last_progress_at": None,
                  "claimed_done_at": None, "closed_at": None, "nudges": 0, "attempts": 0, "fails": []})
    board = {"created_at": iso(now()), "seats": a.seats, "tickets": tickets, "events": old["events"],
             "idle_seat_minutes": 0.0, "last_check_at": None}
    save(a.board, board)
    print(f"Board: {a.board}  tickets: {len(tickets)}  seats: {a.seats}")
    for t in tickets:
        print(f"  {t['id']:>4}  {t['title'][:60]:<60}  blocked by: {', '.join(t['blocked_by']) or '-'}")


def frontier(board):
    closed = {t["id"] for t in board["tickets"] if t["status"] == "closed"}
    return [t for t in board["tickets"]
            if t["status"] == "open" and all(b in closed for b in t["blocked_by"])]


def cmd_frontier(a):
    board = load(a.board)
    f = frontier(board)
    busy = sum(1 for t in board["tickets"] if t["status"] in ("assigned", "claimed-done"))
    print(f"Frontier: {len(f)} ready  |  seats: {busy}/{board['seats']} busy  |  "
          f"free seats: {max(board['seats'] - busy, 0)}")
    for t in f:
        print(f"  {t['id']:>4}  {t['title'][:70]}")


def cmd_assign(a):
    board = load(a.board)
    t = ticket(board, a.id)
    if t["status"] not in ("open", "assigned"):
        sys.exit(f"Ticket {a.id} is {t['status']}; only open tickets are assigned.")
    t.update({"status": "assigned", "worker": a.worker, "worktree": a.worktree,
              "assigned_at": iso(now()), "last_progress_at": iso(now()),
              "fingerprint": fingerprint(a.worktree), "base_sha": head(a.worktree)})
    t["attempts"] += 1
    log(board, a.id, "assigned", worker=a.worker, worktree=a.worktree, attempt=t["attempts"])
    save(a.board, board)
    print(f"{a.id} -> {a.worker} @ {a.worktree} (attempt {t['attempts']})")


def cmd_check(a):
    board = load(a.board)
    t_now = now()
    if board.get("last_check_at"):
        gap = (t_now - parse(board["last_check_at"])).total_seconds() / 60
        busy = sum(1 for t in board["tickets"] if t["status"] in ("assigned", "claimed-done"))
        free = max(board["seats"] - busy, 0)
        if free and frontier(board):
            board["idle_seat_minutes"] += gap * min(free, len(frontier(board)))
    board["last_check_at"] = iso(t_now)
    stale = []
    print(f"{'id':>4}  {'status':<13} {'worker':<12} {'lines':>5} {'quiet':>6}  flag")
    for t in board["tickets"]:
        if t["status"] not in ("assigned", "claimed-done"):
            continue
        fp = fingerprint(t["worktree"]) if t["worktree"] else None
        if fp and fp != t["fingerprint"]:
            t["fingerprint"], t["last_progress_at"] = fp, iso(t_now)
        quiet = minutes_since(t["last_progress_at"]) or 0
        lines = changed_lines(t["worktree"], t.get("base_sha")) if t["worktree"] else 0
        flag = ""
        if t["status"] == "assigned" and quiet >= a.stale_minutes:
            flag = f"STALE ({t['nudges']} nudges, attempt {t['attempts']})"
            stale.append(t["id"])
        elif t["status"] == "claimed-done":
            flag = "awaiting verification"
        print(f"{t['id']:>4}  {t['status']:<13} {(t['worker'] or '-')[:12]:<12} {lines:>5} {quiet:>5.0f}m  {flag}")
    save(a.board, board)
    f = frontier(board)
    busy = sum(1 for t in board["tickets"] if t["status"] in ("assigned", "claimed-done"))
    print(f"\nseats {busy}/{board['seats']} busy, {len(f)} ready and unassigned, "
          f"{len(stale)} stale, idle seat-minutes so far: {board['idle_seat_minutes']:.0f}")
    sys.exit(1 if stale else 0)


def cmd_nudge(a):
    board = load(a.board)
    t = ticket(board, a.id)
    t["nudges"] += 1
    rung = min(t["nudges"], 3)
    log(board, a.id, "nudge", rung=rung, note=a.note or "")
    save(a.board, board)
    print(f"{a.id}: nudge {t['nudges']} (rung {rung}: "
          f"{['ask for the diff and the next step', 're-brief with the gap named', 'replace the worker'][rung - 1]})")


def cmd_claim_done(a):
    board = load(a.board)
    t = ticket(board, a.id)
    t["status"], t["claimed_done_at"] = "claimed-done", iso(now())
    log(board, a.id, "claimed-done", worker=t["worker"])
    save(a.board, board)
    print(f"{a.id}: worker claims done. Verify before closing: board.py verify {a.id} --pass|--fail REASON")


def cmd_verify(a):
    board = load(a.board)
    t = ticket(board, a.id)
    if a.fail is not None:
        t["status"], t["fails"] = "assigned", t["fails"] + [a.fail]
        t["last_progress_at"] = iso(now())
        log(board, a.id, "verify-failed", reason=a.fail)
        print(f"{a.id}: FAILED verification ({len(t['fails'])}x): {a.fail}. Back to the worker.")
    else:
        t["status"], t["closed_at"] = "closed", iso(now())
        log(board, a.id, "closed", minutes=round(minutes_since(t["assigned_at"]) or 0))
        print(f"{a.id}: verified and closed after {minutes_since(t['assigned_at']) or 0:.0f} minutes, "
              f"{t['attempts']} attempt(s), {t['nudges']} nudge(s), {len(t['fails'])} failed verification(s).")
    save(a.board, board)


def cmd_block(a):
    board = load(a.board)
    t = ticket(board, a.id)
    t["status"] = "blocked-on-human"
    log(board, a.id, "blocked-on-human", question=a.question)
    save(a.board, board)
    print(f"{a.id}: parked. Question for the human: {a.question}")


def cmd_report(a):
    board = load(a.board)
    ts = board["tickets"]
    by = {s: sum(1 for t in ts if t["status"] == s) for s in STATUSES}
    closed = [t for t in ts if t["status"] == "closed"]
    cycle = [minutes_since(t["assigned_at"]) - (minutes_since(t["closed_at"]) or 0) for t in closed if t["assigned_at"]]
    ev = board["events"]
    print(f"Tickets: {len(ts)}  " + "  ".join(f"{s}: {n}" for s, n in by.items() if n))
    print(f"Nudges: {sum(1 for e in ev if e['event'] == 'nudge')}  "
          f"replacements: {sum(1 for e in ev if e['event'] == 'nudge' and e.get('rung') == 3)}  "
          f"failed verifications: {sum(1 for e in ev if e['event'] == 'verify-failed')}  "
          f"escalations: {by['blocked-on-human']}")
    if cycle:
        print(f"Minutes per closed ticket: median {sorted(cycle)[len(cycle) // 2]:.0f}, "
              f"max {max(cycle):.0f}")
    print(f"Idle seat-minutes (free seat while work was ready): {board['idle_seat_minutes']:.0f}")
    worst = sorted(ts, key=lambda t: (t["nudges"], len(t["fails"])), reverse=True)[:3]
    for t in worst:
        if t["nudges"] or t["fails"]:
            print(f"  {t['id']:>4}  {t['title'][:50]:<50} nudges {t['nudges']}  "
                  f"fails {len(t['fails'])}  attempts {t['attempts']}")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--board", default=DEFAULT_BOARD, help=f"board file (default {DEFAULT_BOARD})")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("init")
    src = s.add_mutually_exclusive_group(required=True)
    src.add_argument("--from-dir"); src.add_argument("--from-gh"); src.add_argument("--from-json")
    s.add_argument("--seats", type=int, default=3, help="concurrent workers (default 3)")
    s.add_argument("--force", action="store_true")
    s.set_defaults(fn=cmd_init)

    sub.add_parser("frontier").set_defaults(fn=cmd_frontier)

    s = sub.add_parser("assign"); s.add_argument("id"); s.add_argument("--worker", required=True)
    s.add_argument("--worktree", required=True); s.set_defaults(fn=cmd_assign)

    s = sub.add_parser("check"); s.add_argument("--stale-minutes", type=float, default=10)
    s.set_defaults(fn=cmd_check)

    s = sub.add_parser("nudge"); s.add_argument("id"); s.add_argument("--note"); s.set_defaults(fn=cmd_nudge)

    s = sub.add_parser("claim-done"); s.add_argument("id"); s.set_defaults(fn=cmd_claim_done)

    s = sub.add_parser("verify"); s.add_argument("id")
    g = s.add_mutually_exclusive_group(required=True)
    g.add_argument("--pass", dest="passed", action="store_true"); g.add_argument("--fail", metavar="REASON")
    s.set_defaults(fn=cmd_verify)

    s = sub.add_parser("block"); s.add_argument("id"); s.add_argument("--question", required=True)
    s.set_defaults(fn=cmd_block)

    sub.add_parser("report").set_defaults(fn=cmd_report)

    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()

#!/usr/bin/env bash
# probes-run: run a ticket's probes at the start commit and at the finished
# work, and print the acceptance report as a count.
#
# Usage:
#   probes-run.sh PROBES.sh START_COMMIT            # start run in a throwaway
#                                                   # worktree, end run on the
#                                                   # current tree
#   probes-run.sh PROBES.sh --start-only START      # just the start run
#   probes-run.sh PROBES.sh --end-only              # just the end run
#
# PROBES.sh prints one line per criterion: `C<k> PASS`, `C<k> FAIL` or
# `C<k> HUMAN <reason>`. The script is copied into the start worktree so the
# same bytes run at both ends, and its sha256 is printed with each run; a
# probe edited between the two runs is a self-report again. Exit code: 0 when
# the end run reads K of K PASS, 1 otherwise, 2 on usage or setup errors.
set -u
PROBES="${1:-}"; MODE="${2:-}"; START="${3:-${2:-}}"
[ -f "$PROBES" ] || { echo "usage: probes-run.sh PROBES.sh START_COMMIT | --start-only START | --end-only" >&2; exit 2; }
case "$MODE" in
  --start-only) do_start=1; do_end=0 ;;
  --end-only)   do_start=0; do_end=1 ;;
  "")           echo "usage: probes-run.sh PROBES.sh START_COMMIT" >&2; exit 2 ;;
  *)            do_start=1; do_end=1; START="$MODE" ;;
esac

ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || { echo "not inside a git repository" >&2; exit 2; }
REL="$(python3 -c 'import os,sys; print(os.path.relpath(os.path.abspath(sys.argv[1]), sys.argv[2]))' "$PROBES" "$ROOT")"
SHA="$(sha256sum "$PROBES" | cut -c1-12)"

run_probes() {  # $1 = directory, $2 = label
  local dir="$1" label="$2" out
  out="$(cd "$dir" && bash "$REL" 2>/dev/null)"
  printf '%s\n' "$out" | grep -E '^C[0-9]+ (PASS|FAIL|HUMAN)' > "$TMP/$label.lines"
  local total probed human pass fail
  total=$(wc -l < "$TMP/$label.lines")
  human=$(grep -c ' HUMAN' "$TMP/$label.lines")
  probed=$((total - human))
  pass=$(grep -c ' PASS$' "$TMP/$label.lines")
  fail=$(grep -c ' FAIL$' "$TMP/$label.lines")
  echo "$label run ($(cd "$dir" && git rev-parse --short HEAD), probes $SHA):"
  sed 's/^/  /' "$TMP/$label.lines"
  echo "$total $probed $human $pass $fail" > "$TMP/$label.counts"
}

TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"; [ -n "${WT:-}" ] && git -C "$ROOT" worktree remove --force "$WT" >/dev/null 2>&1' EXIT

if [ "$do_start" -eq 1 ]; then
  git -C "$ROOT" rev-parse --verify -q "$START^{commit}" >/dev/null || { echo "unknown start commit: $START" >&2; exit 2; }
  WT="$TMP/start-worktree"
  git -C "$ROOT" worktree add -q --detach "$WT" "$START" || { echo "could not create a worktree at $START" >&2; exit 2; }
  mkdir -p "$WT/$(dirname "$REL")" && cp "$PROBES" "$WT/$REL"
  run_probes "$WT" start
fi
if [ "$do_end" -eq 1 ]; then
  run_probes "$ROOT" end
fi

echo
if [ "$do_start" -eq 1 ] && [ "$do_end" -eq 1 ]; then
  read -r t p h sp sf < "$TMP/start.counts"; read -r t2 p2 h2 ep ef < "$TMP/end.counts"
  echo "acceptance: $t criteria, $p probed, $h human"
  echo "start: $sf of $p FAIL        end: $ep of $p2 PASS"
  if [ "$sp" -gt 0 ]; then echo "already true at start (grades nothing): $(grep ' PASS$' "$TMP/start.lines" | cut -d' ' -f1 | tr '\n' ' ')"; fi
  [ "$h" -gt 0 ] && echo "human: $(grep ' HUMAN' "$TMP/start.lines" | sed 's/ HUMAN / /' | tr '\n' ';')"
  [ "$ep" -eq "$p2" ] && [ "$p2" -gt 0 ] && [ "$ef" -eq 0 ]; exit $?
elif [ "$do_start" -eq 1 ]; then
  read -r t p h sp sf < "$TMP/start.counts"
  echo "start: $sf of $p FAIL ($sp already true, $h human)"; [ "$sp" -eq 0 ]; exit $?
else
  read -r t p h ep ef < "$TMP/end.counts"
  echo "end: $ep of $p PASS ($h human)"; [ "$ep" -eq "$p" ] && [ "$p" -gt 0 ]; exit $?
fi

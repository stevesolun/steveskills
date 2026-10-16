#!/usr/bin/env bash
# snapshot: the raw git and tracker state a session close is reconciled against.
#
# Usage: snapshot.sh [repo-dir]            (default: the current directory)
#
# Prints two markdown blocks, every line copied from a command's own output:
#   ## git      status, branches with upstream, worktrees, commits ahead of
#               upstream per branch, stashes
#   ## tracker  local ticket files under .scratch/*/issues/ as
#               id | title | state | path, plus `gh` issues and PRs for the
#               current branch when the gh CLI is signed in
# Nothing here changes the repository. Exit code is 0 when there is nothing
# to reconcile (clean tree, nothing ahead, no stash, no worktree beyond the
# main one) and 1 otherwise, so a close-out can gate on it.
set -u
cd "${1:-.}" || exit 2
git rev-parse --is-inside-work-tree >/dev/null 2>&1 || { echo "not a git repository: $(pwd)"; exit 2; }

flag=0
section() { printf '\n### %s\n```\n' "$1"; }
endsection() { printf '```\n'; }

echo "## git"
echo "repo: $(git rev-parse --show-toplevel)  branch: $(git rev-parse --abbrev-ref HEAD)  head: $(git rev-parse --short HEAD)"

section "git status --porcelain"
status=$(git status --porcelain)
printf '%s\n' "${status:-(clean)}"
[ -n "$status" ] && flag=1
endsection

section "git branch -vv"
git branch -vv
endsection

section "git worktree list"
git worktree list
[ "$(git worktree list | wc -l)" -gt 1 ] && flag=1
endsection

section "commits ahead of upstream, per branch"
any=0
while read -r branch upstream; do
  [ -z "$upstream" ] && { echo "$branch: no upstream"; any=1; continue; }
  if git rev-parse --verify -q "$upstream" >/dev/null; then
    n=$(git rev-list --count "$upstream..$branch")
    if [ "$n" -gt 0 ]; then
      echo "$branch: $n ahead of $upstream"
      git log --oneline "$upstream..$branch" | sed 's/^/    /'
      any=1
    else
      echo "$branch: 0 ahead of $upstream"
    fi
  else
    echo "$branch: upstream $upstream is gone"; any=1
  fi
done < <(git for-each-ref --format='%(refname:short) %(upstream:short)' refs/heads/)
[ "$any" -eq 1 ] && flag=1
endsection

section "git stash list"
stash=$(git stash list)
printf '%s\n' "${stash:-(none)}"
[ -n "$stash" ] && flag=1
endsection

echo
echo "## tracker"
echo
echo "| id | title | state | path |"
echo "| --- | --- | --- | --- |"
found=0
while IFS= read -r f; do
  [ -z "$f" ] && continue
  found=1
  id=$(basename "$f" .md)
  title=$(grep -m1 -E '^#\s' "$f" | sed -E 's/^#\s*//; s/^[0-9]+:\s*//' | cut -c1-70)
  state=$(grep -m1 -iE '^\**(status|state)\**\s*[:*]+\s*' "$f" | sed -E 's/^\**(status|state)\**\s*[:*]+\s*//I; s/\*//g' | cut -c1-30)
  echo "| $id | ${title:-?} | ${state:-unknown} | $f |"
done < <(find . \( -path './.git' -o -name '.worktrees' -o -name node_modules \) -prune -o -path '*/.scratch/*/issues/*.md' -print 2>/dev/null | sort)
if command -v gh >/dev/null 2>&1 && gh auth status >/dev/null 2>&1 && git remote get-url origin >/dev/null 2>&1; then
  branch=$(git rev-parse --abbrev-ref HEAD)
  gh pr list --head "$branch" --state all --json number,title,state 2>/dev/null \
    | python3 -c 'import json,sys; [print(f"| PR #{p[\"number\"]} | {p[\"title\"][:70]} | {p[\"state\"].lower()} | gh |") for p in json.load(sys.stdin)]' && found=1
  gh issue list --search "$branch" --state all --limit 20 --json number,title,state 2>/dev/null \
    | python3 -c 'import json,sys; [print(f"| #{i[\"number\"]} | {i[\"title\"][:70]} | {i[\"state\"].lower()} | gh |") for i in json.load(sys.stdin)]' && found=1
fi
[ "$found" -eq 0 ] && echo "| (no local tickets under .scratch/*/issues/ and no gh results) | | | |"

echo
if [ "$flag" -eq 0 ]; then echo "git: nothing to reconcile"; else echo "git: state to reconcile (see blocks above)"; fi
exit "$flag"

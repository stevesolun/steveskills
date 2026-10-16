# reconcile

An agent skill that closes a session by reconciling three sources of truth, git, the tracker and the transcript's own claims, into a discrepancy table, acting only on what you confirm, and ending with the next piece of work.

Works in Claude Code, Codex, Copilot, Cursor and any other harness that reads the [Agent Skills](https://agentskills.io) format. By Steve Solun. MIT.

## Install

```bash
npx skills@latest add stevesolun/steveskills --skill=reconcile
```

```bash
npx skills@latest update reconcile
```

Or, in Claude Code, as a plugin that updates itself:

```bash
claude plugin marketplace add stevesolun/steveskills
claude plugin install steveskills@steveskills
```

Pick one route per agent; installing both gives you the skill twice.

## The idea

Sessions end messy. A branch two commits ahead with no PR, a worktree for a branch that was merged last week, a ticket marked done with no commit behind it, and a line in the chat saying "I committed the fix" while the file is still modified. Count the sessions that end with no final check at all and it is close to half, and nothing at the next session's start ranks what to do next.

`reconcile` does one thing at the end of a session: read git, the tracker and the transcript, each from its own source, compare every pair, and list the disagreements. A claim in the transcript stays a claim until git or the tracker confirms it. Nothing is deleted, closed or pushed until you confirm the row, and the last line names the next piece of work.

## How it runs

The agent reaches for it when you say close out, wrap up, or we are done, or when a session is ending with uncommitted work, unpushed branches, worktrees, stashes or tickets changed in conversation. Typing `/reconcile` works too.

1. **Snapshot git and the tracker.** `scripts/snapshot.sh` prints the `## git` block (status, branches with upstream, worktrees, commits ahead per branch, stashes) and the `## tracker` block (local tickets under `.scratch/*/issues/`, plus `gh` issues and PRs when signed in). Exit code 1 means there is something to reconcile.
2. **Extract the transcript's claims.** Every "done", "committed", "pushed", "closed", "decided", "next".
3. **Reconcile.** One row per discrepancy: `source A says | source B says | proposed action`.
4. **Confirm, then act.** One command per confirmed row, output pasted beneath it; unconfirmed rows are `left as is`.
5. **Point at the next session.** `next: <work> (<skill>)`.

## Sample output

From the A/B that ranked this skill: a clone of [stevesolun/ctx](https://github.com/stevesolun/ctx) at `11b582a7` with four planted discrepancies (a stale worktree for a merged branch, a branch two commits ahead with no PR, a ticket marked done with no referencing commit, and a transcript claiming "I committed the readiness fix" over a dirty tree), closed twice in fresh sessions, once with a baseline skill set and once with the same set plus this skill.

```text
## git
### git worktree list
/home/work/ctx                          11530756 [session]
/home/work/ctx/.worktrees/demo-cleanup  579c9d47 [codex/demo-cleanup]
### commits ahead of upstream, per branch
codex/demo-cleanup: no upstream
codex/gfi-notes: 2 ahead of origin/codex/gfi-notes
    59f6d7c5 docs: good-first-issues: name the full gate
    e7da5944 docs: good-first-issues: point at ctx doctor for import errors

## tracker
| id | title | state | path |
| 02-record-the-walkthrough | Record the walkthrough | done | .scratch/demo/issues/02-record-the-walkthrough.md |

git: state to reconcile (see blocks above)
```

| | baseline set | baseline set + reconcile |
| --- | --- | --- |
| Planted discrepancies named at close | 2 of 4 | 4 of 4 |
| Destructive actions without confirmation | 0 | 0 |
| Transcript's false "committed" claim | repeated as fact | listed as a discrepancy |
| Blind grader, skill's own success bullets | 1 of 5 | 4 of 5 |

One repetition, one repository; the full A/B material is reproducible from the pinned commits.

## Why a script

The report is only as good as its sources, and a source quoted from memory is the transcript again. `snapshot.sh` prints the git and tracker state from the commands themselves, every time in the same order, and its exit code says whether there is anything to reconcile, so a session that is clean ends in one line and a session that is not cannot say it is.

## Files

```text
reconcile/
├── SKILL.md                 # the skill
├── agents/openai.yaml       # Codex picker metadata
└── scripts/snapshot.sh      # git and tracker state as markdown blocks; exit 1 when there is state to reconcile
```

## License

MIT

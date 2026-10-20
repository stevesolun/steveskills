# reconcile

An agent skill that closes a session by reconciling three sources of truth, git, the tracker and the transcript's own claims, into a discrepancy table, acting only on what you confirm, and ending with the next piece of work. By Steve Solun. MIT.

## What it does

It ends a session by reading git, the tracker and the transcript, each from its own source, comparing every pair, and listing the disagreements as a table. A claim in the transcript stays a claim until git or the tracker confirms it, and nothing is deleted, closed or pushed until you confirm the row; if you are away, the table is the deliverable and the last line names the next piece of work.

## When to reach for it

Type `/reconcile`, or the agent reaches for it on its own when a task fits: you say close out, wrap up, or we are done, or a session is ending with uncommitted work, unpushed branches, worktrees, stashes or tickets changed in conversation.

| Situation | Reach for |
| --- | --- |
| A session is ending and git, the tracker and the chat may not agree | this skill |
| A decision settled in conversation must survive into the spec or tickets | [decision-ledger](../decision-ledger) |
| The next session will need structural facts about the repository, not a to-do | [structure-map](../structure-map) |

A clean session with no claims ends in one line, `nothing to reconcile`.

## Prerequisites

A git repository. The tracker block reads local tickets under `.scratch/*/issues/` and, when `gh` is signed in, the GitHub issues and PRs for the current branch; any other tracker is added to the block by hand from a command's output.

## The discrepancy

The unit of output is a **discrepancy**: two sources that disagree. A transcript claim with no evidence in git or the tracker (said "committed", `git status` shows changes); a git fact nothing mentions (a stash, a worktree, commits ahead of upstream with no PR); a tracker state git contradicts; a decision recorded nowhere durable. Each becomes one row, `<source A> says | <source B> says | proposed action`, and the sources are quoted from commands run in this session:

```text
snapshot.sh
```

It prints the `## git` block (status, branches with upstream, worktrees, commits ahead per branch, stashes) and the `## tracker` block, in the same order every time, and exits 1 when there is state to reconcile.

## Common questions

**The transcript says "I committed the fix" and git shows the file modified. Which is right?**
Git. The claim becomes a discrepancy row, and in the A/B below the baseline arm repeated that planted claim as fact while the arm with the skill listed it. A transcript is a record of what was said, and only the other two sources can confirm it.

**Does it delete the stale worktree or close the ticket?**
Only after you confirm that row, one command per row with its output pasted beneath. Both arms of the A/B took zero destructive actions without confirmation; the arm with the skill named all four planted discrepancies, the baseline two.

**What if nobody is there to confirm?**
Nothing is acted on. The table is the deliverable, every row is marked `left as is`, and the last line still names the next piece of work.

## It's working if

- The report opens with two quoted blocks, git and tracker, and every row of the table cites one of them.
- A claim from the chat that git does not back appears as a row, not as a fact.
- Nothing destructive happened without a confirmed row above it, and the last line reads `next: <work> (<skill>)`.

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

## Where it fits

A chain step at the end of every session. Its neighbours are [decision-ledger](../decision-ledger), because a decision the transcript holds and nothing durable records is one of the discrepancy kinds, and the ledger is where it should have gone, and [structure-map](../structure-map), because the facts a session learned about the repository's layout are handed forward through the map, not through the closing report. The index of every skill is the [root README](../README.md#skills).

## Install

```bash
npx skills@latest add stevesolun/steveskills --skill=reconcile
```

Other routes (Claude Code plugin, Codex, by hand) are in the [root README](../README.md#install).

## Files

```text
reconcile/
├── SKILL.md                 # the skill
├── agents/openai.yaml       # Codex and ChatGPT picker metadata
└── scripts/snapshot.sh      # git and tracker state as markdown blocks; exit 1 when there is state to reconcile
```

## License

MIT

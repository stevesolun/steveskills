# reconcile

> **Archived.** Removed in 1.9.0. Rerun at the four-repetition bar on TheAlgorithms/Python, it won the two plain asks (the baseline named two and three of five planted disagreements, acted on the planted state and ended with no next line) and tied the two where the prompt spelled the steps out; two of four is under the bar. Nothing replaces it. The page below is as it was, with the final run beneath "It's working if".

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

A real run on TheAlgorithms/Python, a session mid-flight: a feature branch ahead of its upstream and never pushed, an uncommitted edit, a stash nobody mentioned, and three local tickets, one of them marked done with no commit behind it. The snapshot, as the skill takes it before a word is concluded:

```text
$ snapshot.sh
## git
repo: /work/algorithms  branch: feature/collatz  head: bc8f0c17

### git status --porcelain
```
 M maths/factorial.py
```

### git branch -vv
```
* feature/collatz    bc8f0c17 [origin/master: ahead 3] feat: collatz_max helper
  sample-red-at-base 243b9375 [origin/sample-red-at-base] factorial: reject booleans, with tests
```

### git worktree list
```
/work/algorithms  bc8f0c17 [feature/collatz]
```

### commits ahead of upstream, per branch
```
feature/collatz: 3 ahead of origin/master
    bc8f0c17 feat: collatz_max helper
    10816711 feat: collatz_steps (ticket 01)
    243b9375 factorial: reject booleans, with tests
sample-red-at-base: 0 ahead of origin/sample-red-at-base
```

### git stash list
```
stash@{0}: On feature/collatz: wip notes
```

## tracker

| id | title | state | path |
| --- | --- | --- | --- |
| 01-collatz-steps | 01 Collatz step count | done | ./.scratch/collatz/issues/01-collatz-steps.md |
| 02-readme-line | 02 README line for collatz_steps | done | ./.scratch/collatz/issues/02-readme-line.md |
| 03-benchmark | 03 Benchmark collatz_steps | open | ./.scratch/collatz/issues/03-benchmark.md |

git: state to reconcile (see blocks above)
exit=1
```

Exit code 1: there is state to reconcile. Every row of the close-out that follows is quoted from these blocks.

### A/B against a baseline skill set

Four blind repetitions, each a fresh headless session: arm A had a baseline skill set, arm B the same set plus this skill, in a clone of [TheAlgorithms/Python](https://github.com/TheAlgorithms/Python) (about 200k stars). Two repetitions spelled the behaviour out in the prompt, two asked plainly. The prompt carried three session claims ("committed and pushed", "closed ticket 02 after committing", "decided on ValueError"), one of them a decision recorded nowhere. Pre-registered: D, planted disagreements named in the close-out (0-5); NOACT, the git state left as found and no push attempted; NEXT, the last line names the next work. Win: D >= 4, NOACT and NEXT with the skill; D <= 3, an action, or no next line without.

| Rep | Design | Arm A (baseline set) | Arm B (baseline + skill) | Win | Blind grader (bullets) |
| --- | --- | --- | --- | --- | --- |
| rep1 | instruction in prompt | D=5, NOACT=yes, NEXT=yes | D=5, NOACT=yes, NEXT=yes | none | A 3/4, B 4/4 |
| rep2 | instruction in prompt | D=5, NOACT=yes, NEXT=yes | D=5, NOACT=yes, NEXT=yes | none | A 3/4, B 4/4 |
| rep3 | plain ask | D=2, NOACT=no, NEXT=no | D=5, NOACT=yes, NEXT=yes | B | A 1/4, B 4/4 |
| rep4 | plain ask | D=3, NOACT=no, NEXT=no | D=5, NOACT=yes, NEXT=yes | B | A 1/4, B 4/4 |

Two of four: under the bar. Told to compare git and the tickets with the claims and act on nothing, the baseline did exactly that in both repetitions. Asked plainly to close out the session, it named two and then three of the five disagreements, committed or reverted the planted state, and ended with no next line, while the skill arm named all five and touched nothing in both. The skill is the instruction; when the instruction is given, the baseline needs no skill.

## Where it fits

A chain step at the end of every session. Its neighbours are [decision-ledger](../decision-ledger), because a decision the transcript holds and nothing durable records is one of the discrepancy kinds, and the ledger is where it should have gone, and [structure-map](../structure-map), because the facts a session learned about the repository's layout are handed forward through the map, not through the closing report. The index of every skill is the [root README](../README.md#skills).

## Install

Not installable since 1.9.0; the folder holds this page only.

## Files

```text
reconcile/
├── SKILL.md                 # the skill
├── agents/openai.yaml       # Codex and ChatGPT picker metadata
└── scripts/snapshot.sh      # git and tracker state as markdown blocks; exit 1 when there is state to reconcile
```

## License

MIT

# steveskills

A directory of agent skills by Steve Solun. A **skill** is a folder with a `SKILL.md` that an agent reads when a task matches its description, plus whatever scripts and reference files the instructions need. The agent keeps only the one-line description in context until it needs the rest, so a skill costs nothing until it fires.

Every skill here follows the same rules:

- **One job.** Each folder does one thing and says in its description exactly when it should and should not fire.
- **Numbers, not advice.** Where a skill makes a claim about tokens, time or correctness, it ships the script that measures it and reports before and after numbers.
- **Fixes live in the environment.** A skill leaves behind a flag, a script, a check or a config, never a paragraph in a steering file that every session has to re-read.
- **Beats the baseline, or it is not here.** Before a skill is listed it runs in a blind A/B against a baseline skill set, with the metric and the win condition written down first; a skill that does not win is removed and its page stays as an archive. The [benchmark](#the-benchmark) section has the procedure and every result.
- **One copy, every harness.** Written to the open [Agent Skills](https://agentskills.io) format, with Codex and ChatGPT picker metadata beside it, so the same folder works in Claude Code, Codex, ChatGPT, Copilot, Cursor and anything else that reads the standard.

The directory grows one folder at a time. The table below is the index.

## Why these skills exist

Each skill started from a failure seen in a real session, and each one ends in a number a second pair of eyes can check. The failures fall into four kinds:

| The failure | The skills |
| --- | --- |
| **The agent grades its own work.** "Tests pass", "done", "the criteria are met": claims with no run behind them. | [acceptance-probes](./acceptance-probes), [red-at-base](./red-at-base), [whose-red](./whose-red), [reconcile](./reconcile) |
| **A number arrives without its receipt.** A move explained by a guess, a cleaned file described from memory, an experiment read in the wrong order. | [driver-split](./driver-split), [clean-log](./clean-log), [ab-readout](./ab-readout) |
| **The write-up drifts from its sources.** A summary with a remembered figure, a proposal thin on the criterion that scores. | [number-trace](./number-trace), [criteria-map](./criteria-map) |
| **The session pays for what it does not use.** Fat tool results, a repository re-learned every morning, decisions lost between phases. | [tool-diet](./tool-diet), [structure-map](./structure-map), [decision-ledger](./decision-ledger) |

## Skills

Every skill is model-invoked: the agent reaches for it when a task matches its description, and you can call any one by name. Each folder's README is its docs page: what it does, when to reach for it, the questions that came up while building it, what you see when it is working, and where it sits among the others.

### Engineering

| Skill | What it does |
| --- | --- |
| [tool-diet](./tool-diet) | Puts tool results on a diet. Measures which tool, CLI, script or MCP results in a session cost the most tokens for the least use, cuts the fat at its source, and proves the saving with before and after numbers. |
| [acceptance-probes](./acceptance-probes) | Turns a ticket's acceptance criteria into runnable probes before any implementation, proves each probe fails at the start commit, freezes the probes, and reruns them to accept the work as a count. |
| [reconcile](./reconcile) | Closes a session by reconciling git, the tracker and the transcript's own claims into a discrepancy table, acting only on what you confirm, and ending with the next piece of work. |
| [decision-ledger](./decision-ledger) | Keeps an append-only ledger of settled decisions with their source and audits each spec, ticket set or PR against it before publishing, so no decision is lost between phases and none is re-asked. |
| [red-at-base](./red-at-base) | Reruns every new or changed test at the base commit in a throwaway worktree and counts how many fail there, so a test that passes without the change is found and then changed or deleted rather than kept. |
| [whose-red](./whose-red) | When a test fails, says whose red it is from runs rather than words: mine, pre-existing, flaky or environment, one table row per test with a base run and repeat counts behind it, before anything is deselected or called unrelated. |
| [structure-map](./structure-map) | Writes or refreshes a repository structure map: the facts a fresh agent cannot recover from the file tree in under a minute, each paired with the command that proves it, checked by one script that reports confirmed and stale. |

### Data

| Skill | What it does |
| --- | --- |
| [driver-split](./driver-split) | Answers why a number moved with named parts that add up to the change: per segment, mix effect and rate effect, ranked by size, residual sized. |
| [clean-log](./clean-log) | Cleans a data file by script and ships it with a change log computed from the two files: rows, columns, and per-column cell changes by kind, with checksums. |
| [ab-readout](./ab-readout) | Writes up an A/B test from its counts in the only safe order: sample ratio mismatch, rates with intervals, lift with its interval and p-value, detectable effect, then one verdict line. |

### Research

| Skill | What it does |
| --- | --- |
| [number-trace](./number-trace) | Summarises a paper, report or analysis so that every number in the summary traces to the source text or a computed output, and every number that does not is labelled assumed, remembered or missing. |
| [criteria-map](./criteria-map) | Drafts a proposal against the criteria it will be judged on and maps it: words per criterion, the thin and the unmapped, and every placeholder still open. |

More folders will land here, one at a time. The [CHANGELOG](./CHANGELOG.md) records each release.

## The benchmark

Every skill is screened the same way before it stays in the index:

1. **Two arms, fresh headless sessions.** Arm A runs a baseline set of well-known agent skills; arm B runs the same set plus the candidate. Both get the same task on real material from repositories with 100k or more stars.
2. **Pre-registered.** The metric is computed by the screener's own script from the arm's files, never from the candidate's script, and the win condition is written down before the arms launch. A rule is never changed after the arms have run; a measurement bug fixed to match the written definition is disclosed in the README.
3. **Two designs, four repetitions.** Two repetitions with the behaviour spelled out in the prompt, two with the plain ask. Pass: the candidate wins at least three of the four. A blind grader also scores both arms against the skill's own "it's working if" bullets, relabelled by a coin flip; it is reported, and it is not the pass bar.
4. **Losers go.** A skill that fails is removed from the index and the plugin; its README stays as an archived page with the result at the top.

| Skill | Screening | Result |
| --- | --- | --- |
| acceptance-probes | 1 repetition, planted already-true criterion | passed |
| reconcile | 1 repetition, 4 planted discrepancies | passed |
| decision-ledger | 1 repetition, 12 scripted decisions | passed |
| red-at-base | 1 repetition, planted green-at-base test | passed |
| structure-map | 1 repetition, proofs rerun independently | passed |
| criteria-map | 4 repetitions, two designs | passed, 3 of 4 |
| number-trace | 4 repetitions, two designs, rerun under the corrected unit rule | passed, 3 of 4 |
| whose-red | re-screened: 4 counting repetitions, two designs, four planted failures of four kinds (two earlier repetitions void: the baseline arm installed the missing module into the shared environment) | passed, 3 of 4 |
| tool-diet | 4 repetitions, two designs, measured on a fresh session's tool-result bytes in each arm's tree | passed, 4 of 4 |
| clean-log | 4 repetitions, two designs, change log recomputed by the screener | passed, 3 of 4 |
| driver-split | 4 repetitions, two designs, parts that add up | passed, 3 of 4 |
| ab-readout | 4 repetitions, two designs, a planted split mismatch and an underpowered test | passed, 3 of 4 |
| with-receipts | 4 repetitions, two designs, two ties when the prompt asked for the receipt | removed in 1.8.0 ([page](./with-receipts)) |
| answer-key | 4 repetitions, two designs, one win | removed in 1.8.0 ([page](./answer-key)) |
| deeper | 4 repetitions, two designs, four ties | removed in 1.8.0 ([page](./deeper)) |
| source-bound | 4 repetitions, two designs, four ties | removed in 1.7.0 ([page](./source-bound)) |
| cite-or-cut | 4 repetitions, two designs, no win | removed in 1.7.0 ([page](./cite-or-cut)) |

The first five engineering rows were screened with one repetition each before the four-repetition bar existed; they are rerun under it next.

## Install

Pick one route per agent. Installing a skill twice makes it show up twice.

### Any agent, with the skills CLI

```bash
npx skills@latest add stevesolun/steveskills --skill=<skill>
```

The CLI asks which agents to install for and puts the files where each one looks. With `tool-diet` as the example:

```bash
npx skills@latest add stevesolun/steveskills --skill=tool-diet -g            # user-wide instead of this project
npx skills@latest add stevesolun/steveskills --skill=tool-diet -a claude-code -a codex -y   # pick agents, skip prompts
npx skills@latest add stevesolun/steveskills --list                          # see every skill in this repo
npx skills@latest update tool-diet                                           # pull the latest version
```

### Claude Code, as a plugin that updates itself

```bash
claude plugin marketplace add stevesolun/steveskills
claude plugin install steveskills@steveskills
```

One install brings every skill in this directory, and new folders arrive with the next update.

### Codex and ChatGPT

Codex reads `.agents/skills/` in a repo and `~/.agents/skills/` for the user, and the ChatGPT desktop app reads the same standalone skills. The skills CLI above writes there when you pick Codex. By hand:

```bash
git clone --depth 1 https://github.com/stevesolun/steveskills /tmp/steveskills
mkdir -p ~/.agents/skills && cp -r /tmp/steveskills/<skill> ~/.agents/skills/   # e.g. tool-diet
```

Restart Codex if the skill does not show up in `/skills`.

### By hand, for anything else

Copy a skill folder into your agent's skills directory (Claude Code: `.claude/skills/` in the project or `~/.claude/skills/`). Keep the folder name equal to the `name` in its `SKILL.md`.

## Use

Each skill is **model-invoked**: the agent reaches for it on its own when the task matches the skill's description. You can also call any skill by name:

| Harness | Explicit call |
| --- | --- |
| Claude Code | `/<skill>` (or `/steveskills:<skill>` when installed as the plugin) |
| Codex CLI and IDE | `$<skill>`, or pick it from `/skills` |
| ChatGPT desktop | type `@` and pick the skill |

Prompts that make the agent reach for each skill without being told, and what comes back:

| Skill | Say something like | What comes back |
| --- | --- | --- |
| tool-diet | "Why did this session burn 300K tokens? Find the waste and fix it." / "That MCP server keeps returning huge payloads. Put it on a diet." | A table: the call, the kind of fat, the cut, tokens before → after, and the share of the session's tool tokens recovered. Durable cuts land in the repo. |
| acceptance-probes | "Implement ticket 14 and prove the acceptance criteria." / "Were the criteria on this ticket really met?" | `probes.sh`, one function per criterion, red at the start commit; after the work, `start: K of K FAIL, end: K of K PASS`, with criteria that were already true flagged and `HUMAN` ones left unticked. |
| reconcile | "We're done for today, close out the session." / "Wrap up: what's left on this branch?" | The raw `## git` and `## tracker` blocks, a table of discrepancies between git, tracker and the transcript's claims, nothing acted on until you confirm, and a last line `next: <work> (<skill>)`. |
| decision-ledger | "Write the spec from our interview." / "Publish the tickets; make sure nothing we decided got lost." | `.scratch/<effort>/ledger.md` with one line per settled decision and its source, and `honoured H of L live, missing M` with a file and line per hit before anything is published. |
| red-at-base | "Add tests for this change and tell me which ones would fail without it." / "Would these tests have caught the old behaviour?" | `N of M new or changed tests fail at base (<sha>): R red, E error, G green` with the ID list from a rerun in a throwaway worktree; a green test is changed or deleted, never explained. |
| whose-red | "The suite is red, is that me?" / "Can I skip this failing test, it looks unrelated." | One row per failing test: `mine`, `pre-existing`, `flaky` or `environment`, with the base run and repeat counts behind it, and `failing N: mine a, pre-existing b, flaky c, environment d`. |
| structure-map | "Write down how this repo is laid out for the next session." / "Refresh the structure map." | `docs/STRUCTURE.md` under 60 lines, each entry `fact | proof: <command> | expect: <output>`, and `confirmed C, stale S` from running every proof before the map is committed. |
| driver-split | "Why is gross margin down in EMEA this quarter?" / "How much of the drop is the UK versus everything else?" | A table of parts that add up to the change: per segment, mix effect, rate effect and interaction in points, ranked, the largest driver named, the residual sized. |
| clean-log | "Clean this export and tell me everything you changed." | The cleaning as a script with dropped rows in a side file, and a log computed from the two files: rows by key, columns, cells changed per column by kind with examples, both checksums. |
| ab-readout | "Write up the checkout test and tell me whether to ship it." | SRM check, rate per arm with interval, lift with interval and p-value, smallest detectable effect and sample needed, then one verdict line that is the only recommendation. |
| number-trace | "Help me understand this paper, with the key numbers quoted." / "Write up the analysis of this file using only numbers you computed." | One row per number in the summary: the source line it matched, `labelled` for a figure the summary marks as computed or assumed, or NOT FOUND; `numbers: N in doc, F found, L labelled, M not found`, exit 1 while any is unfound. |
| criteria-map | "Draft the grant against these review criteria." / "Which criteria does my proposal address weakly?" | Words and share per criterion, the mapped sections, NONE and THIN flags, and every placeholder with its line. |

Every skill ends in a number or an artifact a second pair of eyes can check, never in the agent's own assessment of its work.

## Layout

```text
.claude-plugin/        # Claude Code plugin and marketplace manifests
CHANGELOG.md           # one entry per release
<skill>/
├── README.md          # the docs page: what it does, when to reach for it, common questions, it's working if
├── SKILL.md           # the skill itself (frontmatter + instructions)
├── <REFERENCE>.md     # reference a branch of the skill loads on demand, where a skill has one
├── agents/openai.yaml # Codex and ChatGPT picker metadata
└── scripts/           # the one script that prints the number behind the claim
```

## License

MIT

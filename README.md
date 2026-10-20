# steveskills

A directory of agent skills by Steve Solun. A **skill** is a folder with a `SKILL.md` that an agent reads when a task matches its description, plus whatever scripts and reference files the instructions need. The agent keeps only the one-line description in context until it needs the rest, so a skill costs nothing until it fires.

Every skill here follows the same rules:

- **One job.** Each folder does one thing and says in its description exactly when it should and should not fire.
- **Numbers, not advice.** Where a skill makes a claim about tokens, time or correctness, it ships the script that measures it and reports before and after numbers.
- **Fixes live in the environment.** A skill leaves behind a flag, a script, a check or a config, never a paragraph in a steering file that every session has to re-read.
- **One copy, every harness.** Written to the open [Agent Skills](https://agentskills.io) format, with Codex and ChatGPT picker metadata beside it, so the same folder works in Claude Code, Codex, ChatGPT, Copilot, Cursor and anything else that reads the standard.

The directory grows one folder at a time. The table below is the index.

## Skills

| Skill | What it does |
| --- | --- |
| [tool-diet](./tool-diet) | Puts tool results on a diet. Measures which tool, CLI, script or MCP results in a session cost the most tokens for the least use, cuts the fat at its source, and proves the saving with before and after numbers. |
| [deeper](./deeper) | Rewrites a task for expert depth, not size. Names the raw inputs, instruments and outside check a top practitioner would use, rewrites the prompt to ask for exactly that, counts the depth markers before and after, and runs it against that check. |
| [acceptance-probes](./acceptance-probes) | Turns a ticket's acceptance criteria into runnable probes before any implementation, proves each probe fails at the start commit, freezes the probes, and reruns them to accept the work as a count. |
| [reconcile](./reconcile) | Closes a session by reconciling git, the tracker and the transcript's own claims into a discrepancy table, acting only on what you confirm, and ending with the next piece of work. |
| [decision-ledger](./decision-ledger) | Keeps an append-only ledger of settled decisions with their source and audits each spec, ticket set or PR against it before publishing, so no decision is lost between phases and none is re-asked. |
| [red-at-base](./red-at-base) | Reruns every new or changed test at the base commit in a throwaway worktree and counts how many fail there, so a test that passes without the change is found and then changed or deleted rather than kept. |
| [whose-red](./whose-red) | When a test fails, says whose red it is from runs rather than words: mine, pre-existing, flaky or environment, one table row per test with a base run and repeat counts behind it, before anything is deselected or called unrelated. |
| [structure-map](./structure-map) | Writes or refreshes a repository structure map: the facts a fresh agent cannot recover from the file tree in under a minute, each paired with the command that proves it, checked by one script that reports confirmed and stale. |
| [with-receipts](./with-receipts) | Delivers a number from data with its receipt: the question as resolved, the source and its freshness from the data, the query as it ran, a second route to the same number with the delta, and a reviewer who did not write the query. |
| [driver-split](./driver-split) | Answers why a number moved with named parts that add up to the change: per segment, mix effect and rate effect, ranked by size, residual sized. |
| [answer-key](./answer-key) | Keeps a file of data questions with known answers, runs it on every change to the data model, definitions or analysis skill, logs each run with its git SHA, and gates on the pass rate. |
| [clean-log](./clean-log) | Cleans a data file by script and ships it with a change log computed from the two files: rows, columns, and per-column cell changes by kind, with checksums. |
| [ab-readout](./ab-readout) | Writes up an A/B test from its counts in the only safe order: sample ratio mismatch, rates with intervals, lift with its interval and p-value, detectable effect, then one verdict line. |

More folders will land here. Each one carries its own README with details and sample output.

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
| deeper | "/deeper find out why checkout conversion dropped last month" / "Give me the expert version of this task, not a longer one." | The expert gap, raw inputs, instruments and outside proof; a rewritten prompt; depth markers before → after; then the run, reported against the outside check first. `--full` adds the outcome and other fields, `--run` skips the stop. |
| acceptance-probes | "Implement ticket 14 and prove the acceptance criteria." / "Were the criteria on this ticket really met?" | `probes.sh`, one function per criterion, red at the start commit; after the work, `start: K of K FAIL, end: K of K PASS`, with criteria that were already true flagged and `HUMAN` ones left unticked. |
| reconcile | "We're done for today, close out the session." / "Wrap up: what's left on this branch?" | The raw `## git` and `## tracker` blocks, a table of discrepancies between git, tracker and the transcript's claims, nothing acted on until you confirm, and a last line `next: <work> (<skill>)`. |
| decision-ledger | "Write the spec from our interview." / "Publish the tickets; make sure nothing we decided got lost." | `.scratch/<effort>/ledger.md` with one line per settled decision and its source, and `honoured H of L live, missing M` with a file and line per hit before anything is published. |
| red-at-base | "Add tests for this change and tell me which ones would fail without it." / "Would these tests have caught the old behaviour?" | `N of M new or changed tests fail at base (<sha>): R red, E error, G green` with the ID list from a rerun in a throwaway worktree; a green test is changed or deleted, never explained. |
| whose-red | "The suite is red, is that me?" / "Can I skip this failing test, it looks unrelated." | One row per failing test: `mine`, `pre-existing`, `flaky` or `environment`, with the base run and repeat counts behind it, and `failing N: mine a, pre-existing b, flaky c, environment d`. |
| structure-map | "Write down how this repo is laid out for the next session." / "Refresh the structure map." | `docs/STRUCTURE.md` under 60 lines, each entry `fact | proof: <command> | expect: <output>`, and `confirmed C, stale S` from running every proof before the map is committed. |
| with-receipts | "How many active customers did we have last month?" / "Put the weekly metrics in a report I can send to the board." | The number with a `receipt:` block: question as resolved, source, freshness (newest date in the data), the query, the cross-check route, the delta, the reviewer; `receipts.py footer` exits 0 only when all seven are there. |
| driver-split | "Why is gross margin down in EMEA this quarter?" / "How much of the drop is the UK versus everything else?" | A table of parts that add up to the change: per segment, mix effect, rate effect and interaction in points, ranked, the largest driver named, the residual sized. |
| answer-key | "We changed the revenue definition; is the analytics agent still right?" / "Can we launch the finance domain to stakeholders?" | `P of N pass (rate)` per run, one row per question with expected and actual, a log row with git SHA and label, exit 1 under the gate. |
| clean-log | "Clean this export and tell me everything you changed." | The cleaning as a script with dropped rows in a side file, and a log computed from the two files: rows by key, columns, cells changed per column by kind with examples, both checksums. |
| ab-readout | "Write up the checkout test and tell me whether to ship it." | SRM check, rate per arm with interval, lift with interval and p-value, smallest detectable effect and sample needed, then one verdict line that is the only recommendation. |

Every skill ends in a number or an artifact a second pair of eyes can check, never in the agent's own assessment of its work.

## Layout

```text
.claude-plugin/        # Claude Code plugin and marketplace manifests
<skill>/
├── README.md          # what it does, when it fires, sample output
├── SKILL.md           # the skill itself (frontmatter + instructions)
├── agents/openai.yaml # Codex and ChatGPT picker metadata
└── scripts/           # anything the skill runs
```

## License

MIT

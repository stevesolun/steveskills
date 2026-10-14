# steveskills

A directory of agent skills by Steve Solun. A **skill** is a folder with a `SKILL.md` that an agent reads when a task matches its description, plus whatever scripts and reference files the instructions need. The agent keeps only the one-line description in context until it needs the rest, so a skill costs nothing until it fires.

Every skill here follows the same rules:

- **One job.** Each folder does one thing and says in its description exactly when it should and should not fire.
- **Measured, not preached.** Where a skill makes a claim about tokens, time or correctness, it ships the script that measures it and reports before and after numbers.
- **Fixes live in the environment.** A skill leaves behind a flag, a script, a check or a config, never a paragraph in a steering file that every session has to re-read.
- **One copy, every harness.** Written to the open [Agent Skills](https://agentskills.io) format, with Codex and ChatGPT picker metadata beside it, so the same folder works in Claude Code, Codex, ChatGPT, Copilot, Cursor and anything else that reads the standard.

The directory grows one folder at a time. The table below is the index.

## Skills

| Skill | What it does |
| --- | --- |
| [tool-diet](./tool-diet) | Puts tool results on a diet. Measures which tool, CLI, script or MCP results in a session cost the most tokens for the least use, cuts the fat at its source, and proves the saving with before and after numbers. |

More folders will land here. Each one carries its own README with details and sample output.

## Install

Pick one route per agent. Installing a skill twice makes it show up twice.

### Any agent, with the skills CLI

```bash
npx skills@latest add stevesolun/steveskills --skill=tool-diet
```

The CLI asks which agents to install for and puts the files where each one looks. Useful flags:

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

### Codex and ChatGPT

Codex reads `.agents/skills/` in a repo and `~/.agents/skills/` for the user, and the ChatGPT desktop app reads the same standalone skills. The skills CLI above writes there when you pick Codex. By hand:

```bash
git clone --depth 1 https://github.com/stevesolun/steveskills /tmp/steveskills
mkdir -p ~/.agents/skills && cp -r /tmp/steveskills/tool-diet ~/.agents/skills/
```

Restart Codex if the skill does not show up in `/skills`.

### By hand, for anything else

Copy a skill folder into your agent's skills directory (Claude Code: `.claude/skills/` in the project or `~/.claude/skills/`). Keep the folder name equal to the `name` in its `SKILL.md`.

## Use

Each skill is **model-invoked**: the agent reaches for it on its own when the task matches the skill's description. You can also call it by name.

| Harness | Explicit call |
| --- | --- |
| Claude Code | `/tool-diet` (or `/steveskills:tool-diet` when installed as the plugin) |
| Codex CLI and IDE | `$tool-diet`, or pick it from `/skills` |
| ChatGPT desktop | type `@` and pick `tool-diet` |

Prompts that make the agent reach for `tool-diet` without being told:

```text
Why did this session burn 300K tokens? Find the waste and fix it.
```

```text
That MCP server keeps returning huge payloads. Put it on a diet.
```

```text
Run the tool diet on the last session log and show me before and after.
```

What comes back is a short table: the call, the kind of fat, the cut, tokens before → after, and one line with the share of the session's tool tokens recovered. Durable cuts land in the repo (a flag, a wrapper script, an MCP tool description), so the next session is lean without being told.

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

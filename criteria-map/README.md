# criteria-map

An agent skill for drafting a grant, funding or project proposal against the criteria it will be judged on: an outline with one section per criterion, first drafts with placeholders for the figures the author has not supplied, and a map that shows the words devoted to each criterion, the criteria left thin or unmapped, and the placeholders still open.

Works in Claude Code, Codex, Copilot, Cursor and any other harness that reads the [Agent Skills](https://agentskills.io) format. By Steve Solun. MIT.

## Install

```bash
npx skills@latest add stevesolun/steveskills --skill=criteria-map
```

```bash
npx skills@latest update criteria-map
```

Or, in Claude Code, as a plugin that updates itself:

```bash
claude plugin marketplace add stevesolun/steveskills
claude plugin install steveskills@steveskills
```

Pick one route per agent; installing both gives you the skill twice.

## The idea

The research-role ask for a grant is precise: collect the funder, the criteria, the aims, the novelty, the team and the limits in one message; draft an outline mapped to the criteria and first drafts of the aims and significance; leave placeholders for preliminary data, budget and citations and invent none of them; and say which criteria the idea addresses weakly. Reviewers score against the list, so a proposal's weakness is a criterion with too few words behind it, and its most dangerous state is a placeholder that reads like a figure.

`criteria-map` lays the draft over the list. The criteria file is the funder's own wording; the draft's headings use that wording; the script maps each criterion to the sections that answer it (the heading that names it best, with its subsections, or failing that the sections carrying its keywords), prints the words and the share of the draft per criterion, flags criteria that are NONE or THIN, and counts the placeholders left, with their lines.

## How it runs

The agent reaches for it when preparing a grant or funding application, a proposal against a published template or rubric, or when asked which criteria a draft addresses weakly. Typing `/criteria-map` works too.

1. **Collect the inputs in one message**; the criteria go to `CRITERIA.txt`, one per line, keywords after a colon.
2. **Outline one section per criterion**, headings in the criterion's words.
3. **Draft with placeholders, in the field's register**; nothing invented in a placeholder's place.
4. **Map.** `criteria-map.py CRITERIA.txt DRAFT.md --placeholders`.
5. **Strengthen the weak criteria, then close the placeholders.**

## Sample output

A real run on a proposal written against a published template: the Kubernetes project's enhancement proposal for user namespaces (KEP-127, 9,375 words, from the project's [enhancements](https://github.com/kubernetes/enhancements) repository; the main Kubernetes repository has about 115k stars), mapped against the fifteen sections the KEP template requires.

```text
$ criteria-map.py kep-criteria.txt keps/sig-node/127-user-namespaces/README.md
draft: 80 sections, 9375 words; criteria: 15
criterion                           words  share holes  sections
Summary                                 7     0%     0  THIN Summary
Motivation                            506     5%     0       Motivation
Goals                                 127     1%     0       Goals
Non-Goals                              75     1%     0       Non-Goals
Proposal                              347     4%     0       Proposal
Risks and Mitigations                 104     1%     0       Risks and Mitigations
Design Details                       3136    33%     0       Design Details
Test Plan                             519     6%     0       Test Plan
Graduation Criteria                   124     1%     0       Graduation Criteria
Upgrade / Downgrade Strategy           83     1%     0       Upgrade / Downgrade Strategy
Version Skew Strategy                 477     5%     0       Version Skew Strategy
Production Readiness Review Questi   3587    38%     0       Production Readiness Review
Monitoring Requirements               461     5%     0       Monitoring Requirements
Drawbacks                               0     0%     0  THIN Drawbacks
Alternatives                          732     8%     0       Alternatives

unmapped criteria: 0; thin: 2 (Summary, Drawbacks)
placeholders left in the draft: 0
```

Exit code 1. A mature, merged proposal still has a seven-word summary and an empty Drawbacks section, which is what a reviewer scoring against the template would circle first; design details and the production-readiness questionnaire carry 71 percent of the words between them. On a grant draft the same table shows which review criterion got two paragraphs out of ten pages.

## Why a script

"Which criteria do I address weakly?" has an answer in words per criterion, and a writer cannot see their own draft that way. `criteria-map.py` counts it, flags the thin and the missing, and lists every placeholder with a line number, so the draft ships when the map is full and the count of open placeholders is zero, not when it feels finished.

## Files

```text
criteria-map/
├── SKILL.md                     # the skill
├── agents/openai.yaml           # Codex picker metadata
└── scripts/criteria-map.py      # words per criterion, thin and unmapped criteria, placeholders; --help for options
```

## License

MIT

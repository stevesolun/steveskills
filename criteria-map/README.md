# criteria-map

An agent skill for drafting a grant, funding or project proposal against the criteria it will be judged on: an outline with one section per criterion, first drafts with placeholders for the figures the author has not supplied, and a map that shows the words devoted to each criterion, the criteria left thin or unmapped, and the placeholders still open. By Steve Solun. MIT.

## What it does

It lays the draft over the list it will be scored against. Reviewers read a proposal against a public list, the funder's criteria or the template's required sections, so a proposal's weakness is a criterion with too few words behind it, and its most dangerous state is a placeholder that reads like a figure. Here every criterion gets a word count, every missing or thin one gets a flag, and every placeholder is listed with its line; a placeholder stays a placeholder until the author supplies the figure.

## When to reach for it

Type `/criteria-map`, or the agent reaches for it on its own when a task fits: preparing a grant or funding application, drafting a proposal against a published template or rubric, or answering which criteria a draft addresses weakly.

| Situation | Reach for |
| --- | --- |
| The proposal will be scored against a published list | this skill |
| The draft's sentences need support or softening | [cite-or-cut](../cite-or-cut) |
| A section must cite only the files the author collected | [source-bound](../source-bound) |

A document with no stated criteria has nothing to map.

## Prerequisites

The criteria in the funder's own words: the published review criteria, the template's required sections, or the rubric, pasted or linked. They go into `CRITERIA.txt`, one per line, with a colon and keywords where the funder's wording uses several terms for one criterion.

## The map

The **map** is the draft laid over the criteria: for every criterion, the sections that answer it and how many words they carry, so a thin answer and a missing one are visible as numbers before a reviewer finds them. A section is mapped to a criterion when its heading shares a word with the criterion's name (with its subsections), or, failing that, when the criterion's keywords appear in it.

```text
criteria-map.py CRITERIA.txt DRAFT.md [--placeholders] [--thin N]
```

Per criterion it prints the mapped sections, the words devoted, the share of the draft and the placeholders in them, flags `NONE` (no section) and `THIN` (under 40 words, or `--thin N`), then the unmapped and thin criteria by name and, with `--placeholders`, every placeholder (`[PRELIMINARY DATA]`, `[BUDGET]`, `[CITATION]`, `TODO`, `TBD`, `XXX`, `???`) with its line. Exit 1 while any criterion is unmapped or any placeholder remains.

## Common questions

**A merged, mature proposal came out with two THIN criteria. Is the threshold too strict?**
The run below is a Kubernetes enhancement that was accepted and shipped, and its Summary is seven words and its Drawbacks section is empty. Those are the two things a reviewer scoring against the template circles first; the flag is right, and the proposal was accepted on its other 9,000 words. `--thin N` moves the line when a funder's format calls for shorter sections.

**The funder's criterion uses different words from my headings.**
Headings in the criterion's own words map first; where the limits force a merged section, its heading names both criteria. For the rest, the keywords after the colon in `CRITERIA.txt` carry the funder's other terms (`Broader impacts: outreach, training, society`), and a section is mapped when those appear in it.

## It's working if

- Every criterion has a mapped section with a word count, and `NONE` or `THIN` appears next to the ones a reviewer would circle, by name.
- Every placeholder in the draft is listed with its line, and the draft ships with that list or with zero.
- No figure, result or reference in the draft came from anywhere but the author's material; the square brackets are where the figures will go.
- The weak criteria are named with words and share, not with an impression of the whole.

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

### A/B against a baseline skill set

Four blind repetitions, each a fresh headless session: arm A had a baseline skill set, arm B the same set plus this skill. The task was a Kubernetes enhancement proposal drafted against the template's fifteen required sections from 395 words of author notes that say what the author does not have (no benchmark, no SLO numbers, no PRR answers); two repetitions said "leave placeholders rather than filling in", two asked plainly. Pre-registered counts: S, required sections missing; V, numbers with units in the draft that the notes do not carry and that sit outside a placeholder; W, thin sections (under 40 words) the report does not name as weak. Win: S = V = W = 0 with the skill and at least one above 0 without.

| Rep | Design | Arm A (baseline set) | Arm B (baseline + skill) | Win | Blind grader (bullets) |
| --- | --- | --- | --- | --- | --- |
| rep1 | instruction in prompt | S=0, V=0, W=2 | S=0, V=0, W=0 | B | A 2/4, B 3/4 |
| rep2 | instruction in prompt | S=0, V=1, W=2 | S=0, V=0, W=0 | B | A 2/4, B 4/4 |
| rep3 | plain ask | S=0, V=3, W=1 | S=0, V=2, W=0 | none | A 1/4, B 4/4 |
| rep4 | plain ask | S=0, V=4, W=1 | S=0, V=0, W=0 | B | A 1/4, B 4/4 |

Three wins of four. The baseline left Goals and Non-Goals thin without saying so in both prompted repetitions, and on the plain ask wrote three and then four figures the author never supplied (an evaluation time under 1 ms, a 60-second window, 80 and 100 bytes per window). The skill arm wrote one such estimate in repetition 3, "roughly 100 bytes", hedged in prose instead of placed in a placeholder, which cost it that repetition. The blind grader put the skill arm at 3/4 once and 4/4 three times, the baseline at 1 or 2.

## Where it fits

A reach-for-it-anytime standalone for the research role. Its neighbours are [cite-or-cut](../cite-or-cut), because once the sections are drafted their sentences still have to earn their claims, and [source-bound](../source-bound), because a proposal's background section drawn from a folder of papers has to cite only those papers. The index of every skill is the [root README](../README.md#skills).

## Install

```bash
npx skills@latest add stevesolun/steveskills --skill=criteria-map
```

Other routes (Claude Code plugin, Codex, by hand) are in the [root README](../README.md#install).

## Files

```text
criteria-map/
├── SKILL.md                     # the skill
├── agents/openai.yaml           # Codex and ChatGPT picker metadata
└── scripts/criteria-map.py      # words per criterion, thin and unmapped criteria, placeholders; --help for options
```

## License

MIT

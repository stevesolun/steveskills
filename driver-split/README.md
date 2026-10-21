# driver-split

An agent skill that answers "why did the number move?" with named parts that add up to the change: per segment, how much came from the segment's weight shifting and how much from the rate inside it moving, ranked by size, with the residual called a residual and sized. By Steve Solun. MIT.

## What it does

It turns a why-question about a metric into arithmetic that closes. For a rate (margin, conversion, fix rate) the change between two points is split, per segment, into a mix effect, a rate effect and their interaction; for a total, into each segment's change and share. The parts in the answer add up to the change the asker quoted, and anything unexplained is named as a residual with its size; a cause with no size is a guess the write-up is not allowed to make.

## When to reach for it

Type `/driver-split`, or the agent reaches for it on its own when a task fits: being asked why a metric fell or rose, what is driving a move, or how much of a change is one segment versus everything else.

| Situation | Reach for |
| --- | --- |
| A number moved between two points and someone wants the reasons, sized | this skill |
| Two arms were randomly assigned and the question is whether the difference is real | [ab-readout](../ab-readout) |

A number with no before and after has nothing to split.

## Prerequisites

Python 3, and the metric reproducible from the source at both points with the same query. The segments go in a CSV, one row each: `segment,before_num,before_den,after_num,after_den` for a rate, `segment,before,after` for a total, with every row of the source in exactly one segment so the segments sum to the whole (an "other" bucket catches the rest).

## The split

A **split** is a list of named parts that add up to the change, biggest first. The shape is what the business expects of a good answer to "why is it down": 2.4 of the 3.2 points in one segment, two more parts of 0.4 each, the rest named as approximate. What goes wrong in practice is a paragraph that names a cause without a size, or parts that quietly do not sum to the move the asker quoted.

```text
driver-split.py SEGMENTS.csv [--unit pts|abs]
```

For a rate file it prints, per segment, the weight before and after, the rate before and after, and the mix, rate and interaction effects (`--unit pts` as percentage points, `--unit abs` in the metric's own units), ranked by size; then `parts: ... change: ... add up`, and the largest driver with its share of the move. For a total file it prints each segment's change and share. Segments that pull in opposite directions are reported as offsetting, because a small net move can hide two large drivers. Each deeper level (the largest driver split again on a second dimension) is its own run, kept with its file.

## Common questions

**Mix or rate: which one is the cause?**
Both are, in the proportions the table prints, and the two answer different questions. In the sample run the largest part is `platforms` at +9.88 lines per file; its files did get longer (+5.12, the rate effect), but more of its contribution is mix (+6.85): the shortest-file area shrank from 47% to 28% of the codebase, which pulls the average up without any file changing. A paragraph would have said "TypeScript made the files longer" and been half right.

**The net change is small but the parts are huge. Which do I report?**
The parts, with the net stated as what they add up to. In the second sample run the net is -1,757 lines, while one part alone is -2,631 and another is +1,899; the script says `the overall change is only -1757 because other parts offset it`, and the write-up says the same instead of reporting a quiet net.

**My segments do not sum to the whole.**
Then the split cannot close, and the script will say the parts do not add up. Every row of the source belongs to exactly one segment; an "other" bucket holds whatever the chosen dimension does not name.

## It's working if

- The write-up's parts add up to the change the asker quoted, and the script's `add up` line is quoted beneath them.
- The largest driver is named with its size and its share of the move, and offsetting parts are called out whenever the net is small.
- A second-level split exists on the largest driver, or the remaining unexplained part is labelled residual and sized.

Two real splits on [vuejs/vue](https://github.com/vuejs/vue) (212k stars) between the tags `v2.6.14` and `v2.7.16`, the release that rewrote the codebase in TypeScript. First, a ratio: the average length of a source file under `src/`, split by area. Weight is each area's share of files; rate is its lines per file.

```text
$ driver-split.py lines-per-file.csv --unit abs
overall rate: 93.69 -> 110.94  change +17.25
segment                     weight              rate      mix     rate    inter    total
platforms             46.9%-> 27.7%   58.01->  68.93    +6.85    +5.12    -2.10    +9.88
core                  30.9%-> 40.5%  109.68-> 119.93    +1.54    +3.17    +0.99    +5.69
compiler               9.3%-> 12.2%  177.00-> 185.61    +2.40    +0.80    +0.25    +3.45
server                11.3%->  0.0%  119.59->   0.00    -2.94   -13.56   +13.56    -2.94
v3                     0.0%-> 12.2%    0.00-> 105.50   -11.39    +0.00   +12.83    +1.44
src                    0.0%->  0.7%    0.00->  17.00    -0.63    +0.00    +0.11    -0.52
shared                 1.0%->  1.4%  182.50-> 199.00    +0.28    +0.17    +0.05    +0.51
sfc                    0.5%->  0.0%  134.00->   0.00    -0.21    -0.69    +0.69    -0.21
types                  0.0%->  5.4%    0.00->  92.75    -5.06    +0.00    +5.01    -0.05

parts: +17.25  change: +17.25  add up
largest driver: platforms (+9.88 of +17.25, 57% of the move)
```

Files got 17 lines longer on average. The largest part is `platforms`, and the split says why in two numbers: its files did get longer (+5.12, the rate effect), but more of its contribution is mix (+6.85): the shortest-file area shrank from 47% to 28% of the codebase when the Weex platform was dropped, which pulls the average up without any file changing. A paragraph would have said "TypeScript made the files longer" and been half right.

Second, a total: lines of source under `src/` by area.

```text
$ driver-split.py loc.csv
overall total: 18176 -> 16419  change -1757
segment                    before        after       change    share
server                       2631            0        -2631     150%
platforms                    5279         2826        -2453     140%
v3                              0         1899        +1899    -108%
types                           0          742         +742     -42%
core                         6581         7196         +615     -35%
compiler                     3186         3341         +155      -9%
sfc                           134            0         -134       8%
shared                        365          398          +33      -2%
src                             0           17          +17      -1%

parts: -1757  change: -1757  add up
largest driver: server (-2631); the overall change is only -1757 because other parts offset it
```

The net change is small and misleading on its own: server rendering and Weex left the tree, the Vue 3 compatibility layer and the type definitions arrived, and the script reports the offsetting parts instead of the net.

### A/B against a baseline skill set

Four blind repetitions, each a fresh headless session: arm A had a baseline skill set, arm B the same set plus this skill. The task was the vuejs/vue commit log and the question why files touched per commit fell from 2021 to 2022, split by contributor type (Evan You, bots, everyone else): a move of 0.28 that hides large offsetting parts (Evan You's share of commits 7% to 80%, bots 36% to 2%, others' commits 13.1 to 7.6 files). Two repetitions asked for parts that add up with share and size per type, two asked why. Pre-registered: TOTAL, the overall before and after; MIX, commit shares for two or more types; RATE, within-type files per commit for two or more types; ADD, per-type contributions that sum to the change. Win: all four with the skill, a miss without.

| Rep | Design | Arm A (baseline set) | Arm B (baseline + skill) | Win | Blind grader (bullets) |
| --- | --- | --- | --- | --- | --- |
| rep1 | instruction in prompt | TOTAL=no, MIX=yes, RATE=yes, ADD=no | TOTAL=yes, MIX=yes, RATE=yes, ADD=yes | B | A 3/4, B 4/4 |
| rep2 | instruction in prompt | TOTAL=yes, MIX=yes, RATE=yes, ADD=no | TOTAL=yes, MIX=yes, RATE=yes, ADD=yes | B | A 3/4, B 4/4 |
| rep3 | plain ask | TOTAL=yes, MIX=yes, RATE=yes, ADD=no | TOTAL=yes, MIX=yes, RATE=yes, ADD=yes | B | A 0/4, B 4/4 |
| rep4 | plain ask | TOTAL=yes, MIX=yes, RATE=yes, ADD=no | TOTAL=no, MIX=yes, RATE=yes, ADD=no | none | A 0/4, B 4/4 |

Three of four: passed. The baseline knew the shares and the rates every time and never produced parts that add up to the change; the skill arm did in three, and in repetition 4 its answer carried neither the overall line nor a sum. The blind grader put the skill arm at 4/4 in all four and the baseline at 3, 3, 0 and 0.

## Where it fits

A reach-for-it-anytime standalone for the data role, usually the second question after a number has landed. Its neighbours are [ab-readout](../ab-readout), because a move between two randomly assigned arms is a different question with its own intervals, and [clean-log](../clean-log), because the segment file is only as clean as the export it came from. The index of every skill is the [root README](../README.md#skills).

## Install

```bash
npx skills@latest add stevesolun/steveskills --skill=driver-split
```

Other routes (Claude Code plugin, Codex, by hand) are in the [root README](../README.md#install).

## Files

```text
driver-split/
├── SKILL.md                     # the skill
├── agents/openai.yaml           # Codex and ChatGPT picker metadata
└── scripts/driver-split.py      # rate (mix, rate, interaction) and total splits; --help for options
```

## License

MIT

# driver-split

An agent skill that answers "why did the number move?" with named parts that add up to the change: per segment, how much came from the segment's weight shifting and how much from the rate inside it moving, ranked by size, with the residual called a residual and sized.

Works in Claude Code, Codex, Copilot, Cursor and any other harness that reads the [Agent Skills](https://agentskills.io) format. By Steve Solun. MIT.

## Install

```bash
npx skills@latest add stevesolun/steveskills --skill=driver-split
```

```bash
npx skills@latest update driver-split
```

Or, in Claude Code, as a plugin that updates itself:

```bash
claude plugin marketplace add stevesolun/steveskills
claude plugin install steveskills@steveskills
```

Pick one route per agent; installing both gives you the skill twice.

## The idea

The most common data question from the business is a why: why is gross margin down in EMEA this quarter, why did conversion drop, why is churn up. The shape of a good answer is fixed, and Anthropic's own worked example of the ad-hoc data question shows it: 2.4 of the 3.2 points are one segment, two more parts of 0.4 each, and the rest named as approximate. Parts, sizes, a residual, biggest first. What goes wrong in practice is a paragraph that names a cause without a size, or parts that do not add up to the change the asker quoted.

`driver-split` does the arithmetic. For a rate (margin, conversion, fix rate) the change between two points is split, per segment, into a mix effect (the segment's share of the whole moved), a rate effect (the rate inside the segment moved) and their interaction; the three columns add up to the change exactly. For a total, each segment's change and share. Offsetting drivers are reported as offsetting, because a small net move can hide two large ones.

## How it runs

The agent reaches for it when asked why a metric fell or rose, what is driving a move, or how much of a change is one segment versus everything else. Typing `/driver-split` works too.

1. **Fix the number and the two points.** The metric as defined, and the before and after reproduced from the source with the same query.
2. **Choose the segmentation** and extract one row per segment; the segments sum to the whole.
3. **Split the change.** `driver-split.py SEGMENTS.csv` prints the table, checks the parts add up, names the largest driver.
4. **Go one level down** on the largest driver with a second dimension until what is left is small or has a dated cause.
5. **Write the answer as the split**, observations first, files saved so it can be rerun.

## Sample output

Two real splits from [stevesolun/ctx](https://github.com/stevesolun/ctx) at `11b582a7`. First, a rate: the fix rate of the bug tracker, high-severity bugs (P0 and P1, 34 bugs) against lower-severity ones (P2 and P3, 58 bugs), split by journey.

```text
$ driver-split.py fixrate.csv
overall rate: 82.35% -> 81.03%  change -1.32 pts
segment                     weight              rate      mix     rate    inter    total
trials                38.2%-> 12.1%   92.3%->  42.9%    -2.60   -18.91   +12.94    -8.57
budget                32.4%->  6.9%   63.6%->  75.0%    +4.76    +3.68    -2.89    +5.55
analysis               2.9%-> 29.3%  100.0%->  94.1%    +4.65    -0.17    -1.55    +2.93
json                   5.9%-> 13.8%  100.0%->  75.0%    +1.40    -1.47    -1.98    -2.05
recommend             17.6%-> 13.8%   83.3%->  87.5%    -0.04    +0.74    -0.16    +0.54
surface                2.9%-> 24.1%  100.0%->  85.7%    +3.74    -0.42    -3.03    +0.29

parts: -1.32  change: -1.32  add up
largest driver: trials (-8.57); the overall change is only -1.32 because other parts offset it
```

The headline number barely moved. Inside it, the trials journey's fix rate fell from 92% to 43%, worth 19 points on its own, and was hidden by the mix shifting toward journeys that fix almost everything. That is the finding a paragraph would have missed.

Second, a total: Python lines by area between a tagged release and the pinned commit.

```text
$ driver-split.py loc.csv
overall total: 395044 -> 396055  change +1011
segment                    before        after       change    share
src/tests                  198219       198861         +642      64%
src/ctx                    128322       128741         +419      41%
scripts                     29430        29283         -147     -15%
src (flat)                  37389        37486          +97      10%
hooks                         393          393           +0       0%
imported-skills              1291         1291           +0       0%

parts: +1011  change: +1011  add up
largest driver: src/tests (+642 of +1011, 64% of the move)
```

## Why a script

Mix and rate effects are easy to describe and easy to get wrong by hand, and a split that does not add up is two guesses dressed as one answer. `driver-split.py` computes the identity, checks it, and ranks the parts, so the write-up can only contain parts that sum to the change the asker quoted.

## Files

```text
driver-split/
├── SKILL.md                     # the skill
├── agents/openai.yaml           # Codex picker metadata
└── scripts/driver-split.py      # rate (mix, rate, interaction) and total splits; --help for options
```

## License

MIT

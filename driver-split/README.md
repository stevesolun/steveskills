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

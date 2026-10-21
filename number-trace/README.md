# number-trace

An agent skill for summarising a paper, a report or a data analysis so that every number in the summary traces to the source text or to an output the analysis computed, and every number that does not is named as assumed, remembered or missing. By Steve Solun. MIT.

## What it does

It makes "I kept to the text" checkable. The summary is written with numbers quoted as the source prints them; a script then takes every number in the summary, with its unit, and finds it in the source files, printing the source line it matched. A number the writer computed or brought in from outside is marked in its own sentence, `(computed from ...)` or `(assumed ...)`, and counted apart. The summary ships only when every number is found or labelled; the script's exit code, not the writer's word, says which.

## When to reach for it

Type `/number-trace`, or the agent reaches for it on its own when a task fits: summarising a paper or report with its key numbers, writing up an analysis of a data file, or sending any document with figures as a faithful account of a source.

| Situation | Reach for |
| --- | --- |
| The summary's numbers must come from the source | this skill |

Prose with no numbers is a citation check, not a trace.

## Prerequisites

Sources are text files, or PDFs with a text layer: `pdftotext` (poppler) is used when present, `pypdf` otherwise. A scanned PDF with no text layer is reported as such and its figures stay out of reach.

## The trace

A **trace** is the link from a number in the summary back to the place it came from: a line of the source, a cell of a table, a row of the analysis output. The script traces each number with its unit (`10 ms`, `45%`, `2.5 GB/s`, `6-7 round trips`), so a `10` in `10,000 us` is not the `10 ms` the summary quotes; when a number recurs in the source, it reports the line that shares the most words with the sentence, so the eye check lands on the right line. Dates, versions, list numbering and section, figure, table and reference numbers are skipped: they are labels, not quantities.

```text
number-trace.py --doc SUMMARY.md SOURCE [SOURCE ...]
```

One row per number: the source line it matched (`unit apart` when the number is there but its unit sits in a column header or the sentence before, so the eye check is owed), `labelled` with the label's kind, or `NOT FOUND`; then `numbers: N in doc, F found, L labelled, M not found`. Exit 1 while any number is neither found nor labelled.

## Common questions

**The same number appears in the source with a different meaning. Does the trace catch that?**
Not by itself: a trace is a presence check with the unit attached. That is why each found row prints the source line it matched and why the skill's last step is an eye check of those lines. The unit removes most coincidences (`45 ms` has to be 45 ms in the source); the printed line catches the rest.

**Why does a labelled number pass?**
Because the reader can see the label. A summary may need a figure the source does not carry; the failure is supplying it silently. `(assumed)` or `(computed from Table 1: 60 of 500)` in the sentence puts the number's status where the reader looks, and the trace counts those apart instead of failing on them.

**What about numbers written in words?**
`twelve percent` is invisible to the script. The summary is written by the agent, and step 2 has it quote digits; a source that spells a number out is quoted as digits with the source's wording beside it.

**The figure is only in a chart.**
Then the text does not carry it, and the summary says so ("the paper reports it in Figure 3") rather than reading a value off the picture.

## It's working if

- Every number in the summary has a row, and every row ends in a source line or a label; a summary with a `NOT FOUND` row does not go out.
- The two or three figures a writer would normally add from memory are visibly labelled in the text, or absent.
- An earlier draft's "from memory" turns out to be in the source: the trace finds it, and the label comes off.

A real run on the "Latency numbers every programmer should know" section of [donnemartin/system-design-primer](https://github.com/donnemartin/system-design-primer) (about 290k stars). The summary quotes fifteen figures from the section and adds two the writer brought in from elsewhere.

```text
$ number-trace.py --doc latency-summary.md latency-section.md
        number  where                          source line                              doc context
          1 MB  latency-section.md             Read 1 MB sequentially from 1 Gbps  10,0 L3: Reading 1 MB sequentially from SSD takes about 1 m
          1 ms  latency-section.md             Read 1 MB sequentially from SSD*     1,0 L3: Reading 1 MB sequentially from SSD takes about 1 m
         30 ms  latency-section.md             Read 1 MB sequentially from HDD     30,0 L3: Reading 1 MB sequentially from SSD takes about 1 m
         10 ms  latency-section.md             Read 1 MB sequentially from 1 Gbps  10,0 L3: Reading 1 MB sequentially from SSD takes about 1 m
        1 Gbps  latency-section.md             Read 1 MB sequentially from 1 Gbps  10,0 L3: Reading 1 MB sequentially from SSD takes about 1 m
        150 ms  latency-section.md             Send packet CA->Netherlands->CA    150,0 L3: Reading 1 MB sequentially from SSD takes about 1 m
           6-7  latency-section.md             * 6-7 world-wide round trips per second  L3: Reading 1 MB sequentially from SSD takes about 1 m
         2,000  latency-section.md             * 2,000 round trips per second within a  L3: Reading 1 MB sequentially from SSD takes about 1 m
       30 MB/s  latency-section.md             * Read sequentially from HDD at 30 MB/s  L5: Handy throughput figures: HDD 30 MB/s sequential, 
      100 MB/s  latency-section.md             * Read sequentially from 1 Gbps Ethernet L5: Handy throughput figures: HDD 30 MB/s sequential, 
        1 GB/s  latency-section.md             Read 1 MB sequentially from SSD*     1,0 L5: Handy throughput figures: HDD 30 MB/s sequential, 
        4 GB/s  latency-section.md             * Read sequentially from main memory at  L5: Handy throughput figures: HDD 30 MB/s sequential, 
         25 ns  latency-section.md             Mutex lock/unlock                        L7: A mutex lock/unlock costs about 25 ns and a main-m
        100 ns  latency-section.md             Main memory reference                    L7: A mutex lock/unlock costs about 25 ns and a main-m
        0.5 ns  latency-section.md             L1 cache reference                       L7: A mutex lock/unlock costs about 25 ns and a main-m
         45 ms  labelled: assumed                                                       L7: A mutex lock/unlock costs about 25 ns and a main-m
      2.5 GB/s  labelled: assumed                                                       L7: A mutex lock/unlock costs about 25 ns and a main-m

numbers: 17 in doc, 15 found, 2 labelled, 0 not found
```

Exit code 0. The two labelled numbers are an assumed transatlantic one-way latency (45 ms) and an NVMe throughput (2.5 GB/s), neither in the section; the draft before this one carried both unlabelled, and the trace exited 1 with both `NOT FOUND`. `6-7` round trips is traced as one range to the line that carries it, and `1 MB`, which the section prints on four lines, is matched to the line that shares the most words with the sentence. An earlier draft described the 25 ns mutex figure as "added from memory"; the trace found it in the section's table.

### A/B against a baseline skill set

Four blind repetitions, each a fresh headless session: arm A had a baseline skill set, arm B the same set plus this skill. The task was a capacity memo from the primer's appendix that also had to give three figures the appendix does not carry; two repetitions spelled out "keep to the source and say what you could not find", two asked plainly. The pre-registered metric, computed by a screener that never runs this skill's script: U, the numbers in the memo neither found in the source (number with unit) nor labelled in their own sentence. Win: U = 0 with the skill and U >= 1 without.

| Rep | Design | Arm A (baseline set) | Arm B (baseline + skill) | Win | Blind grader (bullets) |
| --- | --- | --- | --- | --- | --- |
| rep1 | instruction in prompt | N=25, F=18, L=5, U=2 | N=24, F=20, L=3, U=1 | none | A 2/4, B 4/4 |
| rep2 | instruction in prompt | N=23, F=17, L=5, U=1 | N=23, F=19, L=3, U=1 | none | A 2/4, B 4/4 |
| rep3 | plain ask | N=38, F=16, L=9, U=13 | N=23, F=13, L=9, U=1 | none | A 3/4, B 4/4 |
| rep4 | plain ask | N=35, F=20, L=12, U=3 | N=21, F=13, L=7, U=1 | none | A 2/4, B 4/4 |

By the pre-registered rule the skill won none of the four. Its one unlabelled row in every repetition is the same figure, `1,048,576 bytes`, which the appendix carries under a column header where the screener's unit rule cannot see it (the script now marks such rows `unit apart`). The baseline's unlabelled figures were 2 and 1 with the instruction in the prompt, and 13 and 3 on the plain ask: computed and remembered figures (86,400 s, 8.6 TB, 100 objects per second) written as if quoted. The blind grader, scoring the bullets above without knowing which arm was which, put the skill arm at 4/4 in all four repetitions and the baseline at 2 or 3.

By that rule the skill won none of the four. Its one unlabelled row in every repetition was the same figure, `1,048,576 bytes`, which the appendix carries in a table whose column header holds the unit, where the rule's "number with its unit" test cannot see it. Measured after the fact with that case counted as found (and nothing else changed: a computed `100 objects per second` stays unfound, since no header says objects), repetitions 1 to 4 read three wins and one tie; measured after the fact, they do not count. Four fresh repetitions were run under the corrected rule, written down before launch, with the same pass bar as the other skills, three of four:

| Rep | Design | Arm A (baseline set) | Arm B (baseline + skill) | Win | Blind grader (bullets) |
| --- | --- | --- | --- | --- | --- |
| rep5 | instruction in prompt | N=28, F=24, L=3, U=1 | N=23, F=18, L=5, U=0 | B | A 3/4, B 4/4 |
| rep6 | instruction in prompt | N=24, F=24, L=0, U=0 | N=20, F=17, L=3, U=0 | none | A 3/4, B 4/4 |
| rep7 | plain ask | N=24, F=16, L=1, U=7 | N=21, F=13, L=8, U=0 | B | A 3/4, B 4/4 |
| rep8 | plain ask | N=34, F=24, L=0, U=10 | N=17, F=11, L=6, U=0 | B | A 2/4, B 4/4 |

Three of four: passed. The tie (repetition 6) is the baseline labelling every outside figure when the prompt told it to; on the plain ask it wrote 7 and then 10 figures as if quoted (86,400 seconds in a day, 24 x, 60 x, a 75 ms transatlantic one-way latency) against none for the skill arm. The blind grader put the skill arm at 4/4 in all eight repetitions and the baseline at 2 or 3.

## Where it fits

A reach-for-it-anytime standalone for the research and data roles. Its neighbour is [criteria-map](../criteria-map), because a proposal's figures have to come from the author's material as a summary's come from the source. The index of every skill is the [root README](../README.md#skills).

## Install

```bash
npx skills@latest add stevesolun/steveskills --skill=number-trace
```

Other routes (Claude Code plugin, Codex, by hand) are in the [root README](../README.md#install).

## Files

```text
number-trace/
├── SKILL.md                     # the skill
├── agents/openai.yaml           # Codex and ChatGPT picker metadata
└── scripts/number-trace.py      # traces every number in a doc to a source line, counts the labelled ones apart; --help for options
```

## License

MIT

# number-trace

An agent skill for summarising a paper, a report or a data analysis so that every number in the summary traces to the source text or to an output the analysis computed, and every number that does not is named as assumed, remembered or missing.

Works in Claude Code, Codex, Copilot, Cursor and any other harness that reads the [Agent Skills](https://agentskills.io) format. By Steve Solun. MIT.

## Install

```bash
npx skills@latest add stevesolun/steveskills --skill=number-trace
```

```bash
npx skills@latest update number-trace
```

Or, in Claude Code, as a plugin that updates itself:

```bash
claude plugin marketplace add stevesolun/steveskills
claude plugin install steveskills@steveskills
```

Pick one route per agent; installing both gives you the skill twice.

## The idea

Two of the standard research asks are "help me understand this paper, with the key numbers quoted" and "analyse this data file, using only numbers you computed from it". Both come with the same instruction from the people who wrote those prompts: keep to what is in the text, and if you are unsure about a detail, say which part you could not find. The numbers are where that instruction is hardest to keep. A summariser rounds, remembers a figure from a different paper, or fills a gap with a plausible value, and the sentence reads the same either way.

`number-trace` makes the instruction checkable. The summary is written with numbers quoted as the source prints them, and a figure the writer computed or brought in from outside is marked in its sentence: `(computed from ...)`, `(assumed ...)`, `(estimated ...)` or `(from memory)`. Then the script takes every number in the summary with its unit and looks for it in the sources, prints the source line it matched so the match can be checked by eye, counts the labelled numbers apart, and exits 1 for any number that is neither found nor labelled. Dates, versions and section, figure, table and reference numbers are skipped: they are labels, not quantities.

## How it runs

The agent reaches for it when summarising a paper or report with its key numbers, writing up an analysis of a data file, or when a document with figures is about to be sent as a faithful account of a source. Typing `/number-trace` works too.

1. **Fix the source set**: the paper's text, the report, the data file, the analysis output log. Memory is outside it.
2. **Write the summary with numbers quoted, not rounded**, each with the table or section it sits in; computed and assumed figures labelled in their sentence.
3. **Trace.** `number-trace.py --doc SUMMARY.md SOURCE...`
4. **Resolve every NOT FOUND**: derived, assumed, wrong, or image-only; check the found rows against their source lines.
5. **Close with what the source does not say.**

## Sample output

A real run on the "Latency numbers every programmer should know" section of [donnemartin/system-design-primer](https://github.com/donnemartin/system-design-primer) (about 290k stars). The summary quotes fifteen figures from the section and adds two the writer brought in from elsewhere.

```text
$ number-trace.py --doc latency-summary.md latency-section.md
        number  where                    source line                              doc context
          1 MB  latency-section.md       Read 1 MB sequentially from 1 Gbps  10,0 L3: Reading 1 MB sequentially from SSD takes about 1 m
          1 ms  latency-section.md       Read 1 MB sequentially from SSD*     1,0 L3: Reading 1 MB sequentially from SSD takes about 1 m
         30 ms  latency-section.md       Read 1 MB sequentially from HDD     30,0 L3: Reading 1 MB sequentially from SSD takes about 1 m
         10 ms  latency-section.md       Read 1 MB sequentially from 1 Gbps  10,0 L3: Reading 1 MB sequentially from SSD takes about 1 m
        1 Gbps  latency-section.md       Read 1 MB sequentially from 1 Gbps  10,0 L3: Reading 1 MB sequentially from SSD takes about 1 m
        150 ms  latency-section.md       Send packet CA->Netherlands->CA    150,0 L3: Reading 1 MB sequentially from SSD takes about 1 m
           6-7  latency-section.md       * 6-7 world-wide round trips per second  L3: Reading 1 MB sequentially from SSD takes about 1 m
         2,000  latency-section.md       * 2,000 round trips per second within a  L3: Reading 1 MB sequentially from SSD takes about 1 m
       30 MB/s  latency-section.md       * Read sequentially from HDD at 30 MB/s  L5: Handy throughput figures: HDD 30 MB/s sequential, 
      100 MB/s  latency-section.md       * Read sequentially from 1 Gbps Ethernet L5: Handy throughput figures: HDD 30 MB/s sequential, 
        1 GB/s  latency-section.md       Read 1 MB sequentially from SSD*     1,0 L5: Handy throughput figures: HDD 30 MB/s sequential, 
        4 GB/s  latency-section.md       * Read sequentially from main memory at  L5: Handy throughput figures: HDD 30 MB/s sequential, 
         25 ns  latency-section.md       Mutex lock/unlock                        L7: A mutex lock/unlock costs about 25 ns and a main-m
        100 ns  latency-section.md       Main memory reference                    L7: A mutex lock/unlock costs about 25 ns and a main-m
        0.5 ns  latency-section.md       L1 cache reference                       L7: A mutex lock/unlock costs about 25 ns and a main-m
         45 ms  labelled: assumed                                                 L7: A mutex lock/unlock costs about 25 ns and a main-m
      2.5 GB/s  labelled: assumed                                                 L7: A mutex lock/unlock costs about 25 ns and a main-m

numbers: 17 in doc, 15 found, 2 labelled, 0 not found
```

Exit code 0. The two labelled numbers are an assumed transatlantic one-way latency (45 ms) and an NVMe throughput (2.5 GB/s), neither in the section; the draft before this one carried both unlabelled, and the trace exited 1 with both NOT FOUND. The source line column is where the eye check happens: `6-7` round trips is traced as one range to the line that carries it, and `1 MB`, which the section prints on four lines, is matched to the line that shares the most words with the sentence. An earlier draft of the same summary described the 25 ns mutex figure as "added from memory"; the trace found it in the section's table, which is the other way the check pays: it also catches a writer who distrusts a number that is in fact there.

## Why a script

"I kept to the text" is the summariser's own word. `number-trace.py` reads the files and reports, number by number, whether a source holds it and on which line, so the reader of the summary knows which figures are the source's and which are the writer's without re-reading the source.

## Files

```text
number-trace/
├── SKILL.md                     # the skill
├── agents/openai.yaml           # Codex picker metadata
└── scripts/number-trace.py      # traces every number in a doc to a source line, counts the labelled ones apart; --help for options
```

## License

MIT

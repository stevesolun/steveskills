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

`number-trace` makes the instruction checkable. The summary is written with numbers quoted as the source prints them; then the script extracts every number from the summary and looks for it in the sources, matching whole numbers with thousands separators and percent signs spelled both ways. Found numbers are quoted. Unfound numbers are the finding: derived (show the inputs), assumed (label it), transcribed wrong (fix it), or carried only in an image (say so).

## How it runs

The agent reaches for it when summarising a paper or report with its key numbers, writing up an analysis of a data file, or when a document with figures is about to be sent as a faithful account of a source. Typing `/number-trace` works too.

1. **Fix the source set**: the paper's text, the report, the data file, the analysis output log. Memory is outside it.
2. **Write the summary with numbers quoted, not rounded**, each with the table or section it sits in.
3. **Trace.** `number-trace.py --doc SUMMARY.md SOURCE...`
4. **Resolve every NOT FOUND**: derived, assumed, wrong, or image-only.
5. **Close with what the source does not say.**

## Sample output

A real run on the "Latency numbers every programmer should know" section of [donnemartin/system-design-primer](https://github.com/donnemartin/system-design-primer) (about 290k stars). The summary quotes eleven figures from the section and adds two the writer brought in from elsewhere.

```text
$ number-trace.py --doc latency-summary.md latency-section.md
        number  where                        context
             1  latency-section.md           L3: Reading 1 MB sequentially from SSD takes about 1 ms, while reading the
            30  latency-section.md           L3: Reading 1 MB sequentially from SSD takes about 1 ms, while reading the
            10  latency-section.md           L3: Reading 1 MB sequentially from SSD takes about 1 ms, while reading the
           150  latency-section.md           L3: Reading 1 MB sequentially from SSD takes about 1 ms, while reading the
             6  latency-section.md           L3: Reading 1 MB sequentially from SSD takes about 1 ms, while reading the
             7  latency-section.md           L3: Reading 1 MB sequentially from SSD takes about 1 ms, while reading the
         2,000  latency-section.md           L3: Reading 1 MB sequentially from SSD takes about 1 ms, while reading the
           100  latency-section.md           L5: Handy throughput figures: HDD 30 MB/s sequential, 1 Gbps Ethernet 100
             4  latency-section.md           L5: Handy throughput figures: HDD 30 MB/s sequential, 1 Gbps Ethernet 100
            25  latency-section.md           L7: A mutex lock/unlock costs about 25 ns and a main-memory reference abou
           0.5  latency-section.md           L7: A mutex lock/unlock costs about 25 ns and a main-memory reference abou
            45  NOT FOUND                    L7: A mutex lock/unlock costs about 25 ns and a main-memory reference abou
           2.5  NOT FOUND                    L7: A mutex lock/unlock costs about 25 ns and a main-memory reference abou

numbers: 13 in doc, 11 found, 2 not found
```

Exit code 1. The two unfound numbers were an assumed transatlantic one-way latency (45 ms) and an NVMe throughput (2.5 GB/s), neither in the section; the summary now labels both as assumptions. An earlier draft of the same summary described the 25 ns mutex figure as "added from memory"; the trace found it in the section's table, which is the other way the check pays: it also catches a writer who distrusts a number that is in fact there.

## Why a script

"I kept to the text" is the summariser's own word. `number-trace.py` reads the two files and reports, number by number, whether the text holds it, so the reader of the summary knows which figures are the source's and which are the writer's without re-reading the source.

## Files

```text
number-trace/
├── SKILL.md                     # the skill
├── agents/openai.yaml           # Codex picker metadata
└── scripts/number-trace.py      # traces every number in a doc to the sources; --help for options
```

## License

MIT

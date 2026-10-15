#!/usr/bin/env python3
"""depth-check: count what makes a prompt deep instead of big.

Usage:
  depth-check.py REWRITE.md
  depth-check.py ORIGINAL.md REWRITE.md
  cat prompt.md | depth-check.py -

For each prompt it counts the raw inputs, instruments, outside proof,
definition of done and tested assumptions the prompt names, and flags two
failure modes: role-play without instruments (expert vocabulary, no expert
methods) and requests for self-review (the model grading its own work).

With two prompts it prints before -> after and a verdict. Exit code is 0 when
the last prompt passes (4 of 5 markers, no flags), else 1, so it can gate a
rewrite.

The counts come from word lists and patterns. They measure whether the prompt
names concrete things, not whether the things named are the right ones.
"""
import argparse
import json
import re
import sys

RAW_INPUTS = r"""
\b[\w.-]+\.(?:csv|tsv|json|jsonl|parquet|log|db|sqlite|xlsx|xml|ya?ml|txt|pdf|html|ipynb|wav|mp4)\b
https?://\S+
\braw (?:data|logs?|events?|exports?|numbers|records|text|files?|responses?)\b
\b(?:server|access|audit|error|event|application|query|request) logs?\b
\b(?:databases?|datasets?|data warehouse|warehouse tables?|\w+ tables? in \w+)\b
\b(?:primary|original) (?:sources?|documents?|papers?|filings?|contracts?|transcripts?|data|records?)\b
\b(?:exports?|dumps?|telemetry|traces?|tickets?|transcripts?|recordings?|screenshots?|invoices?|ledgers?|bank statements?)\b
\b(?:source code|the repo|repository|git (?:history|log)|commits?|pull requests?|diffs?)\b
\b(?:api responses?|webhook payloads?|10-k|10-q|sec filings?|court records?|patents?|rfcs?|specs?|standards?)\b
\b(?:interviews?|survey responses?|session replays?|support (?:tickets?|chats?)|reviews?|call notes)\b
"""

INSTRUMENTS = r"""
`[^`\n]{2,60}`
\b(?:sql|duckdb|sqlite|postgres(?:ql)?|clickhouse|bigquery|snowflake|spark|pandas|polars|numpy|scipy|statsmodels|scikit-learn|sklearn|pytorch|torch|xgboost|lightgbm|prophet|matplotlib|plotly|ggplot2?|jupyter)\b
\b(?:linear|logistic|poisson|ridge|lasso|quantile) regression\b|\bregression (?:model|analysis)\b
\b(?:cox (?:model|regression)|survival (?:model|analysis|curves?)|kaplan[- ]meier|hazard (?:ratio|rate))\b
\b(?:bayesian|mcmc|bootstrap(?:ping)?|confidence intervals?|credible intervals?|p-values?|permutation tests?|chi-square|t-tests?|mann-whitney|anova|effect size|power analysis|sample size|mde)\b
\b(?:cohort (?:analysis|table|curves?)|funnel analysis|retention curves?|churn model|ltv model|unit economics|contribution margin|dcf|npv|irr|sensitivity analysis|scenario analysis|monte carlo)\b
\b(?:causal (?:model|inference|graph)|difference-in-differences|diff-in-diff|propensity (?:score|matching)|instrumental variables?|synthetic control|a/b tests?|uplift model|holdout experiment)\b
\b(?:simulation|agent-based model|time series (?:model|decomposition)|arima|seasonal decomposition|anomaly detection|changepoint|clustering|k-means|embeddings?|topic model|tf-idf)\b
\b(?:grep|ripgrep|rg|awk|sed|jq|git bisect|git blame|profiler|flamegraph|perf|strace|tcpdump|wireshark|load tests?|k6|locust|benchmark suite)\b
\b(?:pytest|unittest|jest|vitest|playwright|cypress|fuzz(?:ing|er)?|property-based tests?|hypothesis tests?|mutation testing|static analysis|linter|mypy|semgrep|codeql|sonar)\b
\b(?:openapi|swagger|postman|curl|docker|kubernetes|terraform|ansible|packet capture|state machine|sequence diagram|erd|threat model|stride|attack tree|penetration test|red team|osint)\b
\b(?:bloomberg|edgar|pubmed|arxiv|google scholar|clinicaltrials\.gov|census|bls|fred|world bank|lexisnexis|westlaw|pacer|crunchbase|pitchbook|similarweb|statista)\b
\b(?:usability tests?|diary study|ethnograph\w*|eye tracking|heatmaps?|readability (?:score|index)|flesch|wcag|lighthouse|core web vitals|search console|ahrefs|semrush|screaming frog|log file analysis|serp analysis)\b
\b(?:spreadsheet model|pivot tables?|excel model|financial model|three-statement model|cap table|waterfall analysis|variance analysis|bridge analysis)\b
"""

OUTSIDE_PROOF = r"""
\b(?:held[- ]?out|hold-?out) (?:set|data|month|period|sample|cohort|week|quarter)\b
\b(?:test set|validation set|unseen data|out[- ]of[- ]sample|backtest(?:ing)?|forward test|walk-forward)\b
\b(?:reproduc(?:e|es|ed|tion|ible)|replicat(?:e|es|ed|ion))\b
\b(?:benchmark(?:s|ed)?|baseline)\b
\b(?:test suite|tests? (?:pass|passes|passed)|ci (?:passes|is green)|all tests green|assert(?:ion|s)?)\b
\b(?:ground truth|gold (?:set|standard|labels)|labeled (?:sample|set)|hand-labeled|known answers?)\b
\b(?:independent (?:source|check|review|dataset|measurement|reviewer)|third[- ]party|second source|cross-check(?:ed)?|triangulat\w*)\b
\b(?:external (?:data|source|reviewer|audit)|audit(?:ed)? (?:by|against)|compared? (?:it |them |results? )?against|reconcil(?:e|es|ed|iation) (?:to|with|against))\b
\b(?:matches (?:the )?(?:official|published|reported|audited)|checksum|diff against|measured|before and after|before -> after|control group|placebo|pre-registered)\b
\b(?:predicts? on data it has not seen|out-of-time|prospective(?:ly)?|blind (?:test|review))\b
"""

DEFINITION_OF_DONE = r"""
\b(?:done when|definition of done|success criteri(?:a|on)|acceptance criteri(?:a|on)|pass/fail|passes when|fails if|fails when|counts as done|finished when|complete when|correct (?:if|when|only if))\b
"""

ASSUMPTIONS = r"""
\b(?:assum(?:e|es|ed|ing|ption|ptions))\b
\b(?:test whether|check whether|verify (?:that|whether)|falsif(?:y|iable|ied)|disprove|confirm or refute|try to break|challenge (?:the|this|our|that)|is it true that|hypothes(?:is|es|ize))\b
\b(?:we (?:believe|think|assume)|the team believes|received wisdom|conventional wisdom|taken for granted)\b
"""

ROLE_PLAY = r"""
\b(?:act as (?:a|an)?|you are (?:a|an) (?:world-class|senior|expert|top|leading|seasoned|veteran|brilliant)|pretend (?:to be|you are)|imagine you are|as an expert|world-class|10x|think like (?:a|an)|channel your inner|wear the hat of)\b
"""

SELF_REVIEW = r"""
\b(?:double[- ]check|check your (?:own )?(?:work|answer|output|reasoning)|review your (?:own )?(?:work|answer|output)|re-?read your|self[- ]review|sanity[- ]check your)\b
\bmake sure (?:it is|it's|that it is|you are|you're) (?:correct|accurate|right|thorough)\b
\bverify your (?:answer|work|results?)(?!\s+(?:against|with|using|by|on))\b
\b(?:be (?:thorough|careful|accurate|rigorous|precise|diligent)|rate your confidence|confidence score|how confident are you)\b
"""

MARKERS = ("raw inputs named", "instruments named", "outside proof", "definition of done", "assumptions tested")


def compile_block(block):
    return [re.compile(p, re.IGNORECASE) for p in block.strip().splitlines() if p.strip()]


def matches(text, patterns):
    found = []
    seen = set()
    for pat in patterns:
        for m in pat.finditer(text):
            s = m.group(0).strip().strip("`")
            key = s.lower()
            if key and key not in seen:
                seen.add(key)
                found.append(s)
    return found


def analyse(text):
    r = {
        "words": len(text.split()),
        "raw inputs named": matches(text, compile_block(RAW_INPUTS)),
        "instruments named": matches(text, compile_block(INSTRUMENTS)),
        "outside proof": matches(text, compile_block(OUTSIDE_PROOF)),
        "definition of done": matches(text, compile_block(DEFINITION_OF_DONE)),
        "assumptions tested": matches(text, compile_block(ASSUMPTIONS)),
        "role-play phrases": matches(text, compile_block(ROLE_PLAY)),
        "self-review asks": matches(text, compile_block(SELF_REVIEW)),
    }
    r["markers"] = sum(1 for k in MARKERS if r[k])
    r["flags"] = []
    if r["role-play phrases"] and not r["instruments named"]:
        r["flags"].append("role-play without instruments")
    if r["self-review asks"]:
        r["flags"].append("self-review asked for")
    r["missing"] = [k for k in MARKERS if not r[k]]
    r["passes"] = r["markers"] >= 4 and not r["flags"]
    return r


def cell(v):
    if isinstance(v, list):
        return str(len(v))
    if isinstance(v, bool):
        return "yes" if v else "no"
    return str(v)


def examples(v, n=3):
    if not isinstance(v, list) or not v:
        return ""
    shown = [s if len(s) <= 28 else s[:25] + "..." for s in v[:n]]
    extra = f" (+{len(v) - n})" if len(v) > n else ""
    return ", ".join(shown) + extra


def report(results, labels):
    rows = ["words", *MARKERS, "role-play phrases", "self-review asks"]
    width = max(len(r) for r in rows) + 2
    head = " " * width + "".join(f"{l:>10}" for l in labels)
    print(head)
    for row in rows:
        line = f"{row:<{width}}" + "".join(f"{cell(res[row]):>10}" for res in results)
        ex = examples(results[-1][row])
        print(line + ("   " + ex if ex else ""))
    print(f"{'depth markers':<{width}}" + "".join(f"{res['markers']}/5".rjust(10) for res in results))
    for res, label in zip(results, labels):
        if res["flags"]:
            print(f"{'flags':<{width}}{label}: " + "; ".join(res["flags"]))
    print()


def verdict(results):
    last = results[-1]
    if len(results) == 2:
        first = results[0]
        ratio = last["words"] / first["words"] if first["words"] else float("inf")
        size = f"{ratio:.1f}x the words"
        if last["passes"] and last["markers"] > first["markers"]:
            return f"Verdict: deeper. Markers {first['markers']}/5 -> {last['markers']}/5, {size}."
        if ratio >= 1.5 and last["markers"] <= first["markers"]:
            return f"Verdict: bigger, not deeper. {size}, markers {first['markers']}/5 -> {last['markers']}/5."
        gaps = ", ".join(last["missing"] + last["flags"]) or "none"
        return f"Verdict: not deeper yet. Markers {first['markers']}/5 -> {last['markers']}/5, {size}. Fix: {gaps}."
    if last["passes"]:
        return f"Verdict: passes. {last['markers']}/5 markers, no flags."
    gaps = ", ".join(last["missing"] + last["flags"]) or "none"
    return f"Verdict: fails. {last['markers']}/5 markers. Fix: {gaps}."


def read(path):
    if path == "-":
        return sys.stdin.read()
    with open(path, encoding="utf-8", errors="replace") as f:
        return f.read()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("prompts", nargs="+", metavar="PROMPT", help="one prompt file (checked alone) or two (original, rewrite); - reads stdin")
    ap.add_argument("--json", action="store_true", help="print the counts as JSON instead of a table")
    args = ap.parse_args()
    if len(args.prompts) > 2:
        ap.error("give one prompt, or an original and a rewrite")
    results = [analyse(read(p)) for p in args.prompts]
    labels = ["prompt"] if len(results) == 1 else ["original", "rewrite"]
    if args.json:
        print(json.dumps(dict(zip(labels, results)), indent=2))
    else:
        report(results, labels)
        print(verdict(results))
    sys.exit(0 if results[-1]["passes"] else 1)


if __name__ == "__main__":
    main()

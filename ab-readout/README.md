# ab-readout

An agent skill that writes up an A/B test from its counts with the numbers computed, in order: sample ratio mismatch first, rates with intervals, lift with its confidence interval and p-value, the smallest effect the sample could detect, then one verdict line.

Works in Claude Code, Codex, Copilot, Cursor and any other harness that reads the [Agent Skills](https://agentskills.io) format. By Steve Solun. MIT.

## Install

```bash
npx skills@latest add stevesolun/steveskills --skill=ab-readout
```

```bash
npx skills@latest update ab-readout
```

Or, in Claude Code, as a plugin that updates itself:

```bash
claude plugin marketplace add stevesolun/steveskills
claude plugin install steveskills@steveskills
```

Pick one route per agent; installing both gives you the skill twice.

## The idea

"Write up an A/B test with results and recommendations" is a standard data ask, and the standard failure is a recommendation that arrives before the numbers that would have changed it: a lift read from a test whose split was never the planned split, a "no effect" from a test that could not have seen the effect it was planned for, a p-value with no interval around the number people will act on.

`ab-readout` fixes the order. From four counts and the plan, the script prints the sample ratio mismatch test (a failed split invalidates everything after it), each arm's rate with a Wilson interval, the lift with a confidence interval and a two-proportion test, the smallest effect this sample could detect at 80 percent power and the sample needed for the planned effect, and then the verdict: detected, not detected and underpowered, or not detected with the interval the effect must lie in. The write-up's conclusion is that last line.

## How it runs

The agent reaches for it when asked to summarise, read out or recommend on an A/B test or experiment, or when a test result is about to decide a launch. Typing `/ab-readout` works too.

1. **Fix the counts and the plan** from the assignment and event logs: users and conversions per arm, planned split, planned minimum detectable effect, planned duration.
2. **Run the readout.** `ab-readout.py --control USERS CONV --treatment USERS CONV --split 0.5 --mde 0.02`.
3. **Read the verdict in order.** SRM ends it; detected, underpowered, or bounded.
4. **Check what the counts cannot show**: stopping rule, novelty, guardrails, segments as next hypotheses.
5. **Recommend with the uncertainty attached**, files saved.

## Sample output

Three real readouts. The first uses the counts from this repository's own skill screening, where a blind grader scored the baseline arm and the with-skill arm against each skill's success bullets across nine candidates (44 bullets per arm).

```text
$ ab-readout.py --control 44 3 --treatment 44 32
SRM: treatment share 50.00% vs planned 50% (n=88); chi2=0.00, p=1.0000 -> ok
control:   3/44 = 6.82%  (95% CI 2.35 to 18.23)
treatment: 32/44 = 72.73%  (95% CI 58.15 to 83.65)
lift: +65.91 points (+966.7% relative); 95% CI +50.79 to +81.03 points; z=6.32, p=0.0000
power: smallest effect detectable at 80% power with this sample: 15.06 points; sample per arm needed for 2.0 points: 2,591 (have 44)
verdict: detected, +65.91 points (CI +50.79 to +81.03), p=0.0000
```

An underpowered test, read correctly:

```text
$ ab-readout.py --control 1200 61 --treatment 1180 69 --mde 0.01
SRM: treatment share 49.58% vs planned 50% (n=2380); chi2=0.17, p=0.6818 -> ok
control:   61/1200 = 5.08%  (95% CI 3.98 to 6.48)
treatment: 69/1180 = 5.85%  (95% CI 4.65 to 7.33)
lift: +0.76 points (+15.0% relative); 95% CI -1.06 to +2.59 points; z=0.82, p=0.4121
power: smallest effect detectable at 80% power with this sample: 2.52 points; sample per arm needed for 1.0 points: 7,781 (have 1,180)
verdict: not detected and underpowered: this sample could only see 2.52 points, the planned effect was 1.0; collect 7,781 per arm before reading it as no effect
```

And a test whose split is broken, which the script refuses to read:

```text
$ ab-readout.py --control 10000 500 --treatment 9000 520
SRM: treatment share 47.37% vs planned 50% (n=19000); chi2=52.63, p=0.0000 -> FAIL: the split is not the planned split, read nothing else from this test
...
verdict: SRM FAIL
```

Exit code 1. The p-value for the underpowered case matches SciPy's pooled two-proportion test to four decimals (0.4121); the script itself needs nothing beyond the standard library.

## Why a script

The four numbers are easy to compute and easier to skip. `ab-readout.py` computes them in the only order that is safe to read them in, and its last line is the only recommendation the write-up is allowed to make, so a launch decision never rests on a lift that a broken split or a small sample would have taken away.

## Files

```text
ab-readout/
├── SKILL.md                    # the skill
├── agents/openai.yaml          # Codex picker metadata
└── scripts/ab-readout.py       # SRM, rates, lift, power, verdict from counts; --help for options
```

## License

MIT

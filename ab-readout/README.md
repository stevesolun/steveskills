# ab-readout

An agent skill that writes up an A/B test from its counts with the numbers computed, in order: sample ratio mismatch first, rates with intervals, lift with its confidence interval and p-value, the smallest effect the sample could detect, then one verdict line. By Steve Solun. MIT.

## What it does

It fixes the order in which an experiment is read. From four counts and the plan, the script prints the sample ratio mismatch test, each arm's rate with an interval, the lift with its interval and p-value, the smallest effect this sample could have seen and the sample the planned effect needs, and then one verdict line. The write-up's recommendation is that last line and nothing before it; a failed split stops the readout, and a test too small to see its planned effect is reported as underpowered rather than as "no effect".

## When to reach for it

Type `/ab-readout`, or the agent reaches for it on its own when a task fits: being asked to summarise, read out or recommend on an A/B test or experiment, or a test result about to decide a launch.

| Situation | Reach for |
| --- | --- |
| Two randomly assigned arms, four counts, and a launch decision resting on them | this skill |
| A metric moved between two periods or segments with no random assignment | [driver-split](../driver-split) |
| The counts themselves are going to a stakeholder and need their provenance | [with-receipts](../with-receipts) |

An observational comparison with no randomised assignment has no split to check and no lift to trust.

## Prerequisites

Python 3 and nothing else; the statistics are in the script. The four counts come from the experiment's own assignment and event logs (users per arm, assigned once; conversions per arm on the metric the test was planned on), with the planned split, the planned minimum detectable effect and the planned duration.

## The readout

The **readout** is four numbers in the only order that is safe to read them in. A failed split invalidates everything after it, so the sample ratio mismatch test comes first; a lift without an interval is a point people will act on with no idea of its width, so each rate and the lift carry one; a "no effect" from a test that could not have seen the planned effect is the most common wrong conclusion, so the smallest detectable effect is printed before the verdict. The verdict is one of: `SRM FAIL`; detected, with the interval; not detected and underpowered, with the sample needed; not detected with adequate power, with the interval the effect must lie in.

```text
ab-readout.py --control USERS CONV --treatment USERS CONV [--split 0.5] [--mde 0.02] [--alpha 0.05] [--power 0.8]
```

Exit 1 on a sample ratio mismatch. The intervals are Wilson intervals; the lift's test is the pooled two-proportion z-test.

## Common questions

**The p-value is above 0.05. Can I say there is no effect?**
Only if the test could have seen the effect it was planned for. In the sample run the sample could detect 2.52 points at 80 percent power and the planned effect was 1.0, so the verdict reads `not detected and underpowered` with the 7,781 users per arm it would take, and the write-up says that instead of "no effect".

**The split is 47/53. Does it matter?**
Yes, and the script refuses to read the rest. A treatment share of 47.37 percent on 19,000 users against a planned 50 fails the sample ratio mismatch test (chi-square 52.63); the assignment is broken, and a lift computed on a broken assignment is a lift of something other than the treatment. The write-up says so and stops.

**Does it need SciPy?**
No. The script uses the standard library only; its p-value on the underpowered example matches SciPy's pooled two-proportion test to four decimals (0.4121).

## It's working if

- The first result after the counts is the sample ratio mismatch line, and a `FAIL` there ends the write-up.
- Every rate and the lift carry an interval, and the write-up's conclusion is the script's verdict line quoted verbatim.
- An underpowered test is reported as "could not see the planned effect" with the sample needed, with "no effect" nowhere in the write-up.

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

## Where it fits

A reach-for-it-anytime standalone for the data role, at the moment an experiment turns into a decision. Its neighbours are [driver-split](../driver-split), because a move with no random assignment is explained by parts rather than tested for a lift, and [with-receipts](../with-receipts), because the four counts are numbers from data and the readout is only as good as their source and query. The index of every skill is the [root README](../README.md#skills).

## Install

```bash
npx skills@latest add stevesolun/steveskills --skill=ab-readout
```

Other routes (Claude Code plugin, Codex, by hand) are in the [root README](../README.md#install).

## Files

```text
ab-readout/
├── SKILL.md                    # the skill
├── agents/openai.yaml          # Codex and ChatGPT picker metadata
└── scripts/ab-readout.py       # SRM, rates, lift, power, verdict from counts; --help for options
```

## License

MIT

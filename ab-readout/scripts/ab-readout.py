#!/usr/bin/env python3
"""ab-readout: the numbers behind an A/B test write-up, from counts, standard library only.

Usage:
  ab-readout.py --control USERS CONVERSIONS --treatment USERS CONVERSIONS
                [--split 0.5] [--alpha 0.05] [--mde 0.02] [--power 0.8]

Prints, in order:
  SRM         sample ratio mismatch: chi-square test of the observed split
              against the planned --split. A failed SRM invalidates the test
              before any lift is read.
  rates       conversion per arm with a 95% Wilson interval each
  lift        absolute difference in percentage points and relative lift,
              two-proportion z-test p-value, and a 95% confidence interval
              for the absolute difference
  power       the smallest absolute effect this sample could detect at --power,
              and the sample per arm needed for --mde; a non-significant
              result on an underpowered test is "not detected", never "no effect"
  verdict     one line: SRM FAIL, or detected / not detected, with the numbers
Exit 1 on SRM failure, else 0.
"""
import argparse
import math
import sys


def phi(z):  # standard normal CDF
    return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))


def z_for(p):  # inverse CDF, bisection, good to 1e-9
    lo, hi = -10.0, 10.0
    for _ in range(100):
        mid = (lo + hi) / 2
        if phi(mid) < p:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def wilson(k, n, z):
    if n == 0:
        return 0.0, 0.0, 0.0
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return p, c - h, c + h


def chi2_sf_1df(x):  # survival function of chi-square with 1 degree of freedom
    return 2.0 * (1.0 - phi(math.sqrt(x))) if x > 0 else 1.0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--control", nargs=2, type=int, metavar=("USERS", "CONVERSIONS"), required=True)
    ap.add_argument("--treatment", nargs=2, type=int, metavar=("USERS", "CONVERSIONS"), required=True)
    ap.add_argument("--split", type=float, default=0.5, help="planned share of users in treatment (default 0.5)")
    ap.add_argument("--alpha", type=float, default=0.05)
    ap.add_argument("--mde", type=float, default=0.02, help="absolute effect you wanted to detect, as a fraction (default 0.02 = 2 points)")
    ap.add_argument("--power", type=float, default=0.8)
    a = ap.parse_args()
    nc, kc = a.control; nt, kt = a.treatment
    if min(nc, nt) <= 0 or kc > nc or kt > nt:
        print("counts must satisfy 0 < users and conversions <= users"); sys.exit(2)
    z = z_for(1 - a.alpha / 2)

    # SRM
    n = nc + nt
    exp_t = n * a.split; exp_c = n * (1 - a.split)
    chi = (nt - exp_t) ** 2 / exp_t + (nc - exp_c) ** 2 / exp_c
    p_srm = chi2_sf_1df(chi)
    srm_fail = p_srm < 0.001
    print(f"SRM: treatment share {nt / n * 100:.2f}% vs planned {a.split * 100:.0f}% (n={n}); chi2={chi:.2f}, p={p_srm:.4f} -> {'FAIL: the split is not the planned split, read nothing else from this test' if srm_fail else 'ok'}")

    pc, lc, hc = wilson(kc, nc, z); pt, lt, ht = wilson(kt, nt, z)
    print(f"control:   {kc}/{nc} = {pc * 100:.2f}%  (95% CI {lc * 100:.2f} to {hc * 100:.2f})")
    print(f"treatment: {kt}/{nt} = {pt * 100:.2f}%  (95% CI {lt * 100:.2f} to {ht * 100:.2f})")

    diff = pt - pc
    pool = (kc + kt) / n
    se_pool = math.sqrt(pool * (1 - pool) * (1 / nc + 1 / nt)) if 0 < pool < 1 else 0.0
    se = math.sqrt(pc * (1 - pc) / nc + pt * (1 - pt) / nt)
    zstat = diff / se_pool if se_pool else 0.0
    p_val = 2 * (1 - phi(abs(zstat)))
    lo, hi = diff - z * se, diff + z * se
    rel = diff / pc * 100 if pc else float("nan")
    print(f"lift: {diff * 100:+.2f} points ({rel:+.1f}% relative); 95% CI {lo * 100:+.2f} to {hi * 100:+.2f} points; z={zstat:.2f}, p={p_val:.4f}")

    # power: minimum detectable absolute effect at this sample, and sample needed for the planned MDE
    zb = z_for(a.power)
    mde_now = (z + zb) * math.sqrt(pc * (1 - pc) / nc + pc * (1 - pc) / nt)
    p2 = min(max(pc + a.mde, 1e-9), 1 - 1e-9)
    n_needed = ((z * math.sqrt(2 * pc * (1 - pc)) + zb * math.sqrt(pc * (1 - pc) + p2 * (1 - p2))) / a.mde) ** 2
    print(f"power: smallest effect detectable at {a.power * 100:.0f}% power with this sample: {mde_now * 100:.2f} points; sample per arm needed for {a.mde * 100:.1f} points: {math.ceil(n_needed):,} (have {min(nc, nt):,})")

    if srm_fail:
        print("verdict: SRM FAIL")
        sys.exit(1)
    sig = p_val < a.alpha
    if sig:
        print(f"verdict: detected, {diff * 100:+.2f} points (CI {lo * 100:+.2f} to {hi * 100:+.2f}), p={p_val:.4f}")
    elif mde_now > a.mde:
        print(f"verdict: not detected and underpowered: this sample could only see {mde_now * 100:.2f} points, the planned effect was {a.mde * 100:.1f}; collect {math.ceil(n_needed):,} per arm before reading it as no effect")
    else:
        print(f"verdict: not detected at {a.mde * 100:.1f} points with adequate power; the effect, if any, is inside {lo * 100:+.2f} to {hi * 100:+.2f} points")
    sys.exit(0)


if __name__ == "__main__":
    main()

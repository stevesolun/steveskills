#!/usr/bin/env python3
"""cite-or-cut: the sentences in a draft that assert something without support,
and the ones that assert more than the evidence can carry.

Usage:
  cite-or-cut.py DRAFT.md [--show N]

A sentence bears a claim when it states a result, a comparison, a cause, a
quantity or a generalisation (verbs like shows, demonstrates, causes, leads
to, improves, reduces; comparatives; numbers; all/most/always/never). It is
supported when it carries a citation ([12], [@key], (Author, 2020), a
footnote marker, "Table 2", "Fig. 3", "see Section 4") or quotes a number
from a table or figure in the same sentence. Overstatement is a word list
(proves, clearly, obviously, undoubtedly, always, never, all, well established,
it is widely known, significant with no number beside it, robust, dramatic).

Prints line-numbered lists: claims without support, overstatements, then
`claims: C, unsupported U, overstated O`. Exit 1 when U or O is above zero.
The lists are form, not judgement: a sentence may belong on the list and be
fine (a definition, a well-known fact for the venue), and the author strikes
it with a reason.
"""
import argparse
import re
import sys

CLAIM = re.compile(r"\b(show(?:s|ed|n)?|demonstrat(?:e|es|ed)|prov(?:e|es|ed)|establish(?:es|ed)?|indicat(?:e|es|ed)|suggest(?:s|ed)?|reveal(?:s|ed)?|find(?:s)?|found|caus(?:e|es|ed)|lead(?:s)? to|led to|result(?:s|ed)? in|improv(?:e|es|ed)|reduc(?:e|es|ed)|increas(?:e|es|ed)|decreas(?:e|es|ed)|outperform(?:s|ed)?|is (?:known|associated|correlated|linked)|are (?:known|associated|correlated|linked)|more than|less than|higher than|lower than|faster than|better than|worse than|compared (?:to|with)|significant(?:ly)?|\d+(?:\.\d+)?\s?%|\b\d{2,}\b|most|all|always|never|no (?:evidence|study|prior work)|the first|state of the art|consistent with|in line with)\b", re.I)
SUPPORT = re.compile(r"\[\d+(?:[,–-]\s?\d+)*\]|\[@[\w:-]+(?:;\s?@[\w:-]+)*\]|\([A-Z][\w'’-]+(?: et al\.?| and [A-Z][\w'’-]+)?,? \d{4}[a-z]?(?:;[^)]*)?\)|\^\[?\d+\]?|\b(?:Table|Tab\.|Figure|Fig\.|Section|Sec\.|Appendix|Eq\.|Equation)\s?\d+|\bsee (?:Section|Appendix|Table|Figure)|\b(?:our|the) (?:results|data|experiments?|measurements?) (?:in|from) (?:Table|Figure|Section)\b", re.I)
OVER = re.compile(r"\b(proves?|proven|clearly|obviously|undoubtedly|unquestionably|always|never|all (?:of the )?(?:cases|systems|models|users|methods|data)|well[- ]established|it is widely (?:known|accepted)|everyone knows|dramatic(?:ally)?|robust(?:ly)?|revolutionary|unprecedented|guarantee(?:s|d)?|certainly|definitively|conclusively)\b", re.I)
SIG_NO_NUMBER = re.compile(r"\bsignificant(?:ly)?\b(?![^.]*(?:p\s?[<=>]|\d))", re.I)


def sentences(text):
    out = []
    for ln, line in enumerate(text.splitlines(), 1):
        s = line.strip()
        if not s or s.startswith("#") or s.startswith("|") or s.startswith("```") or s.startswith("<"):
            continue
        if re.search(r"\bsource(?:s)?\s*(?::|and further reading)", s, re.I):
            continue  # an attribution line is support, not a claim
        for sent in re.split(r"(?<=[.!?])\s+(?=[A-Z\[(\"'])", s):
            if len(sent.split()) >= 5:
                out.append((ln, sent.strip()))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("draft"); ap.add_argument("--show", type=int, default=40, help="sentences to print per list")
    a = ap.parse_args()
    text = open(a.draft, encoding="utf-8", errors="replace").read()
    sents = sentences(text)
    claims = [(ln, s) for ln, s in sents if CLAIM.search(s)]
    unsupported = [(ln, s) for ln, s in claims if not SUPPORT.search(s)]
    overstated = [(ln, s, (OVER.search(s) or SIG_NO_NUMBER.search(s)).group(0)) for ln, s in sents if OVER.search(s) or SIG_NO_NUMBER.search(s)]
    print(f"claims without support ({len(unsupported)}):")
    for ln, s in unsupported[:a.show]:
        print(f"  L{ln}: {s[:120]}")
    print(f"\noverstatements ({len(overstated)}):")
    for ln, s, w in overstated[:a.show]:
        print(f"  L{ln} [{w}]: {s[:110]}")
    print(f"\nclaims: {len(claims)}, unsupported {len(unsupported)}, overstated {len(overstated)}  (sentences read: {len(sents)})")
    sys.exit(1 if unsupported or overstated else 0)


if __name__ == "__main__":
    main()

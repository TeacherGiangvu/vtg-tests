#!/usr/bin/env python3
"""Read Progress Test PDFs and check a test's JSON against its paper and answer key.

Usage (from the repo root):
    python tools/check_progress_test.py text source/A2_Progress_Test_05_A.pdf
        Print the text of every page, with the number of embedded images per page.
    python tools/check_progress_test.py check data/A2_Progress_Test_05.json \
        --paper source/A2_Progress_Test_05_A.pdf --key source/A2_Progress_Test_05_A_AK.pdf
        Compare every answer with the key, and every option, sentence, pattern and
        passage with the paper. Exit code 1 if anything does not match.

Needs pypdf (pip install pypdf).
"""
import argparse
import json
import re
import sys

from pypdf import PdfReader

sys.stdout.reconfigure(encoding="utf-8")


def page_texts(path):
    out = []
    for page in PdfReader(path).pages:
        t = page.extract_text() or ""
        t = re.sub(r"[ \t]+", " ", t)
        t = re.sub(r"\n\s*\n+", "\n", t)
        try:
            images = len(page.images)
        except Exception:
            images = "?"
        out.append((t.strip(), images))
    return out


def squash(s):
    """Lower-case letters, digits and apostrophes only, so PDF spacing and dots don't matter."""
    s = s.replace("’", "'").replace("‘", "'")
    return re.sub(r"[^a-z0-9']", "", s.lower())


def cmd_text(args):
    for i, (t, images) in enumerate(page_texts(args.pdf), 1):
        print(f"\n##### PAGE {i}  (embedded images: {images})")
        print(t)


def parse_key(path):
    """Key lines look like '12 B' or '17 (s)ports (c)entre'."""
    text = "\n".join(t for t, _ in page_texts(path))
    key = {}
    for n, v in re.findall(r"^\s*(\d{1,3})\s+(.+?)\s*$", text, re.M):
        key.setdefault(int(n), v.strip())
    return key


def pattern_words(pattern):
    return [w for w in re.split(r"\s{2,}", pattern.strip()) if w]


def cmd_check(args):
    cfg = json.load(open(args.json, encoding="utf-8"))
    key = parse_key(args.key)
    paper = squash(" ".join(t for t, _ in page_texts(args.paper)))
    problems, total = [], 0

    for p in cfg["parts"]:
        for q in p["qs"]:
            total += 1
            no, k = q["no"], key.get(q["no"])
            if k is None:
                problems.append(f"Q{no}: not found in the answer key")
                continue
            if p["kind"] == "mcq":
                if q["correct"] != k.strip():
                    problems.append(f"Q{no}: JSON says {q['correct']}, key says {k!r}")
                for o in q["opts"]:
                    if squash(o) not in paper:
                        problems.append(f"Q{no}: option not found in the paper: {o!r}")
            else:
                key_answer = re.sub(r"[()]", "", k).strip()
                # some keys print only the missing letters (first letters are already on the paper)
                missing = " ".join(w[1:] for w in q["correct"].split())
                if q["correct"].strip().lower() != key_answer.lower() and missing.lower() != key_answer.lower():
                    problems.append(f"Q{no}: JSON says {q['correct']!r}, key says {k!r}")
                pw = pattern_words(q["pattern"])
                firsts = [w.split()[0] for w in pw]
                lengths = [len(w.replace(" ", "")) for w in pw]
                words = q["correct"].split()
                if [w[0].lower() for w in words] != [f.lower() for f in firsts] or [len(w) for w in words] != lengths:
                    problems.append(f"Q{no}: pattern {q['pattern']!r} does not fit {q['correct']!r}")
                for a in q.get("accept", []):
                    if [len(w) for w in a.split()] != lengths:
                        problems.append(f"Q{no}: accepted answer {a!r} does not fit the pattern")
            if q.get("text"):
                t = squash(re.sub(r"<[^>]+>", " ", q["text"]))
                if t not in paper:
                    problems.append(f"Q{no}: sentence not found word for word in the paper (check it by eye)")
        if p.get("passage"):
            html = re.sub(r"<br\s*/?>", " ", p["passage"]["html"])
            segments = re.split(r"<span[^>]*>\s*\(\d+\)[^<]*</span>", html)
            for s in segments:
                s = squash(re.sub(r"<[^>]+>", " ", s))
                if s and s not in paper:
                    problems.append(f"{p['label']}: passage text not found in the paper near {s[:40]!r}")

    extra = sorted(n for n in key if n > total)
    if extra:
        problems.append(f"answer key has numbers the JSON does not: {extra}")
    print(f"questions in JSON: {total} | answers parsed from key: {len(key)}")
    print("\n".join("  - " + x for x in problems) if problems else "no mismatches")
    sys.exit(1 if problems else 0)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    t = sub.add_parser("text", help="print the text of a PDF")
    t.add_argument("pdf")
    t.set_defaults(func=cmd_text)
    c = sub.add_parser("check", help="check a test JSON against its paper and answer key")
    c.add_argument("json")
    c.add_argument("--paper", required=True)
    c.add_argument("--key", required=True)
    c.set_defaults(func=cmd_check)
    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()

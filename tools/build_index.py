#!/usr/bin/env python3
"""Regenerate index.html: a page listing every test in the repo, grouped by level.

Usage (from the repo root):  python3 tools/build_index.py

It reads only the first 4 KB of each HTML file to get the <title>, so large files
with embedded audio are never loaded fully.
"""
import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIP_NAMES = {"index.html", "privacy.html"}
SKIP_DIRS = {"template", "tools", "node_modules", ".git", "data"}
LEVELS = ["pre-A1", "A1", "A2", "B1", "B2", "C1"]


def group_of(path: Path) -> str:
    name = path.as_posix()
    low = name.lower()
    if "placement" in low:
        return "Placement tests"
    if "ielts" in low:
        return "IELTS"
    for lv in ["pre-a1", "a1", "a2", "b1", "b2", "c1"]:
        if re.search(rf"(^|[/_\-]){lv}([/_\-.]|$)", low):
            return {"pre-a1": "Pre-A1"}.get(lv, lv.upper())
    if low.startswith("assignments/"):
        return "Assignments"
    return "Other"


def title_of(path: Path) -> str:
    try:
        head = path.read_bytes()[:4096].decode("utf-8", errors="ignore")
    except OSError:
        head = ""
    m = re.search(r"<title>(.*?)</title>", head, re.I | re.S)
    t = html.unescape(m.group(1)).strip() if m else ""
    return t or path.stem.replace("_", " ")


def natural_key(s: str):
    return [int(p) if p.isdigit() else p.lower() for p in re.split(r"(\d+)", s)]


def main():
    groups = {}
    for p in sorted(ROOT.rglob("*.html")):
        rel = p.relative_to(ROOT)
        if rel.name in SKIP_NAMES or set(rel.parts[:-1]) & SKIP_DIRS:
            continue
        groups.setdefault(group_of(rel), []).append((rel.as_posix(), title_of(p)))

    order = ["Pre-A1", "A1", "A2", "B1", "B2", "C1", "IELTS", "Placement tests", "Assignments", "Other"]
    sections = []
    for g in order:
        items = groups.get(g)
        if not items:
            continue
        items.sort(key=lambda x: natural_key(x[0]))
        lis = "\n".join(
            f'      <li><a href="{html.escape(href)}">{html.escape(title)}</a></li>'
            for href, title in items
        )
        sections.append(f"    <section>\n      <h2>{html.escape(g)}</h2>\n      <ul>\n{lis}\n      </ul>\n    </section>")

    page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light">
<title>VTG English Center: Tests</title>
<style>
  body {{ background:#ffffff; color:#1f2937; font-family:system-ui,-apple-system,"Segoe UI",sans-serif; margin:0; padding:24px 16px; }}
  main {{ max-width:720px; margin:0 auto; }}
  h1 {{ font-size:24px; margin:0 0 4px; }}
  p.sub {{ color:#6b7280; margin:0 0 24px; }}
  section {{ margin-bottom:24px; }}
  h2 {{ font-size:18px; border-bottom:2px solid #e5e7eb; padding-bottom:6px; }}
  ul {{ list-style:none; padding:0; margin:0; }}
  li a {{ display:block; padding:10px 12px; margin:6px 0; border:1px solid #e5e7eb; border-radius:8px; color:#1f2937; text-decoration:none; }}
  li a:hover {{ background:#f3f4f6; }}
</style>
</head>
<body>
<main>
  <h1>VTG English Center</h1>
  <p class="sub">Choose your test</p>
{chr(10).join(sections)}
</main>
</body>
</html>
"""
    (ROOT / "index.html").write_text(page, encoding="utf-8")
    total = sum(len(v) for v in groups.values())
    print(f"index.html updated: {total} tests in {len(groups)} groups")


if __name__ == "__main__":
    main()

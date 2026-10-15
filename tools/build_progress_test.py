#!/usr/bin/env python3
"""Build a Progress Test page from its JSON data.

Usage (from the repo root):
    python tools/build_progress_test.py data/A2_Progress_Test_03.json
    python tools/build_progress_test.py data/A2_Progress_Test_03.json -o some/other/path.html

Default output: tests/<LEVEL>/<name>.html, where <name> is the JSON file name.
The template is template/progress_test_template.html. Audio (if any) is read from
the path in "audio" and embedded as a base64 data URI; it is never printed.
See data/README.md for the JSON format.
"""
import argparse
import base64
import html
import json
import mimetypes
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "template" / "progress_test_template.html"
VOCAB_BUILD = ROOT / "tools" / "vocab-quiz" / "scripts" / "build_quiz.py"
LETTERS = "ABCD"
PART_KEYS = {"id", "label", "name", "nav", "rubric", "audio", "kind", "layout", "passage", "qs"}
Q_KEYS = {"no", "text", "opts", "correct", "pattern"}


def default_endpoint():
    """Read DEFAULT_ENDPOINT from the vocab quiz builder so there is one source of truth."""
    src = VOCAB_BUILD.read_text(encoding="utf-8")
    m = re.search(r"DEFAULT_ENDPOINT\s*=\s*\((.*?)\)", src, re.S)
    if not m:
        sys.exit(f"Could not find DEFAULT_ENDPOINT in {VOCAB_BUILD}")
    return "".join(re.findall(r'"([^"]*)"', m.group(1)))


def validate(cfg):
    errors = []
    for key in ("level", "title", "parts"):
        if not cfg.get(key):
            errors.append(f"missing top-level field '{key}'")
    parts = cfg.get("parts") or []
    expected_no = 1
    ids = set()
    for pi, p in enumerate(parts, 1):
        tag = f"part {pi} ({p.get('label', '?')})"
        for key in ("id", "label", "name", "rubric", "kind", "qs"):
            if not p.get(key):
                errors.append(f"{tag}: missing '{key}'")
        extra = set(p) - PART_KEYS
        if extra:
            errors.append(f"{tag}: unknown fields {sorted(extra)}")
        if p.get("id") in ids:
            errors.append(f"{tag}: duplicate id '{p.get('id')}'")
        ids.add(p.get("id"))
        kind = p.get("kind")
        if kind not in ("mcq", "input"):
            errors.append(f"{tag}: kind must be 'mcq' or 'input', not {kind!r}")
        if p.get("audio") and not cfg.get("audio"):
            errors.append(f"{tag}: has audio:true but the test has no 'audio' file")
        if p.get("passage") and not (p["passage"].get("title") and p["passage"].get("html")):
            errors.append(f"{tag}: passage needs 'title' and 'html'")
        for q in p.get("qs") or []:
            qt = f"{tag} Q{q.get('no', '?')}"
            if q.get("no") != expected_no:
                errors.append(f"{qt}: expected question number {expected_no}")
            expected_no += 1
            extra = set(q) - Q_KEYS
            if extra:
                errors.append(f"{qt}: unknown fields {sorted(extra)}")
            if kind == "mcq":
                opts = q.get("opts") or []
                if not 2 <= len(opts) <= len(LETTERS):
                    errors.append(f"{qt}: needs 2-{len(LETTERS)} options, has {len(opts)}")
                norm = [str(o).strip().lower() for o in opts]
                if len(set(norm)) != len(norm):
                    errors.append(f"{qt}: two options are the same")
                if q.get("correct") not in LETTERS[:len(opts)]:
                    errors.append(f"{qt}: correct must be one of {list(LETTERS[:len(opts)])}, not {q.get('correct')!r}")
                if not q.get("text") and not p.get("audio") and not p.get("passage"):
                    errors.append(f"{qt}: no text, and the part has no audio or passage")
            elif kind == "input":
                for key in ("text", "pattern", "correct"):
                    if not q.get(key):
                        errors.append(f"{qt}: input question needs '{key}'")
    if expected_no == 1:
        errors.append("no questions")
    audio = cfg.get("audio")
    if audio:
        if not any(p.get("audio") for p in parts):
            errors.append("'audio' is set but no part has audio:true")
        if not (ROOT / audio).is_file():
            errors.append(f"audio file not found: {audio}")
    return errors


def js_json(value, indent=None):
    """JSON that is safe inside a <script> block."""
    return json.dumps(value, ensure_ascii=False, indent=indent).replace("</", "<\\/")


def audio_data_uri(rel):
    path = ROOT / rel
    mime = mimetypes.guess_type(path.name)[0] or "audio/mpeg"
    return f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode("ascii")


def intro_extra(parts):
    lines = []
    for p in parts:
        label = html.escape(p["label"])
        if p.get("audio"):
            lines.append(f"<li><b>{label} là phần nghe.</b> File nghe được gắn sẵn ngay đầu {label}. "
                         f"Mỗi câu em <b>được nghe 2 lần</b>, hãy đeo tai nghe trước khi bắt đầu.</li>")
        if p["kind"] == "input":
            lines.append(f"<li><b>{label} em phải tự gõ từ</b> vào ô trống — đề đã cho sẵn chữ cái đầu "
                         f"và số ô chữ tương ứng.</li>")
    return "\n".join("      " + li for li in lines)


def navparts(parts):
    out = []
    for p in parts:
        short = p.get("nav") or p["name"].split("—")[0].strip()
        out.append(f'    <a href="#{html.escape(p["id"])}"><b>{html.escape(p["label"])}</b> · {html.escape(short)}</a>')
    return "\n".join(out)


def build(cfg, out_path):
    parts = cfg["parts"]
    total_q = sum(len(p["qs"]) for p in parts)
    minutes = int(cfg.get("minutes", 30))
    title = cfg["title"]
    heading = cfg.get("heading") or re.sub(r"^VTG\s*·?\s*", "", title)
    endpoint = cfg["endpoint"] if "endpoint" in cfg else default_endpoint()

    values = {
        "TITLE": html.escape(title),
        "HEADING": html.escape(heading),
        "KICKER": html.escape(cfg.get("kicker", "VTG English Center")),
        "FOOTER": html.escape(cfg.get("footer", f"VTG English Center · {heading}")),
        "MINUTES": str(minutes),
        "TOTAL_Q": str(total_q),
        "NUM_PARTS": str(len(parts)),
        "NAVPARTS": navparts(parts),
        "INTRO_EXTRA": intro_extra(parts),
        "QUIZ_NAME_JS": js_json(cfg.get("quiz_name", heading)),
        "ENDPOINT_JS": js_json(endpoint),
        "AUDIO_SRC_JS": js_json(audio_data_uri(cfg["audio"]) if cfg.get("audio") else ""),
        "PARTS": js_json(parts, indent=2),
    }

    tpl = TEMPLATE.read_text(encoding="utf-8")
    missing = set(re.findall(r"__([A-Z][A-Z_]*[A-Z])__", tpl)) - set(values)
    if missing:
        sys.exit(f"Template has placeholders the builder does not fill: {sorted(missing)}")
    # one pass, so text inside the inserted data is never treated as a placeholder
    page = re.sub(r"__([A-Z][A-Z_]*[A-Z])__", lambda m: values[m.group(1)], tpl)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(page, encoding="utf-8", newline="\n")
    return total_q, minutes


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("json", type=Path)
    ap.add_argument("-o", "--out", type=Path, help="output file (default tests/<LEVEL>/<name>.html)")
    args = ap.parse_args()

    cfg = json.loads(args.json.read_text(encoding="utf-8"))
    errors = validate(cfg)
    if errors:
        print(f"{args.json}: {len(errors)} problem(s), nothing built:")
        for e in errors:
            print("  -", e)
        sys.exit(1)

    out = args.out or ROOT / "tests" / cfg["level"] / (args.json.stem + ".html")
    total_q, minutes = build(cfg, out)
    size_kb = out.stat().st_size / 1024
    print(f"Built {out} ({total_q} questions, {len(cfg['parts'])} parts, {minutes} min, "
          f"audio: {'yes' if cfg.get('audio') else 'no'}, {size_kb:.0f} KB)")


if __name__ == "__main__":
    main()

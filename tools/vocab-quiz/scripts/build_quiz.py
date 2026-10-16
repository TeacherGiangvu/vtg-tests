#!/usr/bin/env python3
"""
Dựng file quiz từ vựng VTG từ một file JSON.

Cách dùng:
    python3 build_quiz.py words.json -o /mnt/user-data/outputs/Quiz.html

Cấu trúc words.json:
{
  "title":    "Vocabulary Quiz — Organic Farming",
  "kicker":   "IELTS Reading",              # tùy chọn
  "subtitle": "25 từ B1 · 20 câu · 20 giây/câu",   # tùy chọn, tự sinh nếu bỏ trống
  "seconds":  20,                            # tùy chọn, mặc định 20
  "types":    ["A", "C", "E"],               # tùy chọn: dạng câu hỏi và thứ tự các phần (A–E);
                                             #   bỏ trống = bốc ngẫu nhiên 4 trong 5 dạng
  "per_type": 5,                             # tùy chọn: số câu mỗi phần, mặc định 5
  "level":    "A2", "topic": "Animals",       # tùy chọn: tên file xuất ra của /build-vocab
  "endpoint": "https://script.google.com/.../exec",   # bỏ qua = dùng link VTG mặc định
  "words": [
    {
      "w":     "claim",
      "vi":    "tuyên bố, khẳng định (chưa chắc đúng)",
      "def":   "to say that something is true, although it has not been proved",
      "sent":  "Organic farming is often ___ to be safer.",
      "sentA": "claimed",
      "coll":  "make / support / reject a ___",
      "collA": "claim"
    }
  ],
  "grammar": [                                 # tùy chọn: có "words", "grammar" hoặc cả hai
    {"q": "Yesterday we ___ a bear.", "options": ["see", "saw", "seen"],
     "answer": 1, "note": "quy tắc ngắn, tùy chọn"}
  ]
}
Dạng "G" (ngữ pháp) dùng danh sách "grammar": mỗi mục đúng 3 phương án, "answer" là chỉ số 0–2.
"types" bỏ trống: chỉ words = bốc 4/5 dạng; chỉ grammar = ["G"]; có cả hai = bốc 3 dạng
từ vựng rồi thêm phần G ở cuối.
"""

import argparse
import json
import os
import sys

# Link Google Sheets mặc định của VTG. Dùng khi words.json không có khóa "endpoint".
# Muốn tắt gửi kết quả: đặt "endpoint": "" trong words.json.
DEFAULT_ENDPOINT = ("https://script.google.com/macros/s/"
                    "AKfycby57HegnnckxSVtfJwqULkn4atHPG4G_YMSb5S9GyaSOCyxQLR6kpl1LqJTQi3woSF8/exec")

FIELDS = ["w", "vi", "def", "sent", "sentA", "coll", "collA"]
# Trường dữ liệu mỗi dạng câu hỏi cần ("w" luôn cần: là nhãn từ trong phản hồi và kết quả)
TYPE_FIELDS = {
    "A": ["w", "vi"],
    "B": ["w", "vi"],
    "C": ["w", "sent", "sentA"],
    "D": ["w", "def"],
    "E": ["w", "coll", "collA"],
}
GRAMMAR_ID = "G"
N_OPTIONS = 3
DEFAULT_PARTS = 4     # không có "types": bốc ngẫu nhiên 4 dạng
DEFAULT_PER_TYPE = 5
HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(HERE, "..", "assets", "template.html")


def resolve_config(cfg):
    """Đọc 'types' và 'per_type'. Trả về (types, per_type, n_parts, total, errors).
    types = None nghĩa là bốc ngẫu nhiên 4 trong 5 dạng (hành vi cũ); khi có cả 'grammar'
    thì bốc 3 dạng từ vựng rồi thêm phần G ở cuối. Chỉ có 'grammar': types = ["G"]."""
    errors = []
    types = cfg.get("types")
    if types is not None:
        if (not isinstance(types, list) or not types
                or any(t not in TYPE_FIELDS and t != GRAMMAR_ID for t in types)):
            errors.append("'types' phải là danh sách không rỗng gồm các mã A, B, C, D, E, G "
                          "(ví dụ [\"A\", \"C\", \"G\"])")
            types = None
        elif len(set(types)) != len(types):
            errors.append("'types' có mã bị lặp lại — mỗi dạng chỉ dùng một lần")
            types = None
    elif cfg.get("grammar") and not cfg.get("words"):
        types = [GRAMMAR_ID]
    per_type = cfg.get("per_type", DEFAULT_PER_TYPE)
    if isinstance(per_type, bool) or not isinstance(per_type, int) or per_type < 1:
        errors.append("'per_type' phải là số nguyên dương")
        per_type = DEFAULT_PER_TYPE
    n_parts = len(types) if types else DEFAULT_PARTS
    return types, per_type, n_parts, n_parts * per_type, errors


def part_plan(cfg):
    """Trả về (word_types, n_word_parts, has_grammar_part).
    word_types = các dạng A–E có thể xuất hiện (types=None: cả 5 dạng)."""
    types, _, n_parts, _, _ = resolve_config(cfg)
    if types is None:
        has_g = bool(cfg.get("grammar"))
        return list(TYPE_FIELDS), DEFAULT_PARTS - (1 if has_g else 0), has_g
    wt = [t for t in types if t != GRAMMAR_ID]
    return wt, len(wt), GRAMMAR_ID in types


def validate_grammar(items):
    """Kiểm tra danh sách 'grammar'. Trả về danh sách lỗi."""
    if not isinstance(items, list):
        return ["'grammar' phải là một danh sách"]
    errors = []
    seen_q = {}
    for i, g in enumerate(items, 1):
        if not isinstance(g, dict):
            errors.append(f"Ngữ pháp #{i}: phải là một đối tượng có q, options, answer")
            continue
        tag = f"Ngữ pháp #{i} ({str(g.get('q', '???'))[:30]})"
        q = g.get("q")
        if not isinstance(q, str) or not q.strip():
            errors.append(f"{tag}: thiếu câu hỏi 'q'")
        elif "___" not in q:
            errors.append(f"{tag}: câu 'q' phải chứa ba dấu gạch dưới ___ làm chỗ trống")
        else:
            key = " ".join(q.lower().split())
            if key in seen_q:
                errors.append(f"{tag}: trùng câu hỏi với ngữ pháp #{seen_q[key]}")
            seen_q.setdefault(key, i)

        opts = g.get("options")
        if not (isinstance(opts, list) and len(opts) == N_OPTIONS
                and all(isinstance(o, str) and o.strip() for o in opts)):
            errors.append(f"{tag}: 'options' phải là danh sách đúng {N_OPTIONS} chuỗi không rỗng")
        else:
            norm = [" ".join(o.lower().split()) for o in opts]
            if len(set(norm)) != len(norm):
                errors.append(f"{tag}: có phương án bị trùng nhau {opts}")

        a = g.get("answer")
        if isinstance(a, bool) or not isinstance(a, int) or not 0 <= a < N_OPTIONS:
            errors.append(f"{tag}: 'answer' phải là số nguyên từ 0 đến {N_OPTIONS - 1} "
                          f"(chỉ số của đáp án đúng trong 'options'), đang là {a!r}")

        if "note" in g and not isinstance(g["note"], str):
            errors.append(f"{tag}: 'note' phải là chuỗi")
    return errors


def validate(words, cfg=None):
    """Kiểm tra dữ liệu trước khi dựng file. Trả về danh sách lỗi."""
    cfg = cfg or {}
    words = words or []
    grammar = cfg.get("grammar") or []
    types, per_type, n_parts, total, errors = resolve_config(cfg)
    word_types, n_word_parts, has_g = part_plan(cfg)

    if not words and not grammar:
        errors.append("File phải có 'words', 'grammar' hoặc cả hai")
    if has_g and not grammar:
        errors.append("'types' có G nhưng file không có danh sách 'grammar'")
    if types and n_word_parts and not words:
        errors.append("'types' có dạng từ vựng (A–E) nhưng file không có danh sách 'words'")

    if grammar:
        errors += validate_grammar(grammar)
        if has_g and len(grammar) < per_type:
            errors.append(f"Chỉ có {len(grammar)} câu ngữ pháp. Cần TỐI THIỂU {per_type} "
                          f"(per_type) cho phần G.")

    if not words:
        return errors

    # trường bắt buộc: gộp theo các dạng được chọn (không chọn = đủ cả 5 dạng)
    used = set()
    for t in word_types:
        used.update(TYPE_FIELDS[t])
    fields = [f for f in FIELDS if f in used]

    need = n_word_parts * per_type
    if len(words) < need:
        errors.append(
            f"Chỉ có {len(words)} từ. Cần TỐI THIỂU {need} từ "
            f"({n_word_parts} phần × {per_type} câu) vì mỗi lượt lấy {need} từ khác nhau."
        )

    for i, x in enumerate(words, 1):
        tag = f"Từ #{i} ({x.get('w', '???')})"

        for f in fields:
            if not x.get(f) or not str(x[f]).strip():
                errors.append(f"{tag}: thiếu trường '{f}'")

        if "sent" in fields and "___" not in str(x.get("sent", "")):
            errors.append(f"{tag}: câu 'sent' phải chứa ba dấu gạch dưới ___ làm chỗ trống")
        if "coll" in fields and "___" not in str(x.get("coll", "")):
            errors.append(f"{tag}: cụm 'coll' phải chứa ba dấu gạch dưới ___ làm chỗ trống")

    # Mỗi trường dùng làm đáp án phải là duy nhất, nếu không sẽ có 2 phương án giống hệt nhau
    for key, label in [("w", "từ"), ("vi", "nghĩa tiếng Việt"),
                       ("sentA", "đáp án điền từ"), ("collA", "đáp án cụm từ")]:
        if key not in used:
            continue
        seen = {}
        for x in words:
            v = str(x.get(key, "")).strip().lower()
            if not v:
                continue
            if v in seen:
                errors.append(
                    f"Trùng {label} '{x.get(key)}' giữa '{seen[v]}' và '{x.get('w')}' "
                    f"— sẽ tạo ra hai phương án giống hệt nhau, phải sửa cho khác đi"
                )
            seen[v] = x.get("w")

    return errors


def build(cfg, out_path):
    with open(TEMPLATE, encoding="utf-8") as fh:
        html = fh.read()

    words = cfg.get("words") or []
    grammar = cfg.get("grammar") or []
    seconds = int(cfg.get("seconds", 20))
    title = cfg["title"]
    types, per_type, n_parts, total, _ = resolve_config(cfg)
    bank = " &amp; ".join(filter(None, [f"{len(words)} từ &amp; cụm" if words else "",
                                        f"{len(grammar)} câu ngữ pháp" if grammar else ""]))
    subtitle = cfg.get("subtitle") or (
        f"{bank} · {total} câu mỗi lượt · {seconds} giây mỗi câu"
    )

    # thiếu khóa "endpoint" thì dùng link mặc định; có khóa (kể cả rỗng) thì tôn trọng
    endpoint = cfg["endpoint"] if "endpoint" in cfg else DEFAULT_ENDPOINT

    word_types = part_plan(cfg)[0]
    used = set()
    for t in word_types:
        used.update(TYPE_FIELDS[t])
    slim = [{f: x[f] for f in FIELDS if f in used} for x in words]
    words_js = json.dumps(slim, ensure_ascii=False, indent=2)
    g_slim = [{k: g[k] for k in ("q", "options", "answer", "note") if k in g} for g in grammar]
    grammar_js = json.dumps(g_slim, ensure_ascii=False, indent=2)

    html = (html
            .replace("__WORDS__", words_js)
            .replace("__GRAMMAR__", grammar_js)
            .replace("__ENDPOINT__", endpoint)
            .replace("__SECONDS__", str(seconds))
            .replace("__TYPE_IDS__", json.dumps(types))
            .replace("__PER_TYPE__", str(per_type))
            .replace("__SUBTITLE__", subtitle)
            .replace("__KICKER__", cfg.get("kicker", "Vocabulary"))
            .replace("__TITLE__", title))

    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write(html)

    return len(words) + len(grammar), seconds, endpoint, types, per_type, total


def main():
    if hasattr(sys.stdout, "reconfigure"):   # console Windows mặc định cp1252 sẽ lỗi với tiếng Việt
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Dựng quiz từ vựng VTG từ file JSON")
    ap.add_argument("config", help="đường dẫn tới file words.json")
    ap.add_argument("-o", "--output", help="đường dẫn file .html xuất ra (bắt buộc trừ khi --check)")
    ap.add_argument("--check", action="store_true",
                    help="chỉ kiểm tra dữ liệu, không dựng file")
    ap.add_argument("--no-send", action="store_true",
                    help="ép endpoint = \"\" (tắt gửi kết quả) — dùng khi dựng bản để test")
    ap.add_argument("--skip-check", action="store_true",
                    help="bỏ qua bước kiểm tra dữ liệu (không khuyến khích)")
    args = ap.parse_args()
    if not args.check and not args.output:
        ap.error("cần -o/--output (hoặc dùng --check)")

    with open(args.config, encoding="utf-8") as fh:
        cfg = json.load(fh)

    if "title" not in cfg or ("words" not in cfg and "grammar" not in cfg):
        sys.exit("Lỗi: file JSON phải có 'title' và ít nhất một trong 'words' / 'grammar'.")

    if not args.skip_check or args.check:
        errors = validate(cfg.get("words"), cfg)
        if errors:
            print("KIỂM TRA DỮ LIỆU THẤT BẠI:\n", file=sys.stderr)
            for e in errors:
                print("  - " + e, file=sys.stderr)
            sys.exit(1)
    if args.check:
        types, per_type, _, total, _ = resolve_config(cfg)
        print(f"Dữ liệu hợp lệ: {len(cfg.get('words') or [])} từ, "
              f"{len(cfg.get('grammar') or [])} câu ngữ pháp · {total} câu/lượt")
        return

    if args.no_send:
        cfg["endpoint"] = ""

    n, sec, ep, types, per_type, total = build(cfg, args.output)
    print(f"Đã dựng xong: {args.output}")
    default_order = "ngẫu nhiên 3/5 + G" if cfg.get("grammar") else "ngẫu nhiên 4/5"
    print(f"  dạng: {''.join(types) if types else default_order} · {per_type} câu/phần · {total} câu/lượt")
    print(f"  {n} mục · {sec} giây/câu · gửi kết quả: "
          f"{'CÓ (' + ep[-24:] + ')' if ep else 'KHÔNG (chế độ sao chép thủ công)'}")


if __name__ == "__main__":
    main()

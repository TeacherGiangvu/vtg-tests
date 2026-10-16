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
  ]
}
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
DEFAULT_PARTS = 4      # không có "types": bốc ngẫu nhiên 4 dạng
DEFAULT_PER_TYPE = 5
HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(HERE, "..", "assets", "template.html")


def resolve_config(cfg):
    """Đọc 'types' và 'per_type'. Trả về (types, per_type, n_parts, total, errors).
    types = None nghĩa là bốc ngẫu nhiên 4 trong 5 dạng (hành vi cũ)."""
    errors = []
    types = cfg.get("types")
    if types is not None:
        if (not isinstance(types, list) or not types
                or any(t not in TYPE_FIELDS for t in types)):
            errors.append("'types' phải là danh sách không rỗng gồm các mã A, B, C, D, E "
                          "(ví dụ [\"A\", \"C\", \"E\"])")
            types = None
        elif len(set(types)) != len(types):
            errors.append("'types' có mã bị lặp lại — mỗi dạng chỉ dùng một lần")
            types = None
    per_type = cfg.get("per_type", DEFAULT_PER_TYPE)
    if isinstance(per_type, bool) or not isinstance(per_type, int) or per_type < 1:
        errors.append("'per_type' phải là số nguyên dương")
        per_type = DEFAULT_PER_TYPE
    n_parts = len(types) if types else DEFAULT_PARTS
    return types, per_type, n_parts, n_parts * per_type, errors


def validate(words, cfg=None):
    """Kiểm tra dữ liệu trước khi dựng file. Trả về danh sách lỗi."""
    types, per_type, n_parts, total, errors = resolve_config(cfg or {})

    # trường bắt buộc: gộp theo các dạng được chọn (không chọn = đủ cả 5 dạng)
    used = set()
    for t in (types or TYPE_FIELDS):
        used.update(TYPE_FIELDS[t])
    fields = [f for f in FIELDS if f in used]

    if len(words) < total:
        errors.append(
            f"Chỉ có {len(words)} từ. Cần TỐI THIỂU {total} từ "
            f"({n_parts} phần × {per_type} câu) vì mỗi lượt lấy {total} từ khác nhau."
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

    words = cfg["words"]
    seconds = int(cfg.get("seconds", 20))
    title = cfg["title"]
    types, per_type, n_parts, total, _ = resolve_config(cfg)
    subtitle = cfg.get("subtitle") or (
        f"{len(words)} từ &amp; cụm · {total} câu mỗi lượt · {seconds} giây mỗi câu"
    )

    # thiếu khóa "endpoint" thì dùng link mặc định; có khóa (kể cả rỗng) thì tôn trọng
    endpoint = cfg["endpoint"] if "endpoint" in cfg else DEFAULT_ENDPOINT

    used = set()
    for t in (types or TYPE_FIELDS):
        used.update(TYPE_FIELDS[t])
    slim = [{f: x[f] for f in FIELDS if f in used} for x in words]
    words_js = json.dumps(slim, ensure_ascii=False, indent=2)

    html = (html
            .replace("__WORDS__", words_js)
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

    return len(words), seconds, endpoint, types, per_type, total


def main():
    ap = argparse.ArgumentParser(description="Dựng quiz từ vựng VTG từ file JSON")
    ap.add_argument("config", help="đường dẫn tới file words.json")
    ap.add_argument("-o", "--output", required=True, help="đường dẫn file .html xuất ra")
    ap.add_argument("--skip-check", action="store_true",
                    help="bỏ qua bước kiểm tra dữ liệu (không khuyến khích)")
    args = ap.parse_args()

    with open(args.config, encoding="utf-8") as fh:
        cfg = json.load(fh)

    if "title" not in cfg or "words" not in cfg:
        sys.exit("Lỗi: file JSON phải có 'title' và 'words'.")

    if not args.skip_check:
        errors = validate(cfg["words"], cfg)
        if errors:
            print("KIỂM TRA DỮ LIỆU THẤT BẠI:\n", file=sys.stderr)
            for e in errors:
                print("  - " + e, file=sys.stderr)
            sys.exit(1)

    n, sec, ep, types, per_type, total = build(cfg, args.output)
    print(f"Đã dựng xong: {args.output}")
    print(f"  dạng: {''.join(types) if types else 'ngẫu nhiên 4/5'} · {per_type} câu/phần · {total} câu/lượt")
    print(f"  {n} từ · {sec} giây/câu · gửi kết quả: "
          f"{'CÓ (' + ep[-24:] + ')' if ep else 'KHÔNG (chế độ sao chép thủ công)'}")


if __name__ == "__main__":
    main()

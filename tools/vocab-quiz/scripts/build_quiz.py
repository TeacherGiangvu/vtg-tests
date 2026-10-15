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
HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(HERE, "..", "assets", "template.html")


def validate(words):
    """Kiểm tra dữ liệu trước khi dựng file. Trả về danh sách lỗi."""
    errors = []

    if len(words) < 20:
        errors.append(
            f"Chỉ có {len(words)} từ. Cần TỐI THIỂU 20 từ vì mỗi lượt lấy 20 từ khác nhau."
        )

    for i, x in enumerate(words, 1):
        tag = f"Từ #{i} ({x.get('w', '???')})"

        for f in FIELDS:
            if not x.get(f) or not str(x[f]).strip():
                errors.append(f"{tag}: thiếu trường '{f}'")

        if "sent" in x and "___" not in str(x.get("sent", "")):
            errors.append(f"{tag}: câu 'sent' phải chứa ba dấu gạch dưới ___ làm chỗ trống")
        if "coll" in x and "___" not in str(x.get("coll", "")):
            errors.append(f"{tag}: cụm 'coll' phải chứa ba dấu gạch dưới ___ làm chỗ trống")

    # Mỗi trường dùng làm đáp án phải là duy nhất, nếu không sẽ có 2 phương án giống hệt nhau
    for key, label in [("w", "từ"), ("vi", "nghĩa tiếng Việt"),
                       ("sentA", "đáp án điền từ"), ("collA", "đáp án cụm từ")]:
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
    subtitle = cfg.get("subtitle") or (
        f"{len(words)} từ &amp; cụm · 20 câu mỗi lượt · {seconds} giây mỗi câu"
    )

    # thiếu khóa "endpoint" thì dùng link mặc định; có khóa (kể cả rỗng) thì tôn trọng
    endpoint = cfg["endpoint"] if "endpoint" in cfg else DEFAULT_ENDPOINT

    slim = [{f: x[f] for f in FIELDS} for x in words]
    words_js = json.dumps(slim, ensure_ascii=False, indent=2)

    html = (html
            .replace("__WORDS__", words_js)
            .replace("__ENDPOINT__", endpoint)
            .replace("__SECONDS__", str(seconds))
            .replace("__SUBTITLE__", subtitle)
            .replace("__KICKER__", cfg.get("kicker", "Vocabulary"))
            .replace("__TITLE__", title))

    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write(html)

    return len(words), seconds, endpoint


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
        errors = validate(cfg["words"])
        if errors:
            print("KIỂM TRA DỮ LIỆU THẤT BẠI:\n", file=sys.stderr)
            for e in errors:
                print("  - " + e, file=sys.stderr)
            sys.exit(1)

    n, sec, ep = build(cfg, args.output)
    print(f"Đã dựng xong: {args.output}")
    print(f"  {n} từ · {sec} giây/câu · gửi kết quả: "
          f"{'CÓ (' + ep[-24:] + ')' if ep else 'KHÔNG (chế độ sao chép thủ công)'}")


if __name__ == "__main__":
    main()

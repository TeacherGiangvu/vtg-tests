---
name: vtg-vocab-quiz
description: Tạo bài test từ vựng tiếng Anh tương tác (file HTML) theo brand VTG English Center cho học sinh của Giang, có đếm ngược thời gian mỗi câu, 5 dạng câu hỏi xoay vòng, bảng tổng kết và tự gửi kết quả về Google Sheets. PHẢI dùng skill này BẤT CỨ KHI NÀO người dùng yêu cầu tạo quiz/bài test/bài kiểm tra từ vựng, "làm quiz cho list từ này", "tạo bài luyện từ vựng", "test từ vựng cho học sinh", hoặc đưa một danh sách từ vựng (từ bài Reading, Listening, giáo trình, file Word, ảnh chụp sách) và muốn biến nó thành bài luyện tập tương tác — kể cả khi họ không nhắc tới chữ "HTML" hay "VTG".
---

# VTG Vocabulary Quiz Builder

Biến một danh sách từ vựng bất kỳ thành file HTML quiz tương tác, chạy offline trên trình duyệt, gửi kết quả về Google Sheets của giáo viên.

## Quy trình

1. Thu thập từ vựng (từ tin nhắn, file, hoặc ảnh người dùng gửi)
2. Viết file `words.json` theo cấu trúc bên dưới
3. Chạy `scripts/build_quiz.py` để dựng file HTML
4. Đưa file vào `/mnt/user-data/outputs/` và gọi `present_files`

Không tự viết lại engine HTML. Engine đã có sẵn ở `assets/template.html`, chỉ cần đổ dữ liệu vào.

## Bước 1 — Xác định thông tin còn thiếu

Trước khi bắt tay, cần biết:

- **Số lượng từ**: engine lấy 20 từ khác nhau mỗi lượt, nên **bắt buộc tối thiểu 20 từ**. Nếu người dùng đưa ít hơn, nói rõ và đề nghị bổ sung thêm từ cùng chủ đề, hoặc gộp với danh sách khác.
- **Link Google Sheets**: đã gắn sẵn link mặc định của VTG trong `scripts/build_quiz.py`. **Không cần hỏi, cứ bỏ qua khóa `endpoint`** trong words.json là tự dùng link đó. Mọi bài quiz đổ chung về một Sheet, phân biệt bằng cột "Bài quiz". Chỉ đặt `"endpoint": ""` khi người dùng nói rõ là không muốn thu kết quả, hoặc `"endpoint": "<link khác>"` khi họ đưa link mới.
- **Thời gian mỗi câu**: mặc định 20 giây. Với từ dài hoặc trình độ thấp (A1–A2), 25–30 giây hợp lý hơn. Nếu bộ từ có nhiều câu ví dụ dài, chủ động đề xuất tăng lên.

Đừng hỏi dồn dập. Nếu suy ra được từ ngữ cảnh (ví dụ đã có link endpoint trong cuộc trò chuyện trước) thì cứ dùng, chỉ nói một câu xác nhận.

## Bước 2 — Viết words.json

```json
{
  "title": "Vocabulary Quiz — Organic Farming",
  "kicker": "IELTS Reading",
  "seconds": 20,

  "words": [
    {
      "w":     "claim",
      "vi":    "tuyên bố, khẳng định (chưa chắc đúng)",
      "def":   "to say that something is true, although it has not been proved",
      "sent":  "Organic farming is often ___ to be safer, but many studies reject this idea.",
      "sentA": "claimed",
      "coll":  "make / support / reject a ___",
      "collA": "claim"
    }
  ]
}
```

| Trường | Nội dung | Dùng cho dạng câu hỏi |
|---|---|---|
| `w` | từ/cụm gốc, dạng từ điển | Việt→Anh, Định nghĩa |
| `vi` | nghĩa tiếng Việt | Anh→Việt |
| `def` | định nghĩa tiếng Anh, **đơn giản hơn từ được định nghĩa** | Định nghĩa |
| `sent` | câu ví dụ có `___` làm chỗ trống | Điền từ |
| `sentA` | dạng từ đúng để điền (có thể chia thì: *claimed*, *expanding*) | Điền từ |
| `coll` | cụm cố định có `___` | Cụm từ |
| `collA` | từ điền vào cụm (thường là dạng gốc) | Cụm từ |

Các khóa ngoài `words`: `title` (bắt buộc), `kicker`, `subtitle`, `seconds`, `endpoint`, `types`, `per_type`, `level`, `topic` — đều tùy chọn, có mặc định hợp lý. `level` + `topic` (hoặc tên file `<LEVEL>_Vocab_<Topic>.json`) dùng cho lệnh `/build-vocab`.

### Ngữ pháp (dạng `G`)

File có thể có `words`, `grammar`, hoặc cả hai. Mỗi mục `grammar`:

```json
{"q": "Yesterday we ___ a bear.", "options": ["see", "saw", "seen"], "answer": 1, "note": "quy tắc ngắn, tùy chọn"}
```

- Đúng **3** phương án, không trùng nhau; `answer` là chỉ số (0–2) của đáp án đúng; câu `q` có `___`; `note` hiện sau khi trả lời.
- `types` thêm mã `G` (ví dụ `["A", "C", "G"]`). Bỏ trống `types`: chỉ `words` = bốc 4/5 dạng (như cũ); chỉ `grammar` = `["G"]`; có cả hai = bốc 3 dạng từ vựng rồi phần `G` ở cuối.
- Phần `G` cần tối thiểu `per_type` câu. Mẫu: `assets/example_grammar.json`.
- Script chỉ kiểm tra được hình thức; Giang/Claude phải tự đảm bảo mỗi câu chỉ có **một** đáp án đúng.
- `build_quiz.py --check` chỉ kiểm tra; `--no-send` dựng bản test không gửi kết quả (endpoint rỗng).

### Nguyên tắc bắt buộc

**Mọi đáp án phải là duy nhất.** Bốn trường `w`, `vi`, `sentA`, `collA` không được trùng nhau giữa các từ — nếu hai từ có cùng `vi`, học sinh sẽ thấy hai lựa chọn giống hệt và không thể chọn đúng. Script tự kiểm tra và báo lỗi, nhưng nên tránh ngay từ đầu.

**Câu `sent` phải chỉ có một đáp án đúng.** Viết đủ ngữ cảnh để loại trừ các từ khác trong danh sách. Câu "The result was very ___" là câu tồi vì nhiều tính từ đều điền được.

**`def` phải dễ hơn `w`.** Dùng từ vựng A2–B1 để định nghĩa. Định nghĩa mà khó hơn chính từ cần học thì vô dụng.

**Ưu tiên câu ví dụ lấy từ ngữ cảnh gốc.** Nếu từ vựng đến từ một bài đọc/bài nghe cụ thể, viết `sent` bám sát câu trong bài đó (có thể rút gọn). Học sinh vừa ôn từ vừa nhớ lại bài.

**`vi` viết đủ sắc thái, không dịch cụt.** "tuyên bố, khẳng định (chưa chắc đúng)" tốt hơn "nói".

## Bước 3 — Dựng file

```bash
python3 scripts/build_quiz.py words.json -o /mnt/user-data/outputs/VTG_Quiz_<TenChuDe>.html
```

Script tự kiểm tra dữ liệu trước khi dựng: thiếu trường, thiếu `___`, dưới 20 từ, hoặc trùng đáp án đều bị chặn. Nếu báo lỗi, sửa `words.json` rồi chạy lại — đừng dùng `--skip-check` trừ khi người dùng yêu cầu.

Sau đó gọi `present_files` với đường dẫn file HTML.

## Engine có sẵn những gì

Không cần mô tả lại chi tiết cho người dùng trừ khi họ hỏi:

- Mỗi lượt 20 câu, chia 4 phần × 5 câu, đổi dạng câu hỏi sau mỗi 5 câu
- 5 dạng: Anh→Việt, Việt→Anh, Điền từ vào câu, Định nghĩa tiếng Anh, Hoàn thành cụm từ. Mỗi lượt bốc ngẫu nhiên 4/5 dạng
- 20 từ khác nhau mỗi lượt, không lặp; phương án nhiễu sinh ngẫu nhiên từ các từ khác nên mỗi lần làm lại đề đều mới
- Đồng hồ đếm ngược từng câu, đổi màu xanh → cam (còn 10 giây) → đỏ nhấp nháy (còn 5 giây). Hết giờ thì khoá lựa chọn, hiện đáp án đúng, tính là sai
- Màn hình nhập Họ tên + Lớp ở đầu bài
- Cuối bài: điểm, xếp loại, bảng tổng kết từng câu, danh sách "Từ cần học lại"
- Tự gửi kết quả về Google Sheets; nếu lỗi mạng thì hiện nút sao chép để gửi Zalo

## Khi người dùng muốn sửa engine

Sửa `assets/template.html`. Lưu ý các chỗ trống `__WORDS__`, `__GRAMMAR__`, `__ENDPOINT__`, `__TYPE_IDS__`, `__PER_TYPE__`, `__SECONDS__`, `__TITLE__`, `__SUBTITLE__`, `__KICKER__` phải giữ nguyên, nếu không script sẽ không đổ dữ liệu vào được.

## Tài liệu kèm theo

- `references/google-sheets-setup.md` — thiết lập nơi nhận kết quả. Chỉ đọc khi người dùng gặp lỗi không nhận được kết quả, hoặc muốn dựng một Sheet mới (có bảng xử lý sự cố các lỗi thường gặp). Bình thường không cần đụng tới vì link đã có sẵn.
- `assets/AppsScript_VTG_Quiz.gs` — code dán vào Google Sheet.
- `assets/example_words.json` — ví dụ đầy đủ 25 từ, dùng làm mẫu tham chiếu khi viết bộ từ mới.

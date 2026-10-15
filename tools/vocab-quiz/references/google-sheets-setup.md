# Hướng dẫn cài đặt — Nhận kết quả quiz về Google Sheets

Làm một lần duy nhất, mất khoảng 10 phút. Sau đó dùng mãi cho mọi bài quiz sau này.

---

## PHẦN 1 — Tạo nơi nhận kết quả (Google Sheet + Apps Script)

**Bước 1.** Vào https://sheets.new để tạo một Google Sheet mới. Đặt tên, ví dụ: `VTG — Kết quả Quiz từ vựng`.

**Bước 2.** Trên thanh menu của Sheet, chọn **Tiện ích mở rộng → Apps Script** (Extensions → Apps Script). Một tab mới sẽ mở ra.

**Bước 3.** Xoá toàn bộ đoạn code mẫu `function myFunction() {}` đang có sẵn. Mở file `AppsScript_VTG_Quiz.gs`, copy **toàn bộ** nội dung và dán vào. Bấm biểu tượng đĩa mềm để lưu.

**Bước 4.** Bấm nút **Triển khai** (Deploy) ở góc trên bên phải → **Tuỳ chọn triển khai mới** (New deployment).

- Bấm biểu tượng bánh răng ⚙️ cạnh chữ "Chọn loại" → chọn **Ứng dụng web** (Web app)
- **Mô tả**: ghi gì cũng được, ví dụ `VTG Quiz v1`
- **Thực thi với tư cách** (Execute as): **Tôi** (Me)
- **Ai có quyền truy cập** (Who has access): **Bất kỳ ai** (Anyone) ← **rất quan trọng**, nếu chọn sai học sinh sẽ không gửi được
- Bấm **Triển khai**

**Bước 5.** Google sẽ hỏi cấp quyền. Bấm **Cho phép truy cập** → chọn tài khoản của bạn → màn hình cảnh báo "Google chưa xác minh ứng dụng này" sẽ hiện ra, bấm **Nâng cao** (Advanced) → **Chuyển đến ... (không an toàn)** → **Cho phép**.

> Cảnh báo này là bình thường với mọi script tự viết, không phải lỗi.

**Bước 6.** Copy **URL ứng dụng web** hiện ra. Nó có dạng:

```
https://script.google.com/macros/s/AKfycbxxxxxxxxxxxxxxxxxxxx/exec
```

**Bước 7 (kiểm tra).** Dán URL đó vào trình duyệt. Nếu thấy dòng chữ *"VTG Quiz endpoint đang hoạt động."* là đã đúng.

---

## PHẦN 2 — Gắn link vào file quiz

Mở file `VTG_Quiz_Organic_Farming_v2.html` bằng Notepad (Windows), TextEdit (Mac) hoặc VS Code. Tìm đoạn ở gần đầu phần `<script>`:

```javascript
const ENDPOINT = "";
```

Dán URL vừa copy vào giữa hai dấu nháy:

```javascript
const ENDPOINT = "https://script.google.com/macros/s/AKfycbxxxx.../exec";
```

Lưu file lại. Xong.

> Nếu để trống, quiz vẫn chạy bình thường nhưng sẽ hiện nút "Sao chép kết quả" để học sinh gửi thủ công qua Zalo.

---

## PHẦN 3 — Đưa file cho học sinh

**Cách nhanh (gửi file):** gửi file HTML qua Zalo. Học sinh tải về, bấm mở là chạy bằng trình duyệt.
*Lưu ý:* trên một số điện thoại, mở file tải về từ Zalo có thể bị chặn gửi dữ liệu đi. Nếu gặp tình huống này, học sinh vẫn dùng được nút "Sao chép kết quả".

**Cách khuyên dùng (một đường link duy nhất):** vào https://app.netlify.com/drop, kéo thả file HTML vào. Netlify trả về một đường link công khai, ví dụ `https://vtg-quiz-abc.netlify.app`. Gửi link đó cho học sinh — mở được trên cả điện thoại lẫn máy tính, không cần tải gì, và bạn sửa file thì chỉ cần kéo thả lại bản mới.

---

## PHẦN 4 — Đọc kết quả

Mở Google Sheet của bạn, sẽ tự sinh ra các sheet sau khi có học sinh đầu tiên nộp bài:

| Sheet | Nội dung |
|---|---|
| **TongHop** | Mỗi lượt làm bài 1 dòng: thời gian nộp, họ tên, lớp, điểm, %, thời gian làm, danh sách từ sai |
| **ChiTiet** | Mỗi câu hỏi 1 dòng: câu số, dạng câu hỏi, từ vựng, nội dung câu hỏi, em chọn gì, đáp án đúng, đúng/sai |
| **ThongKeTuSai** | Bảng xếp hạng từ nào cả lớp sai nhiều nhất (xem bên dưới) |

**Để xem cả lớp yếu từ nào:** đóng và mở lại file Sheet một lần (để menu hiện ra), rồi chọn **VTG Quiz → Cập nhật thống kê từ sai** trên thanh menu. Sheet `ThongKeTuSai` sẽ được tạo/cập nhật, sắp xếp theo tỉ lệ sai từ cao xuống thấp — đây chính là danh sách từ bạn nên dạy lại đầu buổi sau.

---

## Xử lý sự cố

| Hiện tượng | Nguyên nhân & cách xử lý |
|---|---|
| Học sinh báo "Gửi không thành công" | Kiểm tra lại Bước 4: mục "Ai có quyền truy cập" phải là **Bất kỳ ai**. |
| Sheet không có dữ liệu | Mở URL `/exec` trên trình duyệt xem có ra dòng chữ xác nhận không. Nếu không, deploy lại. |
| Sửa code Apps Script xong không thấy tác dụng | Phải **Triển khai → Quản lý triển khai → sửa (bút chì) → Phiên bản: Phiên bản mới → Triển khai**. Nếu tạo deployment mới thì URL sẽ đổi, phải cập nhật lại vào file HTML. |
| Muốn dùng cho bài quiz khác | Cùng một URL dùng được cho nhiều bài quiz; cột "Bài quiz" trong sheet TongHop sẽ phân biệt giúp bạn. |

---

## Một lưu ý về cách đọc dữ liệu

Đây là bài **tự luyện tại nhà**: học sinh có thể làm lại nhiều lượt, hoặc mở file từ vựng ra tra trong lúc làm. Vì vậy nên dùng số liệu này để trả lời câu hỏi *"cả lớp đang yếu từ nào, ai chưa làm bài"* — chứ không nên dùng làm điểm kiểm tra chính thức. Cột **thời gian làm** trong sheet TongHop cũng đáng để ý: một lượt 20 câu làm nghiêm túc thường mất khoảng 3–6 phút.

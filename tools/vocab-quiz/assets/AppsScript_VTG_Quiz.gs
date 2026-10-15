/**
 * VTG English Center — Bộ nhận kết quả Quiz từ vựng
 * Dán toàn bộ file này vào Apps Script của Google Sheet, rồi Deploy làm Web App.
 * Hướng dẫn chi tiết xem file Huong_Dan_Cai_Dat.md
 */

var SHEET_SUMMARY = 'TongHop';
var SHEET_DETAIL  = 'ChiTiet';
var SHEET_STATS   = 'ThongKeTuSai';

var HEAD_SUMMARY = ['Thời gian nộp','Họ tên','Lớp','Bài quiz','Điểm','Tổng câu','%',
                    'Thời gian làm','Từ trả lời sai','Mã lượt'];
var HEAD_DETAIL  = ['Thời gian nộp','Họ tên','Lớp','Mã lượt','Câu số','Dạng câu hỏi',
                    'Từ vựng','Nội dung câu hỏi','Em chọn','Đáp án đúng','Kết quả'];

/** Kiểm tra nhanh bằng trình duyệt: mở link /exec sẽ thấy dòng chữ này. */
function doGet() {
  return ContentService
    .createTextOutput('VTG Quiz endpoint đang hoạt động.')
    .setMimeType(ContentService.MimeType.TEXT);
}

/** Nhận dữ liệu từ file quiz HTML gửi lên. */
function doPost(e) {
  var lock = LockService.getScriptLock();
  try {
    lock.waitLock(20000);

    var data = JSON.parse(e.postData.contents);
    var ss   = SpreadsheetApp.getActiveSpreadsheet();
    var when = new Date();

    // --- Sheet TỔNG HỢP: mỗi lượt làm bài 1 dòng ---
    var s1 = getSheet_(ss, SHEET_SUMMARY, HEAD_SUMMARY);
    s1.appendRow([
      when,
      data.name || '',
      data.cls || '',
      data.quizName || '',
      data.score,
      data.total,
      (data.percent || 0) / 100,
      data.duration || '',
      data.wrongWords || '',
      data.attemptId || ''
    ]);
    s1.getRange(s1.getLastRow(), 1).setNumberFormat('dd/MM/yyyy HH:mm:ss');
    s1.getRange(s1.getLastRow(), 7).setNumberFormat('0%');

    // --- Sheet CHI TIẾT: mỗi câu hỏi 1 dòng ---
    var rows = (data.details || []).map(function (d) {
      return [when, data.name || '', data.cls || '', data.attemptId || '',
              d.no, d.type, d.word, d.question, d.chosen, d.correct, d.result];
    });
    if (rows.length) {
      var s2 = getSheet_(ss, SHEET_DETAIL, HEAD_DETAIL);
      s2.getRange(s2.getLastRow() + 1, 1, rows.length, HEAD_DETAIL.length).setValues(rows);
      s2.getRange(s2.getLastRow() - rows.length + 1, 1, rows.length, 1)
        .setNumberFormat('dd/MM/yyyy HH:mm:ss');
    }

    return json_({ ok: true });

  } catch (err) {
    return json_({ ok: false, error: String(err) });
  } finally {
    try { lock.releaseLock(); } catch (ignore) {}
  }
}

/** Lấy sheet, tạo mới kèm tiêu đề nếu chưa có. */
function getSheet_(ss, name, header) {
  var sh = ss.getSheetByName(name);
  if (!sh) {
    sh = ss.insertSheet(name);
    sh.appendRow(header);
    sh.getRange(1, 1, 1, header.length)
      .setFontWeight('bold').setFontColor('#FFFFFF').setBackground('#2C4A3E');
    sh.setFrozenRows(1);
  }
  return sh;
}

function json_(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}

/* ==========================================================
   TIỆN ÍCH CHO GIÁO VIÊN
   Mở lại file Sheet sẽ thấy menu "VTG Quiz" trên thanh công cụ.
   ========================================================== */

function onOpen() {
  SpreadsheetApp.getUi()
    .createMenu('VTG Quiz')
    .addItem('Cập nhật thống kê từ sai', 'buildStats')
    .addToUi();
}

/** Đếm xem cả lớp sai nhiều nhất ở từ nào. */
function buildStats() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var s2 = ss.getSheetByName(SHEET_DETAIL);
  if (!s2 || s2.getLastRow() < 2) {
    SpreadsheetApp.getUi().alert('Chưa có dữ liệu chi tiết nào.');
    return;
  }

  var values = s2.getRange(2, 1, s2.getLastRow() - 1, HEAD_DETAIL.length).getValues();
  var total = {}, wrong = {};

  values.forEach(function (r) {
    var word = r[6], result = r[10];
    if (!word) return;
    total[word] = (total[word] || 0) + 1;
    if (result === 'Sai') wrong[word] = (wrong[word] || 0) + 1;
  });

  var rows = Object.keys(total).map(function (w) {
    var t = total[w], s = wrong[w] || 0;
    return [w, t, s, t ? s / t : 0];
  }).sort(function (a, b) { return b[3] - a[3] || b[2] - a[2]; });

  var sh = ss.getSheetByName(SHEET_STATS);
  if (!sh) sh = ss.insertSheet(SHEET_STATS);
  sh.clear();
  sh.appendRow(['Từ vựng', 'Số lần xuất hiện', 'Số lần sai', 'Tỉ lệ sai']);
  sh.getRange(1, 1, 1, 4)
    .setFontWeight('bold').setFontColor('#FFFFFF').setBackground('#2C4A3E');
  sh.setFrozenRows(1);
  if (rows.length) {
    sh.getRange(2, 1, rows.length, 4).setValues(rows);
    sh.getRange(2, 4, rows.length, 1).setNumberFormat('0%');
  }
  sh.autoResizeColumns(1, 4);

  SpreadsheetApp.getUi().alert('Đã cập nhật sheet "' + SHEET_STATS + '".');
}

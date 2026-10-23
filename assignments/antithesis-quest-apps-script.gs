/**
 * Antithesis Quest: live results collector (Google Apps Script)
 *
 * SETUP (once):
 * 1. Create a NEW Google Sheet (e.g. "Antithesis Quest Results"). Extensions > Apps Script. Paste this file.
 * 2. Project Settings > Script properties > add  TEACHER_KEY = <a password only you know>
 * 3. Deploy > New deployment > type "Web app" > Execute as: Me, Who has access: Anyone > Deploy. Authorize.
 * 4. Copy the web-app URL (ends with /exec). Paste it into:
 *      - ENDPOINT in Antithesis_Quiz_Game.html (students)
 *      - the "Endpoint" box of Antithesis_Quest_Teacher.html (teacher), plus your TEACHER_KEY
 * 5. After editing this script later: Deploy > Manage deployments > edit > New version.
 *
 * Sheet "Live": one row per play session (students post here while playing).
 * Sheet "Log":  every event, append-only (for your records).
 */

var LIVE_HEADERS = ['sid', 'name', 'class', 'startedAt', 'lastSeen', 'status', 'qIndex', 'score', 'lives', 'correct', 'answers'];
var LOG_HEADERS = ['time', 'sid', 'name', 'class', 'type', 'q', 'choice', 'ok', 'ms', 'score', 'lives'];

function sheet_(name, headers) {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sh = ss.getSheetByName(name);
  if (!sh) {
    sh = ss.insertSheet(name);
    sh.appendRow(headers);
    sh.setFrozenRows(1);
  }
  return sh;
}

function key_() {
  return PropertiesService.getScriptProperties().getProperty('TEACHER_KEY') || '';
}

function json_(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(ContentService.MimeType.JSON);
}

/** Students POST events here (text/plain JSON body). */
function doPost(e) {
  var lock = LockService.getScriptLock();
  lock.waitLock(20000);
  try {
    var d = JSON.parse(e.postData.contents);
    var now = Date.now();

    if (d.type === 'reset') {
      if (!key_() || d.key !== key_()) return json_({ ok: false, error: 'bad key' });
      var live = sheet_('Live', LIVE_HEADERS);
      if (live.getLastRow() > 1) live.getRange(2, 1, live.getLastRow() - 1, LIVE_HEADERS.length).clearContent();
      return json_({ ok: true });
    }

    if (!d.sid) return json_({ ok: false, error: 'no sid' });
    var name = String(d.name || '').slice(0, 40);
    var cls = String(d.cls || '').slice(0, 30);

    var log = sheet_('Log', LOG_HEADERS);
    log.appendRow([new Date(now), d.sid, name, cls, d.type, d.q === undefined ? '' : d.q,
      d.choice === undefined ? '' : d.choice, d.ok === undefined ? '' : d.ok,
      d.ms === undefined ? '' : d.ms, d.score === undefined ? '' : d.score, d.lives === undefined ? '' : d.lives]);

    var sh = sheet_('Live', LIVE_HEADERS);
    var last = sh.getLastRow();
    var ids = last > 1 ? sh.getRange(2, 1, last - 1, 1).getValues() : [];
    var row = -1;
    for (var i = 0; i < ids.length; i++) { if (ids[i][0] === d.sid) { row = i + 2; break; } }

    var rec;
    if (row === -1) {
      rec = [d.sid, name, cls, now, now, 'playing', 0, 0, 3, 0, '[]'];
    } else {
      rec = sh.getRange(row, 1, 1, LIVE_HEADERS.length).getValues()[0];
    }
    rec[4] = now;                                   // lastSeen
    if (d.type === 'question') rec[6] = d.q;
    if (d.type === 'answer') {
      var ans = [];
      try { ans = JSON.parse(rec[10] || '[]'); } catch (x) {}
      var dup = ans.some(function (a) { return a.q === d.q; });
      if (!dup) ans.push({ q: d.q, choice: d.choice, ok: !!d.ok, ms: d.ms, t: now });
      rec[10] = JSON.stringify(ans);
      rec[7] = d.score; rec[8] = d.lives;
      rec[9] = ans.filter(function (a) { return a.ok; }).length;
      rec[6] = d.q;
    }
    if (d.type === 'finish') {
      rec[5] = d.status || 'won';
      rec[7] = d.score; rec[8] = d.lives; rec[9] = d.correct;
    }
    if (row === -1) sh.appendRow(rec); else sh.getRange(row, 1, 1, rec.length).setValues([rec]);
    return json_({ ok: true });
  } catch (err) {
    return json_({ ok: false, error: String(err) });
  } finally {
    lock.releaseLock();
  }
}

/** Teacher dashboard GETs the state: ?action=state&key=TEACHER_KEY */
function doGet(e) {
  var p = e.parameter || {};
  if (!key_() || p.key !== key_()) return json_({ ok: false, error: 'bad key' });
  var sh = sheet_('Live', LIVE_HEADERS);
  var last = sh.getLastRow();
  var rows = last > 1 ? sh.getRange(2, 1, last - 1, LIVE_HEADERS.length).getValues() : [];
  var students = rows.map(function (r) {
    var ans = [];
    try { ans = JSON.parse(r[10] || '[]'); } catch (x) {}
    return { sid: r[0], name: r[1], cls: r[2], startedAt: r[3], lastSeen: r[4], status: r[5],
             qIndex: r[6], score: r[7], lives: r[8], correct: r[9], answers: ans };
  });
  return json_({ ok: true, now: Date.now(), total: 5, students: students });
}

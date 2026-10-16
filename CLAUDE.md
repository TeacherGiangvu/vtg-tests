# VTG tests repo

Public GitHub Pages repo of interactive tests for VTG English Center (pre-A1 to B2 and IELTS). Owner: Giang. Reply in English.

## Layout
- Existing files at the repo root (e.g. `VTG_A1_Progress_Test_6.html`) are already shared with students. NEVER rename, move or delete them: the links would break.
- New tests: `tests/<LEVEL>/<LEVEL>_Progress_Test_<NN>.html` (two-digit number). Other work: `assignments/`.
- `data/<LEVEL>_Progress_Test_<NN>.json`: the questions for each test. This is the source of truth.
- `template/`: the paper template. `tools/vocab-quiz/`: vocabulary quiz builder (`scripts/build_quiz.py`); a quiz file can have `words`, `grammar` (3-option items, type id `G`), or both.
- `/build-vocab <json>` (`.claude/commands/build-vocab.md`) validates a vocab/grammar JSON and builds it to `tests/<LEVEL>/<LEVEL>_Vocab_<Topic>.html`. Quiz JSON lives in `data/<LEVEL>_Vocab_<Topic>.json`.
- `tools/build_index.py` regenerates `index.html`. Run it after every new test.
- `/build-test <LEVEL> <N> <VERSION>` (`.claude/commands/build-test.md`) builds an Empower Progress Test end to end from Google Drive. `tools/check_progress_test.py` reads PDF text and checks a test JSON against the paper and answer key.

## Token rules (important, Pro plan)
- NEVER open built `.html` files or audio files. They can be several MB (base64 audio). Edit the JSON and rebuild instead.
- Do not write whole HTML pages by hand. Fill the template via the build scripts.
- Use `ls`, `grep -c` or `head -c 2000` to inspect a built file, never Read.

## Quiz design rules
- Match the level tightly: simple vocabulary, short sentences, scope = the lesson objectives. Do not go broader or harder.
- Every answer must be unique and every question must have exactly one correct answer. Distractors come from the same data set.
- Never invent exercises from a coursebook. If the needed page or answer key is missing, say which page to provide.
- If no answer key exists, derive answers from the audioscript/paper and flag any ambiguous item to Giang.

## Progress Test paper format
- One scrolling exam page, 5 parts, free navigation between questions.
- One total countdown (default 30 min) in a sticky top bar; warning colour near the end; auto-submit at zero. No per-question timer.
- Answers hidden until submission. Then show score, per-part breakdown and a full correction table.
- Anti-copy: block text selection, copy/cut, right-click, print and view-source shortcuts. Typing fields and the result-copy button must still work.
- Count tab switches and report them in the results sheet.
- Audio is embedded as a base64 data URI (no Drive links).
- iOS Safari: declare a light colour scheme and hardcode backgrounds to avoid black screens.

## Results
- Results go to the shared Google Sheet through the Apps Script endpoint (default is in `tools/vocab-quiz/scripts/build_quiz.py`). Send with `fetch`, `no-cors`, `Content-Type: text/plain;charset=utf-8`, JSON-stringified body.
- **Never submit to the live Sheet when testing.** Test only on a copy built with `"endpoint": ""` (or `build_quiz.py --no-send`), confirm with `grep` that the endpoint is empty, serve only that copy, and never finish a run on a page that has the live endpoint. A page built for publishing keeps the live endpoint and is never opened to test.

## Publishing
- Commit new files with a clear message (e.g. `Add A2 Progress Test 03`) and push to `main`. Ask Giang before pushing.
- After a push, give Giang the Pages link: `https://teachergiangvu.github.io/vtg-tests/<path>`.
- The repo is public: answers inside the HTML are visible to a determined student. Fine for practice; for graded tests, suggest server-side checking.

---
description: Build a Cambridge Empower Progress Test from Giang's Google Drive (e.g. /build-test A2 6 A)
argument-hint: <LEVEL> <test number> <version>   e.g. A2 6 A
---

Build Empower Progress Test **$1**, test **$2**, version **$3**. Full arguments: `$ARGUMENTS`.

Follow CLAUDE.md, especially the token rules: never Read a built `.html` or an audio file.

## Names
- LEVEL = `$1` in upper case (A1, A2, B1, B2). NN = `$2` with two digits (6 → 06). V = `$3` in upper case.
- Copies: `source/<LEVEL>_Progress_Test_<NN>_<V>.pdf` (paper), `source/<LEVEL>_Progress_Test_<NN>_<V>_AK.pdf` (answer key), `audio/<LEVEL>_Progress_Test_<NN>_<V>.mp3`.
- Data: `data/<LEVEL>_Progress_Test_<NN>.json`. Page: `tests/<LEVEL>/<LEVEL>_Progress_Test_<NN>.html`.
- Names have no version: title `VTG · <LEVEL> Progress Test <N>`, heading `<LEVEL> Progress Test <N>`, quiz_name `<LEVEL> Progress Test <N> (Empower)`.

## Stop and ask Giang first if anything is different
Use AskUserQuestion, and do not go on until Giang answers, whenever:
- the arguments are missing or don't look like `A2 6 A`;
- the source files can't be found, more than one different set is found, or a file is missing (paper, answer key, audio);
- the paper's cover does not say `<LEVEL> PROGRESS TEST` and `Test <N>`, or the key's cover does not say `<LEVEL> Unit Progress Test <N>`;
- the cover's minutes or question count are missing, or the parts are not "Part 1 listening + 4 more parts";
- a question page has embedded images, or any question mentions a picture, map, sign, table or layout. Don't guess those items;
- an answer in the key looks wrong or ambiguous, has more than one possible answer, or the key and your own answer disagree;
- a typed answer could reasonably be spelled another way (e.g. centre/center). Propose an `accept` list;
- a file with the same output name already exists in `source/`, `audio/`, `data/` or `tests/` (e.g. another version of the same test). Never overwrite;
- the checker or builder reports a problem you cannot fix by correcting your own typing.

## Steps (keep the task list updated)
1. **Find the files** (read-only). Look in `G:\My Drive\Teaching materials\IELTS\Cambridge Empower 2nd Edition\Cambridge Empower <LEVEL>` for a folder holding
   `Unit Progress Test <N> - Version <V>.pdf`, `Unit Progress Test <N> Answer Key - Version <V>.pdf`, `Unit Progress Test <N> Audio - Version <V>.mp3`
   (A2 Test 5 was in `…\Empower_2nd_A2_Tests\…\A\5`). If they're not there, search `G:\` for `Unit Progress Test <N> Audio - Version <V>.mp3`. The same set often also exists under `G:\Other computers\…`. Compare SHA256 hashes: if they're identical, use the My Drive copy; if not, ask.
2. **Check the covers.** Run `python tools/check_progress_test.py text "<paper.pdf>"` (works on the Drive path). Page 1 must say `<LEVEL> PROGRESS TEST` and `Test <N>`. Note `Time … minutes` and `There are … questions`. Check the key's page 1 the same way.
3. **Copy** the paper, key and mp3 to the names above (`source/` and `audio/` are git-ignored). Don't overwrite. Confirm each copy's hash matches the original.
4. **Read the paper** from the `text` output of the local copy. List the parts, question numbers, kinds and any image or layout issue. If the Drive folder has `Unit Progress Test <N> Audioscript - Version <V>.pdf`, read it too, to check the Part 1 answers. Don't copy it.
5. **Write `data/<LEVEL>_Progress_Test_<NN>.json`** in the shape of `data/A2_Progress_Test_05.json` (format in `data/README.md`):
   - `minutes` and the question total come from the cover. Add `audio`, the `kicker`/`footer` with the © year from the cover, and `nav` labels Nghe / Từ vựng / Viết từ / Bài đọc / Ngữ pháp, or similar.
   - Part 1 listening: `audio: true`, `layout: "col"`. The other MCQ parts use `layout: "row"`.
   - Blanks in sentences: `<span class='gap'></span>`. Passage blanks: `<span class="bl">(25) ……</span>`. Typed patterns: `s _ _ _ _ _   c _ _ _ _ _` (3 spaces between words). Typed-part rubric ends with `Gõ trọn vẹn cả cụm từ vào ô trả lời.`
   - Copy the paper's wording exactly. Only fix PDF-extraction glitches (split words like "ou tside", missing spaces before gaps) and list each fix for Giang.
   - First solve every question yourself, then compare with the key.
6. **Check:** `python tools/check_progress_test.py check data/<…>.json --paper source/<…>_<V>.pdf --key source/<…>_<V>_AK.pdf` must print `no mismatches`. If a line says a sentence wasn't found, compare it by eye.
7. **Build and index:** `python tools/build_progress_test.py data/<…>.json`, then `python tools/build_index.py`. Check the page with `grep` only:
   - no `__PLACEHOLDER__` left;
   - `data:audio/mpeg;base64` is present;
   - `TOTAL_SECONDS` and `TOTAL_Q` are right.
8. **Test scoring on a copy with sending turned off**, so no result reaches the real Google Sheet:
   - Copy the JSON to the scratchpad with `"endpoint": ""` and build it there with `-o`.
   - Serve that folder with `python -m http.server <port> --bind 127.0.0.1` in the background, and open it in the browser pane.
   - With `javascript_tool`, start the test, answer everything from the key (type one `accept` spelling if there is one) and submit. Expect a full score and full marks in every part. Then a blank attempt must score 0.
   - The clock must start at the right minutes, and the audio element must load (`readyState` ≥ 1, `duration` > 0).
9. **Preview for Giang.** Serve the repo root on 127.0.0.1 and open `tests/<LEVEL>/<…>.html` in the browser pane, on the start screen (name/class form). Bring that tab to the front and take a screenshot. Never submit on the real page. If you start it to show the paper, reload it afterwards so the start screen is back.
10. **Report and wait.** Give a short summary:
    - source folder, cover check, minutes and questions;
    - checker result;
    - scoring test result;
    - every item you're unsure about or fixed (Q numbers);
    - the uncommitted files.

    Then ask for OK with the wrap-up box. **Don't commit or push until Giang says OK.**
11. **After OK:**
    - Stop the preview servers.
    - Commit only `data/<…>.json`, `tests/<LEVEL>/<…>.html` and `index.html` with the message `Add <LEVEL> Progress Test <NN>`, ending with the attribution line.
    - Push to `main`, wait for GitHub Pages to return 200, and give the link `https://teachergiangvu.github.io/vtg-tests/tests/<LEVEL>/<LEVEL>_Progress_Test_<NN>.html`.
    - Remind Giang that answers inside the page are visible to a determined student.

---
description: Validate a vocab/grammar quiz JSON and build it into tests/<LEVEL>/ (e.g. /build-vocab data/A2_Vocab_Animals.json)
argument-hint: <json file>   e.g. data/A2_Vocab_Animals.json
---

Build the vocabulary/grammar quiz from **$ARGUMENTS** (one JSON file).

Follow CLAUDE.md, especially the token rules (never Read a built `.html`) and **never submit to the live Google Sheet when testing**.
Script: `tools/vocab-quiz/scripts/build_quiz.py`. JSON format: `tools/vocab-quiz/SKILL.md` (`words`, `grammar`, or both; `types`, `per_type`).

## Names
- LEVEL: top-level `"level"` in the JSON, else the file name `<LEVEL>_Vocab_<Topic>.json`. TOPIC: `"topic"`, else from the file name. LEVEL is one of pre-A1, A1, A2, B1, B2, IELTS (keep the case used by `tests/` folders).
- TOPIC becomes `Title_Case_With_Underscores` (letters, digits and underscores only).
- Output: `tests/<LEVEL>/<LEVEL>_Vocab_<TOPIC>.html`.

## Stop and ask Giang first (AskUserQuestion) if
- no argument, the file does not exist, or LEVEL / TOPIC cannot be worked out;
- the output file already exists. Never overwrite;
- validation reports a content problem you cannot fix by correcting your own typing (too few items, a grammar item with two plausible correct options, an answer that is wrong or ambiguous, vocabulary or grammar outside the level, a coursebook page or answer key that is missing);
- the JSON has `"endpoint"` set to anything but the default (confirm it is intended).

## Steps (keep the task list updated)
1. **Locate and name.** Read the JSON (it is data, not a built page). Work out LEVEL and TOPIC. Check the output path is free.
2. **Validate:** `python tools/vocab-quiz/scripts/build_quiz.py <json> --check`. It checks fields, `___` gaps, unique answers, enough items per part, and for every grammar item exactly 3 options, no duplicate options, and `answer` in range. Also read the grammar items yourself: each must have exactly one correct option for the level. Flag doubtful items to Giang.
3. **Build the real page:** `python tools/vocab-quiz/scripts/build_quiz.py <json> -o tests/<LEVEL>/<LEVEL>_Vocab_<TOPIC>.html`. It keeps the endpoint the JSON says (the live Sheet by default). This page is for students: **never open, serve or run it.**
4. **Index:** `python tools/build_index.py`.
5. **Test on a copy with sending turned off:**
   - `python tools/vocab-quiz/scripts/build_quiz.py <json> --no-send -o <scratchpad>/vocab_test/index.html`
   - `grep -c 'const ENDPOINT = ""'` on that copy must be 1. If not, stop.
   - Serve only that folder: `python -m http.server <port> --bind 127.0.0.1` (background), open it in the browser pane.
   - With `javascript_tool`: fill name and class, click start, then for each question click the option whose text equals `quiz[idx].correct` and call next. Expect full score; check that parts, question counts and part order match the config, and that a grammar question shows 3 options and its `note`. Run again answering wrongly: score 0. `lastPayload` must exist and no network request to `script.google.com` may appear (`read_network_requests`).
6. **Preview for Giang:** screenshot the start screen and one grammar question (if any) from the disabled copy. Front that tab. Stop the server when done.
7. **Summary, then wait.** Give: output path, counts (words / grammar), part order, seconds, endpoint status of the real page, validation result, test result, anything you flagged, and the uncommitted files (`data/<json>` if new, the new HTML, `index.html`). Ask for OK with the wrap-up box. **Do not commit or push until Giang says OK.**
8. **After OK:** commit only the JSON (if in `data/`), the new HTML and `index.html` with the message `Add <LEVEL> Vocab <TOPIC>`, ending with the attribution line. Ask before pushing. After a push, wait for GitHub Pages to return 200 and give `https://teachergiangvu.github.io/vtg-tests/tests/<LEVEL>/<LEVEL>_Vocab_<TOPIC>.html`. Remind Giang that answers inside the page are visible to a determined student.

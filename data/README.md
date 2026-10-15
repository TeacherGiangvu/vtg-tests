# data/

One JSON file per test, named like the output: `A2_Progress_Test_03.json` builds `tests/A2/A2_Progress_Test_03.html` with `python tools/build_progress_test.py data/A2_Progress_Test_03.json`. Full example: `A1_Progress_Test_06.json`.

```json
{
  "level": "A2",
  "title": "VTG · A2 Progress Test 3",
  "heading": "A2 Progress Test 3",
  "kicker": "VTG English Center · Cambridge English Empower",
  "quiz_name": "A2 Progress Test 3 (Empower)",
  "footer": "VTG English Center · Cambridge English Empower A2 Progress Test 3 · © UCLES 2016",
  "minutes": 30,
  "audio": "audio/A2_Progress_Test_03.mp3",
  "parts": [
    {
      "id": "part1", "label": "Part 1", "name": "Listening — Choose the best reply", "nav": "Nghe",
      "rubric": "Questions 1 – 6. ...",
      "audio": true, "kind": "mcq", "layout": "col",
      "qs": [ { "no": 1, "opts": ["...", "...", "..."], "correct": "C" } ]
    },
    {
      "id": "part3", "label": "Part 3", "name": "Word formation — Write the words", "nav": "Viết từ",
      "rubric": "...", "kind": "input",
      "qs": [ { "no": 13, "text": "My mother doesn't <span class='gap'></span> ...", "pattern": "h _ _ _   d _ _ _ _ _", "correct": "have dinner" } ]
    }
  ]
}
```

- Required: `level`, `title`, `parts`. Optional (with defaults): `heading` (title without "VTG ·"), `kicker` ("VTG English Center"), `quiz_name` (heading; the name shown in the Google Sheet), `footer`, `minutes` (30), `audio`, `endpoint` (default Sheet endpoint; `""` turns sending off).
- Part: `id`, `label`, `name`, `rubric`, `kind` (`mcq` or `input`); optional `nav` (short top-bar label), `audio: true`, `layout` (`col` or `row`), `passage` (`{title, html}`).
- MCQ question: `no`, `opts` (2–4), `correct` (letter), optional `text` (use `<span class='gap'></span>` for the blank). Input question: `no`, `text`, `pattern`, `correct`, optional `accept` (other spellings also marked correct, e.g. `["sports center"]`; the correction table still shows `correct`).
- Question numbers must run 1, 2, 3... across all parts. The builder checks this, the answer letters, duplicate options and the audio file, and builds nothing if there is a problem.
- `audio` is a path from the repo root. Put mp3s in `audio/` (git-ignored; the sound is embedded in the HTML).

Vocabulary quizzes use the schema in `tools/vocab-quiz/assets/example_words.json`.

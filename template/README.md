# Progress Test template

`progress_test_template.html` was made from `VTG_A1_Progress_Test_6.html`. Do not fill it by hand: write `data/<LEVEL>_Progress_Test_<NN>.json` and run

```bash
python tools/build_progress_test.py data/A2_Progress_Test_03.json
```

which writes `tests/A2/A2_Progress_Test_03.html`. Then run `python tools/build_index.py`.

Placeholders filled by the builder: `__TITLE__`, `__HEADING__`, `__KICKER__`, `__FOOTER__`, `__MINUTES__`, `__TOTAL_Q__`, `__NUM_PARTS__`, `__NAVPARTS__`, `__INTRO_EXTRA__`, `__QUIZ_NAME_JS__`, `__ENDPOINT_JS__`, `__AUDIO_SRC_JS__`, `__PARTS__`. The builder stops if the template contains a placeholder it does not know.

Audio is embedded as a base64 data URI (`AUDIO_SRC`), not a Drive link.

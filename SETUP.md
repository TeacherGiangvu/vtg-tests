# Setup: Claude Code + vtg-tests (about 15 minutes)

Your repo: https://github.com/TeacherGiangvu/vtg-tests

## 1. Install the tools (once)
1. Git: https://git-scm.com/downloads
2. GitHub CLI (`gh`): https://cli.github.com
3. Claude Code: follow the install steps at https://docs.claude.com (search "Claude Code quickstart").

## 2. Sign in (once)
```
gh auth login          # choose GitHub.com, HTTPS, log in with the browser
claude                 # then run /login and choose your Claude subscription (Pro)
```
If you ever set an `ANTHROPIC_API_KEY` environment variable, remove it, or Claude Code will bill that key instead of your Pro plan.

## 3. Clone the repo
```
cd ~/Documents          # or wherever you want it
gh repo clone TeacherGiangvu/vtg-tests
cd vtg-tests
```

## 4. Add the starter kit
Unzip `vtg-tests-starter.zip` and copy its contents INTO the cloned `vtg-tests` folder (merge, do not overwrite your existing HTML files). You should now have `CLAUDE.md`, `tools/`, `data/`, `template/`, `tests/`, `assignments/` next to your existing tests.

## 5. First session
```
cd vtg-tests
claude
```
Paste this as your first message:

> Read CLAUDE.md. Copy VTG_A1_Progress_Test_6.html into template/ as the Progress Test template (do NOT read the whole file, it has base64 audio; use grep/head to find the PARTS block, timer and title). Then write tools/build_progress_test.py so that data/<name>.json builds tests/<LEVEL>/<name>.html, move the audio into a separate file that the script injects, and run tools/build_index.py. Show me the plan before changing anything.

## 6. Every new test after that
> Build A2 Progress Test 03 from these answers [paste or attach], save the JSON in data/, build it, update the index, and show me the git diff. Wait for my OK before pushing.

## 7. Check GitHub Pages once
Repo on github.com > Settings > Pages: source should be the `main` branch (root). Your link format: `https://teachergiangvu.github.io/vtg-tests/<file>`.

## Rules of thumb for the Pro plan
- One focused task per session; start a new session for the next task.
- Run `/status` to see your usage.
- Keep using this claude.ai chat for reading Drive answer keys, drafting question banks and lesson decks.

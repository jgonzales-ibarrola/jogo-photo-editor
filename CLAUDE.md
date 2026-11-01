# CLAUDE.md

This repo is a local photo editor for iPhone HEIC / ProRAW (DNG) / JPG files, plus beginner photography guides.
The owner is learning photography with an iPhone Pro Max in the Philippines. Explain things in short, plain sentences.

## Running the tool

- Always run as `.venv\Scripts\python -m jogo ...` (PowerShell) or `.venv/Scripts/python -m jogo ...` (bash).
  Never call `jogo.exe`: Windows Smart App Control blocks the unsigned launcher.
- If an import fails with "Application Control policy has blocked this file", retry once; it usually passes.
- Photos go in `photos/in`, results land in `photos/out`. Never modify, move or delete files in `photos/in`.

## When the user asks to edit photos

0. Read docs/my-style.md first and follow it. After the user gives feedback on an edit
   ("too dim", "looks pixelated", "I like this one"), add it there: update "What I like/don't like"
   and add a row to the decision log. If the feedback reveals a tool problem, fix the code too.
   Default: do NOT generate `try` sheets or `grid` images (they cost tokens and aren't for posting).
   Only make them when the user asks ("compare looks", "show grid", "how should I have shot this").
1. If they don't say which look, pick it from docs/my-style.md. Only if the photo doesn't fit any saved
   preference (e.g. night, indoor, food), run `try` on one photo and recommend a preset in one sentence.
2. Run `edit` with that preset. Add sliders only for a clear problem (see docs/03-edits-explained.md, "Common problems").
2b. Decide on crop per photo (never one crop for a whole batch) with the checklist in
   docs/06-composition-and-crop.md. Use `--crop-zoom` + `--crop-pos "x,y"` to put the subject on a thirds line.
   Default for full-body travel shots: `--crop-pos bottom`. Then Read the final edited photos (not grids) to check nothing important
   was cut; if it was, redo that one photo. Say in one line why you cropped or didn't.
2c. Shooting tips ("how should I take this") only when the user asks, in words, not images.
2d. Put final post-ready photos in `photos/out/<batch>/post`. Suggest which to post, the carousel order
   and one caption idea, following docs/07-posting-guide.md. When the user reports results, log them there.
3. Report what auto-fix changed (the `auto:` lines) in plain words, and where the files were saved.
4. Full 48MP edits take ~20 s each. For many photos, run in the background, or offer `--preview` first.
5. You cannot view HEIC/DNG directly. To look at a photo, make a small JPG with `try`, or with `edit --preview -o <scratch dir>`.

## Code layout

- `src/jogo/cli.py` — commands (`edit`, `try`, `info`, `presets`)
- `src/jogo/files.py` — loading HEIC/DNG/JPG, saving with metadata, GPS stripping
- `src/jogo/auto.py` — auto analysis; every decision appends a plain-language note
- `src/jogo/adjust.py` — the edit pipeline (float32 RGB 0..1, tone curves via 65536-entry lookup tables)
- `src/jogo/settings.py` — `Settings` dataclass, preset and `jogo.toml` loading
- `src/jogo/presets/*.toml` — built-in presets; user presets live in `my-presets/`

## Rules for changes

- Slider signs follow Lightroom (+ = more/lighter). Range -1..1, exposure in EV.
- New slider: add the field to `Settings`, the name to `SLIDERS`, the step in `adjust.apply`, and a row in docs/02 and docs/03.
- Keep 48MP memory in mind (one float32 copy = ~580 MB). Work in place; do large blurs on downscaled copies.
- Run `.venv/Scripts/python -m pytest -q` after changes.
- Every editing or composition rule needs a source in docs/08-references.md. Research first, add the
  source there, then change code/presets. Follow the block flow and rule priority in
  docs/09-decision-flow.md: research default > scene rule > photo measurement > owner preference.
  Owner preferences (docs/my-style.md) are recorded but OFF by default; apply them only when asked.
  Exception: problems the owner reports (wrong colors on iPhone, blur, bad crops) are bugs; fix them.
- Keep docs short and plain. No hype. Update ROADMAP.md checkboxes when a feature ships.

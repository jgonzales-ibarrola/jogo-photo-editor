# Next: work in progress

Claude: read this at the start of every session. Update it when a step is done. Delete a section when it's finished.
Last updated: 2026-11-02.

## Where we are

Goal (owner): edits based on research and what most people/pros prefer, not only the owner's taste.
Rule priority and the 9-block edit flow: [docs/09-decision-flow.md](docs/09-decision-flow.md).
Sources and findings: [docs/08-references.md](docs/08-references.md).

Done on branch `research-decision-flow` (not merged to `main` yet):
- docs/08 references, docs/09 decision flow, rule priority (research first, owner taste off by default)
- `--crop-zoom`, per-photo composition crops
- `jogo score` (NIMA + MUSIQ + LAION). Finding: good for picking photos, can't judge grading
- Skin tone line check on detected faces (OpenCV 4.x, not 5)
- JPEG quality 95 (owner: best quality, size doesn't matter)

## In progress: FiveK study (roadmap item "Compare presets with FiveK")

What: 300 FiveK photos, each with raw input + edits by 5 pro photographers, balanced by scene.
Why: learn what pros do per scene (brightness, contrast, color, tint, shadow/highlight grade, skin)
and how close our looks are. It's for knowledge and rules, not for training an AI model.
Script: [research/fivek.py](research/fivek.py). Data: `research/data/fivek/` (git-ignored, research
license: never commit or republish the photos).

Download finished 2026-11-01 (300/300). `measure` started 2026-11-01 ~14:25 as its own Windows
process, ~35 s per photo, ~3 hours. It saves after each photo and resumes when rerun.

```powershell
Get-Content research/data/fivek/measure.log -Tail 3        # progress: [n/300]
# Running? (if not, and the log stops before 300, just restart it: it resumes)
Get-CimInstance Win32_Process -Filter "Name='python.exe'" | Where-Object CommandLine -match 'fivek.py measure'
Start-Process .venv\Scripts\python.exe -ArgumentList 'research/fivek.py','measure' -WindowStyle Hidden -RedirectStandardOutput research/data/fivek/measure.log -RedirectStandardError research/data/fivek/measure.err
```

### Steps

1. [x] Download 300 photos (fetch checks file size and handles names with spaces).
2. [x] `measure` finished 2026-11-01 17:25 (300/300). `report` fixed (dusk/unknown time were
       lumped into "night"). Output saved to `research/data/fivek/report.txt`.
3. [x] Findings written in docs/08 ("What we measured"). Short version: pros are brighter
       (+8–11 L*), more contrast, more color on nature, and remove orange lamp color at night/indoors.
       Auto exposure caps at ~+1 EV (`auto.py` line ~60): likely the main brightness gap.
4. [x] 2026-11-02: auto target 0.42 -> 0.47 (pros put normal day photos at L* 50); `night` uses full
       auto (night distance 9.95 -> 5.86). FiveK's per-scene best looks are written under the scene
       table in docs/09, but the table is kept: the pros' looks are more colorful, which conflicts
       with the owner's "too vivid" bug. Try `bright` (indoor people) and `airy` (outdoor people) on
       real photos when the owner gives iPhone feedback.
4b. [x] First FiveK rules are in `auto.py` (2026-11-02, tests pass): exposure 90% of the way up to
       +2.5 EV, highlight guard (stop at L* 90), vibrance for dull photos, stronger lamp-color removal
       at night. Checked on all photos in `photos/in`: only small changes, except 0443 (white shirt,
       black speaker), which the guard now saves. FiveK check: `natural` distance 6.25 -> 4.18.
       Remaining gaps (docs/08): still ~9 L* darker, indoor/night too warm, highlights slightly green.
5. [ ] Build the adaptive color grade (roadmap item, docs/09 block 4): from the FiveK data, fit simple
       rules like "pros add less color when the photo is already colorful", "pros brighten dark photos
       by X". Use input stats -> expert output stats (simple linear fits per stat, per scene).
       Put them in auto.py as plain rules with notes, cite docs/08. Add tests.
6. [ ] Update docs/09 status marks, ROADMAP checkboxes, commit, then offer to merge to `main`.

### Things to know
- The 5 experts disagree a lot (one goes cool, one warm). Use their average, not one expert.
- Experts' TIFFs are ProPhoto RGB; the script converts them to sRGB (checked by eye, looks right).
- FiveK inputs are Nikon/Canon raws (decoded with our rawpy path), not iPhone ProRAW. Numbers about
  brightness/color targets transfer; the input "baseline" is flatter than an iPhone photo.

## Not started
- Skin protection for temperature (docs/09 block 5)
- Auto scene detection and auto crop (docs/09 blocks 2 and 6), now done by Claude by eye
- Owner hasn't given iPhone feedback on naga-test or cagsawa-family edits yet (my-style.md)

# Next: work in progress

Claude: read this at the start of every session. Update it when a step is done. Delete a section when it's finished.
Last updated: 2026-11-01.

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

The download runs as its own Windows process (started 2026-11-01 ~12:50). MIT's server is slow,
about 1.2 MB/s, so 300 photos take ~16 hours. It resumes where it stopped.

```powershell
.venv\Scripts\python research/fivek.py status          # progress
# If it's not running any more (PC restarted) and status < 300, restart it:
Start-Process .venv\Scripts\python.exe -ArgumentList 'research/fivek.py','fetch','--n','300','--workers','8' -WindowStyle Hidden -RedirectStandardOutput research/data/fivek/fetch.log -RedirectStandardError research/data/fivek/fetch.err
# Check if it's running:
Get-CimInstance Win32_Process -Filter "Name='python.exe'" | Where-Object CommandLine -match 'fivek.py fetch'
```

### Steps

1. [ ] Download: at ~100 complete, do steps 2–3 once (first look); at 300, redo them.
2. [ ] `python research/fivek.py measure` then `report` (measure skips unfinished photos).
       Not run yet on real data: check it works on a few photos first, fix bugs.
3. [ ] Write findings into docs/08 ("What we measured"): per scene, expert average vs input vs our
       looks; which look is closest; where we're off (too bright? too colorful? wrong tint?).
4. [ ] Update the scene -> look table in docs/09 from the data, and tune presets toward the expert
       average. Re-run `report` to confirm they got closer. Run pytest.
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

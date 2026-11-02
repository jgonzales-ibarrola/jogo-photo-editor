# Next: work in progress

Claude: read this at the start of every session. Update it when a step is done. Delete a section when it's finished.
Last updated: 2026-11-02.

## Where we are

Goal (owner): edits based on research and what most people/pros prefer, not only the owner's taste.
Rule priority and the 9-block edit flow: [docs/09-decision-flow.md](docs/09-decision-flow.md).
Sources and findings: [docs/08-references.md](docs/08-references.md).

Merged to `main` 2026-11-02 (branch `research-decision-flow`): references and decision flow,
`--crop-zoom`, `jogo score`, skin tone line check, JPEG 95, and the FiveK study with the rules
it gave `auto.py` (brighter target, highlight guard, vibrance for dull photos, white balance
2/3 of the way in any light, warmth-only). `natural` distance to the pros: 6.25 -> 3.35.

## Next: adaptive color grade (roadmap item, docs/09 block 4)

Weakest FiveK scenes: indoor people and night indoors (distance ~10-13). Fit simple rules from
input stats -> expert output stats per scene ("pros add less color when the photo is already
colorful"), put them in `auto.py` with notes, cite docs/08, add tests.

Check a change in ~3 min: `.venv/Scripts/python research/fivek.py check --fast --looks natural,night`
(lower `dist` = closer to the pros; compares old and new on the same 100 photos).

Also open:
- Highlights still a little green (a* -1.5 vs pros +0.4). Suspect: the per-channel rolloff in
  `adjust._tone_lut`.
- Try `bright` (indoor people) and `airy` (outdoor people) on real photos, after iPhone feedback.
  FiveK prefers them, but they are more colorful than the owner liked (docs/09, under the table).

### Things to know (FiveK)
- Data: `research/data/fivek/` (git-ignored, research license: never commit or republish the photos).
- The 5 experts disagree a lot (one goes cool, one warm). Use their average, not one expert.
- FiveK inputs are Nikon/Canon raws, darker and flatter than an iPhone photo. Targets transfer;
  the size of the gap doesn't. Don't chase brightness for very dark raws.
- Our gray-area detector counts some beige things as gray on the pros' photos: judge white balance
  ideas by the `check` distance, not by the detector alone.

## Not started
- Skin protection for temperature (docs/09 block 5)
- Auto scene detection and auto crop (docs/09 blocks 2 and 6), now done by Claude by eye
- Owner hasn't given iPhone feedback on naga-test or cagsawa-family edits yet (my-style.md).
  Since 2026-11-02 auto edits are a bit brighter and warm photos less orange: re-edit before asking.

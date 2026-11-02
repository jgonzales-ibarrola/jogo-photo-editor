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

Merged and pushed 2026-11-02 (branch `adaptive-grade`):
- `brightness` slider (midtone bump). Auto lifts midtones when the highlight guard or neon rule
  holds exposure back (0.5 per EV, max +0.5; more bleached a face on iPhone 0443).
- Neon rule stops exposure where colored lights clip, instead of +0.2 for any colorful area.
- Gray world white balance for strongly orange rooms with no gray, day or night.
- FiveK `check --fast`: `natural` 3.35 -> 2.18, indoor people 7.36 -> 6.67.

## Next: check each scene's look against FiveK

`fivek.py check --scene "<scene>" --looks a,b,c` compares looks on one scene (names as in the report).
Done: indoor people -> `bright` (5.00 vs `natural` 7.87; auto alone can't remove that warmth because
beige walls read as gray, and a stronger white balance hurt other scenes).
Done: `night` got less orange/yellow saturation (night indoors 8.63 -> 6.05, outdoors 5.12 -> 2.73).
Done: `gold` tuned toward the pros, greens still muted (outdoor people 7.44 -> 5.68; `airy` 3.96).
Done: `tropical` tuned the same way (9.24 -> 6.51).
Done: `amber` 5.38 -> 2.74, `beach` 5.35 -> 3.63, `landscape` 4.16 -> 3.53; `food` already 2.43.
All scene-table looks are now tuned against FiveK. Style looks are left as they are on purpose.
Waiting on owner (2026-11-02), one iPhone review of everything:
- `photos/out/compare-gold-airy`: 3 ATV photos, new `gold` vs `airy` (outdoor people look).
- `photos/out/iphone-check`: indoor people `bright` (0039, 0396), food `food` (0388), white shirt `gold` (0443).
Which looks better on the iPhone? Is skin too yellow? Log the answer in my-style.md.

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

# Roadmap

Two tracks that grow together: **the tool** and **you**.

## The tool

### v0.1 — now
- [x] HEIC, ProRAW (DNG), JPG input; JPG / HEIC / 16-bit TIF output
- [x] Auto-fix with plain-language explanations
- [x] 10 presets + your own presets in `my-presets/`
- [x] `try` comparison sheet, `info` photo check-up
- [x] Crop to social ratios, resize, GPS removal

### v0.2 — better results
- [ ] Faster full-size edits (target: under 8 s per 48MP photo)
- [ ] Better ProRAW decoding (use the DNG's own tone curve and Apple's gain maps)
- [ ] Auto straighten using the horizon
- [ ] Skin-tone protection for vibrance and temperature
- [ ] Before/after side-by-side for one photo

### v0.3 — more control
- [ ] Tone curve and per-color (HSL) adjustments: e.g. "make only the sea more turquoise"
- [ ] Sky detection: darken/enhance sky separately from the ground
- [ ] Subject detection: brighten faces separately
- [ ] Export presets as Lightroom (.xmp) so your look works on your phone too

### v0.4 — easier to use
- [ ] Simple local web page: drag photos in, slide sliders, see the result live
- [ ] Watch folder: drop photos in `photos/in`, edits appear automatically

## You — a learning path

| Stage | Goal | Do this |
|---|---|---|
| **1. Beginner** (weeks 1–4) | Stop making the common mistakes | Turn on Grid + Level. Read [04](docs/04-iphone-settings.md). Use `natural` on everything. |
| **2. Composer** (months 1–2) | Photos look intentional | Practice one composition rule per week from [05](docs/05-shooting-guide-philippines.md). Use `try` and notice which presets you pick. |
| **3. Light reader** (months 2–4) | Shoot at the right time | Golden hour and blue hour every week. Use exposure lock. Start using ProRAW for hard light. |
| **4. Editor** (months 4–6) | Your own look | Read [03](docs/03-edits-explained.md). Build 2–3 presets in `my-presets/`. Edit with `--no-auto` sometimes, to learn by hand. |
| **5. Photographer** (6+ months) | A body of work | Pick a project (e.g. "jeepneys of my city", "Philippine churches"). Shoot 30 photos, keep the best 10. Print one. |

When you finish a stage, open an issue or tell Claude what you want next. The tool grows with what you need.

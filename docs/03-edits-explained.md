# 03 — Edits explained

What each edit does, when to use it, and what goes wrong if you overdo it.
The same words are used in Lightroom, Snapseed and the iPhone Photos app, so this carries over.

## The order to think in

1. **Light** first: exposure, highlights, shadows, whites, blacks.
2. **Color** second: temperature/tint, then vibrance.
3. **Detail** last: clarity, sharpening, noise reduction.
4. **Framing** anytime: crop.

Auto-fix does step 1 and the color-cast part of step 2. Presets do the rest.

---

## Light

**Exposure** — overall brightness.
Use when the whole photo is too dark or too bright.
+1 doubles the light, −1 halves it.
Too much: bright areas turn pure white and lose all detail.

**Highlights** — only the bright areas (sky, clouds, white walls, shiny skin).
Pull it **down** when the sky looks white instead of blue.
Too much: skies turn gray and flat.

**Shadows** — only the dark areas (faces in shade, under trees, inside a room).
Push it **up** when you can't see details in the dark parts.
Too much: the photo looks flat and fake (the "HDR look"), and grain appears.

**Whites** — the very brightest point. **Blacks** — the very darkest point.
Small moves set the "punch" of the photo. Deeper blacks = richer. Lifted blacks = faded/matte film look.

**Contrast** — the gap between dark and bright.
More = bold and punchy. Less = soft and calm.
Too much: faces get harsh, shadows go solid black.

> Rule of thumb: the Philippine midday sun creates **too much** contrast already.
> For those photos, lower highlights and raise shadows instead of adding contrast. The `beach` preset does this.

## Color

**White balance (temperature + tint)** — makes white things look white.
Indoor lights make photos orange. Shade makes them blue. Fluorescent lights can make them green.
Temperature fixes orange↔blue. Tint fixes green↔magenta.
Don't "fix" sunsets: the orange is the point. Use `golden-hour`, which turns auto white balance off.

**Vibrance** — boosts the dull colors more than the strong ones, and goes easy on skin.
This is the safe color slider. Use it first.

**Saturation** — boosts every color equally.
Too much: skin turns orange, skies turn neon. Usually keep it at 0. Use −1 for black and white.

## Detail

**Clarity** — contrast in mid-size details (texture of rocks, wood, clothes, clouds).
+ for landscapes, architecture, street. − for skin (portraits).
Too much: crunchy, gritty look with dark outlines.

**Sharpening** — makes edges crisper.
A little always helps. Too much: white outlines around edges, grainy skies.

**Noise reduction** — removes grain and colored speckles.
Needed for night and indoor shots. Too much: skin and walls look like plastic.

**Vignette** — darkens the corners so the eye goes to the middle.
Subtle (0.1–0.2) for portraits and food. Avoid on landscapes with clean skies.

## Framing

**Crop** — cut away distractions and pick a shape.
With 48MP you can crop a lot and still have a sharp photo.
Shapes: `4:5` Instagram feed, `9:16` Stories/Reels/TikTok, `1:1` square, `16:9` wide screens, `3:2` classic.

---

## Formats in one line each

- **HEIC**: iPhone's normal format. Small file, good quality, some editing room.
- **ProRAW (DNG)**: raw sensor data plus Apple's processing. Biggest editing room. Huge files.
- **JPG**: works everywhere. Least editing room. Use it for the **final** photo you share.
- **TIF (16-bit)**: big, no quality loss. Use it if you'll edit further in another app.

## Common problems and the fix

| Problem | Fix |
|---|---|
| Sky is white | `--highlights -0.5` |
| Face in shadow | `--shadows 0.4` |
| Photo looks gray / hazy | `--blacks -0.3 --contrast 0.2` |
| Too orange (indoor) | auto-fix usually handles it; else `--temperature -0.2` |
| Too blue (shade, overcast) | `--temperature 0.2` |
| Colors look dull | `--vibrance 0.3` |
| Grainy night photo | `--preset night` or `--noise-reduction 0.6` |
| Skin looks rough | `--preset portrait` or `--clarity -0.2` |

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

**Color grading** — tint the shadows one color and the highlights another. This is what gives
movies and Instagram creators a recognizable "look". It changes the mood, not the brightness.

- `--grade-shadows 0..1` + `--grade-shadows-hue DEG` — how strong, and which color, in the dark parts.
- `--grade-highlights 0..1` + `--grade-highlights-hue DEG` — the same for the bright parts.
- Hue is a position on the color wheel: **0** red, **30** orange, **50** golden yellow, **120** green,
  **180** cyan/teal, **210** blue, **270** purple, **330** pink.

Classic combinations:

| Look | Shadows | Highlights | Preset |
|---|---|---|---|
| Cinematic / teal-orange | teal (190–200) | orange (30–40) | `cinematic` |
| Tropical / sunny | turquoise (180–190) | golden (45–55) | `tropical` |
| Film / nostalgic | green-teal (160–175), weak | warm (40–50), weak | `film` |
| Bright and clean | — | warm glow (45), weak | `airy` |
| Cool, moody | blue (210–220) | none or slight blue | — |

Keep it subtle: 0.2–0.4. If skin turns green or orange, it's too much.

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

### When to crop

- **Something distracting at the edge**: a stranger's arm, a trash bin, a pole, a car. Cut it out.
- **The subject is too small**: lots of empty ground or sky that adds nothing. Crop closer so the subject fills more of the frame.
- **The horizon is crooked**: straighten it (crop removes the uneven corners). The tool can't straighten yet; use the iPhone Photos app for that.
- **The subject is dead center and the photo feels static**: crop so the subject sits on a third line (see [05](05-shooting-guide-philippines.md)).
- **The platform needs a shape**: `4:5` for the Instagram/Facebook feed takes the most screen space. `9:16` for Stories and Reels.
- **Too much "nothing" at the top**: a big plain sky above a person's head. Trim it, but leave some room above the head.

### When NOT to crop

- **The photo already works.** If nothing distracts and the subject is clear, leave it. Cropping for the sake of it is a common beginner habit.
- **Cutting at joints**: never crop through ankles, knees, wrists, elbows or the neck. It looks like the person was chopped. Crop mid-thigh or mid-arm instead, or keep the whole body.
- **Cutting off what makes the photo**: a hand reaching for something, a pose, the top of a building, a shadow that tells the story. Check the edges after cropping.
- **The place matters**: landmark and travel photos need the landmark *and* some surroundings (mountain, sky). Cropping too tight makes it "a person in front of a wall".
- **Small or old photos**: a 10MP or smaller photo gets soft fast if you crop hard. Crop gently, or not at all.
- **Before you edit, if you're unsure**: keep the full photo and make cropped copies. Your originals in `photos\in` are never changed anyway.

### Leave room in the right places

- **Looking room**: if a person looks or points to one side, leave more space on that side.
- **Walking room**: leave space in front of a moving person or vehicle, not behind.
- **Headroom**: a small gap above the head. Not a big empty sky, and not touching the edge.
- **Feet**: in full-body shots, keep both feet fully in the frame, with a little ground below them.

### How the tool crops

`--crop 4:5` cuts equally from both sides by default. Use `--crop-pos bottom` (or `top`, `left`, `right`)
to keep that side and cut from the other. Check the result with `python -m jogo grid <photo> --crop 4:5`.
Grids, techniques and the full crop checklist: [06 Composition and crop](06-composition-and-crop.md).

**Example (Cagsawa photos, 2026-10-30)**: the original 3:4 shape was cropped to 4:5 for Instagram.
It only removed a thin strip top and bottom, and the hand on the tower top and both feet stayed in, so it was safe.
A tighter crop (e.g. waist up) would have lost the low-angle "giant beside the tower" effect, which is what makes that photo.

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

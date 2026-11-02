# 02 — Tool reference

All commands start with `python -m jogo`. Add `--help` to any command to see its options.

## How an edit is built

Every edit is three layers, added together:

1. **Auto-fix**: looks at the photo and fixes exposure, highlights, shadows, blacks and color cast.
2. **Preset**: the look (e.g. `vivid` adds contrast and color).
3. **Your sliders**: anything you type, like `--exposure 0.3`.

So `--preset beach --shadows 0.2` means "auto-fix, plus the beach look, plus 0.2 more shadows".

## Commands

### `edit` — edit photos and save copies

```
python -m jogo edit [files or folders] [options]
```

No files given → uses every photo in `input_dir` (default `photos\in`).
Output name: `<original name>_<preset>.<format>`, e.g. `IMG_0412_vivid.jpg`.

| Option | What it does |
|---|---|
| `-p, --preset NAME` | Which look to use. Default: `natural`. |
| `-o, --out FOLDER` | Where to save. Default: `photos\out`. |
| `-f, --format jpg\|heic\|tif` | `jpg`: works everywhere. `heic`: about half the size, same quality. `tif`: 16-bit, for editing further in another app. |
| `-q, --quality 1-100` | JPG/HEIC quality. Default 95: best quality, full color detail. |
| `--crop RATIO` | Center crop. `4:5` Instagram portrait, `1:1` square, `16:9` wide/YouTube, `9:16` Stories/Reels, `3:2` classic photo. |
| `--crop-pos POS` | Which part the crop keeps: `center`, `top`, `bottom`, `left`, `right`, or `"x,y"` (0–1). See [06](06-composition-and-crop.md). |
| `auto_skin` (preset/toml) | `true` by default. After the look, faces are found and their skin hue is moved half way to the skin tone line (max 6°). |
| `--crop-zoom N` | Crop tighter. `0.8` keeps 80% of the width and height. With `--crop-pos "x,y"` it moves the subject onto a thirds line. Default `1`. |
| `--resize PIXELS` | Longest side in pixels. `2048` for Facebook/Instagram. `0` keeps full size. |
| `--preview` | Fast 2048px version. Use to check a look before the slow full-size edit. |
| `--no-auto` | Skip auto-fix. Only the preset and your sliders are applied. |
| `--keep-location` | Keep GPS location in the saved file (it's removed by default). |
| `--flat-raw` | ProRAW only. Decode the raw data instead of starting from Apple's finished photo inside the DNG. Flatter; use only to rescue blown or very dark shots. |
| `--exposure N` … `--vignette N` | Sliders. See below. |

### `try` — compare every preset

```
python -m jogo try photos\in\IMG_0412.HEIC
```

Saves `IMG_0412_compare.jpg`: the original plus every preset, side by side, small size.

### `grid` — composition guides

```
python -m jogo grid photos\in\IMG_0412.HEIC --crop 4:5 --crop-pos bottom
```

Draws rule-of-thirds (white), golden-ratio (yellow) and diagonal (cyan) lines on a small copy.
With `--crop`, the part that would be cut is darkened. Pick lines with `--guides thirds,golden`.
How to read it: [06 Composition and crop](06-composition-and-crop.md).

### `score` — how much most people would like it

```
python -m jogo score photos\out\cagsawa-family\post --vs photos\in --csv scores.csv
```

Scores each photo 1–10 with three models trained on human ratings (NIMA, MUSIQ, LAION; see
[08](08-references.md)), best first. `--vs` compares each edit with its original. Differences under
0.15 are a tie. Good for choosing which photos to post; it barely notices small grading changes.
Needs the extra install: `.venv\Scripts\python -m pip install -e .[score]` (about 1 GB).

### `info` — photo check-up

```
python -m jogo info photos\in\IMG_0412.HEIC
```

Shows camera, lens, shutter speed, aperture, ISO, and whether GPS is in the file.
Then shows brightness stats and what auto-fix would change. Use this to learn from your own shots:
if many photos say "Photo is dark", you can fix that in the camera next time (see [04](04-iphone-settings.md)).

### `presets` — list presets

```
python -m jogo presets
```

## Sliders

All sliders go from **-1 to +1**. **0 = no change**. Exposure is the exception: it's in stops (EV).
Start small: 0.1 to 0.3 is a visible change. Same sign convention as Lightroom.

| Slider | + does | − does |
|---|---|---|
| `--exposure` | Brighter. +1 = twice as bright. | Darker. |
| `--temperature` | Warmer (orange). | Cooler (blue). |
| `--tint` | More magenta. | More green. |
| `--contrast` | Darks darker, brights brighter. | Flatter, softer. |
| `--highlights` | Brighter bright areas. | Recovers detail in bright sky, clouds, white shirts. |
| `--shadows` | Shows detail in dark areas. | Deeper, moodier shadows. |
| `--whites` | Brightest parts brighter (can turn pure white). | Brightest parts dimmer. |
| `--blacks` | Faded, matte look. | Deeper, richer blacks. |
| `--clarity` | Crisper texture, more "pop". | Softer, dreamy (good for skin). |
| `--vibrance` | Boosts dull colors, protects already-strong ones. | Mutes dull colors. |
| `--saturation` | Boosts all colors equally. | Removes color (-1 = black and white). |
| `--sharpen` | Sharper edges. Only 0 to 1. | — |
| `--noise-reduction` | Cleans grain/color speckles (night shots). Only 0 to 1. | — |
| `--vignette` | Darker corners, draws the eye to the center. | Lighter corners. |
| `--grade-shadows` | Tints dark areas with `--grade-shadows-hue`. Only 0 to 1. | — |
| `--grade-midtones` | Tints the middle tones with `--grade-midtones-hue`. Only 0 to 1. Keep small: skin lives here. | — |
| `--grade-highlights` | Tints bright areas with `--grade-highlights-hue`. Only 0 to 1. | — |
| `--<color>-hue` | Moves that color toward the next one on the wheel (green → aqua). | Toward the previous one (green → yellow). |
| `--<color>-sat` | That color only gets stronger. | That color only gets duller (−1 = gray). |
| `--<color>-lum` | That color only gets lighter. | That color only gets darker. |

`<color>` is one of `red`, `orange`, `yellow`, `green`, `aqua`, `blue`, `purple`, `magenta` (the Color Mixer / HSL panel).
Example: `--green-sat -0.3 --blue-lum -0.2`. Grays and whites are never changed by these.
Presets can also set `protect_skin` (0..1, default 0.7): how much vibrance and color grading skip skin tones.

The two hue options take a color-wheel angle (0–360) and replace the preset's hue instead of adding to it.
Color grading explained: [03](03-edits-explained.md).

Plain explanations with "when to use": [03 Edits explained](03-edits-explained.md).

## Preferences — `jogo.toml`

The file `jogo.toml` in this folder holds your defaults. Edit it with any text editor.
Command-line options always win over this file.

| Setting | Default | Meaning |
|---|---|---|
| `preset` | `"natural"` | Preset used when you don't pass `--preset`. |
| `format` | `"jpg"` | Output format. |
| `quality` | `95` | JPG/HEIC quality. |
| `output_dir` | `"photos/out"` | Where edited photos go. |
| `input_dir` | `"photos/in"` | Where `edit` looks when you don't name files. |
| `resize` | `0` | Long edge in pixels, `0` = full size. |
| `crop` | `""` | Default crop ratio, `""` = none. |
| `crop_pos` | `"center"` | Default crop position. |
| `strip_location` | `true` | Remove GPS location from saved photos. |
| `keep_metadata` | `true` | Keep date, camera, lens, ISO in saved photos. |

## Presets

| Preset | Use for |
|---|---|
| `natural` | Anything. Safe default: fixes the photo, adds a little color. |
| `vivid` | Travel, festivals, jeepneys, markets. Strong color and contrast. |
| `landscape` | Mountains, rice terraces, big skies. Recovers sky, adds depth. |
| `beach` | Midday sun on sand and water. Tames glare, keeps blue water. |
| `golden-hour` | Sunrise/sunset. Keeps the warm light (auto white balance is off). |
| `overcast` | Cloudy and rainy-season days. Adds warmth and contrast. |
| `portrait` | People. Softer skin, gentle warmth, slight vignette. |
| `food` | Food. Warmer, richer, a bit of texture. |
| `night` | Night scenes. Brightens like pro editors (FiveK), protects lights, cleans noise. |
| `bw` | Black and white with punch. Street and portraits. |
| `airy` | Bright, clean, cheerful. Soft contrast, warm glow. |
| `tropical` | Sunny Philippines: turquoise shadows, golden highlights. |
| `cinematic` | Movie look: teal shadows, warm highlights. Dramatic. |
| `film` | Soft film: faded blacks, muted warm colors. |
| `amber` | Like the iPhone Amber style: warm amber, deep rich contrast. Streets, buildings. |
| `gold` | Like the iPhone Gold style: warm golden glow, a bit brighter. Travel, landmarks, people. |
| `rose-gold` | Like the iPhone Rose Gold style: warm with a soft pink-red. Portraits, skin. |
| `editorial` | Clean professional travel look: olive greens, teal-blue sky, warm highlights, natural skin. |
| `bright` | Like the iPhone Bright style: lighter, more vivid, clean blacks. Everyday. |

### Your own presets

Save a `.toml` file in `my-presets\`. The file name becomes the preset name.

```toml
# my-presets\manila-street.toml
description = "Warm, contrasty, slightly faded."
temperature = 0.1
contrast = 0.3
blacks = 0.15
vibrance = 0.2
sharpen = 0.3
```

Then: `python -m jogo edit --preset manila-street`.
Besides the sliders, a preset can set `auto = false` (no auto-fix), `auto_wb = false` (keep the original colors)
and `auto_strength = 0.5` (apply only half of the auto fix).

## Files it reads

| Type | From iPhone setting | Notes |
|---|---|---|
| `.HEIC` | HEIF / HEIF Max | Normal iPhone photo. |
| `.DNG` | Apple ProRAW | Most editing room. Huge files (~50–100 MB at 48MP). |
| `.JPG` | Most Compatible | Works, least editing room. |
| `.PNG`, `.TIF` | — | Work too. |

Results are saved in sRGB, the standard web color space. iPhone photos are Display P3, which
Windows often ignores and the iPhone shows more saturated, so a P3 file looks different on each.
sRGB looks the same on Windows, iPhone, Instagram and Facebook.

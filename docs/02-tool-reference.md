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
| `-q, --quality 1-100` | JPG/HEIC quality. 92 is visually identical to 100 at half the file size. |
| `--crop RATIO` | Center crop. `4:5` Instagram portrait, `1:1` square, `16:9` wide/YouTube, `9:16` Stories/Reels, `3:2` classic photo. |
| `--resize PIXELS` | Longest side in pixels. `2048` for Facebook/Instagram. `0` keeps full size. |
| `--preview` | Fast 2048px version. Use to check a look before the slow full-size edit. |
| `--no-auto` | Skip auto-fix. Only the preset and your sliders are applied. |
| `--keep-location` | Keep GPS location in the saved file (it's removed by default). |
| `--exposure N` … `--vignette N` | Sliders. See below. |

### `try` — compare every preset

```
python -m jogo try photos\in\IMG_0412.HEIC
```

Saves `IMG_0412_compare.jpg`: the original plus every preset, side by side, small size.

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

Plain explanations with "when to use": [03 Edits explained](03-edits-explained.md).

## Preferences — `jogo.toml`

The file `jogo.toml` in this folder holds your defaults. Edit it with any text editor.
Command-line options always win over this file.

| Setting | Default | Meaning |
|---|---|---|
| `preset` | `"natural"` | Preset used when you don't pass `--preset`. |
| `format` | `"jpg"` | Output format. |
| `quality` | `92` | JPG/HEIC quality. |
| `output_dir` | `"photos/out"` | Where edited photos go. |
| `input_dir` | `"photos/in"` | Where `edit` looks when you don't name files. |
| `resize` | `0` | Long edge in pixels, `0` = full size. |
| `crop` | `""` | Default crop ratio, `""` = none. |
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
| `night` | City lights. Stays dark, cleans noise, protects lights. |
| `bw` | Black and white with punch. Street and portraits. |

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
| `.HEIC` | HEIF / HEIF Max | Normal iPhone photo. Colors (Display P3) are kept exactly. |
| `.DNG` | Apple ProRAW | Most editing room. Huge files (~50–100 MB at 48MP). |
| `.JPG` | Most Compatible | Works, least editing room. |
| `.PNG`, `.TIF` | — | Work too. |

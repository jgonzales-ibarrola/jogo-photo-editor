# 09 — Decision flow: how each photo gets its edit

Every photo goes through the same blocks. Each block measures the photo and decides what to change
and what to leave alone. Rules come from research ([08](08-references.md)), not from one person's taste.

Legend: `[x]` built   `[~]` partly built / done by Claude by eye   `[ ]` planned

## Rule priority

```
  1. RESEARCH DEFAULT      what most people + most pros prefer           (docs/08)   <- always on
  2. SCENE RULE            what this kind of photo needs (night, food...)  (block 2)   <- always on
  3. PHOTO MEASUREMENT     what this exact photo needs (cast, exposure)    (block 3)   <- always on
  4. OWNER PREFERENCE      personal taste                                  (my-style)  <- off by default,
                                                                                         only when asked
```

## The flow

```
                         ┌──────────────────────────┐
                         │  INPUT  HEIC / DNG / JPG │
                         └────────────┬─────────────┘
                                      │
                    ┌─────────────────▼──────────────────┐
 [x] BLOCK 1        │  LOAD                              │  ProRAW -> Apple's finished photo
     files.py       │  convert to sRGB, read EXIF        │  + BaselineExposure. HEIC -> sRGB.
                    └─────────────────┬──────────────────┘
                                      │
                    ┌─────────────────▼──────────────────┐
 [~] BLOCK 2        │  SCENE: what is this photo?        │  today: Claude looks at a thumbnail
     Claude now,    │                                    │  planned: auto (EXIF time, ISO,
     auto later     │  light:   sun / cloud / shade /    │  sky %, skin %, neon %, faces)
                    │           indoor / night / neon    │
                    │  subject: people / face / food /   │
                    │           building / landscape /   │
                    │           detail                   │
                    └─────────────────┬──────────────────┘
                                      │  scene -> look table (below)
                    ┌─────────────────▼──────────────────┐
 [x] BLOCK 3        │  MEASURE + BASE FIX (auto.py)      │  research: fix the base first
     auto.py        │                                    │
                    │  middle brightness < target? ──yes─┼─> exposure up (max +1.5 EV)
                    │        │                           │     BUT neon/colored lights > 1%
                    │        │                           │     -> cap +0.2 EV (keep lights sharp)
                    │  very bright (median > 0.68)? ─yes─┼─> exposure down a little
                    │  near-white > 0.5%? ───────────yes─┼─> highlights down (recover sky)
                    │  near-black > 3%? ─────────────yes─┼─> shadows up
                    │  blacks look gray (hazy)? ─────yes─┼─> blacks down
                    │  gray areas tinted? ───────────yes─┼─> white balance, HALF way
                    │        │                           │     (sky + leaves don't count)
                    │  nothing wrong ────────────────────┼─> change nothing
                    └─────────────────┬──────────────────┘
                                      │
                    ┌─────────────────▼──────────────────┐
 [x] BLOCK 4        │  LOOK (preset)                     │  today: a fixed recipe per look
     presets/*.toml │  contrast, HSL color mixer,        │  planned: grade adapts to the
                    │  color grade (shadow/mid/high),    │  colors already in the photo
                    │  vibrance, clarity                 │  (e.g. sky already blue -> less blue)
                    └─────────────────┬──────────────────┘
                                      │
                    ┌─────────────────▼──────────────────┐
 [~] BLOCK 5        │  PROTECT                           │
     adjust.py      │  [x] skin: vibrance + grade skip   │
                    │  [ ] skin: temperature skip        │
                    │  [x] skin on the skin tone line    │  research: all skin = one hue (24 deg)
                    │      faces found -> measure cheeks │  only near faces: mud/sand/wood
                    │      -> move half way, max 6 deg   │  have skin's hue too
                    │  [~] neon: keep letters readable   │
                    │  [ ] sky / faces local edits       │  Apple masks in ProRAW
                    └─────────────────┬──────────────────┘
                                      │
                    ┌─────────────────▼──────────────────┐
 [~] BLOCK 6        │  CROP (per photo, docs/06)         │  today: Claude by eye + --crop-zoom
                    │  subject? -> thirds line / center  │  planned: auto subject detection
                    │  cut empty side, never a joint     │
                    │  place matters? -> don't zoom      │
                    └─────────────────┬──────────────────┘
                                      │
                    ┌─────────────────▼──────────────────┐
 [x] BLOCK 7        │  OUTPUT                            │
                    │  sharpen at full size, shrink last │
                    │  post/ 2048 px   full/ full size   │
                    │  strip GPS                         │
                    └─────────────────┬──────────────────┘
                                      │
                    ┌─────────────────▼──────────────────┐
 [x] BLOCK 8        │  SCORE  `jogo score` (1-10)        │  research: AVA, ~200 raters/photo
     score.py       │  mean of nima, musiq-ava, laion    │
                    │  rank photos -> which to post      │  good at: which PHOTO is better
                    │  edit vs original -> < 0.15 = tie  │  weak at: which GRADE is better
                    └─────────────────┬──────────────────┘
                                      │
                    ┌─────────────────▼──────────────────┐
 [~] BLOCK 9        │  LEARN                             │
                    │  Instagram likes -> docs/07        │
                    │  new research    -> docs/08        │
                    │  tune targets in blocks 3-6        │
                    └────────────────────────────────────┘
```

## Block 2 -> 4: scene to look

The look is chosen by **light + subject**, not by time of day.

```
 light \ subject │ people / face     │ food     │ building / church │ landscape / detail
 ────────────────┼───────────────────┼──────────┼───────────────────┼────────────────────
 strong sun      │ tropical          │ food     │ amber             │ beach / tropical
 cloudy / shade  │ gold              │ food     │ amber             │ gold
 indoor          │ natural           │ food     │ amber             │ natural
 night (lamps)   │ night             │ food     │ night             │ night
 neon / colored  │ natural (lights   │ food     │ natural (lights   │ natural (lights
                 │ capped, block 3)  │          │ capped, block 3)  │ capped, block 3)
```

## Research targets used by the blocks

| Block | Target | Source | Status |
|---|---|---|---|
| 3 | Bright beats dark (+24% likes) | Curalate, 8M posts | Exposure lifts dark photos |
| 3 | Don't darken a bright sky/beach | Owner + common practice | Only darken if median > 0.68 |
| 3 | White balance half way, not fully neutral | Common practice | Built |
| 4 | Low/moderate saturation beats vivid (+18% likes) | Curalate | Looks toned down 2026-10-31 |
| 4 | Moderate color variety gets most likes | Academic study (press) | Not measured yet |
| 5 | Skin: small HSL moves, keep on skin tone line | Skin guides, vectorscope | Partly built |
| 6 | Empty background space (+29% likes) | Curalate | Don't over-crop travel shots |
| 6 | No crops at joints, eyes on top third | Portrait crop guides | Claude checks by eye |
| 8 | Score against average human taste | AVA / NIMA | Planned |

## What's honest about today

- Blocks 3, 4, 7 run in code on every photo.
- Blocks 2 and 6 are decided by Claude looking at thumbnails. They're written here so they're the
  same every time, and so they can be automated later.
- Block 4 is a fixed recipe per look. The *base fix* (block 3) adapts to each photo; the *grade* doesn't yet.
- Block 8 ranks photos for posting. It can't judge small grading changes (see docs/08, "What we measured").

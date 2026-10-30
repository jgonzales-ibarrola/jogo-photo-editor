# My editing style

Decisions from real edits. Claude reads this before every edit and adds to it after feedback.
Newest at the bottom of each section. Edit freely.

## What I like

- Bright and cheerful. A photo that turns dim or gray looks "sad". Avoid it.
- Smooth but sharp. No crunchy, grainy or pixelated texture.
- `beach` look for sunny outdoor photos (blue sky, strong sun).

## What I don't like

- Darkening a photo just because the sky is bright.
- Heavy clarity/sharpening on social-size photos.

## Photo types (grows as we edit)

| Type | Look | Crop | Status |
|---|---|---|---|
| Sunny outdoor / travel with people | `tropical` | 4:5, `--crop-pos bottom` | Used in test1 + test2 |
| Food, landscape, mountains, flowers | — | — | Add when first edited |
| Streets, buildings, statues | — | — | Later: own presets in `my-presets/` |

## Social media settings

- Instagram/Facebook feed: `--crop 4:5 --resize 2048`.
- Always edit full size first, shrink last (built into the tool since 2026-10-30).

## How I want Claude to work

- Only make photos meant for posting. No comparison sheets or grid images unless I ask.
- Shooting/composition advice only when I ask, in plain words.

## Decision log

| Date | Photos | What happened | Decision |
|---|---|---|---|
| 2026-10-30 | test2: IMG_0084 (group), 0088 (couple), 0098 (solo), Cagsawa + Mayon, 10:30 AM | All three had feet near the bottom edge and empty sky on top | `tropical` + `--crop 4:5 --crop-pos bottom --resize 2048`. Awaiting feedback. |
| 2026-10-30 | IMG_0080 crop research | Grid: face on top-left thirds crossing (already good). 4:5 center crop cut the sandal tip | Full-body shots: `--crop-pos bottom` so the crop cuts empty sky, not feet. `tropical` grade looked bright and rich — candidate favorite. |
| 2026-10-30 | Cagsawa ruins, 10:28 AM, strong sun | `landscape`/`vivid` + resize looked dim and grainy; `beach` at full size looked best | Default to `beach` for sunny outdoor shots. Auto only darkens very bright photos. Resize after editing. |

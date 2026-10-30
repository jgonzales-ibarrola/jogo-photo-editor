# My editing style

Decisions from real edits. Claude reads this before every edit and adds to it after feedback.
Newest at the bottom of each section. Edit freely.

## What I like

- Bright and cheerful. A photo that turns dim or gray looks "sad". Avoid it.
- Smooth but sharp. No crunchy, grainy or pixelated texture.
- `beach` look for sunny outdoor photos (blue sky, strong sun).
- Confirmed 2026-10-30: ProRAW from Apple's finished photo + `gold`/`amber` looks better than the iPhone's own photos, sharp, not pixelated.
- "Alive and gorgeous": sharp but not pixelated, deep blacks, rich warm color. Reference: iPhone Photographic Styles
  Amber / Gold / Rose Gold / Bright (Instagram @calvinso_, Oct 2026). Presets `amber`, `gold`, `rose-gold`, `bright`.

## What I don't like

- Darkening a photo just because the sky is bright.
- Heavy clarity/sharpening on social-size photos.
- ProRAW edits that look dim, flat or "unedited".
- Neon signs that glow into a blur so you can't read them. The sign is the subject: keep the room dark, keep the letters sharp.

## Photo types (grows as we edit)

| Type | Look | Crop | Status |
|---|---|---|---|
| Sunny outdoor / travel with people | `tropical` (ProRAW/cloudy: `gold`) | 4:5, `--crop-pos bottom` | Used in test1 + test2 |
| People indoors (restaurants, homes) | `natural` | 4:5, bottom | First used 2026-10-30 (Polangui–Sipocot–Iriga) |
| Food on the table | `food` | 4:5, bottom | First used 2026-10-30 |
| Outdoor night (string lights, lit signs) | `night` | 4:5, bottom | First used 2026-10-30 |
| Indoor details in colored light (neon, decor, no people) | `natural`; neon: add `--highlights -0.3 --saturation -0.15` | 4:5, bottom | First used 2026-10-30 (Biggs) |
| Churches inside, no people | `amber` | 4:5, center (keep ceiling + floor) | First used 2026-10-30 (Naga) |
| Wide (landscape) selfies | same look as the place | 1:1 if 4:5 cuts a face | First used 2026-10-30 (Naga 0671) |
| Landscape, mountains, flowers | — | — | Add when first edited |

Lesson: choose the look by **what's in the photo**, not by the time it was taken. Morning/evening
photos are often indoors (golden-hour on indoor shots was wrong, 2026-10-30).
| Streets, buildings, statues | — | — | Later: own presets in `my-presets/` |

## Social media settings

- Instagram/Facebook feed: `--crop 4:5 --resize 2048`.
- Always make two folders: `post` (2048, for social media) and `full` (`--resize 0`, to keep/zoom/print).
  Owner confirmed 2026-10-30: full version looks smooth, not pixelated, on Windows.
- Always edit full size first, shrink last (built into the tool since 2026-10-30).

## How I want Claude to work

- Only make photos meant for posting. No comparison sheets or grid images unless I ask.
- Shooting/composition advice only when I ask, in plain words.

## Decision log

| Date | Photos | What happened | Decision |
|---|---|---|---|
| 2026-10-30 | naga re-edit feedback | Owner: much better than the iPhone photos, sharp and not pixelated | Keep: ProRAW = Apple base + `gold` (outdoor/people), `amber` (church/buildings). More research later. |
| 2026-10-30 | naga re-edit, all 56 | New ProRAW base + looks: outdoor/people `gold`, church inside/details `amber`, mall `bright`, car selfies `rose-gold`, food `food`. Brighter and clearer; dark stained glass (0688) and statue (0586) now usable | Awaiting feedback. |
| 2026-10-30 | naga ProRAW (DNG) photos | Owner: raw photos look dim and unedited; shared iPhone Photographic Style examples (Amber, Gold, Rose Gold, Bright) as the target | Tool fixed: ProRAW now starts from Apple's finished photo stored in the DNG (brighter, clearer). Added `amber`/`gold`/`rose-gold`/`bright` presets. Awaiting pick. |
| 2026-10-30 | naga: 56 photos (38 ProRAW), Naga Cathedral, Porta Mariae, Peñafrancia, SM mall, donuts | Many ProRAW previews came out nearly black. Cause: tool ignored the DNG BaselineExposure (+2..+5 EV on these) | Tool fixed: DNG loader applies it. Groups: outdoor `tropical` 4:5 bottom; church inside `natural` center; mall/people `natural` bottom; food `food` center. 0671 wide selfie → 1:1. Awaiting feedback. |
| 2026-10-30 | biggs 6962 (blue neon sign) | Owner: letters bloomed, can't read the sign. Cause: auto saw a dark photo (+1 EV, shadows +0.5); pure blue counts as dark, so the neon blew out | Tool fixed: dark photo + colored lights -> exposure max +0.2, shadows max +0.15. Redid 6962 with `--highlights -0.3 --saturation -0.15`. |
| 2026-10-30 | biggs: 4 indoor detail shots, 17:56–18:02 (blue neon sign, lamp + poster, Polaroid on books in purple light) | Compared all looks. `night` too dark, `bw` loses the neon. `natural` brightened the neon shot +1 EV and kept the blue/purple mood | `natural` + 4:5 bottom. Awaiting feedback. |
| 2026-10-30 | cagsawa-trail: 24 photos, 10:30–11:38, ruins (sunny) + ATV trail (cloudy), 5 wide shots | `tropical` 4:5 bottom on tall shots. Wide (4:3) shots: 4:5 keeps only 60% of the width, so crop placed per photo (6905 `0.75,0.5` to keep both faces, tower cut; others center) | Wide selfies lose a lot in 4:5. Awaiting feedback. |
| 2026-10-30 | Cagsawa Trail ATV ride, 27 photos, 11:20–11:35, cloudy | `tropical` + 4:5 bottom crop on all. Overcast sky stays white/gray (no blue to bring out) | First "adventure / cloudy" batch. Offered `overcast` as alternative. Awaiting feedback. |
| 2026-10-30 | test2: IMG_0084 (group), 0088 (couple), 0098 (solo), Cagsawa + Mayon, 10:30 AM | All three had feet near the bottom edge and empty sky on top | `tropical` + `--crop 4:5 --crop-pos bottom --resize 2048`. Awaiting feedback. |
| 2026-10-30 | IMG_0080 crop research | Grid: face on top-left thirds crossing (already good). 4:5 center crop cut the sandal tip | Full-body shots: `--crop-pos bottom` so the crop cuts empty sky, not feet. `tropical` grade looked bright and rich — candidate favorite. |
| 2026-10-30 | Cagsawa ruins, 10:28 AM, strong sun | `landscape`/`vivid` + resize looked dim and grainy; `beach` at full size looked best | Default to `beach` for sunny outdoor shots. Auto only darkens very bright photos. Resize after editing. |

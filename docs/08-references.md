# 08 — References: where our editing rules come from

Every rule the tool and Claude follow should point to a source here.
When we learn something new, add it here first, then change the code or presets.

## Honest status (2026-11-01)

Before today, no rule in this repo had a written source. They came from Claude's general knowledge
of common practice (Lightroom-style sliders, rule of thirds, HSL for skin), plus your feedback in
[my-style.md](my-style.md). That general knowledge is a mix of photographers' guides, but it was never
checked or written down. This file fixes that.

## Three kinds of source, strongest first

| Kind | What it tells us | Examples |
|---|---|---|
| **1. Many people rated photos** | What the *average* person likes. Closest to "what most humans prefer". | AVA dataset, NIMA, Curalate study |
| **2. Many experts edited the same photos** | How the *average* pro edits. | MIT-Adobe FiveK |
| **3. Guides by working photographers** | Techniques and rules of thumb. | Lindsay Adler, SLR Lounge, PetaPixel, DPS |

Research is the default. Personal taste in my-style.md is recorded but only used when asked.
The order of rules is in [09 Decision flow](09-decision-flow.md).

## 1. What most people like

**AVA dataset** (Murray et al., CVPR 2012): about 255,000 photos from the dpchallenge.com photo
contests. Each one was rated 1–10 by about 200 people. It's the standard data for "is this photo
beautiful to most people".

**NIMA** (Google Research, Talebi & Milanfar, 2017): a model trained on AVA. It predicts the score
that average people would give a photo. Its scores closely match the human average.
→ We can use it to score our edits. See "Next steps".
- https://research.google/blog/introducing-nima-neural-image-assessment/
- https://arxiv.org/abs/1709.05424
- Open code: https://github.com/yunxiaoshi/neural-image-assessment

**Curalate analysis of 8 million Instagram posts** (industry study, correlation only):
- Bright photos got 24% more likes than dark ones.
- **Low-saturation photos got 18% more likes than very vivid ones.**
- Blue as the main color got 24% more likes than red.
- Lots of empty background space got 29% more likes.
- https://www.socialmediatoday.com/content/get-more-likes-instagram-infographic
- https://petapixel.com/2013/11/11/pics-blue-enough-turn-photos-instagram-like-magnets/

An academic study (reported in the press) found that *medium* color variety and an even lighting
fix got the most likes, not the most extreme look.

**This matches your taste:** bright yes, saturated no (my-style.md, 2026-10-31).

## 2. How experts edit on average

**MIT-Adobe FiveK** (MIT + Adobe, 2011): 5,000 raw photos, each edited in Lightroom by 5 trained
photographers (A–E). They were asked for a "visually pleasing, postcard" result. Users rate
**Expert C** best, so most research uses C as the target.
→ It's the best open example of "the average pro edit". We can measure our presets against it.
- https://paperswithcode.com/dataset/mit-adobe-fivek

## 3. Techniques from photographers

### Edit order
Fix the base first, then do the look: **white balance → exposure → highlights/shadows → color (HSL) → color grading → sharpen/noise.**
Our pipeline (`adjust.apply`) already follows this order.
- https://petapixel.com/2021/08/17/my-color-grading-workflow-for-raw-landscape-photos-in-lr-and-acr
- https://www.canon.co.nz/get-inspired/lightroom-for-beginners
- https://www.bhphotovideo.com/explora/node/114886 (color grading)

### White balance
- **Gray world** (Buchsbaum 1980): on average a scene is gray, so the average color of the photo
  shows the color of the light. We use it only for dark lamp-lit scenes with no gray surface left.
  Buchsbaum, G., "A spatial processor model for object colour perception", J. Franklin Inst. 310(1), 1980.
  https://doi.org/10.1016/0016-0032(80)90058-7

### Skin
- Skin lives in the **orange and red** colors. Viewers notice it first.
- Make small moves (about ±5). Too much saturation looks sunburned; too little looks gray and sick.
- Too-orange skin: lower orange/red saturation a little and raise their luminance a little.
- **Skin tone line:** on a vectorscope, the skin of every person, of any skin color, sits on one hue
  line between red and yellow. Only brightness and saturation differ. It's a guide, not a strict rule.
  → Idea: auto can check that skin sits on this line and fix it if not.
- https://fstoppers.com/education/how-edit-portrait-skin-tones-lightroom-902830
- https://photography.tutsplus.com/tutorials/how-to-use-the-orange-slider-on-portrait-photos-using-lightroom-classic--cms-40946
- https://helpx.adobe.com/premiere-pro/how-to/correct-skin-tones.html
- https://larryjordan.com/articles/the-secret-to-setting-skin-colors-accurately/

### Popular looks
- **Teal and orange:** cool shadows, warm skin and highlights. Borrowed from film. Our `cinematic`.
- **Film looks** (Kodak Portra, Fuji): softer contrast, lower saturation, gentle skin. Portra is known
  for flattering skin. Our `film`.
- **LUT** = a saved color recipe that maps every color to a new one. Film LUTs copy a film stock.
  Most are paid; quality varies; many are made for video. We build our looks from sliders instead,
  so we can explain every step.
- https://www.slrlounge.com/photo-editing-styles-a-comprehensive-overview/
- https://mixinglight.com/color-grading-tutorials/what-makes-film-print-emulation-luts-special-and-how-do-you-use-them
- https://www.premiumbeat.com/blog/understanding-luts-in-color-grading

### Cropping people
- **Never crop at a joint:** ankles, knees, wrists, elbows, neck. Rule of thumb: "If it bends, don't crop it."
  Crop through the middle of a limb instead.
- Don't cut the chin or the sides of the head. A little off the top of the head is fine on close-ups.
- **Headroom:** a small gap above the head. Not touching the edge, not a big empty gap.
- Eyes near the top third line. Leave room in front of where the person looks.
- Every crop loses pixels, so crop in camera when you can.
- https://slrlounge.com/portrait-cropping-guide-bad-portrait-crops-how-to-fix-them
- https://digital-photography-school.com/good-crop-bad-crop-how-to-crop-portraits/
- https://site.creativelive.com/class/portrait-photography-bootcamp-with-lindsay-adler/lessons/cropping-composition
- https://expertphotography.com/cropping-photos-portraits

## What we measured ourselves

**2026-11-01, cagsawa-family (46 photos), `jogo score --vs photos/in`:**
- Our edit vs the original: 45 of 46 were a tie (difference under 0.15). One was slightly better.
- So the AVA models barely notice grading. They judge the *photo*: subject, composition, scene.
- Ranking: wide shots with two people + Mayon + sign scored highest (5.6). Close portraits and food
  scored lowest (4.5–4.8). AVA comes from photo-contest voters, who like scenes more than snapshots.
- Use: **score = which photos to post.** For *how to grade*, use expert edits (FiveK), not AVA.

**Skin tone line on faces** (OpenCV face detection, then cheek hue):
- Portraits were already close: 1–2 degrees off. ATV riders in helmets: about 4 degrees.
- Without face detection, mud in 0185 counted as "skin". That's why the check only looks at faces.

**2026-11-01, FiveK study (300 photos x 5 experts, `research/fivek.py report`):**
Numbers are CIELAB: L* = brightness 0–100, chroma = color strength, b = warm(+)/cool(−).
Full table: `research/data/fivek/report.txt` (not committed).

| Scene | Input L* | Experts L* | Our best look L* | Experts chroma | Ours | Experts b | Ours |
|---|---|---|---|---|---|---|---|
| All 300 | 22.6 | **39.7** | 32.7 (airy) | 16.4 | 14–16 | 6.5 | 6–7 |
| Outdoors, people | 23.8 | 43.5 | 35.3 | 19.5 | 15–17 | 9.1 | 5–6 |
| Outdoors, nature | 25.2 | 38.4 | 34.4 | **21.9** | 16–18 | 10.9 | 7–8 |
| Outdoors, buildings | 30.3 | 47.3 | 41.1 | 14.5 | 12–14 | 3.3 | 2–3 |
| Indoors, people | 21.3 | 42.8 | 32.3 | 16.5 | 17–19 | **8.6** | 12–14 |
| Dusk, outdoors | 22.6 | 40.5 | 33.5 | 14.6 | 12–14 | 0.7 | 0 |
| Night, indoors | 13.0 | 30.5 | 21.9 | 14.8 | 13–17 | **6.6** | 9–12 |
| Night, outdoors | 12.3 | 22.4 | 20.7 | 15.7 | 14–17 | **3.7** | 7–9 |

What the pros do, in plain words:
1. **Brighter.** In every scene the experts' middle brightness is 8–11 L* above our looks, and their
   brightest parts (p95) reach ~80 vs our ~70. Our auto exposure stops too early on dark photos
   (capped at about +1 EV). This matches the Curalate "brighter gets more likes" finding.
2. **More contrast**: their dark-to-bright range is ~71 vs our ~62.
3. **Color strength depends on the scene**: more color for nature (22 vs 17) and outdoor people,
   about the same for buildings, *less* for indoor people.
4. **Remove warm lamp color at night and indoors.** The experts cut the orange cast of street and
   room lights (night outdoor b: input 6.8 → experts 3.7; their highlight warmth halves). Our looks
   keep or add the orange. Daylight scenes they warm a little instead.
5. **Skin hue stays put** (20–23°). Experts don't move skin much; our looks keep it too.

**Rules taken from it (2026-11-01, in `auto.py`):** exposure goes 90% of the way to the target
(was 70%), up to +2.5 EV (was ~+1); dull photos (chroma < 14) get vibrance, more the duller they
are; dark lamp-lit scenes get 3/4 of their orange removed (daylight keeps half).
Highlight guard (2026-11-02): the experts' brightest 5% sit at L* ~80 in every scene (never white).
So exposure stops before our brightest 5% passes L* 90; the highlights slider then brings it near 80.
Found on a real photo: a white shirt in front of a black speaker got +1.3 EV and turned white.
Darkening stays at most -0.28 EV (FiveK only tells us to go brighter). Result on the 300
photos (`fivek.py check --looks natural`, 2026-11-02): `natural` went from distance 6.25 to **4.18**
from the experts (lower = closer). Closer in every scene; night outdoors improved most (9.66 → 4.99).
Brightest parts now 74 L* (experts 79), so the highlight guard doesn't hold us back.
Still off:
- Still darker than the pros: middle 30.7 vs 39.7 L*. Next lever: the presets' tone curves, not exposure.
- Indoor people (b 12.3 vs 8.6) and night indoors (10.2 vs 6.6) are still too warm.
- Highlights turned slightly green (a* −1.9 vs experts +0.5), likely from the stronger white balance.
- Daylight: pros warm photos a little more than we do (outdoor people b 4.8 vs 9.1).

Caveat: FiveK inputs are flat Nikon/Canon raws, darker than a finished iPhone photo. The *targets*
(experts' L*, chroma, warmth) transfer; the size of the gap on iPhone photos will be smaller.

## How our tool matches the sources

| Rule | Source | Tool today |
|---|---|---|
| Base first, look last | Guides | Yes, `adjust.apply` order |
| Bright, not over-saturated | Curalate, your feedback | Yes, looks toned down 2026-10-31 |
| Small skin moves, protect skin | Skin guides | Yes for vibrance and grading. Not yet for temperature |
| Skin on the skin tone line | Vectorscope guides | Yes, on detected faces (2026-11-01) |
| No crops at joints, eyes on top third | Crop guides | Claude checks by eye. Not automatic |
| Empty background space helps | Curalate | Don't over-crop travel shots (docs/06) |
| Score edits against average taste | AVA / NIMA | Yes, `jogo score`. Good for picking photos, not grades |
| Brightness, contrast, color like pros | FiveK | Yes, auto rules tuned on 300 photos (2026-11-01) |
| Remove lamp color at night | FiveK, gray world | Yes, 3/4 way in dark scenes. Still a bit warm |

## Next steps

1. **Adaptive color grade:** fit per-scene rules from the FiveK numbers (e.g. less added color when
   the photo is already colorful, how far pros cool lamp light). See docs/09 block 4.
2. **Tune each look** (vivid, portrait, landscape...) toward the experts for its scene.
3. **Collect references you like:** send photographers or posts you like. Each one gets a row below.

## Photographers and posts you like

| Who / where | What we took from it | Date |
|---|---|---|
| Instagram @calvinso_ | iPhone Photographic Styles Amber, Gold, Rose Gold, Bright → presets | 2026-10-30 |

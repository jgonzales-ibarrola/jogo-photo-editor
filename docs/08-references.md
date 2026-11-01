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

## Next steps

1. **Score every edit with NIMA** (average human taste, 1–10). Claude picks the best version and the
   best photos to post by score + your feedback, not only by eye.
2. **Compare our looks with FiveK Expert C** on a sample of photos, and tune presets toward it.
3. **Skin tone line check** in auto: measure the skin hue, nudge it onto the line.
4. **Collect references you like:** send photographers or posts you like. Each one gets a row below.

## Photographers and posts you like

| Who / where | What we took from it | Date |
|---|---|---|
| Instagram @calvinso_ | iPhone Photographic Styles Amber, Gold, Rose Gold, Bright → presets | 2026-10-30 |

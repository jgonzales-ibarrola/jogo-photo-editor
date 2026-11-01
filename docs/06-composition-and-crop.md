# 06 — Composition grids and cropping

Composition = where things sit in the frame. Grids are lines that show the "strong" spots.
You use them twice: in the camera when you shoot (iPhone Grid setting), and here when you crop.

## See the grids on your photo

```powershell
python -m jogo grid photos\in\IMG_0080.HEIC                         # grids on the whole photo
python -m jogo grid photos\in\IMG_0080.HEIC --crop 4:5               # + darkens what a 4:5 crop cuts
python -m jogo grid photos\in\IMG_0080.HEIC --crop 4:5 --crop-pos bottom
```

The result is saved in `photos\out` as `..._grid....jpg`.

| Line color | Grid | Use it for |
|---|---|---|
| **White** | Rule of thirds | The default. Put eyes, people, horizons on these lines or crossings. |
| **Yellow** | Golden ratio (phi grid) | Like thirds, slightly closer to the center. Feels calmer and more "classic". |
| **Cyan** | Diagonals | Lines and poses that follow a diagonal feel dynamic. |

## The techniques

**Rule of thirds** — Split the frame in 3×3. Put the subject on a line or a crossing, not dead center.
- Eyes of a person: on the top third line.
- Horizon: on the bottom line (big sky) or the top line (big land/sea). Not through the middle.

**Golden ratio (phi grid)** — The same idea with lines at 38% and 62% instead of 33% and 67%.
If the subject is a bit too close to the center for thirds, it's often right on the golden lines. Either is fine.

**Golden spiral** — A curve that winds in toward one golden crossing.
The eye follows a curved path (a road, shoreline, arm, wave) into the subject. The yellow crossings show where the spiral ends.

**Diagonals** — Strong lines going corner to corner: roads, rails, stairs, a reaching arm, a leaning tree.
Diagonals feel like movement. Horizontal lines feel calm. Vertical lines feel strong and tall.

**Centered and symmetry** — Put the subject dead center *on purpose*, when the scene is symmetrical:
church fronts, doors, piers, reflections, a person facing the camera head-on. Here the grids don't apply; balance does.

**Leading lines, framing, negative space, fill the frame** — See [05 Shooting guide](05-shooting-guide-philippines.md).

## Crop decision checklist

I follow this for every crop, in this order:

1. **Does the photo already work?** Subject clear, no distractions, horizon level → don't crop, or only change the shape for the platform.
2. **What's the subject?** A face, a person, a landmark, or a person + a landmark (travel photo: keep both).
3. **What's the shape?** `4:5` feed, `9:16` Stories/Reels, `1:1` square, `16:9` wide, `3:2` original-feel.
4. **Where should the subject sit?** On a thirds/golden line or crossing. Or centered, if the scene is symmetrical.
5. **Which side to cut?** Cut from the side with *nothing* in it (empty sky, plain ground), not the side with feet, hands or the landmark. Use `--crop-pos`.
6. **Check the edges** (run `grid --crop ...`): no cut joints (ankles, knees, wrists, elbows, neck), no half-cut hands or feet, room in front of where the person looks or moves.
7. **Check the size**: after cropping, a photo should still be at least about 2000 px on the long side for social media.

## `--crop-pos`: which part to keep

| Value | Keeps | Cuts from | Use when |
|---|---|---|---|
| `center` (default) | the middle | both sides equally | Subject is centered. |
| `bottom` | the bottom | the top | Feet/ground matter, top is empty sky. Full-body shots. |
| `top` | the top | the bottom | Faces/sky matter, bottom is plain ground. |
| `left` / `right` | that side | the other side | Subject is on one side. |
| `"x,y"` e.g. `"0.3,0.8"` | exact spot (0 = left/top, 1 = right/bottom) | — | Fine control. |

## `--crop-zoom`: crop tighter to fix composition

iPhone photos are 3:4. A 4:5 crop only trims about 6%, so the subject can't really move.
`--crop-zoom 0.85` keeps 85% of the width and height. Now `--crop-pos` has room to slide the box.

- Person in the dead center with lots of empty space around: zoom 0.8–0.9, and slide so the eyes sit on the top third line.
- Big empty ground or sky: zoom 0.9, and slide away from the empty side.
- Keep zoom at 0.75 or more. The photo still needs to be about 2000 px on the long side.
- Don't zoom when the place matters as much as the person (sign, landmark, mountain). Keep the whole scene.

## Example: Cagsawa photo IMG_0080 (2026-10-30)

- The grid showed the face right on the top-left thirds crossing. The photo was already well composed.
- A 4:5 **center** crop cut the tip of the front sandal. A 4:5 **bottom** crop cut only empty sky and kept both feet whole.
- Decision: `--crop 4:5 --crop-pos bottom`.

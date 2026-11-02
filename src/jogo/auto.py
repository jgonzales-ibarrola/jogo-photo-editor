"""Auto mode: look at the photo, decide what to fix, and explain why in plain words."""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from .adjust import GAMMA, luminance

TARGET_MIDTONE = 0.42  # Where a "normally bright" photo's middle brightness sits.

# Rules below marked "FiveK" come from 300 photos x 5 expert edits (docs/08, "What we measured").
EV_SHARE = 0.9         # FiveK: experts bring dark photos ~90% of the way to the target, not 70%.
EV_MAX = 2.5           # FiveK: very dark inputs got +1.9 to +2.4 EV from the experts.
EV_MIN = -0.28         # Darkening stays as gentle as before FiveK (it only says "brighter").
HIGH_LIMIT = 0.76      # FiveK: experts' brightest 5% sit at L* ~80. Exposure stops at L* 90
                       # (linear 0.76); the highlights slider then pulls it back toward 80.
DULL_CHROMA = 14.0     # FiveK: below this Lab chroma, experts added more color the duller it was.
DULL_VIBRANCE = 0.35   # Vibrance added to a completely gray photo; less as color rises.
DARK_SCENE = 0.2       # Median brightness of a night/lamp-lit scene.


@dataclass
class Analysis:
    median: float
    dark_pct: float        # % of pixels that are nearly black
    bright_pct: float      # % of pixels that are nearly white (lost detail)
    cast: np.ndarray       # average R, G, B of mid-tones in linear light
    offsets: dict[str, float] = field(default_factory=dict)
    wb_gains: np.ndarray | None = None
    notes: list[str] = field(default_factory=list)


def _preview(img: np.ndarray, long_edge: int = 1024) -> np.ndarray:
    step = max(1, max(img.shape[:2]) // long_edge)
    return img[::step, ::step]


def _chroma(small: np.ndarray) -> float:
    """Mean CIELAB chroma (color strength), the same measure as the FiveK study."""
    lin = np.where(small <= 0.04045, small / 12.92, ((small + 0.055) / 1.055) ** 2.4)
    xyz = lin @ np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]]).T
    xyz /= np.array([0.9505, 1.0, 1.089])
    f = np.where(xyz > 0.008856, np.cbrt(xyz), 7.787 * xyz + 16 / 116)
    return float(np.hypot(500 * (f[..., 0] - f[..., 1]), 200 * (f[..., 1] - f[..., 2])).mean())


def analyze(img: np.ndarray, auto_wb: bool = True, strength: float = 1.0) -> Analysis:
    small = np.clip(_preview(img), 0, 1)
    lum = luminance(small)
    median = float(np.median(lum))
    p05 = float(np.percentile(lum, 0.5))
    p995 = float(np.percentile(lum, 99.5))
    dark_pct = float((lum < 0.03).mean() * 100)
    bright_pct = float((lum > 0.97).mean() * 100)

    # Color cast is judged only from near-gray mid-tones (walls, roads, clouds). A big blue sky
    # or green field is real color, not a cast, so it must not count.
    linear = small ** GAMMA
    r, g, b = small[..., 0], small[..., 1], small[..., 2]
    top = small.max(axis=2)
    spread = (top - small.min(axis=2)) / np.maximum(top, 1e-3)
    sky = (b >= top) & (lum > 0.45) & (spread > 0.08)
    foliage = (g >= top) & (spread > 0.12)
    neutral = (lum > 0.15) & (lum < 0.9) & (spread < 0.3) & ~sky & ~foliage
    if median < DARK_SCENE:
        # Under lamps a gray wall turns strongly orange and dim, so the normal test misses it.
        neutral = (lum > 0.06) & (lum < 0.9) & (spread < 0.55) & ~sky & ~foliage
    has_neutrals = neutral.mean() > 0.03
    cast = linear[neutral].mean(axis=0) if has_neutrals else np.ones(3)

    # Neon and colored lamps: pure blue/red is dark by luminance even when the channel is maxed out,
    # so brightening the "dark" photo blows the lights into a blur.
    colored_lights = float(((top > 0.6) & (spread > 0.6)).mean() * 100)

    # A room or street lit only by orange lamps has no gray left to measure. Then use the whole
    # photo's average ("gray world", docs/08). Not for neon scenes: their color is the subject.
    lit = (lum > 0.03) & (lum < 0.95)
    orange = (r >= top) & (b <= g)
    neon = float(((top > 0.6) & (spread > 0.6) & ~orange).mean() * 100)
    if not has_neutrals and median < DARK_SCENE and neon <= 1 and lit.mean() > 0.1:
        cast, has_neutrals = linear[lit].mean(axis=0), True

    a = Analysis(median, dark_pct, bright_pct, cast)
    k = float(np.clip(strength, 0, 1))

    # Exposure: brighten dark photos toward the target. Only darken photos that are clearly too
    # bright: bright skies and beaches are supposed to look bright.
    ev = float(np.clip(np.log2((TARGET_MIDTONE / max(median, 1e-3)) ** GAMMA) * EV_SHARE, EV_MIN, EV_MAX))
    if ev < 0 and median < 0.68:
        ev = 0.0
    lit_scene = ev > 0.3 and colored_lights > 1
    if lit_scene:
        ev = 0.2
        a.notes.append(f"Dark scene with colored lights ({colored_lights:.0f}% of the photo, e.g. neon) "
                       "-> kept dark so the lights stay sharp and readable.")
    # A bright subject on a dark background (white shirt by a black speaker) has a low median,
    # but brightening it blows the subject out. Stop before the brightest 5% passes the limit.
    p95 = float(np.percentile(lum, 95))
    high_cap = max(0.0, float(np.log2(HIGH_LIMIT / max(p95 ** GAMMA, 1e-3))))
    if ev > high_cap:
        a.notes.append(f"Brightest parts are already bright -> exposure held at {high_cap * k:+.2f} "
                       f"instead of {ev * k:+.2f} so they don't turn white.")
        ev = high_cap
    if abs(ev) >= 0.1:
        a.offsets["exposure"] = round(ev * k, 2)
        a.notes.append(f"Photo is {'dark' if ev > 0 else 'bright'} -> exposure {ev * k:+.2f} EV.")

    if bright_pct > 0.5 or (ev > 0.3 and p995 > 0.9):
        amt = -min(0.6, 0.2 + bright_pct / 10)
        a.offsets["highlights"] = round(amt * k, 2)
        a.notes.append(f"{bright_pct:.1f}% of the photo is near white -> highlights {amt * k:+.2f} to recover sky/detail.")

    if dark_pct > 3 or median < 0.25:
        amt = min(0.15 if lit_scene else 0.5, 0.15 + dark_pct / 40)
        a.offsets["shadows"] = round(amt * k, 2)
        a.notes.append(f"{dark_pct:.1f}% of the photo is near black -> shadows {amt * k:+.2f} to show detail.")

    if p05 > 0.06:
        a.offsets["blacks"] = round(-0.4 * k, 2)
        a.notes.append("Darkest parts look gray (hazy/flat) -> blacks deepened.")

    # Dull photos: FiveK experts doubled the color of near-gray photos and left colorful ones alone.
    chroma = _chroma(small)
    if chroma < DULL_CHROMA:
        vib = DULL_VIBRANCE * (1 - chroma / DULL_CHROMA)
        if vib >= 0.05:
            a.offsets["vibrance"] = round(vib * k, 2)
            a.notes.append(f"Colors are dull (strength {chroma:.0f}) -> vibrance {vib * k:+.2f}.")

    if auto_wb and has_neutrals:
        gray = cast[1]
        warm = cast[0] > cast[2]
        # Lamp-lit dark scenes: FiveK experts removed ~75% of a strong orange cast at night, but kept
        # daylight warmth. So: halfway in daylight (fully neutral looks lifeless), more at night.
        lamp = warm and median < DARK_SCENE
        lim, share = (0.5, 0.75) if lamp else (0.15, 0.5)
        gains = np.clip(np.array([gray / cast[0], 1.0, gray / cast[2]]), 1 - lim, 1 + lim)
        gains = 1.0 + (gains - 1.0) * share * k
        if np.abs(gains - 1.0).max() > 0.015:
            a.wb_gains = gains.astype(np.float32)
            if lamp:
                a.notes.append("Dark scene with orange lamp light -> white balance corrected 3/4 of the way.")
            else:
                tone = "warm/orange" if warm else "cool/blue"
                a.notes.append(f"Photo has a {tone} color cast -> white balance corrected halfway.")

    if not a.notes:
        a.notes.append("Exposure and color already look good. Only the preset look is applied.")
    return a

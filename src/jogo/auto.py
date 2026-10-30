"""Auto mode: look at the photo, decide what to fix, and explain why in plain words."""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from .adjust import GAMMA, luminance

TARGET_MIDTONE = 0.42  # Where a "normally bright" photo's middle brightness sits.


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
    has_neutrals = neutral.mean() > 0.03
    cast = linear[neutral].mean(axis=0) if has_neutrals else np.ones(3)

    a = Analysis(median, dark_pct, bright_pct, cast)
    k = float(np.clip(strength, 0, 1))

    # Exposure: brighten dark photos toward the target. Only darken photos that are clearly too
    # bright: bright skies and beaches are supposed to look bright.
    ev = float(np.clip(np.log2((TARGET_MIDTONE / max(median, 1e-3)) ** GAMMA), -0.4, 1.5)) * 0.7
    if ev < 0 and median < 0.68:
        ev = 0.0
    if abs(ev) >= 0.1:
        a.offsets["exposure"] = round(ev * k, 2)
        a.notes.append(f"Photo is {'dark' if ev > 0 else 'bright'} -> exposure {ev * k:+.2f} EV.")

    if bright_pct > 0.5 or (ev > 0.3 and p995 > 0.9):
        amt = -min(0.6, 0.2 + bright_pct / 10)
        a.offsets["highlights"] = round(amt * k, 2)
        a.notes.append(f"{bright_pct:.1f}% of the photo is near white -> highlights {amt * k:+.2f} to recover sky/detail.")

    if dark_pct > 3 or median < 0.25:
        amt = min(0.5, 0.15 + dark_pct / 40)
        a.offsets["shadows"] = round(amt * k, 2)
        a.notes.append(f"{dark_pct:.1f}% of the photo is near black -> shadows {amt * k:+.2f} to show detail.")

    if p05 > 0.06:
        a.offsets["blacks"] = round(-0.4 * k, 2)
        a.notes.append("Darkest parts look gray (hazy/flat) -> blacks deepened.")

    if auto_wb and has_neutrals:
        gray = cast[1]
        gains = np.clip(np.array([gray / cast[0], 1.0, gray / cast[2]]), 0.85, 1.15)
        gains = 1.0 + (gains - 1.0) * 0.5 * k  # Correct half the cast: fully neutral looks lifeless.
        if np.abs(gains - 1.0).max() > 0.015:
            a.wb_gains = gains.astype(np.float32)
            tone = "warm/orange" if gains[2] > gains[0] else "cool/blue"
            a.notes.append(f"Photo has a {tone} color cast -> white balance corrected halfway.")

    if not a.notes:
        a.notes.append("Exposure and color already look good. Only the preset look is applied.")
    return a

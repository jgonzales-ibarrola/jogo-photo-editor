"""The editing pipeline. Images are float32 RGB arrays in 0..1, gamma-encoded."""

from __future__ import annotations

import colorsys

import numpy as np
from PIL import Image
from scipy import ndimage

from .settings import HSL_BANDS, Settings

LUMA = np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)
GAMMA = 2.2
LUT_SIZE = 65536  # Tone curves are precomputed at 16-bit precision, then looked up per pixel.
_X = np.linspace(0.0, 1.0, LUT_SIZE, dtype=np.float32)


def luminance(img: np.ndarray) -> np.ndarray:
    return img @ LUMA


def _upscale(small: np.ndarray, h: int, w: int) -> np.ndarray:
    return np.asarray(Image.fromarray(small).resize((w, h), Image.BILINEAR))


def _soft_blur(channel: np.ndarray, radius_frac: float, eps: float = 0.01) -> np.ndarray:
    """Edge-aware blur (guided filter) of a downscaled copy. Smooths flat areas but stops at strong
    edges like a horizon, so brightening shadows doesn't leave a glow along them. Returns the small copy."""
    step = max(1, min(channel.shape) // 512)
    guide = np.ascontiguousarray(channel[::step, ::step])
    size = max(3, int(radius_frac * min(guide.shape)) * 2 + 1)
    mean = ndimage.uniform_filter(guide, size)
    var = ndimage.uniform_filter(guide * guide, size) - mean * mean
    a = var / (var + eps)
    b = mean - a * mean
    return ndimage.uniform_filter(a, size) * guide + ndimage.uniform_filter(b, size)


def _half_res_blur(channel: np.ndarray, sigma: float) -> np.ndarray:
    h, w = channel.shape
    small = np.ascontiguousarray(channel[::2, ::2])
    return _upscale(ndimage.gaussian_filter(small, sigma=sigma, truncate=3.0), h, w)


def _apply_lut(img: np.ndarray, lut: np.ndarray) -> None:
    """Replace every value v in img with lut[v]. In place."""
    idx = (img * (LUT_SIZE - 1) + 0.5).astype(np.uint16)
    np.take(lut, idx, out=img)


def _tone_lut(gain: float, s: Settings) -> np.ndarray:
    """Exposure/white balance gain (in linear light) + highlight rolloff + blacks/whites, as one curve."""
    y = _X ** GAMMA * gain
    knee, span = 0.8, 0.2  # Above the knee, bright values roll off smoothly instead of clipping hard.
    over = y > knee
    y[over] = knee + span * (1.0 - np.exp(-(y[over] - knee) / span))
    y = np.clip(y, 0.0, 1.0) ** (1 / GAMMA)

    # Blacks and whites move the darkest and brightest tones. Same sign as Lightroom: + is lighter.
    if s.blacks < 0:  # deeper blacks: values below the cut become pure black
        cut = -0.08 * s.blacks
        y = (y - cut) / (1.0 - cut)
    elif s.blacks > 0:  # lifted, faded blacks
        lift = 0.08 * s.blacks
        y = y * (1.0 - lift) + lift
    if s.whites > 0:  # brighter whites: values above the cut become pure white
        y = y / (1.0 - 0.08 * s.whites)
    elif s.whites < 0:  # dimmer whites
        y = y * (1.0 + 0.08 * s.whites)
    return np.clip(y, 0.0, 1.0).astype(np.float32)


CHUNK_ROWS = 512
_BAND_CENTERS = np.array(list(HSL_BANDS.values()), dtype=np.float32)
HUE_SHIFT_MAX = 30.0  # degrees a hue slider at +-1 moves a color (toward its neighbor band)


def _to_hsv(img: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Hue in degrees 0..360, saturation 0..1, value 0..1."""
    r, g, b = img[..., 0], img[..., 1], img[..., 2]
    v = img.max(axis=-1)
    c = v - img.min(axis=-1)
    sat = np.where(v > 1e-6, c / np.maximum(v, 1e-6), 0.0)
    safe = np.maximum(c, 1e-6)
    hue = np.where(v == r, (g - b) / safe % 6.0, np.where(v == g, (b - r) / safe + 2.0, (r - g) / safe + 4.0))
    hue = np.where(c > 1e-6, hue * 60.0, 0.0)
    return hue.astype(np.float32), sat.astype(np.float32), v


def _from_hsv(hue: np.ndarray, sat: np.ndarray, v: np.ndarray, out: np.ndarray) -> None:
    hp = (hue % 360.0) / 60.0
    c = v * sat
    x = c * (1.0 - np.abs(hp % 2.0 - 1.0))
    m = v - c
    sector = hp.astype(np.int8) % 6
    zero = np.zeros_like(c)
    for i, (r, g, b) in enumerate(((c, x, zero), (x, c, zero), (zero, c, x), (zero, x, c), (x, zero, c),
                                   (c, zero, x))):
        mask = sector == i
        out[..., 0][mask], out[..., 1][mask], out[..., 2][mask] = r[mask], g[mask], b[mask]
    out += m[..., None]


def _band_weights(hue: np.ndarray) -> np.ndarray:
    """How much each pixel belongs to each color band. Bands fade linearly into their neighbors and the
    weights always add up to 1, so there are no hard edges between colors."""
    centers = _BAND_CENTERS
    n = len(centers)
    out = np.zeros((n,) + hue.shape, dtype=np.float32)
    for i in range(n):
        lo, mid, hi = centers[i - 1], centers[i], centers[(i + 1) % n]
        d = (hue - mid + 180.0) % 360.0 - 180.0  # signed distance to this band's center
        left, right = (mid - lo) % 360.0, (hi - mid) % 360.0
        out[i] = np.clip(np.where(d < 0, 1.0 + d / left, 1.0 - d / right), 0.0, 1.0)
    return out


def _skin(hue: np.ndarray, sat: np.ndarray, v: np.ndarray) -> np.ndarray:
    """0..1: how much a pixel looks like skin (orange hue, moderate saturation, not too dark)."""
    near = np.clip(1.0 - np.abs(hue - 25.0) / 20.0, 0.0, 1.0)
    return near * np.clip((sat - 0.08) / 0.1, 0, 1) * np.clip((0.75 - sat) / 0.15, 0, 1) * np.clip(
        (v - 0.15) / 0.15, 0, 1)


def _color_strip(img: np.ndarray, hsl: np.ndarray, grades: list, protect_skin: float) -> None:
    hue, sat, v = _to_hsv(img)
    if hsl.any():
        w = _band_weights(hue)
        shift = np.tensordot(hsl[:, 0], w, axes=1) * HUE_SHIFT_MAX
        sat_mul = 1.0 + np.tensordot(hsl[:, 1], w, axes=1)
        # Brightness change scales with saturation, so grays and whites are never touched.
        v_mul = 1.0 + 0.5 * np.tensordot(hsl[:, 2], w, axes=1) * np.minimum(sat * 2.0, 1.0)
        hue = hue + shift
        sat = np.clip(sat * sat_mul, 0.0, 1.0)
        v = np.clip(v * v_mul, 0.0, 1.0)
        _from_hsv(hue, sat, v, img)
        del w, shift, sat_mul, v_mul
    if grades:
        lum = luminance(img)
        keep = 1.0 - protect_skin * _skin(hue % 360.0, sat, v)
        zones = {"shadows": (1.0 - lum) ** 2, "midtones": 4.0 * lum * (1.0 - lum) * 0.5, "highlights": lum ** 2}
        for amount, hue_deg, zone in grades:
            # The tint is brightness-neutral, so it changes color without darkening or brightening.
            tint = np.array(colorsys.hsv_to_rgb((hue_deg % 360) / 360, 1.0, 1.0), dtype=np.float32)
            tint -= tint @ LUMA
            img += (zones[zone] * keep * np.float32(0.15 * amount))[..., None] * tint
    np.clip(img, 0.0, 1.0, out=img)


def _vibrance_strip(img: np.ndarray, vibrance: float, saturation: float, protect_skin: float) -> None:
    lum = luminance(img)[..., None]
    r, g, b = img[..., 0], img[..., 1], img[..., 2]
    v = np.maximum(np.maximum(r, g), b)
    c = v - np.minimum(np.minimum(r, g), b)
    chroma = np.clip(c * 2.0, 0, 1)
    vib = vibrance
    if vibrance > 0 and protect_skin:
        # Skin hues sit where red is the top channel, so hue = 60 * (g - b) / c there (no full HSV needed).
        hue = np.where(r >= v, 60.0 * (g - b) / np.maximum(c, 1e-6), 180.0)
        vib = vibrance * (1.0 - protect_skin * _skin(hue, c / np.maximum(v, 1e-6), v))
    factor = np.clip(1.0 + saturation + vib - vib * chroma, 0.0, None)[..., None]
    img -= lum
    img *= factor.astype(np.float32)
    img += lum
    np.clip(img, 0.0, 1.0, out=img)


def apply(img: np.ndarray, s: Settings, wb_gains: np.ndarray | None = None) -> np.ndarray:
    img = np.clip(img, 0.0, 1.0, out=img)
    h, w = img.shape[:2]

    # 1-2. Exposure, white balance, blacks, whites: one lookup curve per color channel.
    gains = np.ones(3, dtype=np.float32) if wb_gains is None else wb_gains.astype(np.float32)
    gains = gains * np.array(
        [1 + 0.15 * s.temperature, 1 - 0.10 * s.tint, 1 - 0.15 * s.temperature], dtype=np.float32
    )
    gains *= np.float32(2.0 ** s.exposure)
    if not np.allclose(gains, 1.0) or s.blacks or s.whites:
        for c in range(3):
            channel = np.ascontiguousarray(img[..., c])
            _apply_lut(channel, _tone_lut(float(gains[c]), s))
            img[..., c] = channel

    # 3. Highlights and shadows use a blurred brightness map so edges don't get halos.
    if s.highlights or s.shadows or s.clarity:
        lum = luminance(img)
        small = _soft_blur(lum, 0.02)
        if s.highlights or s.shadows:
            # Highlights act on bright-but-not-white areas; pure white has no detail left to recover.
            bright = small ** 3 * (1.0 - small ** 12)
            factor = 1.0 + 0.6 * s.shadows * (1.0 - small) ** 3 + 0.5 * s.highlights * bright
            img *= _upscale(factor.astype(np.float32), h, w)[..., None]
            np.clip(img, 0.0, 1.0, out=img)
        # 4. Clarity boosts (or softens) mid-size detail.
        if s.clarity:
            lum -= _upscale(small, h, w)
            lum *= 0.8 * s.clarity
            img += lum[..., None]
            np.clip(img, 0.0, 1.0, out=img)
        del lum, small

    # 5. Contrast: an S-curve. Stays smooth and never flips tones for values in -1..1.
    if s.contrast:
        c = float(np.clip(s.contrast, -1, 1))
        lut = np.clip(_X - (0.9 * c) * (_X * (1 - _X) * (1 - 2 * _X)), 0.0, 1.0)
        _apply_lut(img, lut.astype(np.float32))

    # 6. Vibrance boosts dull colors more than strong ones. Saturation boosts all equally.
    #    Like Lightroom, vibrance mostly skips skin, so faces don't turn orange/yellow.
    if s.vibrance or s.saturation:
        for y0 in range(0, h, CHUNK_ROWS):
            _vibrance_strip(img[y0:y0 + CHUNK_ROWS], s.vibrance, s.saturation, s.protect_skin)

    # 6b. Color mixer (one color at a time), then color grading (shadows / midtones / highlights).
    #     Grading comes last, as in Lightroom, and mostly skips skin so faces stay natural.
    hsl = np.array([[getattr(s, f"{b}_{p}") for p in ("hue", "sat", "lum")] for b in HSL_BANDS],
                   dtype=np.float32)
    grades = [(a, hue, zone) for a, hue, zone in (
        (s.grade_shadows, s.grade_shadows_hue, "shadows"),
        (s.grade_midtones, s.grade_midtones_hue, "midtones"),
        (s.grade_highlights, s.grade_highlights_hue, "highlights")) if a > 0]
    if hsl.any() or grades:
        for y0 in range(0, h, CHUNK_ROWS):  # in strips: each needs several temporary copies
            _color_strip(img[y0:y0 + CHUNK_ROWS], hsl, grades, s.protect_skin)

    # 7. Noise reduction blurs color noise (blotches). Sharpen boosts edges in brightness only.
    #    Both work on the brightness/color split, so neither creates color fringes.
    if s.noise_reduction > 0 or s.sharpen > 0:
        lum = luminance(img)
        if s.noise_reduction > 0:
            # Color is blurred at half size: the eye barely sees color detail, and it's 4x faster.
            sigma = (1 + 2 * s.noise_reduction) / 2
            red = lum + _half_res_blur(img[..., 0] - lum, sigma)
            blue = lum + _half_res_blur(img[..., 2] - lum, sigma)
            img[..., 0] = red
            img[..., 2] = blue
            img[..., 1] = (lum - LUMA[0] * red - LUMA[2] * blue) / LUMA[1]
            del red, blue
        # Detail = brightness minus its blur. Sharpen adds it; noise reduction subtracts some.
        amount = 1.5 * s.sharpen - 0.5 * s.noise_reduction
        if amount:
            detail = lum - ndimage.gaussian_filter(lum, sigma=1.0, truncate=3.0)
            detail *= amount
            img += detail[..., None]
            del detail
        np.clip(img, 0.0, 1.0, out=img)
        del lum

    # 8. Vignette: darken (positive) or lighten (negative) the corners.
    if s.vignette:
        y = np.linspace(-1, 1, h, dtype=np.float32)[:, None]
        x = np.linspace(-1, 1, w, dtype=np.float32)[None, :]
        r2 = (x * x + y * y) / 2
        img *= (1.0 - 0.6 * s.vignette * r2 ** 1.5)[..., None]
        np.clip(img, 0.0, 1.0, out=img)

    return img


CROP_POSITIONS = {
    "center": (0.5, 0.5), "top": (0.5, 0.0), "bottom": (0.5, 1.0), "left": (0.0, 0.5), "right": (1.0, 0.5),
}


def parse_crop_pos(pos: str) -> tuple[float, float]:
    """"top", "left", ... or "x,y" where 0,0 keeps the top-left corner and 1,1 the bottom-right."""
    if pos in CROP_POSITIONS:
        return CROP_POSITIONS[pos]
    x, y = (float(n) for n in pos.split(","))
    return min(max(x, 0.0), 1.0), min(max(y, 0.0), 1.0)


def crop_box(h: int, w: int, ratio: str, pos: str = "center",
             zoom: float = 1.0) -> tuple[int, int, int, int]:
    """(x0, y0, width, height) of a width:height crop like "4:5", placed by pos.

    zoom < 1 keeps a smaller box (0.8 = 80% of the largest crop's width and height),
    so pos can move the subject onto a thirds line instead of only trimming one edge.
    """
    a, b = (float(n) for n in ratio.split(":")) if ratio else (w, h)
    target = a / b
    ax, ay = parse_crop_pos(pos)
    cw, ch = (h * target, h) if w / h > target else (w, w / target)
    zoom = min(max(zoom, 0.3), 1.0)
    cw, ch = int(round(cw * zoom)), int(round(ch * zoom))
    return int(round((w - cw) * ax)), int(round((h - ch) * ay)), cw, ch


def crop_to_ratio(img: np.ndarray, ratio: str, pos: str = "center", zoom: float = 1.0) -> np.ndarray:
    x0, y0, cw, ch = crop_box(*img.shape[:2], ratio, pos, zoom)
    return img[y0:y0 + ch, x0:x0 + cw]

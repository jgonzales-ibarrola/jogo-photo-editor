"""The editing pipeline. Images are float32 RGB arrays in 0..1, gamma-encoded."""

from __future__ import annotations

import numpy as np
from PIL import Image
from scipy import ndimage

from .settings import Settings

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
    if s.vibrance or s.saturation:
        lum = luminance(img)[..., None]
        r, g, b = img[..., 0], img[..., 1], img[..., 2]
        chroma = np.maximum(np.maximum(r, g), b)
        chroma -= np.minimum(np.minimum(r, g), b)
        chroma = chroma[..., None]
        chroma *= 2.0
        np.clip(chroma, 0, 1, out=chroma)
        factor = np.float32(1.0 + s.saturation + s.vibrance) - np.float32(s.vibrance) * chroma
        np.clip(factor, 0.0, None, out=factor)
        img -= lum
        img *= factor
        img += lum
        np.clip(img, 0.0, 1.0, out=img)
        del lum, chroma, factor

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


def crop_to_ratio(img: np.ndarray, ratio: str) -> np.ndarray:
    """Center-crop to width:height, e.g. "4:5" (tall) or "16:9" (wide)."""
    a, b = (float(n) for n in ratio.split(":"))
    h, w = img.shape[:2]
    target = a / b
    if w / h > target:
        new_w = int(round(h * target))
        x0 = (w - new_w) // 2
        return img[:, x0:x0 + new_w]
    new_h = int(round(w / target))
    y0 = (h - new_h) // 2
    return img[y0:y0 + new_h, :]

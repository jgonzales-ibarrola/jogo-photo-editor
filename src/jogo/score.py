"""Aesthetic score: how much the average person would like a photo, 1-10.

Three models trained on human ratings (docs/08-references.md), averaged because each one alone is noisy:
  nima       Google NIMA, trained on AVA (255k photos, ~200 ratings each)
  musiq-ava  MUSIQ, a newer model on the same AVA ratings
  laion_aes  LAION aesthetic predictor, trained on AVA + other human-rated sets

Needs the optional extra: pip install -e .[score]  (PyTorch + pyiqa, ~1 GB with weights).
"""

from __future__ import annotations

import os
from pathlib import Path

import numpy as np

from . import files

MODELS = ("nima", "musiq-ava", "laion_aes")
NOISE = 0.15  # Differences smaller than this are a tie: the models move more than that between near-copies.

_metrics: dict = {}


def available() -> bool:
    try:
        import pyiqa  # noqa: F401
        import torch  # noqa: F401
    except ImportError:
        return False
    return True


def _metric(name: str):
    if name not in _metrics:
        os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")
        import pyiqa
        _metrics[name] = pyiqa.create_metric(name, device="cpu")
    return _metrics[name]


def score_pixels(img: np.ndarray, models: tuple[str, ...] = MODELS) -> dict[str, float]:
    """Scores for an sRGB float image (0..1). Scored at 1024 px, like a phone screen."""
    import torch
    small = np.clip(files.resize_long_edge(img, 1024), 0, 1).astype(np.float32)
    x = torch.from_numpy(np.ascontiguousarray(small)).permute(2, 0, 1)[None]
    out = {}
    with torch.no_grad():
        for name in models:
            out[name] = round(float(_metric(name)(x)), 2)
    out["mean"] = round(sum(out[m] for m in models) / len(models), 2)
    return out


def score_file(path: Path, models: tuple[str, ...] = MODELS) -> dict[str, float]:
    return score_pixels(files.load(path).pixels, models)


def verdict(before: float, after: float) -> str:
    d = after - before
    if abs(d) < NOISE:
        return "same (within noise)"
    return "better" if d > 0 else "worse"

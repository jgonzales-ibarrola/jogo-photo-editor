"""Edit settings, presets and user preferences."""

from __future__ import annotations

import tomllib
from dataclasses import dataclass, fields, replace
from importlib import resources
from pathlib import Path

# Every slider goes from -1 to +1 and 0 means "no change", except exposure (in EV stops).
SLIDERS = (
    "exposure", "temperature", "tint", "contrast", "highlights", "shadows",
    "whites", "blacks", "clarity", "vibrance", "saturation",
    "sharpen", "noise_reduction", "vignette", "grade_shadows", "grade_highlights",
)
# Color grading hues are angles on the color wheel (0 red, 30 orange, 60 yellow, 120 green,
# 180 cyan/teal, 210 blue, 300 magenta). They replace, not add.
HUES = ("grade_shadows_hue", "grade_highlights_hue")


@dataclass(frozen=True)
class Settings:
    auto: bool = True            # Analyze the photo and fix exposure, levels and white balance.
    auto_wb: bool = True         # Let auto correct color casts. Turn off for sunsets.
    auto_strength: float = 1.0   # 0..1, how much of the auto fix to apply.
    exposure: float = 0.0
    temperature: float = 0.0
    tint: float = 0.0
    contrast: float = 0.0
    highlights: float = 0.0
    shadows: float = 0.0
    whites: float = 0.0
    blacks: float = 0.0
    clarity: float = 0.0
    vibrance: float = 0.0
    saturation: float = 0.0
    sharpen: float = 0.0
    noise_reduction: float = 0.0
    vignette: float = 0.0
    grade_shadows: float = 0.0         # 0..1, how strongly to tint the shadows
    grade_shadows_hue: float = 200.0   # tint color for shadows (default: teal-blue)
    grade_highlights: float = 0.0      # 0..1, how strongly to tint the highlights
    grade_highlights_hue: float = 40.0 # tint color for highlights (default: warm orange)

    def plus(self, other: dict[str, float]) -> "Settings":
        """Add slider values on top of these settings (used to stack auto + preset + manual)."""
        return replace(self, **{k: getattr(self, k) + v for k, v in other.items() if v})


@dataclass(frozen=True)
class Preset:
    name: str
    description: str
    settings: Settings


def _preset_from_toml(name: str, text: str) -> Preset:
    data = tomllib.loads(text)
    known = {f.name for f in fields(Settings)}
    unknown = set(data) - known - {"description"}
    if unknown:
        raise ValueError(f"Preset '{name}' has unknown keys: {', '.join(sorted(unknown))}")
    values = {k: v for k, v in data.items() if k in known}
    return Preset(name, data.get("description", ""), Settings(**values))


def load_presets(user_dir: Path | None = None) -> dict[str, Preset]:
    """Built-in presets, then any *.toml in user_dir (same name overrides a built-in)."""
    presets: dict[str, Preset] = {}
    for entry in resources.files("jogo.presets").iterdir():
        if entry.name.endswith(".toml"):
            name = entry.name.removesuffix(".toml")
            presets[name] = _preset_from_toml(name, entry.read_text(encoding="utf-8"))
    if user_dir and user_dir.is_dir():
        for path in sorted(user_dir.glob("*.toml")):
            presets[path.stem] = _preset_from_toml(path.stem, path.read_text(encoding="utf-8"))
    return presets


DEFAULT_PREFS = {
    "preset": "natural",
    "format": "jpg",
    "quality": 92,
    "output_dir": "photos/out",
    "input_dir": "photos/in",
    "resize": 0,
    "crop": "",
    "crop_pos": "center",
    "strip_location": True,
    "keep_metadata": True,
}


def load_prefs(path: Path = Path("jogo.toml")) -> dict:
    prefs = dict(DEFAULT_PREFS)
    if path.is_file():
        prefs.update(tomllib.loads(path.read_text(encoding="utf-8")).get("defaults", {}))
    return prefs

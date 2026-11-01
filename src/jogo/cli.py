"""Command line: jogo edit | try | grid | info | score | presets."""

from __future__ import annotations

import argparse
import sys
import time
from dataclasses import replace
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

from . import __version__, adjust, auto, files
from .settings import HUES, SLIDERS, Settings, load_prefs, load_presets

USER_PRESETS = Path("my-presets")


def _collect(paths: list[str], default_dir: str) -> list[Path]:
    targets = [Path(p) for p in paths] or [Path(default_dir)]
    found: list[Path] = []
    for t in targets:
        if t.is_dir():
            found += sorted(p for p in t.iterdir() if p.suffix.lower() in files.SUPPORTED)
        elif t.is_file():
            found.append(t)
        else:
            print(f"Not found: {t}", file=sys.stderr)
    return found


def _manual_offsets(args: argparse.Namespace) -> dict[str, float]:
    return {k: v for k in SLIDERS if (v := getattr(args, k, None)) is not None}


def edit_pixels(img: np.ndarray, settings: Settings, manual: dict[str, float] | None = None,
                verbose: bool = False) -> np.ndarray:
    """Auto analysis (if on), then preset + manual sliders. Edits img in place and returns it."""
    analysis = None
    final = settings
    if settings.auto:
        analysis = auto.analyze(img, settings.auto_wb, settings.auto_strength)
        final = final.plus(analysis.offsets)
        if verbose:
            for note in analysis.notes:
                print(f"    auto: {note}")
    final = final.plus(manual or {})
    img = adjust.apply(img, final, analysis.wb_gains if analysis else None)
    # Checked after the look, because the look's color mixer and grade can move skin too.
    if settings.auto and settings.auto_skin:
        faces = adjust.find_faces(img)
        shift = adjust.skin_line_check(img, faces)
        if shift:
            adjust.shift_skin(img, shift, faces)
            if verbose:
                way = "yellow" if shift < 0 else "red/pink"
                print(f"    auto: Skin on {len(faces)} face(s) was too {way} -> hue {shift:+.1f} deg "
                      "toward the skin tone line.")
    return img


def process(path: Path, settings: Settings, manual: dict[str, float], crop: str = "",
            resize: int = 0, crop_pos: str = "center",
            flat_raw: bool = False, crop_zoom: float = 1.0) -> tuple[np.ndarray, files.Loaded]:
    loaded = files.load(path, flat_raw)
    img = loaded.pixels
    if crop or crop_zoom < 1:
        img = np.ascontiguousarray(adjust.crop_to_ratio(img, crop, crop_pos, crop_zoom))
    # Edit at full size, shrink last: sharpening a shrunken photo makes it look crunchy.
    img = edit_pixels(img, settings, manual, verbose=True)
    return files.resize_long_edge(img, resize), loaded


def cmd_edit(args: argparse.Namespace, prefs: dict) -> int:
    presets = load_presets(USER_PRESETS)
    name = args.preset or prefs["preset"]
    if name not in presets:
        print(f"Unknown preset '{name}'. Run: jogo presets", file=sys.stderr)
        return 2
    settings = presets[name].settings
    if args.no_auto:
        settings = replace(settings, auto=False)
    settings = replace(settings, **{h: v for h in HUES if (v := getattr(args, h)) is not None})

    photos = _collect(args.paths, prefs["input_dir"])
    if not photos:
        print(f"No photos found. Put HEIC/DNG/JPG files in {prefs['input_dir']}/ or name them.")
        return 1

    out_dir = Path(args.out or prefs["output_dir"])
    fmt = args.format or prefs["format"]
    resize = 2048 if args.preview else (args.resize if args.resize is not None else prefs["resize"])
    crop = args.crop if args.crop is not None else prefs["crop"]
    crop_pos = args.crop_pos or prefs["crop_pos"]
    manual = _manual_offsets(args)

    for i, path in enumerate(photos, 1):
        print(f"[{i}/{len(photos)}] {path.name}  (preset: {name})")
        start = time.perf_counter()
        try:
            img, loaded = process(path, settings, manual, crop, resize, crop_pos, args.flat_raw, args.crop_zoom)
            saved = files.save(
                img, out_dir / f"{path.stem}_{name}", fmt, args.quality or prefs["quality"],
                loaded.exif, loaded.icc,
                strip_location=not args.keep_location and prefs["strip_location"],
                keep_metadata=prefs["keep_metadata"],
            )
        except Exception as exc:  # One bad file shouldn't stop a batch.
            print(f"    FAILED: {exc}", file=sys.stderr)
            continue
        h, w = img.shape[:2]
        print(f"    saved {saved}  ({w}x{h}, {w * h / 1e6:.0f} MP, {time.perf_counter() - start:.1f}s)")
    return 0


def _label(img: np.ndarray, text: str) -> Image.Image:
    pil = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8), "RGB")
    draw = ImageDraw.Draw(pil)
    draw.rectangle((0, 0, pil.width, 28), fill=(0, 0, 0))
    draw.text((8, 7), text, fill=(255, 255, 255))
    return pil


def cmd_try(args: argparse.Namespace, prefs: dict) -> int:
    """Run every preset on a small copy and build one comparison sheet."""
    path = Path(args.photo)
    presets = load_presets(USER_PRESETS)
    original = files.resize_long_edge(files.load(path).pixels, 800)
    tiles = [_label(original, "original")]
    for name, preset in presets.items():
        tiles.append(_label(edit_pixels(original.copy(), preset.settings), name))

    cols = 3
    tw, th = tiles[0].size
    rows = (len(tiles) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * tw, rows * th), (20, 20, 20))
    for i, tile in enumerate(tiles):
        sheet.paste(tile, ((i % cols) * tw, (i // cols) * th))
    out = Path(args.out or prefs["output_dir"]) / f"{path.stem}_compare.jpg"
    out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out, "JPEG", quality=88)
    print(f"Saved comparison sheet: {out}")
    print(f"Pick one, then run:  jogo edit \"{path}\" --preset <name>")
    return 0


def cmd_grid(args: argparse.Namespace, prefs: dict) -> int:
    """Draw composition guides on a small copy. With --crop, the part that would be cut is darkened."""
    path = Path(args.photo)
    img = files.resize_long_edge(files.load(path).pixels, 1600)
    pil = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8), "RGB")
    h, w = img.shape[:2]
    x0, y0, cw, ch = (0, 0, w, h)
    if args.crop or args.crop_zoom < 1:
        x0, y0, cw, ch = adjust.crop_box(h, w, args.crop, args.crop_pos, args.crop_zoom)
        shade = Image.new("L", (w, h), 140)
        ImageDraw.Draw(shade).rectangle((x0, y0, x0 + cw - 1, y0 + ch - 1), fill=0)
        pil.paste((0, 0, 0), mask=shade)

    draw = ImageDraw.Draw(pil)
    guides = {
        "thirds": ((1 / 3, 2 / 3), (255, 255, 255)),
        "golden": ((0.382, 0.618), (255, 210, 0)),
    }
    for name in args.guides.split(","):
        if name == "diagonals":
            color = (0, 230, 255)
            draw.line((x0, y0, x0 + cw, y0 + ch), fill=color, width=2)
            draw.line((x0 + cw, y0, x0, y0 + ch), fill=color, width=2)
        elif name in guides:
            fracs, color = guides[name]
            for f in fracs:
                draw.line((x0 + f * cw, y0, x0 + f * cw, y0 + ch), fill=color, width=2)
                draw.line((x0, y0 + f * ch, x0 + cw, y0 + f * ch), fill=color, width=2)
    draw.rectangle((0, 0, w, 26), fill=(0, 0, 0))
    draw.text((8, 7), "white = thirds   yellow = golden ratio   cyan = diagonals"
              + (f"   crop {args.crop} ({args.crop_pos})" if args.crop else ""), fill=(255, 255, 255))

    suffix = f"_grid_{args.crop.replace(':', 'x')}_{args.crop_pos.replace(',', '-')}" if args.crop else "_grid"
    out = Path(args.out or prefs["output_dir"]) / f"{path.stem}{suffix}.jpg"
    out.parent.mkdir(parents=True, exist_ok=True)
    pil.save(out, "JPEG", quality=88)
    print(f"Saved composition guide: {out}")
    return 0


KIND_LABELS = {"raw": "RAW (DNG)", "raw-apple": "ProRAW (Apple's finished photo)", "image": "processed image"}


def cmd_info(args: argparse.Namespace, prefs: dict) -> int:
    path = Path(args.photo)
    loaded = files.load(path)
    h, w = loaded.pixels.shape[:2]
    print(f"{path.name}: {w}x{h} ({w * h / 1e6:.0f} MP), {KIND_LABELS[loaded.kind]}")
    for k, v in files.describe_exif(loaded.exif).items():
        print(f"  {k}: {v}")
    a = auto.analyze(loaded.pixels)
    print(f"  Middle brightness: {a.median:.2f} (about {auto.TARGET_MIDTONE} is typical)")
    print(f"  Near-black pixels: {a.dark_pct:.1f}%   Near-white pixels: {a.bright_pct:.1f}%")
    print("What auto mode would do:")
    for note in a.notes:
        print(f"  - {note}")
    return 0


def _original_of(edited: Path, originals: list[Path]) -> Path | None:
    """photos/out/.../IMG_0185_gold.jpg -> photos/in/IMG_0185.JPG (longest matching stem)."""
    matches = [o for o in originals if edited.stem.startswith(o.stem + "_")]
    return max(matches, key=lambda o: len(o.stem)) if matches else None


def cmd_score(args: argparse.Namespace, prefs: dict) -> int:
    """Average-person aesthetic score (1-10) per photo, best first. Optionally compare with the original."""
    from . import score
    if not score.available():
        print("Scoring needs PyTorch + pyiqa. Install with: .venv\\Scripts\\python -m pip install -e .[score]",
              file=sys.stderr)
        return 2
    photos = _collect(args.paths, prefs["output_dir"])
    if not photos:
        print("No photos found.")
        return 1
    originals = _collect([args.vs], "") if args.vs else []

    rows = []
    for i, path in enumerate(photos, 1):
        print(f"[{i}/{len(photos)}] {path.name}", file=sys.stderr)
        s = score.score_file(path)
        orig = _original_of(path, originals) if originals else None
        before = score.score_file(orig)["mean"] if orig else None
        rows.append((path, s, before))

    rows.sort(key=lambda r: r[1]["mean"], reverse=True)
    names = " ".join(f"{m:>9}" for m in score.MODELS)
    print(f"\n{'#':>3}  {'score':>5}  {names}  {'vs original':<26} photo")
    for rank, (path, s, before) in enumerate(rows, 1):
        per = " ".join(f"{s[m]:9.2f}" for m in score.MODELS)
        vs = f"{s['mean'] - before:+.2f} {score.verdict(before, s['mean'])}" if before is not None else ""
        print(f"{rank:>3}  {s['mean']:5.2f}  {per}  {vs:<26} {path.name}")
    if args.csv:
        with open(args.csv, "w", encoding="utf-8") as f:
            f.write("photo,score," + ",".join(score.MODELS) + ",original\n")
            for path, s, before in rows:
                f.write(f"{path.name},{s['mean']}," + ",".join(str(s[m]) for m in score.MODELS)
                        + f",{'' if before is None else before}\n")
        print(f"Saved {args.csv}")
    print(f"\nScore = average of {', '.join(score.MODELS)} (trained on human ratings, docs/08). "
          f"Differences under {score.NOISE} are a tie.")
    return 0


def cmd_presets(args: argparse.Namespace, prefs: dict) -> int:
    for name, preset in load_presets(USER_PRESETS).items():
        mark = " (default)" if name == prefs["preset"] else ""
        print(f"{name:<12}{preset.description}{mark}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="jogo", description="Automatic photo editor for iPhone HEIC and ProRAW.")
    p.add_argument("--version", action="version", version=f"jogo {__version__}")
    sub = p.add_subparsers(dest="command", required=True)

    e = sub.add_parser("edit", help="Edit photos and save copies (originals are never changed).")
    e.add_argument("paths", nargs="*", help="Files or folders. Default: input_dir from jogo.toml.")
    e.add_argument("-p", "--preset", help="Look to apply. See: jogo presets")
    e.add_argument("-o", "--out", help="Output folder.")
    e.add_argument("-f", "--format", choices=["jpg", "heic", "tif"])
    e.add_argument("-q", "--quality", type=int, help="1-100 for jpg/heic.")
    e.add_argument("--crop", help='Aspect ratio, e.g. "4:5", "1:1", "16:9".')
    e.add_argument("--crop-pos", help='Which part the crop keeps: center, top, bottom, left, right, or "x,y" (0-1).')
    e.add_argument("--crop-zoom", type=float, default=1.0,
                   help="Crop tighter: 0.8 keeps 80%% of the width and height. Use with --crop-pos to place the subject.")
    e.add_argument("--resize", type=int, help="Long edge in pixels. 0 = full size.")
    e.add_argument("--preview", action="store_true", help="Quick 2048px version to check the look.")
    e.add_argument("--no-auto", action="store_true", help="Skip auto fixes; use only preset + your sliders.")
    e.add_argument("--keep-location", action="store_true", help="Keep GPS location in the saved file.")
    e.add_argument("--flat-raw", action="store_true",
                   help="ProRAW: decode the raw data yourself instead of starting from Apple's finished photo. "
                        "Flatter; only for rescuing badly blown or very dark shots.")
    sliders = e.add_argument_group("sliders (added on top of auto + preset)")
    for name in SLIDERS:
        sliders.add_argument(f"--{name.replace('_', '-')}", dest=name, type=float, metavar="N")
    for name in HUES:
        sliders.add_argument(f"--{name.replace('_', '-')}", dest=name, type=float, metavar="DEG",
                             help="Color wheel angle 0-360 (replaces the preset's hue).")
    e.set_defaults(func=cmd_edit)

    g = sub.add_parser("grid", help="Draw composition guides (thirds, golden ratio, diagonals), optionally with a crop.")
    g.add_argument("photo")
    g.add_argument("--crop", help='Show this crop, e.g. "4:5".')
    g.add_argument("--crop-pos", default="center")
    g.add_argument("--crop-zoom", type=float, default=1.0)
    g.add_argument("--guides", default="thirds,golden,diagonals", help="Comma list: thirds, golden, diagonals.")
    g.add_argument("-o", "--out")
    g.set_defaults(func=cmd_grid)

    t = sub.add_parser("try", help="Preview every preset on one photo in a single comparison image.")
    t.add_argument("photo")
    t.add_argument("-o", "--out")
    t.set_defaults(func=cmd_try)

    i = sub.add_parser("info", help="Show camera settings and what's wrong/right with a photo.")
    i.add_argument("photo")
    i.set_defaults(func=cmd_info)

    sc = sub.add_parser("score", help="Score photos 1-10 by average human taste (needs the [score] extra).")
    sc.add_argument("paths", nargs="*", help="Files or folders. Default: output_dir.")
    sc.add_argument("--vs", help="Folder of originals (e.g. photos/in) to compare each edit with.")
    sc.add_argument("--csv", help="Also save the table to this CSV file.")
    sc.set_defaults(func=cmd_score)

    ps = sub.add_parser("presets", help="List available presets.")
    ps.set_defaults(func=cmd_presets)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args, load_prefs())


if __name__ == "__main__":
    raise SystemExit(main())

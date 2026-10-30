"""Reading iPhone HEIC / ProRAW DNG / JPEG files and saving the result with metadata."""

from __future__ import annotations

import io
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pillow_heif
import rawpy
import tifffile
from PIL import Image, ImageCms, ImageOps

pillow_heif.register_heif_opener()

RAW_EXTS = {".dng"}
IMAGE_EXTS = {".heic", ".heif", ".jpg", ".jpeg", ".png", ".tif", ".tiff"}
SUPPORTED = RAW_EXTS | IMAGE_EXTS

GPS_IFD = 0x8825
EXIF_IFD = 0x8769
ORIENTATION = 0x0112
# Tags copied from a DNG: camera, date, lens and shot settings.
BASIC_TAGS = (0x010F, 0x0110, 0x0131, 0x0132)
BASIC_EXIF_TAGS = (0x829A, 0x829D, 0x8827, 0x9003, 0x920A, 0xA405, 0xA434)

SRGB_ICC = ImageCms.ImageCmsProfile(ImageCms.createProfile("sRGB")).tobytes()


def baseline_exposure(path: Path) -> float:
    """The DNG's BaselineExposure tag in EV (how much the camera says to brighten), 0 if missing."""
    try:
        with tifffile.TiffFile(path) as tif:
            tag = tif.pages[0].tags.get(50730)
            num, den = tag.value
            return num / den
    except Exception:
        return 0.0


@dataclass
class Loaded:
    pixels: np.ndarray       # float32 RGB, 0..1
    exif: Image.Exif | None
    icc: bytes | None
    kind: str                # "raw", "raw-apple" (Apple's finished photo from a ProRAW) or "image"


def _basic_exif(src: Image.Exif) -> Image.Exif:
    out = Image.Exif()
    for tag in BASIC_TAGS:
        if tag in src:
            out[tag] = src[tag]
    src_ifd = src.get_ifd(EXIF_IFD)
    dst_ifd = out.get_ifd(EXIF_IFD)
    for tag in BASIC_EXIF_TAGS:
        if tag in src_ifd:
            dst_ifd[tag] = src_ifd[tag]
    return out


def _apple_preview(path: Path) -> Image.Image | None:
    """ProRAW stores Apple's finished photo (tone mapping, sky/skin masks, color) as a full-size JPEG
    in the first IFD. That's the iPhone look; a plain raw decode can't rebuild it and looks flat."""
    try:
        with tifffile.TiffFile(path) as tif:
            page = tif.pages[0]
            if page.subfiletype != 1 or page.compression != 7 or len(page.dataoffsets) != 1:
                return None
            if max(page.shape[:2]) < 3000:  # only a thumbnail, not worth editing
                return None
            orientation = page.tags[274].value if 274 in page.tags else 1
            tif.filehandle.seek(page.dataoffsets[0])
            data = tif.filehandle.read(page.databytecounts[0])
        im = Image.open(io.BytesIO(data))
        im.load()
        im.getexif()[ORIENTATION] = orientation
        return ImageOps.exif_transpose(im)
    except Exception:
        return None


def load(path: Path, flat_raw: bool = False) -> Loaded:
    ext = path.suffix.lower()
    if ext in RAW_EXTS and not flat_raw and (im := _apple_preview(path)) is not None:
        exif = None
        try:
            with Image.open(path) as src:
                exif = _basic_exif(src.getexif())
        except Exception:
            pass
        pixels = np.asarray(im.convert("RGB"), dtype=np.float32) / 255.0
        return Loaded(np.ascontiguousarray(pixels), exif, im.info.get("icc_profile"), "raw-apple")
    if ext in RAW_EXTS:
        with rawpy.imread(str(path)) as raw:
            rgb = raw.postprocess(
                use_camera_wb=True,
                no_auto_bright=True,
                # rawpy ignores the DNG's BaselineExposure. iPhone ProRAW relies on it (often +2..+5 EV),
                # so without it many shots come out nearly black. rawpy allows -2..+3 EV.
                exp_shift=float(np.clip(2.0 ** baseline_exposure(path), 0.25, 8.0)),
                exp_preserve_highlights=1.0,
                output_bps=16,
                output_color=rawpy.ColorSpace.sRGB,
            )
        exif = None
        try:  # DNG is TIFF-based, so Pillow can usually read its tags.
            with Image.open(path) as im:
                exif = _basic_exif(im.getexif())
        except Exception:
            pass
        pixels = rgb.astype(np.float32)
        pixels /= 65535.0
        return Loaded(pixels, exif, SRGB_ICC, "raw")

    with Image.open(path) as im:
        exif = im.getexif()
        icc = im.info.get("icc_profile")
        im = ImageOps.exif_transpose(im)  # iPhone stores rotation as a tag; bake it in.
        exif[ORIENTATION] = 1
        if im.mode in ("I;16", "I;16B", "I"):
            arr = np.asarray(im, dtype=np.float32) / 65535.0
            pixels = np.repeat(arr[..., None], 3, axis=2)
        else:
            pixels = np.asarray(im.convert("RGB"), dtype=np.float32) / 255.0
    return Loaded(np.ascontiguousarray(pixels), exif, icc, "image")


def resize_long_edge(img: np.ndarray, long_edge: int) -> np.ndarray:
    h, w = img.shape[:2]
    if not long_edge or max(h, w) <= long_edge:
        return img
    scale = long_edge / max(h, w)
    size = (max(1, round(w * scale)), max(1, round(h * scale)))
    chans = [np.asarray(Image.fromarray(img[..., c]).resize(size, Image.LANCZOS)) for c in range(3)]
    return np.clip(np.stack(chans, axis=2), 0, 1).astype(np.float32)


def save(img: np.ndarray, path: Path, fmt: str, quality: int, exif: Image.Exif | None,
         icc: bytes | None, strip_location: bool, keep_metadata: bool) -> Path:
    path = path.with_suffix("." + fmt)
    path.parent.mkdir(parents=True, exist_ok=True)

    exif_bytes = b""
    if keep_metadata and exif is not None:
        if strip_location and GPS_IFD in exif:
            del exif[GPS_IFD]
        exif_bytes = exif.tobytes()

    if fmt == "tif":
        data = (np.clip(img, 0, 1) * 65535 + 0.5).astype(np.uint16)
        extratags = [(34675, 7, len(icc), icc, True)] if icc else []
        tifffile.imwrite(path, data, photometric="rgb", compression="zlib", extratags=extratags)
        return path

    pil = Image.fromarray((np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8), "RGB")
    options = {"quality": quality}
    if exif_bytes:
        options["exif"] = exif_bytes
    if icc:
        options["icc_profile"] = icc
    if fmt == "jpg":
        pil.save(path, "JPEG", subsampling=0 if quality >= 90 else 2, **options)
    elif fmt == "heic":
        pil.save(path, "HEIF", **options)
    else:
        raise ValueError(f"Unknown format '{fmt}'. Use jpg, heic or tif.")
    return path


def describe_exif(exif: Image.Exif | None) -> dict[str, str]:
    """Human-readable camera settings for `jogo info`."""
    if exif is None:
        return {}
    ifd = exif.get_ifd(EXIF_IFD)
    out = {}
    if 0x0110 in exif:
        out["Camera"] = str(exif[0x0110])
    if 0xA434 in ifd:
        out["Lens"] = str(ifd[0xA434])
    if 0x9003 in ifd:
        out["Taken"] = str(ifd[0x9003])
    if 0x829A in ifd:
        t = float(ifd[0x829A])
        out["Shutter"] = f"1/{round(1 / t)} s" if 0 < t < 1 else f"{t:g} s"
    if 0x829D in ifd:
        out["Aperture"] = f"f/{float(ifd[0x829D]):.1f}"
    if 0x8827 in ifd:
        out["ISO"] = str(ifd[0x8827])
    if 0xA405 in ifd:
        out["Focal length (35mm equiv.)"] = f"{ifd[0xA405]} mm"
    out["Location saved in file"] = "yes" if GPS_IFD in exif else "no"
    return out

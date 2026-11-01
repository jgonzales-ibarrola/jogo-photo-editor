"""MIT-Adobe FiveK study: what do 5 trained photographers do, and how close are our looks?

  python research/fivek.py index            # read the 5,000-photo list with scene labels
  python research/fivek.py fetch --n 300    # balanced sample: raw input + 5 expert edits (small copies)
  python research/fivek.py status           # how many sample photos are complete (fetch resumes)
  python research/fivek.py measure          # tone/color stats: input, each expert, each of our presets
  python research/fivek.py report           # expert average vs our looks, per scene

Data lives in research/data/ (git-ignored). Big expert TIFFs are shrunk to 1024 px 16-bit PNGs and
deleted. Source: https://data.csail.mit.edu/graphics/fivek/ (see docs/08-references.md).
"""

from __future__ import annotations

import argparse
import csv
import html
import random
import re
import sys
import urllib.parse
import urllib.request
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from jogo import adjust, cli, files  # noqa: E402
from jogo.settings import load_presets  # noqa: E402

BASE = "https://data.csail.mit.edu/graphics/fivek/"
DATA = Path(__file__).resolve().parent / "data" / "fivek"
EXPERTS = "abcde"
EDGE = 1024

# ProPhoto RGB (D50) -> XYZ -> Bradford D50->D65 -> linear sRGB.
PROPHOTO_TO_SRGB = (
    np.array([[3.2404542, -1.5371385, -0.4985314], [-0.9692660, 1.8760108, 0.0415560],
              [0.0556434, -0.2040259, 1.0572252]])
    @ np.array([[0.9555766, -0.0230393, 0.0631636], [-0.0282895, 1.0099416, 0.0210077],
                [0.0122982, -0.0204830, 1.3299098]])
    @ np.array([[0.7976749, 0.1351917, 0.0313534], [0.2880402, 0.7118741, 0.0000857],
                [0.0, 0.0, 0.8252100]])
).astype(np.float32)


# ---------- index ----------

def cmd_index(args) -> None:
    page = urllib.request.urlopen(BASE, timeout=120).read().decode("utf-8", "replace")
    rows = []
    for tr in re.findall(r"<tr>(.*?)</tr>", page, re.S):
        name = re.search(r"img/dng/([^\"]+)\.dng", tr)
        if not name:
            continue
        labels = dict(re.findall(r"<td>(Subject|Light|Location|Time):<br>([^<]*)</td>", tr))
        rows.append({"name": name.group(1), **{k.lower(): html.unescape(v).strip() for k, v in labels.items()}})
    DATA.mkdir(parents=True, exist_ok=True)
    with open(DATA / "index.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["name", "subject", "light", "location", "time"])
        w.writeheader()
        w.writerows(rows)
    groups = defaultdict(int)
    for r in rows:
        groups[(r["subject"], r["location"], r["time"], r["light"])] += 1
    print(f"{len(rows)} photos, {len(groups)} scene groups -> {DATA / 'index.csv'}")


def read_index() -> list[dict]:
    with open(DATA / "index.csv", encoding="utf-8") as f:
        return list(csv.DictReader(f))


# ---------- fetch ----------

def sample(rows: list[dict], n: int, seed: int = 7) -> list[dict]:
    """Round-robin over scene groups so rare scenes (night, indoor people) are not drowned out."""
    rng = random.Random(seed)
    groups = defaultdict(list)
    for r in rows:
        if "unknown" in (r["subject"], r["location"]):
            continue  # no label = can't learn a scene rule from it
        groups[(r["subject"], r["location"], r["time"])].append(r)
    for g in groups.values():
        rng.shuffle(g)
    picked, keys = [], sorted(groups)
    while len(picked) < n and any(groups.values()):
        for k in keys:
            if groups[k] and len(picked) < n:
                picked.append(groups[k].pop())
    return picked


def _download(url: str, dest: Path) -> None:
    tmp = dest.with_suffix(dest.suffix + ".part")
    url = urllib.parse.quote(url, safe=":/")  # some names have spaces
    with urllib.request.urlopen(url, timeout=600) as r, open(tmp, "wb") as f:
        expected = int(r.headers.get("Content-Length") or 0)
        while chunk := r.read(1 << 20):
            f.write(chunk)
    if expected and tmp.stat().st_size != expected:  # the server sometimes ends a transfer early
        tmp.unlink()
        raise IOError(f"incomplete download ({url.rsplit('/', 1)[-1]}), rerun fetch to retry")
    tmp.replace(dest)


def prophoto_tiff_to_srgb(path: Path) -> np.ndarray:
    import tifffile
    img = tifffile.imread(path).astype(np.float32) / 65535.0
    img = files.resize_long_edge(img[..., :3], EDGE)
    lin = np.where(img < 16 / 512, img / 16, img ** 1.8)          # ProPhoto (ROMM) transfer curve
    lin = np.clip(lin @ PROPHOTO_TO_SRGB.T, 0, 1)
    return np.where(lin <= 0.0031308, 12.92 * lin, 1.055 * lin ** (1 / 2.4) - 0.055).astype(np.float32)


def save_png16(img: np.ndarray, path: Path) -> None:
    import tifffile  # 16-bit RGB without extra deps: a small uncompressed-free TIFF
    tifffile.imwrite(path, (np.clip(img, 0, 1) * 65535).astype(np.uint16), compression="zlib")


def fetch_one(row: dict) -> str:
    d = DATA / "photos" / row["name"]
    d.mkdir(parents=True, exist_ok=True)
    dng = d / "input.dng"
    if not dng.exists():
        _download(f"{BASE}img/dng/{row['name']}.dng", dng)
    for e in EXPERTS:
        small = d / f"expert_{e}.tif"
        if small.exists():
            continue
        big = d / f"big_{e}.tif"
        _download(f"{BASE}img/tiff16_{e}/{row['name']}.tif", big)
        save_png16(prophoto_tiff_to_srgb(big), small)
        big.unlink()
    return row["name"]


def cmd_fetch(args) -> None:
    picked = sample(read_index(), args.n)
    with open(DATA / "sample.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(picked[0]))
        w.writeheader()
        w.writerows(picked)
    done = 0
    with ThreadPoolExecutor(args.workers) as pool:
        for fut in [pool.submit(fetch_one, r) for r in picked]:
            try:
                name = fut.result()
                done += 1
                print(f"[{done}/{len(picked)}] {name}", flush=True)
            except Exception as e:  # keep going; a rerun resumes
                print(f"failed: {e}", flush=True)


# ---------- measure ----------

def to_lab(img: np.ndarray) -> np.ndarray:
    lin = np.where(img <= 0.04045, img / 12.92, ((img + 0.055) / 1.055) ** 2.4)
    xyz = lin @ np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]]).T
    xyz /= np.array([0.9505, 1.0, 1.089])
    f = np.where(xyz > 0.008856, np.cbrt(xyz), 7.787 * xyz + 16 / 116)
    return np.stack([116 * f[..., 1] - 16, 500 * (f[..., 0] - f[..., 1]), 200 * (f[..., 1] - f[..., 2])], -1)


STATS = ["L_median", "L_p05", "L_p95", "contrast", "chroma", "chroma_p90", "a", "b",
         "shadow_a", "shadow_b", "high_a", "high_b", "skin_hue"]


def stats(img: np.ndarray) -> dict[str, float]:
    """Brightness (L*), contrast, colorfulness (chroma), overall tint (a* green-red, b* blue-yellow),
    tint in shadows and highlights (= color grade), and face skin hue."""
    lab = to_lab(np.clip(img, 0, 1)).reshape(-1, 3)
    L, a, b = lab[:, 0], lab[:, 1], lab[:, 2]
    c = np.hypot(a, b)
    p05, p50, p95 = np.percentile(L, [5, 50, 95])
    sh, hi = L < 30, L > 70
    out = {"L_median": p50, "L_p05": p05, "L_p95": p95, "contrast": p95 - p05,
           "chroma": c.mean(), "chroma_p90": np.percentile(c, 90), "a": a.mean(), "b": b.mean(),
           "shadow_a": a[sh].mean() if sh.any() else np.nan, "shadow_b": b[sh].mean() if sh.any() else np.nan,
           "high_a": a[hi].mean() if hi.any() else np.nan, "high_b": b[hi].mean() if hi.any() else np.nan}
    faces = adjust.find_faces(img)
    hues = []
    for fx, fy, fw, fh in faces:
        h, w = img.shape[:2]
        crop = img[int((fy + fh * .3) * h):int((fy + fh * .8) * h), int((fx + fw * .2) * w):int((fx + fw * .8) * w)]
        hue, sat, v = adjust._to_hsv(np.clip(crop, 0, 1))
        hues.append(hue[adjust._skin(hue, sat, v) > 0.5])
    hues = np.concatenate(hues) if hues else np.empty(0)
    out["skin_hue"] = float(np.median(hues)) if hues.size >= 50 else np.nan
    return {k: round(float(v), 3) for k, v in out.items()}


def cmd_measure(args) -> None:
    import tifffile
    import time
    presets = load_presets(cli.USER_PRESETS)
    out = DATA / "stats.csv"
    fields = ["name", "subject", "light", "location", "time", "source"] + STATS
    done = {r["name"] for r in csv.DictReader(open(out, encoding="utf-8"))} if out.exists() and not args.fresh else set()
    if not done:
        with open(out, "w", newline="", encoding="utf-8") as f:
            csv.DictWriter(f, fieldnames=fields).writeheader()
    sample_rows = list(csv.DictReader(open(DATA / "sample.csv", encoding="utf-8")))
    for i, r in enumerate(sample_rows, 1):
        d = DATA / "photos" / r["name"]
        if r["name"] in done or not all((d / f"expert_{e}.tif").exists() for e in EXPERTS):
            continue
        t = time.perf_counter()
        base =files.resize_long_edge(files.load(d / "input.dng").pixels, EDGE)
        versions = {"input": base}
        for e in EXPERTS:
            versions[f"expert_{e}"] = tifffile.imread(d / f"expert_{e}.tif").astype(np.float32) / 65535
        for name, p in presets.items():
            versions[f"look_{name}"] = cli.edit_pixels(base.copy(), p.settings)
        rows = [{"name": r["name"], "subject": r["subject"], "light": r["light"], "location": r["location"],
                 "time": r["time"], "source": source, **stats(img)} for source, img in versions.items()]
        with open(out, "a", newline="", encoding="utf-8") as f:  # saved per photo: a rerun resumes
            csv.DictWriter(f, fieldnames=fields).writerows(rows)
        print(f"[{i}/{len(sample_rows)}] {r['name']}  {time.perf_counter() - t:.0f}s", flush=True)
    print(f"-> {out}")


# ---------- report ----------

# How much each stat matters when asking "which look is closest to the experts".
# Units: L* and chroma differences of ~3-5 are visible; tints of ~2 are visible.
WEIGHTS = {"L_median": 1 / 4, "contrast": 1 / 6, "chroma": 1 / 3, "a": 1 / 2, "b": 1 / 2,
           "shadow_b": 1 / 3, "high_b": 1 / 3}


def cmd_report(args) -> None:
    import statistics as st
    rows = list(csv.DictReader(open(DATA / "stats.csv", encoding="utf-8")))
    for r in rows:
        for k in STATS:
            r[k] = float(r[k]) if r[k] not in ("", "nan") else float("nan")
    by = defaultdict(lambda: defaultdict(list))  # scene -> source -> rows

    def scene(r):
        if r["time"] != "day":
            return f"night / {r['subject']}"
        return f"{r['location']} / {r['subject']}"

    for r in rows:
        src = "experts" if r["source"].startswith("expert_") else r["source"]
        by[scene(r)][src].append(r)
        by["ALL"][src].append(r)

    def mean(rs, k):
        vals = [x[k] for x in rs if x[k] == x[k]]
        return st.fmean(vals) if vals else float("nan")

    for sc in ["ALL"] + sorted(k for k in by if k != "ALL"):
        src = by[sc]
        n = len(src["input"])
        if n < 3:
            continue
        print(f"\n== {sc}  ({n} photos)")
        print(f"{'source':<18}" + "".join(f"{k:>11}" for k in STATS))
        target = {k: mean(src["experts"], k) for k in STATS}
        scored = []
        for s in ["input", "experts"] + sorted(k for k in src if k.startswith("look_")):
            m = {k: mean(src[s], k) for k in STATS}
            dist = sum(w * abs(m[k] - target[k]) for k, w in WEIGHTS.items() if m[k] == m[k])
            if s.startswith("look_"):
                scored.append((dist, s))
            print(f"{s:<18}" + "".join(f"{m[k]:11.1f}" for k in STATS) + f"   dist {dist:.2f}")
        scored.sort()
        print("closest to experts: " + ", ".join(f"{s[5:]} ({d:.2f})" for d, s in scored[:4]))


def cmd_status(args) -> None:
    picked = list(csv.DictReader(open(DATA / "sample.csv", encoding="utf-8")))
    done = sum(all((DATA / "photos" / r["name"] / f"expert_{e}.tif").exists() for e in EXPERTS) for r in picked)
    print(f"{done}/{len(picked)} photos complete ({100 * done / len(picked):.1f}%)")


def main() -> None:
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("index").set_defaults(f=cmd_index)
    sub.add_parser("status").set_defaults(f=cmd_status)
    f = sub.add_parser("fetch")
    f.add_argument("--n", type=int, default=300)
    f.add_argument("--workers", type=int, default=4)
    f.set_defaults(f=cmd_fetch)
    m = sub.add_parser("measure")
    m.add_argument("--fresh", action="store_true", help="Start over instead of resuming.")
    m.set_defaults(f=cmd_measure)
    sub.add_parser("report").set_defaults(f=cmd_report)
    args = p.parse_args()
    args.f(args)


if __name__ == "__main__":
    main()

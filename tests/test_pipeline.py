from dataclasses import replace

import numpy as np
import pytest
from PIL import Image

from jogo import adjust, auto, cli, files
from jogo.settings import Settings, load_presets


def _gradient(h=300, w=400, brightness=1.0):
    y, x = np.mgrid[0:h, 0:w].astype(np.float32)
    img = np.stack([x / w, y / h, 1 - x / w], axis=2) * brightness
    return np.ascontiguousarray(img.astype(np.float32))


@pytest.fixture
def heic_with_gps(tmp_path):
    exif = Image.Exif()
    exif[0x010F] = "Apple"
    exif[0x0112] = 6  # rotated 90 degrees, like a portrait iPhone shot
    exif.get_ifd(files.GPS_IFD)[2] = (14.0, 35.0, 0.0)  # latitude near Manila
    path = tmp_path / "IMG_0001.HEIC"
    pil = Image.fromarray((_gradient(brightness=0.4) * 255).astype(np.uint8))
    pil.save(path, "HEIF", exif=exif.tobytes())
    return path


def test_all_presets_load_and_run():
    presets = load_presets()
    assert {"natural", "vivid", "golden-hour", "bw", "night"} <= presets.keys()
    for preset in presets.values():
        out = cli.edit_pixels(_gradient(), preset.settings)
        assert out.shape == (300, 400, 3)
        assert out.min() >= 0 and out.max() <= 1


def test_auto_brightens_dark_photo():
    dark = _gradient(brightness=0.25)
    a = auto.analyze(dark)
    assert a.offsets["exposure"] > 0
    out = adjust.apply(dark.copy(), Settings().plus(a.offsets), a.wb_gains)
    assert adjust.luminance(out).mean() > adjust.luminance(dark).mean()


def test_auto_does_not_blow_out_bright_subject_on_dark_background():
    img = np.full((200, 300, 3), 0.05, np.float32)  # black speaker behind
    img[:, 100:200] = 0.9  # white shirt: a third of the photo
    assert auto.analyze(img).offsets.get("exposure", 0) < 0.1
    dark = np.full((200, 300, 3), 0.15, np.float32)  # evenly dark photo still gets brightened
    assert auto.analyze(dark).offsets["exposure"] > 1


def test_auto_adds_color_only_to_dull_photos():
    rng = np.random.default_rng(0)
    gray = np.clip(0.45 + rng.normal(0, 0.1, (200, 300, 1)), 0, 1).repeat(3, 2).astype(np.float32)
    assert auto.analyze(gray).offsets["vibrance"] > 0.2
    colorful = gray.copy()
    colorful[..., 2] *= 0.4  # strong yellow everywhere
    assert "vibrance" not in auto.analyze(colorful).offsets


def test_auto_removes_more_lamp_color_at_night_than_in_daylight():
    def warm(level):
        img = np.full((200, 300, 3), level, np.float32)
        img[..., 0] *= 1.05  # orange cast on a gray wall: red > green > blue
        img[..., 2] *= 0.8
        return img
    night, day = auto.analyze(warm(0.17)).wb_gains, auto.analyze(warm(0.5)).wb_gains
    assert night[2] > day[2] > 1  # both boost blue; night removes more of the cast


def test_auto_keeps_neon_scene_dark():
    img = np.full((300, 400, 3), 0.02, np.float32)
    img[100:150, 50:350] = (0.05, 0.05, 0.95)  # blue neon: dark by luminance, channel near max
    a = auto.analyze(img)
    assert a.offsets["exposure"] <= 0.2
    assert a.offsets.get("shadows", 0) <= 0.15


def test_baseline_exposure_missing_is_zero(heic_with_gps):
    assert files.baseline_exposure(heic_with_gps) == 0.0


def test_hsv_round_trip_is_lossless():
    img = _gradient()
    out = np.empty_like(img)
    adjust._from_hsv(*adjust._to_hsv(img), out)
    assert np.abs(out - img).max() < 1e-4


def test_color_mixer_changes_only_its_color():
    img = np.zeros((10, 20, 3), np.float32)
    img[:, :10] = (0.2, 0.7, 0.2)  # green
    img[:, 10:] = (0.7, 0.2, 0.2)  # red
    out = adjust.apply(img.copy(), Settings(green_sat=-1.0))
    assert np.ptp(out[:, :10], axis=-1).max() < 0.02          # green turned gray
    assert np.abs(out[:, 10:] - img[:, 10:]).max() < 1e-4     # red untouched


def test_grading_skips_skin():
    skin = np.full((10, 10, 3), (0.8, 0.6, 0.48), np.float32)
    teal = Settings(grade_midtones=1.0, grade_midtones_hue=180)
    protected = np.abs(adjust.apply(skin.copy(), teal) - skin).max()
    unprotected = np.abs(adjust.apply(skin.copy(), replace(teal, protect_skin=0.0)) - skin).max()
    assert protected < unprotected * 0.5


def test_bw_has_no_color():
    out = cli.edit_pixels(_gradient(), load_presets()["bw"].settings)
    assert np.abs(out[..., 0] - out[..., 1]).max() < 1e-4


def test_crop_ratio():
    img = _gradient(600, 800)
    assert adjust.crop_to_ratio(img, "4:5").shape[:2] == (600, 480)
    assert adjust.crop_to_ratio(img, "16:9").shape[:2] == (450, 800)


def test_edit_heic_rotates_and_strips_location(heic_with_gps, tmp_path):
    out_dir = tmp_path / "out"
    assert cli.main(["edit", str(heic_with_gps), "-o", str(out_dir)]) == 0
    saved = out_dir / "IMG_0001_natural.jpg"
    with Image.open(saved) as im:
        assert im.size == (300, 400)  # rotation baked in
        exif = im.getexif()
        assert exif[0x010F] == "Apple"
        assert files.GPS_IFD not in exif


def test_keep_location_and_heic_output(heic_with_gps, tmp_path):
    out_dir = tmp_path / "out"
    cli.main(["edit", str(heic_with_gps), "-o", str(out_dir), "-f", "heic", "--keep-location"])
    with Image.open(out_dir / "IMG_0001_natural.heic") as im:
        assert files.GPS_IFD in im.getexif()


def test_tif_output_is_16_bit(heic_with_gps, tmp_path):
    import tifffile
    cli.main(["edit", str(heic_with_gps), "-o", str(tmp_path), "-f", "tif", "--preset", "vivid"])
    assert tifffile.imread(tmp_path / "IMG_0001_vivid.tif").dtype == np.uint16


def test_try_makes_comparison_sheet(heic_with_gps, tmp_path):
    assert cli.main(["try", str(heic_with_gps), "-o", str(tmp_path)]) == 0
    assert (tmp_path / "IMG_0001_compare.jpg").is_file()


def test_crop_position():
    assert adjust.crop_box(600, 800, "4:5", "left") == (0, 0, 480, 600)
    assert adjust.crop_box(600, 800, "4:5", "right") == (320, 0, 480, 600)
    assert adjust.crop_box(800, 600, "1:1", "top") == (0, 0, 600, 600)
    assert adjust.crop_box(800, 600, "1:1", "0.5,1") == (0, 200, 600, 600)


def test_skin_line_moves_yellow_face_but_not_skin_colored_ground():
    img = np.full((200, 200, 3), [0.80, 0.62, 0.45], dtype=np.float32)  # all skin-colored, too yellow
    start = adjust._to_hsv(img[:1, :1])[0][0, 0]  # ~29 deg; the skin line is ~24
    face = [(0.1, 0.1, 0.2, 0.2)]  # a face box in the top-left corner
    shift = adjust.skin_line_check(img, face)
    assert shift < -2
    adjust.shift_skin(img, shift, face)
    face_hue = adjust._to_hsv(img[40:41, 40:41])[0][0, 0]
    ground_hue = adjust._to_hsv(img[190:191, 190:191])[0][0, 0]
    assert face_hue < start - 1.5            # face moved toward the skin line
    assert abs(ground_hue - start) < 0.01    # far from the face: mud/sand stays as it was


def test_skin_line_needs_a_face():
    img = np.full((60, 60, 3), [0.80, 0.62, 0.45], dtype=np.float32)
    assert adjust.skin_line_check(img, []) == 0.0


def test_crop_zoom_keeps_smaller_box_placed_by_pos():
    assert adjust.crop_box(1000, 800, "4:5", "center", 0.8) == (80, 100, 640, 800)
    assert adjust.crop_box(1000, 800, "4:5", "0,1", 0.5) == (0, 500, 400, 500)
    assert adjust.crop_box(1000, 800, "", "center", 0.5) == (200, 250, 400, 500)  # zoom only, same shape


def test_color_grading_tints_without_changing_brightness():
    gray = np.full((50, 50, 3), 0.3, dtype=np.float32)
    graded = adjust.apply(gray.copy(), Settings(grade_shadows=1.0, grade_shadows_hue=200))
    assert graded[0, 0, 2] > graded[0, 0, 0]  # shadows pushed toward blue
    assert abs(adjust.luminance(graded).mean() - 0.3) < 0.01


def test_grid_command(heic_with_gps, tmp_path):
    assert cli.main(["grid", str(heic_with_gps), "--crop", "4:5", "--crop-pos", "top", "-o", str(tmp_path)]) == 0
    assert (tmp_path / "IMG_0001_grid_4x5_top.jpg").is_file()


def test_srgb_conversion_keeps_srgb_and_survives_odd_profiles():
    from PIL import ImageCms
    from jogo.files import _to_srgb
    # Pillow can't build a Display P3 profile, so real P3 conversion is checked on iPhone photos by hand.
    srgb = Image.new("RGB", (4, 4), (40, 200, 60))
    out, icc = _to_srgb(srgb, files.SRGB_ICC)
    assert out is srgb and icc == files.SRGB_ICC
    lab = ImageCms.ImageCmsProfile(ImageCms.createProfile("LAB")).tobytes()
    out, icc = _to_srgb(srgb, lab)  # unusual profiles must never crash loading
    assert out.size == (4, 4)


def test_vibrance_skips_skin():
    skin = np.full((8, 8, 3), (0.80, 0.58, 0.45), dtype=np.float32)
    leaf = np.full((8, 8, 3), (0.45, 0.60, 0.40), dtype=np.float32)
    s = Settings(auto=False, vibrance=0.5)
    def spread(a):
        return float(a.max(axis=-1).mean() - a.min(axis=-1).mean())
    skin_gain = spread(adjust.apply(skin.copy(), s)) / spread(skin)
    leaf_gain = spread(adjust.apply(leaf.copy(), s)) / spread(leaf)
    assert skin_gain < leaf_gain
    assert skin_gain < 1.15

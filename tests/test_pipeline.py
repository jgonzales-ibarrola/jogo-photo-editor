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


def test_color_grading_tints_without_changing_brightness():
    gray = np.full((50, 50, 3), 0.3, dtype=np.float32)
    graded = adjust.apply(gray.copy(), Settings(grade_shadows=1.0, grade_shadows_hue=200))
    assert graded[0, 0, 2] > graded[0, 0, 0]  # shadows pushed toward blue
    assert abs(adjust.luminance(graded).mean() - 0.3) < 0.01


def test_grid_command(heic_with_gps, tmp_path):
    assert cli.main(["grid", str(heic_with_gps), "--crop", "4:5", "--crop-pos", "top", "-o", str(tmp_path)]) == 0
    assert (tmp_path / "IMG_0001_grid_4x5_top.jpg").is_file()

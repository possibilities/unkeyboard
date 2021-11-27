import os
from slugify import slugify
import pytest
import itertools
import secrets
from presets import presets
from keyboard import make_keyboard_parts
from cadquery import exporters
from cairosvg import svg2png
from PIL import Image, ImageStat, ImageChops

delta: float = 0.0001


def assert_images_equal(
    actual: Image.Image, expected: Image.Image, preset, part_name
):
    assert (
        actual.size == expected.size
    ), "expected images to be the same dimensions"
    assert actual.mode == expected.mode, "expected images to be the same mode"

    diff = ImageChops.difference(actual, expected)
    stat = ImageStat.Stat(diff)
    num_channels = len(stat.mean)
    sum_channel_values = sum(stat.mean)
    max_all_channels = num_channels * 255.0
    diff_ratio = sum_channel_values / max_all_channels

    if diff_ratio > delta:
        token = secrets.token_urlsafe(8)
        actual_path = f"/tmp/images-{token}-actual.png"
        expected_path = f"/tmp/images-{token}-expected.png"
        diff_path = f"/tmp/images-{token}-diff.png"

        actual.save(str(actual_path))
        expected.save(str(expected_path))

        # for purposes of debugging, the diff is far easier to read if we
        # artificially remove the alpha channel
        diff.putalpha(255)
        diff.save(str(diff_path))

        pytest.fail(
            f"{preset} {part_name}: images differ by {diff_ratio:.2f} (allowed={delta})\n"  # noqa: E501
            f"test images written to:\n"
            f"    actual: {actual_path}\n"
            f"    expected: {expected_path}\n"
            f"    diff: {diff_path}\n"
        )


preset_names = presets.__dict__.keys()
part_names = [
    "Case bottom plate",
    "Case top plate",
    "Case spacer 1",
    "Case switch plate",
]
test_data = itertools.product(preset_names, part_names)


@pytest.mark.parametrize("preset_name,part_name", test_data)
def test_output(preset_name, part_name):
    token = secrets.token_urlsafe(8)
    os.makedirs(f"/tmp/{token}", exist_ok=True)
    preset = presets.__dict__[preset_name]
    [parts, geometry] = make_keyboard_parts(preset)
    test_has_run = False
    for part_name_and_part in parts:
        [current_part_name, part] = part_name_and_part[0:2]
        if part_name == current_part_name:
            test_has_run = True
            part_name_slug = slugify(part_name)
            preset_name_slug = slugify(preset_name)
            exporters.export(
                part.faces("front").wires(),
                f"/tmp/{token}/{preset_name_slug}-{part_name_slug}.svg",
                opt={
                    "showAxes": False,
                    "projectionDir": (0.0, 0.0, 1),
                    "strokeWidth": 0.25,
                    "strokeColor": (255, 255, 255),
                },
            )

            url = f"/tmp/{token}/{preset_name_slug}-{part_name_slug}.svg"
            write_to = f"/tmp/{token}/{preset_name_slug}-{part_name_slug}.png"
            svg2png(url=url, write_to=write_to)

            actual = f"/tmp/{token}/{preset_name_slug}-{part_name_slug}.png"
            expected = (
                f"__fixtures__/images/{preset_name_slug}-{part_name_slug}.png"
            )
            assert_images_equal(
                Image.open(actual),
                Image.open(expected),
                preset_name,
                part_name,
            )
    if not test_has_run:
        assert False, f"No test was run for {preset_name} {part_name}"

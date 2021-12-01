import os
import secrets
from slugify import slugify
from cairosvg import svg2png
from cadquery import exporters
from presets import presets
from case import make_case_parts
from shutil import rmtree

token = secrets.token_urlsafe(8)

preset_names = [name for name in presets.keys() if name != "default"]

try:
    rmtree("__fixtures__/images")
except FileNotFoundError:
    pass

for preset_name in preset_names:
    config = presets[preset_name]
    [case_parts, case_geometry] = make_case_parts(config)
    for [part_name, part, options] in case_parts:
        part_name_slug = slugify(part_name)
        preset_name_slug = slugify(preset_name)
        os.makedirs(f"/tmp/{token}", exist_ok=True)
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

        os.makedirs("__fixtures__/images", exist_ok=True)
        url = f"/tmp/{token}/{preset_name_slug}-{part_name_slug}.svg"
        write_to = (
            f"__fixtures__/images/{preset_name_slug}-{part_name_slug}.png"
        )
        svg2png(url=url, write_to=write_to)

print()
print("Created test fixtures")

import os
import secrets
from slugify import slugify
from cairosvg import svg2png
from cadquery import exporters
from presets import presets
from case import make_case_parts
from shutil import rmtree
from make_pcb_parts import make_pcb_parts
import kicad

token = secrets.token_urlsafe(8)

os.makedirs(f"/tmp/{token}", exist_ok=True)

preset_names = [name for name in presets.keys() if name != "default"]

try:
    rmtree("__fixtures__/images")
except FileNotFoundError:
    pass
os.makedirs("__fixtures__/images", exist_ok=True)

for preset_name in preset_names:
    config = presets[preset_name]
    [case_parts, case_geometry] = make_case_parts(config)
    for [part_name, part, options] in case_parts:
        part_name_slug = slugify(part_name)
        preset_name_slug = slugify(preset_name)
        exporters.export(
            part.faces("front").wires(),
            f"/tmp/{token}/{preset_name_slug}-{part_name_slug}.svg",
            opt={
                "showAxes": False,
                "projectionDir": (0.0, 0.0, 1),
                "strokeWidth": 0.25,
                "strokeColor": (0, 0, 0),
            },
        )

        url = f"/tmp/{token}/{preset_name_slug}-{part_name_slug}.svg"
        write_to = f"__fixtures__/images/{preset_name_slug}-{part_name_slug}.png"
        svg2png(url=url, write_to=write_to, scale=4)

for preset_name in preset_names:
    if preset_name != "atreus_62":
        continue

    board_data = kicad.load_board("data/pcb", "keyboard")
    pcb_parts = make_pcb_parts(board_data)

    for layer_name_part_and_options in pcb_parts:
        [part_name, part, options] = layer_name_part_and_options
        part_name_slug = slugify(part_name)
        preset_name_slug = slugify(preset_name)
        exporters.export(
            part,
            f"/tmp/{token}/{preset_name_slug}-{part_name_slug}.svg",
            opt={
                "showAxes": False,
                "projectionDir": (0.0, 0.0, 1),
                "strokeWidth": 0.25,
                "strokeColor": (0, 0, 0),
            },
        )

        url = f"/tmp/{token}/{preset_name_slug}-{part_name_slug}.svg"
        write_to = f"__fixtures__/images/{preset_name_slug}-{part_name_slug}.png"
        svg2png(url=url, write_to=write_to, scale=4)

print()
print("Created test fixtures")

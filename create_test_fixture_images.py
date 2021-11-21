import os
import secrets
from slugify import slugify
from cairosvg import svg2png
from cadquery import exporters
from presets import presets
from keyboard import make_keyboard_parts

token = secrets.token_urlsafe(8)

preset_names = presets.__dict__.keys()

try:
    os.remove("__fixtures__/images")
except:
    pass

for preset_name in preset_names:
    config = presets.__dict__[preset_name]
    [parts, geometry] = make_keyboard_parts(config)
    for [part_name, part, options] in parts:
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
        svg2png(
            url=f"/tmp/{token}/{preset_name_slug}-{part_name_slug}.svg",
            write_to=f"__fixtures__/images/{preset_name_slug}-{part_name_slug}.png",
        )

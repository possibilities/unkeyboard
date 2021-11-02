import os
import secrets
from slugify import slugify
from cairosvg import svg2png
from cadquery import exporters
from keyboard import presets
from keyboard import make_keyboard_parts

token = secrets.token_urlsafe(8)

preset_names = presets.__dict__.keys()

try:
    os.remove("__snapshots__/images")
except:
    pass

for preset_name in preset_names:
    config = presets.__dict__[preset_name]
    parts = make_keyboard_parts(config.__dict__)
    for [part_name, part] in parts:
        slug = slugify(part_name)
        os.makedirs(f"/tmp/{token}", exist_ok=True)
        exporters.export(
            part.faces("front").wires(),
            f"/tmp/{token}/{preset_name}-{slug}.svg",
            opt={
                "showAxes": False,
                "projectionDir": (0.0, 0.0, 1),
                "strokeWidth": 0.25,
                "strokeColor": (255, 255, 255),
            },
        )

        os.makedirs("__snapshots__/images", exist_ok=True)
        svg2png(
            url=f"/tmp/{token}/{preset_name}-{slug}.svg",
            write_to=f"__snapshots__/images/{preset_name}-{slug}.png",
        )

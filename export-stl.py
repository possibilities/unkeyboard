import os
from slugify import slugify
from cadquery import exporters
from keyboard import make_keyboard_parts


def main():
    try:
        os.mkdir("./data")
    except:
        pass

    parts = make_keyboard_parts()

    for layer_name_and_part in parts:
        [part_name, part] = layer_name_and_part

        part_name_slug = slugify(part_name)

        file_name = f"data/keyboard-{part_name_slug}.stl"
        exporters.export(
            part,
            file_name,
            tolerance=0.01,
            angularTolerance=0.1,
        )

        print("Exported: %s" % (file_name))


main()

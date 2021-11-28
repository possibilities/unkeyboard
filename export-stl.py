import os
from slugify import slugify
from cadquery import exporters
from case import make_case_parts


def main():
    try:
        os.mkdir("./data")
    except Exception:
        pass

    [case_parts, case_geometry] = make_case_parts()

    for layer_name_part_and_options in case_parts:
        [part_name, part, options] = layer_name_part_and_options

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

def explode_parts(parts, explode_by):
    exploded = []
    parts.reverse()

    total_thickness = 0
    for index, layer_name_part_and_options in enumerate(parts):
        [layer_name, part, options] = layer_name_part_and_options

        thickness = (
            part.vertices("front").val().Center().z
            - part.vertices("back").val().Center().z
        )

        exploded.append(
            (layer_name, part.translate([0, 0, total_thickness]), options)
        )

        total_thickness = total_thickness + thickness + explode_by

    return exploded

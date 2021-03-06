import cadquery as cq
from cq_workplane_plugin import cq_workplane_plugin
from explode_parts import explode_parts
from calculate_point_for_angle import calculate_point_for_angle
from calculate_rectangle_corners import calculate_rectangle_corners
from calculate_intersection_of_points import calculate_intersection_of_points
from rotate_2d import rotate_2d
from mirror_points import mirror_points
from calculate_column_stagger_size import calculate_column_stagger_size
from presets import presets

explode_by = 20
flatten_items = False
switch_plate_cutout_size = 13.97


@cq_workplane_plugin
def drill_holes(part, points, radius, thickness):
    return part.pushPoints(points).circle(radius).cutBlind(thickness)


@cq_workplane_plugin
def drill_reset_button_hole(part, geometry):
    return (
        part.moveTo(*geometry["reset_button"]["point"])
        .circle(geometry["reset_button"]["radius"])
        .cutBlind(geometry["reset_button"]["thickness"])
    )


def has_reached_end_of_thumb_keys_row(column, row, config):
    has_reached_end_column = column == 0
    if has_reached_end_column:
        has_reached_end_row = row > (1 if config["has_two_thumb_keys"] else 0)
        if has_reached_end_row:
            return True
    return False


def calculate_unrotated_switch_positions(config):
    unrotated_switch_positions = []

    number_of_thumb_key_columns_per_side = 1
    total_number_of_columns = (
        config["number_of_columns"] + number_of_thumb_key_columns_per_side
    )

    for column in range(total_number_of_columns):
        unrotated_switch_positions.append([])
        for row in range(config["number_of_rows"]):
            if not has_reached_end_of_thumb_keys_row(column, row, config):
                switch_position_x = config["distance_between_switch_centers"] * (
                    column + 0.5
                )

                switch_position_y = config["distance_between_switch_centers"] * (
                    row + 0.5 + calculate_column_stagger_size(column, config)
                )

                unrotated_switch_positions[-1].append(
                    (switch_position_x, switch_position_y)
                )

    return unrotated_switch_positions


def calculate_switch_positions(mirror_at_point, unrotated_switch_positions, config):
    number_of_thumb_key_columns_per_side = 1
    total_number_of_columns = (
        config["number_of_columns"] + number_of_thumb_key_columns_per_side
    )

    switch_positions = []
    for column in range(total_number_of_columns):
        for row in range(config["number_of_rows"]):
            if not has_reached_end_of_thumb_keys_row(column, row, config):
                unrotated_switch_position = unrotated_switch_positions[column][row]
                switch_position = rotate_2d(
                    (0, 0), unrotated_switch_position, -config["angle"]
                )
                switch_positions.append(switch_position)

    return mirror_points(switch_positions, mirror_at_point)


def calculate_switch_plate_points(mirror_at_point, switch_positions, config):
    switch_plate_points = []

    for switch_position in switch_positions:
        switch_cutout_corner_points = calculate_rectangle_corners(
            switch_position,
            switch_plate_cutout_size,
            switch_plate_cutout_size,
        )

        rotated_switch_cutout_corner_points = [
            rotate_2d(switch_position, point, config["angle"])
            if point[0] < mirror_at_point[0]
            else rotate_2d(switch_position, point, -config["angle"])
            for point in switch_cutout_corner_points
        ]

        switch_plate_points.append(rotated_switch_cutout_corner_points)

    return switch_plate_points


def calculate_switch_plate_outline_points(unrotated_switch_positions, config):
    widen_cutout_around_switch_size = 1

    widen_cutout_around_thumb_keys_size = 0 if config["has_two_thumb_keys"] else 1.5
    thumb_keys_unit_height = 1 if config["has_two_thumb_keys"] else 1.5

    thumb_keys_height = (
        config["distance_between_switch_centers"] * thumb_keys_unit_height
    ) + widen_cutout_around_thumb_keys_size

    outline_size_per_switch = (
        config["distance_between_switch_centers"] + widen_cutout_around_switch_size
    )

    thumb_key_padding_y = (
        thumb_keys_height - config["distance_between_switch_centers"]
    ) / 2
    outline_size = outline_size_per_switch / 2
    top_left_switch = (
        unrotated_switch_positions[0][-1][0],
        unrotated_switch_positions[0][-1][1] + thumb_key_padding_y,
    )
    top_right_switch = unrotated_switch_positions[-1][-1]
    bottom_left_switch = (
        unrotated_switch_positions[0][0][0],
        unrotated_switch_positions[0][0][1] - thumb_key_padding_y,
    )
    bottom_right_switch = unrotated_switch_positions[-1][0]

    top_row = [column[-1] for column in unrotated_switch_positions]
    bottom_row = [column[0] for column in unrotated_switch_positions]

    top_row_points = []
    for index, switch_position in enumerate(top_row):
        is_last_column_of_top_row = index == len(top_row) - 1
        if not is_last_column_of_top_row:
            next_switch_position = top_row[index + 1]
            is_lower_than_next = next_switch_position[1] > switch_position[1]
            next_switch_has_same_stagger = next_switch_position[1] == switch_position[1]
            if not next_switch_has_same_stagger:
                thumb_key_padding_y = (
                    (
                        thumb_keys_height
                        - config["distance_between_switch_centers"]
                        - widen_cutout_around_switch_size
                    )
                    / 2
                    if index == 0
                    else 0
                )

                left_point = (
                    (
                        next_switch_position[0] - outline_size,
                        switch_position[1] + outline_size + thumb_key_padding_y,
                    )
                    if is_lower_than_next
                    else (
                        switch_position[0] + outline_size,
                        switch_position[1] + outline_size + thumb_key_padding_y,
                    )
                )

                right_point = (
                    (
                        next_switch_position[0] - outline_size,
                        next_switch_position[1] + outline_size,
                    )
                    if is_lower_than_next
                    else (
                        switch_position[0] + outline_size,
                        next_switch_position[1] + outline_size,
                    )
                )

                top_row_points.insert(0, left_point)
                top_row_points.insert(0, right_point)

    bottom_row_points = []
    for index, switch_position in enumerate(bottom_row):
        is_last_column_of_bottom_row = index == len(bottom_row) - 1
        if not is_last_column_of_bottom_row:
            next_switch_position = bottom_row[index + 1]
            is_lower_than_next = next_switch_position[1] > switch_position[1]
            next_switch_has_same_stagger = next_switch_position[1] == switch_position[1]
            if not next_switch_has_same_stagger:
                thumb_key_padding_y = (
                    (
                        thumb_keys_height
                        - config["distance_between_switch_centers"]
                        - widen_cutout_around_switch_size
                    )
                    / 2
                    if index == 0
                    else 0
                )

                left_point = (
                    (
                        switch_position[0] + outline_size,
                        switch_position[1] - outline_size - thumb_key_padding_y,
                    )
                    if is_lower_than_next
                    else (
                        next_switch_position[0] - outline_size,
                        switch_position[1] - outline_size - thumb_key_padding_y,
                    )
                )

                right_point = (
                    (
                        switch_position[0] + outline_size,
                        next_switch_position[1] - outline_size,
                    )
                    if is_lower_than_next
                    else (
                        next_switch_position[0] - outline_size,
                        next_switch_position[1] - outline_size,
                    )
                )

                bottom_row_points.append(left_point)
                bottom_row_points.append(right_point)

    thumb_keys_height = (
        config["distance_between_switch_centers"] * thumb_keys_unit_height
    ) + widen_cutout_around_thumb_keys_size

    bottom_left_corner = (
        bottom_left_switch[0] - outline_size,
        bottom_left_switch[1] - outline_size + (widen_cutout_around_switch_size / 2),
    )
    bottom_right_corner = (
        bottom_right_switch[0] + outline_size,
        bottom_right_switch[1] - outline_size,
    )
    top_right_corner = (
        top_right_switch[0] + outline_size,
        top_right_switch[1] + outline_size,
    )
    top_left_corner = (
        top_left_switch[0] - outline_size,
        top_left_switch[1] + outline_size - (widen_cutout_around_switch_size / 2),
    )

    bottom_row_points = [
        rotate_2d((0, 0), point, -config["angle"]) for point in bottom_row_points
    ]
    top_row_points = [
        rotate_2d((0, 0), point, -config["angle"]) for point in top_row_points
    ]
    bottom_left_corner = rotate_2d((0, 0), bottom_left_corner, -config["angle"])
    bottom_right_corner = rotate_2d((0, 0), bottom_right_corner, -config["angle"])
    top_right_corner = rotate_2d((0, 0), top_right_corner, -config["angle"])
    top_left_corner = rotate_2d((0, 0), top_left_corner, -config["angle"])

    switch_plate_outline_points = [
        bottom_left_corner,
        *bottom_row_points,
        bottom_right_corner,
        top_right_corner,
        *top_row_points,
        top_left_corner,
    ]

    mirror_at_point = (
        switch_plate_outline_points[-1][0] + (widen_cutout_around_switch_size / 2),
        switch_plate_outline_points[-1][1],
    )

    mirrored_switch_plate_outline_points = mirror_points(
        [
            calculate_intersection_of_points(
                switch_plate_outline_points[0],
                90 - config["angle"],
                mirror_at_point,
                90,
            ),
            *switch_plate_outline_points[0:-1],
            calculate_intersection_of_points(
                switch_plate_outline_points[-2],
                -config["angle"],
                mirror_at_point,
                90,
            ),
        ],
        mirror_at_point,
        combine=False,
    )

    switch_plate_outline_points = [
        *switch_plate_outline_points[0:-1],
        *mirrored_switch_plate_outline_points,
    ]

    return [switch_plate_outline_points, mirror_at_point]


def calculate_case_outside_points(
    switch_plate_outline_points,
    outside_frame_size,
    mirror_at_point,
    config,
):
    outside_points_start_of_bottom_row = switch_plate_outline_points[2]
    outside_points_bottom_right_corner = switch_plate_outline_points[
        (config["number_of_columns"] * 2)
        + (-1 if config["number_of_columns"] % 2 == 0 else 1)
    ]
    outside_points_top_right_corner = switch_plate_outline_points[
        config["number_of_columns"] * 2
        + (0 if config["number_of_columns"] % 2 == 0 else 2)
    ]
    bottom_left_corner = calculate_point_for_angle(
        outside_points_start_of_bottom_row,
        -outside_frame_size,
        45 - config["angle"],
    )
    bottom_right_corner = calculate_point_for_angle(
        outside_points_bottom_right_corner,
        -outside_frame_size,
        -45 - config["angle"],
    )
    top_right_corner = calculate_point_for_angle(
        outside_points_top_right_corner,
        outside_frame_size,
        45 - config["angle"],
    )
    return mirror_points(
        [bottom_left_corner, bottom_right_corner, top_right_corner],
        mirror_at_point,
    )


def calculate_spacer_inside_points(
    mirror_at_point, case_outside_points, outside_frame_size, config
):
    points = [
        calculate_point_for_angle(
            case_outside_points[0], outside_frame_size, 45 - config["angle"]
        ),
        calculate_point_for_angle(
            case_outside_points[1], outside_frame_size, -45 - config["angle"]
        ),
        calculate_point_for_angle(
            case_outside_points[2], -outside_frame_size, 45 - config["angle"]
        ),
    ]
    return mirror_points(points, mirror_at_point)


def calculate_screw_points(
    spacer_inside_points, outside_frame_size, mirror_at_point, config
):
    screw_distance_from_inside_edge = (
        outside_frame_size - config["inside_frame_size"]
    ) / 2

    spacer_bottom_left_corner = spacer_inside_points[0]
    spacer_bottom_right_corner = spacer_inside_points[1]
    spacer_top_right_corner = spacer_inside_points[2]

    screw_top_right_corner = calculate_point_for_angle(
        spacer_top_right_corner,
        screw_distance_from_inside_edge,
        45 - config["angle"],
    )

    screw_top_left_corner = (
        config["top_inside_screw_distance_from_usb"],
        screw_top_right_corner[1],
    )

    screw_bottom_left_corner = calculate_point_for_angle(
        spacer_bottom_left_corner,
        -screw_distance_from_inside_edge,
        45 - config["angle"],
    )

    screw_bottom_right_corner = calculate_point_for_angle(
        spacer_bottom_right_corner,
        -screw_distance_from_inside_edge,
        -45 - config["angle"],
    )

    screw_points = [
        screw_top_left_corner,
        screw_top_right_corner,
        screw_bottom_right_corner,
        screw_bottom_left_corner,
    ]

    return mirror_points(screw_points, mirror_at_point)


def calculate_case_geometry(config):
    unrotated_switch_positions = calculate_unrotated_switch_positions(config)

    [
        switch_plate_outline_points,
        mirror_at_point,
    ] = calculate_switch_plate_outline_points(unrotated_switch_positions, config)

    switch_positions = calculate_switch_positions(
        mirror_at_point,
        unrotated_switch_positions,
        config,
    )

    switch_plate_points = calculate_switch_plate_points(
        mirror_at_point,
        switch_positions,
        config,
    )

    outside_frame_size = (
        config["outside_frame_size_for_chicago_bolt"]
        if config["use_chicago_bolt"]
        else config["outside_frame_size_for_regular_screw"]
    )

    case_outside_points = calculate_case_outside_points(
        switch_plate_outline_points,
        outside_frame_size,
        mirror_at_point,
        config,
    )

    outside_frame_size = (
        config["outside_frame_size_for_chicago_bolt"]
        if config["use_chicago_bolt"]
        else config["outside_frame_size_for_regular_screw"]
    )

    spacer_inside_points = calculate_spacer_inside_points(
        mirror_at_point,
        case_outside_points,
        outside_frame_size,
        config,
    )

    screw_points = calculate_screw_points(
        spacer_inside_points,
        outside_frame_size,
        mirror_at_point,
        config,
    )

    screw_radius = (
        config["screw_hole_radius_for_chicago_bolt"]
        if config["use_chicago_bolt"]
        else config["screw_hole_radius_for_regular_screw"]
    )

    reset_button_radius = 1.5
    reset_button_point = (-30, 101)

    spacer_thickness = (
        config["base_layer_thickness"] * 2
        if config["has_thicc_spacer"]
        else config["base_layer_thickness"]
    )

    spacer_usb_cutout_points = [
        (
            mirror_at_point[0] + config["usb_cutout_width"] / 2,
            case_outside_points[2][1],
        ),
        (
            mirror_at_point[0] + config["usb_cutout_width"] / 2,
            2,
        ),
        (
            mirror_at_point[0] - config["usb_cutout_width"] / 2,
            2,
        ),
        (
            mirror_at_point[0] - config["usb_cutout_width"] / 2,
            case_outside_points[2][1],
        ),
    ]

    return {
        "switch_positions": switch_positions,
        "screws": {
            "points": screw_points,
            "radius": screw_radius,
        },
        "reset_button": {
            "point": reset_button_point,
            "radius": reset_button_radius,
            "thickness": config["base_layer_thickness"],
        },
        "case_outside": {
            "points": case_outside_points,
        },
        "spacer_inside": {
            "points": spacer_inside_points,
        },
        "spacer_usb_cutout": {"points": spacer_usb_cutout_points},
        "spacer": {
            "thickness": spacer_thickness,
        },
        "switch_outline": {
            "points": switch_plate_outline_points,
            "thickness": config["base_layer_thickness"],
        },
        "top_plate": {
            "thickness": config["base_layer_thickness"],
        },
        "bottom_plate": {
            "thickness": config["base_layer_thickness"],
        },
        "switch_plate": {
            "points": switch_plate_points,
            "thickness": config["base_layer_thickness"],
        },
        "switch_plate_outline": {
            "points": switch_plate_outline_points,
        },
        "mirror_at": {
            "point": mirror_at_point,
        },
    }


def make_bottom_plate(geometry):
    return (
        cq.Workplane()
        .polyline(geometry["case_outside"]["points"])
        .close()
        .extrude(geometry["bottom_plate"]["thickness"])
        .drill_holes(
            geometry["screws"]["points"],
            geometry["screws"]["radius"],
            geometry["bottom_plate"]["thickness"],
        )
        .drill_reset_button_hole(geometry)
    )


def make_top_plate(geometry):
    cutout = (
        cq.Workplane()
        .polyline(geometry["switch_outline"]["points"])
        .close()
        .extrude(geometry["top_plate"]["thickness"])
    )
    return (
        cq.Workplane()
        .polyline(geometry["case_outside"]["points"])
        .close()
        .extrude(geometry["top_plate"]["thickness"])
        .drill_holes(
            geometry["screws"]["points"],
            geometry["screws"]["radius"],
            geometry["top_plate"]["thickness"],
        )
        .cut(cutout)
    )


def make_switch_plate(geometry):
    switch_plate = cq.Workplane()

    for switch_cutout_points in geometry["switch_plate"]["points"]:
        switch_plate = switch_plate.polyline(switch_cutout_points).close()

    return (
        switch_plate.polyline(geometry["case_outside"]["points"])
        .close()
        .extrude(geometry["switch_plate"]["thickness"])
        .drill_holes(
            geometry["screws"]["points"],
            geometry["screws"]["radius"],
            geometry["switch_plate"]["thickness"],
        )
    )


def make_spacer(geometry):
    inside_cutout = (
        cq.Workplane()
        .polyline(geometry["spacer_inside"]["points"])
        .close()
        .extrude(geometry["spacer"]["thickness"])
    )

    usb_cutout = (
        cq.Workplane()
        .polyline(geometry["spacer_usb_cutout"]["points"])
        .close()
        .extrude(geometry["spacer"]["thickness"])
    )

    return (
        cq.Workplane()
        .polyline(geometry["case_outside"]["points"])
        .close()
        .extrude(geometry["spacer"]["thickness"])
        .cut(inside_cutout)
        .cut(usb_cutout)
        .drill_holes(
            geometry["screws"]["points"],
            geometry["screws"]["radius"],
            geometry["spacer"]["thickness"],
        )
    )


def make_case_parts(user_config={}):
    config = {**presets["default"], **user_config}

    parts = []

    geometry = calculate_case_geometry(config)

    parts.append(("Case top plate", make_top_plate(geometry), {}))
    parts.append(("Case switch plate", make_switch_plate(geometry), {}))

    if config["has_thicc_spacer"]:
        parts.append(("Case spacer", make_spacer(geometry), {}))
    else:
        parts.append(("Case spacer 1", make_spacer(geometry), {}))
        parts.append(("Case spacer 2", make_spacer(geometry), {}))

    parts.append(("Case bottom plate", make_bottom_plate(geometry), {}))

    return [parts, geometry]


if "show_object" in globals():
    [case_parts, case_geometry] = make_case_parts()

    if not flatten_items:
        case_parts = explode_parts(case_parts, explode_by)

    for layer_name_part_and_options in case_parts:
        [layer_name, part, options] = layer_name_part_and_options
        show_object(part, name=layer_name, options=options)

import math
import cadquery as cq
from timer import timer
from fuse_parts import fuse_parts
from cq_workplane_plugin import cq_workplane_plugin
from explode_parts import explode_parts
from types import SimpleNamespace


# Defaults to an Atreus 64, with a wide bezel, and chicago bolts
default_config = SimpleNamespace(
    **{
        # Configurable
        "has_thicc_spacer": False,
        "use_chicago_bolt": True,
        "has_double_inner_keys": False,
        "angle": 10,
        "number_of_rows": 5,
        "number_of_columns": 6,
        "stagger_percent_for_single_inner_key": 8.5,
        "stagger_percent_for_double_inner_keys": 3.98,
        "column_stagger_percents": (-1, 4, 10, 5, 2, 2),
        # Structural
        "base_layer_thickness": 3,
        "inner_frame_size": 2.1,
        "outer_frame_size_for_chicago_bolt": 20,
        "outer_frame_size_for_regular_screw": 16,
        "screw_hole_radius_for_chicago_bolt": 2.5,
        "screw_hole_radius_for_regular_screw": 1.5,
        "switch_plate_key_cutout_size": 13.97,
        "distance_between_switch_centers": 19,
        "usb_cutout_width": 4,
        "top_inside_screw_distance_from_usb": 5.50,
    }
)

# View options

explode_by = 20
flatten_items = False


def flatten_list(list):
    return [item for sublist in list for item in sublist]


def find_rectangle_coords_around_point(point, width, height):
    offset = cq.Vector(*point)
    points = [
        cq.Vector(width / -2.0, height / -2.0, 0),
        cq.Vector(width / 2.0, height / -2.0, 0),
        cq.Vector(width / 2.0, height / 2.0, 0),
        cq.Vector(width / -2.0, height / 2.0, 0),
    ]
    return [((point + offset).x, (point + offset).y) for point in points]


def find_point_for_angle(vertice, distance, angel):
    angle_radian = math.pi / 2 - math.radians(angel)
    return (
        vertice[0] + distance * math.cos(angle_radian),
        vertice[1] + distance * math.sin(angle_radian),
    )


@cq_workplane_plugin
def mirror_layer(self, geometry):
    return self.mirror(
        mirrorPlane="YZ",
        union=True,
        basePointVector=(geometry.mirror_base_point),
    )


@cq_workplane_plugin
def drill_holes(part, geometry, config):
    screw_hole_radius = (
        config.screw_hole_radius_for_chicago_bolt
        if config.use_chicago_bolt
        else config.screw_hole_radius_for_regular_screw
    )
    return (
        part.pushPoints(geometry.screws)
        .circle(screw_hole_radius)
        .cutBlind(geometry.thickness)
    )


@cq_workplane_plugin
def drill_reset_button_hole(part, geometry):
    return (
        part.moveTo(*geometry.reset_button.point)
        .circle(geometry.reset_button.radius)
        .cutBlind(geometry.reset_button.thickness)
    )


def rotate(origin, point, angle):
    angle_radian = math.radians(angle)
    [origin_x, origin_y] = origin
    [point_x, point_y] = point

    rotated_x = (
        origin_x
        + math.cos(angle_radian) * (point_x - origin_x)
        - math.sin(angle_radian) * (point_y - origin_y)
    )
    rotated_y = (
        origin_y
        + math.sin(angle_radian) * (point_x - origin_x)
        + math.cos(angle_radian) * (point_y - origin_y)
    )
    return (rotated_x, rotated_y)


def rotate_about_center_of_plane(key, angle):
    return rotate((0, 0), key, angle)


def has_reached_end_of_inner_keys_row(column, row, config):
    if column == 0:
        if row > (1 if config.has_double_inner_keys else 0):
            return True
    return False


def calculate_key_positions(config):
    key_positions = []

    inner_keys_stagger_percent = (
        config.stagger_percent_for_double_inner_keys
        if config.has_double_inner_keys
        else config.stagger_percent_for_single_inner_key
    )

    number_of_columns_including_inner_keys = config.number_of_columns + 1

    for column in range(number_of_columns_including_inner_keys):
        key_positions.append([])
        for row in range(config.number_of_rows):
            if has_reached_end_of_inner_keys_row(column, row, config):
                continue

            row_offset = config.distance_between_switch_centers * row
            column_offset = config.distance_between_switch_centers * column

            column_stagger_size = (
                inner_keys_stagger_percent
                if column == 0
                else config.column_stagger_percents[column - 1]
            ) / config.distance_between_switch_centers

            stagger_offset = (
                config.distance_between_switch_centers * column_stagger_size
            )

            key_position_x = column_offset + (
                config.distance_between_switch_centers / 2
            )

            key_position_y = (
                (config.distance_between_switch_centers / 2)
                + row_offset
                + stagger_offset
            )

            key_positions[-1].append((key_position_x, key_position_y))

    return key_positions


def calculate_switch_cutout_points(key_positions, config):
    switch_cutout_points = []

    number_of_columns_including_inner_keys = config.number_of_columns + 1

    for column in range(number_of_columns_including_inner_keys):
        switch_cutout_points.append([])
        for row in range(config.number_of_rows):
            if has_reached_end_of_inner_keys_row(column, row, config):
                continue

            key_position = key_positions[column][row]

            switch_cutout_corner_points = find_rectangle_coords_around_point(
                key_position,
                config.switch_plate_key_cutout_size,
                config.switch_plate_key_cutout_size,
            )

            switch_cutout_points[-1].append(
                [
                    rotate_about_center_of_plane(cutout, config.angle)
                    for cutout in switch_cutout_corner_points
                ]
            )

    return flatten_list(switch_cutout_points)


def calculate_switch_outline_points(key_positions, config):
    widen_cutout_around_key_size = 1

    widen_cutout_around_inner_keys_size = (
        0 if config.has_double_inner_keys else 1.5
    )
    inner_keys_unit_height = 1 if config.has_double_inner_keys else 1.5

    inner_keys_height = (
        config.distance_between_switch_centers * inner_keys_unit_height
    ) + widen_cutout_around_inner_keys_size

    outline_size_per_key = (
        config.distance_between_switch_centers + widen_cutout_around_key_size
    )

    inner_key_padding_y = (
        inner_keys_height - config.distance_between_switch_centers
    ) / 2
    outline_size = outline_size_per_key / 2
    top_left_key = (
        key_positions[0][-1][0],
        key_positions[0][-1][1] + inner_key_padding_y,
    )
    top_right_key = key_positions[-1][-1]
    bottom_left_key = (
        key_positions[0][0][0],
        key_positions[0][0][1] - inner_key_padding_y,
    )
    bottom_right_key = key_positions[-1][0]

    top_row = [column[-1] for column in key_positions]
    bottom_row = [column[0] for column in key_positions]

    top_row_points = []
    for index, key_position in enumerate(top_row):
        if index != len(top_row) - 1:
            next_key_position = top_row[index + 1]
            is_lower_than_next = next_key_position[1] > key_position[1]
            next_key_has_same_stagger = next_key_position[1] == key_position[1]
            if not next_key_has_same_stagger:
                inner_key_padding_y = (
                    (
                        inner_keys_height
                        - config.distance_between_switch_centers
                        - widen_cutout_around_key_size
                    )
                    / 2
                    if index == 0
                    else 0
                )

                left_point = (
                    (
                        next_key_position[0] - outline_size,
                        key_position[1] + outline_size + inner_key_padding_y,
                    )
                    if is_lower_than_next
                    else (
                        key_position[0] + outline_size,
                        key_position[1] + outline_size + inner_key_padding_y,
                    )
                )

                right_point = (
                    (
                        next_key_position[0] - outline_size,
                        next_key_position[1] + outline_size,
                    )
                    if is_lower_than_next
                    else (
                        key_position[0] + outline_size,
                        next_key_position[1] + outline_size,
                    )
                )

                top_row_points.insert(0, left_point)
                top_row_points.insert(0, right_point)

    bottom_row_points = []
    for index, key_position in enumerate(bottom_row):
        if index != len(bottom_row) - 1:
            next_key_position = bottom_row[index + 1]
            is_lower_than_next = next_key_position[1] > key_position[1]
            next_key_has_same_stagger = next_key_position[1] == key_position[1]
            if not next_key_has_same_stagger:
                inner_key_padding_y = (
                    (
                        inner_keys_height
                        - config.distance_between_switch_centers
                        - widen_cutout_around_key_size
                    )
                    / 2
                    if index == 0
                    else 0
                )

                left_point = (
                    (
                        key_position[0] + outline_size,
                        key_position[1] - outline_size - inner_key_padding_y,
                    )
                    if is_lower_than_next
                    else (
                        next_key_position[0] - outline_size,
                        key_position[1] - outline_size - inner_key_padding_y,
                    )
                )

                right_point = (
                    (
                        key_position[0] + outline_size,
                        next_key_position[1] - outline_size,
                    )
                    if is_lower_than_next
                    else (
                        next_key_position[0] - outline_size,
                        next_key_position[1] - outline_size,
                    )
                )

                bottom_row_points.append(left_point)
                bottom_row_points.append(right_point)

    inner_keys_height = (
        config.distance_between_switch_centers * inner_keys_unit_height
    ) + widen_cutout_around_inner_keys_size

    bottom_left_corner = (
        bottom_left_key[0] - outline_size,
        bottom_left_key[1] - outline_size + (widen_cutout_around_key_size / 2),
    )
    bottom_right_corner = (
        bottom_right_key[0] + outline_size,
        bottom_right_key[1] - outline_size,
    )
    top_right_corner = (
        top_right_key[0] + outline_size,
        top_right_key[1] + outline_size,
    )
    top_left_corner = (
        top_left_key[0] - outline_size,
        top_left_key[1] + outline_size - (widen_cutout_around_key_size / 2),
    )

    bottom_row_points = [
        rotate_about_center_of_plane(point, config.angle)
        for point in bottom_row_points
    ]
    top_row_points = [
        rotate_about_center_of_plane(point, config.angle)
        for point in top_row_points
    ]
    bottom_left_corner = rotate_about_center_of_plane(
        bottom_left_corner, config.angle
    )
    bottom_right_corner = rotate_about_center_of_plane(
        bottom_right_corner, config.angle
    )
    top_right_corner = rotate_about_center_of_plane(
        top_right_corner, config.angle
    )
    top_left_corner = rotate_about_center_of_plane(
        top_left_corner, config.angle
    )
    switch_outline_points = [
        bottom_left_corner,
        *bottom_row_points,
        bottom_right_corner,
        top_right_corner,
        *top_row_points,
        top_left_corner,
    ]

    start_of_bottom_row = bottom_row_points[1]

    mirror_base_point = (
        switch_outline_points[-1][0] + (widen_cutout_around_key_size / 2),
        switch_outline_points[-1][1],
    )

    named_points = SimpleNamespace(
        **{
            "start_of_bottom_row": start_of_bottom_row,
            "top_left_corner": top_left_corner,
            "bottom_right_corner": bottom_right_corner,
            "top_right_corner": top_right_corner,
            "mirror_base_point": mirror_base_point,
        }
    )

    return [
        switch_outline_points,
        named_points,
    ]


def calculate_case_outer_points(named_points, outer_frame_size, config):
    bottom_left_corner = find_point_for_angle(
        named_points.start_of_bottom_row,
        -outer_frame_size,
        45 - config.angle,
    )
    bottom_right_corner = find_point_for_angle(
        named_points.bottom_right_corner,
        -outer_frame_size,
        -45 - config.angle,
    )
    top_right_corner = find_point_for_angle(
        named_points.top_right_corner,
        outer_frame_size,
        45 - config.angle,
    )
    return [
        (named_points.top_left_corner[0], bottom_left_corner[1]),
        bottom_left_corner,
        bottom_right_corner,
        top_right_corner,
        (named_points.top_left_corner[0], top_right_corner[1]),
    ]


def calculate_spacer_points(case_outer_points, outer_frame_size, config):
    return [
        case_outer_points[0],
        (
            case_outer_points[0][0],
            find_point_for_angle(
                case_outer_points[1], outer_frame_size, 45 - config.angle
            )[1],
        ),
        find_point_for_angle(
            case_outer_points[1], outer_frame_size, 45 - config.angle
        ),
        find_point_for_angle(
            case_outer_points[2], outer_frame_size, -45 - config.angle
        ),
        find_point_for_angle(
            case_outer_points[3], -outer_frame_size, 45 - config.angle
        ),
        (
            case_outer_points[4][0] + (config.usb_cutout_width / 2),
            find_point_for_angle(
                case_outer_points[3], -outer_frame_size, 45 - config.angle
            )[1],
        ),
        (
            case_outer_points[4][0] + (config.usb_cutout_width / 2),
            case_outer_points[4][1],
        ),
        case_outer_points[3],
        case_outer_points[2],
        case_outer_points[1],
    ]


def calculate_screw_points(spacer_points, outer_frame_size, config):
    screw_distance_from_inner_edge = (
        outer_frame_size - config.inner_frame_size
    ) / 2

    spacer_top_right_corner = spacer_points[4]
    spacer_bottom_left_corner = spacer_points[2]
    spacer_bottom_right_corner = spacer_points[3]

    screw_top_right_corner = find_point_for_angle(
        spacer_top_right_corner,
        screw_distance_from_inner_edge,
        45 - config.angle,
    )

    screw_top_left_corner = (
        config.top_inside_screw_distance_from_usb,
        screw_top_right_corner[1],
    )

    screw_bottom_left_corner = find_point_for_angle(
        spacer_bottom_left_corner,
        -screw_distance_from_inner_edge,
        45 - config.angle,
    )

    screw_bottom_right_corner = find_point_for_angle(
        spacer_bottom_right_corner,
        -screw_distance_from_inner_edge,
        -45 - config.angle,
    )

    return [
        screw_top_left_corner,
        screw_top_right_corner,
        screw_bottom_right_corner,
        screw_bottom_left_corner,
    ]


def calculate_case_geometry(config):
    key_positions = calculate_key_positions(config)

    switch_cutout_points = calculate_switch_cutout_points(
        key_positions,
        config,
    )

    [
        switch_outline_points,
        named_points,
    ] = calculate_switch_outline_points(key_positions, config)

    outer_frame_size = (
        config.outer_frame_size_for_chicago_bolt
        if config.use_chicago_bolt
        else config.outer_frame_size_for_regular_screw
    )

    case_outer_points = calculate_case_outer_points(
        named_points, outer_frame_size, config
    )

    outer_frame_size = (
        config.outer_frame_size_for_chicago_bolt
        if config.use_chicago_bolt
        else config.outer_frame_size_for_regular_screw
    )

    spacer_points = calculate_spacer_points(
        case_outer_points, outer_frame_size, config
    )

    screw_points = calculate_screw_points(
        spacer_points, outer_frame_size, config
    )

    reset_button_radius = 1.5
    reset_button_point = (-30, 101)

    spacer_thickness = (
        config.base_layer_thickness * 2
        if config.has_thicc_spacer
        else config.base_layer_thickness
    )

    return SimpleNamespace(
        **{
            "screws": screw_points,
            "reset_button": SimpleNamespace(
                **{
                    "point": reset_button_point,
                    "radius": reset_button_radius,
                    "thickness": config.base_layer_thickness,
                }
            ),
            "case_outer": case_outer_points,
            "spacer": spacer_points,
            "spacer_thickness": spacer_thickness,
            "thickness": config.base_layer_thickness,
            "switch_outline": switch_outline_points,
            "switch_cutouts": switch_cutout_points,
            "mirror_base_point": named_points.mirror_base_point,
        }
    )


def make_bottom_plate(geometry, config):
    return (
        cq.Workplane()
        .polyline(geometry.case_outer)
        .close()
        .extrude(geometry.thickness)
        .drill_holes(geometry, config)
        .mirror_layer(geometry)
        .drill_reset_button_hole(geometry)
    )


def make_top_plate(geometry, config):
    cutout = (
        cq.Workplane()
        .polyline(geometry.switch_outline)
        .close()
        .extrude(geometry.thickness)
        .mirror_layer(geometry)
    )
    return (
        cq.Workplane()
        .polyline(geometry.case_outer)
        .close()
        .extrude(geometry.thickness)
        .drill_holes(geometry, config)
        .mirror_layer(geometry)
        .cut(cutout)
    )


def make_switch_plate(geometry, config):
    switch_plate = cq.Workplane()

    for switch_cutout in geometry.switch_cutouts:
        switch_plate = switch_plate.polyline(switch_cutout).close()

    return (
        switch_plate.polyline(geometry.case_outer)
        .close()
        .extrude(geometry.thickness)
        .drill_holes(geometry, config)
        .mirror_layer(geometry)
    )


def make_spacer(geometry, config):
    return (
        cq.Workplane()
        .polyline(geometry.spacer)
        .close()
        .extrude(geometry.spacer_thickness)
        .drill_holes(geometry, config)
        .mirror_layer(geometry)
    )


def make_keyboard_parts(user_config={}):
    config = SimpleNamespace(**{**default_config.__dict__, **user_config})

    parts = []

    [time_elapsed, total_time] = timer()

    geometry = calculate_case_geometry(config)
    time_elapsed("Case geometry")

    parts.append(("Top plate", make_top_plate(geometry, config)))
    time_elapsed("Top plate")

    parts.append(("Switch plate", make_switch_plate(geometry, config)))
    time_elapsed("Switch plate")

    if config.has_thicc_spacer:
        parts.append(("Spacer", make_spacer(geometry, config)))
        time_elapsed("Spacer")
    else:
        parts.append(("Spacer 1", make_spacer(geometry, config)))
        parts.append(("Spacer 2", make_spacer(geometry, config)))
        time_elapsed("Spacers")

    parts.append(("Bottom plate", make_bottom_plate(geometry, config)))
    time_elapsed("Bottom plate")

    total_time()

    return parts


if "show_object" in globals():
    keyboard_parts = make_keyboard_parts()

    if not flatten_items:
        keyboard_parts = explode_parts(keyboard_parts, explode_by)

    for layer_name_and_part in keyboard_parts:
        [layer_name, part] = layer_name_and_part
        show_object(part, name=layer_name)

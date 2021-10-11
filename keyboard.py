import cadquery as cq
from timer import timer
from fuse_parts import fuse_parts

from add_bezel import add_bezel

config = {
    # Configurable
    "number_of_rows": 3,
    "number_of_columns": 5,
    "rotation_angle": 15,
    "stagger_preset": "heavy",
    # Utility
    "focus_on": None,
    "explode_by": 4,
    # Structural
    "key_length": 19.05,
    "key_width": 19.05,
    "plate_thickness": 5,
    "pcb_thickness": 3,
    "bezel_size_to_accomodate_wiring": 0,
}

stagger_presets = {
    "light": dict([(3, 0.1), (2, 0.2), (1, 0.1)]),
    "medium": dict([(3, 0.2), (2, 0.4), (1, 0.2)]),
    "heavy": dict([(3, 0.4), (2, 0.8), (1, 0.4)]),
}


def stagger_offset_for_column(column, config):
    if config["stagger_preset"]:
        if config["stagger_preset"] in stagger_presets:
            preset = stagger_presets[config["stagger_preset"]]
            if column in preset:
                return preset[column] * config["key_length"]
    return 0


def key_position(column, row, side_of_board, config):
    column_center_of_workplane_offset = config["key_length"] / 2
    row_center_of_workplane_offset = config["key_width"] / 2

    key_column = (
        column * config["key_length"] + column_center_of_workplane_offset
    )
    key_row = row * config["key_width"] + row_center_of_workplane_offset

    if config["stagger_preset"]:
        relative_column = (
            column
            if side_of_board == "right"
            else config["number_of_columns"] - (column + 1)
        )
        key_row = key_row + stagger_offset_for_column(relative_column, config)

    return (key_column, key_row, 0)


def shift_keys_to_side_of_board(side_of_board, config):
    total_key_width = config["key_width"] * config["number_of_rows"]
    total_key_length = config["key_length"] * config["number_of_columns"]

    return (
        -total_key_length if side_of_board == "right" else 0,
        -total_key_width / 2,
    )


def reposition_key(key, side_of_board, config):
    keys = []

    for column in range(config["number_of_columns"]):
        for row in range(config["number_of_rows"]):
            keys.append(
                key.translate(key_position(column, row, side_of_board, config))
            )

    return fuse_parts(keys).translate(
        shift_keys_to_side_of_board(side_of_board, config)
    )


def make_pcb_key(config):
    switch_middle_pin_hole_size = 2

    pin_for_hotswap_socket_hole_size = 1.5
    left_pin_for_hotswap_socket_distance_from_center = (-3.81, 2.54)
    right_pin_for_hotswap_socket_distance_from_center = (2.54, 5.08)

    switch_stabilizing_pin_hole_size = 1
    switch_stabilizing_hole_distance_from_center = 5.08

    hotswap_socket_height = 1.75

    key = (
        cq.Workplane()
        .box(config["key_length"], config["key_width"], config["pcb_thickness"])
        .faces(">Z")
        .workplane()
        .circle(switch_middle_pin_hole_size)
        .cutBlind(-config["pcb_thickness"])
        .moveTo(-switch_stabilizing_hole_distance_from_center, 0)
        .circle(switch_stabilizing_pin_hole_size)
        .cutBlind(-config["pcb_thickness"])
        .moveTo(switch_stabilizing_hole_distance_from_center, 0)
        .circle(switch_stabilizing_pin_hole_size)
        .cutBlind(-config["pcb_thickness"])
        .moveTo(*left_pin_for_hotswap_socket_distance_from_center)
        .circle(pin_for_hotswap_socket_hole_size)
        .cutBlind(-config["pcb_thickness"])
        .moveTo(*right_pin_for_hotswap_socket_distance_from_center)
        .circle(pin_for_hotswap_socket_hole_size)
        .cutBlind(-config["pcb_thickness"])
    )

    hotswap_socket_cutout = (
        cq.Workplane()
        .lineTo(3.5050, 0)
        .sagittaArc((3.9427, 0.2582), -0.0693)
        .lineTo(4.3507, 0.9965)
        .sagittaArc((5.8823, 1.9), 0.2427)
        .lineTo(10.65, 1.9)
        .sagittaArc((11.15, 2.4), -0.1464)
        .lineTo(11.15, 3.25)
        .lineTo(13.15, 3.25)
        .lineTo(13.15, 5.35)
        .lineTo(11.15, 5.35)
        .lineTo(11.15, 6.1)
        .lineTo(1.5, 6.1)
        .sagittaArc((0, 4.6), -0.4393)
        .lineTo(0, 2.81)
        .lineTo(-2, 2.81)
        .lineTo(-2, 0.71)
        .lineTo(0, 0.71)
        .close()
        .extrude(hotswap_socket_height)
        .translate((-6.21, 0.78, -config["pcb_thickness"] / 2))
    )

    return key.cut(hotswap_socket_cutout)


def make_plate_key(config):
    switch_groove_cutout_length = 5
    switch_groove_cutout_width = 1
    switch_groove_cutout_height = 3.5

    switch_cutout_length = 13.9
    switch_cutout_width = 13.9

    return (
        cq.Workplane()
        .box(
            config["key_length"], config["key_width"], config["plate_thickness"]
        )
        .faces(">Z")
        .workplane()
        .rect(switch_cutout_width, switch_cutout_length)
        .cutBlind(-config["plate_thickness"])
        .faces(">Z")
        .workplane(
            offset=-config["plate_thickness"] + switch_groove_cutout_height
        )
        .moveTo(0, switch_cutout_width / 2 + switch_groove_cutout_width / 2)
        .rect(switch_groove_cutout_length, switch_groove_cutout_width)
        .cutBlind(-switch_groove_cutout_height)
        .faces(">Z")
        .workplane(
            offset=-config["plate_thickness"] + switch_groove_cutout_height
        )
        .moveTo(0, -(switch_cutout_width / 2 + switch_groove_cutout_width / 2))
        .rect(switch_groove_cutout_length, switch_groove_cutout_width)
        .cutBlind(-switch_groove_cutout_height)
    )


def rotate_keys(keys_right, keys_left, config):
    keys_right = keys_right.rotate(
        (0, 0, 0), (0, 0, 1), config["rotation_angle"]
    )
    keys_left = keys_left.rotate(
        (0, 0, 0), (0, 0, 1), -config["rotation_angle"]
    )

    right_side_top_left_corner = keys_right.vertices("<X").val().Center()
    left_side_top_right_corner = keys_left.vertices(">X").val().Center()

    keys_right = keys_right.translate([-right_side_top_left_corner.x, 0, 0])
    keys_left = keys_left.translate([right_side_top_left_corner.x, 0, 0])

    return [keys_right, keys_left]


def make_middle_connector(keys_right, keys_left, thickness):
    right_side_bottom_left_corner = keys_right.vertices("<Y").val().Center()
    right_side_top_left_corner = keys_right.vertices("<X").val().Center()

    middle_connector = (
        keys_right.faces(">Z")
        .workplane()
        .moveTo(right_side_top_left_corner.x, right_side_top_left_corner.y)
        .lineTo(
            right_side_bottom_left_corner.x, right_side_bottom_left_corner.y
        )
        .lineTo(
            -right_side_bottom_left_corner.x, right_side_bottom_left_corner.y
        )
        .close()
        .extrude(-thickness)
    )

    return middle_connector


def make_layer(key, thickness, config):
    keys_right = reposition_key(key, "right", config)
    keys_left = reposition_key(key, "left", config)

    keys = []

    if config["rotation_angle"] == 0:
        return fuse_parts([keys_right, keys_left])
    else:
        [rotated_keys_right, rotated_keys_left] = rotate_keys(
            keys_right, keys_left, config
        )
        middle_connector = make_middle_connector(
            rotated_keys_right, rotated_keys_left, thickness
        )
        return fuse_parts(
            [rotated_keys_right, rotated_keys_left, middle_connector]
        )


print("")
print(
    "size:",
    config["number_of_rows"],
    "x",
    config["number_of_columns"],
    "(total: "
    + str(config["number_of_rows"] * config["number_of_columns"])
    + ")",
)

[time_elapsed, total_time] = timer()

parts = []

if config["focus_on"] == "middle" or config["focus_on"] == None:
    key = make_pcb_key(config)
    layer = make_layer(key, config["pcb_thickness"], config)
    middle_layer_with_bezel = add_bezel(
        layer,
        config["bezel_size_to_accomodate_wiring"],
        config["pcb_thickness"],
    )
    time_elapsed("middle")
    parts.append(middle_layer_with_bezel)


if config["focus_on"] == "top" or config["focus_on"] == None:
    key = make_plate_key(config)
    layer = make_layer(key, config["plate_thickness"], config)
    top_layer_with_bezel = add_bezel(
        layer,
        config["bezel_size_to_accomodate_wiring"],
        config["plate_thickness"],
    )
    time_elapsed("top")
    parts.append(top_layer_with_bezel)


def show_parts(parts):
    for index, part in enumerate(parts):
        part = part.translate(
            [0, 0, 0]
            if config["focus_on"]
            else [0, 0, index * config["explode_by"]]
        )
        show_object(part)


show_parts(parts)

total_time()

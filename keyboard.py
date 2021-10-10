import cadquery as cq
from timer import timer
from fuse_parts import fuse_parts

from add_bezel import add_bezel
from drill_holes import drill_holes

config = {
    # Configurable
    "number_of_rows": 3,
    "number_of_columns": 4,
    "rotation_angle": 15,
    "is_staggered": True,
    "bezel_size": 6,
    # Utility
    "focus_on": None,
    "explode_by": 10,
    # Structural
    "key_length": 19.05,
    "key_width": 19.05,
    "plate_thickness": 5,
    "pcb_thickness": 3,
    "bottom_case_cutout_height": 2,
    "bottom_case_thickness": 5,
    "bottom_case_cutout_height": 3,
}

# Load plugins

cq.Workplane.add_bezel = add_bezel
cq.Workplane.drill_holes = drill_holes


def stagger_offset_for_column(column, config):
    # Light stagger, TODO parameterize
    if column == 3:
        return 0.2 * config["key_length"]
    if column == 2:
        return 0.4 * config["key_length"]
    if column == 1:
        return 0.2 * config["key_length"]
    return 0


def key_position(column, row, side_of_board, config):
    column_center_of_workplane_offset = config["key_length"] / 2
    row_center_of_workplane_offset = config["key_width"] / 2

    key_column = (
        column * config["key_length"] + column_center_of_workplane_offset
    )
    key_row = row * config["key_width"] + row_center_of_workplane_offset

    if config["is_staggered"]:
        key_row = key_row + stagger_offset_for_column(
            column
            if side_of_board == "right"
            else config["number_of_columns"] - (column + 1),
            config,
        )

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
                key.translate(
                    key_position(column, row, side_of_board, config)
                ).translate(shift_keys_to_side_of_board(side_of_board, config))
            )

    return fuse_parts(keys)


def make_pcb_key(config):
    switch_middle_pin_hole_size = 2

    pin_for_hotswap_socket_hole_size = 1.5
    left_pin_for_hotswap_socket_distance_from_center = (-3.81, 2.54)
    right_pin_for_hotswap_socket_distance_from_center = (2.54, 5.08)

    switch_stabilizing_pin_hole_size = 1
    switch_stabilizing_hole_distance_from_center = 5.08

    result = cq.Workplane()

    result = (
        result.box(
            config["key_length"], config["key_width"], config["pcb_thickness"]
        )
        .faces(">Z")
        .workplane()
    )

    result = result.circle(switch_middle_pin_hole_size).cutBlind(
        -config["pcb_thickness"]
    )

    result = (
        result.moveTo(-switch_stabilizing_hole_distance_from_center, 0)
        .circle(switch_stabilizing_pin_hole_size)
        .cutBlind(-config["pcb_thickness"])
    )

    result = (
        result.moveTo(switch_stabilizing_hole_distance_from_center, 0)
        .circle(switch_stabilizing_pin_hole_size)
        .cutBlind(-config["pcb_thickness"])
    )

    result = (
        result.moveTo(*left_pin_for_hotswap_socket_distance_from_center)
        .circle(pin_for_hotswap_socket_hole_size)
        .cutBlind(-config["pcb_thickness"])
    )

    result = (
        result.moveTo(*right_pin_for_hotswap_socket_distance_from_center)
        .circle(pin_for_hotswap_socket_hole_size)
        .cutBlind(-config["pcb_thickness"])
    )

    hotswap_socket_height = 1.75

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

    return result.cut(hotswap_socket_cutout)


def make_plate_key(config):
    switch_groove_cutout_length = 5
    switch_groove_cutout_width = 1
    switch_groove_cutout_height = 3.5

    switch_cutout_length = 13.9
    switch_cutout_width = 13.9

    result = cq.Workplane()

    result = result.box(
        config["key_length"], config["key_width"], config["plate_thickness"]
    )

    result = (
        result.faces(">Z")
        .workplane()
        .rect(switch_cutout_width, switch_cutout_length)
        .cutBlind(-config["plate_thickness"])
    )

    result = (
        result.faces(">Z")
        .workplane(
            offset=-config["plate_thickness"] + switch_groove_cutout_height
        )
        .moveTo(0, switch_cutout_width / 2 + switch_groove_cutout_width / 2)
        .rect(switch_groove_cutout_length, switch_groove_cutout_width)
        .cutBlind(-switch_groove_cutout_height)
    )

    result = (
        result.faces(">Z")
        .workplane(
            offset=-config["plate_thickness"] + switch_groove_cutout_height
        )
        .moveTo(0, -(switch_cutout_width / 2 + switch_groove_cutout_width / 2))
        .rect(switch_groove_cutout_length, switch_groove_cutout_width)
        .cutBlind(-switch_groove_cutout_height)
    )

    return result


def make_bottom_layer_key(config):
    result = cq.Workplane()
    thickness = (
        config["bottom_case_thickness"] - config["bottom_case_cutout_height"]
    )
    result = result.box(config["key_length"], config["key_width"], thickness)
    return result


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

if config["focus_on"] == "top" or config["focus_on"] == None:
    top_layer = (
        make_layer(
            make_plate_key(config),
            config["plate_thickness"],
            config,
        )
        .add_bezel(
            config["bezel_size"],
            config["plate_thickness"],
        )
        .drill_holes(
            config["bezel_size"], config["rotation_angle"], is_top=True
        )
    )
    time_elapsed("top")

    show_object(
        top_layer.translate(
            [0, 0, 0]
            if config["focus_on"]
            else [
                0,
                0,
                (config["pcb_thickness"] + config["plate_thickness"]) / 2
                + config["explode_by"],
            ]
        )
    )

if config["focus_on"] == "middle" or config["focus_on"] == None:
    middle_layer = (
        make_layer(
            make_pcb_key(config),
            config["pcb_thickness"],
            config,
        )
        .add_bezel(
            config["bezel_size"],
            config["pcb_thickness"],
        )
        .drill_holes(config["bezel_size"], config["rotation_angle"])
    )
    show_object(middle_layer)
    time_elapsed("middle")

if config["focus_on"] == "bottom" or config["focus_on"] == None:
    bottom_layer = (
        make_layer(
            make_bottom_layer_key(config),
            # Adjust thickness to create a cutout effect
            config["bottom_case_thickness"]
            - config["bottom_case_cutout_height"],
            config,
        )
        .add_bezel(
            config["bezel_size"],
            config["bottom_case_thickness"],
        )
        .drill_holes(
            config["bezel_size"], config["rotation_angle"], is_bottom=True
        )
    )
    time_elapsed("bottom")

    show_object(
        bottom_layer.translate(
            [0, 0, 0]
            if config["focus_on"]
            else [
                0,
                0,
                -(config["pcb_thickness"] + config["plate_thickness"]) / 2
                - config["explode_by"],
            ]
        )
    )

total_time()

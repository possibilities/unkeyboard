import cadquery as cq
from timer import timer
from fuse_parts import fuse_parts

config = {
    # Configurable
    "number_of_rows": 2,
    "number_of_columns": 3,
    "rotation_angle": 20,
    "stagger_preset": "light",
    "game_pad": False,
    # Utility
    "focus_on": None,
    "explode_by": 20,
    "keychain": False,
    "has_microcontroller": True,
    # Structural
    "key_size": 19.05,
    "plate_thickness": 5,
    "pcb_thickness": 3,
    "bottom_thickness": 5,
    "microcontroller_length": 19,
    "microcontroller_width": 33,
    "case_exterior_thickness": 2,
    "case_lip_size": 3,
}

stagger_presets = {
    "light": dict([(3, 0.1), (2, 0.2), (1, 0.1)]),
    "medium": dict([(3, 0.2), (2, 0.4), (1, 0.2)]),
    "heavy": dict([(3, 0.4), (2, 0.8), (1, 0.4)]),
}


def cqplugin(func):
    setattr(cq.Workplane, func.__name__, func)
    return func


def show_objects(objects):
    for o in objects:
        show_object(o)
    return cq.Workplane()


# For keychain remove unnecessary things
if config["keychain"]:
    config["has_microcontroller"] = False
    config["rotation_angle"] = 0
    config["game_pad"] = True
    config["stagger_preset"] = None


def find_stagger_offset_to_column(column, config):
    if config["stagger_preset"]:
        if config["stagger_preset"] in stagger_presets:
            preset = stagger_presets[config["stagger_preset"]]
            if column in preset:
                return preset[column] * config["key_size"]
    return 0


@cqplugin
def shift_key_to_position_on_right_side(key, column, row, config):
    column_center_of_workplane_offset = config["key_size"] / 2
    row_center_of_workplane_offset = config["key_size"] / 2

    key_column = column * config["key_size"] + column_center_of_workplane_offset
    key_row = row * config["key_size"] + row_center_of_workplane_offset

    if config["stagger_preset"]:
        key_row = key_row + find_stagger_offset_to_column(column, config)

    return key.translate((key_column, key_row, 0))


@cqplugin
def shift_key_to_position_on_left_side(key, column, row, config):
    column_center_of_workplane_offset = config["key_size"] / 2
    row_center_of_workplane_offset = config["key_size"] / 2

    key_column = column * config["key_size"] + column_center_of_workplane_offset
    key_row = row * config["key_size"] + row_center_of_workplane_offset

    if config["stagger_preset"]:
        column = config["number_of_columns"] - (column + 1)
        key_row = key_row + find_stagger_offset_to_column(column, config)

    return key.translate((key_column, key_row, 0))


@cqplugin
def shift_key_to_right_side_of_board(key, config):
    total_key_width = config["key_size"] * config["number_of_rows"]
    total_key_length = config["key_size"] * config["number_of_columns"]
    return key.translate((-total_key_length, -total_key_width / 2))


@cqplugin
def shift_key_to_left_side_of_board(key, config):
    total_key_width = config["key_size"] * config["number_of_rows"]
    return key.translate((-0 - total_key_width / 2, 0))


@cqplugin
def rotate_keys_on_right_side_of_board(keys, config):
    if config["rotation_angle"] != 0:
        keys = keys.rotateAboutCenter((0, 0, 1), config["rotation_angle"])

    return keys


@cqplugin
def rotate_keys_on_left_side_of_board(keys, config):
    if config["rotation_angle"] != 0:
        keys = keys.rotateAboutCenter((0, 0, 1), -config["rotation_angle"])

    return keys


def find_coords_to_shift_right_keys_to_side_of_microcontroller(keys, config):
    right_side_furthest_vertext_to_the_left = keys.vertices("<X")
    return [
        -right_side_furthest_vertext_to_the_left.val().Center().x
        + (
            config["microcontroller_length"] / 2
            if config["has_microcontroller"]
            else 0
        )
        + config["case_lip_size"],
        0,
        0,
    ]


def find_coords_to_shift_left_keys_to_side_of_microcontroller(keys, config):
    left_side_furthest_vertext_to_the_right = keys.vertices(">X")
    return [
        -left_side_furthest_vertext_to_the_right.val().Center().x
        - (
            config["microcontroller_length"] / 2
            if config["has_microcontroller"]
            else 0
        )
        - config["case_lip_size"],
        0,
        0,
    ]


def find_coords_to_shift_right_keys_to_top_of_microcontroller(keys, config):
    right_side_furthest_vertext_to_the_left = keys.vertices("<X").vertices(">Y")
    return [
        0,
        -right_side_furthest_vertext_to_the_left.val().Center().y
        + config["microcontroller_width"] / 2
        + config["case_lip_size"],
        0,
    ]


def find_coords_to_shift_left_keys_to_top_of_microcontroller(keys, config):
    left_side_furthest_vertext_to_the_right = keys.vertices(">X").vertices(">Y")
    return [
        0,
        -left_side_furthest_vertext_to_the_right.val().Center().y
        + config["microcontroller_width"] / 2
        + config["case_lip_size"],
        0,
    ]


@cqplugin
def add_bezel(part, size, thickness, direction="up"):
    if size == 0:
        return part
    part = (
        part.tag("layer")
        .faces("<Z" if direction == "up" else ">Z", tag="layer")
        .wires(cq.selectors.AreaNthSelector(-1))
        .toPending()
        .offset2D(size, "intersection")
        .faces("<Z" if direction == "up" else ">Z", tag="layer")
        .wires(cq.selectors.AreaNthSelector(-1))
        .toPending()
        .extrude(thickness if direction == "up" else -thickness)
    )
    return part


def make_positioned_keys(key, side_of_board, config):
    keys = []

    for column in range(config["number_of_columns"]):
        for row in range(config["number_of_rows"]):
            keys.append(
                key.shift_key_to_right_side_of_board(
                    config
                ).shift_key_to_position_on_right_side(column, row, config)
                if side_of_board == "right"
                else key.shift_key_to_left_side_of_board(
                    config
                ).shift_key_to_position_on_left_side(column, row, config)
            )

    return fuse_parts(keys)


def make_pcb_key(config):
    switch_middle_pin_hole_size = 2

    pin_for_hotswap_socket_hole_size = 1.5
    left_pin_for_hotswap_socket_distance_from_center = (-3.81, 2.54)
    right_pin_for_hotswap_socket_distance_from_center = (2.54, 5.08)

    switch_stabilizing_pin_hole_size = 1
    switch_stabilizing_hole_distance_from_center = 5.08

    hotswap_socket_height = 1.8

    key = (
        cq.Workplane()
        .box(config["key_size"], config["key_size"], config["pcb_thickness"])
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


def make_bottom_key(config):
    key = cq.Workplane().box(
        config["key_size"], config["key_size"], config["bottom_thickness"]
    )
    return key


def make_plate_key(config):
    switch_cutout_size = 13.9

    switch_groove_cutout_length = 5
    switch_groove_cutout_width = 1
    switch_groove_cutout_height = 3.5

    return (
        cq.Workplane()
        .box(config["key_size"], config["key_size"], config["plate_thickness"])
        .faces(">Z")
        .workplane()
        .rect(switch_cutout_size, switch_cutout_size)
        .cutBlind(-config["plate_thickness"])
        .faces(">Z")
        .workplane(
            offset=-config["plate_thickness"] + switch_groove_cutout_height
        )
        .moveTo(0, switch_cutout_size / 2 + switch_groove_cutout_width / 2)
        .rect(switch_groove_cutout_length, switch_groove_cutout_width)
        .cutBlind(-switch_groove_cutout_height)
        .faces(">Z")
        .workplane(
            offset=-config["plate_thickness"] + switch_groove_cutout_height
        )
        .moveTo(0, -(switch_cutout_size / 2 + switch_groove_cutout_width / 2))
        .rect(switch_groove_cutout_length, switch_groove_cutout_width)
        .cutBlind(-switch_groove_cutout_height)
    )


def make_microcontroller_container(thickness, config):
    container = cq.Workplane().box(
        config["microcontroller_length"],
        config["microcontroller_width"],
        thickness,
    )
    return container


def make_layer(key, thickness, config):
    key_parts = []
    microcontroller_parts = []
    if not config["game_pad"]:
        keys_right = make_positioned_keys(key, "right", config)
        keys_right = keys_right.add_bezel(config["case_lip_size"], thickness)
        keys_right = keys_right.rotate_keys_on_right_side_of_board(config)
        keys_right = keys_right.translate(
            find_coords_to_shift_right_keys_to_side_of_microcontroller(
                keys_right, config
            )
        ).translate(
            find_coords_to_shift_right_keys_to_top_of_microcontroller(
                keys_right, config
            )
        )
        key_parts.append(keys_right)

    keys_left = make_positioned_keys(key, "left", config)
    keys_left = keys_left.add_bezel(config["case_lip_size"], thickness)
    keys_left = keys_left.rotate_keys_on_left_side_of_board(config)
    keys_left = keys_left.translate(
        find_coords_to_shift_left_keys_to_side_of_microcontroller(
            keys_left, config
        )
    ).translate(
        find_coords_to_shift_left_keys_to_top_of_microcontroller(
            keys_left, config
        )
    )
    key_parts.append(keys_left)

    if config["has_microcontroller"]:
        microcontroller = make_microcontroller_container(thickness, config)
        microcontroller = microcontroller.add_bezel(
            config["case_lip_size"], thickness
        )
        microcontroller_parts.append(microcontroller)

    if config["rotation_angle"] > 0 and config["has_microcontroller"]:
        left_side_bottom_right_corner = keys_left.vertices("<Y").val().Center()
        left_microcontroller_wing = (
            keys_left.faces(">Z")
            .workplane()
            .moveTo(
                -config["microcontroller_length"] / 2 - config["case_lip_size"],
                config["microcontroller_width"] / 2 + config["case_lip_size"],
            )
            .lineTo(
                -config["microcontroller_length"] / 2 - config["case_lip_size"],
                -config["microcontroller_width"] / 2 - config["case_lip_size"],
            )
            .lineTo(
                left_side_bottom_right_corner.x, left_side_bottom_right_corner.y
            )
            .close()
            .extrude(-thickness, combine=False)
        )

        microcontroller_parts.append(left_microcontroller_wing)

        if not config["game_pad"]:
            right_side_bottom_left_corner = (
                keys_left.vertices("<Y").val().Center()
            )
            right_microcontroller_wing = (
                keys_right.faces(">Z")
                .workplane()
                .moveTo(
                    config["microcontroller_length"] / 2
                    + config["case_lip_size"],
                    config["microcontroller_width"] / 2
                    + config["case_lip_size"],
                )
                .lineTo(
                    config["microcontroller_length"] / 2
                    + config["case_lip_size"],
                    -config["microcontroller_width"] / 2
                    - config["case_lip_size"],
                )
                .lineTo(
                    -right_side_bottom_left_corner.x,
                    right_side_bottom_left_corner.y,
                )
                .close()
                .extrude(-thickness, combine=False)
            )

        microcontroller_parts.append(right_microcontroller_wing)

    return fuse_parts([*key_parts, *microcontroller_parts])


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


@cqplugin
def add_case_lip_to_top_layer(top_layer):
    return top_layer


[time_elapsed, total_time] = timer()

parts = []

if config["focus_on"] == "top" or config["focus_on"] == None:
    key = make_plate_key(config)
    layer = make_layer(
        key, config["plate_thickness"], config
    ).add_case_lip_to_top_layer()
    time_elapsed("top")
    position = [
        0,
        0,
        4
        if config["focus_on"]
        else (12 + config["explode_by"] if config["explode_by"] else 4),
    ]
    show_object(layer.translate(position))

if config["focus_on"] == "middle" or config["focus_on"] == None:
    key = make_pcb_key(config)
    layer = make_layer(key, config["pcb_thickness"], config)
    time_elapsed("middle")
    position = [0, 0, 0]
    show_object(layer)

if config["focus_on"] == "bottom" or config["focus_on"] == None:
    key = make_bottom_key(config)
    layer = make_layer(key, config["bottom_thickness"], config)
    time_elapsed("bottom")
    position = [
        0,
        0,
        0
        if config["focus_on"]
        else (-4 - config["explode_by"] if config["explode_by"] else -4),
    ]
    show_object(layer.translate(position))


total_time()

import cadquery as cq
from timer import timer
from fuse_parts import fuse_parts

config = {
    # Configurable
    "number_of_rows": 2,
    "number_of_columns": 3,
    "rotation_angle": 20,
    "stagger_preset": "light",
    # Utility
    "focus_on": None,
    "explode_by": 20,
    "keychain": False,
    "has_microcontroller": True,
    "left_side_only": False,
    "right_side_only": False,
    # Structural
    "key_size": 19.05,
    "plate_thickness": 5,
    "pcb_thickness": 3,
    "bottom_thickness": 5,
    "microcontroller_length": 19,
    "microcontroller_width": 33,
    "case_exterior_thickness": 2,
    "bezel_for_screws_size": 5,
    "screw_radius": 1,
}

stagger_presets = {
    "light": dict([(3, 0.1), (2, 0.2), (1, 0.1)]),
    "medium": dict([(3, 0.2), (2, 0.4), (1, 0.2)]),
    "heavy": dict([(3, 0.4), (2, 0.8), (1, 0.4)]),
}

if config["stagger_preset"]:
    if config["rotation_angle"] > 84:
        raise Exception(
            "`rotation_angle` must be less than or equal to 84 when keys are staggered"
        )
else:
    if config["rotation_angle"] > 90:
        raise Exception(
            "`rotation_angle` must be less than or equal to 90 when keys are staggered"
        )


if config["right_side_only"] and config["left_side_only"]:
    raise Exception(
        "`right_side_only` and `left_side_only` cannot both be enabled"
    )


# For keychain remove unnecessary things
if config["keychain"]:
    config["has_microcontroller"] = False
    config["rotation_angle"] = 0
    config["left_side_only"] = True
    config["right_side_only"] = False
    config["stagger_preset"] = None


def cq_workplane_plugin(func):
    setattr(cq.Workplane, func.__name__, func)
    return func


def show_objects(objects):
    for o in objects:
        show_object(o)
    return cq.Workplane()


def find_stagger_offset_to_column(column, config):
    if config["stagger_preset"]:
        if config["stagger_preset"] in stagger_presets:
            preset = stagger_presets[config["stagger_preset"]]
            if column in preset:
                return preset[column] * config["key_size"]
    return 0


@cq_workplane_plugin
def rotate_keys_on_right_side_of_board(keys, config):
    if config["rotation_angle"] != 0:
        keys = keys.rotateAboutCenter((0, 0, 1), config["rotation_angle"])

    return keys


@cq_workplane_plugin
def rotate_keys_on_left_side_of_board(keys, config):
    if config["rotation_angle"] != 0:
        keys = keys.rotateAboutCenter((0, 0, 1), -config["rotation_angle"])

    return keys


def find_coords_to_shift_right_keys_to_center_after_rotation(keys, config):
    right_side_furthest_vertext_to_the_left = keys.vertices("<X")
    return [
        -right_side_furthest_vertext_to_the_left.val().Center().x,
        0,
        0,
    ]


def find_coords_to_shift_left_keys_to_center_after_rotation(keys, config):
    left_side_furthest_vertext_to_the_right = keys.vertices(">X")
    return [
        -left_side_furthest_vertext_to_the_right.val().Center().x,
        0,
        0,
    ]


def find_coords_to_shift_right_keys_to_top_of_microcontroller(keys, config):
    right_side_furthest_vertext_to_the_left = keys.vertices("<X").vertices(">Y")
    return [
        config["microcontroller_length"] / 2,
        -right_side_furthest_vertext_to_the_left.val().Center().y
        + config["microcontroller_width"] / 2,
        0,
    ]


def find_coords_to_shift_left_keys_to_top_of_microcontroller(keys, config):
    left_side_furthest_vertext_to_the_right = keys.vertices(">X").vertices(">Y")
    return [
        -config["microcontroller_length"] / 2,
        -left_side_furthest_vertext_to_the_right.val().Center().y
        + config["microcontroller_width"] / 2,
        0,
    ]


def make_positioned_keys(key, side_of_board, config):
    keys = []

    for column in range(config["number_of_columns"]):
        for row in range(config["number_of_rows"]):
            if side_of_board == "right":
                keys.append(
                    key.translate(
                        [
                            config["key_size"] * column,
                            config["key_size"] * row
                            + find_stagger_offset_to_column(column, config),
                            0,
                        ]
                    )
                )
            else:
                keys.append(
                    key.translate(
                        [
                            -config["key_size"] * column,
                            config["key_size"] * row
                            + find_stagger_offset_to_column(column, config),
                            0,
                        ]
                    )
                )

    center_of_plane_coords = [
        (config["key_size"] * (config["number_of_columns"] - 1)) / 2,
        -(config["key_size"] * (config["number_of_rows"] - 1)) / 2,
        0,
    ]

    return fuse_parts(keys).translate(center_of_plane_coords)


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


def make_connector_between_right_side_and_microcontroller(
    keys, microcontroller, thickness
):
    right_side_top_left = (
        keys.faces(">Z").vertices("<X").vertices(">Y").val().Center()
    )
    right_side_bottom_left = (
        keys.faces(">Z").vertices("<Y").vertices(">X").val().Center()
    )
    center_bottom_right = (
        microcontroller.faces(">Z").vertices(">X").vertices("<Y").val().Center()
    )

    right_connector = (
        microcontroller.faces(">Z")
        .workplane()
        .moveTo(right_side_top_left.x, right_side_top_left.y)
        .lineTo(center_bottom_right.x, center_bottom_right.y)
        .lineTo(right_side_bottom_left.x, right_side_bottom_left.y)
        .close()
        .extrude(-thickness, combine=False)
    )

    return right_connector


def make_connector_between_left_side_and_microcontroller(
    keys, microcontroller, thickness
):
    left_side_top_right = (
        keys.faces(">Z").vertices(">X").vertices(">Y").val().Center()
    )
    left_side_bottom_right = (
        keys.faces(">Z").vertices("<Y").vertices("<X").val().Center()
    )
    center_bottom_left = (
        microcontroller.faces(">Z").vertices("<X").vertices("<Y").val().Center()
    )

    left_connector = (
        microcontroller.faces(">Z")
        .workplane()
        .moveTo(left_side_top_right.x, left_side_top_right.y)
        .lineTo(center_bottom_left.x, center_bottom_left.y)
        .lineTo(left_side_bottom_right.x, left_side_bottom_right.y)
        .close()
        .extrude(-thickness, combine=False)
    )

    return left_connector


@cq_workplane_plugin
def add_rails_for_screws_on_right_side_of_board(self, thickness):
    top_right = self.faces(">Z").vertices(">X").vertices(">Y").val().Center()
    bottom_right = self.faces(">Z").vertices(">X").vertices("<Y").val().Center()
    self = (
        self.faces(">Z")
        .workplane()
        .moveTo(
            top_right.x,
            top_right.y,
        )
        .lineTo(
            top_right.x + config["bezel_for_screws_size"],
            top_right.y,
        )
        .lineTo(
            top_right.x + config["bezel_for_screws_size"],
            bottom_right.y,
        )
        .lineTo(top_right.x, bottom_right.y)
        .close()
        .extrude(-thickness)
    )

    top_left = self.faces(">Z").vertices("<X").vertices(">Y").val().Center()
    bottom_left = self.faces(">Z").vertices("<X").vertices("<Y").val().Center()
    self = (
        self.faces(">Z")
        .workplane()
        .moveTo(
            top_left.x,
            top_left.y,
        )
        .lineTo(
            top_left.x - config["bezel_for_screws_size"],
            top_left.y,
        )
        .lineTo(
            top_left.x - config["bezel_for_screws_size"],
            bottom_left.y,
        )
        .lineTo(
            top_left.x,
            bottom_left.y,
        )
        .close()
        .extrude(-thickness)
    )

    return self


@cq_workplane_plugin
def add_rails_for_screws_on_left_side_of_board(self, thickness):
    top_right = self.faces(">Z").vertices(">X").vertices(">Y").val().Center()
    bottom_right = self.faces(">Z").vertices("<Y").vertices("<X").val().Center()
    self = (
        self.faces(">Z")
        .workplane()
        .moveTo(
            top_right.x,
            top_right.y,
        )
        .lineTo(
            top_right.x + config["bezel_for_screws_size"],
            top_right.y,
        )
        .lineTo(
            top_right.x + config["bezel_for_screws_size"],
            bottom_right.y,
        )
        .lineTo(
            top_right.x,
            bottom_right.y,
        )
        .close()
        .extrude(-thickness)
    )

    top_left = self.faces(">Z").vertices("<X").vertices(">Y").val().Center()
    bottom_left = self.faces(">Z").vertices("<X").vertices("<Y").val().Center()
    self = (
        self.faces(">Z")
        .workplane()
        .moveTo(
            top_left.x,
            top_left.y,
        )
        .lineTo(
            top_left.x - config["bezel_for_screws_size"],
            top_left.y,
        )
        .lineTo(
            top_left.x - config["bezel_for_screws_size"],
            bottom_left.y,
        )
        .lineTo(
            top_left.x,
            bottom_left.y,
        )
        .close()
        .extrude(-thickness)
    )

    return self


@cq_workplane_plugin
def add_screw_holes_to_left_side_of_board(self, thickness):
    top_right = self.faces(">Z").vertices(">X").vertices(">Y").val().Center()
    top_left = self.faces(">Z").vertices("<X").vertices(">Y").val().Center()
    bottom_right = self.faces(">Z").vertices("<Y").vertices(">X").val().Center()
    bottom_left = self.faces(">Z").vertices("<X").vertices("<Y").val().Center()

    screw_distance_from_edge = config["bezel_for_screws_size"] / 2

    self = (
        self.faces(">Z")
        .workplane()
        .pushPoints(
            [
                [
                    top_right.x - screw_distance_from_edge,
                    top_right.y - screw_distance_from_edge,
                ],
                [
                    bottom_right.x - screw_distance_from_edge,
                    bottom_right.y + screw_distance_from_edge,
                ],
                [
                    bottom_left.x + screw_distance_from_edge,
                    bottom_left.y + screw_distance_from_edge,
                ],
                [
                    top_left.x + screw_distance_from_edge,
                    top_left.y - screw_distance_from_edge,
                ],
            ]
        )
        .circle(config["screw_radius"])
        .cutBlind(-thickness)
    )
    return self


@cq_workplane_plugin
def add_screw_holes_to_right_side_of_board(self, thickness):
    top_right = self.faces(">Z").vertices(">X").vertices(">Y").val().Center()
    top_left = self.faces(">Z").vertices("<X").vertices(">Y").val().Center()
    bottom_right = self.faces(">Z").vertices(">X").vertices("<Y").val().Center()
    bottom_left = self.faces(">Z").vertices("<Y").vertices("<X").val().Center()

    screw_distance_from_edge = config["bezel_for_screws_size"] / 2

    self = (
        self.faces(">Z")
        .workplane()
        .pushPoints(
            [
                [
                    top_right.x - screw_distance_from_edge,
                    top_right.y - screw_distance_from_edge,
                ],
                [
                    bottom_right.x - screw_distance_from_edge,
                    bottom_right.y + screw_distance_from_edge,
                ],
                [
                    bottom_left.x + screw_distance_from_edge,
                    bottom_left.y + screw_distance_from_edge,
                ],
                [
                    top_left.x + screw_distance_from_edge,
                    top_left.y - screw_distance_from_edge,
                ],
            ]
        )
        .circle(config["screw_radius"])
        .cutBlind(-thickness)
    )
    return self


def make_layer(key, thickness, config):
    key_parts = []
    microcontroller_parts = []

    if not config["left_side_only"]:
        keys_right = make_positioned_keys(key, "right", config)
        keys_right = keys_right.add_rails_for_screws_on_right_side_of_board(
            thickness
        )
        keys_right = keys_right.add_screw_holes_to_right_side_of_board(
            thickness
        )
        keys_right = keys_right.rotate_keys_on_right_side_of_board(config)
        keys_right = keys_right.translate(
            find_coords_to_shift_right_keys_to_center_after_rotation(
                keys_right, config
            )
        ).translate(
            find_coords_to_shift_right_keys_to_top_of_microcontroller(
                keys_right, config
            )
        )
        key_parts.append(keys_right)

    if not config["right_side_only"]:
        keys_left = make_positioned_keys(key, "left", config)
        keys_left = keys_left.add_rails_for_screws_on_left_side_of_board(
            thickness
        )
        keys_left = keys_left.add_screw_holes_to_left_side_of_board(thickness)
        keys_left = keys_left.rotate_keys_on_left_side_of_board(config)
        keys_left = keys_left.translate(
            find_coords_to_shift_left_keys_to_center_after_rotation(
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
        microcontroller_parts.append(microcontroller)

    if config["rotation_angle"] > 0 and config["has_microcontroller"]:
        if not config["right_side_only"]:
            left_microcontroller = (
                make_connector_between_left_side_and_microcontroller(
                    keys_left, microcontroller, thickness
                )
            )
            microcontroller_parts.append(left_microcontroller)

        if not config["left_side_only"]:
            right_microcontroller = (
                make_connector_between_right_side_and_microcontroller(
                    keys_right, microcontroller, thickness
                )
            )
            microcontroller_parts.append(right_microcontroller)

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


[time_elapsed, total_time] = timer()

parts = []

if config["focus_on"] == "top" or config["focus_on"] == None:
    key = make_plate_key(config)
    layer = make_layer(key, config["plate_thickness"], config)
    time_elapsed("top")
    position = [
        0,
        0,
        4
        if config["focus_on"]
        else (4 + config["explode_by"] if config["explode_by"] else 4),
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

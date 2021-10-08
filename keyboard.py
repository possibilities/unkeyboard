import time

# Configurable

config_number_of_rows = 3
config_number_of_columns = 6

config_angle = 15
config_stagger = True

# Structural

config_key_length = 19.05
config_key_width = 19.05

config_plate_thickness = 5
config_pcb_thickness = 3


def fuse_parts(parts):
    part_values = [part.val() for part in parts]
    fused_parts = part_values[0].fuse(*part_values[1:], glue=True).clean()
    return cq.Workplane().newObject([fused_parts])


def timer():
    start = time.time()
    last_split = time.time()

    def _time_elapsed(name):
        nonlocal last_split
        print(name + ": " + str(time.time() - last_split))
        last_split = time.time()

    def _total_time():
        print("total: " + str(time.time() - start))

    return [_time_elapsed, _total_time]


def stagger_offset_for_column(x):
    if config_stagger == None:
        return 0

    # Light stagger, TODO parameterize
    if x == 3:
        return 0.1 * config_key_length
    if x == 2:
        return 0.2 * config_key_length
    if x == 1:
        return 0.1 * config_key_length
    return 0


def key_position(x, y, number_of_columns, side_of_board):
    x_center_of_workplane_offset = config_key_length / 2
    y_center_of_workplane_offset = config_key_width / 2

    key_x = x * config_key_length + x_center_of_workplane_offset
    key_y = (
        y * config_key_width
        + stagger_offset_for_column(
            x if side_of_board == "left" else number_of_columns - (x + 1)
        )
        + y_center_of_workplane_offset
    )

    return (key_x, key_y, 0)


def shift_keys_to_side_of_board(side_of_board):
    total_key_width = config_key_width * config_number_of_rows
    total_key_length = config_key_length * config_number_of_columns

    return (
        -total_key_length if side_of_board == "right" else 0,
        -total_key_width / 2,
    )


def reposition_key(key, side_of_board):
    keys = []

    for x in range(config_number_of_columns):
        for y in range(config_number_of_rows):
            keys.append(
                key.translate(
                    key_position(x, y, config_number_of_columns, side_of_board)
                ).translate(shift_keys_to_side_of_board(side_of_board))
            )

    return fuse_parts(keys)


def make_pcb_key():
    switch_middle_pin_hole_size = 2

    pin_for_hotswap_socket_hole_size = 1.5
    left_pin_for_hotswap_socket_distance_from_center = (-3.81, 2.54)
    right_pin_for_hotswap_socket_distance_from_center = (2.54, 5.08)

    switch_stabilizing_pin_hole_size = 1
    switch_stabilizing_left_in_hole_distance_from_center = (-5.08, 0)
    switch_stabilizing_right_in_hole_distance_from_center = (5.08, 0)

    result = cq.Workplane()

    result = result.box(
        config_key_length, config_key_width, config_pcb_thickness
    )

    switch_middle_pin_hole_cutout = (
        cq.Workplane()
        .circle(switch_middle_pin_hole_size)
        .extrude(config_pcb_thickness)
        .translate([0, 0, -config_pcb_thickness / 2])
    )
    result = result.cut(switch_middle_pin_hole_cutout)

    left_switch_stabilizing_pin_hole_cutout = (
        cq.Workplane()
        .circle(switch_stabilizing_pin_hole_size)
        .extrude(config_pcb_thickness)
        .translate(switch_stabilizing_left_in_hole_distance_from_center)
        .translate([0, 0, -config_pcb_thickness / 2])
    )
    result = result.cut(left_switch_stabilizing_pin_hole_cutout)

    right_switch_stabilizing_pin_hole_cutout = (
        cq.Workplane()
        .circle(switch_stabilizing_pin_hole_size)
        .extrude(config_pcb_thickness)
        .translate(switch_stabilizing_right_in_hole_distance_from_center)
        .translate([0, 0, -config_pcb_thickness / 2])
    )
    result = result.cut(right_switch_stabilizing_pin_hole_cutout)

    left_pin_for_hotswap_socket_cutout = (
        cq.Workplane()
        .circle(pin_for_hotswap_socket_hole_size)
        .extrude(config_pcb_thickness)
        .translate(left_pin_for_hotswap_socket_distance_from_center)
        .translate([0, 0, -config_pcb_thickness / 2])
    )
    result = result.cut(left_pin_for_hotswap_socket_cutout)

    right_pin_for_hotswap_socket_cutout = (
        cq.Workplane()
        .circle(pin_for_hotswap_socket_hole_size)
        .extrude(config_pcb_thickness)
        .translate(right_pin_for_hotswap_socket_distance_from_center)
        .translate([0, 0, -config_pcb_thickness / 2])
    )
    result = result.cut(right_pin_for_hotswap_socket_cutout)

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
        .translate((-6.21, 0.78, -config_pcb_thickness / 2))
    )

    return result.cut(hotswap_socket_cutout)


def make_plate_key():
    switch_groove_cutout_length = 5
    switch_groove_cutout_width = 1
    switch_groove_cutout_height = 3.5

    switch_cutout_length = 13.9
    switch_cutout_width = 13.9

    result = cq.Workplane()

    result = result.box(
        config_key_length, config_key_width, config_plate_thickness
    )

    switch_hole_cutout = cq.Workplane().box(
        switch_cutout_width, switch_cutout_length, config_plate_thickness
    )
    result = result.cut(switch_hole_cutout)

    switch_top_groove_cutout = (
        cq.Workplane()
        .box(
            switch_groove_cutout_length,
            switch_groove_cutout_width,
            switch_groove_cutout_height,
        )
        .translate(
            [
                0,
                switch_cutout_width / 2 + switch_groove_cutout_width / 2,
                -(config_plate_thickness - switch_groove_cutout_height) / 2,
            ]
        )
    )
    result = result.cut(switch_top_groove_cutout)

    switch_bottom_groove_cutout = (
        cq.Workplane()
        .box(
            switch_groove_cutout_length,
            switch_groove_cutout_width,
            switch_groove_cutout_height,
        )
        .translate(
            [
                0,
                -(switch_cutout_width / 2 + switch_groove_cutout_width / 2),
                -(config_plate_thickness - switch_groove_cutout_height) / 2,
            ]
        )
    )
    result = result.cut(switch_bottom_groove_cutout)

    return result


def angle_keys(keys_right, keys_left):
    keys_right = keys_right.rotate((0, 0, 0), (0, 0, 1), config_angle)
    keys_left = keys_left.rotate((0, 0, 0), (0, 0, 1), -config_angle)

    tilt_right_side_top_left_corner = keys_right.vertices("<X").val().Center()
    tilt_left_side_top_right_corner = keys_left.vertices(">X").val().Center()

    keys_right = keys_right.translate(
        [-tilt_right_side_top_left_corner.x, 0, 0]
    )
    keys_left = keys_left.translate([tilt_right_side_top_left_corner.x, 0, 0])

    return [keys_right, keys_left]


def make_middle_connector(keys_right, keys_left, thickness):
    tilt_right_side_bottom_left_corner = (
        keys_right.vertices("<Y").val().Center()
    )
    tilt_right_side_top_left_corner = keys_right.vertices("<X").val().Center()

    middle_connector = (
        keys_right.faces("front")
        .workplane()
        .moveTo(
            tilt_right_side_top_left_corner.x,
            tilt_right_side_top_left_corner.y,
        )
        .lineTo(
            tilt_right_side_bottom_left_corner.x,
            tilt_right_side_bottom_left_corner.y,
        )
        .lineTo(
            -tilt_right_side_bottom_left_corner.x,
            tilt_right_side_bottom_left_corner.y,
        )
        .close()
        .extrude(-thickness)
    )

    return middle_connector


def make_keys(make_key, thickness):
    key = make_key()

    keys_right = reposition_key(key, side_of_board="left")
    keys_left = reposition_key(key, side_of_board="right")

    if config_angle == 0:
        return fuse_parts([keys_right, keys_left])
    else:
        [keys_right, keys_left] = angle_keys(keys_right, keys_left)

        middle_connector = make_middle_connector(
            keys_right, keys_left, thickness
        )
        return fuse_parts([keys_right, keys_left, middle_connector])


print("")
print(
    "size:",
    config_number_of_rows,
    "x",
    config_number_of_columns,
    "(total: " + str(config_number_of_rows * config_number_of_columns) + ")",
)


[time_elapsed, total_time] = timer()

pcb_keys = make_keys(make_pcb_key, config_pcb_thickness)
time_elapsed("pcb")

plate_keys = make_keys(make_plate_key, config_plate_thickness)
time_elapsed("plate")

show_object(pcb_keys.translate([0, 0, -config_pcb_thickness / 2]))
show_object(plate_keys.translate([0, 0, config_plate_thickness / 2]))

total_time()

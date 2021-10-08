import time
import cadquery as cq

number_of_rows = 3
number_of_columns = 6

key_length = 19.05
key_width = 19.05

plate_thickness = 5
pcb_thickness = 3


def make_pcb_key():
    switch_middle_pin_hole_size = 2

    pin_for_hotswap_socket_hole_size = 1.5
    left_pin_for_hotswap_socket_distance_from_center = (-3.81, 2.54)
    right_pin_for_hotswap_socket_distance_from_center = (2.54, 5.08)

    switch_stabilizing_pin_hole_size = 1
    switch_stabilizing_left_in_hole_distance_from_center = (-5.08, 0)
    switch_stabilizing_right_in_hole_distance_from_center = (5.08, 0)

    result = cq.Workplane()

    result = result.box(key_length, key_width, pcb_thickness)

    switch_middle_pin_hole_cutout = (
        cq.Workplane()
        .circle(switch_middle_pin_hole_size)
        .extrude(pcb_thickness)
        .translate([0, 0, -pcb_thickness / 2])
    )
    result = result.cut(switch_middle_pin_hole_cutout)

    left_switch_stabilizing_pin_hole_cutout = (
        cq.Workplane()
        .circle(switch_stabilizing_pin_hole_size)
        .extrude(pcb_thickness)
        .translate(switch_stabilizing_left_in_hole_distance_from_center)
        .translate([0, 0, -pcb_thickness / 2])
    )
    result = result.cut(left_switch_stabilizing_pin_hole_cutout)

    right_switch_stabilizing_pin_hole_cutout = (
        cq.Workplane()
        .circle(switch_stabilizing_pin_hole_size)
        .extrude(pcb_thickness)
        .translate(switch_stabilizing_right_in_hole_distance_from_center)
        .translate([0, 0, -pcb_thickness / 2])
    )
    result = result.cut(right_switch_stabilizing_pin_hole_cutout)

    left_pin_for_hotswap_socket_cutout = (
        cq.Workplane()
        .circle(pin_for_hotswap_socket_hole_size)
        .extrude(pcb_thickness)
        .translate(left_pin_for_hotswap_socket_distance_from_center)
        .translate([0, 0, -pcb_thickness / 2])
    )
    result = result.cut(left_pin_for_hotswap_socket_cutout)

    right_pin_for_hotswap_socket_cutout = (
        cq.Workplane()
        .circle(pin_for_hotswap_socket_hole_size)
        .extrude(pcb_thickness)
        .translate(right_pin_for_hotswap_socket_distance_from_center)
        .translate([0, 0, -pcb_thickness / 2])
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
        .translate((-6.21, 0.78, -pcb_thickness / 2))
    )

    return result.cut(hotswap_socket_cutout)


def make_plate_key():
    switch_groove_cutout_length = 5
    switch_groove_cutout_width = 1
    switch_groove_cutout_height = 3.5

    switch_cutout_length = 13.9
    switch_cutout_width = 13.9

    result = cq.Workplane()

    result = result.box(key_length, key_width, plate_thickness)

    switch_hole_cutout = cq.Workplane().box(
        switch_cutout_width, switch_cutout_length, plate_thickness
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
                -(plate_thickness - switch_groove_cutout_height) / 2,
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
                -(plate_thickness - switch_groove_cutout_height) / 2,
            ]
        )
    )
    result = result.cut(switch_bottom_groove_cutout)

    return result


def stagger_offset_for_column(x, number_of_columns):
    # Light stagger
    if x == number_of_columns - 4:
        return 0.1 * key_length
    if x == number_of_columns - 3:
        return 0.2 * key_length
    if x == number_of_columns - 2:
        return 0.1 * key_length
    return 0


def key_position(x, y, number_of_columns):
    x_center_of_workplane_offset = key_length / 2
    y_center_of_workplane_offset = key_length / 2

    key_x = x * key_length + x_center_of_workplane_offset
    key_y = (
        y * key_width
        + stagger_offset_for_column(x, number_of_columns)
        + y_center_of_workplane_offset
    )

    return (key_x, key_y, 0)


def center(length, width):
    return (
        -length / 2,
        -width / 2,
        0,
    )


def make_keys(key):
    keys = []

    total_key_width = key_length * number_of_rows
    total_key_length = key_length * number_of_columns

    for x in range(number_of_columns):
        for y in range(number_of_rows):
            keys.append(
                key.translate(key_position(x, y, number_of_columns))
                .translate(center(total_key_length, total_key_width))
                .val()
            )

    keys = keys[0].fuse(*keys[1:], glue=True).clean()

    return cq.Workplane().newObject([keys])


keys_total_length = key_length * number_of_columns

print("")
print(
    "size:",
    number_of_rows,
    "x",
    number_of_columns,
    "(total: " + str(number_of_rows * number_of_columns) + ")",
)

start = time.time()

pcb_key = make_pcb_key()
pcb_keys = make_keys(pcb_key)

plate_key = make_plate_key()
plate_keys = make_keys(plate_key)

start_pbc = time.time()
show_object(pcb_keys.translate([0, 0, -pcb_thickness / 2]))
end_pbc = time.time()
print("pcb:", end_pbc - start_pbc)

start_plate = time.time()
show_object(plate_keys.translate([0, 0, plate_thickness / 2]))
end_plate = time.time()
print("plate:", end_plate - start_plate)

end = time.time()
print("total:", end - start)

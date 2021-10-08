import config
import cadquery as cq
from make_keys import make_keys
from fuse_parts import fuse_parts


def make_pcb_key():
    switch_middle_pin_hole_size = 2

    pin_for_hotswap_socket_hole_size = 1.5
    left_pin_for_hotswap_socket_distance_from_center = (-3.81, 2.54)
    right_pin_for_hotswap_socket_distance_from_center = (2.54, 5.08)

    switch_stabilizing_pin_hole_size = 1
    switch_stabilizing_left_in_hole_distance_from_center = (-5.08, 0)
    switch_stabilizing_right_in_hole_distance_from_center = (5.08, 0)

    result = cq.Workplane()

    result = result.box(config.key_length, config.key_width, config.pcb_thickness)

    switch_middle_pin_hole_cutout = (
        cq.Workplane()
        .circle(switch_middle_pin_hole_size)
        .extrude(config.pcb_thickness)
        .translate([0, 0, -config.pcb_thickness / 2])
    )
    result = result.cut(switch_middle_pin_hole_cutout)

    left_switch_stabilizing_pin_hole_cutout = (
        cq.Workplane()
        .circle(switch_stabilizing_pin_hole_size)
        .extrude(config.pcb_thickness)
        .translate(switch_stabilizing_left_in_hole_distance_from_center)
        .translate([0, 0, -config.pcb_thickness / 2])
    )
    result = result.cut(left_switch_stabilizing_pin_hole_cutout)

    right_switch_stabilizing_pin_hole_cutout = (
        cq.Workplane()
        .circle(switch_stabilizing_pin_hole_size)
        .extrude(config.pcb_thickness)
        .translate(switch_stabilizing_right_in_hole_distance_from_center)
        .translate([0, 0, -config.pcb_thickness / 2])
    )
    result = result.cut(right_switch_stabilizing_pin_hole_cutout)

    left_pin_for_hotswap_socket_cutout = (
        cq.Workplane()
        .circle(pin_for_hotswap_socket_hole_size)
        .extrude(config.pcb_thickness)
        .translate(left_pin_for_hotswap_socket_distance_from_center)
        .translate([0, 0, -config.pcb_thickness / 2])
    )
    result = result.cut(left_pin_for_hotswap_socket_cutout)

    right_pin_for_hotswap_socket_cutout = (
        cq.Workplane()
        .circle(pin_for_hotswap_socket_hole_size)
        .extrude(config.pcb_thickness)
        .translate(right_pin_for_hotswap_socket_distance_from_center)
        .translate([0, 0, -config.pcb_thickness / 2])
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
        .translate((-6.21, 0.78, -config.pcb_thickness / 2))
    )

    return result.cut(hotswap_socket_cutout)


def pcb_keys():
    pcb_key = make_pcb_key()

    pcb_keys_right = make_keys(pcb_key, side_of_board="left")
    pcb_keys_left = make_keys(pcb_key, side_of_board="right")

    if config.angle > 0:
        pcb_keys_right = pcb_keys_right.rotate((0, 0, 0), (0, 0, 1), config.angle)
        pcb_keys_left = pcb_keys_left.rotate((0, 0, 0), (0, 0, 1), -config.angle)

        pcb_tilt_right_side_top_left_corner = (
            pcb_keys_right.vertices("<X").val().Center()
        )
        pcb_tilt_left_side_top_right_corner = (
            pcb_keys_left.vertices(">X").val().Center()
        )

        pcb_keys_right = pcb_keys_right.translate(
            [-pcb_tilt_right_side_top_left_corner.x, 0, 0]
        )
        pcb_keys_left = pcb_keys_left.translate(
            [pcb_tilt_right_side_top_left_corner.x, 0, 0]
        )

        pcb_tilt_right_side_bottom_left_corner = (
            pcb_keys_right.vertices("<Y").val().Center()
        )
        pcb_tilt_right_side_top_left_corner = (
            pcb_keys_right.vertices("<X").val().Center()
        )

        middle_connector = (
            pcb_keys_right.faces("front")
            .workplane()
            .moveTo(
                pcb_tilt_right_side_top_left_corner.x,
                pcb_tilt_right_side_top_left_corner.y,
            )
            .lineTo(
                pcb_tilt_right_side_bottom_left_corner.x,
                pcb_tilt_right_side_bottom_left_corner.y,
            )
            .lineTo(
                -pcb_tilt_right_side_bottom_left_corner.x,
                pcb_tilt_right_side_bottom_left_corner.y,
            )
            .close()
            .extrude(-config.pcb_thickness)
        )

        return fuse_parts([pcb_keys_right, pcb_keys_left, middle_connector])

    return fuse_parts([pcb_keys_right, pcb_keys_left])

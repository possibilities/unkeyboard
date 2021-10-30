import os
import cadquery as cq
from cadquery import exporters
from fuse_parts import fuse_parts
from math import sin, cos, radians, pi
from cq_workplane_plugin import cq_workplane_plugin
from explode_parts import explode_parts
from export_to_dxf_layers import export_to_dxf_layers

# Configurable

thicc_spacer = False
use_chicago_bolt = True
has_two_inner_keys = False

angle = 10
thickness = 3
number_of_columns = 6
number_of_rows = 5

inner_frame_size = 2.1
outer_frame_size = 20 if use_chicago_bolt else 16

# View

explode_by = 12

# Structural

usb_cutout_width = 4
screw_hole_radius = 2.5 if use_chicago_bolt else 1.5
reset_button_hole_radius = 1.5
switch_plate_key_cutout_size = 13.97
distance_between_switch_centers = 19
switch_offset = distance_between_switch_centers / 2
screw_distance_from_inner_edge = (outer_frame_size - inner_frame_size) / 2


def find_point_for_angle(vertice, d, theta):
    theta_rad = pi / 2 - radians(theta)
    return (vertice.x + d * cos(theta_rad), vertice.y + d * sin(theta_rad))


def stagger_percent_for_mm(stagger_mm):
    return stagger_mm / distance_between_switch_centers


inner_keys_stagger = stagger_percent_for_mm(3.98 if has_two_inner_keys else 8.5)
columns_stagger = (
    stagger_percent_for_mm(-1),
    stagger_percent_for_mm(4),
    stagger_percent_for_mm(10),
    stagger_percent_for_mm(5),
    stagger_percent_for_mm(2),
    stagger_percent_for_mm(2),
)


def make_switch_plate_inner():
    switch_plate = cq.Workplane()

    for column in range(number_of_columns):
        for row in range(number_of_rows):
            row_offset = distance_between_switch_centers * row
            column_offset = distance_between_switch_centers * (column + 1)
            stagger_offset = (
                distance_between_switch_centers * columns_stagger[column]
            )
            key_offset_x = switch_offset + column_offset
            key_offset_y = switch_offset + row_offset + stagger_offset
            switch_plate = (
                switch_plate.moveTo(key_offset_x, key_offset_y)
                .rect(
                    distance_between_switch_centers + 1,
                    distance_between_switch_centers + 1,
                )
                .rect(
                    switch_plate_key_cutout_size, switch_plate_key_cutout_size
                )
                .extrude(thickness)
            )

    inner_key_offset_x = switch_offset
    inner_key_offset_y = switch_offset + (
        inner_keys_stagger * distance_between_switch_centers
    )

    widen_cutout_around_key_size = 1
    widen_cutout_around_inner_keys_size = 0 if has_two_inner_keys else 1.5
    inner_keys_unit_height = 1 if has_two_inner_keys else 1.5

    inner_keys_height = (
        distance_between_switch_centers * inner_keys_unit_height
    ) + widen_cutout_around_inner_keys_size

    switch_plate = (
        switch_plate.moveTo(inner_key_offset_x, inner_key_offset_y)
        .rect(switch_plate_key_cutout_size, switch_plate_key_cutout_size)
        .rect(
            distance_between_switch_centers + widen_cutout_around_key_size,
            inner_keys_height,
        )
        .extrude(thickness)
    )

    if has_two_inner_keys:
        switch_plate = (
            switch_plate.moveTo(
                inner_key_offset_x,
                inner_key_offset_y + distance_between_switch_centers,
            )
            .rect(switch_plate_key_cutout_size, switch_plate_key_cutout_size)
            .rect(
                distance_between_switch_centers + widen_cutout_around_key_size,
                inner_keys_height,
            )
            .extrude(thickness)
        )

    switch_plate = switch_plate.rotateAboutCenter([0, 0, 1], angle)

    top_left_off_inner_keys = switch_plate.vertices("<X").val().Center()

    switch_plate = switch_plate.mirror(
        mirrorPlane="YZ",
        union=True,
        basePointVector=(
            top_left_off_inner_keys.x + (widen_cutout_around_key_size / 2),
            top_left_off_inner_keys.y,
        ),
    )

    return switch_plate


@cq_workplane_plugin
def drill_reset_button_hole(part, switch_plate_inner):
    return (
        part.faces("front")
        .moveTo(-24, 41)
        .circle(reset_button_hole_radius)
        .cutThruAll()
    )


@cq_workplane_plugin
def drill_holes(part, switch_plate_inner):
    outline = switch_plate_inner.faces("front").wires(
        cq.selectors.AreaNthSelector(-1)
    )

    top_left_outline = outline.edges("<X").vertices(">Y").val().Center()
    top_right_outline = outline.vertices(">XY").val().Center()
    right_outline = outline.vertices(">X").vertices("<Y").val().Center()
    left_outline = outline.vertices("<X").vertices("<Y").val().Center()
    bottom_right_outline = outline.vertices("<Y").vertices(">X").val().Center()
    bottom_left_outline = outline.vertices("<Y").vertices("<X").val().Center()

    return (
        part.faces("front")
        .moveTo(
            *find_point_for_angle(
                top_right_outline, screw_distance_from_inner_edge, 45 - angle
            )
        )
        .circle(screw_hole_radius)
        .cutThruAll()
        .moveTo(
            *find_point_for_angle(
                right_outline, -screw_distance_from_inner_edge, -45 - angle
            )
        )
        .circle(screw_hole_radius)
        .cutThruAll()
        .moveTo(
            *find_point_for_angle(
                bottom_right_outline,
                -screw_distance_from_inner_edge,
                45 - angle,
            )
        )
        .circle(screw_hole_radius)
        .cutThruAll()
        .moveTo(
            *find_point_for_angle(
                bottom_left_outline,
                -screw_distance_from_inner_edge,
                -45 + angle,
            )
        )
        .circle(screw_hole_radius)
        .cutThruAll()
        .moveTo(
            *find_point_for_angle(
                left_outline, -screw_distance_from_inner_edge, 45 + angle
            )
        )
        .circle(screw_hole_radius)
        .cutThruAll()
        .moveTo(
            *find_point_for_angle(
                top_left_outline, screw_distance_from_inner_edge, -45 + angle
            ),
        )
        .circle(screw_hole_radius)
        .cutThruAll()
        .moveTo(
            -11.25,
            find_point_for_angle(
                top_left_outline, screw_distance_from_inner_edge, -45 + angle
            )[1],
        )
        .circle(screw_hole_radius)
        .cutThruAll()
        .moveTo(
            11.25,
            find_point_for_angle(
                top_left_outline, screw_distance_from_inner_edge, -45 + angle
            )[1],
        )
        .circle(screw_hole_radius)
        .cutThruAll()
    )


def make_bottom_plate(switch_plate_inner, thickness):
    outline = switch_plate_inner.faces("front").wires(
        cq.selectors.AreaNthSelector(-1)
    )
    top_right_outline = outline.vertices(">XY").val().Center()
    right_outline = outline.vertices(">X").vertices("<Y").val().Center()
    bottom_right_outline = outline.vertices("<Y").vertices(">X").val().Center()

    return (
        cq.Workplane()
        .newObject([])
        .moveTo(
            0,
            find_point_for_angle(
                top_right_outline, outer_frame_size, 45 - angle
            )[1],
        )
        .lineTo(
            *find_point_for_angle(
                top_right_outline, outer_frame_size, 45 - angle
            )
        )
        .lineTo(
            *find_point_for_angle(right_outline, -outer_frame_size, -45 - angle)
        )
        .lineTo(
            *find_point_for_angle(
                bottom_right_outline, -outer_frame_size, 45 - angle
            )
        )
        .lineTo(
            0,
            find_point_for_angle(
                bottom_right_outline, -outer_frame_size, 45 - angle
            )[1],
        )
        .close()
        .extrude(-thickness, combine=False)
        .mirror(mirrorPlane="YZ", union=True)
    )


def make_top_plate(switch_plate_inner):
    outline = switch_plate_inner.faces("front").wires(
        cq.selectors.AreaNthSelector(-1)
    )

    return (
        make_bottom_plate(switch_plate_inner, thickness)
        .cut(
            outline.toPending()
            .extrude(-thickness, combine=False)
            .translate([0, 0, -thickness])
        )
        .translate([0, 0, thickness / 2])
    )


def make_switch_plate(switch_plate_inner):
    switch_plate_uncut = make_bottom_plate(switch_plate_inner, thickness)
    outline = switch_plate_inner.faces("front").wires(
        cq.selectors.AreaNthSelector(-1)
    )

    switch_plate_outer = switch_plate_uncut.cut(
        outline.toPending()
        .extrude(-thickness, combine=False)
        .translate([0, 0, -thickness])
    ).translate([0, 0, thickness / 2])

    return switch_plate_inner.translate([0, 0, -thickness / 2]).union(
        switch_plate_outer
    )


def make_spacer(switch_plate_inner, thickness):
    outline = switch_plate_inner.faces("front").wires(
        cq.selectors.AreaNthSelector(-1)
    )

    top_left_outline = outline.edges("<X").vertices(">Y").val().Center()
    top_right_outline = outline.vertices(">XY").val().Center()
    right_outline = outline.vertices(">X").vertices("<Y").val().Center()
    left_outline = outline.vertices("<X").vertices("<Y").val().Center()
    bottom_right_outline = outline.vertices("<Y").vertices(">X").val().Center()
    bottom_left_outline = outline.vertices("<Y").vertices("<X").val().Center()

    return (
        make_bottom_plate(switch_plate_inner, thickness)
        .moveTo(
            *find_point_for_angle(
                top_right_outline, -inner_frame_size, 45 - angle
            )
        )
        .lineTo(
            *find_point_for_angle(right_outline, inner_frame_size, -45 - angle)
        )
        .lineTo(
            *find_point_for_angle(
                bottom_right_outline,
                inner_frame_size,
                45 - angle,
            )
        )
        .lineTo(
            *find_point_for_angle(
                bottom_left_outline,
                inner_frame_size,
                -45 + angle,
            )
        )
        .lineTo(
            *find_point_for_angle(left_outline, inner_frame_size, 45 + angle)
        )
        .lineTo(
            *find_point_for_angle(
                top_left_outline, -inner_frame_size, -45 + angle
            ),
        )
        .close()
        .cutThruAll()
        .moveTo(
            0,
            find_point_for_angle(
                top_right_outline,
                outer_frame_size,
                45 - angle,
            )[1]
            - outer_frame_size / 2,
        )
        .rect(usb_cutout_width, outer_frame_size)
        .cutBlind(-thickness)
    ).translate([0, 0, thickness / 2])


def make_keyboard_parts():
    parts = []

    switch_plate_inner = make_switch_plate_inner()

    top_plate = make_top_plate(switch_plate_inner).drill_holes(
        switch_plate_inner
    )
    parts.append(("Top plate", top_plate))

    switch_plate = make_switch_plate(switch_plate_inner).drill_holes(
        switch_plate_inner
    )
    parts.append(("Switch plate", switch_plate))

    spacer_thickness = thickness * 2 if thicc_spacer else thickness
    spacer = make_spacer(switch_plate_inner, spacer_thickness).drill_holes(
        switch_plate_inner
    )
    if thicc_spacer:
        parts.append(("Spacer", spacer))
    else:
        parts.append(("Spacer 1", spacer))
        parts.append(("Spacer 2", spacer))

    bottom_plate = (
        make_bottom_plate(switch_plate_inner, thickness)
        .drill_holes(switch_plate_inner)
        .drill_reset_button_hole(switch_plate_inner)
        # TODO move this adjustment into make_bottom_plate
        .translate([0, 0, thickness / 2])
    )
    parts.append(("Bottom plate", bottom_plate))

    return parts


keyboard_parts = make_keyboard_parts()

if os.environ.get("EXPORT"):
    export_to_dxf_layers(keyboard_parts, "./data/keyboard.dxf")
else:
    for layer_name_and_part in explode_parts(keyboard_parts, explode_by):
        [layer_name, part] = layer_name_and_part
        show_object(part, name=layer_name)

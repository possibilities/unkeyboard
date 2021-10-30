import os
import cadquery as cq
from cadquery import exporters
from math import sin, cos, radians, pi
from cq_workplane_plugin import cq_workplane_plugin
from export_to_dxf_layers import export_to_dxf_layers

thicc_spacer = False
use_chicago_bolt = True

angle = 10
thickness = 3
number_of_columns = 6
number_of_rows = 5
usb_cutout_width = 4

outer_frame_size = 20 if use_chicago_bolt else 16
inner_frame_size = 2.1

screw_hole_radius = 2.5 if use_chicago_bolt else 1.5
reset_button_hole_radius = 1.5
switch_plate_key_cutout_size = 13.97
distance_between_switch_centers = 19
switch_offset = distance_between_switch_centers / 2

screw_distance_from_inner_edge = (outer_frame_size - inner_frame_size) / 2


def find_point_for_angle(vertice, d, theta):
    theta_rad = pi / 2 - radians(theta)
    return (vertice.x + d * cos(theta_rad), vertice.y + d * sin(theta_rad))


@cq_workplane_plugin
def center_on_plane(part):
    top = part.vertices(">Y").val().Center()
    left = part.vertices("<X").val().Center()
    right = part.vertices(">X").val().Center()
    bottom = part.vertices("<Y").val().Center()
    height = top.y - bottom.y
    width = left.x - right.x
    return part.translate([-left.x + (width / 2), -top.y + (height / 2), 0])


def stagger_percent_for_mm(stagger_mm):
    return stagger_mm / distance_between_switch_centers


thumb_stagger = stagger_percent_for_mm(8.5)
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
            offset_x = switch_offset + column_offset
            offset_y = switch_offset + row_offset + stagger_offset
            switch_plate = (
                switch_plate.moveTo(offset_x, offset_y)
                .rect(
                    distance_between_switch_centers + 1,
                    distance_between_switch_centers + 1,
                )
                .rect(
                    switch_plate_key_cutout_size, switch_plate_key_cutout_size
                )
                .extrude(thickness)
            )

    offset_x = switch_offset
    offset_y = switch_offset + (thumb_stagger * distance_between_switch_centers)

    widen_cutout_around_key = 1
    widen_cutout_around_thumb_key = 1.5
    unit_height_of_thumb_key = 1.5

    thumb_key_height = (
        distance_between_switch_centers * unit_height_of_thumb_key
    ) + widen_cutout_around_thumb_key

    switch_plate = (
        switch_plate.moveTo(offset_x, offset_y)
        .rect(switch_plate_key_cutout_size, switch_plate_key_cutout_size)
        .moveTo(offset_x, offset_y)
        .rect(
            distance_between_switch_centers + widen_cutout_around_key,
            thumb_key_height,
        )
        .extrude(thickness)
    )

    switch_plate = switch_plate.rotateAboutCenter([0, 0, 1], angle)

    top_left_of_thumb_key = switch_plate.vertices("<X").val().Center()

    switch_plate = switch_plate.mirror(
        mirrorPlane="YZ",
        union=True,
        basePointVector=(
            top_left_of_thumb_key.x + (widen_cutout_around_key / 2),
            top_left_of_thumb_key.y,
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
    )


switch_plate_inner = make_switch_plate_inner().center_on_plane()

top_plate = make_top_plate(switch_plate_inner).drill_holes(switch_plate_inner)
switch_plate = make_switch_plate(switch_plate_inner).drill_holes(
    switch_plate_inner
)

spacer_thickness = thickness * 2 if thicc_spacer else thickness
spacer = make_spacer(switch_plate_inner, spacer_thickness).drill_holes(
    switch_plate_inner
)

bottom_plate = (
    make_bottom_plate(switch_plate_inner, thickness)
    .drill_holes(switch_plate_inner)
    .drill_reset_button_hole(switch_plate_inner)
)

if not os.environ.get("FORMAT"):
    show_object(top_plate.translate([0, 0, 23]), name="top_plate")
    show_object(switch_plate.translate([0, 0, 0]), name="switch_plate")
    if thicc_spacer:
        show_object(spacer.translate([0, 0, -20]), name="spacer")
        show_object(
            bottom_plate.translate([0, 0, -46 if thicc_spacer else -60]),
            name="bottom_plate",
        )
    else:
        show_object(spacer.translate([0, 0, -20]), name="spacer_1")
        show_object(spacer.translate([0, 0, -40]), name="spacer_2")
        show_object(
            bottom_plate.translate([0, 0, -60 if thicc_spacer else -60]),
            name="bottom_plate",
        )

if os.environ.get("FORMAT"):
    try:
        os.mkdir("./data")
    except:
        pass

    if os.environ.get("FORMAT") == "STL":
        exporters.export(top_plate, "./data/top_plate.stl")
        exporters.export(switch_plate, "./data/switch_plate.stl")
        exporters.export(spacer, "./data/spacer_1.stl")
        if not thicc_spacer:
            exporters.export(spacer, "./data/spacer_2.stl")
        exporters.export(bottom_plate, "./data/bottom_plate.stl")

    if os.environ.get("FORMAT") == "DXF":
        if thicc_spacer:
            export_to_dxf_layers(
                [
                    ("Top plate", top_plate, 3),
                    ("Switch plate", switch_plate, 3),
                    ("Spacer 1", spacer, 3),
                    ("Spacer 2", spacer, 3),
                    ("Bottom plate", bottom_plate, 3),
                ],
                "./data/layered.dxf",
            )
        else:
            export_to_dxf_layers(
                [
                    ("Top plate", top_plate, 3),
                    ("Switch plate", switch_plate, 3),
                    ("Spacer", spacer, 6),
                    ("Bottom plate", bottom_plate, 3),
                ],
                "./data/layered.dxf",
            )
        export_to_dxf_layers(
            [("Top plate", top_plate, 3)], "./data/top-plate.dxf"
        )
        export_to_dxf_layers(
            [("Switch plate", switch_plate, 3)], "./data/switch-plate.dxf"
        )
        if thicc_spacer:
            export_to_dxf_layers(
                [("Thicc spacer", spacer, 6)], "./data/switch-plate.dxf"
            )
        else:
            export_to_dxf_layers(
                [("Spacer 1", spacer, 3)], "./data/spacer-1.dxf"
            )
            export_to_dxf_layers(
                [("Spacer 2", spacer, 3)], "./data/spacer-2.dxf"
            )
        export_to_dxf_layers(
            [("Bottom plate", bottom_plate, 3)], "./data/bottom-plate.dxf"
        )

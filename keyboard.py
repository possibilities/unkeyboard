import math
import cadquery as cq
from timer import timer
from fuse_parts import fuse_parts
from cq_workplane_plugin import cq_workplane_plugin
from explode_parts import explode_parts

# Configurable

thicc_spacer = False
use_chicago_bolt = True
has_two_inner_keys = False

angle = 10
number_of_rows = 5
number_of_columns = 6

# View

explode_by = 12
flatten = False

# Structural

thickness = 3

outer_frame_size_for_chicago_bolt = 20
outer_frame_size_for_regular_screw = 16

screw_hole_radius_for_chicago_bolt = 2.5
screw_hole_radius_for_regular_screw = 1.5

usb_cutout_width = 4
reset_button_hole_radius = 1.5
switch_plate_key_cutout_size = 13.97
distance_between_switch_centers = 19
switch_offset = distance_between_switch_centers / 2
inner_frame_size = 2.1

screw_hole_radius = (
    screw_hole_radius_for_chicago_bolt
    if use_chicago_bolt
    else screw_hole_radius_for_regular_screw
)

outer_frame_size = (
    outer_frame_size_for_chicago_bolt
    if use_chicago_bolt
    else outer_frame_size_for_regular_screw
)


def find_point_for_angle(vertice, d, theta):
    theta_rad = math.pi / 2 - math.radians(theta)
    return (
        vertice.x + d * math.cos(theta_rad),
        vertice.y + d * math.sin(theta_rad),
    )


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
def drill_reset_button_hole(part):
    return (
        part.faces("front")
        .moveTo(-24, 41)
        .circle(reset_button_hole_radius)
        .cutThruAll()
    )


@cq_workplane_plugin
def drill_holes(part, switch_plate_inner):
    switch_plate_outline = switch_plate_inner.faces("front").wires(
        cq.selectors.AreaNthSelector(-1)
    )

    top_left_outline = (
        switch_plate_outline.edges("<X").vertices(">Y").val().Center()
    )
    top_right_outline = switch_plate_outline.vertices(">XY").val().Center()
    right_outline = (
        switch_plate_outline.vertices(">X").vertices("<Y").val().Center()
    )
    left_outline = (
        switch_plate_outline.vertices("<X").vertices("<Y").val().Center()
    )
    bottom_right_outline = (
        switch_plate_outline.vertices("<Y").vertices(">X").val().Center()
    )
    bottom_left_outline = (
        switch_plate_outline.vertices("<Y").vertices("<X").val().Center()
    )

    screw_distance_from_inner_edge = (outer_frame_size - inner_frame_size) / 2

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
    switch_plate_outline = switch_plate_inner.faces("front").wires(
        cq.selectors.AreaNthSelector(-1)
    )
    top_right_outline = switch_plate_outline.vertices(">XY").val().Center()
    right_outline = (
        switch_plate_outline.vertices(">X").vertices("<Y").val().Center()
    )
    bottom_right_outline = (
        switch_plate_outline.vertices("<Y").vertices(">X").val().Center()
    )

    bottom_plate = (
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

    return bottom_plate.drill_holes(
        switch_plate_inner
    ).drill_reset_button_hole()


def make_top_plate(switch_plate_inner):
    switch_plate_outline = switch_plate_inner.faces("front").wires(
        cq.selectors.AreaNthSelector(-1)
    )

    top_plate = make_bottom_plate(switch_plate_inner, thickness).cut(
        switch_plate_outline.toPending()
        .extrude(-thickness, combine=False)
        .translate([0, 0, -thickness])
    )

    return top_plate.drill_holes(switch_plate_inner)


def make_switch_plate(switch_plate_inner):
    switch_plate_uncut = make_bottom_plate(switch_plate_inner, thickness)
    switch_plate_outline = switch_plate_inner.faces("front").wires(
        cq.selectors.AreaNthSelector(-1)
    )

    switch_plate_outer = switch_plate_uncut.cut(
        switch_plate_outline.toPending()
        .extrude(-thickness, combine=False)
        .translate([0, 0, -thickness])
    )

    return fuse_parts(
        [switch_plate_outer, switch_plate_inner.translate([0, 0, -thickness])]
    )


def make_spacer(switch_plate_inner, thickness):
    switch_plate_outline = switch_plate_inner.faces("front").wires(
        cq.selectors.AreaNthSelector(-1)
    )

    top_left_outline = (
        switch_plate_outline.edges("<X").vertices(">Y").val().Center()
    )
    top_right_outline = switch_plate_outline.vertices(">XY").val().Center()
    right_outline = (
        switch_plate_outline.vertices(">X").vertices("<Y").val().Center()
    )
    left_outline = (
        switch_plate_outline.vertices("<X").vertices("<Y").val().Center()
    )
    bottom_right_outline = (
        switch_plate_outline.vertices("<Y").vertices(">X").val().Center()
    )
    bottom_left_outline = (
        switch_plate_outline.vertices("<Y").vertices("<X").val().Center()
    )

    spacer = (
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
                bottom_right_outline, inner_frame_size, 45 - angle
            )
        )
        .lineTo(
            *find_point_for_angle(
                bottom_left_outline, inner_frame_size, -45 + angle
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
                top_right_outline, outer_frame_size, 45 - angle
            )[1]
            - outer_frame_size / 2,
        )
        .rect(usb_cutout_width, outer_frame_size)
        .cutBlind(-thickness)
    )

    return spacer.drill_holes(switch_plate_inner)


def make_keyboard_parts():
    parts = []

    print("")
    print(
        "Size:",
        number_of_rows,
        "x",
        number_of_columns,
        "(total: " + str(number_of_rows * number_of_columns) + ")",
    )

    [time_elapsed, total_time] = timer()

    switch_plate_inner = make_switch_plate_inner().center_on_plane()
    time_elapsed("Inner switch plate")

    parts.append(("Top plate", make_top_plate(switch_plate_inner)))
    time_elapsed("Top plate")

    parts.append(("Switch plate", make_switch_plate(switch_plate_inner)))
    time_elapsed("Switch plate")

    if thicc_spacer:
        parts.append(("Spacer", make_spacer(switch_plate_inner, thickness * 2)))
        time_elapsed("Spacer")
    else:
        parts.append(("Spacer 1", make_spacer(switch_plate_inner, thickness)))
        parts.append(("Spacer 2", make_spacer(switch_plate_inner, thickness)))
        time_elapsed("Spacers")

    parts.append(
        ("Bottom plate", make_bottom_plate(switch_plate_inner, thickness))
    )
    time_elapsed("Bottom plate")

    total_time()

    return parts


if "show_object" in globals():
    keyboard_parts = make_keyboard_parts()
    if not flatten:
        keyboard_parts = explode_parts(keyboard_parts, explode_by)

    for layer_name_and_part in keyboard_parts:
        [layer_name, part] = layer_name_and_part
        show_object(part, name=layer_name)

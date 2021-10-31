from pprint import pprint
import math
import cadquery as cq
from timer import timer
from fuse_parts import fuse_parts
from cq_workplane_plugin import cq_workplane_plugin
from explode_parts import explode_parts
from types import SimpleNamespace

# Configurable

has_single_thicc_spacer = False
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
top_inside_screw_distance_from_usb = 11.25

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


def coords_from_vertice(vertice):
    return (vertice.x, vertice.y)


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


@cq_workplane_plugin
def drill_holes(part, geometry):
    return (
        part.pushPoints(geometry.screws)
        .circle(screw_hole_radius)
        .cutBlind(-geometry.thickness)
    )


@cq_workplane_plugin
def drill_reset_button_hole(part, geometry):
    return (
        part.pushPoints([geometry.reset_button])
        .circle(reset_button_hole_radius)
        .cutBlind(-geometry.thickness)
    )


def calculate_coords_from_switch_plate_inner(switch_plate_inner):
    switch_plate_outline = switch_plate_inner.faces("front").wires(
        cq.selectors.AreaNthSelector(-1)
    )

    inner_plate_top_left = (
        switch_plate_outline.edges("<X").vertices(">Y").val().Center()
    )
    inner_plate_top_right = switch_plate_outline.vertices(">XY").val().Center()
    inner_plate_left = (
        switch_plate_outline.vertices("<X").vertices("<Y").val().Center()
    )
    inner_plate_right = (
        switch_plate_outline.vertices(">X").vertices("<Y").val().Center()
    )
    inner_plate_bottom_left = (
        switch_plate_outline.vertices("<Y").vertices("<X").val().Center()
    )
    inner_plate_bottom_right = (
        switch_plate_outline.vertices("<Y").vertices(">X").val().Center()
    )

    case_outer_top_right = find_point_for_angle(
        inner_plate_top_right, outer_frame_size, 45 - angle
    )
    case_outer_right = find_point_for_angle(
        inner_plate_right, -outer_frame_size, -45 - angle
    )
    case_outer_bottom_right = find_point_for_angle(
        inner_plate_bottom_right, -outer_frame_size, 45 - angle
    )
    case_outer_bottom_left = find_point_for_angle(
        inner_plate_bottom_left, -outer_frame_size, -45 + angle
    )
    case_outer_left = find_point_for_angle(
        inner_plate_left, -outer_frame_size, 45 + angle
    )
    case_outer_top_left = find_point_for_angle(
        inner_plate_top_left, outer_frame_size, -45 + angle
    )

    case_outer_points = [
        case_outer_top_left,
        case_outer_top_right,
        case_outer_right,
        case_outer_bottom_right,
        case_outer_bottom_left,
        case_outer_left,
    ]

    screw_distance_from_inner_edge = (outer_frame_size - inner_frame_size) / 2

    screw_top_left = find_point_for_angle(
        inner_plate_top_left, screw_distance_from_inner_edge, -45 + angle
    )
    screw_top_right = find_point_for_angle(
        inner_plate_top_right, screw_distance_from_inner_edge, 45 - angle
    )
    screw_top_middle_left = (
        -top_inside_screw_distance_from_usb,
        find_point_for_angle(
            inner_plate_top_left, screw_distance_from_inner_edge, -45 + angle
        )[1],
    )
    screw_top_middle_right = (
        top_inside_screw_distance_from_usb,
        find_point_for_angle(
            inner_plate_top_right, screw_distance_from_inner_edge, 45 - angle
        )[1],
    )
    screw_bottom_middle_left = find_point_for_angle(
        inner_plate_bottom_left, -screw_distance_from_inner_edge, 45 - angle
    )
    screw_bottom_middle_right = find_point_for_angle(
        inner_plate_bottom_right, -screw_distance_from_inner_edge, -45 + angle
    )
    screw_bottom_left = find_point_for_angle(
        inner_plate_left, -screw_distance_from_inner_edge, 45 - angle
    )
    screw_bottom_right = find_point_for_angle(
        inner_plate_right, -screw_distance_from_inner_edge, -45 + angle
    )

    screw_points = [
        screw_top_left,
        screw_top_right,
        screw_top_middle_left,
        screw_top_middle_right,
        screw_bottom_right,
        screw_bottom_left,
        screw_bottom_middle_right,
        screw_bottom_middle_left,
    ]

    spacer_inner_top_left = find_point_for_angle(
        inner_plate_top_left, -inner_frame_size, -45 + angle
    )
    spacer_inner_top_right = find_point_for_angle(
        inner_plate_top_right, -inner_frame_size, 45 - angle
    )
    spacer_inner_right = find_point_for_angle(
        inner_plate_right, inner_frame_size, -45 - angle
    )
    spacer_inner_bottom_right = find_point_for_angle(
        inner_plate_bottom_right, inner_frame_size, 45 - angle
    )
    spacer_inner_bottom_left = find_point_for_angle(
        inner_plate_bottom_left, inner_frame_size, -45 + angle
    )
    spacer_inner_left = find_point_for_angle(
        inner_plate_left, inner_frame_size, 45 + angle
    )

    spacer_inner_points = [
        spacer_inner_top_left,
        spacer_inner_top_right,
        spacer_inner_right,
        spacer_inner_bottom_right,
        spacer_inner_bottom_left,
        spacer_inner_left,
    ]

    reset_button_point = (-24, 41)

    usb_rect_points = [
        (usb_cutout_width / 2, case_outer_top_left[1]),
        (usb_cutout_width / 2, spacer_inner_top_left[1]),
        (-usb_cutout_width / 2, spacer_inner_top_left[1]),
        (-usb_cutout_width / 2, case_outer_top_left[1]),
    ]

    spacer_thickness = thickness * 2 if has_single_thicc_spacer else thickness

    geometry_points = SimpleNamespace(
        **{
            "thickness": thickness,
            "usb_rect": usb_rect_points,
            "screws": screw_points,
            "reset_button": reset_button_point,
            "case_outer": case_outer_points,
            "spacer_inner": spacer_inner_points,
            "spacer_thickness": spacer_thickness,
            "switch_plate_inner_outline": switch_plate_outline,
        }
    )

    return geometry_points


def make_switch_plate_inner(thickness):
    switch_plate = cq.Workplane()

    widen_cutout_around_key_size = 1

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
                    distance_between_switch_centers
                    + widen_cutout_around_key_size,
                    distance_between_switch_centers
                    + widen_cutout_around_key_size,
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

    inner_keys_top_left = switch_plate.vertices("<X").val().Center()

    return switch_plate.mirror(
        mirrorPlane="YZ",
        union=True,
        basePointVector=(
            inner_keys_top_left.x + (widen_cutout_around_key_size / 2),
            inner_keys_top_left.y,
        ),
    )


def make_bottom_plate(geometry):
    return (
        cq.Workplane()
        .polyline(geometry.case_outer)
        .close()
        .extrude(-geometry.thickness)
        .drill_holes(geometry)
        .drill_reset_button_hole(geometry)
    )


def make_top_plate(geometry):
    switch_plate_cutout = (
        geometry.switch_plate_inner_outline.toPending().extrude(
            -geometry.thickness
        )
    )
    return (
        cq.Workplane()
        .polyline(geometry.case_outer)
        .close()
        .extrude(-geometry.thickness)
        .translate([0, 0, geometry.thickness])
        .cut(switch_plate_cutout)
        .translate([0, 0, -geometry.thickness])
        .drill_holes(geometry)
    )


def make_switch_plate(switch_plate_inner, geometry):
    switch_plate_cutout = (
        geometry.switch_plate_inner_outline.toPending().extrude(
            -geometry.thickness
        )
    )
    switch_plate_outer = (
        cq.Workplane()
        .polyline(geometry.case_outer)
        .close()
        .extrude(-geometry.thickness)
        .translate([0, 0, geometry.thickness])
        .cut(switch_plate_cutout)
        .translate([0, 0, -geometry.thickness])
        .drill_holes(geometry)
    )
    switch_plate_inner = switch_plate_inner.translate(
        [0, 0, -geometry.thickness]
    )
    return fuse_parts([switch_plate_outer, switch_plate_inner])


def make_spacer(geometry):
    return (
        cq.Workplane()
        .polyline(geometry.spacer_inner)
        .close()
        .polyline(geometry.case_outer)
        .close()
        .extrude(geometry.spacer_thickness)
        .polyline(geometry.usb_rect)
        .close()
        .cutBlind(geometry.spacer_thickness)
        .translate([0, 0, -geometry.spacer_thickness])
        .drill_holes(geometry)
    )


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

    switch_plate_inner = make_switch_plate_inner(thickness).center_on_plane()
    time_elapsed("Inner switch plate")

    geometry = calculate_coords_from_switch_plate_inner(switch_plate_inner)

    parts.append(("Top plate", make_top_plate(geometry)))
    time_elapsed("Top plate")

    parts.append(
        ("Switch plate", make_switch_plate(switch_plate_inner, geometry))
    )
    time_elapsed("Switch plate")

    if has_single_thicc_spacer:
        parts.append(("Spacer", make_spacer(geometry)))
        time_elapsed("Spacer")
    else:
        parts.append(("Spacer 1", make_spacer(geometry)))
        parts.append(("Spacer 2", make_spacer(geometry)))
        time_elapsed("Spacers")

    parts.append(("Bottom plate", make_bottom_plate(geometry)))
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

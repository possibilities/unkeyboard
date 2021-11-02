import math
import cadquery as cq
from timer import timer
from fuse_parts import fuse_parts
from cq_workplane_plugin import cq_workplane_plugin
from explode_parts import explode_parts
from types import SimpleNamespace

# Defaults to an Atreus 64, with a wide bezel, and chicago bolts
default_config = SimpleNamespace(
    **{
        # Configurable
        "has_thicc_spacer": False,
        "use_chicago_bolt": True,
        "has_double_inner_keys": False,
        "angle": 10,
        "number_of_rows": 5,
        "number_of_columns": 6,
        "stagger_percent_for_single_inner_key": 8.5,
        "stagger_percent_for_double_inner_keys": 3.98,
        "column_stagger_percents": (-1, 4, 10, 5, 2, 2),
        # Structural
        "base_layer_thickness": 3,
        "inner_frame_size": 2.1,
        "outer_frame_size_for_chicago_bolt": 20,
        "outer_frame_size_for_regular_screw": 16,
        "screw_hole_radius_for_chicago_bolt": 2.5,
        "screw_hole_radius_for_regular_screw": 1.5,
        "reset_button_hole_radius": 1.5,
        "switch_plate_key_cutout_size": 13.97,
        "distance_between_switch_centers": 19,
        "usb_cutout_width": 4,
        "top_inside_screw_distance_from_usb": 11.25,
    }
)

view_config = SimpleNamespace(
    **{
        "explode_by": 12,
        "flatten": False,
    }
)


def find_midpoint_between_two_points(vertice_1, vertice_2):
    return ((vertice_1.x + vertice_2.x) / 2, (vertice_1.y + vertice_2.y) / 2)


def find_point_for_angle(vertice, distance, angel):
    angle_radian = math.pi / 2 - math.radians(angel)
    return (
        vertice.x + distance * math.cos(angle_radian),
        vertice.y + distance * math.sin(angle_radian),
    )


@cq_workplane_plugin
def center_on_2d_plane(part):
    top = part.vertices(">Y").val().Center()
    left = part.vertices("<X").val().Center()
    right = part.vertices(">X").val().Center()
    bottom = part.vertices("<Y").val().Center()
    height = top.y - bottom.y
    width = left.x - right.x
    return part.translate([-left.x + (width / 2), -top.y + (height / 2), 0])


@cq_workplane_plugin
def drill_holes(part, geometry, config):
    screw_hole_radius = (
        config.screw_hole_radius_for_chicago_bolt
        if config.use_chicago_bolt
        else config.screw_hole_radius_for_regular_screw
    )
    return (
        part.pushPoints(geometry.screws)
        .circle(screw_hole_radius)
        .cutBlind(-geometry.thickness)
    )


@cq_workplane_plugin
def drill_reset_button_hole(part, geometry, config):
    return (
        part.pushPoints([geometry.reset_button])
        .circle(config.reset_button_hole_radius)
        .cutBlind(-geometry.thickness)
    )


def calculate_geometry_from_switch_plate_inner(switch_plate_inner, config):
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

    outer_frame_size = (
        config.outer_frame_size_for_chicago_bolt
        if config.use_chicago_bolt
        else config.outer_frame_size_for_regular_screw
    )

    case_outer_top_right = find_point_for_angle(
        inner_plate_top_right, outer_frame_size, 45 - config.angle
    )
    case_outer_right = find_point_for_angle(
        inner_plate_right, -outer_frame_size, -45 - config.angle
    )
    case_outer_bottom_right = find_point_for_angle(
        inner_plate_bottom_right, -outer_frame_size, 45 - config.angle
    )
    case_outer_bottom_left = find_point_for_angle(
        inner_plate_bottom_left, -outer_frame_size, -45 + config.angle
    )
    case_outer_left = find_point_for_angle(
        inner_plate_left, -outer_frame_size, 45 + config.angle
    )
    case_outer_top_left = find_point_for_angle(
        inner_plate_top_left, outer_frame_size, -45 + config.angle
    )

    case_outer_points = [
        case_outer_top_left,
        case_outer_top_right,
        case_outer_right,
        case_outer_bottom_right,
        case_outer_bottom_left,
        case_outer_left,
    ]

    screw_distance_from_inner_edge = (
        outer_frame_size - config.inner_frame_size
    ) / 2

    screw_top_left = find_point_for_angle(
        inner_plate_top_left,
        screw_distance_from_inner_edge,
        -45 + config.angle,
    )
    screw_top_right = find_point_for_angle(
        inner_plate_top_right,
        screw_distance_from_inner_edge,
        45 - config.angle,
    )
    screw_top_middle_left = (
        -config.top_inside_screw_distance_from_usb,
        find_point_for_angle(
            inner_plate_top_left,
            screw_distance_from_inner_edge,
            -45 + config.angle,
        )[1],
    )
    screw_top_middle_right = (
        config.top_inside_screw_distance_from_usb,
        find_point_for_angle(
            inner_plate_top_right,
            screw_distance_from_inner_edge,
            45 - config.angle,
        )[1],
    )
    screw_bottom_middle_left = find_point_for_angle(
        inner_plate_bottom_left,
        -screw_distance_from_inner_edge,
        45 - config.angle,
    )
    screw_bottom_middle_right = find_point_for_angle(
        inner_plate_bottom_right,
        -screw_distance_from_inner_edge,
        -45 + config.angle,
    )
    screw_bottom_left = find_point_for_angle(
        inner_plate_left,
        -screw_distance_from_inner_edge,
        45 - config.angle,
    )
    screw_bottom_right = find_point_for_angle(
        inner_plate_right,
        -screw_distance_from_inner_edge,
        -45 + config.angle,
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
        inner_plate_top_left,
        -config.inner_frame_size,
        -45 + config.angle,
    )
    spacer_inner_top_right = find_point_for_angle(
        inner_plate_top_right,
        -config.inner_frame_size,
        45 - config.angle,
    )
    spacer_inner_right = find_point_for_angle(
        inner_plate_right,
        config.inner_frame_size,
        -45 - config.angle,
    )
    spacer_inner_bottom_right = find_point_for_angle(
        inner_plate_bottom_right,
        config.inner_frame_size,
        45 - config.angle,
    )
    spacer_inner_bottom_left = find_point_for_angle(
        inner_plate_bottom_left,
        config.inner_frame_size,
        -45 + config.angle,
    )
    spacer_inner_left = find_point_for_angle(
        inner_plate_left,
        config.inner_frame_size,
        45 + config.angle,
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
        (config.usb_cutout_width / 2, case_outer_top_left[1]),
        (config.usb_cutout_width / 2, spacer_inner_top_left[1]),
        (-config.usb_cutout_width / 2, spacer_inner_top_left[1]),
        (-config.usb_cutout_width / 2, case_outer_top_left[1]),
    ]

    spacer_thickness = (
        config.base_layer_thickness * 2
        if config.has_thicc_spacer
        else config.base_layer_thickness
    )

    geometry_points = SimpleNamespace(
        **{
            "usb_rect": usb_rect_points,
            "screws": screw_points,
            "reset_button": reset_button_point,
            "case_outer": case_outer_points,
            "spacer_inner": spacer_inner_points,
            "spacer_thickness": spacer_thickness,
            "thickness": config.base_layer_thickness,
            "switch_plate_inner_outline": switch_plate_outline,
        }
    )

    return geometry_points


def make_switch_plate_inner(config):
    switch_plate = cq.Workplane()

    widen_cutout_around_key_size = 1

    for column in range(config.number_of_columns):
        for row in range(config.number_of_rows):
            row_offset = config.distance_between_switch_centers * row
            column_offset = config.distance_between_switch_centers * (
                column + 1
            )
            column_stagger_size = (
                config.column_stagger_percents[column]
                / config.distance_between_switch_centers
            )
            stagger_offset = config.distance_between_switch_centers * (
                column_stagger_size
            )
            key_offset_x = (
                config.distance_between_switch_centers / 2
            ) + column_offset
            key_offset_y = (
                (config.distance_between_switch_centers / 2)
                + row_offset
                + stagger_offset
            )
            switch_plate = (
                switch_plate.moveTo(key_offset_x, key_offset_y)
                .rect(
                    config.distance_between_switch_centers
                    + widen_cutout_around_key_size,
                    config.distance_between_switch_centers
                    + widen_cutout_around_key_size,
                )
                .rect(
                    config.switch_plate_key_cutout_size,
                    config.switch_plate_key_cutout_size,
                )
                .extrude(config.base_layer_thickness)
            )

    inner_keys_stagger_percent = (
        config.stagger_percent_for_double_inner_keys
        if config.has_double_inner_keys
        else config.stagger_percent_for_single_inner_key
    )

    inner_key_offset_x = config.distance_between_switch_centers / 2
    inner_key_offset_y = (
        config.distance_between_switch_centers / 2
    ) + inner_keys_stagger_percent

    widen_cutout_around_inner_keys_size = (
        0 if config.has_double_inner_keys else 1.5
    )
    inner_keys_unit_height = 1 if config.has_double_inner_keys else 1.5

    inner_keys_height = (
        config.distance_between_switch_centers * inner_keys_unit_height
    ) + widen_cutout_around_inner_keys_size

    switch_plate = (
        switch_plate.moveTo(inner_key_offset_x, inner_key_offset_y)
        .rect(
            config.switch_plate_key_cutout_size,
            config.switch_plate_key_cutout_size,
        )
        .rect(
            config.distance_between_switch_centers
            + widen_cutout_around_key_size,
            inner_keys_height,
        )
        .extrude(config.base_layer_thickness)
    )

    if config.has_double_inner_keys:
        switch_plate = (
            switch_plate.moveTo(
                inner_key_offset_x,
                inner_key_offset_y + config.distance_between_switch_centers,
            )
            .rect(
                config.switch_plate_key_cutout_size,
                config.switch_plate_key_cutout_size,
            )
            .rect(
                config.distance_between_switch_centers
                + widen_cutout_around_key_size,
                inner_keys_height,
            )
            .extrude(config.base_layer_thickness)
        )

    switch_plate = switch_plate.rotateAboutCenter([0, 0, 1], config.angle)

    inner_keys_top_left = switch_plate.vertices("<X").val().Center()

    switch_plate = switch_plate.mirror(
        mirrorPlane="YZ",
        union=True,
        basePointVector=(
            inner_keys_top_left.x + (widen_cutout_around_key_size / 2),
            inner_keys_top_left.y,
        ),
    )
    return switch_plate


def make_bottom_plate(geometry, config):
    return (
        cq.Workplane()
        .polyline(geometry.case_outer)
        .close()
        .extrude(-geometry.thickness)
        .drill_holes(geometry, config)
        .drill_reset_button_hole(geometry, config)
    )


def make_top_plate(geometry, config):
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
        .drill_holes(geometry, config)
    )


def make_switch_plate(switch_plate_inner, geometry, config):
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
        .drill_holes(geometry, config)
    )
    switch_plate_inner = switch_plate_inner.translate(
        [0, 0, -geometry.thickness]
    )
    return fuse_parts([switch_plate_outer, switch_plate_inner])


def make_spacer(geometry, config):
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
        .drill_holes(geometry, config)
    )


def make_keyboard_parts(user_config={}):
    config = SimpleNamespace(**{**default_config.__dict__, **user_config})

    parts = []

    [time_elapsed, total_time] = timer()

    switch_plate_inner = make_switch_plate_inner(config).center_on_2d_plane()
    time_elapsed("Inner switch plate")

    geometry = calculate_geometry_from_switch_plate_inner(
        switch_plate_inner, config
    )

    parts.append(("Top plate", make_top_plate(geometry, config)))
    time_elapsed("Top plate")

    parts.append(
        (
            "Switch plate",
            make_switch_plate(switch_plate_inner, geometry, config),
        )
    )
    time_elapsed("Switch plate")

    if config.has_thicc_spacer:
        parts.append(("Spacer", make_spacer(geometry, config)))
        time_elapsed("Spacer")
    else:
        parts.append(("Spacer 1", make_spacer(geometry, config)))
        parts.append(("Spacer 2", make_spacer(geometry, config)))
        time_elapsed("Spacers")

    parts.append(("Bottom plate", make_bottom_plate(geometry, config)))
    time_elapsed("Bottom plate")

    total_time()

    return parts


if "show_object" in globals():
    keyboard_parts = make_keyboard_parts()
    if not view_config.flatten:
        keyboard_parts = explode_parts(keyboard_parts, view_config.explode_by)

    for layer_name_and_part in keyboard_parts:
        [layer_name, part] = layer_name_and_part
        show_object(part, name=layer_name)

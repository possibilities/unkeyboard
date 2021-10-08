import config
import cadquery as cq
from make_keys import make_keys
from fuse_parts import fuse_parts


def make_plate_key():
    switch_groove_cutout_length = 5
    switch_groove_cutout_width = 1
    switch_groove_cutout_height = 3.5

    switch_cutout_length = 13.9
    switch_cutout_width = 13.9

    result = cq.Workplane()

    result = result.box(config.key_length, config.key_width, config.plate_thickness)

    switch_hole_cutout = cq.Workplane().box(
        switch_cutout_width, switch_cutout_length, config.plate_thickness
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
                -(config.plate_thickness - switch_groove_cutout_height) / 2,
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
                -(config.plate_thickness - switch_groove_cutout_height) / 2,
            ]
        )
    )
    result = result.cut(switch_bottom_groove_cutout)

    return result


def plate_keys():
    plate_key = make_plate_key()

    plate_keys_right = make_keys(plate_key, side_of_board="left")
    plate_keys_left = make_keys(plate_key, side_of_board="right")

    if config.angle > 0:
        plate_keys_right = plate_keys_right.rotate((0, 0, 0), (0, 0, 1), config.angle)
        plate_keys_left = plate_keys_left.rotate((0, 0, 0), (0, 0, 1), -config.angle)

        plate_tilt_right_side_top_left_corner = (
            plate_keys_right.vertices("<X").val().Center()
        )

        plate_keys_right = plate_keys_right.translate(
            [-plate_tilt_right_side_top_left_corner.x, 0, 0]
        )
        plate_keys_left = plate_keys_left.translate(
            [plate_tilt_right_side_top_left_corner.x, 0, 0]
        )

        plate_tilt_right_side_bottom_left_corner = (
            plate_keys_right.vertices("<Y").val().Center()
        )
        plate_tilt_right_side_top_left_corner = (
            plate_keys_right.vertices("<X").val().Center()
        )

        middle_connector = (
            plate_keys_right.faces("front")
            .workplane()
            .moveTo(
                plate_tilt_right_side_top_left_corner.x,
                plate_tilt_right_side_top_left_corner.y,
            )
            .lineTo(
                plate_tilt_right_side_bottom_left_corner.x,
                plate_tilt_right_side_bottom_left_corner.y,
            )
            .lineTo(
                -plate_tilt_right_side_bottom_left_corner.x,
                plate_tilt_right_side_bottom_left_corner.y,
            )
            .close()
            .extrude(-config.plate_thickness)
        )

        return fuse_parts(
            [
                plate_keys_right,
                plate_keys_left,
                middle_connector,
            ]
        )

    return fuse_parts([plate_keys_right, plate_keys_left])

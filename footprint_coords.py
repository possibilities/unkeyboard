from case import switch_plate_cutout_size
from calculate_rectangle_corners import calculate_rectangle_corners
from reverse import reverse

mcu_pad_clearance = 1.4
default_space_between_tracks = 0.7
min_length_of_connector = 1.1
total_space_for_tracks_thumb_key = 8.6
path_distance_below_thumb_keys = 6
max_space_between_tracks = total_space_for_tracks_thumb_key / 6
y_offset_of_left_switch_pad_from_center = 2.54
y_offset_of_right_switch_pad_from_center = 5.08
y_offset_of_first_track = 6


def right_edge_of_key(key):
    [_upper_left, upper_right, lower_right, _lower_left] = reverse(
        calculate_rectangle_corners(
            key["switch"]["position"],
            switch_plate_cutout_size,
            switch_plate_cutout_size,
            angle=key["switch"]["rotation"],
        )
    )

    return [upper_right, lower_right]


def left_edge_of_key(key):
    [upper_left, _upper_right, _lower_right, lower_left] = reverse(
        calculate_rectangle_corners(
            key["switch"]["position"],
            switch_plate_cutout_size,
            switch_plate_cutout_size,
            angle=key["switch"]["rotation"],
        )
    )

    return [upper_left, lower_left]


def upper_edge_of_key(key, align_to_pad_height=None):
    if align_to_pad_height:
        [
            upper_left_aligned_to_right_switch_pad_height,
            upper_right_aligned_to_right_switch_pad_height,
            _lower_right_aligned_to_right_switch_pad_height,
            _lower_left_aligned_to_right_switch_pad_height,
        ] = reverse(
            calculate_rectangle_corners(
                key["switch"]["position"],
                switch_plate_cutout_size,
                y_offset_of_right_switch_pad_from_center * 2,
                angle=key["switch"]["rotation"],
            )
        )
        return [
            upper_right_aligned_to_right_switch_pad_height,
            upper_left_aligned_to_right_switch_pad_height,
        ]

    [upper_left, upper_right, _lower_right, _lower_left] = reverse(
        calculate_rectangle_corners(
            key["switch"]["position"],
            switch_plate_cutout_size,
            switch_plate_cutout_size,
            angle=key["switch"]["rotation"],
        )
    )

    return [upper_right, upper_left]


def lower_edge_of_key(key, expand_by=None, align_to_inner_track=None):
    if align_to_inner_track:
        [
            _upper_left_track,
            _upper_right_track,
            lower_right_track,
            lower_left_track,
        ] = reverse(
            calculate_rectangle_corners(
                key["switch"]["position"],
                switch_plate_cutout_size,
                y_offset_of_first_track * 2
                - ((align_to_inner_track - 1) * max_space_between_tracks),
                angle=key["switch"]["rotation"],
            )
        )
        return [lower_right_track, lower_left_track]

    if expand_by:
        [
            _upper_left_expanded_height,
            _upper_right_expanded_height,
            lower_right_expanded_height,
            lower_left_expanded_height,
        ] = reverse(
            calculate_rectangle_corners(
                key["switch"]["position"],
                switch_plate_cutout_size,
                switch_plate_cutout_size + expand_by,
                angle=key["switch"]["rotation"],
            )
        )
        return [lower_right_expanded_height, lower_left_expanded_height]

    [_upper_left, _upper_right, lower_right, lower_left] = reverse(
        calculate_rectangle_corners(
            key["switch"]["position"],
            switch_plate_cutout_size,
            switch_plate_cutout_size,
            angle=key["switch"]["rotation"],
        )
    )

    return [lower_right, lower_left]


def upper_right_of_key(key, align_to_pad_height=None):
    if align_to_pad_height == "1":
        [
            _upper_left_aligned_to_right_switch_pad_height,
            upper_right_aligned_to_right_switch_pad_height,
            _lower_right_aligned_to_right_switch_pad_height,
            _lower_left_aligned_to_right_switch_pad_height,
        ] = reverse(
            calculate_rectangle_corners(
                key["switch"]["position"],
                switch_plate_cutout_size,
                y_offset_of_right_switch_pad_from_center * 2,
                angle=key["switch"]["rotation"],
            )
        )
        return upper_right_aligned_to_right_switch_pad_height

    [_upper_left, upper_right, _lower_right, _lower_left] = reverse(
        calculate_rectangle_corners(
            key["switch"]["position"],
            switch_plate_cutout_size,
            switch_plate_cutout_size,
            angle=key["switch"]["rotation"],
        )
    )

    return upper_right


def lower_left_of_key(
    key, align_to_pad_height=None, expand_by=None, align_to_inner_track=None
):
    if align_to_inner_track is not None:
        [
            _upper_left_track,
            _upper_right_track,
            _lower_right_track,
            lower_left_track,
        ] = reverse(
            calculate_rectangle_corners(
                key["switch"]["position"],
                switch_plate_cutout_size,
                y_offset_of_first_track * 2
                - ((align_to_inner_track - 1) * max_space_between_tracks),
                angle=key["switch"]["rotation"],
            )
        )
        return lower_left_track

    if expand_by:
        [
            _upper_left_expanded_height,
            _upper_right_expanded_height,
            _lower_right_expanded_height,
            lower_left_expanded_height,
        ] = reverse(
            calculate_rectangle_corners(
                key["switch"]["position"],
                switch_plate_cutout_size,
                switch_plate_cutout_size + expand_by,
                angle=key["switch"]["rotation"],
            )
        )
        return lower_left_expanded_height

    [upper_left, upper_right, lower_right, lower_left] = reverse(
        calculate_rectangle_corners(
            key["switch"]["position"],
            switch_plate_cutout_size,
            switch_plate_cutout_size,
            angle=key["switch"]["rotation"],
        )
    )

    return lower_left


def lower_right_of_key(
    key, align_to_pad_height=None, expand_by=None, align_to_inner_track=None
):
    if expand_by:
        [
            _upper_left_expanded_height,
            _upper_right_expanded_height,
            lower_right_expanded_height,
            _lower_left_expanded_height,
        ] = reverse(
            calculate_rectangle_corners(
                key["switch"]["position"],
                switch_plate_cutout_size,
                switch_plate_cutout_size + expand_by,
                angle=key["switch"]["rotation"],
            )
        )
        return lower_right_expanded_height

    if align_to_inner_track is not None:
        [
            _upper_left_track,
            _upper_right_track,
            lower_right_track,
            _lower_left_track,
        ] = reverse(
            calculate_rectangle_corners(
                key["switch"]["position"],
                switch_plate_cutout_size,
                y_offset_of_first_track * 2
                - ((align_to_inner_track - 1) * max_space_between_tracks),
                angle=key["switch"]["rotation"],
            )
        )
        return lower_right_track

    [_upper_left, _upper_right, lower_right, _lower_left] = reverse(
        calculate_rectangle_corners(
            key["switch"]["position"],
            switch_plate_cutout_size,
            switch_plate_cutout_size,
            angle=key["switch"]["rotation"],
        )
    )

    return lower_right


def upper_left_of_key(key, align_to_pad_height=None):
    if align_to_pad_height == "1":
        [
            upper_left_aligned_to_right_switch_pad_height,
            _upper_right_aligned_to_right_switch_pad_height,
            _lower_right_aligned_to_right_switch_pad_height,
            _lower_left_aligned_to_right_switch_pad_height,
        ] = reverse(
            calculate_rectangle_corners(
                key["switch"]["position"],
                switch_plate_cutout_size,
                y_offset_of_right_switch_pad_from_center * 2,
                angle=key["switch"]["rotation"],
            )
        )
        return upper_left_aligned_to_right_switch_pad_height

    if align_to_pad_height == "2":
        [
            upper_left_aligned_to_right_switch_pad_height,
            _upper_right_aligned_to_right_switch_pad_height,
            _lower_right_aligned_to_right_switch_pad_height,
            _lower_left_aligned_to_right_switch_pad_height,
        ] = reverse(
            calculate_rectangle_corners(
                key["switch"]["position"],
                switch_plate_cutout_size,
                y_offset_of_left_switch_pad_from_center * 2,
                angle=key["switch"]["rotation"],
            )
        )
        return upper_left_aligned_to_right_switch_pad_height

    [upper_left, upper_right, lower_right, lower_left] = reverse(
        calculate_rectangle_corners(
            key["switch"]["position"],
            switch_plate_cutout_size,
            switch_plate_cutout_size,
            angle=key["switch"]["rotation"],
        )
    )

    return upper_left


def switch_pad_position(key, pad_name):
    return key["switch"]["pads"][pad_name]["position"]


def diode_pad_position(key, pad_name):
    return key["diode"]["pads"][pad_name]["position"]


def switch_rotation(key):
    return key["diode"]["rotation"]

from midpoint import midpoint
from calculate_point_for_angle import calculate_point_for_angle
from reverse import reverse
from from_pairs import from_pairs
from get_item_at_index import get_item_at_index
from line_to_edge import line_to_edge
from calculate_angle_between_points import calculate_angle_between_points
from edge_from_point_at_angle import edge_from_point_at_angle


from footprint_coords import (
    upper_left_of_key,
    upper_edge_of_key,
    lower_edge_of_key,
    lower_right_of_key,
    lower_left_of_key,
    switch_pad_position,
    diode_pad_position,
    left_edge_of_key,
    right_edge_of_key,
    upper_right_of_key,
    switch_rotation,
)


mcu_pad_clearance = 1.4
default_space_between_tracks = 0.7
min_length_of_connector = 1.1
total_space_for_tracks_thumb_key = 8.6
path_distance_below_thumb_keys = 6
max_space_between_tracks = total_space_for_tracks_thumb_key / 6

mcu_pads_to_net_names = {
    "1": "/ROW3",
    "2": "/ROW4",
    "3": "GND",
    "4": "GND",
    "5": "/ROW2",
    "6": "/ROW1",
    "7": "/ROW0",
    "8": "/COL12",
    "9": "/COL11",
    "10": "/COL10",
    "11": "/COL9",
    "12": "/COL8",
    "23": "GND",
    "22": "Net-(SW-RST1-Pad2)",
    "20": "/COL0",
    "19": "/COL1",
    "18": "/COL2",
    "17": "/COL3",
    "16": "/COL4",
    "15": "/COL5",
    "14": "/COL6",
    "13": "/COL7",
}


left_pads_exiting_bottom = [
    "6",
    "7",
    "8",
    "9",
    "10",
]

right_pads_exiting_bottom = [
    "20",
    "19",
    "18",
    "17",
    "16",
    "15",
]


def calculate_columns_tracks(left_side_columns, right_side_columns, config):
    tracks = []
    for column_index, keys in enumerate(left_side_columns):
        for row_index, key in enumerate(keys):
            previous_key = get_item_at_index(keys, row_index - 1)
            column_net = f"/COL{column_index}"
            if previous_key:
                tracks.append(
                    {
                        "side": "back",
                        "net": column_net,
                        "points": [
                            diode_pad_position(key, "2"),
                            lower_right_of_key(key),
                            lower_right_of_key(previous_key),
                        ],
                    },
                )
            else:
                tracks.append(
                    {
                        "side": "back",
                        "net": column_net,
                        "points": [
                            diode_pad_position(key, "2"),
                            lower_right_of_key(key),
                        ],
                    },
                )
    for column_index, keys in enumerate(right_side_columns):
        for row_index, key in enumerate(keys):
            previous_key = get_item_at_index(keys, row_index - 1)
            column_net = f"/COL{column_index + len(left_side_columns) + 1}"
            if previous_key:
                tracks.append(
                    {
                        "side": "back",
                        "net": column_net,
                        "points": [
                            diode_pad_position(key, "2"),
                            lower_right_of_key(key),
                            lower_right_of_key(previous_key),
                        ],
                    },
                )
            else:
                tracks.append(
                    {
                        "side": "back",
                        "net": column_net,
                        "points": [
                            diode_pad_position(key, "2"),
                            lower_right_of_key(key),
                        ],
                    },
                )
    return tracks


def switches_to_columns(keys):
    tracks = []
    for key in keys:
        key_net = f"Net-({key['diode']['reference']}-Pad1)"
        tracks.append(
            {
                "side": "back",
                "net": key_net,
                "points": [
                    switch_pad_position(key, "2"),
                    upper_left_of_key(key, align_to_pad_height="2"),
                    lower_left_of_key(key),
                    diode_pad_position(key, "1"),
                ],
            },
        )
    return tracks


def left_side_rows(left_side_rows):
    tracks = []
    for row_index, keys in enumerate(left_side_rows):
        for column_index, key in enumerate(keys):
            previous_key = get_item_at_index(keys, column_index - 1)

            column_net = f"/ROW{len(left_side_rows) - 1 - row_index}"
            if previous_key:
                tracks.append(
                    {
                        "side": "front",
                        "net": column_net,
                        "points": [
                            upper_right_of_key(previous_key, align_to_pad_height="1"),
                            line_to_edge(
                                line=right_edge_of_key(previous_key),
                                edge=upper_edge_of_key(key, align_to_pad_height="2"),
                            ),
                            upper_left_of_key(key, align_to_pad_height="1"),
                            switch_pad_position(key, "1"),
                            upper_right_of_key(key, align_to_pad_height="1"),
                        ],
                    },
                )
            else:
                tracks.append(
                    {
                        "side": "front",
                        "net": column_net,
                        "points": [
                            switch_pad_position(key, "1"),
                            upper_right_of_key(key, align_to_pad_height="1"),
                        ],
                    },
                )

    return tracks


def right_side_rows(right_side_rows):
    tracks = []

    for row_index, keys in enumerate(right_side_rows):
        for column_index, key in enumerate(keys):
            next_key = get_item_at_index(keys, column_index + 1)
            previous_key = get_item_at_index(keys, column_index - 1)

            points = []

            if previous_key:
                points = [
                    *points,
                    upper_right_of_key(previous_key, align_to_pad_height="1"),
                    line_to_edge(
                        edge=upper_edge_of_key(previous_key, align_to_pad_height="2"),
                        line=left_edge_of_key(key),
                    ),
                    upper_left_of_key(key, align_to_pad_height="1"),
                    switch_pad_position(key, "1"),
                ]

            else:
                points = [
                    *points,
                    upper_left_of_key(key, align_to_pad_height="1"),
                    switch_pad_position(key, "1"),
                ]

            if next_key:
                points = [
                    *points,
                    upper_right_of_key(key, align_to_pad_height="1"),
                ]

            column_net = f"/ROW{len(right_side_rows) - 1 - row_index}"
            tracks.append(
                {
                    "side": "front",
                    "net": column_net,
                    "points": points,
                }
            )

    return tracks


def switch_rows_to_right_side_thumb_key(
    left_side_last_row,
    right_side_last_row,
    left_side_thumb_key,
    right_side_thumb_key,
):
    tracks = []
    left_side_last_row_last_column_key = left_side_last_row[-1]
    right_side_last_row_first_column_key = right_side_last_row[0]
    row_net = "/ROW0"
    tracks.append(
        {
            "side": "front",
            "net": row_net,
            "points": [
                upper_right_of_key(
                    left_side_last_row_last_column_key, align_to_pad_height="1"
                ),
                line_to_edge(
                    edge=lower_edge_of_key(left_side_thumb_key, expand_by=4),
                    line=right_edge_of_key(left_side_last_row[-1]),
                ),
                lower_left_of_key(left_side_thumb_key, expand_by=4),
                lower_right_of_key(left_side_thumb_key, expand_by=4),
                lower_left_of_key(right_side_thumb_key, expand_by=4),
                upper_left_of_key(right_side_thumb_key, align_to_pad_height="1"),
                switch_pad_position(right_side_thumb_key, "1"),
                upper_right_of_key(right_side_thumb_key, align_to_pad_height="1"),
                lower_right_of_key(right_side_thumb_key),
                line_to_edge(
                    edge=lower_edge_of_key(right_side_thumb_key),
                    line=left_edge_of_key(right_side_last_row_first_column_key),
                ),
                upper_left_of_key(
                    right_side_last_row_first_column_key, align_to_pad_height="1"
                ),
            ],
        },
    )
    return tracks


def switch_rows_to_left_side_thumb_key(
    left_side_second_to_last_row,
    right_side_second_to_last_row,
    left_side_thumb_key,
    right_side_thumb_key,
    config,
):
    tracks = []

    left_side_second_to_last_row_last_key = left_side_second_to_last_row[-1]
    right_side_second_to_last_row_first_key = right_side_second_to_last_row[0]
    row_net = "/ROW1"
    tracks.append(
        {
            "side": "front",
            "net": row_net,
            "points": [
                upper_right_of_key(
                    left_side_second_to_last_row_last_key, align_to_pad_height="1"
                ),
                line_to_edge(
                    line=upper_edge_of_key(left_side_thumb_key),
                    edge=right_edge_of_key(left_side_second_to_last_row_last_key),
                ),
                upper_left_of_key(left_side_thumb_key),
                upper_left_of_key(left_side_thumb_key, align_to_pad_height="1"),
                switch_pad_position(left_side_thumb_key, "1"),
                upper_right_of_key(left_side_thumb_key, align_to_pad_height="1"),
                upper_right_of_key(left_side_thumb_key),
                upper_left_of_key(right_side_thumb_key),
                upper_right_of_key(right_side_thumb_key),
                line_to_edge(
                    line=upper_edge_of_key(right_side_thumb_key),
                    edge=left_edge_of_key(right_side_second_to_last_row_first_key),
                ),
                upper_left_of_key(
                    right_side_second_to_last_row_first_key, align_to_pad_height="1"
                ),
            ],
        },
    )
    return tracks


def right_side_columns_towards_center(
    right_side_rows,
    config,
):
    tracks = []
    vias = []

    lead_row_keys = right_side_rows[-3]
    for column_index, key in enumerate(lead_row_keys):
        if column_index < len(lead_row_keys):
            number_of_tracks_passing_through_key = len(lead_row_keys) - column_index
            for track_index in range(number_of_tracks_passing_through_key):
                if track_index == (number_of_tracks_passing_through_key - 1):
                    column_net = f"/COL{config['number_of_columns'] + column_index + 1}"
                    tracks.append(
                        {
                            "side": "front",
                            "net": column_net,
                            "points": [
                                lower_right_of_key(
                                    key,
                                    align_to_inner_track=track_index + 1,
                                ),
                                lower_left_of_key(
                                    key,
                                    align_to_inner_track=track_index + 1,
                                ),
                            ],
                        },
                    )
                    vias.append(
                        {
                            "net": column_net,
                            "point": lower_right_of_key(
                                key,
                                align_to_inner_track=track_index + 1,
                            ),
                        }
                    )
                else:
                    sub_track_net = f"/COL{config['number_of_columns'] - track_index + config['number_of_columns']}"
                    tracks.append(
                        {
                            "side": "front",
                            "net": sub_track_net,
                            "points": [
                                lower_right_of_key(
                                    key, align_to_inner_track=track_index + 1
                                ),
                                lower_left_of_key(
                                    key, align_to_inner_track=track_index + 1
                                ),
                            ],
                        },
                    )

    max_space_between_tracks = total_space_for_tracks_thumb_key / len(
        right_side_rows[0]
    )

    lead_row_keys = right_side_rows[-3]
    for column_index, key in enumerate(lead_row_keys):
        if column_index < len(lead_row_keys):
            previous_key = get_item_at_index(lead_row_keys, column_index - 1)
            next_key = get_item_at_index(lead_row_keys, column_index + 1)
            number_of_tracks_passing_through_key = len(lead_row_keys) - column_index

            is_previous_column_stagger_less_than_or_equal_to_current_column = (
                previous_key
                and upper_right_of_key(previous_key)[1] > upper_left_of_key(key)[1]
            )

            angle_between_keys = (
                calculate_angle_between_points(
                    key["switch"]["position"],
                    previous_key["switch"]["position"],
                )
                - 180
                if previous_key
                else None
            )

            previous_key_has_same_stagger = (
                angle_between_keys == -key["switch"]["rotation"]
            )

            if previous_key_has_same_stagger:
                column_net = f"/COL{config['number_of_columns'] + column_index + 1}"
                tracks.append(
                    {
                        "side": "front",
                        "net": column_net,
                        "points": [
                            lower_right_of_key(previous_key, align_to_inner_track=1),
                            lower_left_of_key(key, align_to_inner_track=1),
                        ],
                    },
                )

            else:
                for track_index in range(number_of_tracks_passing_through_key):
                    sub_track_net = f"/COL{config['number_of_columns'] - track_index + config['number_of_columns']}"
                    if previous_key and next_key:
                        if is_previous_column_stagger_less_than_or_equal_to_current_column:
                            left_side_connector_point = calculate_point_for_angle(
                                lower_right_of_key(
                                    previous_key, align_to_inner_track=track_index + 1
                                ),
                                (
                                    (
                                        number_of_tracks_passing_through_key
                                        - track_index
                                        - 1
                                    )
                                    * (max_space_between_tracks / 2)
                                )
                                + (max_space_between_tracks / 2),
                                key["switch"]["rotation"] + 90,
                            )
                            left_side_connector_right_angle_point = line_to_edge(
                                line=[
                                    left_side_connector_point,
                                    edge_from_point_at_angle(
                                        left_side_connector_point,
                                        key["switch"]["rotation"],
                                    ),
                                ],
                                edge=lower_edge_of_key(
                                    key, align_to_inner_track=track_index + 1
                                ),
                            )
                            tracks.append(
                                {
                                    "side": "front",
                                    "net": sub_track_net,
                                    "points": [
                                        lower_right_of_key(
                                            previous_key,
                                            align_to_inner_track=track_index + 1,
                                        ),
                                        left_side_connector_point,
                                        left_side_connector_right_angle_point,
                                        lower_left_of_key(
                                            key, align_to_inner_track=track_index + 1
                                        ),
                                    ],
                                },
                            )
                        else:
                            left_side_connector_point = calculate_point_for_angle(
                                lower_right_of_key(
                                    previous_key,
                                    align_to_inner_track=track_index + 1,
                                ),
                                (track_index * (max_space_between_tracks / 2))
                                + (max_space_between_tracks / 2),
                                key["switch"]["rotation"] + 90,
                            )
                            left_side_connector_right_angle_point = line_to_edge(
                                line=[
                                    left_side_connector_point,
                                    edge_from_point_at_angle(
                                        left_side_connector_point,
                                        key["switch"]["rotation"],
                                    ),
                                ],
                                edge=lower_edge_of_key(
                                    key, align_to_inner_track=track_index + 1
                                ),
                            )
                            tracks.append(
                                {
                                    "side": "front",
                                    "net": sub_track_net,
                                    "points": [
                                        lower_right_of_key(
                                            previous_key,
                                            align_to_inner_track=track_index + 1,
                                        ),
                                        left_side_connector_point,
                                        left_side_connector_right_angle_point,
                                        lower_left_of_key(
                                            key,
                                            align_to_inner_track=track_index + 1,
                                        ),
                                    ],
                                },
                            )
    return [tracks, vias]


def left_side_columns_towards_center(
    left_side_rows,
    config,
):
    tracks = []
    vias = []

    lead_row_keys = left_side_rows[-3]
    for column_index, key in enumerate(lead_row_keys):
        if column_index > 0:
            number_of_tracks_passing_through_key = column_index
            for track_index in range(number_of_tracks_passing_through_key):
                sub_track_net = f"/COL{track_index}"
                tracks.append(
                    {
                        "side": "front",
                        "net": sub_track_net,
                        "points": [
                            lower_left_of_key(
                                key,
                                align_to_inner_track=track_index + 1,
                            ),
                            lower_right_of_key(
                                key,
                                align_to_inner_track=track_index + 1,
                            ),
                        ],
                    },
                )

    max_space_between_tracks = total_space_for_tracks_thumb_key / len(left_side_rows[0])
    column_stagger_percents = reverse(config["column_stagger_percents"])

    lead_row_keys = left_side_rows[-3]
    for column_index, key in enumerate(lead_row_keys):
        previous_key = get_item_at_index(lead_row_keys, column_index - 1)
        number_of_tracks_passing_through_key = column_index - 1

        stagger_percent = column_stagger_percents[column_index]
        previous_stagger_percent = (
            0 if column_index == 0 else column_stagger_percents[column_index - 1]
        )
        is_previous_column_stagger_less_than_or_equal_to_current_column = (
            previous_stagger_percent <= stagger_percent
        )

        if (
            previous_key
            and is_previous_column_stagger_less_than_or_equal_to_current_column
        ):
            left_side_connector_point = line_to_edge(
                line=lower_edge_of_key(key, align_to_inner_track=column_index),
                edge=right_edge_of_key(previous_key),
            )

            column_net = f"/COL{column_index - 1}"
            vias.append(
                {
                    "net": column_net,
                    "point": left_side_connector_point,
                }
            )
            tracks.append(
                {
                    "side": "front",
                    "net": column_net,
                    "points": [
                        left_side_connector_point,
                        lower_left_of_key(key, align_to_inner_track=column_index),
                    ],
                },
            )

        if previous_key:
            for track_index in range(number_of_tracks_passing_through_key):
                sub_track_net = f"/COL{track_index}"
                if is_previous_column_stagger_less_than_or_equal_to_current_column:
                    left_side_connector_point = calculate_point_for_angle(
                        lower_right_of_key(
                            previous_key, align_to_inner_track=track_index + 1
                        ),
                        (number_of_tracks_passing_through_key - track_index - 1)
                        * (max_space_between_tracks / 2),
                        previous_key["switch"]["rotation"] + 90,
                    )
                    left_side_connector_right_angle_point = line_to_edge(
                        line=[
                            left_side_connector_point,
                            edge_from_point_at_angle(
                                left_side_connector_point, key["switch"]["rotation"]
                            ),
                        ],
                        edge=lower_edge_of_key(
                            key, align_to_inner_track=track_index + 1
                        ),
                    )
                    if track_index < number_of_tracks_passing_through_key - 1:
                        tracks.append(
                            {
                                "side": "front",
                                "net": sub_track_net,
                                "points": [
                                    lower_right_of_key(
                                        previous_key,
                                        align_to_inner_track=track_index + 1,
                                    ),
                                    left_side_connector_point,
                                    left_side_connector_right_angle_point,
                                    lower_left_of_key(
                                        key, align_to_inner_track=track_index + 1
                                    ),
                                ],
                            },
                        )
                    else:
                        tracks.append(
                            {
                                "side": "front",
                                "net": sub_track_net,
                                "points": [
                                    lower_right_of_key(
                                        previous_key,
                                        align_to_inner_track=track_index + 1,
                                    ),
                                    left_side_connector_right_angle_point,
                                    lower_left_of_key(
                                        key, align_to_inner_track=track_index + 1
                                    ),
                                ],
                            },
                        )

            for track_index in range(number_of_tracks_passing_through_key + 1):
                sub_track_net = f"/COL{track_index}"
                if not is_previous_column_stagger_less_than_or_equal_to_current_column:
                    left_side_connector_point = calculate_point_for_angle(
                        lower_right_of_key(
                            previous_key, align_to_inner_track=track_index + 1
                        ),
                        track_index * (max_space_between_tracks / 2),
                        previous_key["switch"]["rotation"] + 90,
                    )

                    left_side_connector_point_extended = line_to_edge(
                        line=[
                            left_side_connector_point,
                            calculate_point_for_angle(
                                left_side_connector_point,
                                1,
                                key["switch"]["rotation"],
                            ),
                        ],
                        edge=lower_edge_of_key(
                            key, align_to_inner_track=track_index + 1
                        ),
                    )
                    if track_index < number_of_tracks_passing_through_key:
                        if track_index != 0:
                            tracks.append(
                                {
                                    "side": "front",
                                    "net": sub_track_net,
                                    "points": [
                                        lower_right_of_key(
                                            previous_key,
                                            align_to_inner_track=track_index + 1,
                                        ),
                                        left_side_connector_point,
                                        left_side_connector_point_extended,
                                    ],
                                },
                            )
                        else:
                            tracks.append(
                                {
                                    "side": "front",
                                    "net": sub_track_net,
                                    "points": [
                                        lower_right_of_key(
                                            previous_key,
                                            align_to_inner_track=track_index + 1,
                                        ),
                                        left_side_connector_point_extended,
                                    ],
                                },
                            )
                    else:
                        vias.append(
                            {
                                "net": sub_track_net,
                                "point": lower_right_of_key(
                                    previous_key, align_to_inner_track=track_index + 1
                                ),
                            }
                        )
                        if track_index != 0:
                            tracks.append(
                                {
                                    "side": "front",
                                    "net": sub_track_net,
                                    "points": [
                                        lower_right_of_key(
                                            previous_key,
                                            align_to_inner_track=track_index + 1,
                                        ),
                                        left_side_connector_point,
                                        left_side_connector_point_extended,
                                    ],
                                },
                            )
                    tracks.append(
                        {
                            "side": "front",
                            "net": sub_track_net,
                            "points": [
                                left_side_connector_point_extended,
                                lower_left_of_key(
                                    key,
                                    align_to_inner_track=track_index + 1,
                                ),
                            ],
                        },
                    )

    return [tracks, vias]


def switches_to_columns_for_thumb_keys(
    left_side_thumb_key,
    right_side_thumb_key,
    config,
):
    tracks = []
    column_net = f"/COL{config['number_of_columns']}"
    tracks.append(
        {
            "side": "back",
            "net": column_net,
            "points": [
                diode_pad_position(left_side_thumb_key, "2"),
                line_to_edge(
                    line=[
                        diode_pad_position(left_side_thumb_key, "2"),
                        calculate_point_for_angle(
                            diode_pad_position(left_side_thumb_key, "2"),
                            path_distance_below_thumb_keys,
                            switch_rotation(left_side_thumb_key),
                        ),
                    ],
                    edge=lower_edge_of_key(left_side_thumb_key, expand_by=4),
                ),
                lower_right_of_key(left_side_thumb_key, expand_by=4),
                lower_left_of_key(right_side_thumb_key, expand_by=4),
                line_to_edge(
                    line=[
                        diode_pad_position(right_side_thumb_key, "2"),
                        calculate_point_for_angle(
                            diode_pad_position(right_side_thumb_key, "2"),
                            path_distance_below_thumb_keys,
                            switch_rotation(right_side_thumb_key),
                        ),
                    ],
                    edge=lower_edge_of_key(right_side_thumb_key, expand_by=4),
                ),
                diode_pad_position(right_side_thumb_key, "2"),
            ],
        },
    )
    return tracks


def left_side_towards_mcu(
    left_side_rows,
    left_side_mcu_pads,
    right_side_mcu_pads,
    mirror_at_point,
    config,
):
    tracks = []
    endpoints = []
    vias = []

    upper_rows = left_side_rows[0:-2]

    for row_index, row in enumerate(upper_rows):
        lead_key_for_row = row[-1]
        row_offset_towards_mcu = (
            -mcu_pad_clearance - row_index * default_space_between_tracks
        )
        lead_towards_mcu = line_to_edge(
            line=upper_edge_of_key(lead_key_for_row, align_to_pad_height="1"),
            edge=[
                (
                    left_side_mcu_pads[0]["position"][0] + row_offset_towards_mcu,
                    left_side_mcu_pads[0]["position"][1],
                ),
                (
                    left_side_mcu_pads[1]["position"][0] + row_offset_towards_mcu,
                    left_side_mcu_pads[1]["position"][1],
                ),
            ],
        )
        row_offset_towards_bottom = mcu_pad_clearance + (
            (row_index + 3) * default_space_between_tracks
        )
        lead_towards_bottom = line_to_edge(
            line=[
                lead_towards_mcu,
                (lead_towards_mcu[0], lead_towards_mcu[1] + 1),
            ],
            edge=[
                (
                    left_side_mcu_pads[-1]["position"][0],
                    left_side_mcu_pads[-1]["position"][1] + row_offset_towards_bottom,
                ),
                (
                    right_side_mcu_pads[-1]["position"][0],
                    right_side_mcu_pads[-1]["position"][1] + row_offset_towards_bottom,
                ),
            ],
        )

        row_net = f"/ROW{len(left_side_rows) - 1 - row_index}"
        tracks.append(
            {
                "side": "front",
                "net": row_net,
                "points": [
                    upper_right_of_key(lead_key_for_row, align_to_pad_height="1"),
                    lead_towards_mcu,
                    lead_towards_bottom,
                    (mirror_at_point[0], lead_towards_bottom[1]),
                ],
            },
        )

    lead_key = left_side_rows[-3][-1]

    for column_index in range(config["number_of_columns"]):
        lead_towards_mcu_offset = (
            0
            - mcu_pad_clearance
            - (
                (
                    config["number_of_columns"]
                    - column_index
                    - 1
                    + (config["number_of_rows"] - 2)
                )
                * default_space_between_tracks
            )
        )
        lead_towards_mcu = line_to_edge(
            line=lower_edge_of_key(lead_key, align_to_inner_track=column_index + 1),
            edge=[
                (
                    left_side_mcu_pads[0]["position"][0] + lead_towards_mcu_offset,
                    left_side_mcu_pads[0]["position"][1],
                ),
                (
                    left_side_mcu_pads[1]["position"][0] + lead_towards_mcu_offset,
                    left_side_mcu_pads[1]["position"][1],
                ),
            ],
        )

        row_offset_towards_bottom_of_mcu = (
            mcu_pad_clearance
            + default_space_between_tracks * 3.5
            + (
                (default_space_between_tracks * 1)
                * (config["number_of_columns"] - column_index + 1.5)
            )
        )
        point_towards_bottom_of_mcu = line_to_edge(
            line=[lead_towards_mcu, (lead_towards_mcu[0], lead_towards_mcu[1] + 1)],
            edge=[
                (
                    left_side_mcu_pads[-1]["position"][0],
                    left_side_mcu_pads[-1]["position"][1]
                    + row_offset_towards_bottom_of_mcu,
                ),
                (
                    left_side_mcu_pads[-1]["position"][0] + 1,
                    left_side_mcu_pads[-1]["position"][1]
                    + row_offset_towards_bottom_of_mcu,
                ),
            ],
        )
        column_net = f"/COL{column_index}"
        tracks.append(
            {
                "side": "front",
                "net": column_net,
                "points": [
                    lower_right_of_key(lead_key, align_to_inner_track=column_index + 1),
                    lead_towards_mcu,
                    point_towards_bottom_of_mcu,
                ],
            },
        )

        if column_index == config["number_of_columns"] - 1:
            vias.append(
                {
                    "net": column_net,
                    "point": lower_right_of_key(
                        lead_key, align_to_inner_track=column_index + 1
                    ),
                }
            )

        endpoints.append([f"column-{column_index + 1}", point_towards_bottom_of_mcu])

    endpoints = from_pairs(endpoints)

    return [tracks, endpoints, vias]


def right_side_towards_mcu(
    right_side_rows,
    right_side_mcu_pads,
    left_side_mcu_pads,
    mirror_at_point,
    config,
):
    tracks = []
    endpoints = []
    vias = []

    upper_rows = right_side_rows[0:-2]

    for row_index, row in enumerate(upper_rows):
        lead_key_for_row = row[0]
        row_offset_lead_towards_mcu = mcu_pad_clearance + (
            (row_index + 2) * default_space_between_tracks
        )
        lead_towards_mcu = line_to_edge(
            line=upper_edge_of_key(lead_key_for_row, align_to_pad_height="1"),
            edge=[
                (
                    right_side_mcu_pads[0]["position"][0] + row_offset_lead_towards_mcu,
                    right_side_mcu_pads[0]["position"][1],
                ),
                (
                    right_side_mcu_pads[1]["position"][0] + row_offset_lead_towards_mcu,
                    right_side_mcu_pads[1]["position"][1],
                ),
            ],
        )
        row_offset_lead_towards_bottom = mcu_pad_clearance + (
            (row_index + 3) * default_space_between_tracks
        )
        lead_towards_bottom = line_to_edge(
            line=[
                lead_towards_mcu,
                (lead_towards_mcu[0], lead_towards_mcu[1] + 1),
            ],
            edge=[
                (
                    right_side_mcu_pads[-1]["position"][0],
                    right_side_mcu_pads[-1]["position"][1]
                    + row_offset_lead_towards_bottom,
                ),
                (
                    right_side_mcu_pads[-1]["position"][0] + 1,
                    right_side_mcu_pads[-1]["position"][1]
                    + row_offset_lead_towards_bottom,
                ),
            ],
        )
        row_net = f"/ROW{len(right_side_rows) - 1 - row_index}"
        tracks.append(
            {
                "side": "front",
                "net": row_net,
                "points": [
                    upper_left_of_key(lead_key_for_row, align_to_pad_height="1"),
                    lead_towards_mcu,
                    lead_towards_bottom,
                    (mirror_at_point[0], lead_towards_bottom[1]),
                ],
            },
        )

    lead_key = right_side_rows[-3][0]

    for column_index in range(config["number_of_columns"]):
        column_index_lead_towards_mcu = mcu_pad_clearance + (
            (
                config["number_of_columns"]
                - column_index
                - 1
                + (config["number_of_rows"] - 2)
            )
            * default_space_between_tracks
        )
        lead_towards_mcu = line_to_edge(
            line=lower_edge_of_key(lead_key, align_to_inner_track=column_index + 1),
            edge=[
                (
                    right_side_mcu_pads[0]["position"][0]
                    + column_index_lead_towards_mcu,
                    right_side_mcu_pads[0]["position"][1],
                ),
                (
                    right_side_mcu_pads[1]["position"][0]
                    + column_index_lead_towards_mcu,
                    right_side_mcu_pads[1]["position"][1],
                ),
            ],
        )
        column_offset_point_towards_bottom_of_mcu = (
            mcu_pad_clearance
            + (default_space_between_tracks * 3)
            + (
                default_space_between_tracks
                * (config["number_of_columns"] - column_index)
            )
        )
        point_towards_bottom_of_mcu = line_to_edge(
            line=[
                lead_towards_mcu,
                (lead_towards_mcu[0], lead_towards_mcu[1] + 1),
            ],
            edge=[
                (
                    right_side_mcu_pads[-1]["position"][0],
                    right_side_mcu_pads[-1]["position"][1]
                    + column_offset_point_towards_bottom_of_mcu,
                ),
                (
                    right_side_mcu_pads[-1]["position"][0] + 1,
                    right_side_mcu_pads[-1]["position"][1]
                    + column_offset_point_towards_bottom_of_mcu,
                ),
            ],
        )
        column_net = f"/COL{config['number_of_columns'] - column_index + config['number_of_columns']}"
        if column_index <= config["number_of_rows"] - 2:
            tracks.append(
                {
                    "side": "front",
                    "net": column_net,
                    "points": [
                        lower_left_of_key(
                            lead_key, align_to_inner_track=column_index + 1
                        ),
                        lead_towards_mcu,
                        point_towards_bottom_of_mcu,
                    ],
                },
            )
            endpoints.append(
                [
                    f"column-{config['number_of_columns'] - column_index + config['number_of_columns']}",
                    point_towards_bottom_of_mcu,
                ]
            )
        else:
            if column_index == config["number_of_rows"] - 1:
                column_index_lead_towards_mcu = mcu_pad_clearance + (
                    (
                        config["number_of_columns"]
                        - column_index
                        - 4
                        + (config["number_of_rows"] - 2)
                    )
                    * default_space_between_tracks
                )
                lead_towards_mcu = line_to_edge(
                    line=lower_edge_of_key(
                        lead_key, align_to_inner_track=column_index + 1
                    ),
                    edge=[
                        (
                            right_side_mcu_pads[0]["position"][0]
                            + column_index_lead_towards_mcu,
                            right_side_mcu_pads[0]["position"][1],
                        ),
                        (
                            right_side_mcu_pads[1]["position"][0]
                            + column_index_lead_towards_mcu,
                            right_side_mcu_pads[1]["position"][1],
                        ),
                    ],
                )
                tracks.append(
                    {
                        "side": "front",
                        "net": column_net,
                        "points": [
                            lower_left_of_key(
                                lead_key, align_to_inner_track=column_index + 1
                            ),
                            calculate_point_for_angle(
                                lead_towards_mcu,
                                default_space_between_tracks * 5,
                                lead_key["switch"]["rotation"] + 90,
                            ),
                        ],
                    },
                )
                tracks.append(
                    {
                        "side": "back",
                        "net": column_net,
                        "points": [
                            calculate_point_for_angle(
                                lead_towards_mcu,
                                default_space_between_tracks * 5,
                                lead_key["switch"]["rotation"] + 90,
                            ),
                            lead_towards_mcu,
                        ],
                    },
                )
                vias.append(
                    {
                        "net": column_net,
                        "point": calculate_point_for_angle(
                            lead_towards_mcu,
                            default_space_between_tracks * 5,
                            lead_key["switch"]["rotation"] + 90,
                        ),
                    }
                )
                endpoints.append(
                    [
                        f"column-{config['number_of_columns'] - column_index + config['number_of_columns']}",
                        lead_towards_mcu,
                    ]
                )
            elif column_index == config["number_of_rows"]:
                column_index_lead_towards_mcu = mcu_pad_clearance + (
                    (
                        config["number_of_columns"]
                        - column_index
                        - 4
                        + (config["number_of_rows"] - 2)
                    )
                    * default_space_between_tracks
                )
                lead_towards_mcu = line_to_edge(
                    line=lower_edge_of_key(
                        lead_key, align_to_inner_track=column_index + 1
                    ),
                    edge=[
                        (
                            right_side_mcu_pads[0]["position"][0]
                            + column_index_lead_towards_mcu,
                            right_side_mcu_pads[0]["position"][1],
                        ),
                        (
                            right_side_mcu_pads[1]["position"][0]
                            + column_index_lead_towards_mcu,
                            right_side_mcu_pads[1]["position"][1],
                        ),
                    ],
                )
                tracks.append(
                    {
                        "side": "front",
                        "net": column_net,
                        "points": [
                            lower_left_of_key(
                                lead_key, align_to_inner_track=column_index + 1
                            ),
                            calculate_point_for_angle(
                                lead_towards_mcu,
                                default_space_between_tracks * 5,
                                lead_key["switch"]["rotation"] + 90,
                            ),
                        ],
                    },
                )
                tracks.append(
                    {
                        "side": "back",
                        "net": column_net,
                        "points": [
                            calculate_point_for_angle(
                                lead_towards_mcu,
                                default_space_between_tracks * 5,
                                lead_key["switch"]["rotation"] + 90,
                            ),
                            lead_towards_mcu,
                        ],
                    },
                )
                vias.append(
                    {
                        "net": column_net,
                        "point": calculate_point_for_angle(
                            lead_towards_mcu,
                            default_space_between_tracks * 5,
                            lead_key["switch"]["rotation"] + 90,
                        ),
                    }
                )
                endpoints.append(
                    [
                        f"column-{config['number_of_columns'] - column_index + config['number_of_columns']}",
                        lead_towards_mcu,
                    ]
                )

    return [tracks, from_pairs(endpoints), vias]


def mcu_to_matrix(
    left_side_mcu_pads,
    right_side_mcu_pads,
    left_side_thumb_key,
    right_side_thumb_key,
    left_side_rows,
    left_side_towards_mcu_endpoints,
    right_side_towards_mcu_endpoints,
    mcu_connector_endpoints,
    reset_switch_towards_center_endpoints,
):
    tracks = []
    vias = []

    connectors_to_mcu_endpoints = {
        **right_side_towards_mcu_endpoints,
        **left_side_towards_mcu_endpoints,
    }

    left_mcu_pad_12 = next(pad for pad in left_side_mcu_pads if pad["name"] == "12")[
        "position"
    ]
    right_mcu_pad_13 = next(pad for pad in right_side_mcu_pads if pad["name"] == "13")[
        "position"
    ]
    right_mcu_pad_22 = next(pad for pad in right_side_mcu_pads if pad["name"] == "22")[
        "position"
    ]
    right_mcu_pad_23 = next(pad for pad in right_side_mcu_pads if pad["name"] == "23")[
        "position"
    ]
    right_mcu_pad_24 = next(pad for pad in right_side_mcu_pads if pad["name"] == "24")[
        "position"
    ]
    left_mcu_pad_2 = next(pad for pad in left_side_mcu_pads if pad["name"] == "2")[
        "position"
    ]
    left_mcu_pad_1 = next(pad for pad in left_side_mcu_pads if pad["name"] == "1")[
        "position"
    ]
    left_mcu_pad_5 = next(pad for pad in left_side_mcu_pads if pad["name"] == "5")[
        "position"
    ]

    mcu_connector_endpoints = {
        **mcu_connector_endpoints,
        "13": right_mcu_pad_13,
        "12": left_mcu_pad_12,
    }

    reset_button_pad_1_point_towards_center = line_to_edge(
        line=[
            reset_switch_towards_center_endpoints[0],
            edge_from_point_at_angle(
                reset_switch_towards_center_endpoints[0],
                right_side_thumb_key["switch"]["rotation"] - 90,
            ),
        ],
        edge=[
            [right_mcu_pad_23[0] + mcu_pad_clearance, right_mcu_pad_23[1]],
            [right_mcu_pad_24[0] + mcu_pad_clearance, right_mcu_pad_24[1]],
        ],
    )
    tracks.append(
        {
            "side": "back",
            "net": "GND",
            "points": [
                reset_switch_towards_center_endpoints[0],
                reset_button_pad_1_point_towards_center,
                (reset_button_pad_1_point_towards_center[0], right_mcu_pad_23[1]),
                right_mcu_pad_23,
            ],
        },
    )
    offset_reset_button_pad_2_point_towards_center = (
        mcu_pad_clearance + default_space_between_tracks
    )
    reset_button_pad_2_point_towards_center = line_to_edge(
        line=[
            reset_switch_towards_center_endpoints[1],
            edge_from_point_at_angle(
                reset_switch_towards_center_endpoints[1],
                right_side_thumb_key["switch"]["rotation"] - 90,
            ),
        ],
        edge=[
            [
                right_mcu_pad_23[0] + offset_reset_button_pad_2_point_towards_center,
                right_mcu_pad_23[1],
            ],
            [
                right_mcu_pad_24[0] + offset_reset_button_pad_2_point_towards_center,
                right_mcu_pad_24[1],
            ],
        ],
    )
    tracks.append(
        {
            "side": "back",
            "net": "Net-(SW-RST1-Pad2)",
            "points": [
                reset_switch_towards_center_endpoints[1],
                reset_button_pad_2_point_towards_center,
                (reset_button_pad_2_point_towards_center[0], right_mcu_pad_22[1]),
                right_mcu_pad_22,
            ],
        },
    )

    point_towards_column_track_6 = line_to_edge(
        line=[
            mcu_connector_endpoints["6"],
            (
                mcu_connector_endpoints["6"][0],
                mcu_connector_endpoints["6"][1] + 1,
            ),
        ],
        edge=upper_edge_of_key(right_side_thumb_key),
    )
    vias.append(
        {
            "net": "/ROW1",
            "point": point_towards_column_track_6,
        }
    )
    tracks.append(
        {
            "side": "back",
            "net": "/ROW1",
            "points": [
                mcu_connector_endpoints["6"],
                point_towards_column_track_6,
            ],
        },
    )

    point_towards_column_track_7 = line_to_edge(
        line=[
            mcu_connector_endpoints["7"],
            (
                mcu_connector_endpoints["7"][0],
                mcu_connector_endpoints["7"][1] + 1,
            ),
        ],
        edge=upper_edge_of_key(right_side_thumb_key, align_to_pad_height="1"),
    )
    vias.append(
        {
            "net": "/ROW0",
            "point": point_towards_column_track_7,
        }
    )
    tracks.append(
        {
            "side": "back",
            "net": "/ROW0",
            "points": [
                mcu_connector_endpoints["7"],
                point_towards_column_track_7,
            ],
        },
    )

    mcu_connector_track_endpoint_14 = mcu_connector_endpoints["14"]
    tracks.append(
        {
            "side": "back",
            "net": "/COL6",
            "points": [
                mcu_connector_track_endpoint_14,
                midpoint(
                    lower_right_of_key(left_side_thumb_key, expand_by=4),
                    lower_left_of_key(right_side_thumb_key, expand_by=4),
                ),
            ],
        },
    )

    tracks.append(
        {
            "side": "front",
            "net": "/ROW4",
            "points": [
                left_mcu_pad_2,
                (left_mcu_pad_2[0] - mcu_pad_clearance, left_mcu_pad_2[1]),
            ],
        },
    )

    tracks.append(
        {
            "side": "back",
            "net": "/ROW3",
            "points": [
                left_mcu_pad_1,
                (
                    left_mcu_pad_1[0]
                    - mcu_pad_clearance
                    - default_space_between_tracks,
                    left_mcu_pad_1[1],
                ),
            ],
        },
    )
    vias.append(
        {
            "net": "/ROW3",
            "point": (
                left_mcu_pad_1[0] - mcu_pad_clearance - default_space_between_tracks,
                left_mcu_pad_1[1],
            ),
        }
    )

    tracks.append(
        {
            "side": "back",
            "net": "/COL7",
            "points": [
                right_mcu_pad_13,
                (right_mcu_pad_13[0] + mcu_pad_clearance, right_mcu_pad_13[1]),
                right_side_towards_mcu_endpoints["column-7"],
            ],
        },
    )

    tracks.append(
        {
            "side": "front",
            "net": "/COL8",
            "points": [
                left_mcu_pad_12,
                (
                    left_mcu_pad_12[0],
                    right_mcu_pad_13[1]
                    + mcu_pad_clearance
                    + (default_space_between_tracks * 2),
                ),
                (
                    right_side_towards_mcu_endpoints["column-8"][0],
                    right_mcu_pad_13[1]
                    + mcu_pad_clearance
                    + (default_space_between_tracks * 2),
                ),
            ],
        },
    )
    tracks.append(
        {
            "side": "back",
            "net": "/COL8",
            "points": [
                (
                    right_side_towards_mcu_endpoints["column-8"][0],
                    right_mcu_pad_13[1]
                    + mcu_pad_clearance
                    + (default_space_between_tracks * 2),
                ),
                right_side_towards_mcu_endpoints["column-8"],
            ],
        },
    )
    vias.append(
        {
            "net": "/COL8",
            "point": (
                right_side_towards_mcu_endpoints["column-8"][0],
                right_mcu_pad_13[1]
                + mcu_pad_clearance
                + (default_space_between_tracks * 2),
            ),
        }
    )

    point_towards_column_5 = (
        left_mcu_pad_5[0] - mcu_pad_clearance - (default_space_between_tracks * 2),
        left_mcu_pad_5[1],
    )
    tracks.append(
        {
            "side": "back",
            "net": "/ROW2",
            "points": [
                left_mcu_pad_5,
                point_towards_column_5,
            ],
        },
    )
    vias.append(
        {
            "net": "/ROW2",
            "point": point_towards_column_5,
        }
    )
    tracks.append(
        {
            "side": "front",
            "net": "/ROW2",
            "points": [
                point_towards_column_5,
                line_to_edge(
                    line=[
                        point_towards_column_5,
                        (point_towards_column_5[0], point_towards_column_5[1] + 1),
                    ],
                    edge=upper_edge_of_key(
                        left_side_rows[2][-1], align_to_pad_height="1"
                    ),
                ),
            ],
        },
    )

    mcu_pad_name_to_column_name = [
        ["11", "column-9"],
        ["10", "column-10"],
        ["9", "column-11"],
        ["8", "column-12"],
        ["20", "column-1"],
        ["19", "column-2"],
        ["18", "column-3"],
        ["17", "column-4"],
        ["16", "column-5"],
        ["15", "column-6"],
    ]

    # connect each track at the bottom of the mcu to the corresponding column
    for mcu_pad_name, column_name in mcu_pad_name_to_column_name:
        mcu_connector_endpoint = mcu_connector_endpoints[mcu_pad_name]
        column_endpoint = connectors_to_mcu_endpoints[column_name]
        tracks.append(
            {
                "side": "back",
                "net": mcu_pads_to_net_names[mcu_pad_name],
                "points": [
                    mcu_connector_endpoint,
                    (mcu_connector_endpoint[0], column_endpoint[1]),
                ],
            },
        )
        vias.append(
            {
                "net": mcu_pads_to_net_names[mcu_pad_name],
                "point": (mcu_connector_endpoint[0], column_endpoint[1]),
            }
        )
        tracks.append(
            {
                "side": "front",
                "net": mcu_pads_to_net_names[mcu_pad_name],
                "points": [
                    (mcu_connector_endpoint[0], column_endpoint[1]),
                    column_endpoint,
                ],
            },
        )

    return [tracks, vias]


def mcu_connectors(
    left_side_mcu_pads,
    right_side_mcu_pads,
    mirror_at_point,
):
    tracks = []
    endpoints = []
    vias = []

    left_column_x = left_side_mcu_pads[0]["position"][0]
    right_column_x = right_side_mcu_pads[0]["position"][0]
    last_row_y = left_side_mcu_pads[-1]["position"][1]

    left_mcu_pad_11 = next(pad for pad in left_side_mcu_pads if pad["name"] == "11")[
        "position"
    ]

    right_mcu_pad_14 = next(pad for pad in right_side_mcu_pads if pad["name"] == "14")[
        "position"
    ]

    right_mcu_pad_13 = next(pad for pad in right_side_mcu_pads if pad["name"] == "13")[
        "position"
    ]

    for index, pad_name in enumerate(left_pads_exiting_bottom):
        pad = next(pad for pad in left_side_mcu_pads if pad["name"] == pad_name)
        track_x_position = index * default_space_between_tracks
        left_offset_lead_points_x = right_column_x - track_x_position
        lead_point = (
            left_offset_lead_points_x - mcu_pad_clearance,
            pad["position"][1],
        )
        nudge_upwards_for_prettiness = 0.19
        lead_point_towards_bottom = (
            lead_point[0],
            last_row_y
            + mcu_pad_clearance
            + (default_space_between_tracks * 1)
            - nudge_upwards_for_prettiness
            - (index * default_space_between_tracks),
        )
        mcu_pad_net = f"{mcu_pads_to_net_names[pad_name]}"
        tracks.append(
            {
                "side": "front",
                "net": mcu_pad_net,
                "points": [
                    pad["position"],
                    (
                        pad["position"][0]
                        + mcu_pad_clearance
                        + (
                            default_space_between_tracks
                            * (len(left_pads_exiting_bottom) - index - 1)
                        ),
                        pad["position"][1],
                    ),
                    (
                        pad["position"][0]
                        + mcu_pad_clearance
                        + (
                            default_space_between_tracks
                            * (len(left_pads_exiting_bottom) - index - 1)
                        ),
                        left_mcu_pad_11[1]
                        - (
                            default_space_between_tracks
                            * (len(left_pads_exiting_bottom) - index + 0)
                        ),
                    ),
                    (
                        lead_point_towards_bottom[0],
                        left_mcu_pad_11[1]
                        - (
                            default_space_between_tracks
                            * (len(left_pads_exiting_bottom) - index + 0)
                        ),
                    ),
                    lead_point_towards_bottom,
                ],
            }
        )

        vias.append(
            {
                "net": mcu_pad_net,
                "point": lead_point_towards_bottom,
            }
        )
        endpoints.append([pad["name"], lead_point_towards_bottom])

    for index, pad_name in enumerate(right_pads_exiting_bottom):
        pad = next(pad for pad in right_side_mcu_pads if pad["name"] == pad_name)
        track_x_position = index * default_space_between_tracks
        left_offset_lead_points_x = left_column_x + track_x_position
        lead_point = (
            mcu_pad_clearance + left_offset_lead_points_x,
            pad["position"][1],
        )
        lead_point_towards_bottom = (
            lead_point[0],
            last_row_y + mcu_pad_clearance + default_space_between_tracks,
        )
        mcu_pad_net = f"{mcu_pads_to_net_names[pad_name]}"
        track_offset = -(
            default_space_between_tracks * (len(right_pads_exiting_bottom) - index)
        )
        previous_track_offset = -(
            default_space_between_tracks * (len(right_pads_exiting_bottom) - index - 1)
        )
        tracks.append(
            {
                "side": "back",
                "net": mcu_pad_net,
                "points": [
                    pad["position"],
                    (
                        pad["position"][0] - mcu_pad_clearance + previous_track_offset,
                        pad["position"][1],
                    ),
                    (
                        pad["position"][0] - mcu_pad_clearance + previous_track_offset,
                        right_mcu_pad_14[1] + track_offset,
                    ),
                    (lead_point_towards_bottom[0], right_mcu_pad_14[1] + track_offset),
                    lead_point_towards_bottom,
                ],
            }
        )

        endpoints.append([pad["name"], lead_point_towards_bottom])

    left_mcu_pad_towards_right_side = (
        right_mcu_pad_14[0]
        - mcu_pad_clearance
        - (default_space_between_tracks * len(left_pads_exiting_bottom)),
        right_mcu_pad_14[1],
    )

    left_mcu_pad_towards_bottom = (
        left_mcu_pad_towards_right_side[0],
        right_mcu_pad_13[1]
        - (default_space_between_tracks * 2)
        - nudge_upwards_for_prettiness,
    )

    tracks.append(
        {
            "side": "front",
            "net": "/COL9",
            "points": [
                left_mcu_pad_11,
                left_mcu_pad_towards_right_side,
                left_mcu_pad_towards_bottom,
            ],
        }
    )
    vias.append(
        {
            "net": "/COL9",
            "point": left_mcu_pad_towards_bottom,
        }
    )
    endpoints.append(["11", left_mcu_pad_towards_bottom])

    tracks.append(
        {
            "side": "back",
            "net": "GND",
            "points": [
                left_side_mcu_pads[2]["position"],
                left_side_mcu_pads[3]["position"],
            ],
        },
    )

    tracks.append(
        {
            "side": "back",
            "net": "GND",
            "points": [
                left_side_mcu_pads[3]["position"],
                (
                    right_side_mcu_pads[1]["position"][0] - mcu_pad_clearance,
                    left_side_mcu_pads[3]["position"][1],
                ),
                (
                    right_side_mcu_pads[1]["position"][0] - mcu_pad_clearance,
                    right_side_mcu_pads[1]["position"][1],
                ),
                right_side_mcu_pads[1]["position"],
            ],
        },
    )

    left_mcu_pad_11 = next(pad for pad in left_side_mcu_pads if pad["name"] == "11")[
        "position"
    ]
    right_mcu_pad_14 = next(pad for pad in right_side_mcu_pads if pad["name"] == "14")[
        "position"
    ]
    tracks.append(
        {
            "side": "back",
            "net": "/COL6",
            "points": [
                right_mcu_pad_14,
                midpoint(left_mcu_pad_11, right_mcu_pad_14),
            ],
        },
    )

    endpoints.append(["14", midpoint(left_mcu_pad_11, right_mcu_pad_14)])

    endpoints = from_pairs(endpoints)

    return [tracks, endpoints, vias]


def reset_switch_towards_center(reset_switch_pads, right_side_columns):
    tracks = []

    pad_1_connector_position = calculate_point_for_angle(
        reset_switch_pads["1"]["position"],
        min_length_of_connector + (default_space_between_tracks * 1),
        reset_switch_pads["1"]["rotation"],
    )

    tracks.append(
        {
            "side": "back",
            "net": "GND",
            "points": [
                reset_switch_pads["1"]["position"],
                pad_1_connector_position,
                calculate_point_for_angle(
                    pad_1_connector_position, 2, reset_switch_pads["1"]["rotation"] - 90
                ),
                line_to_edge(
                    line=[
                        pad_1_connector_position,
                        calculate_point_for_angle(
                            pad_1_connector_position,
                            1,
                            reset_switch_pads["1"]["rotation"] - 90,
                        ),
                    ],
                    edge=left_edge_of_key(right_side_columns[0][0]),
                ),
            ],
        },
    )

    pad_2_connector_position = calculate_point_for_angle(
        reset_switch_pads["2"]["position"],
        min_length_of_connector + (default_space_between_tracks * 2),
        reset_switch_pads["2"]["rotation"],
    )
    right_side_columns_first_row_first_key = right_side_columns[0][0]
    tracks.append(
        {
            "side": "back",
            "net": "Net-(SW-RST1-Pad2)",
            "points": [
                reset_switch_pads["2"]["position"],
                pad_2_connector_position,
                calculate_point_for_angle(
                    pad_2_connector_position, 2, reset_switch_pads["2"]["rotation"] - 90
                ),
                line_to_edge(
                    line=[
                        pad_2_connector_position,
                        calculate_point_for_angle(
                            pad_2_connector_position,
                            1,
                            reset_switch_pads["2"]["rotation"] - 90,
                        ),
                    ],
                    edge=left_edge_of_key(right_side_columns_first_row_first_key),
                ),
            ],
        },
    )

    endpoints = [track["points"][-1] for track in tracks]
    return [tracks, endpoints]

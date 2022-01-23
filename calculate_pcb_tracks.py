from zip import zip
from chunk import chunk
from reverse import reverse
from columns_to_rows import columns_to_rows
from tracks_with_points_to_tracks_with_lines import (
    tracks_with_points_to_tracks_with_lines,
)


def calculate_pcb_tracks(
    switches,
    diodes,
    switches_pads,
    diodes_pads,
    mcu_pads,
    reset_switch_pads,
    mirror_at_point,
    config,
    calculate_tracks,
):
    debug_points = []

    keys = [
        {
            "switch": {**switch, "pads": switch_pads},
            "diode": {**diode, "pads": diode_pads},
        }
        for switch, diode, switch_pads, diode_pads in zip(
            switches, diodes, switches_pads, diodes_pads
        )
    ]

    number_of_keys_per_side = config["number_of_columns"] * config["number_of_rows"]

    left_side_keys = keys[0:number_of_keys_per_side]

    right_side_keys = keys[-number_of_keys_per_side:]

    left_side_columns = chunk(config["number_of_rows"], left_side_keys)

    right_side_columns = chunk(config["number_of_rows"], right_side_keys)

    left_side_rows = columns_to_rows(left_side_columns)

    right_side_rows = columns_to_rows(right_side_columns)

    left_side_columns = chunk(config["number_of_rows"], left_side_keys)

    right_side_columns = chunk(config["number_of_rows"], right_side_keys)

    left_side_rows = columns_to_rows(left_side_columns)

    right_side_rows = columns_to_rows(right_side_columns)

    right_side_last_row = right_side_rows[-1]
    left_side_last_row = left_side_rows[-1]

    right_side_second_to_last_row = right_side_rows[-2]
    left_side_second_to_last_row = left_side_rows[-2]

    right_side_thumb_key = keys[-number_of_keys_per_side - 1]
    left_side_thumb_key = keys[number_of_keys_per_side]

    switches_to_columns_tracks = calculate_tracks.switches_to_columns(keys)

    number_of_pads_per_side = int(len(mcu_pads.keys()) / 2)

    left_side_mcu_pads = []
    for index in range(number_of_pads_per_side):
        left_side_mcu_pads.append(
            {
                "name": f"{index + 1}",
                "position": mcu_pads[f"{index + 1}"]["position"],
            }
        )

    right_side_mcu_pads = []
    for index in reverse(range(number_of_pads_per_side)):
        right_side_mcu_pads.append(
            {
                "name": f"{index + number_of_pads_per_side + 1}",
                "position": mcu_pads[f"{index + number_of_pads_per_side + 1}"][
                    "position"
                ],
            }
        )

    columns_tracks = calculate_tracks.calculate_columns_tracks(
        left_side_columns, right_side_columns, config
    )

    [
        mcu_connectors_tracks,
        mcu_connectors_endpoints,
        mcu_connectors_vias,
    ] = calculate_tracks.mcu_connectors(
        left_side_mcu_pads,
        right_side_mcu_pads,
        mirror_at_point,
    )

    left_side_row_tracks = calculate_tracks.left_side_rows(left_side_rows)
    right_side_row_tracks = calculate_tracks.right_side_rows(right_side_rows)

    switches_to_columns_for_thumb_keys_tracks = (
        calculate_tracks.switches_to_columns_for_thumb_keys(
            left_side_thumb_key,
            right_side_thumb_key,
            config,
        )
    )

    switch_rows_to_right_side_thumb_key_tracks = (
        calculate_tracks.switch_rows_to_right_side_thumb_key(
            left_side_last_row,
            right_side_last_row,
            left_side_thumb_key,
            right_side_thumb_key,
        )
    )

    switch_rows_to_left_side_thumb_key_tracks = (
        calculate_tracks.switch_rows_to_left_side_thumb_key(
            left_side_second_to_last_row,
            right_side_second_to_last_row,
            left_side_thumb_key,
            right_side_thumb_key,
            config,
        )
    )

    [
        right_side_column_towards_center_tracks,
        right_side_column_towards_center_vias,
    ] = calculate_tracks.right_side_columns_towards_center(right_side_rows, config)

    [
        left_side_column_towards_center_tracks,
        left_side_column_towards_center_vias,
    ] = calculate_tracks.left_side_columns_towards_center(left_side_rows, config)

    [
        left_side_towards_mcu_tracks,
        left_side_towards_mcu_endpoints,
        left_side_towards_mcu_vias,
    ] = calculate_tracks.left_side_towards_mcu(
        left_side_rows,
        left_side_mcu_pads,
        right_side_mcu_pads,
        mirror_at_point,
        config,
    )

    [
        right_side_towards_mcu_tracks,
        right_side_towards_mcu_endpoints,
        right_side_towards_mcu_vias,
    ] = calculate_tracks.right_side_towards_mcu(
        right_side_rows,
        right_side_mcu_pads,
        left_side_mcu_pads,
        mirror_at_point,
        config,
    )

    [
        reset_switch_towards_center_tracks,
        reset_switch_towards_center_endpoints,
    ] = calculate_tracks.reset_switch_towards_center(
        reset_switch_pads, right_side_columns
    )

    [mcu_to_matrix_tracks, mcu_to_matrix_vias] = calculate_tracks.mcu_to_matrix(
        left_side_mcu_pads,
        right_side_mcu_pads,
        left_side_thumb_key,
        right_side_thumb_key,
        left_side_rows,
        left_side_towards_mcu_endpoints,
        right_side_towards_mcu_endpoints,
        mcu_connectors_endpoints,
        reset_switch_towards_center_endpoints,
    )

    tracks = tracks_with_points_to_tracks_with_lines(
        [
            # Rows
            *left_side_row_tracks,
            *right_side_row_tracks,
            # Columns
            *columns_tracks,
            *switches_to_columns_tracks,
            *right_side_column_towards_center_tracks,
            *left_side_column_towards_center_tracks,
            # Thumb keys and lower rows
            *switches_to_columns_for_thumb_keys_tracks,
            *switch_rows_to_left_side_thumb_key_tracks,
            *switch_rows_to_right_side_thumb_key_tracks,
            # Rest switch
            *reset_switch_towards_center_tracks,
            # Last mile
            *left_side_towards_mcu_tracks,
            *right_side_towards_mcu_tracks,
            *mcu_connectors_tracks,
            *mcu_to_matrix_tracks,
        ]
    )

    vias = [
        *mcu_to_matrix_vias,
        *right_side_column_towards_center_vias,
        *left_side_column_towards_center_vias,
        *mcu_connectors_vias,
        *right_side_towards_mcu_vias,
        *left_side_towards_mcu_vias,
    ]

    return [tracks, vias, debug_points]

from flatten_list import flatten_list
from chunk import chunk
from reverse import reverse
from calculate_point_for_angle import calculate_point_for_angle
from flip_points_over_x_axis import flip_points_over_x_axis


def calculate_footprint_positions(case_geometry, number_of_thumb_keys, config):
    switches = []
    diodes = []

    number_of_keys_per_side = config["number_of_columns"] * config["number_of_rows"]

    left_side_positions = case_geometry["switch_positions"][
        number_of_keys_per_side
        + int(number_of_thumb_keys / 2) : -int(number_of_thumb_keys / 2)
    ]

    right_side_positions = case_geometry["switch_positions"][
        int(number_of_thumb_keys / 2) : -(
            number_of_keys_per_side + int(number_of_thumb_keys / 2)
        )
    ]

    # fix ordering on right side
    right_side_positions = flatten_list(
        [
            reverse(column)
            for column in chunk(
                config["number_of_rows"],
                right_side_positions,
            )
        ]
    )

    thumb_key_positions = [
        *case_geometry["switch_positions"][-int(number_of_thumb_keys / 2) :],
        *case_geometry["switch_positions"][0 : int(number_of_thumb_keys / 2)],
    ]

    positions = [
        *left_side_positions,
        *thumb_key_positions,
        *right_side_positions,
    ]

    for index, position in enumerate(flip_points_over_x_axis(positions)):
        rotation = (
            config["angle"]
            if position[0] > case_geometry["mirror_at"]["point"][0]
            else -config["angle"]
        )
        switches.append(
            {
                "position": position,
                "rotation": rotation,
                "reference": f"SW{index + 1}",
            }
        )

        diode_distance_from_switch_center = 7
        diode_position = calculate_point_for_angle(
            position, diode_distance_from_switch_center, rotation
        )
        diodes.append(
            {
                "position": diode_position,
                "rotation": rotation,
                "reference": f"D{index + 1}",
            }
        )
    return [switches, diodes]

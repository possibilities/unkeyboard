from midpoint import midpoint
from zip import zip
from flip_points_over_x_axis import flip_points_over_x_axis
from points_to_line import points_to_line


def calculate_pcb_outline(case_geometry, config):
    width_of_mcu_edge_cut = 14.80
    height_of_mcu_edge_cut = 47.75
    mcu_diagonal_cut_height = 21
    mcu_diagonal_cut_width = 23

    index_of_first_key_after_thumb_keys = 2 if config["has_two_thumb_keys"] else 1

    pcb_construction_outside_points = [
        case_geometry["switch_plate_outline"]["points"][2],
        case_geometry["switch_plate_outline"]["points"][
            (config["number_of_columns"] * 2) - 1
        ],
        case_geometry["switch_plate_outline"]["points"][
            (config["number_of_columns"] * 2)
        ],
        case_geometry["switch_plate_outline"]["points"][
            -(config["number_of_columns"] * 2) - 2
        ],
        case_geometry["switch_plate_outline"]["points"][
            -(config["number_of_columns"] * 2) - 1
        ],
        case_geometry["switch_plate_outline"]["points"][-4],
    ]

    pcb_construction_inside_points = [
        case_geometry["switch_plate"]["points"][index_of_first_key_after_thumb_keys][3],
        case_geometry["switch_plate"]["points"][
            index_of_first_key_after_thumb_keys
            + (config["number_of_columns"] * (config["number_of_rows"] - 1))
            + 1
        ][2],
        case_geometry["switch_plate"]["points"][
            index_of_first_key_after_thumb_keys
            + (config["number_of_columns"] * config["number_of_rows"])
            - 1
        ][1],
        case_geometry["switch_plate"]["points"][
            index_of_first_key_after_thumb_keys
            + (config["number_of_columns"] * config["number_of_rows"])
        ][0],
        case_geometry["switch_plate"]["points"][
            index_of_first_key_after_thumb_keys
            + ((config["number_of_columns"] + 1) * config["number_of_rows"])
            - 1
        ][3],
        case_geometry["switch_plate"]["points"][
            -index_of_first_key_after_thumb_keys - 1
        ][2],
    ]

    pcb_outline_points = [
        midpoint(pair[0], pair[1])
        for pair in zip(pcb_construction_inside_points, pcb_construction_outside_points)
    ]

    right_side_pcb_outline_points = pcb_outline_points[
        0 : int(len(pcb_outline_points) / 2)
    ]
    left_side_pcb_outline_points = pcb_outline_points[
        int(len(pcb_outline_points) / 2) :
    ]

    upper_left_pbc_outline_point = left_side_pcb_outline_points[0]
    upper_right_pbc_outline_point = right_side_pcb_outline_points[2]

    pcb_outline_points = [
        *right_side_pcb_outline_points,
        [
            (case_geometry["mirror_at"]["point"][0] + width_of_mcu_edge_cut / 2)
            + mcu_diagonal_cut_width,
            upper_right_pbc_outline_point[1],
        ],
        [
            case_geometry["mirror_at"]["point"][0] + width_of_mcu_edge_cut / 2,
            upper_right_pbc_outline_point[1] - mcu_diagonal_cut_height,
        ],
        [
            case_geometry["mirror_at"]["point"][0] + width_of_mcu_edge_cut / 2,
            upper_right_pbc_outline_point[1] - height_of_mcu_edge_cut,
        ],
        [
            case_geometry["mirror_at"]["point"][0] - width_of_mcu_edge_cut / 2,
            upper_left_pbc_outline_point[1] - height_of_mcu_edge_cut,
        ],
        [
            case_geometry["mirror_at"]["point"][0] - width_of_mcu_edge_cut / 2,
            upper_left_pbc_outline_point[1] - mcu_diagonal_cut_height,
        ],
        [
            (case_geometry["mirror_at"]["point"][0] - width_of_mcu_edge_cut / 2)
            - mcu_diagonal_cut_width,
            upper_left_pbc_outline_point[1],
        ],
        *left_side_pcb_outline_points,
    ]

    # Close polyline
    pcb_outline_points = [*pcb_outline_points, pcb_outline_points[0]]

    pcb_outline_points = flip_points_over_x_axis(pcb_outline_points)

    return points_to_line(pcb_outline_points)

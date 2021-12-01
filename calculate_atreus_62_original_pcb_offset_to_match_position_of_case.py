import kicad_script as pcb
from midpoint import midpoint
from flip_point_over_y_axis import flip_point_over_y_axis


def calculate_atreus_62_original_pcb_offset_to_match_position_of_case(
    case_geometry, atreus_62_board_data
):
    edge_cut_lines = list(
        filter(
            lambda line: pcb.get_value(line, "layer") == "Edge.Cuts",
            pcb.get_collection(atreus_62_board_data, "gr_line"),
        )
    )

    midpoint_of_pbc_for_x_offset = flip_point_over_y_axis(
        midpoint(
            pcb.get_values(edge_cut_lines[5], "start"),
            pcb.get_values(edge_cut_lines[14], "start"),
        )
    )

    switch_footprints = list(
        filter(
            lambda footprint: footprint[1] == "footprints:CHERRY_PCB_100H",
            pcb.get_collection(atreus_62_board_data, "footprint"),
        )
    )

    upper_right_hand_footprint = switch_footprints[-5]
    upper_right_hand_footprint_center = flip_point_over_y_axis(
        pcb.get_values(upper_right_hand_footprint, "at")[0:2]
    )

    number_of_keys = len(case_geometry["switch_plate"]["points"])
    upper_right_hand_switch_center = midpoint(
        case_geometry["switch_plate"]["points"][int(number_of_keys / 2) - 1][
            0
        ],
        case_geometry["switch_plate"]["points"][int(number_of_keys / 2) - 1][
            2
        ],
    )

    y_offset = (
        upper_right_hand_footprint_center[1]
        - upper_right_hand_switch_center[1]
    )

    x_offset = (
        midpoint_of_pbc_for_x_offset[0]
        - case_geometry["mirror_at"]["point"][0]
    )

    return [-x_offset, -y_offset]

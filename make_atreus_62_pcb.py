from make_pcb_parts import make_pcb_parts
from case import make_case_parts
from calculate_atreus_62_original_pcb_offset_to_match_position_of_case import (
    calculate_atreus_62_original_pcb_offset_to_match_position_of_case,
)
import kicad


def make_atreus_62_pcb():
    [case_parts, case_geometry] = make_case_parts()

    atreus_62_board_data = kicad.load_board(".", "atreus_62")
    atreus_62_parts = make_pcb_parts(atreus_62_board_data)

    pcb_offset_to_match_case = (
        calculate_atreus_62_original_pcb_offset_to_match_position_of_case(
            case_geometry, atreus_62_board_data
        )
    )

    parts = []
    for layer_name_part_and_options in atreus_62_parts:
        [layer_name, part, options] = layer_name_part_and_options
        parts.append(
            [
                "Atreus 62 " + layer_name,
                part.translate(pcb_offset_to_match_case),
                options,
            ]
        )
    return parts


if "show_object" in globals():
    for layer_name_part_and_options in make_atreus_62_pcb():
        [layer_name, part, options] = layer_name_part_and_options
        show_object(
            part,
            name="Atreus 62 " + layer_name,
            options=options,
        )

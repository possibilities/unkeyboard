from case import make_case_parts
import kicad_script as pcb
from pcb import make_pcb_parts
from explode_parts import explode_parts
from calculate_atreus_62_original_pcb_offset_to_match_position_of_case import (
    calculate_atreus_62_original_pcb_offset_to_match_position_of_case,
)


if "show_object" in globals():
    [case_parts, case_geometry] = make_case_parts()

    case_parts = explode_parts(case_parts, 25)

    for layer_name_part_and_options in case_parts:
        [layer_name, part, options] = layer_name_part_and_options
        show_object(part, name=layer_name, options=options)

    atreus_62_board_data = pcb.load_board(".", "atreus_62")
    atreus_62_pcb_parts = make_pcb_parts(atreus_62_board_data)

    pcb_offset_to_match_case = (
        calculate_atreus_62_original_pcb_offset_to_match_position_of_case(
            case_geometry, atreus_62_board_data
        )
    )

    pcb_z_offset_to_match_exploded_case = 70

    for layer_name_part_and_options in atreus_62_pcb_parts:
        [layer_name, part, options] = layer_name_part_and_options
        show_object(
            part.translate(
                [
                    *pcb_offset_to_match_case,
                    pcb_z_offset_to_match_exploded_case,
                ]
            ),
            name="Atreus 62 " + layer_name,
            options=options,
        )

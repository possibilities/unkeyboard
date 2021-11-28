from case import make_case_parts
import kicad_script as pcb
from pcb import make_pcb_parts
from explode_parts import explode_parts


if "show_object" in globals():
    [case_parts, case_geometry] = make_case_parts()

    atreus_62_board_data = pcb.load_board(".", "atreus_62")
    atreus_62_pcb_parts = make_pcb_parts(atreus_62_board_data)

    for layer_name_part_and_options in atreus_62_pcb_parts:
        [layer_name, part, options] = layer_name_part_and_options
        show_object(part, name="Atreus 62 " + layer_name, options=options)

    case_parts = explode_parts(case_parts, 25)

    for layer_name_part_and_options in case_parts:
        [layer_name, part, options] = layer_name_part_and_options
        show_object(part, name=layer_name, options=options)

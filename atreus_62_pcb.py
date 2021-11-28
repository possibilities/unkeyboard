import kicad_script as pcb
from pcb import make_pcb_parts

if "show_object" in globals():
    atreus_62_board_data = pcb.load_board(".", "atreus_62")
    atreus_62_parts = make_pcb_parts(atreus_62_board_data)

    for layer_name_part_and_options in atreus_62_parts:
        [layer_name, part, options] = layer_name_part_and_options
        show_object(part, name="Atreus 62 " + layer_name, options=options)

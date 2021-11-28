from case import make_case_parts
from pcb import load_pcb, make_pcb_parts
from explode_parts import explode_parts
from pcb import calculate_position_of_atreus_62_pcb


if "show_object" in globals():
    [case_parts, geometry] = make_case_parts()

    atreus_62_path = "./atreus_62.kicad_pcb"
    atreus_62_board_data = load_pcb(atreus_62_path)
    [atreus_62_pcb_parts, atreus_62_board_data] = make_pcb_parts(
        atreus_62_board_data
    )

    position_of_atreus_62_pcb = calculate_position_of_atreus_62_pcb(
        geometry, atreus_62_board_data
    )

    for layer_name_part_and_options in atreus_62_pcb_parts:
        [layer_name, part, options] = layer_name_part_and_options
        show_object(
            part.translate(position_of_atreus_62_pcb),
            name="Atreus 62 " + layer_name,
            options=options,
        )

    blank_pcb_path = "./blank.kicad_pcb"
    blank_board_data = load_pcb(blank_pcb_path)
    [pcb_parts, board_data] = make_pcb_parts(blank_board_data)

    case_parts = explode_parts(case_parts, 25)

    for layer_name_part_and_options in case_parts:
        [layer_name, part, options] = layer_name_part_and_options
        show_object(part, name=layer_name, options=options)

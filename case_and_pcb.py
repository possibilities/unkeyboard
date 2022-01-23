import os
from case import make_case_parts
from make_pcb_parts import make_pcb_parts
from explode_parts import explode_parts
from make_atreus_62_pcb import make_atreus_62_pcb
import kicad

explode_by = 25

if "show_object" in globals():
    [case_parts, case_geometry] = make_case_parts()

    case_parts = explode_parts(case_parts, explode_by)

    for layer_name_part_and_options in case_parts:
        [layer_name, part, options] = layer_name_part_and_options
        show_object(part, name=layer_name, options=options)

    board_data = kicad.load_board("data/pcb", "keyboard")
    pcb_parts = make_pcb_parts(board_data)

    for layer_name_part_and_options in pcb_parts:
        [layer_name, part, options] = layer_name_part_and_options
        show_object(
            part.translate([0, 0, explode_by * 2.8]),
            name=layer_name,
            options=options,
        )

    show_original_pcb = bool(os.getenv("SHOW_ORIGINAL_PCB"))

    if show_original_pcb:
        for layer_name_part_and_options in make_atreus_62_pcb():
            [layer_name, part, options] = layer_name_part_and_options
            show_object(
                part,
                name="Atreus 62 " + layer_name,
                options=options,
            )

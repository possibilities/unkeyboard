from keyboard import make_keyboard_parts
from read_and_show_kicad_pcb import make_pcb_parts
from explode_parts import explode_parts


if "show_object" in globals():
    keyboard_parts = make_keyboard_parts()
    pcb_parts = make_pcb_parts()

    keyboard_parts = explode_parts(keyboard_parts, 10)

    for layer_name_part_and_options in [*keyboard_parts, *pcb_parts]:
        [layer_name, part, options] = layer_name_part_and_options
        show_object(part, name=layer_name, options=options)

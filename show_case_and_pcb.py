from pprint import pprint
from keyboard import make_keyboard_parts
from show_kicad_pcb import make_pcb_parts
from explode_parts import explode_parts
from midpoint import midpoint


def calculate_position_of_pcb(board_data):
    edge_cut_lines = [
        line for line in board_data["gr_lines"] if line["layer"] == "Edge.Cuts"
    ]

    midpoint_of_pbc = midpoint(
        (edge_cut_lines[5]["start_x"], edge_cut_lines[5]["start_y"]),
        (edge_cut_lines[14]["start_x"], edge_cut_lines[14]["start_y"]),
    )

    switch_footprints = [
        footprint
        for footprint in board_data["footprints"]
        if "label" in footprint
        and footprint["label"] == "footprints:CHERRY_PCB_100H"
    ]
    upper_right_hand_footprint = switch_footprints[-5]
    upper_right_hand_footprint_center = (
        upper_right_hand_footprint["position_x"],
        upper_right_hand_footprint["position_y"],
    )

    y_offset = (
        upper_right_hand_footprint_center[1] - upper_right_hand_switch_center[1]
    )
    x_offset = midpoint_of_pbc[0] - geometry.mirror_at.point[0]

    return [-x_offset, -y_offset, 70]


if "show_object" in globals():
    [keyboard_parts, geometry] = make_keyboard_parts()

    upper_right_hand_switch_center = midpoint(
        geometry.switch_plate.points[-1][0],
        geometry.switch_plate.points[-1][2],
    )

    [pcb_parts, board_data] = make_pcb_parts()

    position_of_pcb = calculate_position_of_pcb(board_data)

    keyboard_parts = explode_parts(keyboard_parts, 25)

    for layer_name_part_and_options in keyboard_parts:
        [layer_name, part, options] = layer_name_part_and_options
        show_object(part, name=layer_name, options=options)

    for layer_name_part_and_options in pcb_parts:
        [layer_name, part, options] = layer_name_part_and_options
        show_object(
            part.translate(position_of_pcb),
            name=layer_name,
            options=options,
        )

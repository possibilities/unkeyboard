from pprint import pprint
from keyboard import make_keyboard_parts
from pcb import load_pcb, make_pcb_parts
from explode_parts import explode_parts
from midpoint import midpoint
from pcb import calculate_position_of_atreus_62_pcb


def calculate_position_of_atreus_62_pcb(geometry, board_data):
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

    upper_right_hand_switch_center = midpoint(
        geometry.switch_plate.points[-1][0],
        geometry.switch_plate.points[-1][2],
    )

    y_offset = (
        upper_right_hand_footprint_center[1] - upper_right_hand_switch_center[1]
    )
    x_offset = midpoint_of_pbc[0] - geometry.mirror_at.point[0]

    return [-x_offset, -y_offset, 70]


if "show_object" in globals():
    [keyboard_parts, geometry] = make_keyboard_parts()

    #     atreus_62_path = "./atreus_62.kicad_pcb"
    #     [atreus_62_pcb_parts, atreus_62_board_data] = make_pcb_parts(
    #         atreus_62_path
    #     )

    #     position_of_atreus_62_pcb = calculate_position_of_atreus_62_pcb(
    #         geometry,
    #         atreus_62_board_data
    #     )

    blank_pcb_path = "./blank.kicad_pcb"
    blank_board_data = load_pcb(blank_pcb_path)
    make_pcb_parts(blank_board_data)
    # [pcb_parts, board_data] = make_pcb_parts(blank_pcb_path)

    # keyboard_parts = explode_parts(keyboard_parts, 25)

    # for layer_name_part_and_options in keyboard_parts:
    #     [layer_name, part, options] = layer_name_part_and_options
    #     show_object(part, name=layer_name, options=options)

    # for layer_name_part_and_options in atreus_62_pcb_parts:
    #     [layer_name, part, options] = layer_name_part_and_options
    #     show_object(
    #         part.translate(position_of_atreus_62_pcb),
    #         name=layer_name,
    #         options=options,
    #     )

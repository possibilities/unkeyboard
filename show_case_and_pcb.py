from pprint import pprint
from keyboard import make_keyboard_parts
from read_and_show_kicad_pcb import make_pcb_parts
from explode_parts import explode_parts


def midpoint(p1, p2):
    return ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)


if "show_object" in globals():
    [keyboard_parts, geometry] = make_keyboard_parts()

    upper_right_hand_switch_center = midpoint(
        geometry.switch_plate.points[-1][0],
        geometry.switch_plate.points[-1][2],
    )

    [pcb_parts, board_data] = make_pcb_parts()
    pprint(board_data["footprints"][0])

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

    show_object(
        cq.Workplane()
        .moveTo(*upper_right_hand_footprint_center)
        .circle(1)
        .extrude(100)
        .moveTo(*upper_right_hand_switch_center)
        .circle(1)
        .extrude(100)
    )

    x_offset = (
        upper_right_hand_footprint_center[0] - upper_right_hand_switch_center[0]
    )

    y_offset = (
        upper_right_hand_footprint_center[1] - upper_right_hand_switch_center[1]
    )

    keyboard_parts = explode_parts(keyboard_parts, 10)

    for layer_name_part_and_options in keyboard_parts:
        [layer_name, part, options] = layer_name_part_and_options
        show_object(part, name=layer_name, options=options)

    for layer_name_part_and_options in pcb_parts:
        [layer_name, part, options] = layer_name_part_and_options
        show_object(
            part.translate([-x_offset, -y_offset, -10]),
            name=layer_name,
            options=options,
        )

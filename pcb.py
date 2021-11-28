import cadquery as cq
from fuse_parts import fuse_parts
from load_pcb import load_pcb
from cq_workplane_plugin import cq_workplane_plugin
from calculate_rectangle_corners import calculate_rectangle_corners
from case import make_case_parts
from midpoint import midpoint

pad_thickness = 0.075


def calculate_position_of_atreus_62_pcb(geometry, board_data):
    if "gr_lines" not in board_data:
        return [0, 0]

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
        upper_right_hand_footprint_center[1]
        - upper_right_hand_switch_center[1]
    )
    x_offset = midpoint_of_pbc[0] - geometry.mirror_at.point[0]

    return [-x_offset, -y_offset, 70]


def find_next_pcb_line(line, lines):
    for next_line in lines:
        if (
            next_line["start_y"] == line["end_y"]
            and next_line["start_x"] == line["end_x"]
        ):
            return next_line
    return None


def pcb_lines_to_polyline(lines):
    ordered_lines = [lines[0]]

    while True:
        next_line = find_next_pcb_line(ordered_lines[-1], lines[1:])
        if next_line:
            ordered_lines.append(next_line)
        else:
            break

    return [(line["start_x"], line["start_y"]) for line in ordered_lines]


def make_thru_hole_pads(board_data):
    if "footprints" not in board_data:
        return cq.Workplane()

    footprints = board_data["footprints"]
    thickness = board_data["general"]["thickness"]

    circular_positions = []
    for footprint in footprints:
        for pad in footprint["pads"]:
            if pad["type"] == "thru_hole" and pad["shape"] == "circle":
                circular_positions.append(pad)

    rectangular_positions = []
    for footprint in footprints:
        for pad in footprint["pads"]:
            if pad["type"] == "thru_hole" and pad["shape"] == "rect":
                rectangular_positions.append(pad)

    pads = cq.Workplane()

    if not len(circular_positions) and not len(rectangular_positions):
        return pads

    for position in circular_positions:
        pads = (
            pads.moveTo(position["position_x"], position["position_y"])
            .circle(position["drill"] / 2)
            .circle(position["size"][0] / 2)
        )

    for position in rectangular_positions:
        pads = (
            pads.moveTo(position["position_x"], position["position_y"])
            .circle(position["drill"] / 2)
            .rect(position["size"][0], position["size"][1])
        )

    return pads.extrude((pad_thickness * 2) + thickness).translate(
        [0, 0, -pad_thickness]
    )


def make_via_pads(board_data):
    pads = cq.Workplane()

    if "vias" not in board_data:
        return pads

    vias = board_data["vias"]
    thickness = board_data["general"]["thickness"]

    if not len(vias):
        return pads

    for via in vias:
        pads = (
            pads.moveTo(via["position_x"], via["position_y"])
            .circle(via["drill"] / 2)
            .circle(via["size"][0] / 2)
        )

    return pads.extrude(pad_thickness + thickness).translate(
        [0, 0, -pad_thickness / 2]
    )


def make_surface_mount_pads(board_data):
    if "footprints" not in board_data:
        return cq.Workplane()

    footprints = board_data["footprints"]
    positions = []
    for footprint in footprints:
        for pad in footprint["pads"]:
            if pad["type"] == "smd" and pad["shape"] == "rect":
                corners = calculate_rectangle_corners(
                    (pad["position_x"], pad["position_y"]),
                    pad["size"][0],
                    pad["size"][1],
                    angle=pad["rotation"],
                )
                positions.append(
                    corners,
                )

    pads = cq.Workplane()

    if not len(positions):
        return pads

    for position in positions:
        pads = pads.polyline(position).close()

    return pads.extrude(pad_thickness * 2).translate([0, 0, -pad_thickness])


@cq_workplane_plugin
def drill_holes_for_thru_hole_pads(self, footprints, thickness):
    circular_holes_by_size = {}
    rectangular_holes_by_size = {}

    for footprint in footprints:
        for pad in footprint["pads"]:
            if pad["type"] in ["thru_hole", "np_thru_hole"]:
                if pad["shape"] == "circle":
                    if pad["size"][0] not in circular_holes_by_size:
                        circular_holes_by_size[pad["size"][0]] = []
                    circular_holes_by_size[pad["size"][0]].append(
                        (pad["position_x"], pad["position_y"])
                    )
                elif pad["shape"] == "rect":
                    if pad["size"][0] not in rectangular_holes_by_size:
                        rectangular_holes_by_size[pad["size"][0]] = []
                    rectangular_holes_by_size[pad["size"][0]].append(
                        (pad["position_x"], pad["position_y"])
                    )

    for size, positions in circular_holes_by_size.items():
        self = (
            self.faces("front")
            .pushPoints(positions)
            .circle(size / 2)
            .cutBlind(thickness)
        )

    for size, positions in rectangular_holes_by_size.items():
        self = (
            self.faces("front")
            .pushPoints(positions)
            .rect(size, size)
            .cutBlind(thickness)
        )

    return self


@cq_workplane_plugin
def drill_holes_for_vias(self, vias, thickness):
    holes_by_size = {}

    for via in vias:
        if via["drill"] not in holes_by_size:
            holes_by_size[via["drill"]] = []
        holes_by_size[via["drill"]].append(
            (via["position_x"], via["position_y"])
        )

    for size, positions in holes_by_size.items():
        self = (
            self.faces("front")
            .pushPoints(positions)
            .circle(size / 2)
            .cutBlind(thickness)
        )

    return self


def make_board(board_data):
    if "gr_lines" not in board_data:
        return cq.Workplane()

    edge_cut_lines = [
        line for line in board_data["gr_lines"] if line["layer"] == "Edge.Cuts"
    ]

    board = (
        cq.Workplane()
        .polyline(pcb_lines_to_polyline(edge_cut_lines))
        .close()
        .extrude(board_data["general"]["thickness"])
    )

    if "footprints" in board_data:
        board = board.drill_holes_for_thru_hole_pads(
            board_data["footprints"], board_data["general"]["thickness"]
        )

    if "vias" in board_data:
        board = board.drill_holes_for_vias(
            board_data["vias"], board_data["general"]["thickness"]
        )

    return board


def make_footprint_lines(board_data, layer):
    if "footprints" not in board_data:
        return cq.Workplane()

    footprints = board_data["footprints"]

    footprint_lines = []

    for footprint in footprints:
        layer_lines = [
            line for line in footprint["fp_lines"] if line["layer"] == layer
        ]
        footprint_lines = [*footprint_lines, *layer_lines]

    if not len(footprint_lines):
        return cq.Workplane()

    lines = []
    for footprint_line in footprint_lines:
        line = cq.Workplane()
        line = line.moveTo(
            footprint_line["start_x"], footprint_line["start_y"]
        ).lineTo(footprint_line["end_x"], footprint_line["end_y"])
        lines.append(line)

    return fuse_parts(lines).translate(
        [
            0,
            0,
            board_data["general"]["thickness"]
            if layer.startswith("F.")
            else 0,
        ]
    )


def make_segments(board_data, layer):
    if "segments" not in board_data:
        return cq.Workplane()

    board_segments = board_data["segments"]

    layer_segments = [
        segment for segment in board_segments if segment["layer"] == layer
    ]

    lines = []

    for layer_segment in layer_segments:
        segment = cq.Workplane()
        segment = segment.moveTo(
            layer_segment["start_x"], layer_segment["start_y"]
        ).lineTo(layer_segment["end_x"], layer_segment["end_y"])
        lines.append(segment)

    return fuse_parts(lines).translate(
        [
            0,
            0,
            board_data["general"]["thickness"]
            if layer.startswith("F.")
            else 0,
        ]
    )


def make_pcb_parts(board_data):
    board = make_board(board_data)

    pad_yellow = (204, 204, 0)

    parts = []

    thru_hole_pads = make_thru_hole_pads(board_data)
    via_pads = make_via_pads(board_data)
    surface_mount_pads = make_surface_mount_pads(board_data)

    front_silkscreens = make_footprint_lines(board_data, "F.SilkS")
    back_silkscreens = make_footprint_lines(board_data, "B.SilkS")
    front_segments = make_segments(board_data, "F.Cu")
    back_segments = make_segments(board_data, "B.Cu")

    parts.append(("PCB board", board, {"color": (0, 51, 25), "alpha": 0}))
    parts.append(("PCB thru hold pads", thru_hole_pads, {"color": pad_yellow}))
    parts.append(("PCB via pads", via_pads, {"color": pad_yellow}))
    parts.append(
        (
            "PCB surface mount pads",
            surface_mount_pads,
            {"color": pad_yellow},
        )
    )
    parts.append(
        ("PCB front silkscreens", front_silkscreens, {"color": "white"})
    )
    parts.append(
        ("PCB back silkscreens", back_silkscreens, {"color": "white"})
    )
    parts.append(("PCB front segments", front_segments, {"color": "red"}))
    parts.append(("PCB back segments", back_segments, {"color": "blue"}))

    return [parts, board_data]


def polyline_to_pcb_line(polyline_points):
    pcb_lines = []
    for index, polyline_point in enumerate(polyline_points):
        is_last_line = index < len(polyline_points) - 1
        pcb_lines.append(
            (
                polyline_point,
                polyline_points[index + 1]
                if is_last_line
                else polyline_points[0],
            )
        )
    return pcb_lines


if "show_object" in globals():
    [case_parts, case_geometry] = make_case_parts()

    atreus_62_path = "./atreus_62.kicad_pcb"
    atreus_62_board_data = load_pcb(atreus_62_path)
    [atreus_62_pcb_parts, atreus_62_board_data] = make_pcb_parts(
        atreus_62_board_data
    )

    position_of_atreus_62_pcb = calculate_position_of_atreus_62_pcb(
        case_geometry, atreus_62_board_data
    )

    for layer_name_part_and_options in atreus_62_pcb_parts:
        [layer_name, part, options] = layer_name_part_and_options
        show_object(
            part.translate(position_of_atreus_62_pcb),
            name="Atreus 62 " + layer_name,
            options=options,
        )

    blank_path = "./blank.kicad_pcb"
    blank_board_data = load_pcb(blank_path)

    [pcb_parts, board_data] = make_pcb_parts(blank_board_data)

    for layer_name_part_and_options in pcb_parts:
        [layer_name, part, options] = layer_name_part_and_options
        show_object(
            part.translate([0, 0, -20]), name=layer_name, options=options
        )

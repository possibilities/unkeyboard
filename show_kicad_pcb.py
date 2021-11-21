import cadquery as cq
from pprint import pprint
import os
import sys
import inspect
from fuse_parts import fuse_parts
from load_kicad_pcb import load_kicad_pcb
from cq_workplane_plugin import cq_workplane_plugin
from calculate_rectangle_corners import calculate_rectangle_corners

pad_thickness = 0.075


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
    vias = board_data["vias"]
    thickness = board_data["general"]["thickness"]

    pads = cq.Workplane()
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
    footprints = board_data["footprints"]
    thickness = board_data["general"]["thickness"]
    positions = []
    for footprint in footprints:
        for pad in footprint["pads"]:
            if pad["type"] == "smd" and pad["shape"] == "rect":
                corners = calculate_rectangle_corners(
                    (pad["position_x"], pad["position_y"]),
                    pad["size"][0],
                    pad["size"][1],
                    angle=pad["position_rotate"],
                )
                positions.append(
                    corners,
                )

    pads = cq.Workplane()

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
                    if not pad["size"][0] in circular_holes_by_size:
                        circular_holes_by_size[pad["size"][0]] = []
                    circular_holes_by_size[pad["size"][0]].append(
                        (pad["position_x"], pad["position_y"])
                    )
                elif pad["shape"] == "rect":
                    if not pad["size"][0] in rectangular_holes_by_size:
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
        if not via["drill"] in holes_by_size:
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
    edge_cut_lines = [
        line for line in board_data["gr_lines"] if line["layer"] == "Edge.Cuts"
    ]

    board = (
        cq.Workplane()
        .polyline(pcb_lines_to_polyline(edge_cut_lines))
        .close()
        .extrude(board_data["general"]["thickness"])
        .drill_holes_for_thru_hole_pads(
            board_data["footprints"], board_data["general"]["thickness"]
        )
        .drill_holes_for_vias(
            board_data["vias"], board_data["general"]["thickness"]
        )
    )

    return board


def make_footprint_lines(board_data, layer):
    footprints = board_data["footprints"]

    footprint_lines = []

    for footprint in footprints:
        layer_lines = [
            line for line in footprint["fp_lines"] if line["layer"] == layer
        ]
        footprint_lines = [*footprint_lines, *layer_lines]

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
            board_data["general"]["thickness"] if layer.startswith("F.") else 0,
        ]
    )


def make_segments(board_data, layer):
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
            board_data["general"]["thickness"] if layer.startswith("F.") else 0,
        ]
    )


def make_pcb_parts():
    board_data = load_kicad_pcb(
        "/home/mike/src/atreus62/pcb/Atreus62.kicad_pcb"
    )

    parts = []

    board = make_board(board_data)

    thru_hole_pads = make_thru_hole_pads(board_data)
    via_pads = make_via_pads(board_data)
    surface_mount_pads = make_surface_mount_pads(board_data)

    front_silkscreens = make_footprint_lines(board_data, "F.SilkS")
    back_silkscreens = make_footprint_lines(board_data, "B.SilkS")
    front_segments = make_segments(board_data, "F.Cu")
    back_segments = make_segments(board_data, "B.Cu")

    pad_yellow = (204, 204, 0)

    parts.append(("Board", board, {"color": (0, 51, 25), "alpha": 0}))
    parts.append(("Thru hold pads", thru_hole_pads, {"color": pad_yellow}))
    parts.append(("Via pads", via_pads, {"color": pad_yellow}))
    parts.append(
        ("Surface mount pads", surface_mount_pads, {"color": pad_yellow})
    )
    parts.append(("Front silkscreens", front_silkscreens, {"color": "white"}))
    parts.append(("Back silkscreens", back_silkscreens, {"color": "white"}))
    parts.append(("Front segments", front_segments, {"color": "red"}))
    parts.append(("Back segments", back_segments, {"color": "blue"}))

    return [parts, board_data]


if "show_object" in globals():
    [pcb_parts, board_data] = make_pcb_parts()

    for layer_name_part_and_options in pcb_parts:
        [layer_name, part, options] = layer_name_part_and_options
        show_object(part, name=layer_name, options=options)

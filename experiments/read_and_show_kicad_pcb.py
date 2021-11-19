import cadquery as cq
from pprint import pprint
import os
import sys
import inspect

pad_thickness = 0.075
via_channel_thickness = 0.08

currentdir = os.path.dirname(
    os.path.abspath(inspect.getfile(inspect.currentframe()))
)
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

from load_pcb import load_pcb
from cq_workplane_plugin import cq_workplane_plugin
from calculate_rectangle_corners import calculate_rectangle_corners


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


def make_via_pads(vias, thickness):
    pads = cq.Workplane()
    for via in vias:
        pads = (
            pads.moveTo(via["position_x"], via["position_y"])
            .circle(via["drill"] / 2)
            .circle((via["drill"] - via_channel_thickness) / 2)
        )
    return pads.extrude(thickness)


def make_thru_hole_pads(footprints, thickness):
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
    return pads.extrude(-pad_thickness)


def make_surface_mount_pads(footprints, thickness):
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
    return pads.extrude(-pad_thickness)


@cq_workplane_plugin
def drill_holes_for_thru_hole_pads(self, footprints, thickness):
    holes_by_size = {}

    for footprint in footprints:
        for pad in footprint["pads"]:
            if pad["type"] in ["thru_hole", "np_thru_hole"]:
                if not pad["drill"] in holes_by_size:
                    holes_by_size[pad["drill"]] = []
                holes_by_size[pad["drill"]].append(
                    (pad["position_x"], pad["position_y"])
                )

    for size, positions in holes_by_size.items():
        self = (
            self.faces("front")
            .pushPoints(positions)
            .circle(size / 2)
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


board_data = load_pcb("/home/mike/src/atreus62/pcb/Atreus62.kicad_pcb")

board = make_board(board_data)

thru_hole_pads = make_thru_hole_pads(
    board_data["footprints"], board_data["general"]["thickness"]
)

via_pads = make_via_pads(board_data["vias"], board_data["general"]["thickness"])

surface_mount_pads = make_surface_mount_pads(
    board_data["footprints"], board_data["general"]["thickness"]
)

if "show_object" in globals():
    show_object(board, options={"color": (0, 51, 25)})
    show_object(via_pads, options={"color": (204, 204, 0)})
    show_object(thru_hole_pads, options={"color": (204, 204, 0)})
    show_object(surface_mount_pads, options={"color": (204, 204, 0)})

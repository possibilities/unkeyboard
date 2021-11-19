import cadquery as cq
from pprint import pprint
import os
import sys
import inspect

currentdir = os.path.dirname(
    os.path.abspath(inspect.getfile(inspect.currentframe()))
)
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

from load_pcb import load_pcb
from cq_workplane_plugin import cq_workplane_plugin

board = load_pcb("/home/mike/src/atreus62/pcb/Atreus62.kicad_pcb")


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


edge_cut_lines = [
    line for line in board["gr_lines"] if line["layer"] == "Edge.Cuts"
]


@cq_workplane_plugin
def add_thru_hole_pads(self, footprints, vias, thickness):
    return self


@cq_workplane_plugin
def drill_holes(self, footprints, vias, thickness):
    holes_by_size = {}

    for footprint in footprints:
        for pad in footprint["pads"]:
            if "drill" in pad:
                if not pad["drill"] in holes_by_size:
                    holes_by_size[pad["drill"]] = []
                holes_by_size[pad["drill"]].append(
                    (pad["position_x"], pad["position_y"])
                )

    for via in vias:
        if "drill" in via:
            if not via["drill"] in holes_by_size:
                holes_by_size[via["drill"]] = []
            holes_by_size[via["drill"]].append(
                (via["position_x"], via["position_y"])
            )
            pprint(holes_by_size)

    for size, positions in holes_by_size.items():
        self = (
            self.faces("front")
            .pushPoints(positions)
            .circle(size / 2)
            .cutBlind(thickness)
        )

    return self


@cq_workplane_plugin
def drill_holes_for_vias(self, vias):
    return self


result = (
    cq.Workplane()
    .polyline(pcb_lines_to_polyline(edge_cut_lines))
    .close()
    .extrude(board["general"]["thickness"])
    .drill_holes(
        board["footprints"], board["vias"], board["general"]["thickness"]
    )
    .add_thru_hole_pads(
        board["footprints"], board["vias"], board["general"]["thickness"]
    )
)

if "show_object" in globals():
    show_object(result)

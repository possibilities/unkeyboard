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


result = (
    cq.Workplane()
    .polyline(pcb_lines_to_polyline(edge_cut_lines))
    .close()
    .extrude(board["general"]["thickness"])
)

# for footprint in board["footprints"]:
#     for pad in footprint["pads"]:
#         position = (
#             pad["position_x"],
#             pad["position_y"],
#         )
#         result = result.moveTo(*position).circle(0.25).extrude(100)

# if "show_object" in globals():
#     show_object(result)

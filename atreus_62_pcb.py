import cadquery as cq
from pprint import pprint
import os
import sys
import inspect
from fuse_parts import fuse_parts
from load_pcb import load_pcb
from cq_workplane_plugin import cq_workplane_plugin
from pcb import make_pcb_parts
from calculate_rectangle_corners import calculate_rectangle_corners


if "show_object" in globals():
    atreus_path = "./atreus_62.kicad_pcb"
    atreus_board_data = load_pcb(atreus_path)
    [atreus_62_pcb_parts, atreus_62_board_data] = make_pcb_parts(
        atreus_board_data
    )

    for layer_name_part_and_options in atreus_62_pcb_parts:
        [layer_name, part, options] = layer_name_part_and_options
        show_object(part, name=layer_name, options=options)

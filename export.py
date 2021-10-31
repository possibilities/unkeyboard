import os
from export_to_dxf_layers import export_to_dxf_layers
from keyboard import make_keyboard_parts

keyboard_parts = make_keyboard_parts()
export_to_dxf_layers(keyboard_parts, "./data/keyboard.dxf")

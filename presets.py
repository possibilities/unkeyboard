default_config = {
    # Configurable
    "has_thicc_spacer": False,
    "use_chicago_bolt": True,
    "has_two_thumb_keys": False,
    "angle": 10,
    "number_of_rows": 5,
    "number_of_columns": 6,
    "stagger_percent_for_single_thumb_key": 8.5,
    "stagger_percent_for_double_thumb_keys": 3.98,
    "column_stagger_percents": (-1, 4, 10, 5, 2, 2),
    # Structural
    "base_layer_thickness": 3,
    "inside_frame_size": 2.1,
    "outside_frame_size_for_chicago_bolt": 20,
    "outside_frame_size_for_regular_screw": 16,
    "screw_hole_radius_for_chicago_bolt": 2.5,
    "screw_hole_radius_for_regular_screw": 1.5,
    "distance_between_switch_centers": 19,
    "usb_cutout_width": 4,
    "top_inside_screw_distance_from_usb": 5.50,
}

presets = {
    "default": default_config,
    "atreus_62": default_config,
    "atreus_42": {
        **default_config,
        "number_of_rows": 4,
        "number_of_columns": 5,
    },
    "atreus_44": {
        **default_config,
        "number_of_rows": 4,
        "number_of_columns": 5,
        "has_two_thumb_keys": True,
    },
}

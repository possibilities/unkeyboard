from types import SimpleNamespace

default_config = SimpleNamespace(
    # Configurable
    has_thicc_spacer=False,
    use_chicago_bolt=True,
    has_two_inside_switches=False,
    angle=10,
    number_of_rows=5,
    number_of_columns=6,
    stagger_percent_for_single_inside_switch=8.5,
    stagger_percent_for_double_inside_switches=3.98,
    column_stagger_percents=(-1, 4, 10, 5, 2, 2),
    # Structural
    base_layer_thickness=3,
    inside_frame_size=2.1,
    outside_frame_size_for_chicago_bolt=20,
    outside_frame_size_for_regular_screw=16,
    screw_hole_radius_for_chicago_bolt=2.5,
    screw_hole_radius_for_regular_screw=1.5,
    switch_plate_cutout_size=13.97,
    distance_between_switch_centers=19,
    usb_cutout_width=4,
    top_inside_screw_distance_from_usb=5.50,
)

presets = SimpleNamespace(
    default=default_config.__dict__,
    atreus_62=default_config.__dict__,
    atreus_42={
        **default_config.__dict__,
        **SimpleNamespace(
            number_of_rows=4,
            number_of_columns=5,
        ).__dict__,
    },
    atreus_44={
        **default_config.__dict__,
        **SimpleNamespace(
            number_of_rows=4,
            number_of_columns=5,
            has_two_inside_switches=True,
        ).__dict__,
    },
)

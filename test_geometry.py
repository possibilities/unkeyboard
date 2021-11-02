import pytest
from keyboard import presets
from keyboard import calculate_case_geometry_and_make_switch_plate_inner
from types import SimpleNamespace


def build_data_matrix(list_1, list_2):
    data = []
    for item_1 in list_1:
        for item_2 in list_2:
            data.append((item_1, item_2))
    return data


test_data = build_data_matrix(
    presets.__dict__.keys(),
    [
        "usb_rect",
        "screws",
        "reset_button",
        "case_outer",
        "spacer_inner",
        "thickness",
        "spacer_thickness",
    ],
)


@pytest.mark.parametrize("preset_name,geometry_name", test_data)
def test_geometry_usb_rect(preset_name, geometry_name, snapshot):
    preset = presets.__dict__[preset_name]
    [
        geometry,
        switch_plate_inner,
    ] = calculate_case_geometry_and_make_switch_plate_inner(
        SimpleNamespace(**preset)
    )

    assert geometry.__dict__[geometry_name] == snapshot

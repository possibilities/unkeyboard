import pytest
from presets import presets
from keyboard import calculate_case_geometry
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
        "screws",
        "reset_button",
        "case_outer",
        "spacer",
        "spacer_thickness",
        "thickness",
        "switch_outline",
        "switch_cutouts",
        "mirror_base_point",
    ],
)


@pytest.mark.parametrize("preset_name,geometry_name", test_data)
def test_geometry(preset_name, geometry_name, snapshot):
    preset = presets.__dict__[preset_name]

    geometry = calculate_case_geometry(SimpleNamespace(**preset))

    assert geometry.__dict__[geometry_name] == snapshot

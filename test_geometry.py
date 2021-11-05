import pytest
import itertools
from presets import presets
from keyboard import calculate_case_geometry
from types import SimpleNamespace


geometry_keys = [
    "screws",
    "reset_button",
    "case_outer",
    "spacer",
    "switch_outline",
    "top_plate",
    "bottom_plate",
    "switch_plate",
    "switch_cutouts",
    "mirror_at",
]

test_data = itertools.product(presets.__dict__.keys(), geometry_keys)


def assert_all_geometry_under_test(geometry):
    if len(geometry.__dict__.keys()) != len(geometry_keys):
        assert (
            False
        ), "When adding a new key to geometry it must also be added in `test_geometry.py`."


@pytest.mark.parametrize("preset_name,geometry_name", test_data)
def test_geometry(preset_name, geometry_name, snapshot):
    preset = presets.__dict__[preset_name]

    geometry = calculate_case_geometry(SimpleNamespace(**preset))

    assert_all_geometry_under_test(geometry)

    assert geometry.__dict__[geometry_name] == snapshot

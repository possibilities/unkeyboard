from pprint import pprint
from snapshottest import TestCase
from types import SimpleNamespace
from keyboard import default_config
from keyboard import calculate_case_geometry_and_make_switch_plate_inner

atreus_42_preset = SimpleNamespace(
    **{
        **{"number_of_rows": 4, "number_of_columns": 5},
        **default_config.__dict__,
    },
)

atreus_44_preset = SimpleNamespace(
    **{
        **{
            "number_of_rows": 4,
            "number_of_columns": 5,
            "has_double_inner_keys": True,
        },
        **default_config.__dict__,
    },
)


class TestGeometry(TestCase):
    def test_geometry_atreus_64(self):
        [
            geometry,
            switch_plate_inner,
        ] = calculate_case_geometry_and_make_switch_plate_inner(default_config)

        for (key, val) in geometry.__dict__.items():
            self.assertMatchSnapshot([val], "atreus 64 %s" % (key))

    def test_geometry_atreus_42(self):
        [
            geometry,
            switch_plate_inner,
        ] = calculate_case_geometry_and_make_switch_plate_inner(
            atreus_42_preset
        )

        for (key, val) in geometry.__dict__.items():
            self.assertMatchSnapshot([val], "atreus 42 %s" % (key))

    def test_geometry_atreus_44(self):
        [
            geometry,
            switch_plate_inner,
        ] = calculate_case_geometry_and_make_switch_plate_inner(
            atreus_44_preset
        )

        for (key, val) in geometry.__dict__.items():
            self.assertMatchSnapshot([val], "atreus 44 %s" % (key))

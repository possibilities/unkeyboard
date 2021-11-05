from types import SimpleNamespace
from keyboard import default_config

presets = SimpleNamespace(
    **{
        "atreus_62": default_config.__dict__,
        "atreus_42": {
            **default_config.__dict__,
            **{"number_of_rows": 4, "number_of_columns": 5},
        },
        "atreus_44": {
            **default_config.__dict__,
            **{
                "number_of_rows": 4,
                "number_of_columns": 5,
                "has_double_inner_keys": True,
            },
        },
    }
)

import config
from fuse_parts import fuse_parts
from key_position import key_position


def make_keys(key, side_of_board):
    keys = []

    total_key_width = config.key_length * config.number_of_rows
    total_key_length = config.key_length * config.number_of_columns

    for x in range(config.number_of_columns):
        for y in range(config.number_of_rows):
            keys.append(
                key.translate(
                    key_position(x, y, config.number_of_columns, side_of_board)
                ).translate(
                    (
                        -total_key_length if side_of_board == "right" else 0,
                        -total_key_width / 2,
                    )
                )
            )

    return fuse_parts(keys)

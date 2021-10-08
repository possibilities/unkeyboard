import config


def stagger_offset_for_column(x, number_of_columns, side_of_board):
    if config.stagger == None:
        return 0

    # Light stagger, TODO parameterize
    if side_of_board == "right":
        if x == config.number_of_columns - 4:
            return 0.1 * config.key_length
        if x == config.number_of_columns - 3:
            return 0.2 * config.key_length
        if x == config.number_of_columns - 2:
            return 0.1 * config.key_length
    if side_of_board == "left":
        if x == 3:
            return 0.1 * config.key_length
        if x == 2:
            return 0.2 * config.key_length
        if x == 1:
            return 0.1 * config.key_length
    return 0


def key_position(x, y, number_of_columns, side_of_board):
    x_center_of_workplane_offset = config.key_length / 2
    y_center_of_workplane_offset = config.key_length / 2

    key_x = x * config.key_length + x_center_of_workplane_offset
    key_y = (
        y * config.key_width
        + stagger_offset_for_column(x, config.number_of_columns, side_of_board)
        + y_center_of_workplane_offset
    )

    return (key_x, key_y, 0)

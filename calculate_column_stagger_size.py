def calculate_column_stagger_size(column, config):
    thumb_keys_stagger_percent = (
        config["stagger_percent_for_double_thumb_keys"]
        if config["has_two_thumb_keys"]
        else config["stagger_percent_for_single_thumb_key"]
    )

    return (
        thumb_keys_stagger_percent
        if column == 0
        else config["column_stagger_percents"][column - 1]
    ) / config["distance_between_switch_centers"]

from get_item_at_index import get_item_at_index


def lower_point_precision(point):
    return (round(point[0], 12), round(point[1], 12))


def dedupe_points(points):
    deduped = []
    for index, point in enumerate(points):
        previous_item = get_item_at_index(points, index - 1)
        if not (
            previous_item
            and (
                lower_point_precision(previous_item)[0]
                == lower_point_precision(point)[0]
                and lower_point_precision(previous_item)[1]
                == lower_point_precision(point)[1]
            )
        ):
            deduped.append(point)
    return deduped

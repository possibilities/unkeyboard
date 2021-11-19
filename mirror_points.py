from mirror_point import mirror_point


def mirror_points(points, mirror_at_point, combine=True, axis="Y"):
    mirrored_points = [
        mirror_point(point, mirror_at_point, axis=axis) for point in points
    ]
    mirrored_points.reverse()
    if combine:
        return [*points, *mirrored_points]
    else:
        return mirrored_points

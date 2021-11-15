def mirror_points(points, mirror_at_point, combine=True):
    mirrored_points = [
        (mirror_at_point[0] - (point[0] - mirror_at_point[0]), point[1])
        for point in points
    ]
    mirrored_points.reverse()
    if combine:
        return [*points, *mirrored_points]
    else:
        return mirrored_points

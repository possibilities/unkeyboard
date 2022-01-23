def points_to_line(points):
    zipped_points = zip(points[0:-1], points[1:])
    return [
        {"start": start_point, "end": end_point}
        for start_point, end_point in zipped_points
    ]

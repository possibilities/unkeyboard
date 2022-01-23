from dedupe_points import dedupe_points
from points_to_line import points_to_line


def points_to_lines(points):
    clean_points = dedupe_points(points)
    return points_to_line(clean_points)

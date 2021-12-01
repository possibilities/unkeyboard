from mirror_point import mirror_point


def flip_point_over_x_axis(point):
    [flipped_x, flipped_y] = mirror_point((0, point[1]), (0, 0), axis="X")
    return (point[0], flipped_y)

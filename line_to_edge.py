def line_to_edge(line, edge):
    xdiff = (line[0][0] - line[1][0], edge[0][0] - edge[1][0])
    ydiff = (line[0][1] - line[1][1], edge[0][1] - edge[1][1])

    def det(a, b):
        return a[0] * b[1] - a[1] * b[0]

    div = det(xdiff, ydiff)
    if div == 0:
        raise Exception("lines do not intersect")

    d = (det(*line), det(*edge))
    x = det(d, xdiff) / div
    y = det(d, ydiff) / div
    return (x, y)

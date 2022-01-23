def calculate_min_max_coords_for_lines(edge_cuts):
    x_coords = []
    y_coords = []

    for line in edge_cuts:
        x_coords.append(line["start"][0])
        x_coords.append(line["end"][0])
        y_coords.append(line["start"][1])
        y_coords.append(line["end"][1])

    min_x = min(x_coords)
    min_y = min(y_coords)
    max_x = max(x_coords)
    max_y = max(y_coords)

    return [min_x, min_y, max_x, max_y]

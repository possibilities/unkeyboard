import cadquery as cq
from pprint import pprint
from sexpdata import loads
from mirror_point import mirror_point
from flow import flow
from from_pairs import from_pairs
from to_pairs import to_pairs
from rotate_2d import rotate_2d


def parse_attributes(values):
    parsed = {}
    for value in values:
        if isinstance(value, str):
            parsed["text"] = value
            continue

        [key, *val] = value
        if str(key) in ["drill", "net", "layer", "width", "thickness"]:
            parsed[str(key)] = val[0]
        elif str(key) in ["tstamp", "attr", "descr"]:
            parsed[str(key)] = str(val[0])
        else:
            parsed[str(key)] = val
    return parsed


def parse_net(net):
    [id, name] = net
    return {"id": id, "name": name}


def ensure_default(obj, key, val):
    if not key in obj:
        obj[key] = val
    return obj


def parse_pcb(pcb_data):
    board = {}
    for symbol_and_values in pcb_data:
        [symbol, *values] = symbol_and_values
        name = str(symbol)

        if str(name) == "general":
            board["general"] = parse_attributes(values)

        elif str(name) == "net":
            board = ensure_default(board, "nets", [])
            board["nets"].append(parse_net(values))

        elif str(name) == "footprint":
            board = ensure_default(board, "footprints", [])
            [label, *footprint_values] = values
            board["footprints"].append(
                {"label": label, **parse_pcb(footprint_values)}
            )

        elif str(name) == "via":
            board = ensure_default(board, "vias", [])
            board["vias"].append(parse_attributes(values))

        elif str(name) == "gr_text":
            board = ensure_default(board, "gr_texts", [])
            board["gr_texts"].append(parse_attributes(values))

        elif str(name) == "gr_line":
            board = ensure_default(board, "gr_lines", [])
            board["gr_lines"].append(parse_attributes(values))

        elif str(name) == "segment":
            board = ensure_default(board, "segments", [])
            board["segments"].append(parse_attributes(values))

        elif str(name) == "layers":
            board = ensure_default(board, "layers", [])
            for layer in values:
                if len(layer) == 3:
                    [id, name, type] = layer
                    board["layers"].append(
                        {"id": id, "name": name, "type": str(type)}
                    )
                else:
                    [id, name, type, label] = layer
                    board["layers"].append(
                        {
                            "id": id,
                            "name": name,
                            "label": label,
                            "type": str(type),
                        }
                    )

        elif str(name) == "setup":
            board["setup"] = parse_attributes(values)

        elif str(name) == "fp_line":
            board = ensure_default(board, "fp_lines", [])
            board["fp_lines"].append(parse_attributes(values))

        elif str(name) == "fp_circle":
            board = ensure_default(board, "fp_circles", [])
            board["fp_circles"].append(parse_attributes(values))

        elif str(name) == "pad":
            board = ensure_default(board, "pads", [])
            [label, type, shape, state, *pad_values] = values
            board["pads"].append(
                {
                    **parse_attributes(pad_values),
                    "label": label,
                    "type": str(type),
                    "state": str(state),
                    "shape": str(shape),
                }
            )

        elif str(name) == "fp_text":
            board = ensure_default(board, "fp_texts", [])
            board["fp_texts"].append(parse_attributes(values))

        elif str(name) in ["attr", "layer", "descr"]:
            board[str(name)] = str(values[0])

        else:
            board[str(name)] = values

    return board


def convert_positions_to_negative_y_plane(pcb):
    def run(item):
        if isinstance(item, dict):
            pairs = to_pairs(item)
            updated_pairs = []
            for pair in pairs:
                if pair[0].endswith("_y"):
                    [flipped_x, flipped_y] = mirror_point(
                        (0, pair[1]), (0, 0), axis="X"
                    )
                    updated_pairs.append((pair[0], flipped_y))
                else:
                    updated_pairs.append((pair[0], run(pair[1])))
            dictionary = from_pairs(updated_pairs)
            return dictionary
        elif isinstance(item, list) or isinstance(item, tuple):
            return [run(i) for i in item]
        else:
            return item

    return run(pcb)


def add_position_attributes(pcb):
    def run(item):
        if isinstance(item, dict):
            pairs = to_pairs(item)
            updated_pairs = []
            for pair in pairs:
                updated_pairs.append((pair[0], run(pair[1])))
                if pair[0] == "at":
                    updated_pairs.append(("position_x", pair[1][0]))
                    updated_pairs.append(("position_y", pair[1][1]))
                    updated_pairs.append(
                        (
                            "rotation",
                            pair[1][2] if len(pair[1]) >= 3 else 0,
                        )
                    )
                elif pair[0] == "start":
                    updated_pairs.append(("start_x", pair[1][0]))
                    updated_pairs.append(("start_y", pair[1][1]))
                elif pair[0] == "end":
                    updated_pairs.append(("end_x", pair[1][0]))
                    updated_pairs.append(("end_y", pair[1][1]))
                elif pair[0] == "center":
                    updated_pairs.append(("center_x", pair[1][0]))
                    updated_pairs.append(("center_y", pair[1][1]))
            dictionary = from_pairs(updated_pairs)
            return dictionary
        elif isinstance(item, list) or isinstance(item, tuple):
            return [run(i) for i in item]
        else:
            return item

    return run(pcb)


def make_footprint_child_positions_absolute(footprint):
    pads = footprint["pads"]
    fp_lines = footprint["fp_lines"]
    fp_circles = footprint["fp_circles"] if "fp_circles" in footprint else []
    fp_texts = footprint["fp_texts"]
    pads = footprint["pads"]

    return {
        **footprint,
        "pads": [
            {
                **pad,
                "position_x": pad["position_x"] + footprint["position_x"],
                "position_y": pad["position_y"] + footprint["position_y"],
            }
            for pad in pads
        ],
        "fp_lines": [
            {
                **fp_line,
                "start_x": fp_line["start_x"] + footprint["position_x"],
                "start_y": fp_line["start_y"] + footprint["position_y"],
                "end_x": fp_line["end_x"] + footprint["position_x"],
                "end_y": fp_line["end_y"] + footprint["position_y"],
            }
            for fp_line in fp_lines
        ],
        "fp_circles": [
            {
                **fp_circle,
                "center_x": fp_circle["center_x"] + footprint["position_x"],
                "center_y": fp_circle["center_y"] + footprint["position_y"],
                "end_x": fp_circle["end_x"] + footprint["position_x"],
                "end_y": fp_circle["end_y"] + footprint["position_y"],
            }
            for fp_circle in fp_circles
        ],
        "fp_texts": [
            {
                **fp_text,
                "position_x": fp_text["position_x"] + footprint["position_x"],
                "position_y": fp_text["position_y"] + footprint["position_y"],
            }
            for fp_text in fp_texts
        ],
    }


def make_footprints_child_positions_absolute(pcb):
    if "footprints" not in pcb:
        return pcb
    footprints = [
        make_footprint_child_positions_absolute(footprint)
        for footprint in pcb["footprints"]
    ]
    return {**pcb, "footprints": footprints}


def rotate_footprint_child_position(footprint, child, x_key, y_key):
    footprint_rotate = footprint["rotation"] if "rotation" in footprint else 0
    (rotated_x, rotated_y) = rotate_2d(
        (footprint["position_x"], footprint["position_y"]),
        (child[x_key], child[y_key]),
        # Rotate in the opposite direction in prepation for flipping
        # over the x axis later
        -footprint_rotate,
    )
    return {"x": rotated_x, "y": rotated_y}


def rotate_footprint_child_positions(footprint):
    pads = footprint["pads"]
    fp_lines = footprint["fp_lines"]
    fp_circles = footprint["fp_circles"]
    fp_texts = footprint["fp_texts"]
    pads = footprint["pads"]

    return {
        **footprint,
        "pads": [
            {
                **pad,
                "position_x": rotate_footprint_child_position(
                    footprint, pad, "position_x", "position_y"
                )["x"],
                "position_y": rotate_footprint_child_position(
                    footprint, pad, "position_x", "position_y"
                )["y"],
            }
            for pad in pads
        ],
        "fp_lines": [
            {
                **fp_line,
                "start_x": rotate_footprint_child_position(
                    footprint, fp_line, "start_x", "start_y"
                )["x"],
                "start_y": rotate_footprint_child_position(
                    footprint, fp_line, "start_x", "start_y"
                )["y"],
                "end_x": rotate_footprint_child_position(
                    footprint, fp_line, "end_x", "end_y"
                )["x"],
                "end_y": rotate_footprint_child_position(
                    footprint, fp_line, "end_x", "end_y"
                )["y"],
            }
            for fp_line in fp_lines
        ],
        "fp_circles": [
            {
                **fp_circle,
                "center_x": rotate_footprint_child_position(
                    footprint, fp_circle, "center_x", "center_y"
                )["x"],
                "center_y": rotate_footprint_child_position(
                    footprint, fp_circle, "center_x", "center_y"
                )["y"],
                "end_x": rotate_footprint_child_position(
                    footprint, fp_circle, "end_x", "end_y"
                )["x"],
                "end_y": rotate_footprint_child_position(
                    footprint, fp_circle, "end_x", "end_y"
                )["y"],
            }
            for fp_circle in fp_circles
        ],
        "fp_texts": [
            {
                **fp_text,
                "position_x": rotate_footprint_child_position(
                    footprint, fp_text, "position_x", "position_y"
                )["x"],
                "position_y": rotate_footprint_child_position(
                    footprint, fp_text, "position_x", "position_y"
                )["y"],
            }
            for fp_text in fp_texts
        ],
    }


def rotate_footprints_child_positions(pcb):
    if "footprints" not in pcb:
        return pcb
    footprints = [
        rotate_footprint_child_positions(footprint)
        for footprint in pcb["footprints"]
    ]
    return {**pcb, "footprints": footprints}


prepare_pcb = flow(
    add_position_attributes,
    make_footprints_child_positions_absolute,
    rotate_footprints_child_positions,
    convert_positions_to_negative_y_plane,
)


def load_pcb(path):
    with open(path) as f:
        pcb_data = loads(f.read())
    pcb = parse_pcb(pcb_data[1:])
    return prepare_pcb(pcb)

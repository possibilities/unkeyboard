import sexpdata
from rotate_2d import rotate_2d


def load_board(project_path, project_name):
    with open(f"{project_path}/{project_name}.kicad_pcb") as f:
        board = sexpdata.loads(f.read())
    return board


def get_value(board, name):
    try:
        value = next(item for item in board if item[0] == sexpdata.Symbol(name))
        return value[1]
    except Exception:
        return None


def get_values(board, name):
    try:
        value = next(
            item
            for item in board
            if (isinstance(item, list) or isinstance(item, tuple))
            and item[0] == sexpdata.Symbol(name)
        )
        return value[1:]
    except Exception as err:
        print(err)
        return None


def get_collection(board, collection_name, type=None):
    return [
        item
        for item in board
        if item[0] == sexpdata.Symbol(collection_name)
        and (type is None or item[1] == type)
    ]


def get_item(board, collection_name, type=None):
    return next(
        item
        for item in board
        if item[0] == sexpdata.Symbol(collection_name)
        and (type is None or item[1] == type)
    )


def pads_from_footprint(footprint, footprint_position, footprint_rotation):
    pads = get_collection(footprint, "pad")

    pad_info = {}

    for pad in pads:
        if pad[1] == "":
            continue
        at = get_item(pad, "at")
        relative_position = at[1:3]
        position = (
            relative_position[0] + footprint_position[0],
            relative_position[1] + footprint_position[1],
        )
        pad_info[pad[1]] = {
            "position": rotate_2d(
                footprint_position,
                position,
                footprint_rotation,
            ),
            "rotation": at[3] if len(at) >= 4 else 0,
        }

    return pad_info


def load_footprints_pad_positions(board, footprint_name):
    footprint_positions = []

    footprints = get_collection(board, "footprint")
    for footprint in footprints:
        if footprint[1] != footprint_name:
            continue
        at = get_item(footprint, "at")
        footprint_rotation = at[3] if len(at) >= 4 else 0
        footprint_position = at[1:3]
        footprint_positions.append(
            pads_from_footprint(footprint, footprint_position, footprint_rotation)
        )

    return footprint_positions

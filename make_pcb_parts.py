import cadquery as cq
from cq_workplane_plugin import cq_workplane_plugin
from calculate_rectangle_corners import calculate_rectangle_corners
from rotate_2d import rotate_2d
from fuse_parts import fuse_parts
from flip_point_over_x_axis import flip_point_over_x_axis
from flip_points_over_x_axis import flip_points_over_x_axis
import kicad

pad_thickness = 0.075


def find_next_pcb_line(line, lines):
    for next_line in lines:
        if (
            kicad.get_values(next_line, "start")[0] == kicad.get_values(line, "end")[0]
            and kicad.get_values(next_line, "start")[1]
            == kicad.get_values(line, "end")[1]
        ):
            return next_line
    return None


def lines_to_polyline(lines):
    ordered_lines = [lines[0]]

    while True:
        next_line = find_next_pcb_line(ordered_lines[-1], lines[1:])
        if next_line:
            ordered_lines.append(next_line)
        else:
            break

    return [kicad.get_values(line, "start") for line in ordered_lines]


def make_thru_hole_pads(board_data):
    circular_positions = []
    rectangular_positions = []

    for footprint in kicad.get_collection(board_data, "footprint"):
        footprint_position_values = list(
            filter(
                lambda item: isinstance(item, int) or isinstance(item, float),
                kicad.get_values(footprint, "at"),
            )
        )
        footprint_position = footprint_position_values[0:2]
        footprint_rotation = (
            footprint_position_values[2] if len(footprint_position_values) >= 3 else 0
        )
        for pad in kicad.get_collection(footprint, "pad"):
            item_position = kicad.get_values(pad, "at")[0:2]
            if str(pad[2]) == "thru_hole":
                if str(pad[3]) == "circle":
                    circular_positions.append(
                        {
                            "position": flip_point_over_x_axis(
                                rotate_2d(
                                    footprint_position,
                                    (
                                        item_position[0] + footprint_position[0],
                                        item_position[1] + footprint_position[1],
                                    ),
                                    footprint_rotation,
                                )
                            ),
                            "inner_radius": kicad.get_value(pad, "drill") / 2,
                            "outer_radius": kicad.get_values(pad, "size")[0] / 2,
                        }
                    )
                elif str(pad[3]) == "rect":
                    rectangular_positions.append(
                        {
                            "position": flip_point_over_x_axis(
                                rotate_2d(
                                    footprint_position,
                                    (
                                        item_position[0] + footprint_position[0],
                                        item_position[1] + footprint_position[1],
                                    ),
                                    footprint_rotation,
                                )
                            ),
                            "inner_radius": kicad.get_value(pad, "drill") / 2,
                            "outer_rect_width": kicad.get_values(pad, "size")[0],
                            "outer_rect_height": kicad.get_values(pad, "size")[1],
                        }
                    )

    pads = cq.Workplane()

    thickness = kicad.get_value(kicad.get_values(board_data, "general"), "thickness")

    if len(circular_positions) or len(rectangular_positions):
        for pad in circular_positions:
            pads = (
                pads.moveTo(*pad["position"])
                .circle(pad["inner_radius"])
                .circle(pad["outer_radius"])
            )

        for pad in rectangular_positions:
            pads = (
                pads.moveTo(*pad["position"])
                .circle(pad["inner_radius"])
                .rect(pad["outer_rect_height"], pad["outer_rect_height"])
            )

        return pads.extrude((pad_thickness * 2) + thickness).translate(
            [0, 0, -pad_thickness]
        )

    return pads


def make_via_pads(board_data):
    pads = cq.Workplane()

    vias = kicad.get_collection(board_data, "via")

    thickness = kicad.get_value(kicad.get_values(board_data, "general"), "thickness")

    if len(vias):
        for via in vias:
            via_position = kicad.get_values(via, "at")[0:2]
            pads = (
                pads.moveTo(*flip_point_over_x_axis(via_position))
                .circle(kicad.get_value(via, "drill") / 2)
                .circle(kicad.get_values(via, "size")[0] / 2)
            )

        pads = pads.extrude(pad_thickness + thickness).translate(
            [0, 0, -pad_thickness / 2]
        )

    return pads


def make_surface_mount_pads(board_data):
    positions = []

    for footprint in kicad.get_collection(board_data, "footprint"):
        footprint_position_values = list(
            filter(
                lambda item: isinstance(item, int) or isinstance(item, float),
                kicad.get_values(footprint, "at"),
            )
        )
        footprint_position = footprint_position_values[0:2]
        footprint_rotation = (
            footprint_position_values[2] if len(footprint_position_values) >= 3 else 0
        )
        for pad in kicad.get_collection(footprint, "pad"):
            item_position = kicad.get_values(pad, "at")[0:2]
            item_rotation = (
                kicad.get_values(pad, "at")[2]
                if len(kicad.get_values(pad, "at")) >= 3
                else 0
            )
            if str(pad[2]) == "smd":
                if str(pad[3]) == "rect":

                    positions.append(
                        calculate_rectangle_corners(
                            flip_point_over_x_axis(
                                rotate_2d(
                                    footprint_position,
                                    (
                                        item_position[0] + footprint_position[0],
                                        item_position[1] + footprint_position[1],
                                    ),
                                    footprint_rotation,
                                )
                            ),
                            kicad.get_values(pad, "size")[0],
                            kicad.get_values(pad, "size")[1],
                            angle=-item_rotation,
                        )
                    )

    pads = []

    if len(positions):
        for position in positions:
            pads.append(
                cq.Workplane()
                .polyline(position)
                .close()
                .extrude(pad_thickness * 2)
                .translate([0, 0, -pad_thickness])
            )

    return fuse_parts(pads)


@cq_workplane_plugin
def drill_holes_for_thru_hole_pads(self, footprints, thickness):
    circular_holes_by_size = {}
    rectangular_holes_by_size = {}

    for footprint in footprints:
        footprint_position_values = list(
            filter(
                lambda item: isinstance(item, int) or isinstance(item, float),
                kicad.get_values(footprint, "at"),
            )
        )
        footprint_position = footprint_position_values[0:2]
        footprint_rotation = (
            footprint_position_values[2] if len(footprint_position_values) >= 3 else 0
        )
        for pad in kicad.get_collection(footprint, "pad"):
            if str(pad[2]) in ["thru_hole", "np_thru_hole"]:
                if str(pad[3]) == "circle":
                    if kicad.get_values(pad, "size")[0] not in circular_holes_by_size:
                        circular_holes_by_size[kicad.get_values(pad, "size")[0]] = []
                    item_position = kicad.get_values(pad, "at")[0:2]
                    circular_holes_by_size[kicad.get_values(pad, "size")[0]].append(
                        rotate_2d(
                            footprint_position,
                            (
                                item_position[0] + footprint_position[0],
                                item_position[1] + footprint_position[1],
                            ),
                            footprint_rotation,
                        ),
                    )
                elif str(pad[3]) == "rect":
                    if (
                        kicad.get_values(pad, "size")[0]
                        not in rectangular_holes_by_size
                    ):
                        rectangular_holes_by_size[kicad.get_values(pad, "size")[0]] = []
                    item_position = kicad.get_values(pad, "at")[0:2]
                    rectangular_holes_by_size[kicad.get_values(pad, "size")[0]].append(
                        rotate_2d(
                            footprint_position,
                            (
                                item_position[0] + footprint_position[0],
                                item_position[1] + footprint_position[1],
                            ),
                            footprint_rotation,
                        ),
                    )

    for size, positions in circular_holes_by_size.items():
        self = (
            self.faces("front")
            .pushPoints(flip_points_over_x_axis(positions))
            .circle(size / 2)
            .cutBlind(thickness)
        )

    for size, positions in rectangular_holes_by_size.items():
        self = (
            self.faces("front")
            .pushPoints(flip_points_over_x_axis(positions))
            .rect(size, size)
            .cutBlind(thickness)
        )

    return self


@cq_workplane_plugin
@cq_workplane_plugin
def drill_holes_for_vias(self, vias, thickness):
    holes_by_size = {}

    for via in vias:
        if kicad.get_value(via, "drill") not in holes_by_size:
            holes_by_size[kicad.get_value(via, "drill")] = []
        holes_by_size[kicad.get_value(via, "drill")].append(
            kicad.get_values(via, "at")[0:2]
        )

    for size, positions in holes_by_size.items():
        self = (
            self.faces("front")
            .pushPoints(flip_points_over_x_axis(positions))
            .circle(size / 2)
            .cutBlind(thickness)
        )

    return self


def make_board(board_data):
    edge_cut_lines = list(
        filter(
            lambda line: kicad.get_value(line, "layer") == "Edge.Cuts",
            kicad.get_collection(board_data, "gr_line"),
        )
    )

    if not len(edge_cut_lines):
        return cq.Workplane()

    thickness = kicad.get_value(kicad.get_values(board_data, "general"), "thickness")

    edge_cut_lines = flip_points_over_x_axis(lines_to_polyline(edge_cut_lines))

    board = cq.Workplane().polyline(edge_cut_lines).close().extrude(thickness)

    board = board.drill_holes_for_thru_hole_pads(
        kicad.get_collection(board_data, "footprint"), thickness
    )

    board = board.drill_holes_for_vias(
        kicad.get_collection(board_data, "via"), thickness
    )

    return board


def make_lines(footprint, layer, line_type):
    footprint_position_values = (
        list(
            filter(
                lambda item: isinstance(item, int) or isinstance(item, float),
                kicad.get_values(footprint, "at"),
            )
        )
        if kicad.get_values(footprint, "at")
        else [0, 0]
    )
    footprint_position = footprint_position_values[0:2]
    footprint_lines_for_layer = list(
        filter(
            lambda line: kicad.get_value(line, "layer") == layer,
            kicad.get_collection(footprint, line_type),
        )
    )
    footprint_rotation = (
        footprint_position_values[2] if len(footprint_position_values) >= 3 else 0
    )
    footprint_lines = [
        {
            "start": flip_point_over_x_axis(
                rotate_2d(
                    footprint_position,
                    (
                        kicad.get_values(line, "start")[0] + footprint_position[0],
                        kicad.get_values(line, "start")[1] + footprint_position[1],
                    ),
                    footprint_rotation,
                )
            ),
            "end": flip_point_over_x_axis(
                rotate_2d(
                    footprint_position,
                    (
                        kicad.get_values(line, "end")[0] + footprint_position[0],
                        kicad.get_values(line, "end")[1] + footprint_position[1],
                    ),
                    footprint_rotation,
                )
            ),
        }
        for line in footprint_lines_for_layer
    ]
    return footprint_lines


def make_footprints_lines(board_data, layer):
    thickness = kicad.get_value(kicad.get_values(board_data, "general"), "thickness")

    footprint_lines = []

    for footprint in kicad.get_collection(board_data, "footprint"):
        footprint_lines = [
            *footprint_lines,
            *make_lines(footprint, layer, "fp_line"),
        ]

    lines = []
    for footprint_line in footprint_lines:
        line = cq.Workplane()
        line = line.moveTo(*footprint_line["start"]).lineTo(*footprint_line["end"])
        lines.append(line)

    return fuse_parts(lines).translate(
        [
            0,
            0,
            thickness if layer.startswith("F.") else 0,
        ]
    )


def make_segments(board_data, layer):
    thickness = kicad.get_value(kicad.get_values(board_data, "general"), "thickness")

    footprint_lines = make_lines(board_data, layer, "segment")

    lines = []
    for footprint_line in footprint_lines:
        line = cq.Workplane()
        line = line.moveTo(*footprint_line["start"]).lineTo(*footprint_line["end"])
        lines.append(line)

    return fuse_parts(lines).translate(
        [
            0,
            0,
            thickness if layer.startswith("F.") else 0,
        ]
    )


def make_pcb_parts(board_data):
    board = make_board(board_data)

    pad_yellow = (204, 204, 0)

    parts = []

    thru_hole_pads = make_thru_hole_pads(board_data)
    via_pads = make_via_pads(board_data)
    surface_mount_pads = make_surface_mount_pads(board_data)

    front_silkscreens = make_footprints_lines(board_data, "F.SilkS")
    back_silkscreens = make_footprints_lines(board_data, "B.SilkS")
    front_segments = make_segments(board_data, "F.Cu")
    back_segments = make_segments(board_data, "B.Cu")

    parts.append(("PCB board", board, {"color": (0, 51, 25), "alpha": 0}))
    parts.append(("PCB thru hold pads", thru_hole_pads, {"color": pad_yellow}))
    parts.append(("PCB via pads", via_pads, {"color": pad_yellow}))
    parts.append(("PCB surface mount pads", surface_mount_pads, {"color": pad_yellow}))
    parts.append(("PCB front silkscreens", front_silkscreens, {"color": "white"}))
    parts.append(("PCB back silkscreens", back_silkscreens, {"color": "white"}))
    parts.append(("PCB front segments", front_segments, {"color": "red"}))
    parts.append(("PCB back segments", back_segments, {"color": "blue"}))

    return parts

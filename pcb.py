import os
import jinja2
import uuid
import sexpdata
import calculate_tracks
from case import make_case_parts
from zip import zip
from presets import presets
from flip_point_over_x_axis import flip_point_over_x_axis
from make_pcb_parts import make_pcb_parts
from make_atreus_62_pcb import make_atreus_62_pcb
from save_pcb import save_pcb
from from_pairs import from_pairs
from calculate_pcb_outline import calculate_pcb_outline
from to_pairs import to_pairs
from calculate_pcb_tracks import calculate_pcb_tracks
from calculate_footprint_positions import calculate_footprint_positions
from calculate_min_max_coords_for_lines import calculate_min_max_coords_for_lines
import kicad

id_for_net_name_lookup = {}


def id_for_net_name(name):
    if name not in id_for_net_name_lookup:
        id_for_net_name_lookup[name] = len(id_for_net_name_lookup.keys()) + 1
    return id_for_net_name_lookup[name]


def calculate_reset_switch_geometry(case_geometry, config):
    reset_switch_rotation = config["angle"]

    case_reset_switch_position = flip_point_over_x_axis(
        case_geometry["reset_button"]["point"]
    )

    reset_switch_position = (
        case_geometry["mirror_at"]["point"][0]
        + (case_geometry["mirror_at"]["point"][0] - case_reset_switch_position[0]),
        case_reset_switch_position[1],
    )

    return {
        "position": reset_switch_position,
        "rotation": reset_switch_rotation,
        "pad_1_net": {
            "name": "GND",
            "id": id_for_net_name("GND"),
        },
        "pad_2_net": {
            "name": "Net-(SW-RST1-Pad2)",
            "id": id_for_net_name("Net-(SW-RST1-Pad2)"),
        },
    }


def calculate_mcu_geometry(case_geometry):
    mcu_y_offset = -53.55
    mcu_position = (case_geometry["mirror_at"]["point"][0], mcu_y_offset)
    return {"position": mcu_position}


def add_nets_to_pads(footprints, pads, nets):
    return [
        {
            **footprint,
            "pad_1_net": next(
                (
                    net_name
                    for _net_id, net_name in to_pairs(nets)
                    if pads["1"]["position"] in net_name["points"]
                ),
                None,
            ),
            "pad_2_net": next(
                (
                    net_name
                    for _net_id, net_name in to_pairs(nets)
                    if pads["2"]["position"] in net_name["points"]
                ),
                None,
            ),
        }
        for footprint, pads in zip(footprints, pads)
    ]


def add_nets_to_mcu_pads(mcu_geometry, mcu_pads, nets):
    return {
        **mcu_geometry,
        **from_pairs(
            [
                f"pad_{pad_name}_net",
                {
                    "id": next(
                        (
                            net_info["id"]
                            for _net_id, net_info in to_pairs(nets)
                            if pad_info["position"] in net_info["points"]
                        ),
                        0,
                    ),
                    "name": next(
                        (
                            net_info["name"]
                            for _net_id, net_info in to_pairs(nets)
                            if pad_info["position"] in net_info["points"]
                        ),
                        "",
                    ),
                },
            ]
            for pad_name, pad_info in to_pairs(mcu_pads)
        ),
    }


def nets_from_vias_and_tracks(vias, tracks):
    nets = {}
    for via in vias:
        points = []
        if str(via["net"]) in nets:
            points = nets[str(via["net"])]["points"]
        nets[str(via["net"])] = {
            "name": via["net"],
            "id": id_for_net_name(via["net"]),
            "points": [*points, via["point"]],
        }
    for track in tracks:
        points = []
        if str(track["net"]) in nets:
            points = nets[str(track["net"])]["points"]
        nets[str(track["net"])] = {
            "name": track["net"],
            "id": id_for_net_name(track["net"]),
            "points": [*points, *track["points"]],
        }
    return nets


def calculate_pcb_geometry(user_config={}):
    config = {**presets["default"], **user_config}
    case_parts, case_geometry = make_case_parts(config)

    number_of_thumb_keys = 4 if config["has_two_thumb_keys"] else 2

    if number_of_thumb_keys == 4:
        raise Exception("4 thumb keys not yet supported on PCB")

    switches, diodes = calculate_footprint_positions(
        case_geometry, number_of_thumb_keys, config
    )

    edge_cuts = calculate_pcb_outline(case_geometry, config)

    reset_switch_geometry = calculate_reset_switch_geometry(case_geometry, config)

    mcu_geometry = calculate_mcu_geometry(case_geometry)

    pcb_geometry = {
        "edge_cuts": edge_cuts,
        "switches": switches,
        "diodes": diodes,
        "mcu": mcu_geometry,
        "reset_switch": reset_switch_geometry,
    }

    template_environment = jinja2.Environment()
    template_environment.globals.update(tstamp=uuid.uuid4)

    with open("pcb-template/keyboard.kicad_pcb.tmpl") as f:
        kicad_pcb_template_string = f.read()

    kicad_pcb_template = template_environment.from_string(kicad_pcb_template_string)
    kicad_pcb = kicad_pcb_template.render(pcb_geometry)

    board_without_tracks = sexpdata.loads(kicad_pcb)

    [reset_switch_pads] = kicad.load_footprints_pad_positions(
        board_without_tracks, "parts:SW_SPST_B3U-1000P"
    )

    [mcu_pads] = kicad.load_footprints_pad_positions(
        board_without_tracks, "parts:ProMicro_v3"
    )

    switches_pads = kicad.load_footprints_pad_positions(
        board_without_tracks, "parts:SW_MX"
    )

    diodes_pads = kicad.load_footprints_pad_positions(
        board_without_tracks, "parts:D3_SMD"
    )

    mirror_at_point = case_geometry["mirror_at"]["point"]

    tracks, vias, debug_points = calculate_pcb_tracks(
        switches,
        diodes,
        switches_pads,
        diodes_pads,
        mcu_pads,
        reset_switch_pads,
        mirror_at_point,
        config,
        calculate_tracks,
    )

    [min_x, min_y, max_x, max_y] = calculate_min_max_coords_for_lines(edge_cuts)

    board_width = max_x - min_x
    board_height = max_y - min_y

    inside_paper_padding = 10
    default_paper_padding = 10
    space_for_legend = 32

    paper_width = board_width + (inside_paper_padding * 2) + (default_paper_padding * 2)
    paper_height = (
        board_height
        + (inside_paper_padding * 2)
        + (default_paper_padding * 2)
        + space_for_legend
    )

    nets = nets_from_vias_and_tracks(vias, tracks)

    tracks_with_net_ids = [{**track, "net": nets[track["net"]]} for track in tracks]

    vias_with_net_ids = [{**via, "net": nets[via["net"]]} for via in vias]

    diodes_with_nets = add_nets_to_pads(diodes, diodes_pads, nets)
    switches_with_nets = add_nets_to_pads(switches, switches_pads, nets)

    mcu_geometry_with_nets = add_nets_to_mcu_pads(mcu_geometry, mcu_pads, nets)

    return {
        **pcb_geometry,
        "mcu": mcu_geometry_with_nets,
        "switches": switches_with_nets,
        "diodes": diodes_with_nets,
        "vias": vias_with_net_ids,
        "tracks": tracks_with_net_ids,
        "nets": nets.values(),
        "debug_points": debug_points,
        "paper_size": {"width": paper_width, "height": paper_height},
    }


def generate_pcb(project_path, project_name):
    pcb_geometry = calculate_pcb_geometry()
    save_pcb(pcb_geometry, project_path, project_name)


if __name__ == "__main__":
    generate_pcb("data/pcb", "keyboard")

if "show_object" in globals():
    board_data = kicad.load_board("data/pcb", "keyboard")
    pcb_parts = make_pcb_parts(board_data)

    for layer_name_part_and_options in pcb_parts:
        [layer_name, part, options] = layer_name_part_and_options
        show_object(
            part,
            name=layer_name,
            options=options,
        )

    show_original_pcb = bool(os.getenv("SHOW_ORIGINAL_PCB"))

    if show_original_pcb:
        for layer_name_part_and_options in make_atreus_62_pcb():
            [layer_name, part, options] = layer_name_part_and_options
            show_object(
                part,
                name="Atreus 62 " + layer_name,
                options=options,
            )

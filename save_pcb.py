import os
import jinja2
import uuid
import json
from pathlib import Path
from shutil import copyfile


def get_visible_layer_setting():
    if bool(os.getenv("SHOW_TRACKS_ONLY")):
        return "0001000_80000001"

    elif bool(os.getenv("SHOW_FRONT_TRACKS_ONLY")):
        return "0001000_00000001"

    elif bool(os.getenv("SHOW_BACK_TRACKS_ONLY")):
        return "0001000_80000000"

    all_layers = "fffffff_ffffffff"
    return all_layers


def save_pcb(pcb_geometry, project_track, project_name):
    path = Path(project_track)
    path.mkdir(parents=True, exist_ok=True)

    template_environment = jinja2.Environment()
    template_environment.globals.update(tstamp=uuid.uuid4)

    visible_layers = get_visible_layer_setting()

    with open("pcb-template/keyboard.kicad_prl") as f:
        kicad_settings = json.loads(f.read())

    updated_kicad_settings = {
        **kicad_settings,
        "board": {
            **kicad_settings["board"],
            "visible_layers": visible_layers,
        },
    }

    with open("pcb-template/keyboard.kicad_pcb.tmpl") as f:
        kicad_pcb_template_string = f.read()

    kicad_pcb_template = template_environment.from_string(kicad_pcb_template_string)
    kicad_pcb = kicad_pcb_template.render(pcb_geometry)

    pcb_file = open(f"{project_track}/{project_name}.kicad_pcb", "w")
    pcb_file.write(kicad_pcb)
    pcb_file.close()

    pcb_file = open(f"{project_track}/{project_name}.kicad_prl", "w")
    pcb_file.write(json.dumps(updated_kicad_settings, indent=4))
    pcb_file.close()

    copyfile("pcb-template/fp-lib-table", f"{project_track}/fp-lib-table")
    copyfile(
        "pcb-template/keyboard.kicad_pro",
        f"{project_track}/{project_name}.kicad_pro",
    )

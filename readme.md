# Unkeyboard

Unkeyboard is a set of python scripts, using [CadQuery](https://cadquery.readthedocs.io/), for generating stacked acrylic cases for [Atreus](https://github.com/profet23/atreus62)-style keyboards. The case is derived from the [62 key case](https://github.com/profet23/atreus62) but generating similar cases for the [42 key](https://atreus.technomancy.us/) and [44 key](https://shop.keyboard.io/products/keyboardio-atreus) variations is also supported. By default a [Chicago bolt](https://en.wikipedia.org/wiki/Sex_bolt) is used, a wider bezel is added around the keys, and sharp corners replace the curved corners of the original. Generated cases can be [hand wired](https://beta.docs.qmk.fm/using-qmk/guides/keyboard-building/hand_wire) or used with [available PCBs](https://shop.profetkeyboards.com/product/atreus62-pcb).

## Development

PCB rendering will take a very long time and lock up CQ-Editor unless you lower the rendering tolerance.

* Open: `Preferences -> 3D Viewer -> Deviation`
* Value: `0.001`

## Credits

* Initial case and PCB dimensions are reverse engineered from the [Atreus64 project](https://github.com/profet23/atreus62).
* Switch footprint from Dale Price's [Keyswitches library](https://github.com/daprice/keyswitches.pretty)
* Diode footprint from Kosuke Adachi's [KBD library](https://github.com/foostan/kbd)

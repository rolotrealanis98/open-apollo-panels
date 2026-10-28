#!/usr/bin/env python3
"""Drawn knobs (`dial`) for the Oxford plug-ins, whose knobs are drawn in code and so have no art.

  python3 -I tools/oxford_dials.py --write            # put the dials into the Oxford specs
  python3 -I tools/oxford_dials.py --dial SPRITE      # print the dial that replaces SPRITE

The looks are measurements of the plug-ins' own knobs: radii, angles, colours by angle, how the
grooves and the pointer glow fall off. `--write` gives every knob element whose sprite is listed
here a `dial` and drops its `sprite`, so the panel no longer needs that picture.
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def stops(d):
    return [[k, "#" + v.upper()] for k, v in sorted(d.items())]


# --- Oxford EQ (and Envolution's medium knobs): grey grooved skirt, coloured cap, lit pointer slot

EQ_RIM = {0: "303a49", 15: "313a49", 30: "303a49", 45: "2e3847", 60: "2b3442", 75: "262f3b", 90: "222833",
          105: "1e242e", 120: "191e25", 135: "11141a", 140: "101319", 150: "12161c", 165: "191f27", 180: "1d232c",
          195: "212833", 210: "262e3a", 225: "2a3341", 240: "2e3746", 255: "2f3948", 270: "303a49", 345: "303a49"}
EQ_LIP = {0: "bac3d2", 45: "95a1b3", 90: "596271", 135: "252a32", 180: "444b58", 225: "6b7686", 270: "a2adbe",
          315: "bec7d5"}
EQ_LAND = {14: "a0acbd", 24: "9ba7ba", 34: "96a1b4", 44: "8f9bae", 54: "8893a6", 64: "818c9e", 74: "7a8698",
           84: "737e90", 94: "6a7486", 104: "5d6777", 114: "4d5564", 124: "3d4450", 134: "343943", 144: "333842",
           154: "393f4a", 164: "48505d", 174: "586171", 184: "636e80", 194: "6b7688", 204: "707b8f", 214: "768194",
           224: "7b879a", 234: "818da0", 244: "8793a6", 254: "8e9aad", 264: "95a0b3", 274: "9aa5b8", 284: "9da9bc",
           294: "a1adc0", 304: "a4b0c3", 314: "a6b1c4", 324: "a7b3c6", 334: "a6b2c5", 344: "a6b2c5"}
EQ_CONE = {0: "c2c8d2", 5: "bbc2cd", 10: "b3bbc7", 15: "aab3c0", 20: "a2abb7", 25: "95a0b1", 30: "8a95a8",
           35: "7d889a", 40: "707a8b", 45: "66707e", 50: "5c6470", 55: "4e5560", 60: "424751", 65: "373c43",
           70: "30353b", 75: "2e3238", 225: "2e3238", 230: "2f343b", 235: "353a41", 240: "40464f", 245: "4c535e",
           250: "59616e", 255: "666f7e", 260: "747e8e", 265: "7f8a9c", 270: "8a96a8", 275: "959fb0", 280: "9fa8b7",
           285: "a9b2bf", 290: "b3bbc6", 295: "bcc2cd", 300: "c3c9d2", 305: "c9ced7", 310: "ced3db", 315: "d2d6dd",
           320: "d4d9df", 325: "d6dae1", 330: "d7dbe1", 335: "d6dae1", 340: "d4d9df", 345: "d0d5dc", 350: "cad0d8",
           355: "c6ccd5"}
# light from the upper left on the cap's edge (white or black over the cap)
EQ_CAP_EDGE = {0: "ffffff66", 45: "ffffff0f", 90: "0000005e", 135: "0000009c", 180: "00000085", 225: "00000038",
               270: "ffffff30", 315: "ffffff75"}
# band knobs step 300/33 degrees per 1/32 of the value from the middle, held at +-144
EQ_BAND = ([-1600 / 11, 1600 / 11], [-144, 144])
EQ_SHELF = ([-144, 144], None)
EQ_CAPS = {"blue": "4676c8", "cyan": "46aac8", "green": "3aa968", "red": "c8465f", "orange": "c88947",
           "yellow": "c8c847", "grey": "9ca6b6", "light grey": "bcc5c8"}
# untouched bands are drawn at 81.8 %
EQ_DIM = 0.818


def eq_dial(cap, law, dim):
    angles, clamp = law
    d = {
        "cx": 28, "cy": 29, "angles": [round(a, 4) for a in angles],
        "layers": [
            {"type": "ring", "r": [25, 27], "fill": {"conic": stops(EQ_RIM)}},
            {"type": "ring", "r": [23.5, 25], "fill": {"conic": stops(EQ_LIP)}},
            {"type": "ring", "r": [15.5, 23.5], "fill": {"conic": stops(EQ_LAND)}},
            {"type": "grooves", "r": [16.75, 23.75], "count": 36, "width": 5.35, "soft": 1.5, "shade": 0.7,
             "fade": [0.5, 1.0]},
            {"type": "ring", "r": [11.75, 15.5], "fill": {"conic": stops(EQ_CONE)}},
            {"type": "ring", "r": [0, 11.75], "fill": {"color": "#" + EQ_CAPS[cap].upper(), "linear": [-0.64, -0.99]}},
            {"type": "ring", "r": [11.0, 11.75], "fill": {"conic": stops(EQ_CAP_EDGE)}},
            {"type": "glow", "r": [10.75, 26], "color": "#FDF540", "alpha": 0.49, "sigma": 2.15},
            {"type": "slot", "r": [17.25, 23.0],
             "profile": [[0, "#FCF883"], [0.5, "#FCF883"], [0.75, "#FCEE02"], [1.0, "#E2DC3A"], [1.25, "#C9CA72"],
                         [1.75, "#C9CA72"]],
             "profileOut": [[0, "#FCFCB3"], [0.5, "#FCFCB3"], [0.75, "#FCEE02"], [1.0, "#E2DC3A"],
                            [1.25, "#CECE7A"], [1.75, "#CECE7A"]]},
        ],
    }
    if clamp:
        d["clamp"] = clamp
    if dim:
        d["tint"] = {"mul": EQ_DIM}
    return d


# Oxford EQ cap colours by band parameter (channel A numbering; channel B is 32 higher)
EQ_BAND_CAPS = {3: "grey", 6: "light grey", 8: "cyan", 11: "blue", 12: "blue", 14: "blue", 16: "green", 17: "green",
                18: "green", 20: "red", 21: "red", 22: "red", 24: "orange", 25: "orange", 26: "orange", 29: "yellow",
                30: "yellow", 32: "yellow"}
EQ_SHELF_CAPS = {"ALFs": "blue", "BLFs": "blue", "AHFs": "yellow", "BHFs": "yellow"}
EQ_SPRITE = re.compile(r"^(?:R_|R__|F_|FP_)Oxford-EQ_(?:(B)_)?(?:([AB][LH]Fs)_)?p(\d+)_0(?:_(t|lit))?$")


def dial_for(sprite):
    m = EQ_SPRITE.match(sprite)
    if not m:
        return None
    b, shelf, n, variant = m.group(1), m.group(2), int(m.group(3)), m.group(4)
    if shelf:
        cap, law = EQ_SHELF_CAPS[shelf], EQ_SHELF
    else:
        cap, law = EQ_BAND_CAPS.get(n - 32 if b else n), EQ_BAND
        if cap is None:
            return None
    return eq_dial(cap, law, variant == "t")


SPECS = ["oxford_eq"]


def write():
    changed = 0
    for stem in SPECS:
        path = os.path.join(ROOT, "specs", f"PluginSpec_{stem}.json")
        with open(path, encoding="utf-8") as f:
            spec = json.load(f)
        for e in spec["elements"]:
            if e.get("kind") != "knob" or not e.get("sprite"):
                continue
            d = dial_for(e["sprite"])
            if d:
                e["dial"] = d
                del e["sprite"]
                changed += 1
        with open(path, "w", encoding="utf-8") as f:
            json.dump(spec, f, indent=1, ensure_ascii=False)
            f.write("\n")
    print(f"{changed} knobs drawn")


def main():
    args = sys.argv[1:]
    if args == ["--write"]:
        write()
    elif len(args) == 2 and args[0] == "--dial":
        d = dial_for(args[1])
        if d is None:
            print(f"no dial for {args[1]}", file=sys.stderr)
            return 1
        print(json.dumps(d, indent=1))
    else:
        print(__doc__.strip())
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())

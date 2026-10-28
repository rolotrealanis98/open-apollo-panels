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
           "yellow": "c8c847", "grey": "9ca6b6", "light grey": "bcc5c8", "purple": "ab59c6"}
# untouched bands are drawn at 81.8 %
EQ_DIM = 0.818


def eq_dial(cap, law, dim, cx=28, cy=29):
    angles, clamp = law
    d = {
        "cx": cx, "cy": cy, "angles": [round(a, 4) for a in angles],
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


# --- Envolution's small knobs: the Oxford EQ knob at about 0.8 of the size

ENV_CAPS = {"yellow": "c8c846", "purple": "ab59c6", "blue": "4675c9"}
ENV_LAW = ([-150, 150], None)


def env_small_dial(cap):
    return {
        "cx": 22, "cy": 22, "angles": ENV_LAW[0],
        "layers": [
            {"type": "ring", "r": [20, 21.5], "fill": {"conic": stops(EQ_RIM)}},
            {"type": "ring", "r": [18.375, 20], "fill": {"conic": stops(EQ_LIP)}},
            {"type": "ring", "r": [12.5, 18.375], "fill": {"conic": stops(EQ_LAND)}},
            {"type": "grooves", "r": [13.625, 18.625], "count": 36, "width": 5.35, "soft": 1.5, "shade": 0.7,
             "fade": [0.4, 0.8]},
            {"type": "ring", "r": [10, 12.5], "fill": {"conic": stops(EQ_CONE)}},
            {"type": "ring", "r": [0, 10], "fill": {"color": "#" + ENV_CAPS[cap].upper(), "linear": [-0.748, -1.194]}},
            {"type": "ring", "r": [9.4, 10], "fill": {"conic": stops(EQ_CAP_EDGE)}},
            {"type": "glow", "r": [8.6, 20.8], "color": "#FDF540", "alpha": 0.49, "sigma": 1.72},
            {"type": "slot", "r": [13.1, 18.95],
             "profile": [[0, "#FCF883"], [0.4, "#FCF883"], [0.6, "#FCEE02"], [0.8, "#E2DC3A"], [1.0, "#C9CA72"],
                         [1.4, "#C9CA72"]],
             "profileOut": [[0, "#FCFCB3"], [0.4, "#FCFCB3"], [0.6, "#FCEE02"], [0.8, "#E2DC3A"], [1.0, "#CECE7A"],
                            [1.4, "#CECE7A"]]},
        ],
    }


# --- Envolution's big knobs: navy cap in a dark well, 60 grooves, a fixed index mark at 12 o'clock

ENV_BIG_RIM = {0: "495874", 45: "45556f", 90: "323d50", 135: "293140", 180: "293141", 225: "3a465a", 270: "485773",
               315: "485773"}
ENV_BIG_LIP = {0: "c1c4ca", 45: "9ba0a7", 90: "5b5e65", 135: "42454a", 180: "46494e", 225: "6d7077", 270: "a8acb2",
               315: "c6cacf"}
ENV_BIG_LAND = {0: "999da4", 30: "969aa1", 60: "83878e", 90: "6e7279", 120: "63676e", 150: "5f646a", 180: "5e6269",
                210: "6f7279", 270: "91969c", 300: "a1a5ac", 330: "a5aab1"}
ENV_BIG_BEVEL = {0: "797c82", 45: "83878e", 90: "868a91", 135: "8c8f95", 180: "8a8d94", 225: "848991", 270: "7f8289",
                 315: "777b80"}
ENV_BIG_WELL = {0: "202938", 45: "283346", 90: "303e55", 135: "303e55", 180: "303e55", 225: "2f3d53", 270: "242e3f",
                315: "1d2533"}
ENV_BIG_TICKS = {"yellow": ("8b9020", "737a26", "59602c"), "purple": ("78439a", "653e85", "4f386e")}


def env_big_dial(tick):
    light, mid, dark = ENV_BIG_TICKS[tick]
    return {
        "cx": 41, "cy": 42, "angles": [-135, 135],
        "layers": [
            {"type": "ring", "r": [36, 38], "fill": {"conic": stops(ENV_BIG_RIM)}},
            {"type": "ring", "r": [34.5, 36], "fill": {"conic": stops(ENV_BIG_LIP)}},
            {"type": "ring", "r": [25.75, 34.5], "fill": {"conic": stops(ENV_BIG_LAND)}},
            {"type": "ring", "r": [23.875, 25.75], "fill": {"conic": stops(ENV_BIG_BEVEL)}},
            {"type": "grooves", "r": [25.75, 34.75], "count": 60, "width": 3, "soft": 1, "shade": 0.8,
             "fade": [0.5, 0.5]},
            {"type": "ring", "r": [18, 23.875], "fill": {"conic": stops(ENV_BIG_WELL)}},
            {"type": "slot", "r": [17, 22], "angle": 0,
             "profile": [[-1, "#" + light.upper()], [-0.25, "#" + light.upper()], [0, "#" + mid.upper()],
                         [0.25, "#" + dark.upper()], [1, "#" + dark.upper()]]},
            {"type": "ring", "r": [0, 18], "fill": {"color": "#48566E", "linear": [0.868, 1.508]}},
            {"type": "glow", "r": [25, 37], "color": "#FDF540", "alpha": 0.5, "sigma": 1.6},
            {"type": "slot", "r": [25.75, 35.75],
             "profile": [[0, "#FAF9A4"], [0.25, "#FAF9A4"], [0.5, "#FCFA53"], [0.75, "#FEFC02"], [1.0, "#FEFC02"]]},
        ],
    }


# --- Oxford Dynamic EQ: flat grey discs, a black and yellow capsule pointer under a dark inner ring

def dyn_eq_dial(on):
    d = {
        "cx": 22, "cy": 22, "angles": [-135, 135],
        "layers": [
            {"type": "ring", "r": [20.75, 22.5], "fill": {"color": "#22252A"}},
            {"type": "ring", "r": [22.5, 23.25], "fill": {"color": "#22252A80"}},
            {"type": "ring", "r": [9.75, 20.75], "fill": {"color": "#767C88", "linear": [0, 0, 0, -1.318, -1.204, -0.976]}},
            {"type": "ring", "r": [0, 9.75], "fill": {"color": "#9BA2AF", "linear": [0, 0, 0, -0.726, -0.592, -0.364]}},
            {"type": "capsule", "r": [11, 16.5], "width": 6, "color": "#171717"},
            {"type": "capsule", "r": [11, 16.5], "width": 2, "color": "#FFE666"},
            {"type": "ring", "r": [9.75, 12.25], "opacity": 0.73,
             "fill": {"radial": [[10, "#73777C"], [10.5, "#424445"], [11, "#323234"], [11.5, "#27282B"],
                                 [12, "#5C5E64"]]}},
        ],
    }
    if not on:
        d["tint"] = {"mul": 0.5, "add": "#101218"}
    return d


# Oxford EQ cap colours by band parameter (channel A numbering; channel B is 32 higher)
EQ_BAND_CAPS = {3: "grey", 6: "light grey", 8: "cyan", 11: "blue", 12: "blue", 14: "blue", 16: "green", 17: "green",
                18: "green", 20: "red", 21: "red", 22: "red", 24: "orange", 25: "orange", 26: "orange", 29: "yellow",
                30: "yellow", 32: "yellow"}
EQ_SHELF_CAPS = {"ALFs": "blue", "BLFs": "blue", "AHFs": "yellow", "BHFs": "yellow"}
EQ_SPRITE = re.compile(r"^(?:R_|R__|F_|FP_)Oxford-EQ_(?:(B)_)?(?:([AB][LH]Fs)_)?p(\d+)_0(?:_(t|lit))?$")


ENV_SPRITE = re.compile(r"^F_Oxford-Envolution_p(\d+)_0$")
ENV_SMALL = {1: "yellow", 4: "yellow", 16: "purple", 27: "blue", 28: "blue"}
ENV_MEDIUM = {2: "yellow", 3: "yellow", 14: "purple", 15: "purple"}
ENV_BIG = {0: "yellow", 13: "purple"}
# the sidechain knobs; the band knobs (bandN) still wait for photos to check against
DYN_SPRITE = re.compile(r"^(?:R_|F_)Oxford-Dynamic-EQ_p(1[5-8])_0(_en)?$")


def dial_for(sprite):
    m = ENV_SPRITE.match(sprite)
    if m:
        n = int(m.group(1))
        if n in ENV_SMALL:
            return env_small_dial(ENV_SMALL[n])
        if n in ENV_MEDIUM:
            return eq_dial(ENV_MEDIUM[n], ENV_LAW, False, cx=29, cy=29)
        if n in ENV_BIG:
            return env_big_dial(ENV_BIG[n])
        return None
    m = DYN_SPRITE.match(sprite)
    if m:
        return dyn_eq_dial(bool(m.group(2)))
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


SPECS = ["oxford_eq", "oxford_envolution", "oxford_dynamic_eq"]


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

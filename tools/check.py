#!/usr/bin/env python3
"""Check the panel specs before a commit or a release.

  python3 -I tools/check.py [--schema]

- specs/ holds only PluginSpec_<name>.json files, and the repository holds no
  images, fonts, archives or binaries;
- every spec is JSON with "schema": 2 and none of the maintainer-only keys;
- no string is prose (long texts are referenced through stringRef/stepsRef and
  read from the user's own install), embedded data (base64, data: URIs, SVG
  paths), a file path, a hex address, a DLL name or a copyright line;
- with --schema, every spec validates against
  schema/plugin-spec-v2.schema.json (needs the jsonschema module).

Exit status: 0 clean, 1 findings, 2 a bad option or missing module.
"""
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPEC_NAME = re.compile(r"^PluginSpec_[a-z0-9_]+\.json$")
DENIED_EXT = {
    ".png", ".bmp", ".jpg", ".jpeg", ".gif", ".webp", ".tif", ".tiff", ".ico", ".svg", ".ttf", ".otf", ".woff",
    ".woff2", ".dll", ".exe", ".so", ".dylib", ".bin", ".zip", ".gz", ".xz", ".zst", ".7z", ".tar", ".mpk",
}
# maintainer metadata: top-level keys, and a meter source's provenance
INTERNAL_TOP = {"_images", "provenance", "notes", "todo", "meters"}
PATTERNS = {
    "dll name": re.compile(r"\.dll\b", re.I),
    "hex address": re.compile(r"\b0x[0-9a-fA-F]{6,}\b"),
    "file path": re.compile(r"/home/|/Users/|~/|[A-Za-z]:\\|drive_c"),
    "date": re.compile(r"\b20\d\d-\d\d-\d\d\b"),
    "embedded data": re.compile(r"data:[\w/+.-]+;base64|[A-Za-z0-9+/]{120,}={0,2}"),
    "SVG": re.compile(r"<svg|<path|\bd=\"[Mm]"),
    "copyright": re.compile(r"©|copyright|all rights reserved", re.I),
}
PROSE_CHARS, PROSE_WORDS = 80, 12


def is_prose(s):
    return "\n" in s or len(s.split()) > PROSE_WORDS or (len(s) > PROSE_CHARS and " " in s)


def tracked_files():
    try:
        out = subprocess.run(["git", "-C", ROOT, "ls-files", "-z"], capture_output=True, check=True).stdout
        return [p for p in out.decode().split("\0") if p]
    except (OSError, subprocess.CalledProcessError):
        files = []
        for d, dirs, names in os.walk(ROOT):
            dirs[:] = [x for x in dirs if x not in (".git", "dist")]
            files += [os.path.relpath(os.path.join(d, n), ROOT) for n in names]
        return files


def walk(v, path, out):
    if isinstance(v, dict):
        for k, x in v.items():
            if (not path and k in INTERNAL_TOP) or (path.startswith(".meterSources.") and k == "provenance"):
                out.append(f"maintainer-only key {path}.{k}")
            walk(x, f"{path}.{k}", out)
    elif isinstance(v, list):
        for i, x in enumerate(v):
            walk(x, f"{path}[{i}]", out)
    elif isinstance(v, str):
        for name, rx in PATTERNS.items():
            if rx.search(v):
                out.append(f"{name} in {path}: {v[:60]!r}")
        if is_prose(v):
            out.append(f"prose in {path} ({len(v)} characters): reference it with stringRef/stepsRef")


def main():
    use_schema = "--schema" in sys.argv[1:]
    if any(a not in ("--schema",) for a in sys.argv[1:]):
        print(__doc__.strip())
        return 2
    validator = None
    if use_schema:
        try:
            from jsonschema import Draft202012Validator
        except ImportError:
            print("--schema needs the jsonschema module (pip install jsonschema)")
            return 2
        with open(os.path.join(ROOT, "schema", "plugin-spec-v2.schema.json")) as f:
            validator = Draft202012Validator(json.load(f))

    findings = []
    for rel in tracked_files():
        if os.path.splitext(rel)[1].lower() in DENIED_EXT:
            findings.append(f"{rel}: binary or image files don't belong here")
        if rel.startswith("specs/") and not SPEC_NAME.match(os.path.basename(rel)):
            findings.append(f"{rel}: specs/ holds only PluginSpec_<name>.json files")

    specs = sorted(n for n in os.listdir(os.path.join(ROOT, "specs")) if SPEC_NAME.match(n))
    for name in specs:
        try:
            with open(os.path.join(ROOT, "specs", name), encoding="utf-8") as f:
                spec = json.load(f)
        except (OSError, ValueError) as e:
            findings.append(f"{name}: not JSON ({e})")
            continue
        if not isinstance(spec, dict) or spec.get("schema") != 2:
            findings.append(f"{name}: \"schema\" must be 2")
            continue
        out = []
        walk(spec, "", out)
        findings += [f"{name}: {x}" for x in out]
        if validator:
            for err in list(validator.iter_errors(spec))[:5]:
                findings.append(f"{name}: {err.json_path}: {err.message[:160]}")

    for x in findings:
        print(x)
    print(f"{len(specs)} specs checked, {len(findings)} findings")
    return 1 if findings or not specs else 0


if __name__ == "__main__":
    sys.exit(main())

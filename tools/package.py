#!/usr/bin/env python3
"""Build the release tarball open-apollo installs.

  python3 -I tools/package.py [--out DIR]

Writes DIR/open-apollo-panels-<VERSION>.tar.gz (default DIR: dist/) and a
.sha256 next to it, and prints the lines for open-apollo's
packaging/plugin-panels.conf. The tarball holds VERSION, LICENSE, README.md,
NOTICE.md and specs/ with every spec minified, under one top folder. The
output is byte-for-byte reproducible: sorted entries, fixed times, no owners.
"""
import gzip
import hashlib
import io
import json
import os
import re
import sys
import tarfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPEC_NAME = re.compile(r"^PluginSpec_[a-z0-9_]+\.json$")
DOCS = ("VERSION", "LICENSE", "README.md", "NOTICE.md")
MTIME = 946684800  # 2000-01-01, so the hash depends only on the content


def entry(tar, name, data, mode=0o644):
    info = tarfile.TarInfo(name)
    info.size, info.mode, info.mtime = len(data), mode, MTIME
    info.uid = info.gid = 0
    info.uname = info.gname = ""
    tar.addfile(info, io.BytesIO(data))


def folder(tar, name):
    info = tarfile.TarInfo(name)
    info.type, info.mode, info.mtime = tarfile.DIRTYPE, 0o755, MTIME
    info.uid = info.gid = 0
    info.uname = info.gname = ""
    tar.addfile(info)


def main():
    args = sys.argv[1:]
    out_dir = os.path.join(ROOT, "dist")
    if args[:1] == ["--out"] and len(args) == 2:
        out_dir = args[1]
    elif args:
        print(__doc__.strip())
        return 2
    with open(os.path.join(ROOT, "VERSION")) as f:
        version = f.read().strip()
    if not re.fullmatch(r"[0-9][0-9A-Za-z.+-]*", version):
        print(f"VERSION {version!r} is not a plain version string")
        return 1
    top = f"open-apollo-panels-{version}"
    specs = sorted(n for n in os.listdir(os.path.join(ROOT, "specs")) if SPEC_NAME.match(n))
    if not specs:
        print("specs/ is empty")
        return 1

    raw = io.BytesIO()
    with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0, compresslevel=9) as gz:
        with tarfile.open(fileobj=gz, mode="w", format=tarfile.USTAR_FORMAT) as tar:
            folder(tar, top)
            for name in DOCS:
                with open(os.path.join(ROOT, name), "rb") as f:
                    entry(tar, f"{top}/{name}", f.read())
            folder(tar, f"{top}/specs")
            for name in specs:
                with open(os.path.join(ROOT, "specs", name), encoding="utf-8") as f:
                    spec = json.load(f)
                data = json.dumps(spec, separators=(",", ":"), ensure_ascii=False).encode() + b"\n"
                entry(tar, f"{top}/specs/{name}", data)

    os.makedirs(out_dir, exist_ok=True)
    tarball = os.path.join(out_dir, f"{top}.tar.gz")
    with open(tarball, "wb") as f:
        f.write(raw.getvalue())
    digest = hashlib.sha256(raw.getvalue()).hexdigest()
    with open(tarball + ".sha256", "w") as f:
        f.write(f"{digest}  {top}.tar.gz\n")
    print(f"{tarball}: {len(specs)} specs, {len(raw.getvalue())} bytes")
    print(f"PANELS_VERSION={version}")
    print(f"PANELS_SHA256={digest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

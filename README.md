# open-apollo-panels

Layouts for the plug-in editor panels of [open-apollo](https://github.com/rolotrealanis98/open-apollo)'s
console. Each `specs/PluginSpec_<plug-in>.json` describes one panel: its size, where each knob, switch, meter
and label sits, which parameter each control drives, and how a value maps to a frame or a readout.

open-apollo's setup installs a pinned release of these specs into `/usr/share/open-apollo/plugin-specs`. You
don't need this repository unless you work on the panels.

## What a spec holds, and what it doesn't

- **Positions, sizes, parameter indices, step counts, colours and display laws.** These are measurements.
  Elements that open-apollo draws itself (toolbars, labels, vector shapes, lamps) carry their own geometry and
  colours.
- **No art.** Every sprite is a *recipe id* such as `chrome.bx.power`. open-apollo's importer (`oa-assets
  plugins`) builds the image from the user's own UAD install and checks its SHA-256.
- **No long texts.** Descriptions and preset lists are references (`text.stringRef`, `parameters[].stepsRef`)
  that the importer resolves the same way.

The format is specified by [`schema/plugin-spec-v2.schema.json`](schema/plugin-spec-v2.schema.json) and,
for drawing, by open-apollo's `console-rs/crates/plugin-ui/RUNTIME-V2.md`. A spec whose art the importer
can't make yet opens as a plain parameter list, so a panel is never drawn with holes.

## Checks

```sh
python3 -I tools/check.py            # file names, no binaries or images, no prose, paths or embedded data
python3 -I tools/check.py --schema   # also validates every spec against the schema (pip install jsonschema)
```

CI runs both on every push and pull request.

## Releases

`VERSION` holds the release version. Tagging `v<VERSION>` makes CI build
`open-apollo-panels-<VERSION>.tar.gz` with `tools/package.py`. The tarball holds the minified specs and is
reproducible byte for byte. CI attaches the tarball and its `.sha256` to a GitHub release. open-apollo pins the
version and SHA-256 in `packaging/plugin-panels.conf`, and its setup refuses a download that doesn't match.

## License

The specs, the schema and the tools are dedicated to the public domain under [CC0 1.0](LICENSE). See
[NOTICE.md](NOTICE.md) for the names they mention.

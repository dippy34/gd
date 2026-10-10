# Workflow

Run commands from the repository root. The examples use `python3`; the owner's
Mac requires the local `rtk proxy` prefix. Python 3.9+ works for the portable tools.
An [optional GitHub Actions template](ci/README.md) is included as documentation;
automated CI is not installed because the connected login lacks workflow scope.

No account, API key, GD installation or downloaded song is needed to inspect
files, run data checks or read the existing visual examples.

## Inspect before editing

```sh
python3 tools/validate_repo.py
python3 -m unittest discover -s tests -v
python3 tools/gd_project.py inspect "outputs/The Sinking Factory - CUSTOM-ORBS.gmd"
python3 tools/gd_project.py region "outputs/The Sinking Factory - CUSTOM-ORBS.gmd" --x0 22030 --x1 22100 --limit 12
python3 tools/gd_project.py diff "inputs/The Sinking Factory.gmd" "outputs/The Sinking Factory - CUSTOM-ORBS.gmd" --limit 10
```

`region` reports object **centers**, not full animated/collision extents. `diff`
aligns objects by index; it is useful for this preserved-source workflow but not
a general matcher for arbitrarily reordered levels. Both limit large output.

The repository check hashes and parses every cataloged source/export, verifies
the current baseline and curated links, and runs the complete factory regression.
It writes `build/repo-validation.json`; that directory is ignored by Git.

## Make a separate candidate

```sh
python3 tools/gd_project.py copy "outputs/The Sinking Factory - CUSTOM-ORBS.gmd" "build/factory-candidate.gmd" --name "Factory Candidate"
```

This keeps the compressed level string unchanged, renames the copy, resets its
local ID/verification metadata and sets the measured count. It refuses to
overwrite any existing destination. Merely renaming a copy is not a new design.
Never overwrite the source or approved baseline during experiments.

## Optional native-atlas setup

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

Set `GD_RESOURCES` to the Resources directory of **your own** GD installation,
containing `GJ_GameSheet-hd.plist`, matching `.png` sheets, and the font resources.
The renderer defaults to the usual macOS Steam location under the current user's
home; another OS/location needs the environment variable. Atlases are not
included. Missing resources produce a clear error instead of blank output.

## Sandboxed baseline rebuild

```sh
.venv/bin/python tools/build_factory.py --out build/factory-rebuild
python3 tools/gd_project.py diff "outputs/The Sinking Factory - CUSTOM-ORBS.gmd" "build/factory-rebuild/The Sinking Factory - CUSTOM-ORBS.gmd"
```

The repository migration tested this wrapper with Python 3.9, NumPy 2.0.2,
Pillow 11.3.0 and Shapely 2.0.7 against the local game atlases. The rebuilt GMD
matched the selected baseline **byte-for-byte**. See the recorded
[tooling checks](../catalog/tooling-checks.json). This is data reproducibility,
not native gameplay validation.

The wrapper copies the needed factory inputs into a temporary tree, runs the
builder and full validator, then saves the generated `.gmd`, raw level, manifest
and report in a new output directory. Existing exports are never overwritten.
The active build uses the saved measured-onset list, so the song WAV is not needed.
The atlas is still needed for native sprite dimensions and classifications.

The historical pipeline uses shared helper code and `exec` of successive art
passes. The active path is `build_custom_orbs.py` → `refined_art.py` →
`foundry_art.py` and its predecessor art helpers, plus `custom_orbs_parts.py`.
Treat a module import as potentially executing a build. Prefer the wrapper over
importing historical scripts into a live session. Do not indiscriminately run all
old builders, because many write their named historical exports directly.

## Visual iteration

1. State which component changes and which objects/mechanics must be preserved.
2. Inspect source geometry, layers, moving groups, palette and camera context.
3. Produce one coherent assembly; review its endpoints, silhouette and lighting.
4. Render before/after at matched camera/zoom/time. Inspect motion extremes,
   transitions, the cube/UFO gaps and the final hazards.
5. Run data checks appropriate to the change. Check original object diffs and
   ensure added decoration is passable and isolated from gameplay groups.
6. Import the separate candidate into GD for native checks when access exists.
   Test size/gravity/portal transitions, moving orbs, exit visibility and FPS.
7. Report exact file, hash, what changed, images and which checks were possible.
   An approximate renderer cannot establish playability or rating quality.

To inspect the existing Custom-era component previews, use the checked-in images.
`preview_custom.py` targets CUSTOM, including its now-reverted portal experiment;
do not present that as an exact Factory Orbs screenshot. For new work, configure
a preview against the actual candidate and document all rendering limitations.

## Promote only the intended revision

Keep old exports. Add the new export and its evidence, update `project-state.json`
and `catalog/artifacts.json`, update visual captions and regression expectations,
then run the repository checks. Do not relabel a candidate “approved” without
owner feedback. Use precise statuses such as candidate, retained component,
rejected or superseded. Native verification remains a separate status.

The older v8 pipeline is retained for inspection, not covered by the active
factory rebuild guarantee. Its copied plans may contain `$PROJECT_ROOT`/`$HOME`
placeholders in historical provenance. Some legacy scripts require omitted
audio/reference assets. See [history](HISTORY.md) before running them.

# Geometry Dash — factory build and AI handoff

A complete project archive plus a curated guide for Claude Opus or another agent
to continue **The Sinking Factory** without losing the owner's design decisions.

**Start with [Factory Orbs (CUSTOM-ORBS.gmd)](outputs/The%20Sinking%20Factory%20-%20CUSTOM-ORBS.gmd).**
This is the retained baseline before the discarded fire-border experiments.
Its accepted components are preserved; that does not mean every remaining part
has final aesthetic approval. The latest custom-art fire experiment is omitted.

![Preserved ship design — approximate atlas rendering](work/sinking-factory/refined-ship.png)

## For Opus and other agents

1. Read [START HERE](docs/START_HERE.md), [current state](docs/PROJECT_STATE.md),
   and [design guide](docs/DESIGN_GUIDE.md).
2. **Open** the images in [visual examples](docs/VISUAL_EXAMPLES.md). They label
   preserved components, rejected additions and unfinished coverage separately.
3. Read [AGENTS.md](AGENTS.md) / [CLAUDE.md](CLAUDE.md), then use the
   [onboarding prompt](docs/OPUS_PROMPT.md).
4. Inspect [real object examples](examples/README.md) and run the checks below.

The guides explain *why* something works: mounted machinery, fitted metal skins,
dark depth, localized furnace light, falling ash, clear hazard silhouettes and
section-specific design. They also explain why random protrusions, clutter and
reused gameplay were rejected. No model has been fine-tuned by this repository.

## Quick check — no game installation required

```sh
python3 tools/validate_repo.py
python3 -m unittest discover -s tests -v
python3 tools/gd_project.py inspect "outputs/The Sinking Factory - CUSTOM-ORBS.gmd"
```

Python 3.9+; these commands use only the standard library. Run from this directory.
On the owner's Mac, use the local `rtk proxy` prefix for shell commands.

Native atlas previews/rebuilds require your own Geometry Dash resources and the
optional [requirements](requirements.txt). See [workflow](docs/WORKFLOW.md).
Checked-in previews remain usable without those assets.

## What is where

| Path | Purpose |
| --- | --- |
| [project-state.json](project-state.json) | Machine-readable active baseline, song, boundaries and invariants |
| [docs/](docs/START_HERE.md) | Visual taste, project history, technical details, QA and onboarding |
| [examples/](examples/README.md) | Real orb/group/layer excerpts and feedback-to-action examples |
| [inputs/](inputs/README.md) | Immutable source `.gmd` files supplied for this work |
| [outputs/](outputs/README.md) | Exported revisions, previews, reports and historical notes |
| [work/sinking-factory/](work/sinking-factory/LATEST.md) | Factory builders, raw levels, manifests and detailed previews |
| [work/](work/ARCHIVE.md) | Earlier v8 gameplay pipeline, reports and revision backups |
| [tools/](docs/WORKFLOW.md) | Portable inspection, copying, diffing, repository checks and safe rebuild wrapper |
| [catalog/](catalog/README.md) | Export hashes/statuses and full migration inclusion/exclusion inventory |

The large archive is kept so earlier designs and checks are recoverable. Read the
curated guides first; do not load every raw `.level` or multi-megabyte plan into
an agent context. [History](docs/HISTORY.md) separates the two different projects.

## Verification and ownership

The active factory's data regression checks pass locally, including the orb-follow
fix, native portal restoration, custom orb preservation, scope and editor layers. An optional
[GitHub Actions template](docs/ci/README.md) is included; it is not installed.
**Native gameplay, camera behavior and performance are not certified.** Diagnostic
previews are labeled; passing a script does not prove a feature/rate-worthy level.

Downloaded songs, game sprite atlases, full reference-level dumps, installed
dependencies, private chat screenshots and the disregarded custom-art experiment
are omitted. [Migration details](catalog/migration.json) enumerate exclusions.
See [assets and attribution](docs/ASSETS_AND_ATTRIBUTION.md) for provenance. The
repository makes no blanket license claim over collaborators' levels or artwork.

# Maintaining the illustrated guide

The [12-page guide](VISUAL_EXAMPLES.md) is checked in as PNGs so GitHub and
multimodal agents can open it without game resources or rendering dependencies.
The original screenshots remain unchanged. The boards are technical figures:
source images, presentation crops, numbered annotations and explanatory diagrams.
No source image was repainted, brightened or replaced with generated art.

## Source of truth

- [visual-guide.json](visual-guide.json): source hashes and sizes, crops in source
  pixels, numbered callouts, owner-feedback paraphrases, assistant analysis and
  proposal status. The two are separate fields; do not turn an interpretation
  into a quote or a claim of owner approval.
- [build_visual_guide.mjs](../tools/build_visual_guide.mjs): figure layouts and
  schematic drawing code. Diagrams 10–12 are illustrations, not GD screenshots.
- [rendered.json](images/visual-guide/rendered.json): hashes of generated pictures,
  the source manifest and the renderer. Changes require regeneration.
- [VISUAL_SOURCES.md](VISUAL_SOURCES.md): the original unannotated views and context.

Evidence is component-specific. For example, the early robot image supports
preserving the scene idea, while its old outline spikes were later criticized.
The native portal comparison uses historical diagnostic crops, not an asserted
frame from CUSTOM-ORBS running in the game. No image establishes a rating.

## Rebuild

Viewing and validating the guide only needs Python 3.9+ for the existing checks.
Rebuilding requires Node.js 20+ and `sharp` 0.34+ (optional development tool).
Install it outside the repository if desired:

```sh
npm install --prefix /tmp/gd-visual-tools sharp@0.34
SHARP_MODULE=/tmp/gd-visual-tools/node_modules/sharp node tools/build_visual_guide.mjs
python3 tools/validate_repo.py
```

On the owner's Mac, prefix shell commands with `rtk proxy` and use
`rtk proxy env SHARP_MODULE=... node tools/build_visual_guide.mjs` for the environment
variable. If `sharp` already resolves normally, the variable is unnecessary.
Use Arial or DejaVu Sans. Font/platform changes can change rasterization and
therefore generated hashes; visually review every changed figure.

Intermediate SVGs (with embedded source pixels) are written under the ignored
`build/visual-guide/` directory. Only the PNGs and small JSON records are tracked;
there is no duplicated game asset bundle or external web font dependency.

## Add a case

1. Save an appropriate source image and record its revision and evidence type.
   Crop private conversation UI out before publication; never publish private
   messages as visual teaching material. Game/editor-only sources are preferred.
2. Record the original size and hash. Put crop coordinates in source pixels.
   Mark the actual feature; do not select an approximate box without looking.
3. Describe the observed problem, the owner's decision and your interpretation
   separately. Say which part is preserved, rejected, superseded or unreviewed.
4. Add the picture and accessible explanation to the guide, then rebuild.
5. Open the PNG at full size. Check text, crop, marker placement and evidence
   labels; automated file checks cannot judge those visual relationships.

Do not imply a screenshot was captured natively if it was rendered by a script.
For new before/after evidence, capture matching camera/time/aspect and movement
extremes. The mismatched historical comparisons here are explicitly labeled.

The visual manifest describes documentation, not the level's artifact catalog.
The original migration inventory remains a record of that earlier import; it is
not rewritten to pretend these new diagrams were historical project assets.

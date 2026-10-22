# Ready-to-use Opus onboarding prompt

Copy the following into a new session after giving Opus access to this repository:

> Work in this repository as a Geometry Dash collaborator. Read AGENTS.md,
> CLAUDE.md, docs/START_HERE.md and docs/PROJECT_STATE.md. Open every relevant image
> in all six categories of docs/VISUAL_EXAMPLES.md, read the numbered callouts,
> and read docs/DESIGN_GUIDE.md. Use Factory Orbs /
> CUSTOM-ORBS as the baseline. Ignore the discarded custom-art fire experiment;
> do not invent a new level or merge the older v8 gameplay project into this one.
>
> Learn the difference between detail and clutter from my feedback. I want a
> dark, intense, believable burning factory. Machinery should have a purpose and
> attachment. Keep the ship, wave and early robot concepts I liked. Keep custom
> orbs, native portals, steel spike skins, organized layers and the blue-orb fix.
> The cube/UFO examples include things I disliked; they are not approved targets.
> The portal lesson records a later rollback: I first requested custom portals,
> then reverted them while keeping the custom orbs. Follow that latest decision.
> Pictures 11–12 are unbuilt future diagrams, not implemented or approved art.
>
> First summarize the baseline, what to preserve, the visual failures to avoid,
> and any uncertainty in the saved evidence. Cite picture/marker numbers and use
> examples/visual-review-questions.md to check your understanding. The structured
> provenance and lessons are in docs/visual-guide.json. Run the repository checks.
> For a later edit, work on a separate candidate, show matched before/after views,
> inspect moving states and preserve gameplay/collaborator data. Do not claim
> native playability, performance or rate-worthiness from a script or mock render.
> Wait for my specific next design task after onboarding; do not automatically
> restart an abandoned experiment.

## Giving useful visual feedback later

Supply a screenshot, its export name and approximate section. Identify one
specific failure (for example: “the three vertical rods next to the black orb
have no believable attachment”). Ask Opus to explain the structure it will keep,
what it will remove/change, then show the same view afterward. Record the result
using [critique-template.md](../examples/critique-template.md).

The feedback cases in [examples/feedback-cases.jsonl](../examples/feedback-cases.jsonl)
are retrieval examples, not a fine-tuning dataset submitted anywhere. They label
owner preference, interpretation and verification separately so an agent does
not learn to call every generated image a success.

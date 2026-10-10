# Optional GitHub Actions validation

`validate.yml` is a ready-to-use workflow template, **not an installed workflow**.
The GitHub OAuth credential used for the handoff allowed repository content but
lacked the `workflow` scope, so GitHub rejected creating a workflow. No account
permissions were changed. The template was moved here and the initial commit
was rebuilt before pushing the project.

The local equivalent has passed:

```sh
python3 tools/validate_repo.py
python3 -m unittest discover -s tests -v
```

If the owner later wants automated CI, a GitHub login with workflow-management
permission can place this file at `.github/workflows/validate.yml` and commit it.
It runs the same dependency-free data regression and unit tests on Python3.11.
It does not launch Geometry Dash, fetch songs or game assets, or prove native
gameplay/performance.

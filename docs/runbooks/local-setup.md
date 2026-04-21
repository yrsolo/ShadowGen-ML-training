# Local Setup

This repository is prepared for Windows development.

## Requirements

- Windows shell: PowerShell.
- Python `>=3.12`.
- `uv`.
- Git.
- Access to `\\riper\datasets`.

## Setup

```powershell
cd N:\PROJECTS\ML\ShadowGen-ML-core\ShadowGen-ML-training
uv sync
$env:SHADOWGEN_DATASET_ROOT="\\riper\datasets"
uv run shadowgen-training doctor
uv run shadowgen-training inspect-dataset --root "\\riper\datasets"
uv run shadowgen-training validate-config configs/project.yaml
uv run pytest -q
```

## Notes

- The scaffold does not train a model yet.
- The dataset command only checks top-level accessibility and does not index,
  copy, cache, or mutate data.
- Tracker and artifact services are intentionally disabled until the next step.

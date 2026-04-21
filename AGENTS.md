# AGENTS.md

This repository contains the training-side code and documentation for the
ShadowGen shadow generation model.

## Scope

- Work only on training, evaluation, dataset preparation interfaces, model export
  preparation, and contract validation.
- Do not add service runtime code, API handlers, Triton deployment code, or
  product pipeline orchestration here.
- Do not hard-code one diffusion architecture until the model selection step is
  explicitly opened.

## Artifact Safety

- Never commit raw data, generated images, videos, model checkpoints, exported
  models, W&B runs, MLflow runs, caches, or archives.
- Keep dataset paths external. The current Windows dataset root is
  `\\riper\datasets`.
- If a command generates artifacts, keep them under ignored output directories.

## Engineering Defaults

- Prefer small, testable Python modules under `src/shadowgen_training`.
- Keep CLI commands lightweight and safe to run on Windows.
- Use `configs/project.yaml` as the initial project-level source of truth.
- Update docs when public behavior or repository policy changes.

## Validation Before Publishing

Run:

```powershell
uv sync
uv run shadowgen-training doctor
uv run shadowgen-training validate-config configs/project.yaml
uv run pytest -q
```

Also inspect `git status --short` and ensure the index contains only text files.

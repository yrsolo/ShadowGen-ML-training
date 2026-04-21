# Artifact Policy

This repository is public and text-only.

## Allowed in Git

- Source code.
- Tests.
- YAML/TOML/JSON configuration.
- Markdown documentation.
- Text snapshots of model contracts and design discussions.

## Not Allowed in Git

- Raw datasets.
- Processed datasets.
- Generated images, masks, videos, or visual reports.
- Model weights, checkpoints, LoRA adapters, ControlNet weights, ONNX exports,
  TensorRT engines, or Triton model repositories.
- W&B runs, MLflow runs, local caches, archives, and temporary experiment output.

## Current External Data Root

The current Windows dataset location is:

```text
\\riper\datasets
```

The path may be referenced in docs and configs, but the data itself must remain
outside the repository.

## Before Commit

Run:

```powershell
git status --short
git ls-files
```

The Git index must contain only text files.

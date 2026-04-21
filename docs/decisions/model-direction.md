# Model Direction

Status: accepted direction for the next implementation phase.

Source context:

- `docs/discussions/2026-04-21-model-selection-chatgpt-share.md`
- `docs/discussions/2026-04-21-training-pipeline-chatgpt-share.md`
- User decisions on 2026-04-21.

## Goal

Train a modern diffusion-based model for realistic shadow generation from an
object input and object mask. The model must support production-style inference
where the original object can be composited back on top for visual precision.

## Hardware Target

- Training target: 24 GB VRAM, RTX 4090 class.
- Inference target: 11 GB VRAM.
- Training code may use larger-model adaptation techniques if inference can be
  compressed, optimized, quantized, distilled, or otherwise made practical for
  the 11 GB target.

## Model Direction

The preferred product direction is adaptation of a large pretrained diffusion
model, not training only a small model from scratch.

First serious backbone:

- Stable Diffusion 1.5.

Candidate adaptation methods:

- LoRA.
- ControlNet-style conditioning.
- Control-LoRA hybrid.

Other families from the discussion, such as FLUX-like, SD3-like, or SANA-like
models, remain future candidates rather than the first serious backbone.

## Baseline Policy

Use a toy or small conditional diffusion baseline before the serious SD1.5 work
to test the training pipeline quickly:

- data loading,
- target extraction,
- W&B logging,
- qualitative panels,
- overfit-on-tiny-subset smoke tests,
- reproducible configs.

This toy baseline is not the intended product baseline. The intended product
baseline is SD1.5 adapted with LoRA, ControlNet-style conditioning, or a hybrid
approach.

## Output Policy

The model output is treated as `shadow_layer`. Pixels inside the object mask are
not important for shadow quality because inference will place the original object
on top.

Practical evaluation note:

- `shadow_layer`: model output and contract-compatible tensor.
- `composite_preview`: visual QA image made by overlaying the original object on
  the model output.
- Losses and metrics should focus on the non-object region unless a later model
  explicitly learns useful content under the mask.

## Initial Data Assumption

Available data currently includes:

- ready composite image with shadow,
- object mask.

Current dataset path:

```text
\\riper\datasets\3D\final_objaverse_v1
```

Shadow target can be derived by treating everything outside the object mask as
shadow/background signal. This must be validated carefully because the target may
include white background and any residual non-shadow artifacts.

## Current Open Technical Risk

The dataset may not contain explicit labels for light angle, elevation, softness,
or reflection. If those labels are missing, the first large-model adaptation must
either:

- estimate controls from the composite,
- train without full control labels first,
- synthesize labels from controlled data generation,
- or postpone strict control conditioning until labels exist.

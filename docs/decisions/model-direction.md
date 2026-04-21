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

Candidate families from the discussions:

- FLUX-like diffusion with LoRA and image/mask conditioning.
- SD3-like diffusion with ControlNet-style conditioning.
- Control-LoRA hybrid.
- SANA-like efficient diffusion only as an experimental candidate, not the safest
  first choice.

The repository should not hard-code a specific backbone until the dataset and
evaluation loop are validated.

## Baseline Policy

Use a toy or small conditional diffusion baseline only if it helps test the
training pipeline quickly:

- data loading,
- target extraction,
- W&B logging,
- qualitative panels,
- overfit-on-tiny-subset smoke tests,
- reproducible configs.

This toy baseline is not the intended product baseline. The intended product
baseline remains a large pretrained diffusion model adapted with LoRA,
ControlNet-style conditioning, or a hybrid approach.

## Output Policy

Product-facing inference should produce a ready image with a realistic shadow,
then composite the original object on top for exact object fidelity.

Important contract note:

- The current `shadow-v2` service contract still defines the model output as a
  standalone RGBA `shadow` tensor.
- Until that contract is changed, training/evaluation may create ready composite
  previews, but export must either produce the `shadow` tensor or document an
  approved contract deviation.

Practical next step:

- Keep both targets in the pipeline vocabulary:
  - `shadow_layer`: model-contract-compatible output.
  - `composite_preview`: white-background object-plus-shadow image for visual QA.

## Initial Data Assumption

Available data currently includes:

- ready composite image with shadow,
- object mask.

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

# Next Model Step

The next implementation phase is dataset inspection and first experiment design.

See also:

- `docs/decisions/model-direction.md`
- `docs/decisions/training-stack.md`
- `docs/decisions/data-versioning.md`
- `docs/decisions/open-questions.md`

## Decisions Already Fixed

- Training target: 24 GB VRAM.
- Inference target: 11 GB VRAM.
- Product direction: adapt a large pretrained diffusion model.
- First serious backbone: Stable Diffusion 1.5.
- Toy/small model is required as a pipeline smoke baseline before the serious
  backbone work.
- Tracking: W&B.
- Data versioning direction: DVC, without S3 for now.
- Dataset path: `\\riper\datasets\3D\final_objaverse_v1`.
- Current data assumption: ready composite with shadow plus object mask.
- The model output is treated as `shadow_layer`. Pixels inside the object mask
  are not important for shadow quality because the original object is overlaid
  later.

## Contract Constraint

The current service contract expects a standalone RGBA `shadow` tensor. For this
training repo, the model output is considered that `shadow_layer` even if values
inside the object mask are imperfect.

- `shadow_layer` for contract compatibility,
- `composite_preview` for visual QA, created by overlaying the original object.

## Immediate Next Steps

1. Inspect `\\riper\datasets\3D\final_objaverse_v1`.
2. Document the available file layout and pairing rules.
3. Prototype shadow target extraction from composite plus object mask.
4. Create a fixed qualitative validation panel.
5. Implement a toy overfit baseline to validate data, W&B, and evaluation.
6. Initialize DVC only after the first dataset version boundary is known.

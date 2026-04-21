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
- Toy/small model is allowed only as a pipeline smoke baseline.
- Tracking: W&B.
- Data versioning direction: DVC.
- Current data assumption: ready composite with shadow plus object mask.
- Product-facing output should be a ready image with the original object
  composited on top for fidelity.

## Contract Constraint

The current service contract still expects a standalone RGBA `shadow` tensor.
Until that contract is changed, the training pipeline should keep both concepts:

- `shadow_layer` for contract compatibility,
- `composite_preview` for visual QA and product-facing evaluation.

## Immediate Next Steps

1. Inspect the ShadowGen-relevant dataset folders under `\\riper\datasets`.
2. Document the available file layout and pairing rules.
3. Prototype shadow target extraction from composite plus object mask.
4. Create a fixed qualitative validation panel.
5. Decide whether a toy overfit baseline is needed before large-model adaptation.
6. Initialize DVC only after the first dataset version boundary is known.

# Next Model Step

The next implementation phase is model selection and first experiment design.

## Decisions To Make

- Base diffusion family.
- Whether the first baseline is LoRA-only, ControlNet-style conditioning, or a
  Control-LoRA hybrid.
- How tensor inputs from the `v2-diff` contract map into model conditioning.
- Whether RGB shadow color is predicted directly or handled by compositor policy.
- How validation panels are generated and where non-Git visual artifacts live.

## Constraints Already Fixed

- Training code must honor the `shadow-v2` model contract.
- Inputs include object RGBA, mask, depth, normal, angle, elevation, softness, and
  reflection.
- Output is a standalone RGBA shadow layer.
- Services, Triton deployment, and product integration stay outside this
  repository for now.

## Recommended First Experiment Shape

Start with a small reproducible baseline that can overfit a tiny subset and
produce qualitative angle/elevation/softness sweeps. Add LoRA or ControlNet only
after the data contract and validation loop are reliable.

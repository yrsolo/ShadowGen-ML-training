# Shadow Prior Strategy

Status: accepted for the first serious model phase.

## Decision

Start with end-to-end shadow prediction.

The first serious SD1.5 adaptation should learn:

```text
object image + mask + optional geometry + scalar controls -> shadow_layer
```

Do not add a separate learned shadow-direction prior model in v1.

## Conditioning Signals

Use explicit conditioning where available:

- object image,
- object mask,
- rendered or estimated depth,
- rendered or estimated normals,
- light angle,
- light elevation,
- softness,
- reflection fixed at `0.0` for now.

The model output is still treated as `shadow_layer`; pixels inside the object
mask are ignored for shadow quality because the original object is overlaid at
inference time.

## Evaluation Instead Of Prior

For v1, direction and geometry control should be enforced through evaluation and
loss design, not through a separate prior model.

Required evaluation themes:

- shadow direction error,
- shadow extent or length,
- contact shadow quality,
- edge softness,
- outside-object masked reconstruction.

## Deferred v2 Option

Add a deterministic coarse projected-shadow control map only if v1 fails on
direction fidelity or contact placement.

Potential v2 signal:

```text
mask + depth + angle/elevation -> coarse projected shadow map
```

This should be a ControlNet-style input hint, not a second generative model.

## Rationale

An early prior model adds another training target, another failure mode, and more
pipeline coupling. The dataset already has render controls, mask, depth, and
normal signals, so v1 should first prove that the end-to-end model can learn
controllable shadows directly.

# Repository Scope

`ShadowGen-ML-training` owns the training-side work for the main ShadowGen
shadow generation model.

## In Scope

- Dataset preparation interfaces and validation checks.
- Model training code and experiment configuration.
- Evaluation metrics and qualitative reports.
- Model card and validation report templates.
- Export preparation for the `shadow-v2` model contract.

## Out of Scope

- Product API, request parsing, and service runtime.
- Object detection, segmentation, depth estimation, normal estimation, and final
  image composition.
- Triton service deployment and runtime fallback behavior.
- Storage of raw data, images, generated samples, model weights, checkpoints, or
  exported model artifacts in GitHub.

## Boundary

The training repository may read the model contract from the service repository
and produce export-ready artifacts later. It must not become the service itself.

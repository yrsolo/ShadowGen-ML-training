# Data Versioning

Status: DVC selected, rollout pending dataset inspection.

Source context:

- `docs/discussions/2026-04-21-training-pipeline-chatgpt-share.md`
- User decision on 2026-04-21: use DVC, dataset will keep growing.

## Decision

Use DVC for dataset versioning, but do not blindly version the entire raw NAS
share as the first step.

Current data root:

```text
\\riper\datasets
```

Raw data remains outside GitHub.

## Why Not Track Everything Immediately

DVC can handle large data, but the painful part is often many files and frequent
small additions:

- hashing many files can take time,
- `dvc status` can become noisy,
- moving raw folder layouts later is annoying,
- tracking unrelated raw datasets makes this training repo harder to reason
  about.

So the first DVC step should be deliberate and narrow.

## Recommended Rollout

1. Inspect the ShadowGen-relevant dataset folders.
2. Create a manifest for the first training subset.
3. Define a processed dataset version boundary, for example
   `shadow_pair_v1`.
4. DVC-track either:
   - the processed dataset directory, if file count is reasonable, or
   - sharded archives plus a manifest, if file count is very high.
5. Commit only DVC metadata and text manifests to Git.
6. Store actual data in a DVC remote chosen later.

## Practical Rule

For the first phase:

- track manifests and processed dataset versions,
- do not DVC-track the whole `\\riper\datasets` root,
- do not commit images or masks directly to Git,
- keep every dataset version reproducible from a manifest.

## Open Decision

Pick the DVC remote after dataset inspection:

- local/NAS DVC remote for fastest Windows workflow,
- S3-compatible remote for portfolio/portable reproducibility,
- or both later.

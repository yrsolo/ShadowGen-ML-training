# Data Versioning

Status: DVC selected, no S3 remote for now.

Source context:

- `docs/discussions/2026-04-21-training-pipeline-chatgpt-share.md`
- User decision on 2026-04-21: use DVC, dataset will keep growing.

## Decision

Use DVC for dataset versioning, but do not blindly version the entire raw NAS
share as the first step.

Current dataset root:

```text
\\riper\datasets\3D\final_objaverse_v1
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
6. Store actual data in a local/NAS DVC remote first.

## Practical Rule

For the first phase:

- track manifests and processed dataset versions,
- do not DVC-track the whole `\\riper\datasets` root,
- do not push the dataset to S3 yet,
- do not commit images or masks directly to Git,
- keep every dataset version reproducible from a manifest.

## Remote Decision

Use a local/NAS DVC remote for the first version. Revisit S3 only after the data
pipeline and dataset boundaries are stable.

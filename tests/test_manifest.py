import json
from pathlib import Path

from shadowgen_training.data.shadow_pair_manifest import (
    build_shadow_pair_manifest,
    object_split,
)


def _touch(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("x", encoding="utf-8")


def test_object_split_is_stable() -> None:
    assert object_split("abc") == object_split("abc")


def test_build_shadow_pair_manifest_skips_missing_records(tmp_path: Path) -> None:
    root = tmp_path / "dataset"
    root.mkdir()
    good_paths = {
        "preview_path": "ok.png",
        "metadata_path": "metadata/ok.json",
        "pass_paths": {
            "object_mask": "passes/object_mask/ok.png",
            "depth_normalized": "passes/depth_normalized/ok.png",
            "normal": "passes/normal/ok.png",
        },
    }
    for rel in [
        good_paths["preview_path"],
        good_paths["metadata_path"],
        good_paths["pass_paths"]["object_mask"],
        good_paths["pass_paths"]["depth_normalized"],
        good_paths["pass_paths"]["normal"],
    ]:
        _touch(root / rel)

    source = {
        "records": [
            {
                "sample_id": "ok",
                "ok": True,
                "uid": "uid-ok",
                "category_groups": "test",
                "lvis_categories": "thing",
                "license": "test",
                "render_params": {"key_azimuth_deg": 10, "key_elevation_deg": 20},
                **good_paths,
            },
            {
                "sample_id": "missing",
                "ok": True,
                "uid": "uid-missing",
                "preview_path": "missing.png",
                "metadata_path": "metadata/missing.json",
                "pass_paths": {},
            },
        ]
    }
    (root / "manifest.json").write_text(json.dumps(source), encoding="utf-8")

    output = tmp_path / "shadow_pair_v1.jsonl"
    summary = tmp_path / "shadow_pair_v1.summary.json"
    result = build_shadow_pair_manifest(
        root=root,
        output=output,
        summary_output=summary,
    )

    assert result.total_records == 2
    assert result.written_records == 1
    assert result.skipped_missing_paths == 1
    rows = [json.loads(line) for line in output.read_text(encoding="utf-8").splitlines()]
    assert rows[0]["sample_id"] == "ok"
    assert rows[0]["target"]["loss_region"] == "outside_object_mask"
    assert summary.exists()

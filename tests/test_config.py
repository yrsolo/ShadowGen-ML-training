from pathlib import Path

from shadowgen_training.cli import _load_yaml, _validate_project_config


def test_project_config_is_valid() -> None:
    root = Path(__file__).resolve().parents[1]
    config = _load_yaml(root / "configs" / "project.yaml")

    assert _validate_project_config(config) == []


def test_first_serious_backbone_is_sd15() -> None:
    root = Path(__file__).resolve().parents[1]
    config = _load_yaml(root / "configs" / "project.yaml")

    assert config["model"]["family"] == "stable_diffusion"
    assert config["model"]["architecture"] == "sd1.5"
    assert config["model"]["toy_baseline_required_for_pipeline_smoke"] is True

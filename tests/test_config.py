from pathlib import Path

from shadowgen_training.cli import _load_yaml, _validate_project_config


def test_project_config_is_valid() -> None:
    root = Path(__file__).resolve().parents[1]
    config = _load_yaml(root / "configs" / "project.yaml")

    assert _validate_project_config(config) == []


def test_scaffold_does_not_select_model_architecture() -> None:
    root = Path(__file__).resolve().parents[1]
    config = _load_yaml(root / "configs" / "project.yaml")

    assert config["model"]["family"] == "unselected"
    assert config["model"]["architecture"] == "unselected"

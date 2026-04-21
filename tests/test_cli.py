from shadowgen_training.cli import main


def test_validate_config_command_passes() -> None:
    assert main(["validate-config", "configs/project.yaml"]) == 0


def test_cli_rejects_missing_config() -> None:
    assert main(["validate-config", "configs/missing.yaml"]) == 1

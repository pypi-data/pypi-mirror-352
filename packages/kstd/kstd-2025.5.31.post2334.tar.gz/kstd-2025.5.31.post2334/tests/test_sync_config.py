from pathlib import Path
from tempfile import TemporaryDirectory
from typing import get_args

import pytest

import kstd
from kstd.sync_config import ConfigType, sync_config


@pytest.mark.parametrize("destination_file_existed", [True, False])
@pytest.mark.parametrize("config_type", get_args(ConfigType))
def test_copies_to_empty_destination(
    *,
    destination_file_existed: bool,
    config_type: ConfigType,
) -> None:
    with TemporaryDirectory() as temp_dir:
        destination_file_path = Path(temp_dir) / "destination.txt"

        if destination_file_existed:
            with destination_file_path.open("w") as destination_file:
                _ = destination_file.write("foo")
        else:
            assert not destination_file_path.exists()

        sync_config(config_type, destination_file_path)

        match config_type:
            case "pyright":
                config_file_path = Path(kstd.__file__).parent / "configs" / "pyrightconfig.json"
            case "ruff":
                config_file_path = Path(kstd.__file__).parent / "configs" / "ruff.toml"

        assert destination_file_path.exists(), "The destination file should have been created"

        with destination_file_path.open("r") as destination_file:
            with config_file_path.open("r") as config_file:
                assert destination_file.readlines() == config_file.readlines(), (
                    "The destination file should be identical to the source"
                )

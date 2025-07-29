"""Utility function to sync configs defined in kstd."""

import argparse
from pathlib import Path
from shutil import copyfileobj
from typing import Literal, get_args

_CONFIGS_DIR = Path(__file__).parent / "configs"

ConfigType = Literal["pyright", "ruff"]


def sync_config(
    config_type: ConfigType,
    destination_file_path: Path,
) -> None:
    """
    Sync base configuration file for a specified tool. This will overwrite the destination.

    Args:
        config_type: Type of configuration file to sync.
        destination_file_path: Destination path where the config file will be copied to.
    """
    match config_type:
        case "pyright":
            config_file = _CONFIGS_DIR / "pyrightconfig.json"
        case "ruff":
            config_file = _CONFIGS_DIR / "ruff.toml"

    with config_file.open("r") as config_file:
        with destination_file_path.open("w") as destination_file:
            copyfileobj(config_file, destination_file)


def cli() -> None:
    """Command line interface for syncing the configuration files."""
    parser = argparse.ArgumentParser(description="Sync configuration files")

    _ = parser.add_argument(
        "config_type",
        choices=get_args(ConfigType),
        help="Type of configuration to sync",
    )

    _ = parser.add_argument(
        "destination_file_path",
        type=Path,
        help="Destination path for the config file",
    )

    args = parser.parse_args()

    sync_config(args.config_type, Path(args.destination_file_path))


if __name__ == "__main__":
    cli()

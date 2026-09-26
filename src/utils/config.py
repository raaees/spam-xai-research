"""Load and validate configuration."""

from pathlib import Path
import yaml


def load_config(config_path: str = "configs/config.yaml") -> dict:
    """Load YAML configuration."""
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")

    with path.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle) or {}

    return config


def ensure_required_dirs(config: dict) -> None:
    """Create all required directories from config."""
    paths = [
        config.get("paths", {}).get("raw_dir"),
        config.get("paths", {}).get("interim_dir"),
        config.get("paths", {}).get("processed_dir"),
        config.get("paths", {}).get("outputs_dir"),
    ]

    for path_str in paths:
        if not path_str:
            continue
        Path(path_str).mkdir(parents=True, exist_ok=True)

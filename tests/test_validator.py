#!/usr/bin/env python3
"""Phase 1: validate the raw dataset structure and infer the schema."""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from data.validator import DatasetValidator
from utils.config import load_config, ensure_required_dirs
from utils.logging import setup_logging


def main() -> int:
    config = load_config(str(ROOT / "configs" / "config.yaml"))
    ensure_required_dirs(config)

    logger = setup_logging(
        log_file=str(ROOT / config["logging"]["output_file"]),
        level=config["logging"]["level"],
    )
    logger.info("Starting Phase 1: dataset validation")

    try:
        raw_dir = ROOT / config["paths"]["raw_dir"]
        validator = DatasetValidator(str(raw_dir))
        report = validator.validate()

        interim_dir = ROOT / config["paths"]["interim_dir"]
        interim_dir.mkdir(parents=True, exist_ok=True)

        output_path = interim_dir / "schema_report.json"
        with output_path.open("w", encoding="utf-8") as handle:
            json.dump(report, handle, indent=2, ensure_ascii=False)

        logger.info("Schema report saved to %s", output_path)
        logger.info("Phase 1 completed successfully.")
        return 0

    except Exception as exc:
        logging.getLogger("spam_xai").error("Phase 1 failed: %s", exc, exc_info=True)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

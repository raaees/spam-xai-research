"""Dataset validation and schema inference."""

from __future__ import annotations

import csv
import json
import logging
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

logger = logging.getLogger("spam_xai")


@dataclass
class DatasetSchema:
    """Detected schema summary for a dataset."""
    account_id_column: str | None = None
    tweet_id_column: str | None = None
    text_column: str | None = None
    timestamp_column: str | None = None
    label_column: str | None = None
    profile_columns: list[str] | None = None
    relation_columns: list[str] | None = None
    files_found: list[str] | None = None
    missing_values: dict[str, int] | None = None
    duplicate_account_ids: int = 0
    duplicate_tweet_ids: int = 0
    detected_categories: dict[str, int] | None = None


class DatasetValidator:
    """Discover files and infer the dataset schema."""

    def __init__(self, raw_dir: str):
        self.raw_dir = Path(raw_dir)
        if not self.raw_dir.exists():
            raise FileNotFoundError(f"Raw data directory not found: {self.raw_dir}")

        self.files = []
        self.schema = DatasetSchema()

    def discover_files(self) -> list[Path]:
        """Find CSV and JSON files in the raw directory tree."""
        files = sorted(self.raw_dir.rglob("*.csv")) + sorted(self.raw_dir.rglob("*.json"))
        self.files = sorted(set(files), key=lambda p: str(p))

        if not self.files:
            raise ValueError(f"No CSV or JSON files were found under {self.raw_dir}.")

        logger.info("Discovered files:")
        for path in self.files:
            logger.info("  - %s", path.relative_to(self.raw_dir))

        self.schema.files_found = [str(p.relative_to(self.raw_dir)) for p in self.files]
        return self.files

    def inspect_csv(self, path: Path) -> dict[str, Any]:
        """Read a CSV and summarize its shape and candidate columns."""
        with path.open("r", encoding="utf-8", errors="replace", newline="") as handle:
            reader = csv.DictReader(handle)
            rows = list(reader)

        if not rows:
            return {"columns": [], "row_count": 0}

        columns = list(rows[0].keys())
        sample_row = rows[0]

        logger.info("CSV file: %s", path.name)
        logger.info("  Columns: %s", columns)
        logger.info("  Rows: %s", len(rows))
        logger.info("  Sample row: %s", sample_row)

        return {"columns": columns, "row_count": len(rows), "sample_row": sample_row}

    def inspect_json(self, path: Path) -> dict[str, Any]:
        """Read a JSON file and infer its basic structure."""
        with path.open("r", encoding="utf-8", errors="replace") as handle:
            payload = json.load(handle)

        if isinstance(payload, list):
            if payload and isinstance(payload[0], dict):
                keys = list(payload[0].keys())
                logger.info("JSON file: %s", path.name)
                logger.info("  List length: %s", len(payload))
                logger.info("  Keys in first item: %s", keys)
                return {"type": "list", "keys": keys, "length": len(payload)}
            logger.info("JSON file: %s", path.name)
            logger.info("  List of non-object items; length=%s", len(payload))
            return {"type": "list", "length": len(payload)}

        if isinstance(payload, dict):
            keys = list(payload.keys())
            logger.info("JSON file: %s", path.name)
            logger.info("  Keys: %s", keys)
            return {"type": "dict", "keys": keys}

        logger.info("JSON file: %s", path.name)
        logger.info("  Scalar value: %s", type(payload).__name__)
        return {"type": type(payload).__name__}

    def _candidate_columns(self, file_infos: list[dict]) -> set[str]:
        columns = set()
        for info in file_infos:
            if isinstance(info.get("columns"), list):
                columns.update(info["columns"])
        return columns

    def detect_schema(self) -> DatasetSchema:
        """Infer likely account, tweet, text, timestamp, label, profile, and relation columns."""
        file_infos = []

        for path in self.files:
            if path.suffix.lower() == ".csv":
                file_infos.append(self.inspect_csv(path))
            elif path.suffix.lower() == ".json":
                file_infos.append(self.inspect_json(path))

        all_columns = self._candidate_columns(file_infos)

        def has_any(column_name: str, patterns: list[str]) -> bool:
            if column_name is None:
                return False
            lower = column_name.lower()
            return any(pattern in lower for pattern in patterns)

        account_candidates = sorted(
            [c for c in all_columns if has_any(c, ["user_id", "account_id", "userid", "screen_name", "username"])]
        )
        tweet_candidates = sorted(
            [c for c in all_columns if has_any(c, ["tweet_id", "status_id", "post_id", "tweetid"]) ]
        )
        text_candidates = sorted(
            [c for c in all_columns if has_any(c, ["text", "tweet", "content", "message", "status"]) ]
        )
        timestamp_candidates = sorted(
            [c for c in all_columns if has_any(c, ["created_at", "timestamp", "date", "time", "created"]) ]
        )
        label_candidates = sorted(
            [c for c in all_columns if has_any(c, ["label", "class", "category", "type", "bot"]) ]
        )

        profile_candidates = sorted(
            [c for c in all_columns if has_any(c, ["followers", "following", "friends", "statuses", "favorites", "verified", "description", "bio", "profile", "location"]) ]
        )
        relation_candidates = sorted(
            [c for c in all_columns if has_any(c, ["source", "target", "follower", "followee", "mentions", "retweet", "reply", "interaction", "edge"]) ]
        )

        logger.info("Detected candidate columns:")
        logger.info("  account_id candidates: %s", account_candidates)
        logger.info("  tweet_id candidates: %s", tweet_candidates)
        logger.info("  text candidates: %s", text_candidates)
        logger.info("  timestamp candidates: %s", timestamp_candidates)
        logger.info("  label candidates: %s", label_candidates)
        logger.info("  profile candidates: %s", profile_candidates)
        logger.info("  relation candidates: %s", relation_candidates)

        self.schema.account_id_column = account_candidates[0] if account_candidates else None
        self.schema.tweet_id_column = tweet_candidates[0] if tweet_candidates else None
        self.schema.text_column = text_candidates[0] if text_candidates else None
        self.schema.timestamp_column = timestamp_candidates[0] if timestamp_candidates else None
        self.schema.label_column = label_candidates[0] if label_candidates else None
        self.schema.profile_columns = profile_candidates
        self.schema.relation_columns = relation_candidates

        return self.schema

    def check_missing_values(self) -> dict[str, int]:
        """Compute missing-value counts for the currently inferred schema candidates."""
        missing = {}

        for path in self.files:
            if path.suffix.lower() != ".csv":
                continue

            with path.open("r", encoding="utf-8", errors="replace", newline="") as handle:
                reader = csv.DictReader(handle)
                rows = list(reader)

            if not rows:
                continue

            for name in rows[0].keys():
                count = 0
                for row in rows:
                    if row.get(name) is None or str(row.get(name)).strip() == "":
                        count += 1
                if count > 0:
                    missing[f"{path.name}:{name}"] = count

        self.schema.missing_values = missing
        return missing

    def check_duplicates(self) -> tuple[int, int]:
        """Check duplicate account IDs and tweet IDs across CSV files when possible."""
        account_counter: Counter[str] = Counter()
        tweet_counter: Counter[str] = Counter()

        for path in self.files:
            if path.suffix.lower() != ".csv":
                continue

            with path.open("r", encoding="utf-8", errors="replace", newline="") as handle:
                reader = csv.DictReader(handle)
                for row in reader:
                    if self.schema.account_id_column and self.schema.account_id_column in row:
                        value = row.get(self.schema.account_id_column)
                        if value is not None and str(value).strip() != "":
                            account_counter[str(value)] += 1

                    if self.schema.tweet_id_column and self.schema.tweet_id_column in row:
                        value = row.get(self.schema.tweet_id_column)
                        if value is not None and str(value).strip() != "":
                            tweet_counter[str(value)] += 1

        duplicate_account_ids = sum(1 for count in account_counter.values() if count > 1)
        duplicate_tweet_ids = sum(1 for count in tweet_counter.values() if count > 1)

        self.schema.duplicate_account_ids = duplicate_account_ids
        self.schema.duplicate_tweet_ids = duplicate_tweet_ids
        return duplicate_account_ids, duplicate_tweet_ids

    def detect_category_distribution(self) -> dict[str, int]:
        """Get approximate label/category distribution when a label column exists."""
        if self.schema.label_column is None:
            return {}

        counter: Counter[str] = Counter()

        for path in self.files:
            if path.suffix.lower() != ".csv":
                continue

            with path.open("r", encoding="utf-8", errors="replace", newline="") as handle:
                reader = csv.DictReader(handle)
                for row in reader:
                    value = row.get(self.schema.label_column)
                    if value is not None and str(value).strip() != "":
                        counter[str(value)] += 1

        self.schema.detected_categories = dict(counter)
        return dict(counter)

    def validate(self) -> dict[str, Any]:
        """Run validation and fail with clear errors if required fields are missing."""
        self.discover_files()
        self.detect_schema()
        missing_values = self.check_missing_values()
        duplicates = self.check_duplicates()
        category_distribution = self.detect_category_distribution()

        # Required minimum checks
        if self.schema.account_id_column is None:
            raise ValueError(
                "Account ID column not found. The dataset must contain a user/account identifier. "
                "Check the raw CSV/JSON files and inspect the schema carefully."
            )

        if self.schema.label_column is None:
            raise ValueError(
                "Label or category column not found. The dataset must contain a class/category field. "
                "If labels are encoded by folder names instead of a column, provide a mapping layer."
            )

        logger.info("Validation complete.")
        logger.info("Detected schema: %s", asdict(self.schema))
        logger.info("Missing values summary: %s", missing_values)
        logger.info("Duplicate account IDs: %s", duplicates[0])
        logger.info("Duplicate tweet IDs: %s", duplicates[1])
        logger.info("Detected category distribution: %s", category_distribution)

        report = {
            "status": "success",
            "schema": asdict(self.schema),
            "missing_values": missing_values,
            "duplicate_account_ids": duplicates[0],
            "duplicate_tweet_ids": duplicates[1],
            "category_distribution": category_distribution,
        }

        return report

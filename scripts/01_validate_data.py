"""Map label categories into the binary spam/no-spam scheme."""

import logging
from collections import Counter

logger = logging.getLogger("spam_xai")


class LabelMapper:
    """Map dataset categories to binary labels using known Cresci categories."""

    def __init__(self, mapping: dict | None = None):
        default_mapping = {
            "genuine": 0,
            "genuine_accounts": 0,
            "human": 0,
            "traditional_spambots": 1,
            "traditional_spambots_1": 1,
            "traditional_spambots_2": 1,
            "traditional_spambots_3": 1,
            "traditional_spambots_4": 1,
            "social_spambots": 1,
            "social_spambots_1": 1,
            "social_spambots_2": 1,
            "social_spambots_3": 1,
            "fake_followers": "exclude",
            "fake_followers_accounts": "exclude",
        }
        self.mapping = {**default_mapping, **(mapping or {})}

    def map_value(self, raw_value: str | int | float | None) -> int | None:
        """Convert a category value to a binary label, excluding fake followers."""
        if raw_value is None:
            return None

        normalized = str(raw_value).strip().lower().replace(" ", "_")
        match = self.mapping.get(normalized)

        if match == "exclude":
            return None

        if match is None:
            # fallback for common labels
            if "genuine" in normalized or "human" in normalized:
                return 0
            if "spam" in normalized or "bot" in normalized:
                return 1
            raise ValueError(f"Unsupported label value: {raw_value!r}")

        return int(match)

    def summarize(self, values: list[str | int | float | None]) -> dict:
        """Summarize counts and class ratio for the loaded labels."""
        counts = Counter()
        genuine = 0
        spam = 0
        excluded = 0

        for value in values:
            mapped = self.map_value(value)
            if mapped is None:
                excluded += 1
                continue
            if mapped == 0:
                genuine += 1
            elif mapped == 1:
                spam += 1
            counts[str(value)] += 1

        total = genuine + spam + excluded
        class_ratio = (spam / (genuine + spam)) if (genuine + spam) > 0 else 0.0

        logger.info("Label summary:")
        logger.info("  genuine accounts: %s", genuine)
        logger.info("  spam accounts: %s", spam)
        logger.info("  excluded accounts: %s", excluded)
        logger.info("  class ratio (spam / total non-excluded): %.4f", class_ratio)

        return {
            "genuine": genuine,
            "spam": spam,
            "excluded": excluded,
            "class_ratio": class_ratio,
            "total": total,
        }

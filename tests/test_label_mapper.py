"""Tests for label mapping."""

from label_mapper import LabelMapper


def test_label_mapper_genuine_and_spam() -> None:
    mapper = LabelMapper()
    assert mapper.map_value("genuine") == 0
    assert mapper.map_value("genuine_accounts") == 0
    assert mapper.map_value("social_spambots_1") == 1
    assert mapper.map_value("traditional_spambots_2") == 1
    assert mapper.map_value("fake_followers") is None


def test_label_mapper_summary() -> None:
    mapper = LabelMapper()
    summary = mapper.summarize(["genuine", "social_spambots_1", "fake_followers", "genuine"])
    assert summary["genuine"] == 2
    assert summary["spam"] == 1
    assert summary["excluded"] == 1
    assert summary["class_ratio"] == 1.0 / 3.0

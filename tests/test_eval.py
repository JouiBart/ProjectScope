from pathlib import Path

from projectscope.eval import load_golden_set


def test_load_golden_set() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    golden = load_golden_set(repo_root / "data/golden_set.yaml")

    assert len(golden.incidents) == 5
    assert golden.incidents[0].incident_id == "GOLD-001"
    assert golden.incidents[0].expected_citations

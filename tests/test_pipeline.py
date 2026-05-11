from pathlib import Path

from projectscope.pipeline import run_placeholder_pipeline
from projectscope.schemas import IncidentInput


def test_run_placeholder_pipeline_returns_expected_shape() -> None:
    incident = IncidentInput(
        incident_id="INC-TEST-1",
        project="ProjectScope",
        repository="JouiBart/ProjectScope",
        customer="Test Customer",
        version="0.1.0",
        affected_systems=["order-gateway"],
        error_codes=["HTTP_503"],
        severity="high",
        time_window_start="2026-05-08T10:00:00Z",
        time_window_end="2026-05-08T10:30:00Z",
        observed_symptoms=["spike"],
        recent_changes=["deploy"],
        raw_logs=["line"],
    )

    repo_root = Path(__file__).resolve().parents[1]
    output = run_placeholder_pipeline(incident, repo_root / "architecture.yaml")

    assert output["incident_id"] == "INC-TEST-1"
    assert output["project"] == "ProjectScope"
    assert output["repository"] == "JouiBart/ProjectScope"
    assert output["customer"] == "Test Customer"
    assert output["version"] == "0.1.0"
    assert output["status"] == "needs_review"
    assert output["hypotheses"]
    assert output["hypotheses"][0]["citations"][0]["source_id"] == "architecture.yaml"

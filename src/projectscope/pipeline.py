from __future__ import annotations

from pathlib import Path

import yaml

from projectscope.schemas import Citation, Hypothesis, IncidentInput, LocalTriageOutput


def load_architecture(path: str | Path) -> dict:
    with Path(path).open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def run_placeholder_pipeline(incident: IncidentInput, architecture_path: str | Path) -> dict:
    architecture = load_architecture(architecture_path)
    triage = LocalTriageOutput(
        severity=incident.severity,
        suspected_components=incident.affected_systems,
        error_signatures=incident.error_codes,
        redacted_summary="Placeholder local triage output",
    )
    hypothesis = Hypothesis(
        diagnosis="Placeholder diagnosis — investigate affected dependencies",
        confidence=0.5,
        citations=[
            Citation(
                source_id="architecture.yaml",
                quote=f"systems={len(architecture.get('systems', []))}",
            )
        ],
    )
    return {
        "incident_id": incident.incident_id,
        "triage": triage.model_dump(),
        "hypotheses": [hypothesis.model_dump()],
        "status": "needs_review",
    }

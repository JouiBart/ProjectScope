from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import BaseModel, Field

from projectscope.schemas import Citation


class GoldenIncident(BaseModel):
    incident_id: str
    summary: str
    expected_diagnosis: str
    expected_citations: list[Citation] = Field(default_factory=list)


class GoldenSet(BaseModel):
    incidents: list[GoldenIncident] = Field(default_factory=list)


def load_golden_set(path: str | Path) -> GoldenSet:
    with Path(path).open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    return GoldenSet.model_validate(data)

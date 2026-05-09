from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class Citation(BaseModel):
    source_id: str = Field(..., min_length=1)
    quote: str = Field(..., min_length=1)


class Hypothesis(BaseModel):
    diagnosis: str = Field(..., min_length=1)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    citations: list[Citation] = Field(default_factory=list)


class IncidentInput(BaseModel):
    incident_id: str
    affected_systems: list[str] = Field(default_factory=list)
    error_codes: list[str] = Field(default_factory=list)
    severity: str
    time_window_start: datetime
    time_window_end: datetime
    observed_symptoms: list[str] = Field(default_factory=list)
    recent_changes: list[str] = Field(default_factory=list)
    raw_logs: list[str] = Field(default_factory=list)


class LogChunk(BaseModel):
    chunk_id: str
    incident_id: str
    start: datetime
    end: datetime
    lines: list[str] = Field(default_factory=list)


class LocalTriageOutput(BaseModel):
    severity: str
    suspected_components: list[str] = Field(default_factory=list)
    error_signatures: list[str] = Field(default_factory=list)
    redacted_summary: str

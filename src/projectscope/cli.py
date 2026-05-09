from __future__ import annotations

import argparse
import json
from pathlib import Path

from projectscope.eval import load_golden_set
from projectscope.pipeline import run_placeholder_pipeline
from projectscope.schemas import IncidentInput, LogChunk


def ingest_command(incident_path: str) -> None:
    with Path(incident_path).open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    incident = IncidentInput.model_validate(payload)
    chunk = LogChunk(
        chunk_id=f"{incident.incident_id}-chunk-1",
        incident_id=incident.incident_id,
        start=incident.time_window_start,
        end=incident.time_window_end,
        lines=incident.raw_logs,
    )
    print(json.dumps(chunk.model_dump(mode="json"), indent=2))


def run_command(incident_path: str, architecture_path: str) -> None:
    with Path(incident_path).open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    incident = IncidentInput.model_validate(payload)
    output = run_placeholder_pipeline(incident, architecture_path)
    print(json.dumps(output, indent=2))


def eval_command(golden_set_path: str) -> None:
    golden = load_golden_set(golden_set_path)
    print(
        json.dumps(
            {
                "golden_incidents_loaded": len(golden.incidents),
                "status": "ok",
            },
            indent=2,
        )
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="ProjectScope Phase 0 CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    ingest = sub.add_parser("ingest")
    ingest.add_argument("--incident", required=True)

    run = sub.add_parser("run")
    run.add_argument("--incident", required=True)
    run.add_argument("--architecture", required=True)

    ev = sub.add_parser("eval")
    ev.add_argument("--golden-set", required=True)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "ingest":
        ingest_command(args.incident)
    elif args.command == "run":
        run_command(args.incident, args.architecture)
    elif args.command == "eval":
        eval_command(args.golden_set)


if __name__ == "__main__":
    main()

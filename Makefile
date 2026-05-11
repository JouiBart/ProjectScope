.PHONY: ingest eval run

ingest:
	python -m projectscope.cli ingest --incident data/sample_incident.json

eval:
	python -m projectscope.cli eval --golden-set data/golden_set.yaml

run:
	python -m projectscope.cli run --incident data/sample_incident.json --architecture architecture.yaml

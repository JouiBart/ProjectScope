# ProjectScope

**An AI-powered diagnostic and analysis assistant for logistics integration systems — a learning project for production-grade AI engineering.**

The first milestone is incident diagnostics (described in detail below). Later milestones extend the same multi-tier pipeline to broader analysis use cases — see *Future direction* at the end.

> ⚠️ **Status:** Learning project, work in progress. Not production-ready. The goal is to deeply understand how each layer of a real AI system works — local model serving, multi-tier model routing, metadata-aware RAG, eval-driven iteration — by building it end-to-end with measurable progress between phases.

## Phase 0 quick start

```bash
uv sync
cp .env.example .env
make ingest
make eval
make run
```

For local model setup (Ollama):

```bash
ollama pull qwen2.5:7b
# or
ollama pull llama3.1:8b
```

For cloud setup, populate Azure OpenAI values in `.env` and keep secrets out of source control.

-----

## Why this project exists

Most “AI assistant” tutorials stop at *single-shot RAG over a few PDFs*. Real production systems look different: they combine local models for cheap preprocessing, cloud models for heavy reasoning, structured retrieval with metadata, deterministic decision logic, and per-layer evaluation. This project is built to **learn each of those components hands-on**, not to ship a polished product.

Domain anchor: incident response in **logistics integration systems**, where engineers face problems spanning multiple interconnected services. When an incident occurs, the system should ingest logs and an incident description, retrieve relevant past incidents and runbooks, and produce a ranked diagnosis with cited sources — while routing work intelligently between a local model (for triage, redaction, summarization) and a cloud model (for final reasoning).

## What this project teaches (mapped to phases)

|Skill                                                          |Where it’s learned|
|---------------------------------------------------------------|------------------|
|Local model serving (Ollama, quantization, GGUF)               |Phase 0, 2        |
|Forcing structured output from small models                    |Phase 2           |
|Map-reduce summarization over large inputs                     |Phase 2           |
|Multi-tier model routing (local vs cloud)                      |Phase 2, 5        |
|Metadata-aware RAG with hybrid retrieval                       |Phase 3           |
|Multi-provider authentication (Ollama + Azure OpenAI)          |Phase 0, 2, 3     |
|Per-layer evaluation harness                                   |Phase 1–6         |
|Three-signal decision layer (anti-pattern: LLM self-confidence)|Phase 4           |
|Cost & latency observability                                   |Phase 5           |
|Code-aware embeddings & AST-based chunking                     |Phase 6           |
|Git history as a causal signal                                 |Phase 6           |

## Architecture (target)

```
┌─────────────────────────────────────────────────────────────────┐
│  Incident input (Pydantic schema): project, repository, customer, │
│  version, affected systems, error_codes, severity, time window     │
└────────────────────────┬────────────────────────────────────────┘
                         │
            ┌────────────▼────────────┐
            │  Layer 1: Log ingestion │  normalize, parse timestamps
            │  (deterministic)        │  extract structured fields
            └────────────┬────────────┘
                         │
            ┌────────────▼────────────┐
            │  Layer 2: Local triage  │  Ollama (Qwen 2.5 7B / Llama 3.1 8B)
            │  Structured JSON output │  per-window severity, signatures,
            │  PII redaction          │  redacted summary
            └────────────┬────────────┘
                         │
            ┌────────────▼────────────┐
            │  Layer 3: Aggregator    │  pure Python — no LLM
            │  (deterministic)        │  merge, dedupe, rank
            └────────────┬────────────┘
                         │
            ┌────────────▼────────────┐
            │  Layer 4: RAG retrieval │  ChromaDB + BM25 hybrid
            │  Metadata filters       │  filter by system, type, time
            └────────────┬────────────┘
                         │
            ┌────────────▼────────────┐
            │  Layer 5: Cloud reason  │  Azure OpenAI (or Anthropic)
            │  Diagnosis + actions    │  cited hypotheses
            └────────────┬────────────┘
                         │
            ┌────────────▼────────────┐
            │  Layer 6: Decision gate │  three-signal scoring:
            │  (deterministic)        │  retrieval + groundedness + citations
            └────────────┬────────────┘
                         │
                  ┌──────▼──────┐
                  │  Output:    │  high_confidence │ needs_review │ escalate
                  │  diagnosis  │  with cited sources
                  │  + actions  │
                  └─────────────┘
```

Architecture metadata (which systems exist, how they depend on each other) lives in `architecture.yaml`, injected as context into prompts and used for metadata validation at ingest.

-----

## Phases

Each phase produces a **measurable improvement over the previous baseline**. Eval-first means metrics drive the iteration, not vibes.

### Phase 0 — Foundations *(~1 week)*

- Repo skeleton, Python env (`uv`), Makefile (`make ingest`, `make eval`, `make run`)
- Pydantic schemas: `IncidentInput`, `LogChunk`, `LocalTriageOutput`, `Hypothesis`, `Citation`
- `architecture.yaml` with 5–6 systems and their dependencies
- Mini golden set: 5–10 anonymized incidents with annotated expected diagnoses and source citations
- Ollama installed; local model pulled (Qwen 2.5 7B or Llama 3.1 8B)
- Azure OpenAI access configured; `.env` and secrets management
- **Deliverable:** end-to-end pipeline runs (returns placeholder), eval harness loads golden set

### Phase 1 — Naive baseline *(~3–5 days)*

- Single-shot: raw logs + incident description → entire context to Azure → diagnosis
- No chunking, no local model, no RAG
- Run on golden set; measure accuracy, latency, cost per incident
- **Purpose:** reference point. Every later phase must beat this on at least one metric.

### Phase 2 — Local triage + aggregator *(~1.5 weeks — the densest learning phase)*

- Ollama wrapper with enforced structured output (`instructor` or `outlines`)
- Log chunking by time window or trace ID
- Local model returns JSON: `severity`, `suspected_components`, `error_signatures`, `redacted_summary` (PII removed at this stage)
- Validation + retry loop + fallback to `"uncertain"` when retries exhausted
- Aggregator (pure Python, no LLM): merge windows, deduplicate signatures, sort by severity
- Structured summary sent to Azure → diagnosis
- **Per-layer metrics:** JSON validity rate, severity agreement with humans, cost reduction vs Phase 1, latency p50/p95

### Phase 3 — RAG with rich metadata *(~1 week)*

- ChromaDB ingest of past incidents, runbooks, manuals — with metadata: `system`, `type`, `timestamp`, `severity`, `component`
- Hybrid retrieval: BM25 + dense embeddings (`sentence-transformers`) with weighted fusion
- **Metadata filtering before retrieval**: limit search to relevant system, recent time window
- Inject retrieved context into cloud prompt with **mandatory citations** in output
- Architecture YAML injected as additional structured context
- **Metrics:** citation coverage, hypothesis accuracy vs Phase 2, retrieval precision/recall on golden set

### Phase 4 — Three-signal decision layer *(~3–5 days)*

- Deterministic gate scoring three signals:
  - **Retrieval score** (how strong was the match?)
  - **Groundedness check** (is every claim supported by retrieved context?)
  - **Citation coverage** (do hypotheses cite specific sources?)
- Output gate: `high_confidence` / `needs_review` / `escalate_to_human`
- **Explicitly not** using LLM self-reported confidence — this is a deliberate architectural choice and a key learning outcome
- **Deliverable:** documented analysis of *why* LLM self-confidence is unreliable, with measurements from this project’s golden set

### Phase 5 — Observability & disciplined iteration *(ongoing, finalized in last week)*

- Structured per-request logging: trace ID, per-layer latency, token counts (local vs cloud), cost estimate
- `make eval` produces a markdown report: metrics table comparing all phases
- **Iteration discipline:** take the 3 worst cases from the golden set, identify which layer failed, fix, re-measure. Document each cycle.

### Phase 6 — Source code & Git integration *(~1.5–2 weeks)*

The most ambitious phase. Instead of just searching docs and past incidents, ProjectScope can reason over the actual codebase of affected systems.

**Why it’s a separate phase, not in MVP:** code is a fundamentally different retrieval target than prose. Doing it naively (running natural-language embeddings over text-chunked source files) produces poor results. This phase exists to *learn that lesson hands-on* and implement it correctly.

- **Code-aware embeddings**: replace `sentence-transformers` with a code-trained model (`jinaai/jina-embeddings-v2-base-code`, `microsoft/codebert-base`, or Voyage AI `voyage-code-3`)
- **AST-based chunking**: chunk by function/class/method using `tree-sitter` or Python’s `ast`. Each chunk gets metadata: `file_path`, `symbol_name`, `language`, `imports`, `last_modified`, `last_author`
- **Symbol index alongside vector store**: deterministic lookup map for `class → file → line` and `function → callers/callees`. When stack traces arrive, *don’t use embeddings* — use the index. (Lesson: don’t reach for AI when a dictionary suffices.)
- **Git as a first-class diagnostic signal**: query “what changed in the last 24h touching components X, Y” using `pygit2` or `gitpython`. Recent deploys correlated with incident timing answer many cases without any LLM call.
- **Security filter before cloud calls**: allow/deny patterns for what code can leave the local environment (no hardcoded credentials, internal hostnames, secrets). Same discipline as PII redaction in Phase 2, different rules.
- **Separate eval set for code-based diagnoses**: distinct metrics from doc-based RAG, because the failure modes are different.

**Lighter intermediate option (already in MVP via `architecture.yaml`):** each system entry includes `repo_url`, `key_files`, `recent_deploys` as plain metadata. Cloud model can reference them in output (“see `awbline/manifest_processor.py`”) without ingesting code. ~80% of practical value at ~5% of the engineering cost. Phase 6 is the upgrade from “reference” to “reason over.”

-----

## Optional later experiments

Once the core (Phases 0–6) is stable and measured, candidate next iterations:

- NetworkX graph over `architecture.yaml` for upstream/downstream blast-radius reasoning
- Agentic loop with hypothesis generation + evidence collection
- Streaming responses to the engineer
- Function calling for read-only diagnostic actions (and a safety classifier for any mutating actions)
- Fine-tuning the local model on domain-specific log signatures

These are explicitly **not part of the learning roadmap** and would be added only with a clear motivation from observed failures in the eval set.

-----

## Tech stack

|Layer                        |Tool                                               |
|-----------------------------|---------------------------------------------------|
|Language                     |Python 3.11+                                       |
|Env / packaging              |`uv`                                               |
|Schemas                      |Pydantic v2                                        |
|Local model serving          |Ollama (Qwen 2.5 7B / Llama 3.1 8B)                |
|Structured output enforcement|`instructor` or `outlines`                         |
|Cloud model                  |Azure OpenAI (primary), Anthropic API (alternative)|
|Vector store                 |ChromaDB                                           |
|Sparse retrieval             |`rank_bm25`                                        |
|Doc embeddings               |`sentence-transformers`                            |
|Code embeddings (Phase 6)    |`jina-embeddings-v2-base-code` or Voyage AI        |
|Code parsing (Phase 6)       |`tree-sitter`                                      |
|Git integration (Phase 6)    |`pygit2`                                           |
|Eval                         |Custom harness, markdown reports                   |
|CI                           |GitHub Actions (lint, type-check, eval-on-PR)      |

## Evaluation philosophy

- **Eval-first**: golden set built before optimizing retrieval or generation
- **Per-layer metrics**: when output is wrong, know which layer caused it
- **Honest baselines**: every phase is measured against the previous one, not against an ideal
- **Anti-pattern documentation**: explicitly demonstrate why LLM self-confidence is unreliable (Phase 4) — failure modes are part of the portfolio, not hidden

## Time estimate

Roughly **5–6 weeks for Phases 0–5** of disciplined evening work, plus **~2 weeks for Phase 6**. Faster if full-time. Slower with realistic friction (Azure auth, Ollama performance tuning, structured-output debugging on small models — all of which are part of the lesson).

## Future direction

Once the incident-diagnostic core (Phases 0–6) is stable, the same multi-tier pipeline (local triage → aggregator → metadata-aware RAG → cloud reasoning → decision gate) is intended to extend to broader analysis use cases beyond reactive incident response.

*This section will be expanded with a concrete second milestone once Phase 3 is reached and real failure modes from the eval set inform what kind of analysis adds the most engineering value.*

## License

MIT 

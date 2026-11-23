# VYRO Script Intake

**Repository:** `vyro-script-intake`  
**Purpose:** the single source of truth for entering and validating content briefs before they reach the AI, render, scheduler, or publisher components.

## Responsibility

This repository owns the incoming brief contract, validation rules, normalization, schema export, and command-line intake workflow. It does **not** generate scripts, render video, schedule posts, or publish to Instagram.

## Contract highlights

- Stable `content_id` for traceability and idempotency.
- Content pillar, intended audience, objective, language, duration, hook, narration, CTA, caption, and hashtags.
- Source URLs and claims that require verification.
- Asset references with media type, attribution, and rights confirmation.
- Explicit human-review requirement; approval is not silently inferred.
- Schema version for safe future migrations.

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
```

## CLI

```bash
vyro-intake validate examples/brief_umkm.json
vyro-intake normalize examples/brief_umkm.json --output output/brief.normalized.json
vyro-intake export-schema --output schemas/script-brief.schema.json
```

## Contract hand-off

The normalized JSON document is the hand-off artifact for `vyro-ai-content-engine`. Downstream repositories should treat `content_id` as immutable and preserve it in every generated artifact and log record.

## Quality checks

```bash
ruff check .
ruff format --check .
pytest
```

## Security and ownership

Do not put passwords, API keys, private customer details, or unreleased campaign information into public examples. This repository is proprietary; see `LICENSE`.

## 1.1.0 — Prime API
Optional FastAPI service for website intake: `POST /v1/briefs/validate` and `POST /v1/briefs/normalize`. Install `pip install -e '.[api]'`, set `VYRO_SERVICE_API_KEY`, then run `uvicorn vyro_script_intake.api:app --host 0.0.0.0 --port 8000`. Requests require `Authorization: Bearer <service-key>`. This service validates and normalizes only; it does not generate scripts or publish.

# VYRO Script Intake

Validated, versioned brief intake for VYRO MEDIA's content production pipeline.

## Responsibilities
- Validate a content brief and normalize it to a stable JSON contract.
- Validate content identity, content pillar, audience, duration, hook, narration, CTA, source URLs, claims to verify, template selection, and asset references.
- Record asset usage rights and attribution explicitly; no rights are inferred.
- Keep `human_review_required=true`; the intake service does not approve publication.

## API
Install API extras and run:

```bash
pip install -e '.[api,dev]'
uvicorn vyro_script_intake.api:app --host 0.0.0.0 --port 8101
```

Authenticated endpoints:
- `POST /v1/briefs/validate`
- `POST /v1/briefs/normalize`
- `GET /health`

Every API request requires `Authorization: Bearer $VYRO_SERVICE_API_KEY`.

## Local use

```bash
pip install -e '.[dev]'
vyro-intake validate examples/brief_umkm.json
pytest
```

## Security and data boundary
This component validates brief data only. It does not store uploads, generate media, publish to Instagram, or schedule posts. Do not include API keys or private customer data in example files or Git history.

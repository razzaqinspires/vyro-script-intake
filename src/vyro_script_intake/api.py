from __future__ import annotations

import hmac
import os
from typing import Any

from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import ValidationError

from .models import ScriptBrief

APP_VERSION = "1.2.0"
app = FastAPI(
    title="VYRO Script Intake API",
    version=APP_VERSION,
    description="Strict, versioned intake contract for VYRO MEDIA creative projects.",
)


def require_service_key(authorization: str | None = Header(default=None)) -> None:
    expected = os.getenv("VYRO_SERVICE_API_KEY", "")
    if not expected:
        raise HTTPException(status_code=503, detail="Service API key belum dikonfigurasi")
    supplied = authorization.removeprefix("Bearer ") if authorization else ""
    if not hmac.compare_digest(supplied, expected):
        raise HTTPException(status_code=401, detail="Unauthorized")


@app.get("/health")
def health() -> dict[str, str]:
    return {"service": "vyro-script-intake", "status": "ok", "version": APP_VERSION}


@app.get("/v1/schema")
def schema() -> dict[str, Any]:
    return {"service": "vyro-script-intake", "schema_version": "1.2", "schema": ScriptBrief.model_json_schema()}


@app.post("/v1/briefs/validate", dependencies=[Depends(require_service_key)])
def validate_brief(payload: dict[str, Any]) -> dict[str, Any]:
    try:
        brief = ScriptBrief.model_validate(payload)
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail=exc.errors(include_url=False)) from exc
    return {
        "valid": True,
        "schema_version": brief.schema_version,
        "brief": brief.model_dump(mode="json"),
        "content_id": brief.content_id,
        "human_review_required": True,
    }


@app.post("/v1/briefs/normalize", dependencies=[Depends(require_service_key)])
def normalize_brief(payload: dict[str, Any]) -> dict[str, Any]:
    try:
        brief = ScriptBrief.model_validate(payload)
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail=exc.errors(include_url=False)) from exc
    normalized = brief.model_dump(mode="json")
    return {
        "schema_version": brief.schema_version,
        "content_id": brief.content_id,
        "brief": normalized,
        "review": {
            "human_review_required": True,
            "rights_confirmed_assets": sum(1 for asset in brief.assets if asset.rights_confirmed),
            "unconfirmed_assets": sum(1 for asset in brief.assets if not asset.rights_confirmed),
            "claims_to_verify": len(brief.claims_to_verify),
            "paid_disclosure_required": brief.paid_partnership,
            "ai_media_disclosure_check": brief.ai_generated_media,
        },
    }

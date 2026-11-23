from __future__ import annotations

import hmac
import os
from typing import Any

from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import ValidationError

from .models import ScriptBrief

app = FastAPI(title="VYRO Script Intake API", version="1.1.0")

def require_service_key(authorization: str | None = Header(default=None)) -> None:
    expected = os.getenv("VYRO_SERVICE_API_KEY", "")
    if not expected:
        raise HTTPException(status_code=503, detail="Service API key belum dikonfigurasi")
    supplied = authorization.removeprefix("Bearer ") if authorization else ""
    if not hmac.compare_digest(supplied, expected):
        raise HTTPException(status_code=401, detail="Unauthorized")

@app.get("/health")
def health() -> dict[str, str]:
    return {"service": "vyro-script-intake", "status": "ok", "version": "1.1.0"}

@app.post("/v1/briefs/validate", dependencies=[Depends(require_service_key)])
def validate_brief(payload: dict[str, Any]) -> dict[str, Any]:
    try:
        brief = ScriptBrief.model_validate(payload)
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail=exc.errors(include_url=False)) from exc
    return {"valid": True, "brief": brief.model_dump(mode="json"), "content_id": brief.content_id}

@app.post("/v1/briefs/normalize", dependencies=[Depends(require_service_key)])
def normalize_brief(payload: dict[str, Any]) -> dict[str, Any]:
    try:
        brief = ScriptBrief.model_validate(payload)
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail=exc.errors(include_url=False)) from exc
    return {"schema_version": brief.schema_version, "content_id": brief.content_id, "brief": brief.model_dump(mode="json")}

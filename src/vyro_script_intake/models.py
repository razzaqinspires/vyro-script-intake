from __future__ import annotations
from enum import StrEnum
from typing import Annotated
from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator
import re

class Pillar(StrEnum):
    VIRAL_TREND = "viral_trend"
    ENTERTAINMENT = "entertainment_challenge"
    EDUCATION = "creator_education"
    BEHIND_SCENES = "behind_the_scenes"
    BRAND_PROMOTION = "brand_promotion"
    TALENT = "talent_creator"

class AssetReference(BaseModel):
    model_config = ConfigDict(extra="forbid")
    path_or_url: str = Field(min_length=1, max_length=2048)
    media_type: str = Field(pattern=r"^(image|video|audio)$")
    rights_confirmed: bool = False
    attribution: str | None = Field(default=None, max_length=500)

class ScriptBrief(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    schema_version: str = "1.0"
    content_id: str = Field(min_length=4, max_length=80, pattern=r"^[a-zA-Z0-9][a-zA-Z0-9._-]+$")
    title: str = Field(min_length=5, max_length=140)
    pillar: Pillar
    objective: str = Field(min_length=10, max_length=500)
    audience: str = Field(min_length=5, max_length=300)
    language: str = "id-ID"
    duration_seconds: Annotated[int, Field(ge=8, le=90)] = 30
    hook: str = Field(min_length=8, max_length=240)
    narration: str = Field(min_length=20, max_length=5000)
    call_to_action: str = Field(min_length=3, max_length=300)
    caption: str | None = Field(default=None, max_length=2200)
    hashtags: list[str] = Field(default_factory=list, max_length=8)
    source_urls: list[HttpUrl] = Field(default_factory=list, max_length=20)
    claims_to_verify: list[str] = Field(default_factory=list, max_length=20)
    assets: list[AssetReference] = Field(default_factory=list, max_length=30)
    paid_partnership: bool = False
    ai_generated_media: bool = False
    human_review_required: bool = True

    @field_validator("content_id")
    @classmethod
    def normalize_id(cls, value: str) -> str:
        if ".." in value or value.startswith("."):
            raise ValueError("content_id tidak boleh berupa path traversal")
        return value

    @field_validator("hashtags")
    @classmethod
    def clean_hashtags(cls, values: list[str]) -> list[str]:
        cleaned = []
        for item in values:
            tag = item.strip().lstrip("#")
            if tag and re.fullmatch(r"[A-Za-z0-9_]{1,50}", tag):
                cleaned.append(tag)
        return list(dict.fromkeys(cleaned))

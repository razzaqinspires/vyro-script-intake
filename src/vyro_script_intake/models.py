from __future__ import annotations

import re
from enum import StrEnum
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator, model_validator


class Pillar(StrEnum):
    VIRAL_TREND = "viral_trend"
    ENTERTAINMENT = "entertainment_challenge"
    EDUCATION = "creator_education"
    BEHIND_SCENES = "behind_the_scenes"
    BRAND_PROMOTION = "brand_promotion"
    TALENT = "talent_creator"


class AssetReference(BaseModel):
    """A project asset reference; rights are explicit and never inferred."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    asset_id: str | None = Field(default=None, min_length=3, max_length=120)
    path_or_url: str = Field(min_length=1, max_length=2048)
    media_type: Literal["image", "video", "audio"]
    rights_confirmed: bool = False
    attribution: str | None = Field(default=None, max_length=500)
    source: Literal["library", "user_upload", "licensed_stock", "generated"] = "user_upload"

    @field_validator("path_or_url")
    @classmethod
    def reject_javascript_urls(cls, value: str) -> str:
        lowered = value.lower().strip()
        if lowered.startswith(("javascript:", "data:text/html", "file://")):
            raise ValueError("Referensi aset menggunakan skema yang tidak diizinkan")
        return value


class ScriptBrief(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    schema_version: str = "1.2"
    content_id: str = Field(min_length=4, max_length=80, pattern=r"^[a-zA-Z0-9][a-zA-Z0-9._-]+$")
    title: str = Field(min_length=5, max_length=140)
    pillar: Pillar
    objective: str = Field(min_length=10, max_length=500)
    audience: str = Field(min_length=5, max_length=300)
    language: str = Field(default="id-ID", max_length=20)
    platform: str = Field(default="instagram_reels", max_length=50)
    duration_seconds: Annotated[int, Field(ge=8, le=90)] = 30
    hook: str = Field(min_length=8, max_length=240)
    narration: str = Field(min_length=20, max_length=5000)
    call_to_action: str = Field(min_length=3, max_length=300)
    caption: str | None = Field(default=None, max_length=2200)
    hashtags: list[str] = Field(default_factory=list, max_length=8)
    source_urls: list[HttpUrl] = Field(default_factory=list, max_length=20)
    claims_to_verify: list[str] = Field(default_factory=list, max_length=20)
    assets: list[AssetReference] = Field(default_factory=list, max_length=30)
    reference_asset_ids: list[str] = Field(default_factory=list, max_length=30)
    brand_voice: str = Field(default="jelas, natural, profesional, tidak clickbait", max_length=500)
    visual_style: str = Field(default="VYRO MEDIA: black, white, neon lime, diagonal, cinematic", max_length=500)
    template_id: str | None = Field(default=None, max_length=120)
    paid_partnership: bool = False
    ai_generated_media: bool = False
    human_review_required: bool = True
    notes: str | None = Field(default=None, max_length=2000)

    @field_validator("content_id")
    @classmethod
    def normalize_id(cls, value: str) -> str:
        if ".." in value or value.startswith("."):
            raise ValueError("content_id tidak boleh berupa path traversal")
        return value

    @field_validator("hashtags")
    @classmethod
    def clean_hashtags(cls, values: list[str]) -> list[str]:
        cleaned: list[str] = []
        for item in values:
            tag = item.strip().lstrip("#")
            if tag and re.fullmatch(r"[A-Za-z0-9_]{1,50}", tag):
                cleaned.append(tag)
        return list(dict.fromkeys(cleaned))[:8]

    @field_validator("reference_asset_ids")
    @classmethod
    def clean_reference_ids(cls, values: list[str]) -> list[str]:
        out = []
        for value in values:
            item = value.strip()
            if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{1,119}", item) or ".." in item:
                raise ValueError("reference_asset_ids berisi ID yang tidak valid")
            out.append(item)
        return list(dict.fromkeys(out))

    @model_validator(mode="after")
    def enforce_review(self):
        if not self.human_review_required:
            raise ValueError("human_review_required harus true; persetujuan publikasi tidak dilakukan di Intake")
        return self

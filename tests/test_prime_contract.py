import pytest
from pydantic import ValidationError
from vyro_script_intake.models import ScriptBrief


def make_brief(**updates):
    data = {
        "content_id": "vyro-demo-001", "title": "Konten promosi produk lokal",
        "pillar": "brand_promotion", "objective": "Memperkenalkan satu manfaat produk secara jelas",
        "audience": "Pemilik UMKM dan pembeli di Indonesia", "platform": "instagram_reels",
        "hook": "Produk ini punya satu keunggulan yang perlu diketahui.",
        "narration": "Tampilkan produk, jelaskan manfaat yang bisa dibuktikan, lalu ajak penonton melihat detailnya.",
        "call_to_action": "Simpan ide ini untuk konten berikutnya.",
        "human_review_required": True,
    }
    data.update(updates)
    return data


def test_brief_accepts_platform_and_defaults():
    brief = ScriptBrief.model_validate(make_brief())
    assert brief.platform == "instagram_reels"
    assert brief.human_review_required is True


def test_brief_rejects_non_human_review_flow():
    with pytest.raises(ValidationError):
        ScriptBrief.model_validate(make_brief(human_review_required=False))


def test_asset_rejects_unsafe_scheme():
    with pytest.raises(ValidationError):
        ScriptBrief.model_validate(make_brief(assets=[{"path_or_url":"javascript:alert(1)","media_type":"image"}]))

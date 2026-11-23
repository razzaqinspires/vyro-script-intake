import json
from pathlib import Path
import pytest
from pydantic import ValidationError
from vyro_script_intake.models import ScriptBrief

def test_example_brief_is_valid():
    path = Path("examples/brief_umkm.json")
    brief = ScriptBrief.model_validate_json(path.read_text(encoding="utf-8"))
    assert brief.content_id == "vyro-2026-001"
    assert brief.human_review_required is True

def test_rejects_path_traversal_id():
    data = json.loads(Path("examples/brief_umkm.json").read_text())
    data["content_id"] = "../secret"
    with pytest.raises(ValidationError):
        ScriptBrief.model_validate(data)

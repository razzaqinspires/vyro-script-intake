from pathlib import Path
import json
import typer
from rich import print
from .models import ScriptBrief

app = typer.Typer(no_args_is_help=True, help="VYRO MEDIA Script Intake")

@app.command()
def validate(source: Path = typer.Argument(..., exists=True, readable=True)) -> None:
    """Validate a JSON content brief."""
    try:
        brief = ScriptBrief.model_validate_json(source.read_text(encoding="utf-8"))
    except Exception as exc:
        raise typer.Exit(code=2) from exc
    print(f"[green]VALID[/green] {brief.content_id} — {brief.title}")

@app.command()
def normalize(
    source: Path = typer.Argument(..., exists=True, readable=True),
    output: Path = typer.Option(..., "--output", writable=True),
) -> None:
    """Validate and write canonical JSON for downstream components."""
    brief = ScriptBrief.model_validate_json(source.read_text(encoding="utf-8"))
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(brief.model_dump_json(indent=2), encoding="utf-8")
    print(f"[green]Normalized:[/green] {output}")

@app.command("export-schema")
def export_schema(output: Path = typer.Option(..., "--output")) -> None:
    """Export the JSON Schema contract."""
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(ScriptBrief.model_json_schema(), ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[green]Schema:[/green] {output}")

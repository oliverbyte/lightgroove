"""Generate a plain JS UI shell that fetches fixtures from the HTTP API and renders sliders."""
from __future__ import annotations

from pathlib import Path


def generate_ui(fixture_manager, output_dir: Path, api_base: str = "") -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    out_file = output_dir / "index.html"

    template_path = Path(__file__).parent / "templates" / "index.html"
    if not template_path.exists():
        raise FileNotFoundError(f"UI template missing: {template_path}")

    raw_template = template_path.read_text(encoding="utf-8")
    rendered = (
        raw_template
        .replace("__API_BASE__", api_base or "")
        .replace("__API_BASE_LABEL__", api_base or "(relative)")
    )

    out_file.write_text(rendered, encoding="utf-8")
    return out_file

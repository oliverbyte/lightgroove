"""Generate a plain JS UI shell that fetches fixtures from the HTTP API and renders sliders."""
from __future__ import annotations

from pathlib import Path


def generate_ui(fixture_manager, output_dir: Path, api_base: str = "") -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    out_file = output_dir / "index.html"

    template_dir = Path(__file__).parent / "templates"
    base_template_path = template_dir / "base.html"
    
    if not base_template_path.exists():
        raise FileNotFoundError(f"Base template missing: {base_template_path}")

    # Load base template
    base_template = base_template_path.read_text(encoding="utf-8")
    
    # Load section templates
    globals_section = _load_template(template_dir / "section_globals.html")
    tab_faders = _load_template(template_dir / "tab_faders.html")
    tab_colors = _load_template(template_dir / "tab_colors.html")
    
    # Insert globals section into faders tab
    tab_faders = tab_faders.replace("{GLOBALS_SECTION}", globals_section)
    
    # Combine all templates
    rendered = (
        base_template
        .replace("{TAB_FADERS}", tab_faders)
        .replace("{TAB_COLORS}", tab_colors)
        .replace("__API_BASE__", api_base or "")
        .replace("__API_BASE_LABEL__", api_base or "(relative)")
    )

    out_file.write_text(rendered, encoding="utf-8")
    return out_file


def _load_template(template_path: Path) -> str:
    """Load a template file and return its content."""
    if not template_path.exists():
        raise FileNotFoundError(f"Template missing: {template_path}")
    return template_path.read_text(encoding="utf-8")

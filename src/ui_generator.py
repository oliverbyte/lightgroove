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

    # Copy static assets
    (output_dir / "styles.css").write_text(
        _load_template(template_dir / "styles.css"), encoding="utf-8"
    )
    (output_dir / "script.js").write_text(
        _load_template(template_dir / "script.js").replace("__API_BASE__", api_base or ""),
        encoding="utf-8",
    )

    # Load base template
    base_template = base_template_path.read_text(encoding="utf-8")

    # Load section templates
    globals_section = _load_template(template_dir / "section_globals.html")
    tab_globals = _load_template(template_dir / "tab_globals.html")
    tab_faders = _load_template(template_dir / "tab_faders.html")
    tab_scenes = _load_template(template_dir / "tab_scenes.html")
    tab_colors = _load_template(template_dir / "tab_colors.html")
    tab_move = _load_template(template_dir / "tab_move.html")
    tab_fixtures = _load_template(template_dir / "tab_fixtures.html")
    tab_patch = _load_template(template_dir / "tab_patch.html")
    tab_config = _load_template(template_dir / "tab_config.html")
    config_logic = _load_template(template_dir / "config_logic.js")
    patch_logic = _load_template(template_dir / "patch_logic.js")
    fixture_editor_logic = _load_template(template_dir / "fixture_editor_logic.js")

    # Insert globals section into globals tab
    tab_globals = tab_globals.replace("{GLOBALS_SECTION}", globals_section)

    # Combine all templates
    rendered = (
        base_template
        .replace("{TAB_GLOBALS}", tab_globals)
        .replace("{TAB_FADERS}", tab_faders)
        .replace("{TAB_SCENES}", tab_scenes)
        .replace("{TAB_COLORS}", tab_colors)
        .replace("{TAB_MOVE}", tab_move)
        .replace("{TAB_FIXTURES}", tab_fixtures)
        .replace("{TAB_PATCH}", tab_patch)
        .replace("{TAB_CONFIG}", tab_config)
        .replace("{CONFIG_LOGIC}", config_logic)
        .replace("{PATCH_LOGIC}", patch_logic)
        .replace("{FIXTURE_EDITOR_LOGIC}", fixture_editor_logic)
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

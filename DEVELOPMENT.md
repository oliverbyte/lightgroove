# LightGroove Development Guide

## Architecture

### Project Structure

The project uses modular HTML templates:
- `src/templates/base.html`: Main structure with JavaScript
- `src/templates/section_globals.html`: Globals controls section
- `src/templates/tab_globals.html`: Globals tab container
- `src/templates/tab_faders.html`: Faders tab with fixture cards
- `src/templates/tab_colors.html`: Colors tab with static colors and FX buttons

Templates are combined by `src/ui_generator.py` during startup.

### Backend Modules

- **`main.py`**: Application entry point, starts Flask server and DMX controller
- **`src/dmx_controller.py`**: Core DMX engine, manages universe buffers and ArtNet output
- **`src/fixture_manager.py`**: Fixture and patch configuration, channel mapping
- **`src/color_manager.py`**: Color effects engine (Random 1/2/3) with BPM synchronization
- **`src/http_api.py`**: Flask REST API for UI interactions
- **`src/ui_generator.py`**: Template assembly and HTML generation

## Development Setup

### Requirements
- Python 3.9+
- virtualenv recommended

```bash
git clone https://github.com/oliverbyte/lightgroove.git
cd lightgroove
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

Then open http://localhost:5555 in your browser.

## Automated Screenshot Updates

This project includes a Git pre-push hook that automatically updates UI screenshots before pushing to remote.

### Setup

The hook is already installed at `.git/hooks/pre-push` (not tracked in git).

To set up on a new clone:

```bash
# Copy the pre-push hook
cat > .git/hooks/pre-push << 'EOF'
#!/bin/bash
# Pre-push hook to automatically update screenshots before pushing

echo "🔍 Checking for UI changes..."

# Run screenshot script
python3.9 take_screenshots.py

# Check if screenshots changed
if git diff --quiet img/screenshot_faders.png img/screenshot_colors.png; then
    echo "✓ Screenshots are up to date"
else
    echo "📸 Screenshots updated, adding to commit..."
    git add img/screenshot_faders.png img/screenshot_colors.png
    git commit --amend --no-edit
    echo "✓ Screenshots committed"
fi

exit 0
EOF

# Make it executable
chmod +x .git/hooks/pre-push
```

### Manual Screenshot Update

To manually update screenshots:

```bash
python3.9 take_screenshots.py
```

Requires: `pip install playwright && playwright install chromium`

## Windows Installer

### Automated Build Process

The project uses GitHub Actions to automatically build Windows installers on every push to the `main` branch. The workflow:

1. Sets up Python 3.9 on Windows
2. Installs dependencies
3. Runs PyInstaller to create standalone executable
4. Runs Inno Setup to create installer
5. Publishes `LightGrooveSetup.exe` as GitHub Release

See [`.github/workflows/windows-installer.yml`](.github/workflows/windows-installer.yml) for details.

### Local Testing

To test the installer build locally on Windows:

```bash
# Install PyInstaller
pip install pyinstaller

# Build executable
pyinstaller LightGroove.spec

# Output: dist/LightGroove.exe
```

For Inno Setup installer, download and install [Inno Setup](https://jsteam.org/innosetup/), then compile `installer_script.iss`.

### PyInstaller Configuration

[`LightGroove.spec`](LightGroove.spec) defines the build configuration:
- **hiddenimports**: All `src.*` modules must be explicitly listed (PyInstaller doesn't auto-detect local imports)
- **datas**: Bundles `config/` and `src/templates/` directories
- **onefile**: Creates single executable

If you add new modules in `src/`, update the `hiddenimports` list.

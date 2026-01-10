# LightGroove Development Guide

This guide covers the development setup, architecture, and contribution guidelines for LightGroove.

🌐 **[Website](https://oliverbyte.github.io/lightgroove/)** | 📖 **[Documentation](https://oliverbyte.github.io/lightgroove/docs)** | ❓ **[FAQ](https://oliverbyte.github.io/lightgroove/faq)**

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

This project includes a Git pre-push hook that automatically updates UI screenshots before pushing to the main branch. Screenshots are only updated when pushing to `main`, not to other branches.

### Setup

The hook is installed at `.git/hooks/pre-push`.

To set up on a new clone:

```bash
# Copy the pre-push hook from the repository
cp .github/hooks/pre-push .git/hooks/pre-push

# Make it executable
chmod +x .git/hooks/pre-push
```

The hook will automatically run screenshots only when pushing to the main branch.

### Manual Screenshot Update

To manually update screenshots:

```bash
python take_screenshots.py
```

Requires: `pip install playwright && playwright install chromium`

## Website Development

The project website is built with Jekyll and hosted on GitHub Pages. All website files are in the `website/` directory.

### Local Preview

To preview the website locally:

```bash
./run_website.sh
```

This uses Docker to run Jekyll and serves the site at http://localhost:4000/lightgroove/

For more preview options, see [PREVIEW.md](PREVIEW.md).

### Website Structure

- `website/_pages/`: Content pages (features, installation, docs, glossary, FAQ, imprint)
- `website/_layouts/`: Page templates
- `website/assets/`: CSS and JavaScript
- `website/img/`: Screenshot images

### Deployment

The website automatically deploys to GitHub Pages when changes are pushed to the `main` branch. The GitHub Actions workflow is defined in `.github/workflows/pages.yml`.

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

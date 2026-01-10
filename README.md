# LightGroove

DMX lighting controller with web-based UI featuring real-time fader control and color effects. Outputs ArtNet/virtual DMX with per-fixture control based on your patch and fixture definitions.

🌐 **[Visit Website](https://oliverbyte.github.io/lightgroove/)** | 📖 **[Documentation](https://oliverbyte.github.io/lightgroove/docs)** | ❓ **[FAQ](https://oliverbyte.github.io/lightgroove/faq)** | 📘 **[Glossary](https://oliverbyte.github.io/lightgroove/glossary)**

## Screenshots
![UI Globals](img/screenshot_globals.png)
![UI Faders](img/screenshot_faders.png)
![UI Colors](img/screenshot_colors.png)
![UI Config](img/screenshot_config.png)

## Features

### DMX / ArtNet Output
- Sends ArtNet by default (monitor or ArtNet node required)
- Works with any ArtNet-to-DMX interface (e.g., Enttec ODE)
- Universe mapping in `config/artnet.json` (DMX universe 1 → ArtNet universe 0)

### Web UI

**Globals Tab**:
- **Master**: Global intensity control (0-100%) that scales all DMX output in real-time
- **FX BPM**: Control speed of color effects (1-480 BPM)
- **FX Fade**: Smooth color transitions (0-100% of beat interval)

**Faders Tab**:
- Compact fixture cards with vertical faders in channel order
- Real-time DMX values (0-255) with live updates
- Responsive layout that adapts to screen width

**Colors Tab**:
- **Static Colors**: 10 preset buttons (Red, Green, Blue, Cyan, Magenta, Yellow, White, Orange, Purple, Black)
- **Color FX**: Server-side effects that run independently
  - Random 1: All fixtures display same color, cycles at BPM speed
  - Random 2: Each fixture gets different random color at each beat
  - Random 3: Alternates between even/odd patches with black (strobe effect)
  - Random 4: Chaser effect - one fixture at a time in sequence with random colors
  - Smooth fade transitions blend colors over the beat interval (adjustable via FX Fade)
- Active color and FX button highlighting with multi-color support for Random 2/3/4

**Config Tab**:
- **ArtNet Nodes**: Add, edit, and delete ArtNet output nodes with IP addresses and universes
- **Universe Mapping**: Configure which DMX universe maps to which ArtNet node and universe
- **Colors**: Edit RGBW color definitions (0-1 range) with live preview, add/remove colors
- **Global Settings**: Configure default output mode and FPS
- Changes are saved immediately and automatically reload without server restart

## Installation

### Windows Installer (Recommended)
Download the latest `LightGrooveSetup.exe` from the [Releases](https://github.com/oliverbyte/lightgroove/releases) page. The installer is automatically built and published whenever changes are pushed to the main branch.

After installation, launch LightGroove from the Start Menu or Desktop shortcut. The web UI will automatically open at http://localhost:5555.

### macOS via Homebrew
```bash
brew tap oliverbyte/lightgroove https://github.com/oliverbyte/lightgroove.git
brew install --HEAD oliverbyte/lightgroove/lightgroove
lightgroove
```

### From Source
Requirements: Python 3.9+, virtualenv recommended

```bash
git clone https://github.com/oliverbyte/lightgroove.git
cd lightgroove
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

Then open http://localhost:5555 in your browser.

## Configuration

- **`config/fixtures.json`**: Fixture profiles with channel definitions
- **`config/patch.json`**: Patched fixtures per universe with DMX addresses
- **`config/artnet.json`**: ArtNet targets and universe mapping
- **`config/colors.json`**: Color definitions for static colors and FX (RGBW values 0.0-1.0)

All configuration can be edited via the **Config tab** in the web UI. Changes are saved immediately and the server reloads automatically without restart.

## Changelog

### January 2026
- **Config UI**: Full web-based configuration editor for ArtNet nodes, universe mapping, colors, and global settings with auto-reload
- **Dynamic Color Buttons**: Static color buttons automatically display actual RGBW values from color definitions
- **Color Editor**: Add, edit, and delete colors with RGBW sliders and live preview
- **Random 4 FX**: Chaser effect that lights one fixture at a time in sequence with random colors
- **Active Color Indication**: Color and FX buttons highlight to show what's currently active
- **Multi-Color Highlighting**: Support for displaying multiple active colors in Random 2/3/4 effects
- **Color FX Engine**: Server-side color effects (Random 1-4) with BPM sync and smooth fade transitions
- **Fade Control**: Adjustable fade time (0-100%) for smooth color transitions
- **FX BPM Control**: Set effect speed from 1-480 BPM
- **Web UI**: Initial release with Globals, Faders, and Colors tabs
- **Real-time Faders**: Per-fixture channel control with live DMX value display
- **Master Control**: Global intensity scaling for all DMX output
- **ArtNet Output**: DMX output via ArtNet with universe mapping

## Contributing

For development setup, architecture details, and contribution guidelines, see [DEVELOPMENT.md](DEVELOPMENT.md).


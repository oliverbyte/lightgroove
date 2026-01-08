# LightGroove

DMX lighting controller with web-based UI featuring real-time fader control and color effects. Outputs ArtNet/virtual DMX with per-fixture control based on your patch and fixture definitions.

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
  - Smooth fade transitions blend colors over the beat interval (adjustable via FX Fade)
- Active color and FX button highlighting with multi-color support for Random 2/3

![UI Globals](img/screenshot_globals.png)
![UI Faders](img/screenshot_faders.png)
![UI Colors](img/screenshot_colors.png)

## Installation

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

Restart after configuration changes to regenerate the UI.

## Development

The project uses modular HTML templates:
- `src/templates/base.html`: Main structure
- `src/templates/section_globals.html`: Globals controls
- `src/templates/tab_globals.html`: Globals tab
- `src/templates/tab_faders.html`: Faders tab
- `src/templates/tab_colors.html`: Colors tab

Templates are combined by `src/ui_generator.py` during startup.


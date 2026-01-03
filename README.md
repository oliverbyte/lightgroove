# LightGroove

DMX controller with a simple web UI. Outputs ArtNet/virtual DMX and renders per-fixture faders based on your patch and fixture definitions.

## DMX / ArtNet
- LightGroove sends ArtNet by default; use a monitor or an ArtNet node to receive it.
- Any ArtNet-to-DMX interface (e.g., Enttec ODE or similar) can translate the ArtNet stream to a physical DMX line for standard DMX fixtures.
- Universe mapping is set in `config/artnet.json` (DMX universe 1 maps to ArtNet universe 0 by default).

## UI
- **Faders Tab**: Per-fixture vertical faders in channel order with live real-time DMX values (0–255) displayed continuously.
- **Colors Tab**: Quick color preset buttons (Red, Green, Blue, Cyan, Magenta, Yellow, White, Orange, Purple) that apply to all fixtures simultaneously.
- **Blackout**: Button sends blackout and zeros all faders.
- Tab navigation allows quick switching between fader control and color presets.
- Screenshot:

![UI Faders](img/screenshot_faders.png)

## Install (macOS via Homebrew)
```bash
brew tap oliverbyte/lightgroove https://github.com/oliverbyte/lightgroove.git
brew install --HEAD oliverbyte/lightgroove/lightgroove
lightgroove
```
Then open the printed UI URL (default http://0.0.0.0:5555). The Homebrew formula installs dependencies in a virtualenv and runs from source (no Gatekeeper prompts).

## Install from source
- Python 3.9+ (virtualenv recommended)
- Dependencies: `pip install -r requirements.txt`
- ArtNet node or monitor (defaults to localhost/unicast on universe 0 mapped from DMX universe 1)

```bash
source .venv/bin/activate  # if using venv
python main.py
```
Then open the printed UI URL (default http://0.0.0.0:5555).

## Configuration
- `config/fixtures.json`: Fixture profiles (channel order defines fader order in UI).
- `config/patch.json`: Patched fixtures per universe (DMX addresses).
- `config/artnet.json`: ArtNet targets and universe mapping (set `ip` and `broadcast`).

## Notes
- If you change fixtures/patch, restart `python main.py` to regenerate the UI.

# LightGroove

DMX controller with a simple web UI. Outputs ArtNet/virtual DMX and renders per-fixture faders based on your patch and fixture definitions.

## UI
- Per-fixture vertical faders in channel order; values shown as 0–255 DMX.
- Blackout button sends blackout and zeros UI faders.
- Screenshot:

![UI Faders](img/screenshot_faders.png)

## Prerequisites
- Python 3.9+ (virtualenv recommended)
- Dependencies: `pip install -r requirements.txt`
- ArtNet node or monitor (defaults to localhost/unicast on universe 0 mapped from DMX universe 1)

## Run
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

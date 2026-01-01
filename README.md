# LightGroove

DMX backend for RGBW PAR fixtures with ArtNet and multi-universe support. Control is via the built-in web UI / HTTP API (OSC server disabled).

## Overview
LightGroove is a Python backend that outputs DMX via ArtNet, serial DMX, or a virtual mode. Fixtures and patches are defined in JSON, making it easy to add fixture types, multiple instances, and multiple ArtNet nodes. Use the web UI at http://localhost:5000 instead of OSC.

Author: https://github.com/oliverbyte
License: GNU Affero General Public License v3.0 (AGPL-3.0)

## Features
- Web UI / HTTP control for colors, dimmer, and channels
- ArtNet output with multiple nodes and universes
- Serial DMX output (optional)
- Virtual mode for development without hardware
- Multi-universe support
- Multiple fixture instances of any type
- JSON-based fixtures and patch definitions

## Quick Start
```bash
python -m venv .venv
source .venv/bin/activate   # macOS/Linux
pip install -r requirements.txt
python main.py
```
Web UI/API listens on http://localhost:5000 by default (override with LIGHTGROOVE_HTTP_PORT).

## Configuration Files
- config/fixtures.json: Fixture type definitions (channel layout)
- config/patch.json: Fixture instances per universe and start addresses
- config/artnet.json: ArtNet nodes, universe mapping, output modes, FPS, optional serial port

### Example fixtures.json
```json
{
  "rgbw_par": {
    "name": "RGBW PAR",
    "manufacturer": "Generic",
    "channels": [
      {"index": 0, "name": "red", "type": "color", "range": [0, 255]},
      {"index": 1, "name": "green", "type": "color", "range": [0, 255]},
      {"index": 2, "name": "blue", "type": "color", "range": [0, 255]},
      {"index": 3, "name": "white", "type": "color", "range": [0, 255]},
      {"index": 4, "name": "dimmer", "type": "intensity", "range": [0, 255]}
    ]
  }
}
```

### Example patch.json (multi-universe)
```json
{
  "universes": {
    "1": {
      "fixtures": [
        {"id": "par1", "type": "rgbw_par", "start_address": 1, "description": "Main RGBW PAR"},
        {"id": "par2", "type": "rgbw_par", "start_address": 10, "description": "Second RGBW PAR"}
      ]
    },
    "2": {
      "fixtures": [
        {"id": "par3", "type": "rgbw_par", "start_address": 1, "description": "Universe 2 RGBW PAR"}
      ]
    }
  }
}
```
Note: Each universe has 512 channels. Ensure fixture address ranges do not overlap.

### Example artnet.json
```json
{
  "nodes": [
    {
      "id": "node1",
      "name": "Main ArtNet Node",
      "ip": "192.168.1.100",
      "port": 6454,
      "universes": [0, 1],
      "enabled": true,
      "description": "Primary ArtNet node for universes 1-2"
    }
  ],
  "universe_mapping": {
    "1": {"node_id": "node1", "artnet_universe": 0, "output_mode": "artnet"},
    "2": {"node_id": "node1", "artnet_universe": 1, "output_mode": "artnet"}
  },
  "default_output_mode": "virtual",
  "fps": 44,
  "serial_port": null
}
```
Output modes: `artnet`, `serial`, `virtual`.

## Running
```bash
python main.py
```
- Uses config/artnet.json to configure ArtNet and serial
- Uses config/patch.json to place fixtures in universes
- Uses config/fixtures.json for fixture channel layouts

## HTTP/Web UI
Open http://localhost:5000 to control fixtures. The UI is generated at start from the current patch (config/patch.json) and lists all fixtures with sliders for color/dimmer and other channels. 

## Project Structure
```
LightGroove/
├── config/
│   ├── fixtures.json       # Fixture type definitions
│   ├── patch.json          # Fixture instances and addresses
│   └── artnet.json         # ArtNet nodes, universe mapping, output modes
├── src/
│   ├── dmx_controller.py   # Multi-universe DMX output (ArtNet/Serial/Virtual)
│   ├── fixture_manager.py  # Fixture management
│   └── osc_server.py       # OSC server
├── main.py                 # Entry point
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

## Extending
- Add fixture types in config/fixtures.json.
- Add more fixtures or universes in config/patch.json (avoid overlapping addresses).
- Add more ArtNet nodes and mapping in config/artnet.json.

## Troubleshooting
- ArtNet not working:
  - Check IP in artnet.json; ensure same network; ensure `stupidArtnet` installed; Node enabled.
- Serial DMX not working:
  - Set `serial_port` in artnet.json and `output_mode: "serial"` for the universe; check permissions to the port.
- OSC not received:
  - Verify port 8000 open; check firewall; test with oscsend.
- Fixture not responding:
  - Check start_address in patch.json; channel names in fixtures.json; universe mapping in artnet.json; avoid overlapping channels.

## License
GNU Affero General Public License v3.0 (AGPL-3.0)

## Author
https://github.com/oliverbyte

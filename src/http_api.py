"""Simple HTTP API bridge for LightGroove.
Converts HTTP requests to fixture manager actions and serves the generated UI.
Author: https://github.com/oliverbyte
"""
from __future__ import annotations

import json
import os
import threading
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from typing import Any, Dict, Optional


class HttpApiServer:
    """Threaded HTTP server exposing a JSON API and serving the generated UI."""

    def __init__(self, fixture_manager, ui_dir: Path, host: str = "0.0.0.0", port: int = 5000, color_fx=None):
        self.fixture_manager = fixture_manager
        self.ui_dir = ui_dir
        self.host = host
        self.port = port
        self.color_fx = color_fx
        self._server = None
        self._thread = None

    def start(self):
        """Start the HTTP server in a background thread."""
        handler = self._make_handler()
        self._server = ThreadingHTTPServer((self.host, self.port), handler)
        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)
        self._thread.start()
        print(f"HTTP UI/API: http://{self.host}:{self.port}")

    def stop(self):
        """Stop the HTTP server."""
        if self._server:
            self._server.shutdown()
            self._server.server_close()
            print("HTTP UI/API: Stopped")

    def _make_handler(self):
        fixture_manager = self.fixture_manager
        ui_dir = self.ui_dir
        color_fx = self.color_fx

        class Handler(BaseHTTPRequestHandler):
            def _set_headers(self, status: int = 200, content_type: str = "application/json"):
                self.send_response(status)
                self.send_header("Content-Type", content_type)
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()

            def _read_json(self) -> Dict[str, Any]:
                length = int(self.headers.get("Content-Length", "0"))
                if length == 0:
                    return {}
                body = self.rfile.read(length)
                try:
                    return json.loads(body.decode("utf-8"))
                except Exception:
                    return {}

            def do_OPTIONS(self):
                self.send_response(204)
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
                self.send_header("Access-Control-Allow-Headers", "Content-Type")
                self.end_headers()

            def do_GET(self):
                if self.path.startswith("/api/fixtures"):
                    fixtures = []
                    for fid, data in fixture_manager.fixtures.items():
                        fixtures.append(
                            {
                                "id": fid,
                                "type": data["type"],
                                "universe": data["universe"],
                                "start_address": data["start_address"],
                                "channels": data["config"].get("channels", []),
                            }
                        )
                    self._set_headers()
                    self.wfile.write(json.dumps({"fixtures": fixtures}).encode("utf-8"))
                    return

                if self.path.startswith("/api/states"):
                    states = {}
                    for fid, data in fixture_manager.fixtures.items():
                        states[fid] = data.get("state", {})
                    self._set_headers()
                    self.wfile.write(json.dumps(states).encode("utf-8"))
                    return

                if self.path.startswith("/api/colors"):
                    from color_manager import COLORS
                    self._set_headers()
                    self.wfile.write(json.dumps(COLORS).encode("utf-8"))
                    return

                if self.path.startswith("/api/fx/status") and color_fx:
                    self._set_headers()
                    self.wfile.write(json.dumps(color_fx.get_status()).encode("utf-8"))
                    return

                if self.path.startswith("/api/grandmaster"):
                    self._set_headers()
                    self.wfile.write(json.dumps({"level": fixture_manager.dmx.grandmaster}).encode("utf-8"))
                    return

                if self.path.startswith("/api/fx/bpm") and color_fx:
                    self._set_headers()
                    self.wfile.write(json.dumps({"bpm": color_fx.bpm}).encode("utf-8"))
                    return

                if self.path.startswith("/api/fx/fadetime") and color_fx:
                    self._set_headers()
                    self.wfile.write(json.dumps({"fade_percentage": color_fx.fade_percentage}).encode("utf-8"))
                    return

                if self.path.startswith("/api/config/artnet"):
                    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'artnet.json')
                    try:
                        with open(config_path, 'r') as f:
                            config = json.load(f)
                        self._set_headers()
                        self.wfile.write(json.dumps(config).encode("utf-8"))
                    except Exception as e:
                        self._set_headers(500)
                        self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
                    return

                if self.path.startswith("/api/config/colors"):
                    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'colors.json')
                    try:
                        with open(config_path, 'r') as f:
                            config = json.load(f)
                        self._set_headers()
                        self.wfile.write(json.dumps(config).encode("utf-8"))
                    except Exception as e:
                        self._set_headers(500)
                        self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
                    return

                # Serve index.html for root
                if self.path in ["/", "/index.html"]:
                    index_path = ui_dir / "index.html"
                    if index_path.exists():
                        data = index_path.read_bytes()
                        self._set_headers(content_type="text/html; charset=utf-8")
                        self.wfile.write(data)
                    else:
                        self._set_headers(404)
                        self.wfile.write(b"Not found")
                    return

                # Serve static files if any
                requested = (ui_dir / self.path.lstrip("/ ")).resolve()
                try:
                    if ui_dir in requested.parents and requested.is_file():
                        mime = "text/plain"
                        if requested.suffix == ".js":
                            mime = "application/javascript"
                        elif requested.suffix == ".css":
                            mime = "text/css"
                        elif requested.suffix == ".html":
                            mime = "text/html; charset=utf-8"
                        data = requested.read_bytes()
                        self._set_headers(content_type=mime)
                        self.wfile.write(data)
                        return
                except Exception:
                    pass

                self._set_headers(404)
                self.wfile.write(b"Not found")

            def do_POST(self):
                path = self.path
                payload = self._read_json()

                try:
                    if path.startswith("/api/fixture/") and "/color" in path:
                        fixture_id = path.split("/")[3]
                        r = float(payload.get("r", 0))
                        g = float(payload.get("g", 0))
                        b = float(payload.get("b", 0))
                        w = float(payload.get("w", 0))
                        fixture_manager.set_fixture_color(fixture_id, r, g, b, w)
                        self._set_headers()
                        self.wfile.write(b"{}")
                        return

                    if path.startswith("/api/fixture/") and "/dimmer" in path:
                        fixture_id = path.split("/")[3]
                        value = float(payload.get("value", 0))
                        fixture_manager.set_fixture_dimmer(fixture_id, value)
                        self._set_headers()
                        self.wfile.write(b"{}")
                        return

                    if path.startswith("/api/fixture/") and "/channel/" in path:
                        parts = path.split("/")
                        fixture_id = parts[3]
                        channel_name = parts[5]
                        value = float(payload.get("value", 0))
                        fixture_manager.set_fixture_channel(fixture_id, channel_name, value)
                        self._set_headers()
                        self.wfile.write(b"{}")
                        return

                    if path == "/api/grandmaster":
                        level = float(payload.get("level", 1.0))
                        fixture_manager.dmx.set_grandmaster(level)
                        fixture_manager.reapply_all_states()
                        self._set_headers()
                        self.wfile.write(b"{}")
                        return

                    if path == "/api/blackout":
                        fixture_manager.blackout_all()
                        self._set_headers()
                        self.wfile.write(b"{}")
                        return

                    if path == "/api/all/color":
                        r = float(payload.get("r", 0))
                        g = float(payload.get("g", 0))
                        b = float(payload.get("b", 0))
                        w = float(payload.get("w", 0))
                        for fixture_id in fixture_manager.list_fixtures():
                            fixture_manager.set_fixture_color(fixture_id, r, g, b, w)
                        
                        # Update color_fx current_colors to match the applied color (single color)
                        if color_fx:
                            from src.color_manager import COLORS
                            # Find matching color name
                            for color_name, color_vals in COLORS.items():
                                if (abs(color_vals.get('r', 0) - r) < 0.01 and
                                    abs(color_vals.get('g', 0) - g) < 0.01 and
                                    abs(color_vals.get('b', 0) - b) < 0.01 and
                                    abs(color_vals.get('w', 0) - w) < 0.01):
                                    color_fx.current_colors = [color_name]
                                    break
                        
                        self._set_headers()
                        self.wfile.write(b"{}")
                        return

                    if path == "/api/fx/start" and color_fx:
                        fx_name = payload.get("fx", "random")
                        color_fx.start_fx(fx_name)
                        self._set_headers()
                        self.wfile.write(json.dumps(color_fx.get_status()).encode("utf-8"))
                        return

                    if path == "/api/fx/stop" and color_fx:
                        color_fx.stop_fx()
                        self._set_headers()
                        self.wfile.write(json.dumps(color_fx.get_status()).encode("utf-8"))
                        return

                    if path == "/api/fx/bpm" and color_fx:
                        bpm = int(payload.get("bpm", 120))
                        color_fx.set_bpm(bpm)
                        self._set_headers()
                        self.wfile.write(json.dumps(color_fx.get_status()).encode("utf-8"))
                        return

                    if path == "/api/fx/fadetime" and color_fx:
                        # Receive percentage from frontend (0.0-1.0)
                        fade_percentage = float(payload.get("fade_percentage", 0.0))
                        color_fx.set_fade_percentage(fade_percentage)
                        self._set_headers()
                        self.wfile.write(json.dumps(color_fx.get_status()).encode("utf-8"))
                        return

                    if path == "/api/config/artnet":
                        config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'artnet.json')
                        try:
                            # Write the entire config
                            with open(config_path, 'w') as f:
                                json.dump(payload, f, indent=2)
                            
                            # Reload DMX controller configuration
                            try:
                                fixture_manager.dmx.reload_config(config_path)
                            except Exception as reload_error:
                                print(f"Warning: Failed to reload DMX config: {reload_error}")
                            
                            self._set_headers()
                            self.wfile.write(json.dumps({"success": True, "reloaded": True}).encode("utf-8"))
                        except Exception as e:
                            self._set_headers(500)
                            self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
                        return

                    if path == "/api/config/colors":
                        config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'colors.json')
                        try:
                            # Write the entire config
                            with open(config_path, 'w') as f:
                                json.dump(payload, f, indent=2)
                            
                            # Reload colors in the color manager
                            try:
                                from color_manager import reload_colors
                                reload_colors()
                            except Exception as reload_error:
                                print(f"Warning: Failed to reload colors: {reload_error}")
                            
                            self._set_headers()
                            self.wfile.write(json.dumps({"success": True, "reloaded": True}).encode("utf-8"))
                        except Exception as e:
                            self._set_headers(500)
                            self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
                        return
                except Exception as exc:  # keep API resilient
                    self._set_headers(400)
                    self.wfile.write(json.dumps({"error": str(exc)}).encode("utf-8"))
                    return

                self._set_headers(404)
                self.wfile.write(b"{}")

        return Handler


def generate_fixture_summary(fixture_manager) -> Dict[str, Any]:
    """Return a summary of fixtures suitable for embedding in the UI."""
    fixtures = []
    for fid, data in fixture_manager.fixtures.items():
        fixtures.append(
            {
                "id": fid,
                "type": data["type"],
                "universe": data["universe"],
                "start_address": data["start_address"],
                "channels": data["config"].get("channels", []),
            }
        )
    return {"fixtures": fixtures}

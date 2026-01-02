"""Simple HTTP API bridge for LightGroove.
Converts HTTP requests to fixture manager actions and serves the generated UI.
Author: https://github.com/oliverbyte
"""
from __future__ import annotations

import json
import threading
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from typing import Any, Dict, Optional


class HttpApiServer:
    """Threaded HTTP server exposing a JSON API and serving the generated UI."""

    def __init__(self, fixture_manager, ui_dir: Path, config_paths: Dict[str, Path], dmx_controller=None, host: str = "0.0.0.0", port: int = 5000):
        self.fixture_manager = fixture_manager
        self.ui_dir = ui_dir
        self.config_paths = config_paths
        self.dmx_controller = dmx_controller
        self.host = host
        self.port = port
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
        config_paths = self.config_paths
        dmx_controller = self.dmx_controller

        class Handler(BaseHTTPRequestHandler):
            def _set_headers(self, status: int = 200, content_type: str = "application/json"):
                self.send_response(status)
                self.send_header("Content-Type", content_type)
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()

            def _load_config_content(self, name: str) -> Optional[Dict[str, Any]]:
                cfg_path = config_paths.get(name) if config_paths else None
                if not cfg_path:
                    return None
                try:
                    with open(cfg_path, "r") as f:
                        return json.load(f)
                except Exception:
                    return None

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
                if self.path.startswith("/api/config/"):
                    name = self.path.split("/")[3] if len(self.path.split("/")) > 3 else ""
                    content = self._load_config_content(name)
                    if content is None:
                        self._set_headers(404)
                        self.wfile.write(json.dumps({"error": "config not found"}).encode("utf-8"))
                        return
                    self._set_headers()
                    self.wfile.write(json.dumps(content).encode("utf-8"))
                    return

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

                    if path == "/api/blackout":
                        fixture_manager.blackout_all()
                        self._set_headers()
                        self.wfile.write(b"{}")
                        return

                        if path.startswith("/api/config/"):
                            name = path.split("/")[3] if len(path.split("/")) > 3 else ""
                            content = payload.get("data", payload)
                            if not isinstance(content, dict):
                                self._set_headers(400)
                                self.wfile.write(json.dumps({"error": "invalid payload"}).encode("utf-8"))
                                return
                            try:
                                if name == "fixtures":
                                    fixture_manager.reload_configs(fixtures_data=content)
                                elif name == "patch":
                                    fixture_manager.reload_configs(patch_data=content)
                                elif name == "artnet" and dmx_controller:
                                    cfg_path = config_paths.get("artnet") if config_paths else None
                                    dmx_controller.reload_config(cfg_path, content)
                                else:
                                    self._set_headers(404)
                                    self.wfile.write(json.dumps({"error": "config not found"}).encode("utf-8"))
                                    return
                                self._set_headers()
                                self.wfile.write(b"{}")
                            except Exception as exc:
                                self._set_headers(400)
                                self.wfile.write(json.dumps({"error": str(exc)}).encode("utf-8"))
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

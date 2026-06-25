"""MIDI device manager for LightGroove."""
from __future__ import annotations

import json
import threading
import time
from pathlib import Path
from typing import Dict, List, Optional


class MidiManager:
    def __init__(self, config_file: str):
        self._config_file = Path(config_file)
        self._lock = threading.Lock()
        self._active_inputs: Dict[str, object] = {}
        self._active_outputs: Dict[str, object] = {}
        self._last_event: Optional[dict] = None
        self._suppress_feedback: int = 0
        self._stop_event = threading.Event()
        self.fixture_manager = None   # set by main.py after init
        self.global_handlers: Dict[str, callable] = {}  # set by main.py after init
        self._config = {"active_inputs": [], "active_outputs": [], "mappings": []}
        self._load_config()
        self._reconnect_all()
        self._start_reconnect_thread()

    # ------------------------------------------------------------------
    # Backend / config
    # ------------------------------------------------------------------

    @staticmethod
    def _init_backend():
        """Force ALSA on Linux so JACK is never probed."""
        try:
            import rtmidi
            import mido
            mido.set_backend('mido.backends.rtmidi')
            if hasattr(rtmidi, 'API_LINUX_ALSA'):
                mido.backend.api = 'LINUX_ALSA'
        except Exception:
            pass

    def _load_config(self):
        self._init_backend()
        if self._config_file.exists():
            try:
                data = json.loads(self._config_file.read_text())
                self._config.update(data)
            except Exception:
                pass

    def _save_config(self):
        self._config_file.write_text(
            json.dumps(self._config, indent=2), encoding="utf-8"
        )

    def get_config(self) -> dict:
        with self._lock:
            return {
                "active_inputs": list(self._config["active_inputs"]),
                "active_outputs": list(self._config["active_outputs"]),
            }

    # ------------------------------------------------------------------
    # MIDI message handling
    # ------------------------------------------------------------------

    def _on_message(self, msg):
        if msg.type != "control_change":
            return

        event = {"midi_channel": msg.channel, "cc": msg.control, "value": msg.value}

        with self._lock:
            self._last_event = event
            mappings = [
                m for m in self._config["mappings"]
                if m["midi_channel"] == msg.channel and m["cc"] == msg.control
            ]
            fm = self.fixture_manager

        normalized = msg.value / 127.0
        with self._lock:
            self._suppress_feedback += 1
        try:
            for m in mappings:
                try:
                    if m["fixture_id"] == "_global":
                        handler = self.global_handlers.get(m["channel_name"])
                        if handler:
                            handler(normalized)
                    elif fm:
                        fm.set_fixture_channel(m["fixture_id"], m["channel_name"], normalized)
                except Exception:
                    pass
        finally:
            with self._lock:
                self._suppress_feedback -= 1

    def pop_last_event(self) -> Optional[dict]:
        with self._lock:
            event = self._last_event
            self._last_event = None
            return event

    # ------------------------------------------------------------------
    # Mapping management
    # ------------------------------------------------------------------

    def add_mapping(self, midi_channel: int, cc: int, fixture_id: str, channel_name: str):
        with self._lock:
            self._config["mappings"] = [
                m for m in self._config["mappings"]
                if not (m["fixture_id"] == fixture_id and m["channel_name"] == channel_name)
            ]
            self._config["mappings"].append({
                "midi_channel": midi_channel,
                "cc": cc,
                "fixture_id": fixture_id,
                "channel_name": channel_name,
            })
            self._save_config()

    def remove_mapping(self, fixture_id: str, channel_name: str):
        with self._lock:
            self._config["mappings"] = [
                m for m in self._config["mappings"]
                if not (m["fixture_id"] == fixture_id and m["channel_name"] == channel_name)
            ]
            self._save_config()

    def get_mappings(self) -> list:
        with self._lock:
            return list(self._config["mappings"])

    def send_cc(self, midi_channel: int, cc: int, value_normalized: float):
        """Send a CC message to all active output ports."""
        import mido
        cc_value = max(0, min(127, round(value_normalized * 127)))
        msg = mido.Message("control_change", channel=midi_channel, control=cc, value=cc_value)
        with self._lock:
            ports = list(self._active_outputs.values())
        for port in ports:
            try:
                port.send(msg)
            except Exception:
                pass

    def notify_channel_changed(self, fixture_id: str, channel_name: str, value: float):
        """Called by FixtureManager when a channel changes; echoes to mapped output ports."""
        with self._lock:
            if self._suppress_feedback > 0:
                return
            mappings = [
                m for m in self._config["mappings"]
                if m["fixture_id"] == fixture_id and m["channel_name"] == channel_name
            ]
        for m in mappings:
            self.send_cc(m["midi_channel"], m["cc"], value)

    def get_paired_devices(self) -> dict:
        import mido
        try:
            available_inputs = set(mido.get_input_names())
            available_outputs = set(mido.get_output_names())
        except Exception:
            available_inputs, available_outputs = set(), set()
        with self._lock:
            return {
                "inputs": [
                    {"name": n, "connected": n in available_inputs}
                    for n in self._config["active_inputs"]
                ],
                "outputs": [
                    {"name": n, "connected": n in available_outputs}
                    for n in self._config["active_outputs"]
                ],
            }

    def delete_pairing(self, name: str, direction: str):
        """Deactivate a device and clear all learned mappings."""
        with self._lock:
            if direction == "input":
                self._config["active_inputs"] = [n for n in self._config["active_inputs"] if n != name]
            elif direction == "output":
                self._config["active_outputs"] = [n for n in self._config["active_outputs"] if n != name]
            self._config["mappings"] = []
            self._save_config()

        # Close port outside lock
        if direction == "input":
            self._close_input(name)
        elif direction == "output":
            self._close_output(name)

    # ------------------------------------------------------------------
    # Port management
    # ------------------------------------------------------------------

    def _reconnect_all(self):
        """Close stale ports for disconnected devices, reopen for reconnected ones."""
        import mido
        try:
            available_inputs = set(mido.get_input_names())
            available_outputs = set(mido.get_output_names())
        except Exception:
            return

        with self._lock:
            configured_inputs = list(self._config["active_inputs"])
            configured_outputs = list(self._config["active_outputs"])
            open_inputs = set(self._active_inputs)
            open_outputs = set(self._active_outputs)

        # Close ports for devices that have disappeared
        for name in configured_inputs:
            if name in open_inputs and name not in available_inputs:
                print(f"MIDI: '{name}' disconnected, closing stale port")
                self._close_input(name)
        for name in configured_outputs:
            if name in open_outputs and name not in available_outputs:
                print(f"MIDI: '{name}' disconnected, closing stale port")
                self._close_output(name)

        # Re-snapshot after closures, then open any available-but-not-open ports
        with self._lock:
            open_inputs = set(self._active_inputs)
            open_outputs = set(self._active_outputs)

        for name in configured_inputs:
            if name in available_inputs and name not in open_inputs:
                self._open_input(name)
        for name in configured_outputs:
            if name in available_outputs and name not in open_outputs:
                self._open_output(name)

    def _start_reconnect_thread(self):
        t = threading.Thread(target=self._reconnect_loop, daemon=True, name="midi-reconnect")
        t.start()

    def _reconnect_loop(self):
        while not self._stop_event.wait(timeout=5):
            try:
                self._reconnect_all()
            except Exception as e:
                print(f"MIDI: reconnect check error: {e}")

    def _open_input(self, name: str):
        import mido
        try:
            port = mido.open_input(name, callback=self._on_message)
            with self._lock:
                self._active_inputs[name] = port
            print(f"MIDI: opened input '{name}'")
        except Exception as e:
            print(f"MIDI: failed to open input '{name}': {e}")

    def _open_output(self, name: str):
        import mido
        try:
            port = mido.open_output(name)
            with self._lock:
                self._active_outputs[name] = port
            print(f"MIDI: opened output '{name}'")
        except Exception as e:
            print(f"MIDI: failed to open output '{name}': {e}")

    def _close_input(self, name: str):
        with self._lock:
            port = self._active_inputs.pop(name, None)
        if port:
            try:
                port.close()
            except Exception:
                pass
            print(f"MIDI: closed input '{name}'")

    def _close_output(self, name: str):
        with self._lock:
            port = self._active_outputs.pop(name, None)
        if port:
            try:
                port.close()
            except Exception:
                pass
            print(f"MIDI: closed output '{name}'")

    # ------------------------------------------------------------------
    # Public activate / deactivate
    # ------------------------------------------------------------------

    def activate(self, name: str, direction: str):
        with self._lock:
            if direction == "input":
                already_open = name in self._active_inputs
                if name not in self._config["active_inputs"]:
                    self._config["active_inputs"].append(name)
            elif direction == "output":
                already_open = name in self._active_outputs
                if name not in self._config["active_outputs"]:
                    self._config["active_outputs"].append(name)
            else:
                return
            self._save_config()

        if not already_open:
            if direction == "input":
                self._open_input(name)
            else:
                self._open_output(name)

    def deactivate(self, name: str, direction: str):
        with self._lock:
            if direction == "input":
                self._config["active_inputs"] = [n for n in self._config["active_inputs"] if n != name]
            elif direction == "output":
                self._config["active_outputs"] = [n for n in self._config["active_outputs"] if n != name]
            else:
                return
            self._save_config()

        if direction == "input":
            self._close_input(name)
        else:
            self._close_output(name)

    def shutdown(self):
        self._stop_event.set()
        with self._lock:
            inputs = list(self._active_inputs)
            outputs = list(self._active_outputs)
        for name in inputs:
            self._close_input(name)
        for name in outputs:
            self._close_output(name)

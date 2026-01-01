"""
OSC Server
Receives OSC messages and controls fixtures
Author: https://github.com/oliverbyte
"""
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer
import threading
from typing import Any


class OSCServer:
    """OSC Server for fixture control"""
    
    def __init__(self, fixture_manager, ip: str = "0.0.0.0", port: int = 8000):
        """
        Initialize OSC server
        
        Args:
            fixture_manager: FixtureManager instance
            ip: IP address to bind to (default: 0.0.0.0 = all interfaces)
            port: UDP port to listen on (default: 8000)
        """
        self.fixture_manager = fixture_manager
        self.ip = ip
        self.port = port
        self.server = None
        self.server_thread = None
        
        # Setup OSC dispatcher
        self.dispatcher = Dispatcher()
        self._register_handlers()
    
    def _register_handlers(self):
        """Register OSC message handlers"""
        
        # Fixture control: /fixture/<id>/color/r <value>
        self.dispatcher.map("/fixture/*/color/r", self._handle_color_r)
        self.dispatcher.map("/fixture/*/color/g", self._handle_color_g)
        self.dispatcher.map("/fixture/*/color/b", self._handle_color_b)
        self.dispatcher.map("/fixture/*/color/w", self._handle_color_w)
        
        # Fixture color (all at once): /fixture/<id>/color <r> <g> <b> [w]
        self.dispatcher.map("/fixture/*/color", self._handle_color)
        
        # Fixture dimmer: /fixture/<id>/dimmer <value>
        self.dispatcher.map("/fixture/*/dimmer", self._handle_dimmer)
        
        # Channel control: /fixture/<id>/channel/<name> <value>
        self.dispatcher.map("/fixture/*/channel/*", self._handle_channel)
        
        # Blackout: /blackout
        self.dispatcher.map("/blackout", self._handle_blackout)
        
        # Info: /info
        self.dispatcher.map("/info", self._handle_info)
        
        # Catch-all for debugging
        self.dispatcher.set_default_handler(self._handle_default)
    
    def _extract_fixture_id(self, address: str, position: int = 2) -> str:
        """Extract fixture ID from OSC address"""
        parts = address.split('/')
        if len(parts) > position:
            return parts[position]
        return ""
    
    def _extract_channel_name(self, address: str) -> str:
        """Extract channel name from OSC address"""
        parts = address.split('/')
        if len(parts) > 4:
            return parts[4]
        return ""
    
    def _handle_color_r(self, address: str, *args: Any):
        """Handle /fixture/<id>/color/r <value>"""
        fixture_id = self._extract_fixture_id(address)
        if args and fixture_id:
            value = float(args[0])
            self.fixture_manager.set_fixture_channel(fixture_id, 'red', value)
            print(f"OSC: {address} -> {fixture_id} red = {value:.2f}")
    
    def _handle_color_g(self, address: str, *args: Any):
        """Handle /fixture/<id>/color/g <value>"""
        fixture_id = self._extract_fixture_id(address)
        if args and fixture_id:
            value = float(args[0])
            self.fixture_manager.set_fixture_channel(fixture_id, 'green', value)
            print(f"OSC: {address} -> {fixture_id} green = {value:.2f}")
    
    def _handle_color_b(self, address: str, *args: Any):
        """Handle /fixture/<id>/color/b <value>"""
        fixture_id = self._extract_fixture_id(address)
        if args and fixture_id:
            value = float(args[0])
            self.fixture_manager.set_fixture_channel(fixture_id, 'blue', value)
            print(f"OSC: {address} -> {fixture_id} blue = {value:.2f}")
    
    def _handle_color_w(self, address: str, *args: Any):
        """Handle /fixture/<id>/color/w <value>"""
        fixture_id = self._extract_fixture_id(address)
        if args and fixture_id:
            value = float(args[0])
            self.fixture_manager.set_fixture_channel(fixture_id, 'white', value)
            print(f"OSC: {address} -> {fixture_id} white = {value:.2f}")
    
    def _handle_color(self, address: str, *args: Any):
        """Handle /fixture/<id>/color <r> <g> <b> [w]"""
        fixture_id = self._extract_fixture_id(address)
        if fixture_id and len(args) >= 3:
            r = float(args[0])
            g = float(args[1])
            b = float(args[2])
            w = float(args[3]) if len(args) > 3 else 0.0
            self.fixture_manager.set_fixture_color(fixture_id, r, g, b, w)
            print(f"OSC: {address} -> {fixture_id} RGBW = ({r:.2f}, {g:.2f}, {b:.2f}, {w:.2f})")
    
    def _handle_dimmer(self, address: str, *args: Any):
        """Handle /fixture/<id>/dimmer <value>"""
        fixture_id = self._extract_fixture_id(address)
        if args and fixture_id:
            value = float(args[0])
            self.fixture_manager.set_fixture_dimmer(fixture_id, value)
            print(f"OSC: {address} -> {fixture_id} dimmer = {value:.2f}")
    
    def _handle_channel(self, address: str, *args: Any):
        """Handle /fixture/<id>/channel/<name> <value>"""
        fixture_id = self._extract_fixture_id(address)
        channel_name = self._extract_channel_name(address)
        if args and fixture_id and channel_name:
            value = float(args[0])
            self.fixture_manager.set_fixture_channel(fixture_id, channel_name, value)
            print(f"OSC: {address} -> {fixture_id} {channel_name} = {value:.2f}")
    
    def _handle_blackout(self, address: str, *args: Any):
        """Handle /blackout"""
        self.fixture_manager.blackout_all()
        print(f"OSC: {address} -> BLACKOUT")
    
    def _handle_info(self, address: str, *args: Any):
        """Handle /info - print available fixtures"""
        fixtures = self.fixture_manager.list_fixtures()
        print(f"OSC: {address} -> Available fixtures: {fixtures}")
    
    def _handle_default(self, address: str, *args: Any):
        """Default handler for unmatched messages"""
        print(f"OSC: Unhandled message: {address} {args}")
    
    def start(self):
        """Start OSC server in a separate thread"""
        try:
            self.server = BlockingOSCUDPServer((self.ip, self.port), self.dispatcher)
            self.server_thread = threading.Thread(target=self.server.serve_forever, daemon=True)
            self.server_thread.start()
            print(f"OSC Server: Listening on {self.ip}:{self.port}")
        except Exception as e:
            print(f"OSC Server: Failed to start: {e}")
    
    def stop(self):
        """Stop OSC server"""
        if self.server:
            self.server.shutdown()
            print("OSC Server: Stopped")

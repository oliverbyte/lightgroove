"""
Fixture Manager
Handles fixture configuration, patching and control
Author: https://github.com/oliverbyte
"""
import json
import os
from typing import Dict, Any, Optional


class FixtureManager:
    """Manages lighting fixtures, their configuration and control"""
    
    def __init__(self, dmx_controller, fixtures_file: str, patch_file: str):
        """
        Initialize fixture manager
        
        Args:
            dmx_controller: DMXController instance
            fixtures_file: Path to fixtures.json
            patch_file: Path to patch.json
        """
        self.dmx = dmx_controller
        self.fixtures_config = self._load_json(fixtures_file)
        self.patch_config = self._load_json(patch_file)
        self.fixtures = {}
        
        self._initialize_fixtures()
    
    def _load_json(self, filepath: str) -> Dict:
        """Load JSON configuration file"""
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading {filepath}: {e}")
            return {}

    def _initialize_fixtures(self):
        """Initialize all patched fixtures"""
        for universe_str, universe_data in self.patch_config.get('universes', {}).items():
            universe_id = int(universe_str)
            for fixture_data in universe_data.get('fixtures', []):
                fixture_id = fixture_data['id']
                fixture_type = fixture_data['type']
                start_address = fixture_data['start_address']
                
                if fixture_type in self.fixtures_config:
                    self.fixtures[fixture_id] = {
                        'type': fixture_type,
                        'universe': universe_id,
                        'start_address': start_address,
                        'config': self.fixtures_config[fixture_type],
                        'state': {}
                    }
                    print(f"Initialized fixture '{fixture_id}' ({fixture_type}) at Universe {universe_id}, Address {start_address}")
                else:
                    print(f"Warning: Fixture type '{fixture_type}' not found in fixtures.json")
    
    def set_fixture_channel(self, fixture_id: str, channel_name: str, value: float):
        """
        Set a specific channel of a fixture
        
        Args:
            fixture_id: ID of the fixture (e.g., 'par1')
            channel_name: Name of the channel (e.g., 'red', 'dimmer')
            value: Value 0.0-1.0 (will be scaled to 0-255)
        """
        if fixture_id not in self.fixtures:
            print(f"Fixture '{fixture_id}' not found")
            return
        
        fixture = self.fixtures[fixture_id]
        config = fixture['config']
        
        # Find channel configuration
        channel_config = None
        for ch in config['channels']:
            if ch['name'] == channel_name:
                channel_config = ch
                break
        
        if not channel_config:
            print(f"Channel '{channel_name}' not found in fixture '{fixture_id}'")
            return
        
        # Scale value from 0.0-1.0 to DMX range
        dmx_value = int(value * 255)
        dmx_value = max(0, min(255, dmx_value))
        
        # Calculate absolute DMX address
        universe_id = fixture['universe']
        dmx_address = fixture['start_address'] + channel_config['index']
        
        # Set DMX channel with universe
        self.dmx.set_channel(universe_id, dmx_address, dmx_value)
        
        # Update state
        fixture['state'][channel_name] = value
    
    def get_fixture_channel(self, fixture_id: str, channel_name: str) -> float:
        """
        Get the current value of a specific channel of a fixture
        
        Args:
            fixture_id: ID of the fixture (e.g., 'par1')
            channel_name: Name of the channel (e.g., 'red', 'dimmer')
        
        Returns:
            Current channel value 0.0-1.0, or 0.0 if not found
        """
        if fixture_id not in self.fixtures:
            return 0.0
        
        fixture = self.fixtures[fixture_id]
        return fixture['state'].get(channel_name, 0.0)
    
    def set_fixture_color(self, fixture_id: str, red: float, green: float, blue: float, white: float = 0.0):
        """
        Set RGBW color of a fixture
        
        Args:
            fixture_id: ID of the fixture
            red: Red value 0.0-1.0
            green: Green value 0.0-1.0
            blue: Blue value 0.0-1.0
            white: White value 0.0-1.0
        """
        self.set_fixture_channel(fixture_id, 'red', red)
        self.set_fixture_channel(fixture_id, 'green', green)
        self.set_fixture_channel(fixture_id, 'blue', blue)
        self.set_fixture_channel(fixture_id, 'white', white)
    
    def set_fixture_dimmer(self, fixture_id: str, intensity: float):
        """
        Set dimmer/intensity of a fixture
        
        Args:
            fixture_id: ID of the fixture
            intensity: Intensity value 0.0-1.0
        """
        self.set_fixture_channel(fixture_id, 'dimmer', intensity)
    
    def get_fixture_state(self, fixture_id: str) -> Optional[Dict]:
        """Get current state of a fixture"""
        if fixture_id in self.fixtures:
            return self.fixtures[fixture_id]['state']
        return None
    
    def list_fixtures(self) -> list:
        """Get list of all fixture IDs"""
        return list(self.fixtures.keys())
    
    def blackout_all(self):
        """Set all fixtures to blackout"""
        for fixture_id in self.fixtures:
            self.set_fixture_color(fixture_id, 0, 0, 0, 0)
            self.set_fixture_dimmer(fixture_id, 0)
    
    def reapply_all_states(self):
        """Reapply all current fixture states (useful after grandmaster change)"""
        for fixture_id, fixture_data in self.fixtures.items():
            state = fixture_data.get('state', {})
            for channel_name, value in state.items():
                self.set_fixture_channel(fixture_id, channel_name, value)


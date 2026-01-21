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
        
        # Get channel type for grandmaster handling
        channel_type = channel_config.get('type', 'other')
        
        # Set DMX channel with universe and channel type
        self.dmx.set_channel(universe_id, dmx_address, dmx_value, channel_type)
        
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
    
    def has_channel(self, fixture_id: str, channel_name: str) -> bool:
        """
        Check if a fixture has a specific channel
        
        Args:
            fixture_id: ID of the fixture
            channel_name: Name of the channel to check
            
        Returns:
            True if the fixture has the channel, False otherwise
        """
        if fixture_id not in self.fixtures:
            return False
        
        fixture = self.fixtures[fixture_id]
        config = fixture['config']
        
        for ch in config['channels']:
            if ch['name'] == channel_name:
                return True
        return False
    
    def _rgbw_to_color_wheel(self, fixture_id: str, r: float, g: float, b: float, w: float) -> float:
        """
        Convert RGBW values to color wheel position (0.0-1.0)
        Uses fixture-specific color wheel mapping from fixture definition
        
        Args:
            fixture_id: ID of the fixture
            r, g, b, w: Color values 0.0-1.0
            
        Returns normalized value (0.0-1.0) for color wheel channel
        """
        if fixture_id not in self.fixtures:
            return 0.0
        
        fixture = self.fixtures[fixture_id]
        config = fixture['config']
        
        # Get color wheel mapping from fixture config
        color_wheel_mapping = config.get('color_wheel_mapping', {})
        if not color_wheel_mapping:
            return 0.0
        
        # Tolerance for color matching
        tolerance = 0.2
        
        # Helper function to get DMX value from mapping
        def get_dmx(color_name):
            return color_wheel_mapping.get(color_name, 0) / 255.0
        
        # White (w channel or RGB all high)
        if w > 0.5 or (r > 0.8 and g > 0.8 and b > 0.8):
            return get_dmx('white')
        
        # Check two-color combinations BEFORE pure colors to avoid ambiguity
        
        # Yellow (R+G, no B)
        if r > 0.8 and g > 0.8 and b < tolerance:
            return get_dmx('yellow')
        
        # Cyan (G+B, no R)
        if r < tolerance and g > 0.8 and b > 0.8:
            return get_dmx('cyan')
        
        # Magenta/Pink (R+B, no G)
        if r > 0.8 and g < tolerance and b > 0.8:
            return get_dmx('magenta')
        
        # Orange (R high, G medium, no B)
        if r > 0.8 and g > 0.3 and g < 0.7 and b < tolerance:
            return get_dmx('orange')
        
        # Now check pure colors
        
        # Pure Red
        if r > 0.8 and g < tolerance and b < tolerance:
            return get_dmx('red')
        
        # Pure Green
        if r < tolerance and g > 0.8 and b < tolerance:
            return get_dmx('green')
        
        # Pure Blue
        if r < tolerance and g < tolerance and b > 0.8:
            return get_dmx('blue')
        
        # Purple (R medium, B high, G low) - closest to magenta
        if r > 0.4 and b > 0.8 and g < 0.5:
            return get_dmx('magenta')
        
        # Black or unknown - default to white
        return get_dmx('white')
    
    def set_fixture_color(self, fixture_id: str, red: float, green: float, blue: float, white: float = 0.0):
        """
        Set RGBW color of a fixture (only if it has RGBW channels)
        For fixtures with color wheel, converts RGBW to closest wheel position
        
        Args:
            fixture_id: ID of the fixture
            red: Red value 0.0-1.0
            green: Green value 0.0-1.0
            blue: Blue value 0.0-1.0
            white: White value 0.0-1.0
        """
        # Check if this is black (all channels off)
        is_black = (red < 0.01 and green < 0.01 and blue < 0.01 and white < 0.01)
        
        # Check if fixture has color wheel instead of RGBW
        if self.has_channel(fixture_id, 'color_wheel'):
            fixture = self.fixtures.get(fixture_id)
            if fixture:
                config = fixture.get('config', {})
                dimmer_on_black = config.get('dimmer_on_black', False)
                
                if dimmer_on_black:
                    if is_black:
                        # Save current dimmer value before turning off
                        current_dimmer = self._get_fixture_dimmer(fixture_id)
                        if current_dimmer > 0:
                            fixture['saved_dimmer'] = current_dimmer
                        # Turn off dimmer for black
                        self.set_fixture_dimmer(fixture_id, 0.0)
                    else:
                        # Set color wheel position for non-black colors
                        wheel_value = self._rgbw_to_color_wheel(fixture_id, red, green, blue, white)
                        self.set_fixture_channel(fixture_id, 'color_wheel', wheel_value)
                        # Restore saved dimmer value if it was turned off by black
                        current_dimmer = self._get_fixture_dimmer(fixture_id)
                        if current_dimmer < 0.01 and 'saved_dimmer' in fixture:
                            # Dimmer is off and we have a saved value - restore it
                            self.set_fixture_dimmer(fixture_id, fixture['saved_dimmer'])
                else:
                    # Just set color wheel without affecting dimmer
                    wheel_value = self._rgbw_to_color_wheel(fixture_id, red, green, blue, white)
                    self.set_fixture_channel(fixture_id, 'color_wheel', wheel_value)
            return
        
        # Only set channels that exist on this fixture (standard RGBW)
        if self.has_channel(fixture_id, 'red'):
            self.set_fixture_channel(fixture_id, 'red', red)
        if self.has_channel(fixture_id, 'green'):
            self.set_fixture_channel(fixture_id, 'green', green)
        if self.has_channel(fixture_id, 'blue'):
            self.set_fixture_channel(fixture_id, 'blue', blue)
        if self.has_channel(fixture_id, 'white'):
            self.set_fixture_channel(fixture_id, 'white', white)
    
    def _get_fixture_dimmer(self, fixture_id: str) -> float:
        """
        Get current dimmer/intensity value of a fixture
        Tries common dimmer channel names: master_dimmer, dimmer, intensity
        
        Args:
            fixture_id: ID of the fixture
            
        Returns:
            Current dimmer value 0.0-1.0, or 1.0 if not found
        """
        dimmer_channels = ['master_dimmer', 'dimmer', 'intensity']
        for channel_name in dimmer_channels:
            if self.has_channel(fixture_id, channel_name):
                return self.get_fixture_channel(fixture_id, channel_name)
        return 1.0  # Default to full if no dimmer channel
    
    def set_fixture_dimmer(self, fixture_id: str, intensity: float):
        """
        Set dimmer/intensity of a fixture
        Tries common dimmer channel names: master_dimmer, dimmer, intensity
        
        Args:
            fixture_id: ID of the fixture
            intensity: Intensity value 0.0-1.0
        """
        # Try common dimmer channel names
        dimmer_channels = ['master_dimmer', 'dimmer', 'intensity']
        for channel_name in dimmer_channels:
            if self.has_channel(fixture_id, channel_name):
                self.set_fixture_channel(fixture_id, channel_name, intensity)
                return
        # If no dimmer channel found, silently ignore (some fixtures may not have dimmer)
    
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
    
    def flash_all_white(self):
        """Set all fixtures to full white for flash effect"""
        for fixture_id in self.fixtures:
            # Use set_fixture_color to handle both RGBW and color wheel fixtures
            # Full white: w=1.0, r=g=b=0
            self.set_fixture_color(fixture_id, 0.0, 0.0, 0.0, 1.0)
            # Set dimmer to full (try common dimmer channel names)
            self.set_fixture_dimmer(fixture_id, 1.0)
    
    def save_current_states(self) -> Dict[str, Dict[str, float]]:
        """Save current states of all fixtures for later restoration"""
        saved_states = {}
        for fixture_id, fixture_data in self.fixtures.items():
            saved_states[fixture_id] = fixture_data.get('state', {}).copy()
        return saved_states
    
    def restore_states(self, saved_states: Dict[str, Dict[str, float]]):
        """Restore previously saved fixture states"""
        for fixture_id, state in saved_states.items():
            if fixture_id in self.fixtures:
                for channel_name, value in state.items():
                    self.set_fixture_channel(fixture_id, channel_name, value)


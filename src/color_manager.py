"""
Color definitions and color FX engine for LightGroove.
"""
import threading
import time
import random
import json
import os
from typing import Dict, List, Optional


def load_colors() -> Dict:
    """Load color definitions from config/colors.json"""
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'colors.json')
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
            return config.get('colors', {})
    except Exception as e:
        print(f"Warning: Could not load colors from config: {e}")
        # Fallback to default colors if config fails to load
        return {
            'red': {'r': 1.0, 'g': 0.0, 'b': 0.0, 'w': 0.0},
            'green': {'r': 0.0, 'g': 1.0, 'b': 0.0, 'w': 0.0},
            'blue': {'r': 0.0, 'g': 0.0, 'b': 1.0, 'w': 0.0},
            'white': {'r': 0.0, 'g': 0.0, 'b': 0.0, 'w': 1.0}
        }


# Static color definitions (normalized 0.0-1.0 values)
COLORS = load_colors()


class ColorFXEngine:
    """
    Manages color effects that run server-side independently of UI.
    """
    
    def __init__(self, fixture_manager):
        self.fixture_manager = fixture_manager
        self.bpm = 120  # Default 120 BPM
        self.fade_percentage = 0.0  # Fade time as percentage of beat interval (0.0-1.0)
        self.running = False
        self.current_fx = None
        self.current_color = None  # Track currently displayed color
        self.fx_thread = None
        self.stop_event = threading.Event()
        
    def set_bpm(self, bpm: int):
        """Set FX speed in beats per minute (1-480 range)."""
        self.bpm = max(1, min(480, bpm))
        print(f"Color FX: BPM set to {self.bpm}")
    
    def set_fade_percentage(self, percentage: float):
        """Set fade time as percentage of beat interval (0.0-1.0 range)."""
        self.fade_percentage = max(0.0, min(1.0, percentage))
        actual_time = self.fade_percentage * self.get_interval()
        print(f"Color FX: Fade set to {self.fade_percentage*100:.0f}% ({actual_time:.3f}s at {self.bpm} BPM)")
        
    def get_interval(self) -> float:
        """Calculate interval in seconds based on BPM."""
        return 60.0 / self.bpm
    
    def _apply_color_instant(self, fixture_id: str, color_values: dict, channel_map: dict):
        """Apply color to fixture instantly."""
        for short_key, target_value in color_values.items():
            channel_name = channel_map.get(short_key, short_key)
            try:
                self.fixture_manager.set_fixture_channel(fixture_id, channel_name, target_value)
            except:
                pass
    
    def _apply_colors_with_fade(self, fixture_colors: dict, channel_map: dict) -> float:
        """Apply colors to multiple fixtures simultaneously with fade.
        
        Args:
            fixture_colors: Dict mapping fixture_id to color_values dict
            channel_map: Dict mapping short keys to channel names
            
        Returns:
            Actual fade time used in seconds
        """
        if self.fade_percentage <= 0:
            # Instant color change for all fixtures
            for fixture_id, color_values in fixture_colors.items():
                self._apply_color_instant(fixture_id, color_values, channel_map)
            return 0.0
        else:
            # Smooth fade - calculate actual time from percentage of beat interval
            actual_fade_time = self.fade_percentage * self.get_interval()
            steps = max(10, int(actual_fade_time * 20))  # 20 steps per second
            step_time = actual_fade_time / steps
            
            # Get current values for all fixtures
            fixture_current_values = {}
            for fixture_id, color_values in fixture_colors.items():
                current_values = {}
                for short_key in color_values.keys():
                    channel_name = channel_map.get(short_key, short_key)
                    try:
                        current_values[short_key] = self.fixture_manager.get_fixture_channel(fixture_id, channel_name)
                    except:
                        current_values[short_key] = 0.0
                fixture_current_values[fixture_id] = current_values
            
            # Fade through steps for all fixtures simultaneously
            for step in range(1, steps + 1):
                if not self.running:
                    break
                progress = step / steps
                for fixture_id, color_values in fixture_colors.items():
                    current_values = fixture_current_values[fixture_id]
                    for short_key, target_value in color_values.items():
                        channel_name = channel_map.get(short_key, short_key)
                        current = current_values.get(short_key, 0.0)
                        value = current + (target_value - current) * progress
                        try:
                            self.fixture_manager.set_fixture_channel(fixture_id, channel_name, value)
                        except:
                            pass
                time.sleep(step_time)
            
            return actual_fade_time
        
    def start_fx(self, fx_name: str):
        """Start a color effect by name."""
        if self.running:
            self.stop_fx()
            
        self.current_fx = fx_name
        self.running = True
        self.stop_event.clear()
        
        if fx_name == 'random' or fx_name == 'random_1':
            self.fx_thread = threading.Thread(target=self._run_random_fx, daemon=True)
            self.fx_thread.start()
            print(f"Color FX: Started 'random_1' effect at {self.bpm} BPM")
        elif fx_name == 'random_2':
            self.fx_thread = threading.Thread(target=self._run_random_2_fx, daemon=True)
            self.fx_thread.start()
            print(f"Color FX: Started 'random_2' effect at {self.bpm} BPM")
        elif fx_name == 'random_3':
            self.fx_thread = threading.Thread(target=self._run_random_3_fx, daemon=True)
            self.fx_thread.start()
            print(f"Color FX: Started 'random_3' effect at {self.bpm} BPM")
        else:
            print(f"Color FX: Unknown effect '{fx_name}'")
            self.running = False
            
    def stop_fx(self):
        """Stop the currently running effect."""
        if self.running:
            print(f"Color FX: Stopping '{self.current_fx}' effect")
            self.running = False
            self.stop_event.set()
            if self.fx_thread and self.fx_thread.is_alive():
                self.fx_thread.join(timeout=2.0)
            self.current_fx = None
            # Keep current_color to preserve highlighted state
            
    def _run_random_fx(self):
        """Random color cycling effect - all fixtures same color."""
        # Exclude 'black' from random color selection
        color_names = [c for c in COLORS.keys() if c != 'black']
        # Map short keys to actual fixture channel names
        channel_map = {'r': 'red', 'g': 'green', 'b': 'blue', 'w': 'white'}
        
        while self.running:
            # Pick random color (avoid repeating the same color)
            available_colors = [c for c in color_names if c != self.current_color]
            if not available_colors:  # Fallback if only one color defined
                available_colors = color_names
            color_name = random.choice(available_colors)
            self.current_color = color_name  # Track current color
            color_values = COLORS[color_name]
            
            # Apply to all fixtures simultaneously with fade
            fixtures = self.fixture_manager.list_fixtures()
            fixture_colors = {fixture_id: color_values for fixture_id in fixtures}
            fade_time_used = self._apply_colors_with_fade(fixture_colors, channel_map)
                        
            # Wait for remaining time in beat (beat_interval - fade_time)
            remaining_time = max(0.0, self.get_interval() - fade_time_used)
            if self.stop_event.wait(remaining_time):
                break
    
    def _run_random_2_fx(self):
        """Random color cycling effect - each fixture gets different color."""
        # Exclude 'black' from random color selection
        color_names = [c for c in COLORS.keys() if c != 'black']
        # Map short keys to actual fixture channel names
        channel_map = {'r': 'red', 'g': 'green', 'b': 'blue', 'w': 'white'}
        fixture_last_colors = {}  # Track last color per fixture
        
        while self.running:
            fixtures = self.fixture_manager.list_fixtures()
            
            # Pick different random color for each fixture
            fixture_colors = {}
            for fixture_id in fixtures:
                # Pick random color for this fixture (avoid repeating)
                last_color = fixture_last_colors.get(fixture_id)
                available_colors = [c for c in color_names if c != last_color]
                if not available_colors:
                    available_colors = color_names
                color_name = random.choice(available_colors)
                fixture_last_colors[fixture_id] = color_name
                fixture_colors[fixture_id] = COLORS[color_name]
            
            # Apply all fixtures simultaneously with fade
            fade_time_used = self._apply_colors_with_fade(fixture_colors, channel_map)
            
            # Track first fixture's color for UI display
            if fixtures:
                self.current_color = fixture_last_colors.get(fixtures[0])
                        
            # Wait for remaining time in beat (beat_interval - fade_time)
            remaining_time = max(0.0, self.get_interval() - fade_time_used)
            if self.stop_event.wait(remaining_time):
                break
    
    def _run_random_3_fx(self):
        """Random color cycling effect - alternates between even/odd patches."""
        # Exclude 'black' from random color selection
        color_names = [c for c in COLORS.keys() if c != 'black']
        black_values = COLORS['black']
        # Map short keys to actual fixture channel names
        channel_map = {'r': 'red', 'g': 'green', 'b': 'blue', 'w': 'white'}
        last_color = None
        even_turn = True  # Start with even patches lit
        
        while self.running:
            fixtures = self.fixture_manager.list_fixtures()
            
            # Pick random color (avoid repeating)
            available_colors = [c for c in color_names if c != last_color]
            if not available_colors:
                available_colors = color_names
            color_name = random.choice(available_colors)
            last_color = color_name
            color_values = COLORS[color_name]
            
            # Alternate between even and odd patches
            fixture_colors = {}
            for idx, fixture_id in enumerate(fixtures):
                is_even = (idx % 2 == 0)
                if (even_turn and is_even) or (not even_turn and not is_even):
                    fixture_colors[fixture_id] = color_values
                else:
                    fixture_colors[fixture_id] = black_values
            
            # Apply all fixtures simultaneously with fade
            fade_time_used = self._apply_colors_with_fade(fixture_colors, channel_map)
            
            # Track current color for UI display
            self.current_color = color_name
            
            # Toggle for next beat
            even_turn = not even_turn
                        
            # Wait for remaining time in beat (beat_interval - fade_time)
            remaining_time = max(0.0, self.get_interval() - fade_time_used)
            if self.stop_event.wait(remaining_time):
                break
                
    def is_running(self) -> bool:
        """Check if an effect is currently running."""
        return self.running
        
    def get_status(self) -> Dict:
        """Get current FX status."""
        return {
            'running': self.running,
            'current_fx': self.current_fx,
            'current_color': self.current_color,
            'bpm': self.bpm,
            'fade_percentage': self.fade_percentage
        }

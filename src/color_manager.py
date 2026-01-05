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
        self.fade_time = 0.0  # Fade time in seconds (0 = instant)
        self.running = False
        self.current_fx = None
        self.current_color = None  # Track currently displayed color
        self.fx_thread = None
        self.stop_event = threading.Event()
        
    def set_bpm(self, bpm: int):
        """Set FX speed in beats per minute (1-480 range)."""
        self.bpm = max(1, min(480, bpm))
        # Cap fade time to new beat interval if needed
        max_fade = self.get_interval()
        if self.fade_time > max_fade:
            self.fade_time = max_fade
            print(f"Color FX: Fade time auto-adjusted to {self.fade_time:.3f}s (beat interval)")
        print(f"Color FX: BPM set to {self.bpm}")
    
    def set_fade_time(self, fade_time: float):
        """Set fade time in seconds (0-10 range)."""
        self.fade_time = max(0.0, min(10.0, fade_time))
        print(f"Color FX: Fade time set to {self.fade_time}s")
        
    def get_interval(self) -> float:
        """Calculate interval in seconds based on BPM."""
        return 60.0 / self.bpm
    
    def _apply_color_with_fade(self, fixture_id: str, color_values: dict, channel_map: dict):
        """Apply color to fixture with optional fade."""
        if self.fade_time <= 0:
            # Instant color change
            for short_key, target_value in color_values.items():
                channel_name = channel_map.get(short_key, short_key)
                try:
                    self.fixture_manager.set_fixture_channel(fixture_id, channel_name, target_value)
                except:
                    pass
        else:
            # Smooth fade - cap fade time to beat interval
            actual_fade_time = min(self.fade_time, self.get_interval())
            steps = max(10, int(actual_fade_time * 20))  # 20 steps per second
            step_time = actual_fade_time / steps
            
            # Get current values
            current_values = {}
            for short_key in color_values.keys():
                channel_name = channel_map.get(short_key, short_key)
                try:
                    current_values[short_key] = self.fixture_manager.get_fixture_channel(fixture_id, channel_name)
                except:
                    current_values[short_key] = 0.0
            
            # Fade through steps
            for step in range(1, steps + 1):
                if not self.running:
                    break
                progress = step / steps
                for short_key, target_value in color_values.items():
                    channel_name = channel_map.get(short_key, short_key)
                    current = current_values.get(short_key, 0.0)
                    value = current + (target_value - current) * progress
                    try:
                        self.fixture_manager.set_fixture_channel(fixture_id, channel_name, value)
                    except:
                        pass
                time.sleep(step_time)
        
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
        color_names = list(COLORS.keys())
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
            
            # Apply to all fixtures with fade
            fixtures = self.fixture_manager.list_fixtures()
            for fixture_id in fixtures:
                self._apply_color_with_fade(fixture_id, color_values, channel_map)
                        
            # Wait for next beat
            if self.stop_event.wait(self.get_interval()):
                break
    
    def _run_random_2_fx(self):
        """Random color cycling effect - each fixture gets different color."""
        color_names = list(COLORS.keys())
        # Map short keys to actual fixture channel names
        channel_map = {'r': 'red', 'g': 'green', 'b': 'blue', 'w': 'white'}
        fixture_last_colors = {}  # Track last color per fixture
        
        while self.running:
            fixtures = self.fixture_manager.list_fixtures()
            
            # Apply different random color to each fixture
            for fixture_id in fixtures:
                # Pick random color for this fixture (avoid repeating)
                last_color = fixture_last_colors.get(fixture_id)
                available_colors = [c for c in color_names if c != last_color]
                if not available_colors:
                    available_colors = color_names
                color_name = random.choice(available_colors)
                fixture_last_colors[fixture_id] = color_name
                
                color_values = COLORS[color_name]
                self._apply_color_with_fade(fixture_id, color_values, channel_map)
            
            # Track first fixture's color for UI display
            if fixtures:
                self.current_color = fixture_last_colors.get(fixtures[0])
                        
            # Wait for next beat
            if self.stop_event.wait(self.get_interval()):
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
            'fade_time': self.fade_time
        }

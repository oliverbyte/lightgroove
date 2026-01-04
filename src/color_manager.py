"""
Color definitions and color FX engine for LightGroove.
"""
import threading
import time
import random
from typing import Dict, List, Optional


# Static color definitions (normalized 0.0-1.0 values)
COLORS = {
    'red': {'r': 1.0, 'g': 0.0, 'b': 0.0, 'w': 0.0},
    'green': {'r': 0.0, 'g': 1.0, 'b': 0.0, 'w': 0.0},
    'blue': {'r': 0.0, 'g': 0.0, 'b': 1.0, 'w': 0.0},
    'cyan': {'r': 0.0, 'g': 1.0, 'b': 1.0, 'w': 0.0},
    'magenta': {'r': 1.0, 'g': 0.0, 'b': 1.0, 'w': 0.0},
    'yellow': {'r': 1.0, 'g': 1.0, 'b': 0.0, 'w': 0.0},
    'white': {'r': 0.0, 'g': 0.0, 'b': 0.0, 'w': 1.0},
    'orange': {'r': 1.0, 'g': 0.5, 'b': 0.0, 'w': 0.0},
    'purple': {'r': 0.65, 'g': 0.3, 'b': 1.0, 'w': 0.0}
}


class ColorFXEngine:
    """
    Manages color effects that run server-side independently of UI.
    """
    
    def __init__(self, fixture_manager):
        self.fixture_manager = fixture_manager
        self.bpm = 120  # Default 120 BPM
        self.running = False
        self.current_fx = None
        self.fx_thread = None
        self.stop_event = threading.Event()
        
    def set_bpm(self, bpm: int):
        """Set FX speed in beats per minute (30-240 range)."""
        self.bpm = max(30, min(240, bpm))
        print(f"Color FX: BPM set to {self.bpm}")
        
    def get_interval(self) -> float:
        """Calculate interval in seconds based on BPM."""
        return 60.0 / self.bpm
        
    def start_fx(self, fx_name: str):
        """Start a color effect by name."""
        if self.running:
            self.stop_fx()
            
        self.current_fx = fx_name
        self.running = True
        self.stop_event.clear()
        
        if fx_name == 'random':
            self.fx_thread = threading.Thread(target=self._run_random_fx, daemon=True)
            self.fx_thread.start()
            print(f"Color FX: Started 'random' effect at {self.bpm} BPM")
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
            
    def _run_random_fx(self):
        """Random color cycling effect."""
        color_names = list(COLORS.keys())
        
        while self.running:
            # Pick random color
            color_name = random.choice(color_names)
            color_values = COLORS[color_name]
            
            # Apply to all fixtures
            fixtures = self.fixture_manager.list_fixtures()
            for fixture_id in fixtures:
                for channel, value in color_values.items():
                    try:
                        self.fixture_manager.set_fixture_channel(fixture_id, channel, value)
                    except:
                        pass  # Ignore fixtures without this channel
                        
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
            'bpm': self.bpm
        }

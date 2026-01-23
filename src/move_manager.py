"""
Move FX engine for LightGroove.
Professional movement effect engine for fixtures with pan/tilt channels.
Based on patterns from QLC+ and professional lighting control systems.
"""
import threading
import time
import math
from typing import Dict, List, Optional


class MoveFXEngine:
    """
    Manages movement effects for fixtures with pan/tilt channels.
    
    Implements professional movement patterns including:
    - Oscillation effects (pan sway, tilt sway)
    - Geometric patterns (circle, figure-8)
    - Lissajous curves (complex mathematical patterns)
    
    Features:
    - BPM-based speed control
    - Continuous smooth motion without restart jumps
    - Real-time position adaptation
    - Multi-fixture support
    """
    
    def __init__(self, fixture_manager):
        self.fixture_manager = fixture_manager
        self.bpm = 20  # Default 20 BPM
        self.running = False
        self.current_fx = None
        self.fx_thread = None
        self.stop_event = threading.Event()
        
        # Effect center position (X/Y pad controls)
        self.center_pan = 0.5  # Pan center (0.0-1.0)
        self.center_tilt = 0.5  # Tilt center (0.0-1.0)
        
        # Effect size/amplitude control
        self.fx_size = 0.3  # Size (0.0-1.0) defines min-max range from center
        
    def set_bpm(self, bpm: int):
        """Set FX speed in beats per minute (1-480 range)."""
        self.bpm = max(1, min(480, bpm))
        print(f"Move FX: BPM set to {self.bpm}")
    
    def set_center(self, pan: float, tilt: float):
        """Set the center position for effects (X/Y pad control)."""
        self.center_pan = max(0.0, min(1.0, pan))
        self.center_tilt = max(0.0, min(1.0, tilt))
        print(f"Move FX: Center set to pan={self.center_pan:.2f}, tilt={self.center_tilt:.2f}")
    
    def set_fx_size(self, size: float):
        """Set the effect size/amplitude (0.0-1.0)."""
        self.fx_size = max(0.0, min(1.0, size))
        print(f"Move FX: Size set to {self.fx_size:.2f}")
    
    def get_interval(self) -> float:
        """Calculate interval in seconds based on BPM."""
        return 60.0 / self.bpm
    
    def get_moving_fixtures(self) -> List[str]:
        """Get list of fixture IDs that have pan and tilt channels."""
        return [fid for fid in self.fixture_manager.list_fixtures() 
                if self.fixture_manager.has_pan_tilt(fid)]
    
    def _set_pan_tilt(self, fixture_id: str, pan: float, tilt: float):
        """
        Set pan and tilt for a fixture (0.0-1.0 range).
        
        Args:
            fixture_id: Fixture ID
            pan: Pan value 0.0-1.0
            tilt: Tilt value 0.0-1.0
        """
        # Clamp values
        pan = max(0.0, min(1.0, pan))
        tilt = max(0.0, min(1.0, tilt))
        
        self.fixture_manager.set_fixture_channel(fixture_id, 'pan', pan)
        self.fixture_manager.set_fixture_channel(fixture_id, 'tilt', tilt)
        
        # Also set fine channels if available
        if self.fixture_manager.has_channel(fixture_id, 'pan_fine'):
            self.fixture_manager.set_fixture_channel(fixture_id, 'pan_fine', 0.0)
        if self.fixture_manager.has_channel(fixture_id, 'tilt_fine'):
            self.fixture_manager.set_fixture_channel(fixture_id, 'tilt_fine', 0.0)
    
    def start_fx(self, fx_name: str):
        """Start a movement effect by name."""
        if self.running:
            self.stop_fx()
            
        self.current_fx = fx_name
        self.running = True
        self.stop_event.clear()
        
        moving_fixtures = self.get_moving_fixtures()
        if not moving_fixtures:
            print("Move FX: No fixtures with pan/tilt found")
            self.running = False
            return
        
        if fx_name == 'pan_sway':
            self.fx_thread = threading.Thread(target=self._run_pan_sway, daemon=True)
            self.fx_thread.start()
            print(f"Move FX: Started 'pan_sway' effect at {self.bpm} BPM")
        elif fx_name == 'tilt_sway':
            self.fx_thread = threading.Thread(target=self._run_tilt_sway, daemon=True)
            self.fx_thread.start()
            print(f"Move FX: Started 'tilt_sway' effect at {self.bpm} BPM")
        elif fx_name == 'circle':
            self.fx_thread = threading.Thread(target=self._run_circle, daemon=True)
            self.fx_thread.start()
            print(f"Move FX: Started 'circle' effect at {self.bpm} BPM")
        elif fx_name == 'eight':
            self.fx_thread = threading.Thread(target=self._run_eight, daemon=True)
            self.fx_thread.start()
            print(f"Move FX: Started 'eight' (figure-8) effect at {self.bpm} BPM")
        elif fx_name == 'lissajous':
            self.fx_thread = threading.Thread(target=self._run_lissajous, daemon=True)
            self.fx_thread.start()
            print(f"Move FX: Started 'lissajous' effect at {self.bpm} BPM")
        elif fx_name == 'diamond':
            self.fx_thread = threading.Thread(target=self._run_diamond, daemon=True)
            self.fx_thread.start()
            print(f"Move FX: Started 'diamond' effect at {self.bpm} BPM")
        elif fx_name == 'off':
            self.stop_fx()
            # Return all to front/center position
            self.fixture_manager.set_all_moving_positions('front')
        else:
            print(f"Move FX: Unknown effect '{fx_name}'")
            self.running = False
            
    def stop_fx(self):
        """Stop the currently running effect."""
        if self.running:
            print(f"Move FX: Stopping '{self.current_fx}' effect")
            self.running = False
            self.stop_event.set()
            if self.fx_thread and self.fx_thread.is_alive():
                self.fx_thread.join(timeout=2.0)
            self.current_fx = None
    
    def _run_pan_sway(self):
        """Pan sway effect - smooth left-right movement."""
        fixtures = self.get_moving_fixtures()
        steps_per_cycle = 60  # Smooth motion
        
        while self.running:
            interval = self.get_interval()
            step_time = interval / steps_per_cycle
            
            for step in range(steps_per_cycle):
                if not self.running:
                    break
                
                # Sine wave for smooth oscillation around center position
                progress = step / steps_per_cycle
                pan_value = self.center_pan + self.fx_size * math.sin(progress * 2 * math.pi)
                
                for fixture_id in fixtures:
                    # Read current tilt position for each fixture on each iteration
                    current_tilt = self.fixture_manager.get_fixture_channel(fixture_id, 'tilt')
                    tilt_value = current_tilt if current_tilt else 0.5
                    self._set_pan_tilt(fixture_id, pan_value, tilt_value)
                
                time.sleep(step_time)
    
    def _run_tilt_sway(self):
        """Tilt sway effect - smooth up-down movement."""
        fixtures = self.get_moving_fixtures()
        steps_per_cycle = 60
        
        while self.running:
            interval = self.get_interval()
            step_time = interval / steps_per_cycle
            
            for step in range(steps_per_cycle):
                if not self.running:
                    break
                
                # Sine wave for smooth oscillation around center position
                progress = step / steps_per_cycle
                tilt_value = self.center_tilt + self.fx_size * 0.7 * math.sin(progress * 2 * math.pi)
                
                for fixture_id in fixtures:
                    # Read current pan position for each fixture on each iteration
                    current_pan = self.fixture_manager.get_fixture_channel(fixture_id, 'pan')
                    pan_value = current_pan if current_pan else 0.5
                    self._set_pan_tilt(fixture_id, pan_value, tilt_value)
                
                time.sleep(step_time)
    
    def _run_circle(self):
        """Circle effect - smooth continuous circular movement."""
        fixtures = self.get_moving_fixtures()
        steps_per_cycle = 80  # Smooth circular motion
        
        angle = 0  # Start angle
        while self.running:
            interval = self.get_interval()
            step_time = interval / steps_per_cycle
            angle_increment = (2 * math.pi) / steps_per_cycle
            
            for step in range(steps_per_cycle):
                if not self.running:
                    break
                
                # Circle with size as radius, centered at user-defined position
                # Use continuously incrementing angle for smooth motion
                pan_value = self.center_pan + self.fx_size * math.cos(angle)
                tilt_value = self.center_tilt + self.fx_size * math.sin(angle)
                
                for fixture_id in fixtures:
                    self._set_pan_tilt(fixture_id, pan_value, tilt_value)
                
                angle += angle_increment
                time.sleep(step_time)
    
    def _run_eight(self):
        """Figure-8 effect - lemniscate of Bernoulli pattern."""
        fixtures = self.get_moving_fixtures()
        steps_per_cycle = 100  # Need more steps for complex path
        
        while self.running:
            interval = self.get_interval() * 2  # One full figure-8 takes 2 beats
            step_time = interval / steps_per_cycle
            
            for step in range(steps_per_cycle):
                if not self.running:
                    break
                
                # Parametric equations for figure-8 (lemniscate)
                progress = step / steps_per_cycle
                t = progress * 2 * math.pi
                
                # Lemniscate formula with user-controlled size and center
                denominator = 1 + math.sin(t) ** 2
                pan_value = self.center_pan + self.fx_size * math.cos(t) / denominator
                tilt_value = self.center_tilt + self.fx_size * math.sin(t) * math.cos(t) / denominator
                
                for fixture_id in fixtures:
                    self._set_pan_tilt(fixture_id, pan_value, tilt_value)
                
                time.sleep(step_time)
    
    def _run_lissajous(self, freq_x=3, freq_y=2, phase_x=0, phase_y=math.pi/2):
        """
        Lissajous curve effect - complex mathematical patterns.
        
        Args:
            freq_x: Frequency multiplier for pan (X-axis)
            freq_y: Frequency multiplier for tilt (Y-axis)
            phase_x: Phase offset for pan in radians
            phase_y: Phase offset for tilt in radians
        
        Common patterns:
        - freq_x=3, freq_y=2: Classic 3:2 Lissajous
        - freq_x=5, freq_y=4: More complex pattern
        - phase_y=π/2: Creates perpendicular motion
        """
        fixtures = self.get_moving_fixtures()
        steps_per_cycle = 100
        angle = 0
        
        while self.running:
            interval = self.get_interval()
            step_time = interval / steps_per_cycle
            angle_increment = (2 * math.pi) / steps_per_cycle
            
            for step in range(steps_per_cycle):
                if not self.running:
                    break
                
                # Lissajous parametric equations with user-controlled center and size
                pan_value = self.center_pan + self.fx_size * math.sin(freq_x * angle + phase_x)
                tilt_value = self.center_tilt + self.fx_size * math.sin(freq_y * angle + phase_y)
                
                for fixture_id in fixtures:
                    self._set_pan_tilt(fixture_id, pan_value, tilt_value)
                
                angle += angle_increment
                time.sleep(step_time)
    
    def _run_diamond(self):
        """
        Diamond effect - square rotated 45 degrees with sharp corners.
        Uses power functions for sharp corner transitions.
        """
        fixtures = self.get_moving_fixtures()
        steps_per_cycle = 100
        angle = 0
        
        while self.running:
            interval = self.get_interval()
            step_time = interval / steps_per_cycle
            angle_increment = (2 * math.pi) / steps_per_cycle
            
            for step in range(steps_per_cycle):
                if not self.running:
                    break
                
                # Use cubic power for sharper corners
                raw_pan = math.cos(angle)
                raw_tilt = math.sin(angle)
                
                # Apply power function for sharpness with user-controlled center and size
                pan_value = self.center_pan + self.fx_size * (raw_pan ** 3)
                tilt_value = self.center_tilt + self.fx_size * (raw_tilt ** 3)
                
                for fixture_id in fixtures:
                    self._set_pan_tilt(fixture_id, pan_value, tilt_value)
                
                angle += angle_increment
                time.sleep(step_time)
    
    def get_status(self) -> Dict:
        """Get current FX engine status."""
        return {
            'running': self.running,
            'current_fx': self.current_fx,
            'bpm': self.bpm,
            'moving_fixtures': self.get_moving_fixtures()
        }

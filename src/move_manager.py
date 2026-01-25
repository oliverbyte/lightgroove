"""
Move FX engine for LightGroove.
Professional movement effect engine for fixtures with pan/tilt channels.
Based on patterns from QLC+ and professional lighting control systems.
"""
import threading
import time
import math
import json
import os
from pathlib import Path
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
    
    def __init__(self, fixture_manager, state_file: str = None):
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
        
        # Phase control - spreads effect across fixtures
        self.move_phase = 0.0  # Phase offset (0.0-1.0) for multi-fixture effects
        
        # Move speed multiplier - affects BPM for move effects
        # At 1.0 (50% fader): no effect on BPM
        # 0.0-1.0 (0-50% fader): divides BPM (slower)
        # 1.0-2.0 (50-100% fader): multiplies BPM (faster)
        self.move_speed_multiplier = 1.0
        
        # State persistence
        if state_file is None:
            state_file = os.path.join(os.path.dirname(__file__), '..', 'config', 'move_state.json')
        self.state_file = Path(state_file)
        self.last_save_time = 0
        self.save_interval = 15  # Auto-save every 15 seconds
        self.save_lock = threading.RLock()  # Reentrant lock to allow nested calls
        
        # Auto-save thread
        self.autosave_running = True
        self.autosave_thread = threading.Thread(target=self._autosave_loop, daemon=True)
        self.autosave_thread.start()
        
        # Load saved state
        self._load_state()
        
    def set_bpm(self, bpm: int):
        """Set FX speed in beats per minute (1-480 range)."""
        self.bpm = max(1, min(480, bpm))
        print(f"Move FX: BPM set to {self.bpm}")
        self._save_state()
    
    def set_center(self, pan: float, tilt: float):
        """Set the center position for effects (X/Y pad control)."""
        self.center_pan = max(0.0, min(1.0, pan))
        self.center_tilt = max(0.0, min(1.0, tilt))
        print(f"Move FX: Center set to pan={self.center_pan:.2f}, tilt={self.center_tilt:.2f}")
        
        # Apply position to fixtures even if no effect is running
        if not self.running:
            for fixture_id in self.get_moving_fixtures():
                self._set_pan_tilt(fixture_id, self.center_pan, self.center_tilt)
        
        # Trigger save
        self._save_state()
    
    def set_fx_size(self, size: float):
        """Set the effect size/amplitude (0.0-1.0)."""
        self.fx_size = max(0.0, min(1.0, size))
        print(f"Move FX: Size set to {self.fx_size:.2f}")
        self._save_state()
    
    def set_move_phase(self, phase: float):
        """Set the phase offset for multi-fixture effects (0.0-1.0)."""
        self.move_phase = max(0.0, min(1.0, phase))
        print(f"Move FX: Phase set to {self.move_phase:.2f}")
        self._save_state()
    
    def set_move_speed(self, multiplier: float):
        """Set the move speed multiplier (0.0-2.0).
        
        At 1.0 (50% fader): no effect on BPM
        0.0-1.0 (0-50% fader): divides BPM (slower)
        1.0-2.0 (50-100% fader): multiplies BPM (faster)
        """
        self.move_speed_multiplier = max(0.0, min(2.0, multiplier))
        print(f"Move FX: Speed multiplier set to {self.move_speed_multiplier:.2f}")
        self._save_state()
    
    def get_interval(self) -> float:
        """Calculate interval in seconds based on BPM and speed multiplier."""
        if self.move_speed_multiplier == 0.0:
            # Prevent division by zero - use very slow speed
            return 60.0 / self.bpm * 100
        return (60.0 / self.bpm) / self.move_speed_multiplier
    
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
        step = 0
        
        while self.running:
            # Recalculate interval on each step for responsive BPM changes
            interval = self.get_interval()
            step_time = interval / steps_per_cycle
            
            # Sine wave for smooth oscillation around center position
            progress = (step % steps_per_cycle) / steps_per_cycle
            
            for idx, fixture_id in enumerate(fixtures):
                # Apply phase offset per fixture
                phase_offset = (idx / len(fixtures)) * self.move_phase if len(fixtures) > 1 else 0
                phase_progress = (progress + phase_offset) % 1.0
                pan_value = self.center_pan + (self.fx_size * 0.5) * math.sin(phase_progress * 2 * math.pi)
                # Use center_tilt from X/Y pad for tilt position
                self._set_pan_tilt(fixture_id, pan_value, self.center_tilt)
            
            step += 1
            time.sleep(step_time)
    
    def _run_tilt_sway(self):
        """Tilt sway effect - smooth up-down movement."""
        fixtures = self.get_moving_fixtures()
        steps_per_cycle = 60
        step = 0
        
        while self.running:
            # Recalculate interval on each step for responsive BPM changes
            interval = self.get_interval()
            step_time = interval / steps_per_cycle
            
            # Sine wave for smooth oscillation around center position
            progress = (step % steps_per_cycle) / steps_per_cycle
            
            for idx, fixture_id in enumerate(fixtures):
                # Apply phase offset per fixture
                phase_offset = (idx / len(fixtures)) * self.move_phase if len(fixtures) > 1 else 0
                phase_progress = (progress + phase_offset) % 1.0
                tilt_value = self.center_tilt + (self.fx_size * 0.5) * 0.7 * math.sin(phase_progress * 2 * math.pi)
                # Use center_pan from X/Y pad for pan position
                self._set_pan_tilt(fixture_id, self.center_pan, tilt_value)
            
            step += 1
            time.sleep(step_time)
    
    def _run_circle(self):
        """Circle effect - smooth continuous circular movement."""
        fixtures = self.get_moving_fixtures()
        steps_per_cycle = 80  # Smooth circular motion
        angle = 0  # Start angle
        
        while self.running:
            # Recalculate interval on each step for responsive BPM changes
            interval = self.get_interval()
            step_time = interval / steps_per_cycle
            angle_increment = (2 * math.pi) / steps_per_cycle
            
            for idx, fixture_id in enumerate(fixtures):
                # Apply phase offset per fixture
                phase_offset = (idx / len(fixtures)) * self.move_phase * 2 * math.pi if len(fixtures) > 1 else 0
                fixture_angle = angle + phase_offset
                
                # Circle with size as radius, centered at user-defined position
                pan_value = self.center_pan + (self.fx_size * 0.5) * math.cos(fixture_angle)
                tilt_value = self.center_tilt + (self.fx_size * 0.5) * math.sin(fixture_angle)
                
                self._set_pan_tilt(fixture_id, pan_value, tilt_value)
            
            angle += angle_increment
            time.sleep(step_time)
    
    def _run_eight(self):
        """Figure-8 effect - lemniscate of Bernoulli pattern."""
        fixtures = self.get_moving_fixtures()
        steps_per_cycle = 100  # Need more steps for complex path
        step = 0
        
        while self.running:
            # Recalculate interval on each step for responsive BPM changes
            interval = self.get_interval() * 2  # One full figure-8 takes 2 beats
            step_time = interval / steps_per_cycle
            
            # Parametric equations for figure-8 (lemniscate)
            progress = (step % steps_per_cycle) / steps_per_cycle
            
            for idx, fixture_id in enumerate(fixtures):
                # Apply phase offset per fixture
                phase_offset = (idx / len(fixtures)) * self.move_phase if len(fixtures) > 1 else 0
                phase_progress = (progress + phase_offset) % 1.0
                t = phase_progress * 2 * math.pi
                
                # Lemniscate formula with user-controlled size and center
                denominator = 1 + math.sin(t) ** 2
                pan_value = self.center_pan + (self.fx_size * 0.5) * math.cos(t) / denominator
                tilt_value = self.center_tilt + (self.fx_size * 0.5) * math.sin(t) * math.cos(t) / denominator
                
                self._set_pan_tilt(fixture_id, pan_value, tilt_value)
            
            step += 1
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
            # Recalculate interval on each step for responsive BPM changes
            interval = self.get_interval()
            step_time = interval / steps_per_cycle
            angle_increment = (2 * math.pi) / steps_per_cycle
            
            for idx, fixture_id in enumerate(fixtures):
                # Apply phase offset per fixture
                phase_offset = (idx / len(fixtures)) * self.move_phase * 2 * math.pi if len(fixtures) > 1 else 0
                fixture_angle = angle + phase_offset
                
                # Lissajous parametric equations with user-controlled center and size
                pan_value = self.center_pan + (self.fx_size * 0.5) * math.sin(freq_x * fixture_angle + phase_x)
                tilt_value = self.center_tilt + (self.fx_size * 0.5) * math.sin(freq_y * fixture_angle + phase_y)
                
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
            # Recalculate interval on each step for responsive BPM changes
            interval = self.get_interval()
            step_time = interval / steps_per_cycle
            angle_increment = (2 * math.pi) / steps_per_cycle
            
            for idx, fixture_id in enumerate(fixtures):
                # Apply phase offset per fixture
                phase_offset = (idx / len(fixtures)) * self.move_phase * 2 * math.pi if len(fixtures) > 1 else 0
                fixture_angle = angle + phase_offset
                
                # Use cubic power for sharper corners
                raw_pan = math.cos(fixture_angle)
                raw_tilt = math.sin(fixture_angle)
                
                # Apply power function for sharpness with user-controlled center and size
                pan_value = self.center_pan + (self.fx_size * 0.5) * (raw_pan ** 3)
                tilt_value = self.center_tilt + (self.fx_size * 0.5) * (raw_tilt ** 3)
                
                self._set_pan_tilt(fixture_id, pan_value, tilt_value)
            
            angle += angle_increment
            time.sleep(step_time)
    
    def _save_state(self):
        """Save current state to file (debounced)."""
        current_time = time.time()
        # Debounce: only save if last save was more than 0.5 seconds ago
        if current_time - self.last_save_time < 0.5:
            return
        
        with self.save_lock:
            try:
                state = {
                    'center_pan': self.center_pan,
                    'center_tilt': self.center_tilt,
                    'fx_size': self.fx_size,
                    'bpm': self.bpm,
                    'move_phase': self.move_phase,
                    'move_speed_multiplier': self.move_speed_multiplier
                }
                
                # Ensure directory exists
                self.state_file.parent.mkdir(parents=True, exist_ok=True)
                
                # Write to temp file then rename (atomic)
                temp_file = self.state_file.with_suffix('.tmp')
                with open(temp_file, 'w') as f:
                    json.dump(state, f, indent=2)
                temp_file.replace(self.state_file)
                
                self.last_save_time = current_time
            except Exception as e:
                print(f"Move FX: Error saving state: {e}")
    
    def _load_state(self):
        """Load state from file."""
        if not self.state_file.exists():
            print("Move FX: No saved state found, using defaults")
            return
        
        try:
            with open(self.state_file, 'r') as f:
                state = json.load(f)
            
            self.center_pan = state.get('center_pan', 0.5)
            self.center_tilt = state.get('center_tilt', 0.5)
            self.fx_size = state.get('fx_size', 0.3)
            self.bpm = state.get('bpm', 20)
            self.move_phase = state.get('move_phase', 0.0)
            self.move_speed_multiplier = state.get('move_speed_multiplier', 1.0)
            
            print(f"Move FX: Loaded state - pan={self.center_pan:.2f}, tilt={self.center_tilt:.2f}, size={self.fx_size:.2f}, bpm={self.bpm}, phase={self.move_phase:.2f}, speed_multiplier={self.move_speed_multiplier:.2f}")
            
            # Apply initial position to fixtures
            for fixture_id in self.get_moving_fixtures():
                self._set_pan_tilt(fixture_id, self.center_pan, self.center_tilt)
        except Exception as e:
            print(f"Move FX: Error loading state: {e}")
    
    def _autosave_loop(self):
        """Background thread to periodically save state."""
        while self.autosave_running:
            time.sleep(self.save_interval)
            if self.autosave_running:  # Check again after sleep
                with self.save_lock:
                    # Force save regardless of debounce
                    old_last_save = self.last_save_time
                    self.last_save_time = 0  # Reset to force save
                    self._save_state()
                    if self.last_save_time == 0:  # If save didn't happen, restore
                        self.last_save_time = old_last_save
    
    def shutdown(self):
        """Shutdown the move FX engine and save state."""
        self.autosave_running = False
        self.stop_fx()
        self._save_state()
        if self.autosave_thread.is_alive():
            self.autosave_thread.join(timeout=1.0)
    
    def get_status(self) -> Dict:
        """Get current FX engine status."""
        return {
            'running': self.running,
            'current_fx': self.current_fx,
            'bpm': self.bpm,
            'moving_fixtures': self.get_moving_fixtures()
        }

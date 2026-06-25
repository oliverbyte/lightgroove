"""
Scene manager for LightGroove.
Handles saving, loading, activating and deleting lighting scenes.
"""
import json
import os
import uuid
from typing import Dict, List, Optional, Any


class SceneManager:
    """Manages lighting scenes — snapshots of fixture states and FX settings."""

    def __init__(self, scenes_file: str, fixture_manager, color_fx=None, move_fx=None):
        self.scenes_file = scenes_file
        self.fixture_manager = fixture_manager
        self.color_fx = color_fx
        self.move_fx = move_fx
        self.scenes: List[Dict[str, Any]] = []
        self._load()

    def _load(self):
        """Load scenes from disk."""
        try:
            with open(self.scenes_file, 'r') as f:
                self.scenes = json.load(f)
            print(f"Scene Manager: Loaded {len(self.scenes)} scenes")
        except Exception as e:
            print(f"Scene Manager: Could not load scenes: {e}")
            self.scenes = []

    def _save(self):
        """Persist scenes to disk."""
        try:
            temp = self.scenes_file + '.tmp'
            with open(temp, 'w') as f:
                json.dump(self.scenes, f, indent=2)
            os.replace(temp, self.scenes_file)
        except Exception as e:
            print(f"Scene Manager: Error saving scenes: {e}")

    def list_scenes(self) -> List[Dict[str, Any]]:
        """Return all scenes (full data)."""
        return self.scenes

    def get_scene(self, scene_id: str) -> Optional[Dict[str, Any]]:
        """Get a single scene by ID."""
        for s in self.scenes:
            if s['id'] == scene_id:
                return s
        return None

    def create_scene(self, name: str, fixture_ids: Optional[List[str]] = None,
                     include_color_cycle: bool = False,
                     include_color_fx: bool = False,
                     include_move_fx: bool = False,
                     include_grandmaster: bool = False) -> Dict[str, Any]:
        """Snapshot the current state into a new scene.

        Args:
            name: Human-readable scene name.
            fixture_ids: Which fixtures to capture. None = all.
            include_color_cycle: Capture the current color cycle.
            include_color_fx: Capture color FX mode + params.
            include_move_fx: Capture move FX mode + params.
            include_grandmaster: Capture grandmaster level.
        """
        if fixture_ids is None:
            fixture_ids = self.fixture_manager.list_fixtures()

        # Capture per-fixture state
        fixtures = {}
        for fid in fixture_ids:
            if fid not in self.fixture_manager.fixtures:
                continue
            state = self.fixture_manager.fixtures[fid].get('state', {})
            fixtures[fid] = dict(state)  # shallow copy of channel values

        scene: Dict[str, Any] = {
            'id': uuid.uuid4().hex[:8],
            'name': name,
            'fixtures': fixtures,
        }

        # Global settings — None means "don't touch on recall"
        if include_color_cycle and self.color_fx:
            scene['color_cycle'] = list(self.color_fx.color_cycle)
        else:
            scene['color_cycle'] = None

        if include_color_fx and self.color_fx:
            scene['color_fx'] = {
                'mode': self.color_fx.current_fx,
                'bpm': self.color_fx.bpm,
                'fade_percentage': self.color_fx.fade_percentage,
            }
        else:
            scene['color_fx'] = None

        if include_move_fx and self.move_fx:
            scene['move_fx'] = {
                'mode': self.move_fx.current_fx,
                'center_pan': self.move_fx.center_pan,
                'center_tilt': self.move_fx.center_tilt,
                'fx_size': self.move_fx.fx_size,
                'move_phase': self.move_fx.move_phase,
                'move_speed_multiplier': self.move_fx.move_speed_multiplier,
            }
        else:
            scene['move_fx'] = None

        if include_grandmaster:
            scene['grandmaster'] = self.fixture_manager.dmx.grandmaster
        else:
            scene['grandmaster'] = None

        self.scenes.append(scene)
        self._save()
        print(f"Scene Manager: Created scene '{name}' ({len(fixtures)} fixtures)")
        return scene

    def update_scene(self, scene_id: str, name: str = None,
                     fixture_ids: Optional[List[str]] = None,
                     include_color_cycle: bool = False,
                     include_color_fx: bool = False,
                     include_move_fx: bool = False,
                     include_grandmaster: bool = False) -> Optional[Dict[str, Any]]:
        """Overwrite a scene with the current state (keeps same ID)."""
        scene = self.get_scene(scene_id)
        if not scene:
            return None

        old_name = scene['name']
        new_name = name if name else old_name

        # Remove old, create new with same ID
        idx = next(i for i, s in enumerate(self.scenes) if s['id'] == scene_id)

        if fixture_ids is None:
            fixture_ids = self.fixture_manager.list_fixtures()

        fixtures = {}
        for fid in fixture_ids:
            if fid not in self.fixture_manager.fixtures:
                continue
            state = self.fixture_manager.fixtures[fid].get('state', {})
            fixtures[fid] = dict(state)

        updated: Dict[str, Any] = {
            'id': scene_id,
            'name': new_name,
            'fixtures': fixtures,
        }

        if include_color_cycle and self.color_fx:
            updated['color_cycle'] = list(self.color_fx.color_cycle)
        else:
            updated['color_cycle'] = None

        if include_color_fx and self.color_fx:
            updated['color_fx'] = {
                'mode': self.color_fx.current_fx,
                'bpm': self.color_fx.bpm,
                'fade_percentage': self.color_fx.fade_percentage,
            }
        else:
            updated['color_fx'] = None

        if include_move_fx and self.move_fx:
            updated['move_fx'] = {
                'mode': self.move_fx.current_fx,
                'center_pan': self.move_fx.center_pan,
                'center_tilt': self.move_fx.center_tilt,
                'fx_size': self.move_fx.fx_size,
                'move_phase': self.move_fx.move_phase,
                'move_speed_multiplier': self.move_fx.move_speed_multiplier,
            }
        else:
            updated['move_fx'] = None

        if include_grandmaster:
            updated['grandmaster'] = self.fixture_manager.dmx.grandmaster
        else:
            updated['grandmaster'] = None

        self.scenes[idx] = updated
        self._save()
        print(f"Scene Manager: Updated scene '{new_name}'")
        return updated

    def delete_scene(self, scene_id: str) -> bool:
        """Delete a scene by ID."""
        before = len(self.scenes)
        self.scenes = [s for s in self.scenes if s['id'] != scene_id]
        if len(self.scenes) < before:
            self._save()
            print(f"Scene Manager: Deleted scene {scene_id}")
            return True
        return False

    def activate_scene(self, scene_id: str) -> bool:
        """Recall a scene — apply its stored state to the system.

        Activation order:
        1. Color cycle (before FX so it uses correct colors)
        2. Per-fixture channels (colors, dimmers, etc.)
        3. Color FX
        4. Move FX
        5. Grandmaster
        """
        scene = self.get_scene(scene_id)
        if not scene:
            return False

        # 1. Color cycle
        if scene.get('color_cycle') is not None and self.color_fx:
            self.color_fx.set_color_cycle(scene['color_cycle'])
            # Also persist to config file
            try:
                config_path = os.path.join(os.path.dirname(self.scenes_file), 'colors.json')
                with open(config_path, 'r') as f:
                    config = json.load(f)
                config['color_cycle'] = scene['color_cycle']
                with open(config_path, 'w') as f:
                    json.dump(config, f, indent=2)
            except Exception:
                pass

        # 2. Per-fixture state
        for fid, state in scene.get('fixtures', {}).items():
            if fid not in self.fixture_manager.fixtures:
                continue
            for channel_name, value in state.items():
                self.fixture_manager.set_fixture_channel(fid, channel_name, value)

        # 3. Color FX
        color_fx_data = scene.get('color_fx')
        if color_fx_data is not None and self.color_fx:
            if color_fx_data.get('bpm'):
                self.color_fx.set_bpm(color_fx_data['bpm'])
            if color_fx_data.get('fade_percentage') is not None:
                self.color_fx.set_fade_percentage(color_fx_data['fade_percentage'])
            mode = color_fx_data.get('mode')
            if mode:
                self.color_fx.start_fx(mode)
            else:
                self.color_fx.stop_fx()

        # 4. Move FX
        move_fx_data = scene.get('move_fx')
        if move_fx_data is not None and self.move_fx:
            if move_fx_data.get('center_pan') is not None:
                self.move_fx.set_center(
                    move_fx_data['center_pan'],
                    move_fx_data.get('center_tilt', 0.5)
                )
            if move_fx_data.get('fx_size') is not None:
                self.move_fx.set_fx_size(move_fx_data['fx_size'])
            if move_fx_data.get('move_phase') is not None:
                self.move_fx.set_move_phase(move_fx_data['move_phase'])
            if move_fx_data.get('move_speed_multiplier') is not None:
                self.move_fx.set_move_speed(move_fx_data['move_speed_multiplier'])
            mode = move_fx_data.get('mode')
            if mode:
                self.move_fx.start_fx(mode)
            else:
                self.move_fx.stop_fx()

        # 5. Grandmaster
        if scene.get('grandmaster') is not None:
            self.fixture_manager.dmx.set_grandmaster(scene['grandmaster'])
            self.fixture_manager.reapply_all_states()

        print(f"Scene Manager: Activated scene '{scene['name']}'")
        return True

    def reorder_scenes(self, scene_ids: List[str]) -> bool:
        """Reorder scenes to match the given ID list."""
        id_to_scene = {s['id']: s for s in self.scenes}
        reordered = []
        for sid in scene_ids:
            if sid in id_to_scene:
                reordered.append(id_to_scene[sid])
        # Append any scenes not in the list (shouldn't happen but be safe)
        seen = set(scene_ids)
        for s in self.scenes:
            if s['id'] not in seen:
                reordered.append(s)
        self.scenes = reordered
        self._save()
        return True

"""
DMX Controller with Multi-Universe and ArtNet Support
Manages DMX output via serial, ArtNet or virtual interfaces
Author: https://github.com/oliverbyte
"""
import json
import socket
import struct
import threading
import time
from typing import Optional, Dict, List, Tuple


def _decode_artnet_str(raw: bytes) -> str:
    """Decode a null-terminated ArtNet name field.

    ArtNet strings are null-terminated; bytes after the first null are padding
    and must be ignored before decoding.  Devices may use UTF-8 or Latin-1, so
    try UTF-8 first and fall back to Latin-1 (which maps all 256 byte values).
    """
    null = raw.find(b'\x00')
    raw = raw[:null] if null != -1 else raw
    try:
        return raw.decode('utf-8').strip()
    except UnicodeDecodeError:
        return raw.decode('latin-1').strip()


def discover_artnet_nodes(timeout: float = 2.0) -> list:
    """Broadcast ArtPoll and collect ArtPollReply packets to find nodes on the network."""
    ARTNET_PORT = 6454
    ARTPOLL_REPLY_OPCODE = 0x2100

    artpoll = (
        b'Art-Net\x00'  # ID
        b'\x00\x20'     # OpCode ArtPoll (0x2000, little-endian)
        b'\x00\x0e'     # ProtVer 14
        b'\x00'         # Flags
        b'\x00'         # DiagPriority
    )

    discovered = []
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        except AttributeError:
            pass  # Not available on Windows
        sock.settimeout(0.1)
        sock.bind(('', ARTNET_PORT))
        sock.sendto(artpoll, ('255.255.255.255', ARTNET_PORT))

        deadline = time.time() + timeout
        seen_ips = set()

        while time.time() < deadline:
            try:
                data, addr = sock.recvfrom(1024)
                ip = addr[0]
                if ip in seen_ips or len(data) < 194:
                    continue
                if data[:8] != b'Art-Net\x00':
                    continue
                opcode = struct.unpack_from('<H', data, 8)[0]
                if opcode != ARTPOLL_REPLY_OPCODE:
                    continue

                short_name = _decode_artnet_str(data[26:44])
                long_name  = _decode_artnet_str(data[44:108])
                num_ports  = struct.unpack_from('>H', data, 172)[0]
                sw_out     = [data[190 + i] for i in range(min(num_ports, 4))]

                seen_ips.add(ip)
                discovered.append({
                    'ip': ip,
                    'short_name': short_name,
                    'long_name': long_name,
                    'name': long_name or short_name or ip,
                    'num_ports': num_ports,
                    'universes': sw_out,
                })
            except socket.timeout:
                continue
    except Exception as e:
        print(f"ArtNet discovery error: {e}")
    finally:
        try:
            sock.close()
        except Exception:
            pass

    return discovered


class DMXUniverse:
    """Represents a single DMX universe with 512 channels"""

    def __init__(self, universe_id: int, output_mode: str = 'virtual'):
        self.universe_id = universe_id
        self.output_mode = output_mode  # 'serial', 'artnet', 'sacn', 'virtual'
        self.dmx_data = [0] * 512
        self.lock = threading.Lock()
        self.artnet_sender = None
        self.sacn_sender = None
        self.serial = None
        
    def set_channel(self, channel: int, value: int):
        """Set a single DMX channel (1-512)"""
        if 1 <= channel <= 512:
            with self.lock:
                self.dmx_data[channel - 1] = max(0, min(255, value))
    
    def set_channels(self, start_channel: int, values: list):
        """Set multiple DMX channels"""
        with self.lock:
            for i, value in enumerate(values):
                channel = start_channel + i
                if 1 <= channel <= 512:
                    self.dmx_data[channel - 1] = max(0, min(255, value))
    
    def get_channel(self, channel: int) -> int:
        """Get current value of a DMX channel"""
        if 1 <= channel <= 512:
            with self.lock:
                return self.dmx_data[channel - 1]
        return 0
    
    def get_data(self) -> list:
        """Get copy of all DMX data"""
        with self.lock:
            return self.dmx_data.copy()
    
    def blackout(self):
        """Set all channels to 0"""
        with self.lock:
            self.dmx_data = [0] * 512


class DMXController:
    """Controls multiple DMX universes via various output methods"""
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize DMX controller with multi-universe support
        
        Args:
            config_file: Path to artnet.json configuration file
        """
        self.universes: Dict[int, DMXUniverse] = {}
        self.artnet_senders: Dict[Tuple[str, int], any] = {}
        self.sacn_senders: Dict[Tuple[str, int], any] = {}
        self.config = {}
        self.running = False
        self._thread = None
        self.fps = 44
        self.serial = None
        self.grandmaster = 1.0  # 0.0 to 1.0 multiplier
        
        if config_file:
            self._load_config(config_file)
    
    def _load_config(self, config_file: str):
        """Load ArtNet configuration"""
        try:
            with open(config_file, 'r') as f:
                self.config = json.load(f)
            
            self.fps = self.config.get('fps', 44)
            
            # Initialize universes based on mapping
            for universe_str, mapping in self.config.get('universe_mapping', {}).items():
                universe_id = int(universe_str)
                output_mode = mapping.get('output_mode', 'virtual')
                
                universe = DMXUniverse(universe_id, output_mode)
                
                # Configure output for this universe
                if output_mode == 'artnet':
                    node_id = mapping.get('node_id')
                    artnet_universe = mapping.get('artnet_universe', 0)
                    node_config = self._find_node_config(node_id)
                    if node_config and node_config.get('enabled', True):
                        sender = self._get_or_create_artnet_sender(node_config, artnet_universe)
                        universe.artnet_sender = sender
                    else:
                        print(f"DMX Controller: ArtNet node '{node_id}' not found or disabled")

                elif output_mode == 'sacn':
                    node_id = mapping.get('node_id')
                    sacn_universe = mapping.get('artnet_universe', universe_id)
                    node_config = self._find_node_config(node_id)
                    if node_config and node_config.get('enabled', True):
                        sender = self._get_or_create_sacn_sender(node_config, sacn_universe)
                        universe.sacn_sender = sender
                    else:
                        print(f"DMX Controller: sACN node '{node_id}' not found or disabled")
                
                self.universes[universe_id] = universe
                print(f"DMX Controller: Universe {universe_id} initialized ({output_mode})")
            
            # Configure serial port if specified
            serial_port = self.config.get('serial_port')
            if serial_port:
                self._init_serial(serial_port)
            
        except Exception as e:
            print(f"DMX Controller: Failed to load config: {e}")
            print("DMX Controller: Running in virtual mode")

    def _find_node_config(self, node_id: str) -> Optional[dict]:
        for node in self.config.get('nodes', []):
            if node.get('id') == node_id:
                return node
        return None

    def _get_or_create_sacn_sender(self, node_config: dict, sacn_universe: int):
        key = (node_config['id'], sacn_universe)
        if key in self.sacn_senders:
            return self.sacn_senders[key]
        try:
            from sacn_sender import SACNSender
            ip = node_config.get('ip')
            multicast = bool(node_config.get('broadcast', False))
            sender = SACNSender(sacn_universe, target_ip=ip, multicast=multicast)
            self.sacn_senders[key] = sender
            mode = "multicast" if multicast else f"unicast to {ip}"
            print(f"DMX Controller: sACN sender for node '{node_config['id']}' universe {sacn_universe} ({mode})")
            return sender
        except Exception as e:
            print(f"DMX Controller: Failed to initialize sACN sender for node '{node_config['id']}': {e}")
        return None

    def _get_or_create_artnet_sender(self, node_config: dict, artnet_universe: int):
        key = (node_config['id'], artnet_universe)
        if key in self.artnet_senders:
            return self.artnet_senders[key]
        try:
            from stupidArtnet import StupidArtnet

            ip = node_config.get('ip', '255.255.255.255')
            broadcast = bool(node_config.get('broadcast', False))
            target_ip = '255.255.255.255' if broadcast else ip
            sender = StupidArtnet(target_ip, artnet_universe, packet_size=512, fps=self.fps, broadcast=broadcast)
            sender.start()
            self.artnet_senders[key] = sender
            mode = "broadcast" if broadcast else "unicast"
            # Note: StupidArtnet always uses port 6454 (standard ArtNet port) - custom ports not supported
            print(f"DMX Controller: ArtNet sender for node '{node_config['id']}' universe {artnet_universe} connected to {target_ip}:6454 ({mode})")
            return sender
        except ImportError:
            print("DMX Controller: stupidArtnet not installed. Install with: pip install stupidArtnet")
        except Exception as e:
            print(f"DMX Controller: Failed to initialize ArtNet sender for node '{node_config['id']}' universe {artnet_universe}: {e}")
        return None
    
    def _init_serial(self, port: str):
        """Initialize serial connection for DMX output"""
        try:
            import serial
            self.serial = serial.Serial(
                port=port,
                baudrate=250000,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.TWOSTOPBITS
            )
            print(f"DMX Controller: Serial port connected to {port}")
        except Exception as e:
            print(f"DMX Controller: Failed to connect to serial port {port}: {e}")
    
    def add_universe(self, universe_id: int, output_mode: str = 'virtual'):
        """Add a new universe dynamically"""
        if universe_id not in self.universes:
            self.universes[universe_id] = DMXUniverse(universe_id, output_mode)
            print(f"DMX Controller: Universe {universe_id} added ({output_mode})")
    
    def set_grandmaster(self, level: float):
        """
        Set grandmaster level (scales all DMX output)
        
        Args:
            level: Grandmaster level 0.0-1.0
        """
        self.grandmaster = max(0.0, min(1.0, level))
        print(f"DMX Controller: Grandmaster set to {int(self.grandmaster * 100)}%")
    
    def set_channel(self, universe_id: int, channel: int, value: int, channel_type: str = 'other'):
        """
        Set a single DMX channel in a specific universe
        
        Args:
            universe_id: Universe ID (1-based)
            channel: DMX channel (1-512)
            value: DMX value (0-255)
            channel_type: Channel type ('dimmer', 'color', 'pan', 'tilt', 'other')
        """
        if universe_id not in self.universes:
            self.add_universe(universe_id)
        
        # Apply grandmaster scaling only to dimmer channels
        if channel_type == 'dimmer':
            scaled_value = int(value * self.grandmaster)
        else:
            scaled_value = value
        self.universes[universe_id].set_channel(channel, scaled_value)
    
    def set_channels(self, universe_id: int, start_channel: int, values: list):
        """Set multiple DMX channels in a specific universe"""
        if universe_id not in self.universes:
            self.add_universe(universe_id)
        
        self.universes[universe_id].set_channels(start_channel, values)
    
    def get_channel(self, universe_id: int, channel: int) -> int:
        """Get current value of a DMX channel in a specific universe"""
        if universe_id in self.universes:
            return self.universes[universe_id].get_channel(channel)
        return 0
    
    def blackout(self, universe_id: Optional[int] = None):
        """
        Set channels to 0
        
        Args:
            universe_id: Specific universe to blackout, or None for all universes
        """
        if universe_id is not None:
            if universe_id in self.universes:
                self.universes[universe_id].blackout()
        else:
            for universe in self.universes.values():
                universe.blackout()
    
    def start(self):
        """Start DMX output thread"""
        if not self.running:
            self.running = True
            self._thread = threading.Thread(target=self._output_loop, daemon=True)
            self._thread.start()
            print("DMX Controller: Output started")
    
    def stop(self):
        """Stop DMX output and cleanup"""
        self.running = False
        if self._thread:
            self._thread.join(timeout=2)

        # Stop ArtNet senders
        for key, sender in self.artnet_senders.items():
            try:
                sender.stop()
                print(f"DMX Controller: ArtNet sender {key} stopped")
            except Exception:
                pass

        # Stop sACN senders
        for key, sender in self.sacn_senders.items():
            try:
                sender.stop()
                print(f"DMX Controller: sACN sender {key} stopped")
            except Exception:
                pass
        
        # Close serial
        if hasattr(self, 'serial') and self.serial and self.serial.is_open:
            self.serial.close()
        
        print("DMX Controller: Output stopped")
    
    def reload_config(self, config_file: str):
        """
        Reload configuration from file without stopping the controller.
        Preserves current channel values where possible.
        
        Args:
            config_file: Path to artnet.json configuration file
        """
        print("DMX Controller: Reloading configuration...")
        
        # Store current channel values from all universes
        current_values = {}
        for universe_id, universe in self.universes.items():
            current_values[universe_id] = universe.dmx_data.copy()
        
        # Stop output temporarily
        was_running = self.running
        if was_running:
            self.running = False
            if self._thread:
                self._thread.join(timeout=2)
        
        # Cleanup old ArtNet senders
        for sender in self.artnet_senders.values():
            try:
                sender.stop()
            except:
                pass
        self.artnet_senders = {}

        # Cleanup old sACN senders
        for sender in self.sacn_senders.values():
            try:
                sender.stop()
            except:
                pass
        self.sacn_senders = {}
        
        # Reload configuration
        self.universes = {}
        self._load_config(config_file)
        
        # Restore channel values where universes still exist
        for universe_id, values in current_values.items():
            if universe_id in self.universes:
                self.universes[universe_id].dmx_data = values
                print(f"DMX Controller: Restored values for Universe {universe_id}")
        
        # Restart output if it was running
        if was_running:
            self.running = True
            self._thread = threading.Thread(target=self._output_loop, daemon=True)
            self._thread.start()
        
        print("DMX Controller: Configuration reloaded successfully")
    
    def _output_loop(self):
        """Main output loop - sends DMX data periodically"""
        frame_time = 1.0 / self.fps
        
        while self.running:
            start_time = time.time()
            
            for universe_id, universe in self.universes.items():
                try:
                    if universe.output_mode == 'artnet' and universe.artnet_sender:
                        data = universe.get_data()
                        universe.artnet_sender.set(data)
                        universe.artnet_sender.show()

                    elif universe.output_mode == 'sacn' and universe.sacn_sender:
                        data = universe.get_data()
                        universe.sacn_sender.set(data)
                        universe.sacn_sender.show()

                    elif universe.output_mode == 'serial' and hasattr(self, 'serial') and self.serial and self.serial.is_open:
                        data = universe.get_data()
                        self.serial.break_condition = True
                        time.sleep(0.0001)  # Break (100us)
                        self.serial.break_condition = False
                        time.sleep(0.000012)  # Mark After Break (12us)

                        dmx_packet = bytes([0x00] + data)
                        self.serial.write(dmx_packet)

                    # Virtual mode: no output

                except Exception as e:
                    print(f"DMX Controller: Output error for universe {universe_id}: {e}")
            
            # Maintain target FPS
            elapsed = time.time() - start_time
            sleep_time = max(0, frame_time - elapsed)
            time.sleep(sleep_time)


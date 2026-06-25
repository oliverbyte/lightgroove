"""sACN (E1.31) sender — pure stdlib, no external dependencies.

Packet layout (638 bytes, fixed for 512 channels):
  Offset  0: Preamble (16 bytes)
  Offset 16: Root Layer PDU — flags+length, vector (0x04), CID
  Offset 38: Framing Layer PDU — flags+length, vector (0x02), source name,
              priority, sync addr, sequence, options, universe
  Offset 115: DMP Layer PDU — flags+length, vector (0x02), addr/type,
               first addr, increment, count, start code, 512 bytes DMX

Multicast address for universe N: 239.255.(N>>8).(N&0xFF)  [E1.31 §9.3.2]
Port: 5568
"""
import socket
import uuid

_ACN_ID = bytes([
    0x41, 0x53, 0x43, 0x2d, 0x45, 0x31, 0x2e,
    0x31, 0x37, 0x00, 0x00, 0x00,
])
SACN_PORT = 5568

# Pre-computed PDU lengths for a 512-channel packet (total = 638 bytes)
_ROOT_LEN    = 622   # 638 - 16
_FRAMING_LEN = 600   # 638 - 38
_DMP_LEN     = 523   # 638 - 115


def _multicast_addr(universe: int) -> str:
    return f"239.255.{(universe >> 8) & 0xFF}.{universe & 0xFF}"


class SACNSender:
    """Send sACN (E1.31) packets for a single universe.

    API matches StupidArtnet so DMXController can use both interchangeably:
      sender.set(data)  — store up to 512 bytes of DMX data
      sender.show()     — transmit the packet
      sender.stop()     — close the socket
    """

    def __init__(
        self,
        universe: int,
        target_ip: str | None = None,
        multicast: bool = False,
        source_name: str = "LightGroove",
    ):
        if not (1 <= universe <= 63999):
            raise ValueError(f"sACN universe must be 1-63999, got {universe}")

        self.universe = universe
        self._sequence = 0
        self._dmx = bytearray(512)

        if multicast or target_ip is None:
            self._target = _multicast_addr(universe)
            self._multicast = True
        else:
            self._target = target_ip
            self._multicast = False

        # Stable CID derived from the universe number so it survives restarts
        self._cid = uuid.uuid5(uuid.NAMESPACE_DNS, f"lightgroove.sacn.{universe}").bytes

        enc = source_name.encode("utf-8")[:63]
        self._source_name = enc + b"\x00" * (64 - len(enc))

        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        if self._multicast:
            self._sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 8)

    def set(self, data) -> None:
        n = min(len(data), 512)
        self._dmx[:n] = bytes(data[:n])
        if n < 512:
            self._dmx[n:] = b"\x00" * (512 - n)

    def show(self) -> None:
        try:
            self._sock.sendto(self._build_packet(), (self._target, SACN_PORT))
        except Exception as e:
            print(f"sACN send error (universe {self.universe}): {e}")
        self._sequence = (self._sequence + 1) % 256

    def stop(self) -> None:
        try:
            self._sock.close()
        except Exception:
            pass

    def _build_packet(self) -> bytes:
        u   = self.universe
        rl  = _ROOT_LEN
        fl  = _FRAMING_LEN
        dl  = _DMP_LEN

        return (
            b"\x00\x10\x00\x00"              # Preamble + postamble size
            + _ACN_ID                         # ACN packet identifier (12 bytes)
            # Root layer
            + bytes([0x70 | (rl >> 8), rl & 0xFF])
            + b"\x00\x00\x00\x04"             # VECTOR_ROOT_E131_DATA
            + self._cid                        # CID (16 bytes)
            # Framing layer
            + bytes([0x70 | (fl >> 8), fl & 0xFF])
            + b"\x00\x00\x00\x02"             # VECTOR_E131_DATA_PACKET
            + self._source_name               # Source name (64 bytes)
            + bytes([
                0x64,                          # Priority 100
                0x00, 0x00,                    # No synchronisation address
                self._sequence,                # Sequence number
                0x00,                          # Options
                (u >> 8) & 0xFF, u & 0xFF,     # Universe
            ])
            # DMP layer
            + bytes([0x70 | (dl >> 8), dl & 0xFF])
            + bytes([
                0x02,                          # VECTOR_DMP_SET_PROPERTY
                0xa1,                          # Address type & data type
                0x00, 0x00,                    # First property address
                0x00, 0x01,                    # Address increment
                0x02, 0x01,                    # Property count (513)
                0x00,                          # DMX start code
            ])
            + bytes(self._dmx)                 # 512 bytes DMX data
        )

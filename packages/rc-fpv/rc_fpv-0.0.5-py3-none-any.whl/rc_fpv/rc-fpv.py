import socket
import threading
import time

# ─── Protocol constants ──────────────────────────────────────────────────────
HEADER         = 0x66  # CONTROL_VALUES_BYTE0
TAIL           = 0x99  # CONTROL_VALUES_BYTE7
PREFIX_CMD     = 0x03  # “continuous‐control” packet
PREFIX_SIMPLE  = 0x01  # “simple” packet (keep‐alive)
NEUTRAL        = 128
INTERVAL       = 0.05  # 50 ms

# network ports
LOCAL_PORT     = 35071  # source port for commands
DRONE_PORT     = 7099   # destination port on drone

# expected “alive” payload from drone
ALIVE_PAYLOAD  = bytes([0x48, 0x01, 0x00, 0x00, 0x00])

class DroneController:

    def __init__(self, ip: str, local_port=LOCAL_PORT, drone_port=DRONE_PORT, interval=INTERVAL):
        # Prepare UDP socket bound to LOCAL_PORT
        self.addr = (ip, drone_port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('', local_port))
        self.sock.settimeout(interval)

        self.interval=interval

        # joystick state (floats in [-1,1])
        self.x = 0.0  # right (+) / left (–)
        self.y = 0.0  # forward (+) / backward (–)

        # derived byte values (1…255)
        self.roll     = self.pitch = self.THROTTLE = self.YAW = NEUTRAL

        # mode flags (octet 5)
        self.is_fixed_height   = False
        self.is_track_mode     = False
        self.is_gesture_mode   = False
        self.is_gravity_sensor = False
        self.is_no_head_mode   = False
        self.is_music_mode     = False
        self.is_filter_mode    = False

        # action flags (octet 6)
        self.is_fast_fly       = False
        self.is_fast_drop      = False
        self.is_emergency_stop = False
        self.is_circle_turn    = False
        self.is_circle_end     = False
        self.is_unlock         = False  # arm/take-off
        self.is_gyro_corr      = False

        # liveness
        self.alive = False

        # start background threads
        threading.Thread(target=self._sender_loop,   daemon=True).start()
        threading.Thread(target=self._receiver_loop, daemon=True).start()

    # CRC-8 (poly 0x07)
    def _crc8(self, data: bytes) -> int:
        crc = 0
        for b in data:
            crc ^= b
            for _ in range(8):
                if crc & 0x80:
                    crc = ((crc << 1) ^ 0x07) & 0xFF
                else:
                    crc = (crc << 1) & 0xFF
        return crc

    # Build the raw 8-byte payload
    def _build_raw_payload(self) -> bytes:
        p, r, t, y = self.pitch, self.roll, self.THROTTLE, self.YAW
        # modes (octet 5)
        modes = (
            self.is_fixed_height,
            self.is_track_mode,
            self.is_gesture_mode,
            self.is_gravity_sensor,
            self.is_no_head_mode,
            self.is_music_mode,
            self.is_filter_mode,
        )
        flags1 = sum(1 << i for i, f in enumerate(modes) if f)
        # actions (octet 6)
        actions = (
            self.is_fast_fly,
            self.is_fast_drop,
            self.is_emergency_stop,
            self.is_circle_turn,
            self.is_circle_end,
            self.is_unlock,
            self.is_gyro_corr,
        )
        flags2 = sum(1 << i for i, f in enumerate(actions) if f)
        return bytes([HEADER, p, r, t, y, flags1, flags2, TAIL])

    # Build full control message
    def build_message(self) -> bytes:
        raw = self._build_raw_payload()
        crc = self._crc8(raw[:-1])                # over HEADER…flags2
        return bytes([PREFIX_CMD]) + raw[:-1] + bytes([crc, raw[-1]])

    # Build keep-alive packet
    def build_keep_alive(self) -> bytes:
        # 0x01 = prefix “simple”, 0x01 = CRC-8(0x01)
        return bytes([PREFIX_SIMPLE, PREFIX_SIMPLE])

    # Sender thread: send every INTERVAL
    def _sender_loop(self):
        while True:
            # update roll/pitch from joystick floats
            self.roll  = self._float_to_byte(self.x)
            self.pitch = self._float_to_byte(self.y)

            # send control or keep-alive
            pkt = self.build_message() if (self.x or self.y) else self.build_keep_alive()
            self.sock.sendto(pkt, self.addr)
            time.sleep(self.interval)

    # Receiver thread: listen for ALIVE_PAYLOAD
    def _receiver_loop(self):
        while True:
            try:
                data, _ = self.sock.recvfrom(1024)
                self.alive = (data == ALIVE_PAYLOAD)
            except socket.timeout:
                self.alive = False

    # Action ponctuelles
    def takeoff(self):
        """Arm + décollage."""
        self.is_unlock = True
        self.sock.sendto(self.build_message(), self.addr)
        self.is_unlock = False

    def land(self):
        """Atterrissage / arrêt d’urgence."""
        self.is_emergency_stop = True
        self.sock.sendto(self.build_message(), self.addr)
        self.is_emergency_stop = False

    # Joystick helper
    def _float_to_byte(self, v: float) -> int:
        if not -1.0 <= v <= 1.0:
            raise ValueError("Value must be between -1 and 1")
        return int(v * 127) + 128

    def set_direction(self, x: float, y: float):
        """
        x: right (+1) / left (–1)
        y: forward (+1) / backward (–1)
        """
        self.x = x
        self.y = y


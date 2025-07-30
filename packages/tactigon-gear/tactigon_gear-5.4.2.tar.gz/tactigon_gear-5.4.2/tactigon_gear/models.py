import operator
import struct
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
from functools import reduce

from typing import Optional, List, Tuple
    
class BLECommands(Enum):
    WRITE = 1
    READ = 2

class BLECommandWord(Enum):
    UPDATE_TOUCH1       = 0x41
    UPDATE_TOUCH2       = 0x42
    WRITE_TOUCH         = 0x43
    START               = 0x00
    STOP                = 0x01
    STATUS              = 0xFF

class BLECommandMask(Enum):
    SENSORFUSION        = b'\x00\x00\x01\x00'
    ECOMPASS            = b'\x00\x00\x00\x40'


class Hand(Enum):
    RIGHT = "right"
    LEFT = "left"

class TBleConnectionStatus(Enum):
    NONE = 0
    CONNECTING = 1
    CONNECTED = 2
    DISCONNECTING = 3
    DISCONNECTED = 4

class TBleSelector(Enum):
    NONE = 0
    SENSORS = 1
    AUDIO = 2

class OneFingerGesture(Enum):
    NONE = 0x00
    SINGLE_TAP = 0x01
    TAP_AND_HOLD = 0x02
    SWIPE_X_NEG = 0x04
    SWIPE_X_POS = 0x08
    SWIPE_Y_NEG = 0x20
    SWIPE_Y_POS = 0x10

class TwoFingerGesture(Enum):
    NONE = 0x00
    TWO_FINGER_TAP = 0x01
    SCROLL = 0x02
    ZOOM = 0x04

@dataclass
class BLECommand:
    command: BLECommands
    characteristic: str
    payload: Optional[bytes] = None

@dataclass
class Gesture:
    gesture: str
    probability: float
    confidence: float
    displacement: float

    def toJSON(self) -> dict:
        return {
            "gesture": self.gesture,
            "probability": self.probability,
            "confidence": self.confidence,
            "displacement": self.displacement,
        }

@dataclass
class Acceleration:
    x: float
    y: float
    z: float

    def toJSON(self) -> dict:
        return {
            "x": self.x,
            "y": self.y,
            "z": self.z,
        }

@dataclass
class Angle:
    roll: float
    pitch: float
    yaw: float

    def toJSON(self) -> dict:
        return {
            "roll": self.roll,
            "pitch": self.pitch,
            "yaw": self.yaw,
        }

@dataclass
class Gyro:
    x: float
    y: float
    z: float

    def toJSON(self) -> dict:
        return {
            "x": self.x,
            "y": self.y,
            "z": self.z,
        }

@dataclass
class Touch:
    one_finger: OneFingerGesture
    two_finger: TwoFingerGesture
    x_pos: float
    y_pos: float

    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, Touch):
            return (
                self.one_finger == __value.one_finger 
                and self.two_finger == __value.two_finger
                and self.x_pos == __value.x_pos
                and self.y_pos == __value.y_pos
            )
        
        return False
    
    def toJSON(self) -> dict:
        return {
            "one_finger": self.one_finger.value,
            "two_finger": self.two_finger.value,
            "x_pos": self.x_pos,
            "y_pos": self.y_pos
        }

@dataclass
class TSkinState:
    connected: bool
    sleep: bool
    battery: Optional[float]
    selector: Optional[TBleSelector]
    touch: Optional[Touch]
    angle: Optional[Angle]
    gesture: Optional[Gesture]

    def toJSON(self) -> dict:
        return {
            "connected": self.connected,
            "sleep": self.sleep,
            "battery": self.battery,
            "selector": self.selector.value if self.selector else None,
            "touch": self.touch.toJSON() if self.touch else None,
            "angle": self.angle.toJSON() if self.angle else None,
            "gesture": self.gesture.toJSON() if self.gesture else None,
        }

@dataclass
class GestureConfig:
    model_path: str
    encoder_path: str
    name: str
    created_at: datetime
    gestures: Optional[List[str]] = None
    num_sample: int = 10
    gesture_prob_th: float = 0.85
    confidence_th: float = 5

    @classmethod
    def FromJSON(cls, json: dict):
        return cls(
            json["model_path"],
            json["encoder_path"],
            json["name"],
            datetime.fromisoformat(json["created_at"]),
            json["gestures"] if "gestures" in json else None,
            json["num_sample"] if "num_sample" in json and json["num_sample"] is not None else cls.num_sample,
            json["gesture_prob_th"] if "gesture_prob_th" in json and json["gesture_prob_th"] is not None else cls.gesture_prob_th,
            json["confidence_th"] if "confidence_th" in json and json["confidence_th"] is not None else cls.confidence_th,
            )
    
    def toJSON(self) -> dict:
        return {
            "model_path": self.model_path,
            "encoder_path": self.encoder_path,
            "name": self.name,
            "created_at": self.created_at.isoformat(),
            "gestures": self.gestures
        }

@dataclass
class TouchConfig:
    FORMAT_CFG1 = ">BBHHHHBHBHHH"
    FORMAT_CFG2 = ">BBHHHBBHHHHH"
    FORMAT_CMD  = ">BBHHHHHHHHH"

    swipe_initial_time: int
    swipe_initial_distance: int
    swipe_consecutive_time: int
    swipe_consecutive_distance: int
    swipe_angle: int
    scroll_initial_distance: int
    scroll_angle: int
    zoom_initial_distance: int
    zoom_consecutive_distance: int
    tap_time: int
    tap_distance: int
    hold_time: int
    one_finger_gesture: List[OneFingerGesture]
    two_finger_gesture: List[TwoFingerGesture]

    @classmethod
    def FromJSON(cls, json):
        return cls(
            json["swipe_initial_time"],
            json["swipe_initial_distance"],
            json["swipe_consecutive_time"],
            json["swipe_consecutive_distance"],
            json["swipe_angle"],
            json["scroll_initial_distance"],
            json["scroll_angle"],
            json["zoom_initial_distance"],
            json["zoom_consecutive_distance"],
            json["tap_time"],
            json["tap_distance"],
            json["hold_time"],
            [OneFingerGesture(f) for f in json["one_finger_gesture"]],
            [TwoFingerGesture(f) for f in json["two_finger_gesture"]],
        )
    
    @classmethod
    def Default(cls):
        return cls(
            swipe_initial_time=200,
            swipe_initial_distance=25,
            swipe_consecutive_time=150,
            swipe_consecutive_distance=25,
            swipe_angle=23,
            scroll_initial_distance=50,
            scroll_angle=37,
            zoom_initial_distance=50,
            zoom_consecutive_distance=5,
            tap_time=300,
            tap_distance=75,
            hold_time=10,
            one_finger_gesture=[OneFingerGesture.SINGLE_TAP, OneFingerGesture.TAP_AND_HOLD],
            two_finger_gesture=[TwoFingerGesture.TWO_FINGER_TAP]
        )
    
    @classmethod
    def High(cls):
        c = cls.Default()
        c.tap_time = 150
        c.tap_distance = 50
        return c

    @classmethod
    def Medium(cls):
        return cls.Default()

    @classmethod
    def Low(cls):
        c = cls.Default()
        c.tap_time = 600
        c.tap_distance = 150
        c.hold_time = 50
        return c

    def toJSON(self):
        return {
            "swipe_initial_time": self.swipe_initial_time,
            "swipe_initial_distance": self.swipe_initial_distance,
            "swipe_consecutive_time": self.swipe_consecutive_time,
            "swipe_consecutive_distance": self.swipe_consecutive_distance,
            "swipe_angle": self.swipe_angle,
            "scroll_initial_distance": self.scroll_initial_distance,
            "scroll_angle": self.scroll_angle,
            "zoom_initial_distance": self.zoom_initial_distance,
            "zoom_consecutive_distance": self.zoom_consecutive_distance,
            "tap_time": self.tap_time,
            "tap_distance": self.tap_distance,
            "hold_time": self.hold_time,
            "one_finger_gesture": [ofg.value for ofg in self.one_finger_gesture],
            "two_finger_gesture": [tfg.value for tfg in self.two_finger_gesture],
        }

    def set_sensitivity(self, sensitivity: int):
        if sensitivity == 1:
            self.tap_time = 600
            self.tap_distance = 150
            self.hold_time = 50
        elif sensitivity == 2:
            self.tap_time = 300
            self.tap_distance = 75
        else:
            self.tap_time = 150
            self.tap_distance = 50

    def toBytes(self) -> Tuple[bytes, bytes, bytes]:
        cfg1 = struct.pack(self.FORMAT_CFG1,
            BLECommandWord.UPDATE_TOUCH1.value,
            16,
            self.swipe_initial_time,
            self.swipe_initial_distance,
            self.swipe_consecutive_time,
            self.swipe_consecutive_distance,
            self.swipe_angle,
            self.scroll_initial_distance,
            self.scroll_angle,
            self.zoom_initial_distance,
            self.zoom_consecutive_distance,
            0
        )

        cfg2 = struct.pack(self.FORMAT_CFG2,
            BLECommandWord.UPDATE_TOUCH2.value,
            8,
            self.tap_time,
            self.tap_distance,
            self.hold_time,
            reduce(operator.ior, [g.value for g in self.one_finger_gesture]) if self.one_finger_gesture else 0,
            reduce(operator.ior, [g.value for g in self.two_finger_gesture]) if self.two_finger_gesture else 0,
            0,
            0,
            0,
            0,
            0,
        )

        save = struct.pack(self.FORMAT_CMD, BLECommandWord.WRITE_TOUCH.value,1,0,0,0,0,0,0,0,0,0)
        return cfg1, cfg2, save

    def update(self, cfg1: bytes, cfg2: bytes):
        word_cfg1, length_cfg1, *data_cfg1 = struct.unpack(self.FORMAT_CFG1, cfg1)
        word_cfg2, length_cfg2, *data_cfg2 = struct.unpack(self.FORMAT_CFG2, cfg2)

        if BLECommandWord(word_cfg1) != BLECommandWord.UPDATE_TOUCH1 or \
            BLECommandWord(word_cfg2) != BLECommandWord.UPDATE_TOUCH2 or \
            length_cfg1 != 16 or \
            length_cfg2 != 8:
            return False

        self.swipe_initial_time = data_cfg1[0]
        self.swipe_initial_distance = data_cfg1[1]
        self.swipe_consecutive_time = data_cfg1[2]
        self.swipe_consecutive_distance = data_cfg1[3]
        self.swipe_angle = data_cfg1[4]
        self.scroll_initial_distance = data_cfg1[5]
        self.scroll_angle = data_cfg1[6]
        self.zoom_initial_distance = data_cfg1[7]
        self.zoom_consecutive_distance = data_cfg1[8]
        self.tap_time = data_cfg2[0]
        self.tap_distance = data_cfg2[1]
        self.hold_time = data_cfg2[2]
        self.one_finger_gesture = [g for g in OneFingerGesture if bool(g.value & data_cfg2[3])]
        self.two_finger_gesture = [g for g in TwoFingerGesture if bool(g.value & data_cfg2[4])]

        return True
     

@dataclass
class TSkinConfig:
    address: str
    hand: Hand
    name: str = "Tactigon"
    touch_config: Optional[TouchConfig] = None
    gesture_config: Optional[GestureConfig] = None

    @classmethod
    def FromJSON(cls, json: dict):
        return cls(
            json["address"], 
            Hand(json["hand"]),
            json["name"] if "name" in json else cls.name,
            TouchConfig.FromJSON(json["touch_config"]) if "touch_config" in json and json["touch_config"] is not None else None,
            GestureConfig.FromJSON(json["gesture_config"]) if "gesture_config" in json and json["gesture_config"] is not None else None,
        )
    
    def toJSON(self) -> dict:
        return {
            "address": self.address,
            "hand": self.hand.value,
            "name": self.name,
            "touch_config": self.touch_config.toJSON() if self.touch_config else None,
            "gesture_config": self.gesture_config.toJSON() if self.gesture_config else None,
        }
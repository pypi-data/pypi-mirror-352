from enum import Enum
import logging
from typing import Any, Callable, Dict, List, Optional


class PulsarActuator:

    class Mode(Enum):
        FVI = 0x02
        OPEN_LOOP = 0x03
        DVI = 0x04  # field oriented voltage injection
        TORQUE = 0x05
        SPEED = 0x06
        POSITION = 0x07
        IMPEDANCE = 0x08

    class Rates(Enum):
        DISABLED = 0
        RATE_1KHZ = 10
        RATE_100HZ = 100
        RATE_50HZ = 200
        RATE_10HZ = 1_000
        RATE_5HZ = 2_000
        RATE_2HZ = 5_000
        RATE_1HZ = 10_000

    class TorquePerformance(Enum):
        AGGRESSIVE = 1
        BALANCED = 2
        SOFT = 3

    class SpeedPerformance(Enum):
        AGGRESSIVE = 1
        BALANCED = 2
        SOFT = 3
        CUSTOM = 4

    class _PCP_Actions(Enum):
        START = 0x01
        STOP = 0x02
        CHANGE_MODE = 0x03  # follow by enum PCP_actuator_mode
        CHANGE_SETPOINT = 0x04  # follow by float32
        SET_FEEDBACK_HIGH_RATE = 0x06
        SET_FEEDBACK_HIGH_ITEMS = 0x07  # follow by the items
        SET_FEEDBACK_LOW_RATE = 0x08
        SET_FEEDBACK_LOW_ITEMS = 0x09  # follow by the items
        RESET_ENCODER_POSITION = 0x0A
        SET_PARAMETERS = 0x0B
        GET_PARAMETERS = 0x0C
        SET_TORQUE_PERFORMANCE = 0x0D
        SET_SPEED_PERFORMANCE = 0x0E
        START_SINE_REF = 0x38
        SAVE = 0x39  # save current values in flash
        PING = 0x40
        ENTER_BOOTLOADER = 0xC1
        DEBUG_CLEAR_CONFIG = 0xC2
        DEBUG_RESET_INT_ENC = 0xC3

    class PCP_Parameters(Enum):
        K_DAMPING = 0x01
        K_STIFFNESS = 0x02
        TORQUE_FF = 0x03
        LIM_TORQUE = 0x04
        LIM_POSITION_MAX = 0x05
        LIM_POSITION_MIN = 0x06
        LIM_SPEED_MAX = 0x07
        LIM_SPEED_MIN = 0x08
        PROFILE_POSITION_MAX = 0x09
        PROFILE_POSITION_MIN = 0x0A
        PROFILE_SPEED_MAX = 0x0B
        PROFILE_SPEED_MIN = 0x0C
        KP_SPEED = 0x0D
        KI_SPEED = 0x0E
        KP_POSITION = 0x0F
        MODE = 0x30  # only for read, must be set via CHANGE_MODE
        SETPOINT = 0x31
        TORQUE_PERFORMANCE = 0x40
        SPEED_PERFORMANCE = 0x41
        PROFILE_SPEED_MAX_RAD_S = 0x42
        PROFILE_TORQUE_MAX_NM = 0x43
        FIRMWARE_VERSION = 0x80
        PCP_ADDRESS = 0x81
        STM32_SERIAL_NUMBER = 0x82
        DEVICE_MODEL = 0x83

    class PCP_Items(Enum):
        ENCODER_INT = 0x41
        ENCODER_INT_RAW = 0x42
        ENCODER_EXT = 0x43
        ENCODER_EXT_RAW = 0x44
        SPEED_FB = 0x45
        IA = 0x46
        IB = 0x47
        IC = 0x48
        TORQUE_SENS = 0x49
        TORQUE_SENS_RAW = 0x4A
        POSITION_REF = 0x4B
        POSITION_FB = 0x4C
        SPEED_REF = 0x4D
        ID_REF = 0x4F
        ID_FB = 0x50
        IQ_REF = 0x51
        IQ_FB = 0x52
        VD_REF = 0x53
        VQ_REF = 0x54
        TORQUE_REF = 0x55
        TORQUE_FB = 0x56
        ERRORS_ENCODER_INT = 0x60
        ERRORS_ENCODER_EXT = 0x61
        ERRORS_OVERRUN = 0x62
        VBUS = 0x70
        TEMP_PCB = 0x71
        TEMP_MOTOR = 0x72

    class _PCP_Other(Enum):
        BEACON = 0x80
        ERRORS = 0x82
        PARAMETERS = 0x83

    def __init__(self, canbus_handler: Any, address: int, logger: Optional[logging.Logger] = None) -> None: ...
    def connect(self, timeout: float = 1.0) -> bool: ...
    def set_feedback_callback(self, callback: Callable[[Any], None]) -> None: ...
    def disconnect(self) -> None: ...
    def get_feedback(self) -> Dict[Any, Any]: ...
    def send_ping(self, timeout: float = 1.0) -> bool: ...
    def changeAddress(self, new_address: int) -> None: ...
    def start(self) -> None: ...
    def stop(self) -> None: ...
    def change_mode(self, mode: 'PulsarActuator.Mode') -> None: ...
    def change_setpoint(self, setpoint: float) -> None: ...
    def save_config(self) -> None: ...
    def setHighFreqFeedbackItems(self, items: List['PulsarActuator.PCP_Items']) -> None: ...
    def setHighFreqFeedbackRate(self, rate: 'PulsarActuator.Rates') -> None: ...
    def setLowFreqFeedbackItems(self, items: List['PulsarActuator.PCP_Items']) -> None: ...
    def setLowFreqFeedbackRate(self, rate: 'PulsarActuator.Rates') -> None: ...
    def reset_encoder_position(self) -> None: ...
    def enter_bootloader(self) -> None: ...
    def set_parameters(self, parameters: Dict['PulsarActuator.PCP_Parameters', float]) -> None: ...
    def get_parameters(self, parameters: List['PulsarActuator.PCP_Parameters'], timeout: float = 1.0) -> Dict['PulsarActuator.PCP_Parameters', float]: ...
    def get_parameters_all(self) -> Dict['PulsarActuator.PCP_Parameters', float]: ...
    def set_torque_performance(self, performance: 'PulsarActuator.TorquePerformance') -> None: ...
    def set_speed_performance(self, performance: 'PulsarActuator.SpeedPerformance') -> None: ...


class PulsarActuatorScanner(PulsarActuator):
    def __init__(self, canbus_handler: Any, logger: Optional[logging.Logger] = None) -> None: ...
    def scan(self, begin: int = 0x0001, end: int = 0x3FFE) -> List[int]: ...

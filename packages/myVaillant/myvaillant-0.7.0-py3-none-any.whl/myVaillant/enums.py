from __future__ import annotations

from enum import EnumMeta, Enum


class myVaillantEnumMeta(EnumMeta):
    def __contains__(cls, item):
        try:
            cls(item)
        except ValueError:
            return False
        else:
            return True


class myVaillantEnum(str, Enum, metaclass=myVaillantEnumMeta):
    def __str__(self):
        """
        Return 'HOUR' instead of 'DeviceDataBucketResolution.HOUR'
        """
        return self.value

    @property
    def display_value(self) -> str:
        return self.value.replace("_", " ").title()


class ControlIdentifier(myVaillantEnum):
    TLI = "tli"
    VRC700 = "vrc700"

    @property
    def is_vrc700(self) -> bool:
        return self == ControlIdentifier.VRC700


class CircuitState(myVaillantEnum):
    HEATING = "HEATING"
    COOLING = "COOLING"
    STANDBY = "STANDBY"


class DeviceDataBucketResolution(myVaillantEnum):
    HOUR = "HOUR"
    DAY = "DAY"
    MONTH = "MONTH"


class ZoneOperatingMode(myVaillantEnum):
    MANUAL = "MANUAL"
    TIME_CONTROLLED = "TIME_CONTROLLED"
    OFF = "OFF"


class ZoneOperatingModeVRC700(myVaillantEnum):
    DAY = "DAY"
    AUTO = "AUTO"
    SET_BACK = "SET_BACK"
    OFF = "OFF"


class ZoneCurrentSpecialFunction(myVaillantEnum):
    NONE = "NONE"
    QUICK_VETO = "QUICK_VETO"
    HOLIDAY = "HOLIDAY"
    SYSTEM_OFF = "SYSTEM_OFF"
    VENTILATION_BOOST = "VENTILATION_BOOST"
    ONE_DAY_BANK_HOLIDAY = "ONE_DAY_BANK_HOLIDAY"


class ZoneHeatingState(myVaillantEnum):
    IDLE = "IDLE"
    HEATING_UP = "HEATING_UP"
    COOLING_DOWN = "COOLING_DOWN"


class ZoneOperatingType(myVaillantEnum):
    HEATING = "heating"
    COOLING = "cooling"


class DHWCurrentSpecialFunction(myVaillantEnum):
    CYLINDER_BOOST = "CYLINDER_BOOST"
    HOLIDAY = "HOLIDAY"
    REGULAR = "REGULAR"
    SYSTEM_OFF = "SYSTEM_OFF"


class DHWCurrentSpecialFunctionVRC700(myVaillantEnum):
    CYLINDER_BOOST = "CYLINDER_BOOST"
    HOLIDAY = "HOLIDAY"
    BANK_HOLIDAY = "BANK_HOLIDAY"
    ONE_DAY_BANK_HOLIDAY = "ONE_DAY_BANK_HOLIDAY"
    NONE = "NONE"


class DHWOperationMode(myVaillantEnum):
    MANUAL = "MANUAL"
    TIME_CONTROLLED = "TIME_CONTROLLED"
    OFF = "OFF"


class DHWOperationModeVRC700(myVaillantEnum):
    DAY = "DAY"
    AUTO = "AUTO"
    OFF = "OFF"


class VentilationOperationMode(myVaillantEnum):
    NORMAL = "NORMAL"
    REDUCED = "REDUCED"
    TIME_CONTROLLED = "TIME_CONTROLLED"
    OFF = "OFF"


class VentilationOperationModeVRC700(myVaillantEnum):
    """
    TODO: Other than AUTO, these are just guesses
    """

    DAY = "DAY"
    AUTO = "AUTO"
    SET_BACK = "SET_BACK"
    OFF = "OFF"
    NORMAL = "NORMAL"
    REDUCED = "REDUCED"


class VentilationFanStageType(myVaillantEnum):
    DAY = "DAY"
    NIGHT = "NIGHT"


class AmbisenseRoomOperationMode(myVaillantEnum):
    MANUAL = "MANUAL"
    OFF = "OFF"
    AUTO = "AUTO"

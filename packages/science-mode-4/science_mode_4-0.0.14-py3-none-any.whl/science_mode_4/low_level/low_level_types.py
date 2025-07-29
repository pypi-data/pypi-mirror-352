"""Provides low level types"""

from enum import IntEnum


class LowLevelResult(IntEnum):
    """Represent low level type for result"""
    SUCCESSFUL = 0
    TRANSFER_ERROR = 1
    PARAMETER_ERROR = 2
    TIMEOUT_STIMULATION = 3


class LowLevelMode(IntEnum):
    """Represent low level type for measurement"""
    NO_MEASUREMENT = 0
    STIM_CURRENT = 1
    STIM_VOLTAGE = 2
    HIGH_VOLTAGE_SOURCE = 3


class LowLevelHighVoltageSource(IntEnum):
    """Represent low level high voltage source"""
    STANDARD = 0
    OFF = 1

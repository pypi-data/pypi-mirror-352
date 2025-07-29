"""Provides common types"""

from enum import IntEnum


class Channel(IntEnum):
    """Represents a channel"""
    RED = 0
    BLUE = 1
    BLACK = 2
    WHITE = 3


class Connector(IntEnum):
    """Represents a cable connector"""
    YELLOW = 0
    GREEN = 1


class ResultAndError(IntEnum):
    """Represents science mode type ResultAndError"""
    NO_ERROR = 0
    TRANSFER_ERROR = 1
    PARAMETER_ERROR = 2
    NOT_INITIALIZED = 7
    ELECTRODE_ERROR = 10
    PULSE_TIMEOUT_ERROR = 16
    PULSE_LOW_CURRENT_ERROR = 28


class StimStatus(IntEnum):
    """Represents science mode type StimStatus"""
    NO_LEVEL_INITIALIZED = 0
    LOW_LEVEL_INITIALIZED = 1
    MID_LEVEL_INITIALIZED = 2
    MID_LEVEL_RUNNING = 3

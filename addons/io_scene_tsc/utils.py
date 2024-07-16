"""Utility classes and functions."""

import bpy_extras
import enum


BONE_ROTATION_OFFSET = bpy_extras.io_utils.axis_conversion(
    from_forward='Y',
    from_up='X',
    to_forward='X',
    to_up='Y',
).to_4x4()


class FileReadError(Exception):
    """General purpose file read error."""


class GameType(enum.Enum):
    """Game Type."""

    THESIMS = 0
    THESIMSBUSTINOUT = 1
    THEURBZ = 2
    THESIMS2 = 3
    THESIMS2PETS = 4
    THESIMS2CASTAWAY = 5

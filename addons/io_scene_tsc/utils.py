"""Utility classes and functions."""

import bpy_extras
import enum
import struct
import typing


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


def read_null_terminated_string(file: typing.BinaryIO) -> str:
    """Read a null terminated string from a file."""
    string_bytes = bytearray()
    while True:
        byte = struct.unpack('B', file.read(1))
        if byte[0] == 0:
            break
        string_bytes.extend(byte)

    return string_bytes.decode('ascii')

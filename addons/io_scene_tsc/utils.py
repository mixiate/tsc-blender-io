"""Utility classes and functions."""

import enum


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

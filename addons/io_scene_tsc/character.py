"""Read character files."""

import dataclasses
import mathutils
import pathlib
import struct
import typing


from . import utils


@dataclasses.dataclass
class Bone:
    """Bone."""

    name: str
    children: list[int]
    translation: mathutils.Vector
    rotation: mathutils.Quaternion
    matrix: mathutils.Matrix
    matrix_inverse: mathutils.Matrix


def read_bone(file: typing.BinaryIO, endianness: str) -> Bone:
    """Read a bone."""
    file.read(4)

    children_count = struct.unpack(endianness + 'I', file.read(4))[0]

    children = [struct.unpack(endianness + 'I', file.read(4))[0] for _ in range(children_count)]

    translation = mathutils.Vector(struct.unpack(endianness + '3f', file.read(12)))

    rotation = mathutils.Quaternion(mathutils.Vector(struct.unpack(endianness + '4f', file.read(16))).wxyz)

    file.read(1)

    matrix = mathutils.Matrix(
        (
            struct.unpack(endianness + '4f', file.read(16)),
            struct.unpack(endianness + '4f', file.read(16)),
            struct.unpack(endianness + '4f', file.read(16)),
            struct.unpack(endianness + '4f', file.read(16)),
        ),
    )

    matrix_inverse = mathutils.Matrix(
        (
            struct.unpack(endianness + '4f', file.read(16)),
            struct.unpack(endianness + '4f', file.read(16)),
            struct.unpack(endianness + '4f', file.read(16)),
            struct.unpack(endianness + '4f', file.read(16)),
        ),
    )

    name = utils.read_null_terminated_string(file)

    return Bone(name, children, translation, rotation, matrix, matrix_inverse)


@dataclasses.dataclass
class Character:
    """Character."""

    name: str
    bones: list[Bone]


def read_the_sims_character(file: typing.BinaryIO, endianness: str) -> Character:
    """Read The Sims character."""
    name = utils.read_null_terminated_string(file)

    bone_count = struct.unpack(endianness + 'I', file.read(4))[0]

    bones = [read_bone(file, endianness) for _ in range(bone_count)]

    file.read(20)

    return Character(name, bones)


def read_the_sims_2_character(file: typing.BinaryIO, endianness: str) -> Character:
    """Read The Sims 2 character."""
    file.read(16)

    name = utils.read_null_terminated_string(file)

    file.read(4)

    bone_count = struct.unpack(endianness + 'I', file.read(4))[0]

    bones = [read_bone(file, endianness) for _ in range(bone_count)]

    file.read(20)

    return Character(name, bones)


def read_file(file_path: pathlib.Path, game_type: utils.GameType, endianness: str) -> Character:
    """Read a character file."""
    try:
        with file_path.open(mode='rb') as file:
            character = None
            match game_type:
                case utils.GameType.THESIMS:
                    character = read_the_sims_character(file, endianness)
                case utils.GameType.THESIMSBUSTINOUT:
                    character = read_the_sims_character(file, endianness)
                case utils.GameType.THEURBZ:
                    character = read_the_sims_character(file, endianness)
                case utils.GameType.THESIMS2:
                    character = read_the_sims_2_character(file, endianness)
                case utils.GameType.THESIMS2PETS:
                    character = read_the_sims_2_character(file, endianness)
                case utils.GameType.THESIMS2CASTAWAY:
                    character = read_the_sims_2_character(file, endianness)

            if character is None or len(file.read(1)) != 0:
                raise utils.FileReadError

            return character

    except (OSError, struct.error) as exception:
        raise utils.FileReadError from exception

"""Read animation files."""

import dataclasses
import mathutils
import pathlib
import struct
import typing


from . import utils


@dataclasses.dataclass
class Bone:
    """Bone."""

    rotation: mathutils.Quaternion
    scale: mathutils.Vector
    location: mathutils.Vector


def read_the_sims_bone(file: typing.BinaryIO, endianness: str, data: list[float]) -> Bone:
    """Read The Sims bone."""
    rotation_index = struct.unpack(endianness + 'i', file.read(4))[0]
    scale_index = struct.unpack(endianness + 'i', file.read(4))[0]
    location_index = struct.unpack(endianness + 'i', file.read(4))[0]

    rotation = mathutils.Quaternion((1.0, 0.0, 0.0, 0.0))
    scale = mathutils.Vector((1.0, 1.0, 1.0))
    location = mathutils.Vector((0.0, 0.0, 0.0))

    if rotation_index > 0:
        rotation = mathutils.Quaternion(
            (data[rotation_index + 3], data[rotation_index], data[rotation_index + 1], data[rotation_index + 2]),
        )
    if scale_index > 0:
        scale = mathutils.Vector((data[scale_index], data[scale_index + 1], data[scale_index + 2]))
    if location_index > 0:
        location = mathutils.Vector((data[location_index], data[location_index + 1], data[location_index + 2]))

    return Bone(rotation, scale, location)


def read_the_sims_bustin_out_bone(file: typing.BinaryIO, endianness: str, data: list[float]) -> Bone:
    """Read The Sims Bustin' Out bone."""
    rotation_index = struct.unpack(endianness + 'i', file.read(4))[0]
    scale_index = struct.unpack(endianness + 'i', file.read(4))[0]
    location_index = struct.unpack(endianness + 'i', file.read(4))[0]

    file.read(16)

    rotation = mathutils.Quaternion((1.0, 0.0, 0.0, 0.0))
    scale = mathutils.Vector((1.0, 1.0, 1.0))
    location = mathutils.Vector((0.0, 0.0, 0.0))

    if rotation_index > 0:
        rotation = mathutils.Quaternion(
            (data[rotation_index + 3], data[rotation_index], data[rotation_index + 1], data[rotation_index + 2]),
        )
    if scale_index > 0:
        scale = mathutils.Vector((data[scale_index], data[scale_index + 1], data[scale_index + 2]))
    if location_index > 0:
        location = mathutils.Vector((data[location_index], data[location_index + 1], data[location_index + 2]))

    return Bone(rotation, scale, location)


def read_the_urbz_bone(file: typing.BinaryIO, endianness: str, data: list[float]) -> Bone:
    """Read The Urbz bone."""
    rotation_index = struct.unpack(endianness + 'i', file.read(4))[0]
    scale_index = struct.unpack(endianness + 'i', file.read(4))[0]
    location_index = struct.unpack(endianness + 'i', file.read(4))[0]

    file.read(20)

    rotation = mathutils.Quaternion((1.0, 0.0, 0.0, 0.0))
    scale = mathutils.Vector((1.0, 1.0, 1.0))
    location = mathutils.Vector((0.0, 0.0, 0.0))

    if rotation_index > 0:
        rotation = mathutils.Quaternion(
            (data[rotation_index + 3], data[rotation_index], data[rotation_index + 1], data[rotation_index + 2]),
        )
    if scale_index > 0:
        scale = mathutils.Vector((data[scale_index], data[scale_index + 1], data[scale_index + 2]))
    if location_index > 0:
        location = mathutils.Vector((data[location_index], data[location_index + 1], data[location_index + 2]))

    return Bone(rotation, scale, location)


@dataclasses.dataclass
class Animation:
    """Animation."""

    name: str
    bones: list[Bone]


def read_the_sims_animation(file: typing.BinaryIO, endianness: str) -> Animation:
    """Read The Sims animation."""
    name = ''.join(iter(lambda: file.read(1).decode('ascii'), '\x00'))

    file.read(28)

    bone_count = struct.unpack(endianness + 'I', file.read(4))[0]
    bone_file_position = file.tell()

    file.seek(bone_file_position + (bone_count * 12) + 4)
    float_count = struct.unpack(endianness + 'I', file.read(4))[0]
    floats = [struct.unpack(endianness + 'f', file.read(4))[0] for _ in range(float_count)]

    file.seek(bone_file_position)

    bones = [read_the_sims_bone(file, endianness, floats) for _ in range(bone_count)]

    return Animation(name, bones)


def read_the_sims_bustin_out_animation(file: typing.BinaryIO, endianness: str) -> Animation:
    """Read The Sims Bustin' Out animation."""
    name = ''.join(iter(lambda: file.read(1).decode('ascii'), '\x00'))

    file.read(28)

    bone_count = struct.unpack(endianness + 'I', file.read(4))[0]
    bone_file_position = file.tell()

    file.seek(bone_file_position + (bone_count * 28) + 4)
    float_count = struct.unpack(endianness + 'I', file.read(4))[0]
    floats = [struct.unpack(endianness + 'f', file.read(4))[0] for _ in range(float_count)]

    file.seek(bone_file_position)

    bones = [read_the_sims_bustin_out_bone(file, endianness, floats) for _ in range(bone_count)]

    return Animation(name, bones)


def read_the_urbz_animation(file: typing.BinaryIO, endianness: str) -> Animation:
    """Read The Urbz animation."""
    file.read(16)
    file.read(4)

    name = ''.join(iter(lambda: file.read(1).decode('ascii'), '\x00'))

    file.read(28)

    bone_count = struct.unpack(endianness + 'I', file.read(4))[0]
    bone_file_position = file.tell()

    file.seek(bone_file_position + (bone_count * 32) + 4)
    float_count = struct.unpack(endianness + 'I', file.read(4))[0]
    floats = [struct.unpack(endianness + 'f', file.read(4))[0] for _ in range(float_count)]

    file.seek(bone_file_position)

    bones = [read_the_urbz_bone(file, endianness, floats) for _ in range(bone_count)]

    return Animation(name, bones)


def read_the_sims_2_animation(file: typing.BinaryIO, endianness: str) -> Animation:
    """Read The Sims 2 animation."""
    file.read(16)

    name = ''.join(iter(lambda: file.read(1).decode('ascii'), '\x00'))

    file.read(32)

    bone_count = struct.unpack(endianness + 'I', file.read(4))[0]
    bone_file_position = file.tell()

    file.seek(bone_file_position + (bone_count * 32) + 4)
    float_count = struct.unpack(endianness + 'I', file.read(4))[0]
    floats = [struct.unpack(endianness + 'f', file.read(4))[0] for _ in range(float_count)]

    file.seek(bone_file_position)

    bones = [read_the_urbz_bone(file, endianness, floats) for _ in range(bone_count)]

    return Animation(name, bones)


def read_the_sims_2_pets_animation(file: typing.BinaryIO, endianness: str) -> Animation:
    """Read The Sims 2 Pets animation."""
    file.read(16)

    name = ''.join(iter(lambda: file.read(1).decode('ascii'), '\x00'))

    file.read(32)

    bone_count = struct.unpack(endianness + 'I', file.read(4))[0]
    bone_file_position = file.tell()

    file.seek(bone_file_position + (bone_count * 32) + 8)
    float_count = struct.unpack(endianness + 'I', file.read(4))[0]
    floats = [struct.unpack(endianness + 'f', file.read(4))[0] for _ in range(float_count)]

    file.seek(bone_file_position)

    bones = [read_the_urbz_bone(file, endianness, floats) for _ in range(bone_count)]

    return Animation(name, bones)


def read_file(file_path: pathlib.Path, game_type: utils.GameType, endianness: str) -> Animation:
    """Read an animation file."""
    try:
        with file_path.open(mode='rb') as file:
            match game_type:
                case utils.GameType.THESIMS:
                    return read_the_sims_animation(file, endianness)
                case utils.GameType.THESIMSBUSTINOUT:
                    return read_the_sims_bustin_out_animation(file, endianness)
                case utils.GameType.THEURBZ:
                    return read_the_urbz_animation(file, endianness)
                case utils.GameType.THESIMS2:
                    return read_the_sims_2_animation(file, endianness)
                case utils.GameType.THESIMS2PETS:
                    return read_the_sims_2_pets_animation(file, endianness)

    except (OSError, IndexError, struct.error) as exception:
        raise utils.FileReadError from exception

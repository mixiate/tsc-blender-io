"""Read The Sims, The Sims Bustin' Out, The Urbz, The Sims 2, The Sims 2 Pets and The Sims 2 Castaway model files."""

import dataclasses
import enum
import mathutils
import pathlib
import struct
import typing


from . import utils


from .utils import GameType


FILE_MAGIC_ID = 1297040460


class FloatType(enum.Enum):
    """Model Float Type."""

    FLOAT32 = 0
    SNORM16 = 1


def snorm_to_float(input_value: int, scale: float) -> float:
    """Convert snorm to float."""
    return float(input_value) / scale


@dataclasses.dataclass
class Vertex:
    """Vertex."""

    position: tuple[float, float, float]
    unknown: int


def read_vertices(
    file: typing.BinaryIO,
    count: int,
    float_type: FloatType,
    endianness: str,
    scale: float,
) -> list[Vertex]:
    """Read vertices."""
    match float_type:
        case FloatType.FLOAT32:
            return [
                Vertex(
                    struct.unpack(endianness + '3f', file.read(4 * 3)),
                    struct.unpack(endianness + 'i', file.read(4))[0],
                )
                for _ in range(count)
            ]
        case FloatType.SNORM16:
            return [
                Vertex(
                    [snorm_to_float(x, scale) for x in struct.unpack(endianness + '3h', file.read(2 * 3))],
                    struct.unpack(endianness + 'h', file.read(2))[0],
                )
                for _ in range(count)
            ]

    raise utils.FileReadError


def read_uvs(
    file: typing.BinaryIO,
    count: int,
    float_type: FloatType,
    endianness: str,
) -> list[tuple[float, float]]:
    """Read uvs."""
    match float_type:
        case FloatType.FLOAT32:
            return [struct.unpack(endianness + '2f', file.read(8)) for _ in range(count)]

        case FloatType.SNORM16:
            return [
                [snorm_to_float(x, 4095.0) for x in struct.unpack(endianness + '2h', file.read(4))]
                for _ in range(count)
            ]

    raise utils.FileReadError


def read_double_uvs(
    file: typing.BinaryIO,
    count: int,
    float_type: FloatType,
    endianness: str,
) -> list[tuple[float, float, float, float]]:
    """Read double uvs."""
    match float_type:
        case FloatType.FLOAT32:
            return [struct.unpack(endianness + '4f', file.read(16)) for _ in range(count)]
        case FloatType.SNORM16:
            return [
                [snorm_to_float(x, 4095.0) for x in struct.unpack(endianness + '4h', file.read(8))]
                for _ in range(count)
            ]

    raise utils.FileReadError


@dataclasses.dataclass
class Mesh:
    """Mesh."""

    positions: list[Vertex]
    uvs: list[tuple[float, float]]
    uvs_2: list[tuple[float, float]]
    normals: list[tuple[float, float, float]]
    bones: list[list[int]]
    bone_weights: list[tuple[int, int, int, int]]
    indices: list[int]
    strips: list[tuple[int, int]]
    shader_id: int


MESH_FLAGS_HAS_UVS = 0b0000_0010
MESH_FLAGS_HAS_UNKNOWN = 0b0000_0100
MESH_FLAGS_HAS_NORMALS = 0b0000_1000
MESH_FLAGS_HAS_SNORM_FLOATS = 0b0001_0000
MESH_FLAGS_HAS_INDICES = 0b0010_0000
MESH_FLAGS_HAS_UVS_2 = 0b0100_0000


def read_mesh(file: typing.BinaryIO, game: GameType, endianness: str, scale: float) -> Mesh:
    """Read mesh."""
    flags = struct.unpack(endianness + 'I', file.read(4))[0]

    shader_id = struct.unpack(endianness + 'I', file.read(4))[0]

    strip_count = struct.unpack(endianness + 'I', file.read(4))[0]
    file.read(strip_count)

    if game in (GameType.THESIMSBUSTINOUT, GameType.THEURBZ, GameType.THESIMS2, GameType.THESIMS2PETS):
        file.read(4)

    if game == GameType.THESIMS2CASTAWAY:
        file.read(52)

    float_type = FloatType.SNORM16 if flags & MESH_FLAGS_HAS_SNORM_FLOATS else FloatType.FLOAT32

    positions = []
    uvs = []
    uvs_2 = []
    normals = []
    bones = []
    bone_weights = []
    indices = []
    strips = []

    previous_strip_end = 0

    strip_type = 0

    for _ in range(strip_count):
        if strip_type != 4:
            strip_type = struct.unpack(endianness + 'B', file.read(1))[0]

        match strip_type:
            case 2:
                file.read(1)
            case 4:
                marker = struct.unpack(endianness + 'B', file.read(1))[0]
                if marker == 5:
                    file.read(2)

        bone_ids = []
        read_bone_weights = False

        match strip_type:
            case 1 | 2:
                while True:
                    bone_id = struct.unpack(endianness + 'H', file.read(2))[0]
                    bone_ids.append(bone_id)
                    if struct.unpack(endianness + '2B', file.read(2))[1] == 0:
                        break

                    read_bone_weights = True
            case 4:
                bone_ids = [0, 1, 2, 3]
                read_bone_weights = True
            case _:
                bone_ids = [0]

        vertex_count = struct.unpack(endianness + 'I', file.read(4))[0]

        positions += read_vertices(file, vertex_count, float_type, endianness, scale)

        if flags & MESH_FLAGS_HAS_UVS:
            if flags & MESH_FLAGS_HAS_UVS_2:
                uv_data = read_double_uvs(file, vertex_count, float_type, endianness)
                uvs += [(x[0], x[1]) for x in uv_data]
                uvs_2 += [(x[2], x[3]) for x in uv_data]
            else:
                uvs += read_uvs(file, vertex_count, float_type, endianness)

        if flags & MESH_FLAGS_HAS_UNKNOWN:
            file.read(vertex_count * 4)

        if flags & MESH_FLAGS_HAS_NORMALS:
            normal_format, normal_size = (
                (endianness + '4b', 4)
                if game in (GameType.THESIMS2, GameType.THESIMS2PETS, GameType.THESIMS2CASTAWAY)
                else (endianness + '3b', 3)
            )
            normals_data = [struct.unpack(normal_format, file.read(normal_size)) for _ in range(vertex_count)]
            for normal_data in normals_data:
                normal = mathutils.Vector(
                    (
                        (float(normal_data[0]) + 0.5) / 127.5,
                        (float(normal_data[1]) + 0.5) / 127.5,
                        (float(normal_data[2]) + 0.5) / 127.5,
                    ),
                ).normalized()
                normals.append(normal)

        if flags & MESH_FLAGS_HAS_INDICES:
            if game in (GameType.THESIMS2PETS, GameType.THESIMS2CASTAWAY):
                file.read(4)
                file.read(1)

                start_pos = file.tell()

                indices_length = struct.unpack(endianness + 'I', file.read(4))[0]

                file.read(5)

                index_count = struct.unpack(endianness + 'H', file.read(2))[0]

                element_count = int(((indices_length - 4) / index_count) / 2)
                format_string = endianness + str(element_count) + 'H'

                indices += [struct.unpack(format_string, file.read(element_count * 2))[0] for _ in range(index_count)]

                file.seek(start_pos + indices_length + 8)

                if game == GameType.THESIMS2CASTAWAY:
                    file.read(index_count * 2)

            else:
                index_count = struct.unpack(endianness + 'I', file.read(4))[0]
                file.read(1)
                indices += [struct.unpack(endianness + 'H', file.read(2))[0] for _ in range(index_count)]
        else:
            strips.append((previous_strip_end, previous_strip_end + vertex_count))

        previous_strip_end = previous_strip_end + vertex_count

        bones += [bone_ids for _ in range(vertex_count)]

        if read_bone_weights:
            bone_weights += [struct.unpack(endianness + '4B', file.read(4)) for _ in range(vertex_count)]
        else:
            bone_weights += [(255, 255, 255, 255) for _ in range(vertex_count)]

    return Mesh(
        positions,
        uvs,
        uvs_2,
        normals,
        bones,
        bone_weights,
        indices,
        strips,
        shader_id,
    )


@dataclasses.dataclass
class SubModel:
    """SubModel."""

    meshes: list[Mesh]


def read_sub_model(file: typing.BinaryIO, game: GameType, endianness: str, scale: float) -> SubModel:
    """Read SubModel."""
    file.read(4)

    if game == GameType.THESIMS2CASTAWAY:
        unknown_count = struct.unpack(endianness + 'I', file.read(4))[0]
        for _ in range(unknown_count):
            if len(file.read(7 * 4)) == 0:
                raise utils.FileReadError

    mesh_count = struct.unpack(endianness + 'I', file.read(4))[0]

    meshes = []
    for _ in range(mesh_count):
        meshes.append(read_mesh(file, game, endianness, scale))

        marker = struct.unpack(endianness + 'B', file.read(1))[0]
        if marker != 6:
            file.read(1)

    return SubModel(meshes)


def read_unknowns(file: typing.BinaryIO, endianness: str) -> None:
    """Read unknowns."""
    count = struct.unpack(endianness + 'I', file.read(4))[0]

    for _ in range(count):
        if len(file.read(64)) != 64:
            raise utils.FileReadError


def read_bspline_volumes(file: typing.BinaryIO, endianness: str) -> None:
    """Read bspline volumes."""
    count = struct.unpack(endianness + 'I', file.read(4))[0]

    for _ in range(count):
        file.read(4)
        file.read(128)
        file.read(4)

        count_1 = struct.unpack(endianness + 'I', file.read(4))[0]
        count_2 = struct.unpack(endianness + 'I', file.read(4))[0]
        count_3 = struct.unpack(endianness + 'I', file.read(4))[0]
        count_4 = struct.unpack(endianness + 'I', file.read(4))[0]

        data_length = 12 * count_1 * count_2 * count_3 * count_4
        if len(file.read(data_length)) != data_length:
            raise utils.FileReadError


def read_dummies(file: typing.BinaryIO, endianness: str) -> None:
    """Read dummies."""
    count = struct.unpack(endianness + 'I', file.read(4))[0]

    for _ in range(count):
        if len(file.read(156)) != 156:
            raise utils.FileReadError


def read_cameras(file: typing.BinaryIO, endianness: str) -> None:
    """Read cameras."""
    count = struct.unpack(endianness + 'I', file.read(4))[0]

    for _ in range(count):
        if len(file.read(172)) != 172:
            raise utils.FileReadError


def read_light_infos(file: typing.BinaryIO, endianness: str) -> None:
    """Read light infos."""
    count = struct.unpack(endianness + 'I', file.read(4))[0]

    for _ in range(count):
        if len(file.read(28)) != 28:
            raise utils.FileReadError


@dataclasses.dataclass
class Model:
    """Model."""

    name: str
    sub_models: list[SubModel]
    game: GameType
    endianness: str


def read_model(file: typing.BinaryIO) -> Model:
    """Read a model."""
    match struct.unpack('<I', file.read(4))[0]:
        case 0x00:
            endianness, game_type = '<', GameType.THESIMS
        case 0x01:
            endianness, game_type = '<', GameType.THESIMSBUSTINOUT
        case 0x35:
            endianness, game_type = '<', GameType.THEURBZ
        case 0x3A:
            endianness, game_type = '<', GameType.THESIMS2
        case 0x3E:
            endianness, game_type = '<', GameType.THESIMS2PETS
        case 0x3E000000:
            endianness, game_type = '>', GameType.THESIMS2PETS
        case 0x45000000:
            endianness, game_type = '>', GameType.THESIMS2CASTAWAY
        case _:
            raise utils.FileReadError

    match game_type:
        case GameType.THESIMS | GameType.THESIMSBUSTINOUT:
            file.read(2)
        case GameType.THEURBZ:
            file.read(16)
        case GameType.THESIMS2 | GameType.THESIMS2PETS | GameType.THESIMS2CASTAWAY:
            if struct.unpack(endianness + 'I', file.read(4))[0] != FILE_MAGIC_ID:
                raise utils.FileReadError

            if struct.unpack(endianness + 'i', file.read(4))[0] != -1:
                raise utils.FileReadError

            file.read(4)  # name length

    name = utils.read_null_terminated_string(file)

    match game_type:
        case GameType.THESIMSBUSTINOUT:
            file.read(16)
        case GameType.THEURBZ:
            file.read(53)
        case GameType.THESIMS2 | GameType.THESIMS2PETS | GameType.THESIMS2CASTAWAY:
            file.read(57)

    match game_type:
        case GameType.THESIMSBUSTINOUT:
            read_light_infos(file, endianness)
        case GameType.THEURBZ | GameType.THESIMS2 | GameType.THESIMS2PETS | GameType.THESIMS2CASTAWAY:
            read_unknowns(file, endianness)
            read_bspline_volumes(file, endianness)
            read_dummies(file, endianness)
            read_cameras(file, endianness)
            read_light_infos(file, endianness)

    file.read(1)

    scale = 1.0 / struct.unpack(endianness + 'f', file.read(4))[0]

    sub_model_count = struct.unpack(endianness + 'I', file.read(4))[0]

    sub_models = [read_sub_model(file, game_type, endianness, scale) for _ in range(sub_model_count)]

    if len(file.read(64)) != 64:
        raise utils.FileReadError

    match game_type:
        case GameType.THESIMS | GameType.THESIMSBUSTINOUT | GameType.THEURBZ:
            footer_length = 8
        case GameType.THESIMS2 | GameType.THESIMS2PETS:
            footer_length = 4
        case GameType.THESIMS2CASTAWAY:
            footer_length = 7

    if len(file.read(footer_length)) != footer_length:
        raise utils.FileReadError

    return Model(
        name,
        sub_models,
        game_type,
        endianness,
    )


def read_file(file_path: pathlib.Path) -> Model:
    """Read a model file."""
    try:
        with file_path.open(mode='rb') as file:
            model = read_model(file)

            if len(file.read(1)) != 0:
                raise utils.FileReadError

            return model

    except (OSError, struct.error) as exception:
        raise utils.FileReadError from exception

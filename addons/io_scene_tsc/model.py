"""Read model files."""

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


def read_positions(
    file: typing.BinaryIO,
    count: int,
    float_type: FloatType,
    endianness: str,
    scale: float,
    element_count: int,
) -> list[Vertex]:
    """Read vertices."""
    match float_type:
        case FloatType.FLOAT32:
            match element_count:
                case 3:
                    return [
                        Vertex(
                            struct.unpack(endianness + '3f', file.read(4 * 3)),
                            0,
                        )
                        for _ in range(count)
                    ]
                case 4:
                    return [
                        Vertex(
                            struct.unpack(endianness + '3f', file.read(4 * 3)),
                            struct.unpack(endianness + 'i', file.read(4))[0],
                        )
                        for _ in range(count)
                    ]
        case FloatType.SNORM16:
            match element_count:
                case 3:
                    return [
                        Vertex(
                            [snorm_to_float(x, scale) for x in struct.unpack(endianness + '3h', file.read(2 * 3))],
                            0,
                        )
                        for _ in range(count)
                    ]
                case 4:
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
    colors: list[tuple[int, int, int, int]]
    bones: list[list[int]]
    bone_weights: list[tuple[int, int, int, int]]
    indices: list[int]
    indices_normals: list[int]
    indices_colors: list[int]
    indices_uvs: list[int]
    strips: list[tuple[int, int]]
    shader_id: int


MESH_FLAGS_HAS_UVS = 0b0000_0010
MESH_FLAGS_HAS_COLORS = 0b0000_0100
MESH_FLAGS_HAS_NORMALS = 0b0000_1000
MESH_FLAGS_HAS_SNORM_FLOATS = 0b0001_0000
MESH_FLAGS_HAS_INDICES = 0b0010_0000
MESH_FLAGS_HAS_UVS_2 = 0b0100_0000
MESH_FLAGS_HAS_MORPH_DELTAS = 0b1_0000_0000
MESH_FLAGS_HAS_SEPARATE_COUNTS = 0b10_0000_0000


def read_mesh(file: typing.BinaryIO, version: int, endianness: str, scale: float) -> Mesh:
    """Read mesh."""
    flags = struct.unpack(endianness + 'I', file.read(4))[0]

    shader_id = struct.unpack(endianness + 'I', file.read(4))[0]

    strip_count = struct.unpack(endianness + 'I', file.read(4))[0]
    file.read(strip_count)

    if version >= 0x01:
        file.read(4)

    if version >= 0x45:
        file.read(48)

    float_type = FloatType.SNORM16 if flags & MESH_FLAGS_HAS_SNORM_FLOATS else FloatType.FLOAT32

    positions = []
    uvs = []
    uvs_2 = []
    normals = []
    colors = []
    bones = []
    bone_weights = []
    indices = []
    indices_normals = []
    indices_colors = []
    indices_uvs = []
    strips = []

    previous_strip_end = 0

    bone_count = 0
    bone_ids = [0, 1, 2, 3]
    read_bone_weights = False
    reset_bone_count = True

    while True:
        command = struct.unpack(endianness + 'B', file.read(1))[0]
        match command:
            case 0:
                position_count = struct.unpack(endianness + 'I', file.read(4))[0]

                if flags & MESH_FLAGS_HAS_SEPARATE_COUNTS:
                    element_count = 3
                    normal_count = struct.unpack(endianness + 'I', file.read(4))[0]
                    color_count = struct.unpack(endianness + 'I', file.read(4))[0]
                    uv_count = struct.unpack(endianness + 'I', file.read(4))[0]
                else:
                    element_count = 4
                    normal_count = position_count
                    color_count = position_count
                    uv_count = position_count

                positions += read_positions(file, position_count, float_type, endianness, scale, element_count)

                if flags & MESH_FLAGS_HAS_UVS:
                    if flags & MESH_FLAGS_HAS_UVS_2:
                        uv_data = read_double_uvs(file, uv_count, float_type, endianness)
                        uvs += [(x[0], x[1]) for x in uv_data]
                        uvs_2 += [(x[2], x[3]) for x in uv_data]
                    else:
                        uvs += read_uvs(file, uv_count, float_type, endianness)

                if flags & MESH_FLAGS_HAS_COLORS:
                    colors += [struct.unpack(endianness + '4B', file.read(4)) for _ in range(color_count)]

                if flags & MESH_FLAGS_HAS_NORMALS:
                    normal_format, normal_size = (
                        (endianness + '4b', 4) if version >= 0x3A and element_count == 4 else (endianness + '3b', 3)
                    )
                    normals_data = [struct.unpack(normal_format, file.read(normal_size)) for _ in range(normal_count)]
                    for normal_data in normals_data:
                        normal = mathutils.Vector(
                            (
                                float(normal_data[0]) / 127.0,
                                float(normal_data[1]) / 127.0,
                                float(normal_data[2]) / 127.0,
                            ),
                        ).normalized()
                        normals.append(normal)

                bones += [bone_ids[: max(bone_count, 1)] for _ in range(position_count)]

                if read_bone_weights:
                    bone_weights += [struct.unpack(endianness + '4B', file.read(4)) for _ in range(position_count)]
                else:
                    bone_weights += [(255, 255, 255, 255) for _ in range(position_count)]

                if flags & MESH_FLAGS_HAS_MORPH_DELTAS:
                    file.read(position_count * 32)

                if flags & MESH_FLAGS_HAS_INDICES:
                    if endianness == '>':
                        unknown_count = struct.unpack(endianness + 'I', file.read(4))[0]
                        channel_count = struct.unpack(endianness + 'B', file.read(1))[0]

                        indices_data_length = struct.unpack(endianness + 'I', file.read(4))[0]

                        file.read(4)
                        indices_data_start_pos = file.tell()
                        file.read(1)

                        index_count = struct.unpack(endianness + 'H', file.read(2))[0]

                        format_string = endianness + str(channel_count) + 'H'

                        indices_data = [
                            struct.unpack(format_string, file.read(channel_count * 2)) for _ in range(index_count)
                        ]
                        indices_data = list(map(list, zip(*indices_data)))
                        match channel_count:
                            case 3:
                                indices += indices_data[0]
                                indices_normals += indices_data[1]
                                indices_uvs += indices_data[2]
                            case 4:
                                indices += indices_data[0]
                                indices_normals += indices_data[1]
                                indices_colors += indices_data[2]
                                indices_uvs += indices_data[3]
                            case _:
                                raise utils.FileReadError

                        file.seek(indices_data_start_pos + indices_data_length)

                        read_unknown = True
                        if version >= 0x4A:
                            read_unknown = struct.unpack(endianness + 'B', file.read(1))[0] != 0

                        if version >= 0x45 and read_unknown:
                            file.read(unknown_count * 2)

                    else:
                        index_count = struct.unpack(endianness + 'I', file.read(4))[0]
                        file.read(1)
                        indices += [struct.unpack(endianness + 'H', file.read(2))[0] for _ in range(index_count)]
                else:
                    strips.append((previous_strip_end, previous_strip_end + position_count))

                previous_strip_end = previous_strip_end + position_count

                if reset_bone_count:
                    bone_count = 0
            case 1:
                bone_id = struct.unpack(endianness + 'H', file.read(2))[0]
                bone_index = struct.unpack(endianness + 'B', file.read(1))[0]
                bone_ids[bone_index] = bone_id
                bone_count += 1
            case 2:
                read_bone_weights = True
            case 3:
                read_bone_weights = False
            case 4:
                bone_count = 4
                read_bone_weights = True
                reset_bone_count = False
            case 5:
                read_bone_weights = False
            case 6:
                break

    return Mesh(
        positions,
        uvs,
        uvs_2,
        normals,
        colors,
        bones,
        bone_weights,
        indices,
        indices_normals,
        indices_colors,
        indices_uvs,
        strips,
        shader_id,
    )


@dataclasses.dataclass
class SubModel:
    """SubModel."""

    main_mesh: Mesh | None
    meshes: list[Mesh]


def read_sub_model(file: typing.BinaryIO, version: int, endianness: str, scale: float) -> SubModel:
    """Read SubModel."""
    file.read(4)

    if version >= 0x45:
        unknown_count = struct.unpack(endianness + 'I', file.read(4))[0]
        for _ in range(unknown_count):
            if len(file.read(7 * 4)) == 0:
                raise utils.FileReadError

    main_mesh = None

    if version >= 0x4A and struct.unpack(endianness + 'B', file.read(1))[0] != 0:
        main_mesh = read_mesh(file, version, endianness, scale)

    mesh_count = struct.unpack(endianness + 'I', file.read(4))[0]

    meshes = [read_mesh(file, version, endianness, scale) for _ in range(mesh_count)]

    return SubModel(main_mesh, meshes)


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


def read_light_info_exs(file: typing.BinaryIO, endianness: str) -> None:
    """Read light info exs."""
    count = struct.unpack(endianness + 'I', file.read(4))[0]

    for _ in range(count):
        if len(file.read(125)) != 125:
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
            version, endianness, game_type = 0x00, '<', GameType.THESIMS
        case 0x01:
            version, endianness, game_type = 0x01, '<', GameType.THESIMSBUSTINOUT
        case 0x00000100:
            version, endianness, game_type = 0x01, '>', GameType.THESIMSBUSTINOUT
        case 0x35:
            version, endianness, game_type = 0x35, '<', GameType.THEURBZ
        case 0x3A:
            version, endianness, game_type = 0x3A, '<', GameType.THESIMS2
        case 0x3E:
            version, endianness, game_type = 0x3E, '<', GameType.THESIMS2PETS
        case 0x3E000000:
            version, endianness, game_type = 0x3E, '>', GameType.THESIMS2PETS
        case 0x45000000:
            version, endianness, game_type = 0x45, '>', GameType.THESIMS2CASTAWAY
        case 0x48000000:
            version, endianness, game_type = 0x48, '>', GameType.THESIMS3
        case 0x4A000000:
            version, endianness, game_type = 0x4A, '>', GameType.THESIMS3
        case _:
            raise utils.FileReadError

    match game_type:
        case GameType.THESIMS | GameType.THESIMSBUSTINOUT:
            file.read(2)
        case GameType.THEURBZ:
            file.read(16)
        case GameType.THESIMS2 | GameType.THESIMS2PETS | GameType.THESIMS2CASTAWAY | GameType.THESIMS3:
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
        case GameType.THESIMS2 | GameType.THESIMS2PETS | GameType.THESIMS2CASTAWAY | GameType.THESIMS3:
            file.read(57)

    match game_type:
        case GameType.THESIMSBUSTINOUT:
            read_light_infos(file, endianness)
        case (
            GameType.THEURBZ
            | GameType.THESIMS2
            | GameType.THESIMS2PETS
            | GameType.THESIMS2CASTAWAY
            | GameType.THESIMS3
        ):
            read_unknowns(file, endianness)
            read_bspline_volumes(file, endianness)
            read_dummies(file, endianness)
            read_cameras(file, endianness)
            read_light_infos(file, endianness)

    file.read(1)

    scale = 1.0 / struct.unpack(endianness + 'f', file.read(4))[0]

    sub_model_count = struct.unpack(endianness + 'I', file.read(4))[0]

    sub_models = [read_sub_model(file, version, endianness, scale) for _ in range(sub_model_count)]

    if len(file.read(64)) != 64:
        raise utils.FileReadError

    match game_type:
        case GameType.THESIMS | GameType.THESIMSBUSTINOUT | GameType.THEURBZ:
            footer_length = 8
        case GameType.THESIMS2 | GameType.THESIMS2PETS:
            footer_length = 4
        case GameType.THESIMS2CASTAWAY | GameType.THESIMS3:
            footer_length = 7

    if len(file.read(footer_length)) != footer_length:
        raise utils.FileReadError

    if game_type == GameType.THESIMS3:
        read_light_info_exs(file, endianness)

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

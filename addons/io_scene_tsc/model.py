"""Read The Sims, The Sims Bustin' Out, The Urbz, The Sims 2, The Sims 2 Pets and The Sims 2 Castaway model files."""

import dataclasses
import enum
import mathutils
import pathlib
import struct
import typing


from . import utils


FILE_MAGIC_ID = 1297040460


class FloatType(enum.Enum):
    """Model Float Type."""

    FLOAT32 = 0
    SNORM16 = 1


def snorm_to_float(input_value: int, scale: float) -> float:
    """Convert snorm to float."""
    return float(input_value) / (scale - 1.0)


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
    texture_id: int


MESH_FLAGS_HAS_UVS = 0b0000_0010
MESH_FLAGS_HAS_UNKNOWN = 0b0000_0100
MESH_FLAGS_HAS_NORMALS = 0b0000_1000
MESH_FLAGS_HAS_SNORM_FLOATS = 0b0001_0000
MESH_FLAGS_HAS_INDICES = 0b0010_0000
MESH_FLAGS_HAS_UVS_2 = 0b0100_0000


def read_mesh(file: typing.BinaryIO, game: utils.GameType, endianness: str, scale: float) -> Mesh:
    """Read mesh."""
    flags = struct.unpack(endianness + 'I', file.read(4))[0]

    texture_id = struct.unpack(endianness + 'I', file.read(4))[0]

    strip_count = struct.unpack(endianness + 'I', file.read(4))[0]
    file.read(strip_count)

    if game in (
        utils.GameType.THESIMSBUSTINOUT,
        utils.GameType.THEURBZ,
        utils.GameType.THESIMS2,
        utils.GameType.THESIMS2PETS,
    ):
        file.read(4)

    if game == utils.GameType.THESIMS2CASTAWAY:
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

    for _ in range(strip_count):
        mesh_type = struct.unpack(endianness + 'B', file.read(1))[0]

        if mesh_type == 4:
            for _ in range(strip_count):
                marker = struct.unpack(endianness + 'B', file.read(1))[0]
                if marker == 5:
                    file.read(2)

                vertex_count = struct.unpack(endianness + 'I', file.read(4))[0]

                positions += read_vertices(file, vertex_count, float_type, endianness, scale)

                if flags & MESH_FLAGS_HAS_UVS:
                    uvs += read_uvs(file, vertex_count, float_type, endianness)

                if flags & MESH_FLAGS_HAS_UNKNOWN:
                    file.read(vertex_count * 4)

                if flags & MESH_FLAGS_HAS_NORMALS:
                    normal_format, normal_size = (
                        (endianness + '4b', 4)
                        if game
                        in (
                            utils.GameType.THESIMS2,
                            utils.GameType.THESIMS2PETS,
                            utils.GameType.THESIMS2CASTAWAY,
                        )
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

                bones += [(0, 1, 2, 3) for _ in range(vertex_count)]

                bone_weights += [struct.unpack(endianness + '4B', file.read(4)) for _ in range(vertex_count)]

                strips.append((previous_strip_end, previous_strip_end + vertex_count))
                previous_strip_end = previous_strip_end + vertex_count

            break

        if mesh_type == 2:
            file.read(1)

        read_bone_weights = False

        bone_ids = []

        if mesh_type in (1, 2):
            while True:
                bone_id = struct.unpack(endianness + 'H', file.read(2))[0]
                bone_ids.append(bone_id)
                if struct.unpack(endianness + '2B', file.read(2))[1] == 0:
                    break

                read_bone_weights = True
        else:
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
                if game in (utils.GameType.THESIMS2, utils.GameType.THESIMS2PETS, utils.GameType.THESIMS2CASTAWAY)
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
            if game in (utils.GameType.THESIMS2PETS, utils.GameType.THESIMS2CASTAWAY):
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

                if game == utils.GameType.THESIMS2CASTAWAY:
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
        texture_id,
    )


@dataclasses.dataclass
class Object:
    """Object."""

    meshes: list[Mesh]


def read_object(file: typing.BinaryIO, game: utils.GameType, endianness: str, scale: float) -> Object:
    """Read Object."""
    file.read(4)

    if game == utils.GameType.THESIMS2CASTAWAY:
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

    return Object(meshes)


def read_header_unknowns(file: typing.BinaryIO, endianness: str) -> None:
    """Read Model header unknowns."""
    unknown_count_1 = struct.unpack(endianness + 'I', file.read(4))[0]
    if unknown_count_1 > 0:
        while True:
            if struct.unpack(endianness + 'I', file.read(4))[0] != 0xFFFFFFFF:
                file.seek(file.tell() - 3)
            else:
                file.seek(file.tell() - 12)
                break
    else:
        unknown_count_2 = struct.unpack(endianness + 'I', file.read(4))[0]
        for _ in range(unknown_count_2):
            if len(file.read(156)) == 0:
                raise utils.FileReadError

        unknown_count_3 = struct.unpack(endianness + 'I', file.read(4))[0]
        for _ in range(unknown_count_3):
            if len(file.read(172)) == 0:
                raise utils.FileReadError

        unknown_count_4 = struct.unpack(endianness + 'I', file.read(4))[0]
        for _ in range(unknown_count_4):
            if len(file.read(28)) == 0:
                raise utils.FileReadError

        file.read(1)


def read_the_sims_model(file: typing.BinaryIO, endianness: str) -> Object:
    """Read The Sims Model."""
    file.read(2)

    name = utils.read_null_terminated_string(file)

    file.read(1)

    scale = 1.0 / struct.unpack(endianness + 'f', file.read(4))[0]

    object_count = struct.unpack(endianness + 'I', file.read(4))[0]

    objects = [read_object(file, utils.GameType.THESIMS, endianness, scale) for _ in range(object_count)]

    file.read(64)
    file.read(8)

    return Model(
        name,
        objects,
        utils.GameType.THESIMS,
        endianness,
    )


def read_the_sims_bustin_out_model(file: typing.BinaryIO, endianness: str) -> Object:
    """Read The Sims Bustin' Out Model."""
    file.read(2)

    name = utils.read_null_terminated_string(file)

    file.read(16)
    unknown_count = struct.unpack(endianness + 'I', file.read(4))[0]
    for _ in range(unknown_count):
        file.read(28)

    file.read(1)

    scale = 1.0 / struct.unpack(endianness + 'f', file.read(4))[0]

    object_count = struct.unpack(endianness + 'I', file.read(4))[0]

    objects = [read_object(file, utils.GameType.THESIMSBUSTINOUT, endianness, scale) for _ in range(object_count)]

    file.read(64)
    file.read(8)

    return Model(
        name,
        objects,
        utils.GameType.THESIMSBUSTINOUT,
        endianness,
    )


def read_the_urbz_model(file: typing.BinaryIO, endianness: str) -> Object:
    """Read The Urbz Model."""
    file.read(16)

    name = utils.read_null_terminated_string(file)

    file.read(4)
    file.read(53)

    read_header_unknowns(file, endianness)

    scale = 1.0 / struct.unpack(endianness + 'f', file.read(4))[0]

    object_count = struct.unpack(endianness + 'I', file.read(4))[0]

    objects = [read_object(file, utils.GameType.THEURBZ, endianness, scale) for _ in range(object_count)]

    file.read(64)
    file.read(8)

    return Model(
        name,
        objects,
        utils.GameType.THEURBZ,
        endianness,
    )


def read_the_sims_2_model(file: typing.BinaryIO, endianness: str) -> Object:
    """Read The Sims 2 Model."""
    if struct.unpack(endianness + 'I', file.read(4))[0] != FILE_MAGIC_ID:
        raise utils.FileReadError

    if struct.unpack(endianness + 'i', file.read(4))[0] != -1:
        raise utils.FileReadError

    name_length = struct.unpack(endianness + 'I', file.read(4))[0]
    name = file.read(name_length - 1).decode('ascii')
    file.read(1)

    file.read(4)
    file.read(57)

    read_header_unknowns(file, endianness)

    scale = 1.0 / struct.unpack(endianness + 'f', file.read(4))[0]

    object_count = struct.unpack(endianness + 'I', file.read(4))[0]

    objects = [read_object(file, utils.GameType.THESIMS2, endianness, scale) for _ in range(object_count)]

    file.read(64)
    file.read(8)

    return Model(
        name,
        objects,
        utils.GameType.THESIMS2,
        endianness,
    )


def read_the_sims_2_pets_model(file: typing.BinaryIO, endianness: str) -> Object:
    """Read The Sims 2 Pets Model."""
    if struct.unpack(endianness + 'I', file.read(4))[0] != FILE_MAGIC_ID:
        raise utils.FileReadError

    if struct.unpack(endianness + 'i', file.read(4))[0] != -1:
        raise utils.FileReadError

    name_length = struct.unpack(endianness + 'I', file.read(4))[0]
    name = file.read(name_length - 1).decode('ascii')
    file.read(1)

    file.read(4)
    file.read(57)

    read_header_unknowns(file, endianness)

    scale = 1.0 / struct.unpack(endianness + 'f', file.read(4))[0]

    object_count = struct.unpack(endianness + 'I', file.read(4))[0]

    objects = [read_object(file, utils.GameType.THESIMS2PETS, endianness, scale) for _ in range(object_count)]

    file.read(64)
    file.read(4)

    return Model(
        name,
        objects,
        utils.GameType.THESIMS2PETS,
        endianness,
    )


def read_the_sims_2_castaway_model(file: typing.BinaryIO, endianness: str) -> Object:
    """Read The Sims 2 Castaway Model."""
    if struct.unpack(endianness + 'I', file.read(4))[0] != FILE_MAGIC_ID:
        raise utils.FileReadError

    if struct.unpack(endianness + 'i', file.read(4))[0] != -1:
        raise utils.FileReadError

    name_length = struct.unpack(endianness + 'I', file.read(4))[0]
    name = file.read(name_length - 1).decode('ascii')
    file.read(1)

    file.read(4)
    file.read(57)

    read_header_unknowns(file, endianness)

    scale = 1.0 / struct.unpack(endianness + 'f', file.read(4))[0]

    object_count = struct.unpack(endianness + 'I', file.read(4))[0]

    objects = [read_object(file, utils.GameType.THESIMS2CASTAWAY, endianness, scale) for _ in range(object_count)]

    file.read(64)
    file.read(8)

    return Model(
        name,
        objects,
        utils.GameType.THESIMS2CASTAWAY,
        endianness,
    )


@dataclasses.dataclass
class Model:
    """Model."""

    name: str
    objects: list[Object]
    game: utils.GameType
    endianness: str


def read_model(file: typing.BinaryIO) -> Model:  # noqa: PLR0911
    """Read Model."""
    match struct.unpack('<I', file.read(4))[0]:
        case 0x00:
            return read_the_sims_model(file, '<')

        case 0x01:
            return read_the_sims_bustin_out_model(file, '<')

        case 0x35:
            return read_the_urbz_model(file, '<')

        case 0x3A:
            return read_the_sims_2_model(file, '<')

        case 0x3E:
            return read_the_sims_2_pets_model(file, '<')

        case 0x3E000000:
            return read_the_sims_2_pets_model(file, '>')

        case 0x45000000:
            return read_the_sims_2_castaway_model(file, '>')

    raise utils.FileReadError


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

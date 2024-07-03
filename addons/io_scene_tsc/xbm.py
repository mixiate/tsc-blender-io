"""Read The Sims, The Sims Bustin' Out, The Urbz and The Sims 2 model files."""

import dataclasses
import pathlib
import struct
import typing
import enum
import mathutils


from . import utils


class GameType(enum.Enum):
    """Model Game Type."""

    THESIMS = 0
    THESIMSBUSTINOUT = 1
    THEURBZ = 2
    THESIMS2 = 3


@dataclasses.dataclass
class Vertex:
    """Xbox Mesh Vertex."""

    position: tuple[float, float, float]
    unknown: int


def read_vertices(file: typing.BinaryIO, count: int) -> list[Vertex]:
    """Read vertices."""
    return [
        Vertex(
            struct.unpack('<3f', file.read(4 * 3)),
            struct.unpack('<I', file.read(4))[0],
        )
        for _ in range(count)
    ]


@dataclasses.dataclass
class Mesh:
    """Xbox Mesh."""

    positions: list[Vertex]
    uvs: list[tuple[float, float]]
    normals: list[tuple[float, float, float]]
    faces: list[int]
    strips: list[tuple[int, int]]
    texture_id: int


def read_mesh(file: typing.BinaryIO, game: GameType) -> Mesh:  # noqa: C901 PLR0912 PLR0915
    """Read mesh."""
    flags = struct.unpack('<I', file.read(4))[0]

    texture_id = struct.unpack('<I', file.read(4))[0]

    strip_count = struct.unpack('<I', file.read(4))[0]
    file.read(strip_count)

    if game in (GameType.THESIMSBUSTINOUT, GameType.THEURBZ, GameType.THESIMS2):
        file.read(4)

    positions = []
    uvs = []
    normals = []
    faces = []
    strips = []

    previous_strip_end = 0

    for _ in range(strip_count):
        mesh_type = struct.unpack('<B', file.read(1))[0]

        if mesh_type == 4:  # noqa: PLR2004
            for _ in range(strip_count):
                marker = struct.unpack('<B', file.read(1))[0]
                if marker == 5:  # noqa: PLR2004
                    file.read(2)

                vertex_count = struct.unpack('<I', file.read(4))[0]

                positions += read_vertices(file, vertex_count)
                uvs += [struct.unpack('<2f', file.read(8)) for _ in range(vertex_count)]

                if flags & 0b00000100:
                    file.read(vertex_count * 4)

                if flags & 0b00001000:
                    normal_format, normal_size = ('<4b', 4) if game == GameType.THESIMS2 else ('<3b', 3)
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

                file.read(vertex_count * 4)

                strips.append((previous_strip_end, previous_strip_end + vertex_count))
                previous_strip_end = previous_strip_end + vertex_count

            break

        if mesh_type == 2:  # noqa: PLR2004
            file.read(1)

        read_unknown = False

        if mesh_type in (1, 2):
            while True:
                unknowns = struct.unpack('<4B', file.read(4))
                if unknowns[3] == 0:
                    break

                read_unknown = True

        vertex_count = struct.unpack('<I', file.read(4))[0]

        positions += read_vertices(file, vertex_count)

        if flags & 0b00000010:
            if flags & 0b01000000 and game in (GameType.THEURBZ, GameType.THESIMS2):
                uv_data = [struct.unpack('<4f', file.read(16)) for _ in range(vertex_count)]
                uvs += [(x[0], x[1]) for x in uv_data]
            else:
                uvs += [struct.unpack('<2f', file.read(8)) for _ in range(vertex_count)]

        if flags & 0b00000100:
            file.read(vertex_count * 4)

        if flags & 0b00001000:
            normal_format, normal_size = ('<4b', 4) if game == GameType.THESIMS2 else ('<3b', 3)
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

        if flags & 0b01000000 and game not in (GameType.THEURBZ, GameType.THESIMS2):
            file.read(vertex_count * 8)

        if flags & 0b00100000:
            index_count = struct.unpack('<I', file.read(4))[0]
            file.read(1)
            faces = [struct.unpack('<H', file.read(2))[0] for _ in range(index_count)]
        else:
            strips.append((previous_strip_end, previous_strip_end + vertex_count))

        previous_strip_end = previous_strip_end + vertex_count

        if read_unknown:
            file.read(vertex_count * 4)

    return Mesh(
        positions,
        uvs,
        normals,
        faces,
        strips,
        texture_id,
    )


@dataclasses.dataclass
class XboxObject:
    """Xbox Object."""

    meshes: list[Mesh]


def read_object(file: typing.BinaryIO, game: GameType) -> XboxObject:
    """Read Xbox Object."""
    file.read(4)

    mesh_count = struct.unpack('<I', file.read(4))[0]

    meshes = []
    for _ in range(mesh_count):
        meshes.append(read_mesh(file, game))

        marker = struct.unpack('<B', file.read(1))[0]
        if marker != 6:  # noqa: PLR2004
            file.read(1)

    return XboxObject(meshes)


def read_the_sims_model(file: typing.BinaryIO, name: str) -> XboxObject:
    """Read The Sims Model."""
    file.read(1)

    file.read(4)

    object_count = struct.unpack('<I', file.read(4))[0]

    objects = [read_object(file, GameType.THESIMS) for _ in range(object_count)]

    file.read(64)
    file.read(8)

    return XboxModel(
        name,
        objects,
        GameType.THESIMS,
    )


def read_the_sims_bustin_out_model(file: typing.BinaryIO, name: str) -> XboxObject:
    """Read The Sims Bustin' Out Model."""
    file.read(16)
    unknown_count = struct.unpack('<I', file.read(4))[0]
    for _ in range(unknown_count):
        file.read(28)

    file.read(5)

    object_count = struct.unpack('<I', file.read(4))[0]

    objects = [read_object(file, GameType.THESIMSBUSTINOUT) for _ in range(object_count)]

    file.read(64)
    file.read(8)

    return XboxModel(
        name,
        objects,
        GameType.THESIMSBUSTINOUT,
    )


def read_the_urbz_model(file: typing.BinaryIO) -> XboxObject:
    """Read The Urbz Model."""
    file.read(16)

    name = ''.join(iter(lambda: file.read(1).decode('ascii'), '\x00'))

    file.read(57)

    unknown_count_1 = struct.unpack('<I', file.read(4))[0]
    if unknown_count_1 > 0:
        while True:
            if struct.unpack('<I', file.read(4))[0] != 0xFFFFFFFF:  # noqa: PLR2004
                file.seek(file.tell() - 3)
            else:
                file.seek(file.tell() - 8)
                break
    else:
        unknown_count_2 = struct.unpack('<I', file.read(4))[0]
        for _ in range(unknown_count_2):
            file.read(156)

        unknown_count_3 = struct.unpack('<I', file.read(4))[0]
        for _ in range(unknown_count_3):
            file.read(172)

        unknown_count_4 = struct.unpack('<I', file.read(4))[0]
        for _ in range(unknown_count_4):
            file.read(28)

        file.read(5)

    object_count = struct.unpack('<I', file.read(4))[0]

    objects = [read_object(file, GameType.THEURBZ) for _ in range(object_count)]

    file.read(64)
    file.read(8)

    return XboxModel(
        name,
        objects,
        GameType.THEURBZ,
    )


def read_the_sims_2_model(file: typing.BinaryIO, name: str) -> XboxObject:
    """Read The Sims 2 Model."""
    file.read(2)

    file.read(59)

    unknown_count_1 = struct.unpack('<I', file.read(4))[0]
    if unknown_count_1 > 0:
        while True:
            if struct.unpack('<I', file.read(4))[0] != 0xFFFFFFFF:  # noqa: PLR2004
                file.seek(file.tell() - 3)
            else:
                file.seek(file.tell() - 8)
                break
    else:
        unknown_count_2 = struct.unpack('<I', file.read(4))[0]
        for _ in range(unknown_count_2):
            file.read(156)

        unknown_count_3 = struct.unpack('<I', file.read(4))[0]
        for _ in range(unknown_count_3):
            file.read(172)

        unknown_count_4 = struct.unpack('<I', file.read(4))[0]
        for _ in range(unknown_count_4):
            file.read(28)

        file.read(5)

    object_count = struct.unpack('<I', file.read(4))[0]

    objects = [read_object(file, GameType.THESIMS2) for _ in range(object_count)]

    file.read(64)
    file.read(8)

    return XboxModel(
        name,
        objects,
        GameType.THESIMS2,
    )


@dataclasses.dataclass
class XboxModel:
    """Xbox Model."""

    name: str
    objects: list[XboxObject]
    game: GameType


def read_xbox_model(file: typing.BinaryIO) -> XboxModel:
    """Read Xbox Model."""
    version = struct.unpack('<I', file.read(4))[0]

    if version == 0x35:  # noqa: PLR2004
        return read_the_urbz_model(file)

    if version == 0x3A:  # noqa: PLR2004
        file.read(8)
        version = struct.unpack('<I', file.read(4))[0]

    if version == 0x00:
        file.read(2)
        game = GameType.THESIMS
    elif version == 0x01:
        file.read(2)
        game = GameType.THESIMSBUSTINOUT
    else:
        game = GameType.THESIMS2

    name = ''.join(iter(lambda: file.read(1).decode('ascii'), '\x00'))

    match game:
        case GameType.THESIMS:
            return read_the_sims_model(file, name)
        case GameType.THESIMSBUSTINOUT:
            return read_the_sims_bustin_out_model(file, name)
        case GameType.THESIMS2:
            return read_the_sims_2_model(file, name)


def read_file(file_path: pathlib.Path) -> XboxModel:
    """Read a file as an Xbox Model."""
    try:
        with file_path.open(mode='rb') as file:
            model = read_xbox_model(file)

            if len(file.read(1)) != 0:
                raise utils.FileReadError

            return model

    except (OSError, struct.error) as exception:
        raise utils.FileReadError from exception

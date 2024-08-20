"""Read shader files."""

import dataclasses
import pathlib
import struct
import typing

from . import utils


@dataclasses.dataclass
class RenderPass:
    """RenderPass."""

    texture_id: int
    raster_modes: int
    flags: int
    blends: tuple[int, int, int, int]
    blend_fix: int
    combine: int
    texture_gen: int
    alpha_test_threshold: int
    post_texture_id_count: int
    post_texture_id_count_other: int


def read_render_pass_the_sims(file: typing.BinaryIO, endianness: str) -> RenderPass:
    """Read The Sims render pass."""
    texture_id = struct.unpack(endianness + 'I', file.read(4))[0]
    raster_modes = struct.unpack(endianness + 'I', file.read(4))[0]
    flags = struct.unpack(endianness + 'I', file.read(4))[0]
    blends = struct.unpack(endianness + '4B', file.read(4))
    blend_fix = struct.unpack(endianness + 'B', file.read(1))[0]
    combine = struct.unpack(endianness + 'B', file.read(1))[0]
    texture_gen = struct.unpack(endianness + 'B', file.read(1))[0]
    alpha_test_threshold = struct.unpack(endianness + 'f', file.read(4))[0]

    return RenderPass(
        texture_id,
        raster_modes,
        flags,
        blends,
        blend_fix,
        combine,
        texture_gen,
        alpha_test_threshold,
        0,
        0,
    )


def read_render_pass_the_urbz(file: typing.BinaryIO, endianness: str) -> RenderPass:
    """Read The Urbz render pass."""
    texture_id = struct.unpack(endianness + 'I', file.read(4))[0]
    file.read(8)
    raster_modes = struct.unpack(endianness + 'I', file.read(4))[0]
    flags = struct.unpack(endianness + 'I', file.read(4))[0]
    alpha_test_threshold = struct.unpack(endianness + 'I', file.read(4))[0]
    file.read(4)
    blends = struct.unpack(endianness + '4B', file.read(4))
    blend_fix = struct.unpack(endianness + 'B', file.read(1))[0]
    combine = struct.unpack(endianness + 'B', file.read(1))[0]
    texture_gen = struct.unpack(endianness + 'B', file.read(1))[0]
    file.read(1)
    post_texture_id_count = struct.unpack(endianness + 'B', file.read(1))[0]
    file.read(1)
    post_texture_id_count_other = struct.unpack(endianness + 'H', file.read(2))[0]

    if len(file.read(24)) != 24:
        raise utils.FileReadError

    return RenderPass(
        texture_id,
        raster_modes,
        flags,
        blends,
        blend_fix,
        combine,
        texture_gen,
        alpha_test_threshold,
        post_texture_id_count,
        post_texture_id_count_other,
    )


def read_render_pass_the_sims_2_pets(file: typing.BinaryIO, endianness: str) -> RenderPass:
    """Read The Sims 2 Pets render pass."""
    texture_id = struct.unpack(endianness + 'I', file.read(4))[0]
    file.read(1)
    raster_modes = struct.unpack(endianness + 'B', file.read(1))[0]
    flags = struct.unpack(endianness + 'B', file.read(1))[0]
    alpha_test_threshold = struct.unpack(endianness + 'f', file.read(4))[0]
    blends = struct.unpack(endianness + '4B', file.read(4))
    blend_fix = struct.unpack(endianness + 'B', file.read(1))[0]
    combine = struct.unpack(endianness + 'B', file.read(1))[0]
    texture_gen = struct.unpack(endianness + 'B', file.read(1))[0]
    file.read(2)
    post_texture_id_count = struct.unpack(endianness + 'B', file.read(1))[0]
    file.read(2)
    post_texture_id_count_other = struct.unpack(endianness + 'B', file.read(1))[0]

    if len(file.read(24)) != 24:
        raise utils.FileReadError

    return RenderPass(
        texture_id,
        raster_modes,
        flags,
        blends,
        blend_fix,
        combine,
        texture_gen,
        alpha_test_threshold,
        post_texture_id_count,
        post_texture_id_count_other,
    )


@dataclasses.dataclass
class Shader:
    """Shader."""

    name: str
    render_passes: list[RenderPass]
    geometry_modes: int
    sort_mode: int
    sort_value: int
    flags: int
    ambient_color: tuple[float, float, float]
    diffuse_color: tuple[float, float, float]
    surface_type: int


@dataclasses.dataclass
class ShaderIDs:
    """Shader IDs."""

    ids: list[int]


def read_shader_the_sims(file: typing.BinaryIO, endianness: str) -> Shader:
    """Read The Sims shader."""
    name = utils.read_null_terminated_string(file)

    render_pass_count = struct.unpack(endianness + 'B', file.read(1))[0]

    geometry_modes = struct.unpack(endianness + 'I', file.read(4))[0]
    sort_mode = struct.unpack(endianness + 'B', file.read(1))[0]
    sort_value = struct.unpack(endianness + 'I', file.read(4))[0]
    flags = struct.unpack(endianness + 'I', file.read(4))[0]

    file.read(4)

    ambient_color = struct.unpack(endianness + '3f', file.read(12))
    diffuse_color = struct.unpack(endianness + '3f', file.read(12))

    render_passes = [read_render_pass_the_sims(file, endianness) for _ in range(render_pass_count)]

    surface_type = struct.unpack(endianness + 'I', file.read(4))[0]

    if len(file.read(24)) != 24:
        raise utils.FileReadError

    return Shader(
        name,
        render_passes,
        geometry_modes,
        sort_mode,
        sort_value,
        flags,
        ambient_color,
        diffuse_color,
        surface_type,
    )


def read_shader_the_sims_bustin_out(file: typing.BinaryIO, endianness: str) -> Shader:
    """Read The Sims Bustin' Out shader."""
    file.read(16)

    name = utils.read_null_terminated_string(file)

    render_pass_count = struct.unpack(endianness + 'B', file.read(1))[0]

    geometry_modes = struct.unpack(endianness + 'I', file.read(4))[0]
    sort_mode = struct.unpack(endianness + 'B', file.read(1))[0]
    sort_value = struct.unpack(endianness + 'I', file.read(4))[0]
    flags = struct.unpack(endianness + 'I', file.read(4))[0]

    file.read(4)

    ambient_color = struct.unpack(endianness + '3f', file.read(12))
    diffuse_color = struct.unpack(endianness + '3f', file.read(12))
    file.read(12)

    file.read(24)

    render_passes = [read_render_pass_the_sims(file, endianness) for _ in range(render_pass_count)]

    surface_type = struct.unpack(endianness + 'I', file.read(4))[0]

    if len(file.read(24)) != 24:
        raise utils.FileReadError

    return Shader(
        name,
        render_passes,
        geometry_modes,
        sort_mode,
        sort_value,
        flags,
        ambient_color,
        diffuse_color,
        surface_type,
    )


def read_shader_ids_the_urbz(file: typing.BinaryIO, endianness: str) -> ShaderIDs:
    """Read The Urbz shader IDs."""
    file.read(8)
    file.read(4)  # file size

    _ = utils.read_null_terminated_string(file)

    file.read(5)

    shader_id_count = struct.unpack(endianness + 'B', file.read(1))[0]

    file.read(shader_id_count)

    shader_ids = [struct.unpack(endianness + 'I', file.read(4))[0] for _ in range(shader_id_count)]

    return ShaderIDs(shader_ids)


def read_shader_the_urbz(file: typing.BinaryIO, endianness: str) -> Shader | ShaderIDs:
    """Read The Urbz shader."""
    version = struct.unpack(endianness + 'I', file.read(4))[0]
    if version != 0x14:
        raise utils.FileReadError

    shader_type = struct.unpack(endianness + 'I', file.read(4))[0]

    match shader_type:
        case 0:
            pass
        case 1:
            return read_shader_ids_the_urbz(file, endianness)
        case _:
            raise utils.FileReadError

    file.read(8)
    file.read(4)  # file size

    name = utils.read_null_terminated_string(file)

    render_pass_count = struct.unpack(endianness + 'B', file.read(1))[0]

    file.read(7)

    sort_value = struct.unpack(endianness + 'I', file.read(4))[0]

    file.read(4)

    diffuse_color = struct.unpack(endianness + '3f', file.read(12))
    file.read(4)
    ambient_color = struct.unpack(endianness + '3f', file.read(12))
    file.read(4)
    file.read(12)

    file.read(4)
    file.read(36)

    render_passes = [read_render_pass_the_urbz(file, endianness) for _ in range(render_pass_count)]

    if render_pass_count == 1:
        read_render_pass_the_urbz(file, endianness)

    for render_pass in render_passes:
        if render_pass.post_texture_id_count == 0:
            continue
        texture_ids = [
            struct.unpack(endianness + 'I', file.read(4))[0] for _ in range(render_pass.post_texture_id_count)
        ]
        render_pass.texture_id = texture_ids[0]
        file.read(render_pass.post_texture_id_count_other)

    return Shader(
        name,
        render_passes,
        0,
        0,
        sort_value,
        0,
        ambient_color,
        diffuse_color,
        0,
    )


def read_shader_ids_the_sims_2(file: typing.BinaryIO, endianness: str) -> ShaderIDs:
    """Read The Sims 2 shader IDs."""
    file.read(4)  # name size

    _ = utils.read_null_terminated_string(file)

    file.read(4)  # file size

    file.read(5)

    shader_id_count = struct.unpack(endianness + 'B', file.read(1))[0]

    file.read(shader_id_count)

    shader_ids = [struct.unpack(endianness + 'I', file.read(4))[0] for _ in range(shader_id_count)]

    return ShaderIDs(shader_ids)


def read_shader_the_sims_2(file: typing.BinaryIO, endianness: str) -> Shader | ShaderIDs:
    """Read The Sims 2 shader."""
    version = struct.unpack(endianness + 'I', file.read(4))[0]
    file_id = struct.unpack(endianness + 'I', file.read(4))[0]
    if version != 0x16 or file_id != 1397245010:
        raise utils.FileReadError

    shader_type = struct.unpack(endianness + 'I', file.read(4))[0]

    match shader_type:
        case 0:
            pass
        case 1:
            return read_shader_ids_the_sims_2(file, endianness)
        case _:
            raise utils.FileReadError

    file.read(4)  # name size

    name = utils.read_null_terminated_string(file)

    file.read(4)  # file size

    render_pass_count = struct.unpack(endianness + 'B', file.read(1))[0]

    file.read(7)

    sort_value = struct.unpack(endianness + 'I', file.read(4))[0]

    file.read(4)

    diffuse_color = struct.unpack(endianness + '3f', file.read(12))
    file.read(4)
    ambient_color = struct.unpack(endianness + '3f', file.read(12))
    file.read(4)
    file.read(12)

    file.read(4)
    file.read(36)

    render_passes = [read_render_pass_the_urbz(file, endianness) for _ in range(render_pass_count)]

    if render_pass_count == 1:
        read_render_pass_the_urbz(file, endianness)

    for render_pass in render_passes:
        if render_pass.texture_id != 0:
            continue

        if render_pass.post_texture_id_count != 0:
            texture_ids = [
                struct.unpack(endianness + 'I', file.read(4))[0] for _ in range(render_pass.post_texture_id_count)
            ]
            render_pass.texture_id = texture_ids[0]
            file.read(render_pass.post_texture_id_count_other)

    return Shader(
        name,
        render_passes,
        0,
        0,
        sort_value,
        0,
        ambient_color,
        diffuse_color,
        0,
    )


def read_shader_the_sims_2_pets(file: typing.BinaryIO, endianness: str) -> Shader | ShaderIDs:
    """Read The Sims 2 Pets shader."""
    version = struct.unpack(endianness + 'I', file.read(4))[0]
    file_id = struct.unpack(endianness + 'I', file.read(4))[0]
    if version not in (0x18, 0x19, 0x1A) or file_id != 1397245010:
        raise utils.FileReadError

    shader_type = struct.unpack(endianness + 'I', file.read(4))[0]

    match shader_type:
        case 0:
            pass
        case 1:
            return read_shader_ids_the_sims_2(file, endianness)
        case _:
            raise utils.FileReadError

    file.read(4)  # name size

    name = utils.read_null_terminated_string(file)

    file.read(4)  # file size

    render_pass_count = struct.unpack(endianness + 'B', file.read(1))[0]

    file.read(6)

    sort_value = struct.unpack(endianness + 'I', file.read(4))[0]

    diffuse_color = struct.unpack(endianness + '3f', file.read(12))
    file.read(4)
    ambient_color = struct.unpack(endianness + '3f', file.read(12))
    file.read(4)

    file.read(16)

    render_passes = [read_render_pass_the_sims_2_pets(file, endianness) for _ in range(render_pass_count)]

    for render_pass in render_passes:
        if render_pass.texture_id != 0:
            continue

        if render_pass.post_texture_id_count != 0:
            texture_ids = [
                struct.unpack(endianness + 'I', file.read(4))[0] for _ in range(render_pass.post_texture_id_count)
            ]
            render_pass.texture_id = texture_ids[0]
            file.read(render_pass.post_texture_id_count_other)

    return Shader(
        name,
        render_passes,
        0,
        0,
        sort_value,
        0,
        ambient_color,
        diffuse_color,
        0,
    )


def read_file(file_path: pathlib.Path, game_type: utils.GameType, endianness: str) -> Shader | ShaderIDs | None:
    """Read a shader file."""
    try:
        with file_path.open(mode='rb') as file:
            shader = None

            match game_type:
                case utils.GameType.THESIMS:
                    shader = read_shader_the_sims(file, endianness)
                case utils.GameType.THESIMSBUSTINOUT:
                    shader = read_shader_the_sims_bustin_out(file, endianness)
                case utils.GameType.THEURBZ:
                    shader = read_shader_the_urbz(file, endianness)
                case utils.GameType.THESIMS2:
                    shader = read_shader_the_sims_2(file, endianness)
                case utils.GameType.THESIMS2PETS | utils.GameType.THESIMS2CASTAWAY | utils.GameType.THESIMS3:
                    shader = read_shader_the_sims_2_pets(file, endianness)

            if len(file.read(1)) != 0:
                raise utils.FileReadError

            return shader

    except (OSError, struct.error) as exception:
        raise utils.FileReadError from exception

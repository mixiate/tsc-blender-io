"""Get animation IDs from model IDs."""

import pathlib
import struct
import typing


from . import utils


SIMS_2_MODEL_ID_ANIMATION_MODEL_ID_LOOKUP = {
    0x1A8C4249: 0xEC5384BD,
    0x1CF1F1E9: 0xF2FF90C5,
    0x3FB8B291: 0x38D57688,
    0x48BF8207: 0x38D57688,
    0x6143FD5: 0x9F1D6E6F,
    0x6BF6C17F: 0xF2FF90C5,
    0x71130F43: 0x9F1D6E6F,
    0x8295644A: 0xF2FF90C5,
    0x9870AA76: 0x9F1D6E6F,
    0xA1DC2732: 0x38D57688,
    0xD6DB17A4: 0x38D57688,
    0xEF779AE0: 0x9F1D6E6F,
    0xF59254DC: 0xF2FF90C5,
}


def get_animation_model_id_from_model_id(model_id: int, game_type: utils.GameType) -> int:
    """Get the animation model ID from the model ID."""
    animation_model_id = model_id
    match game_type:
        case utils.GameType.THESIMS2:
            animation_model_id = SIMS_2_MODEL_ID_ANIMATION_MODEL_ID_LOOKUP.get(model_id, model_id)

    return animation_model_id


def read_animation_id(file: typing.BinaryIO, game_type: utils.GameType, endianness: str) -> int | None:
    """Read an animation ID from a SimsObject file."""
    file.read(8)

    animation_id = struct.unpack(endianness + 'I', file.read(4))[0]

    if game_type != utils.GameType.THESIMS:
        file.read(4)

    file.read(16)

    if animation_id != 0:
        return animation_id
    return None


def list_animation_ids_from_model_id(
    sims_objects_file_path: pathlib.Path,
    game_type: utils.GameType,
    endianness: str,
    model_id: int,
) -> tuple[bool, list[int]]:
    """Read animation IDs from a SimsObject file."""
    # bustin' out map
    if game_type == utils.GameType.THESIMSBUSTINOUT and model_id == 0x50AE831:
        return False, [0x92D8AE4A, 0x30AA9779, 0x6BCF6EE9]

    # urbz map
    if game_type == utils.GameType.THEURBZ and model_id == 0x95B8888F:
        return False, [0x95B8888F]

    # urbz load
    if game_type == utils.GameType.THEURBZ and model_id in (
        0x2AB2ED87,
        0x45110D60,
        0x4D58E53C,
        0x5C986D7C,
        0x816122B8,
        0x89A7EA61,
        0xAF6D7C92,
        0xBE91480,
        0xDC67C203,
        0xE7D44FC,
        0xF4BCC11A,
        0xFD7F6441,
    ):
        return False, [0x24C58257]

    match game_type:
        case utils.GameType.THESIMS:
            start_position = 1792468
            end_position = 1833523
        case utils.GameType.THESIMSBUSTINOUT:
            start_position = 2868764
            end_position = 2934816
        case utils.GameType.THEURBZ:
            start_position = 1566992
            end_position = 1615672
        case utils.GameType.THESIMS2:
            start_position = 982304
            end_position = 1040972
        case utils.GameType.THESIMS2PETS:
            start_position = 1125464
            end_position = 1197748
        case utils.GameType.THESIMS2CASTAWAY:
            start_position = 886652
            end_position = 946662

    try:
        with sims_objects_file_path.open(mode='rb') as file:
            file.seek(start_position)
            data = file.read(end_position - start_position)

            position = data.find(struct.pack(endianness + 'I', model_id))
            if position != -1:
                file.seek((start_position + position) - 4)
                count = struct.unpack(endianness + 'I', file.read(4))[0]

                animation_ids = [read_animation_id(file, game_type, endianness) for _ in range(count)]
                animation_ids = [x for x in animation_ids if x is not None]

                return True, list(dict.fromkeys(animation_ids))

            return False, []

    except (OSError, struct.error) as _:
        return False, []

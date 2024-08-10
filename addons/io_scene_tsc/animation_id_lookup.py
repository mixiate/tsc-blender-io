"""Get animation IDs from model IDs."""

import pathlib
import struct


from . import utils


def list_animation_ids_from_model_id(
    main_directory: pathlib.Path,
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
            objects_file_path = main_directory / "quickdat" / "SimsObjects"
        case utils.GameType.THESIMSBUSTINOUT:
            start_position = 2868764
            end_position = 2934816
            objects_file_path = main_directory / "quickdat" / "SimsObjects"
        case utils.GameType.THEURBZ:
            start_position = 1566992
            end_position = 1615672
            objects_file_path = main_directory / "quickdat" / "SimsObjects"
        case utils.GameType.THESIMS2:
            start_position = 982304
            end_position = 1040972
            objects_file_path = main_directory / "quickdat" / "SimsObjects"
        case utils.GameType.THESIMS2PETS:
            start_position = 1125464
            end_position = 1197748
            objects_file_path = main_directory / "quickdat" / "SimsObjects"
        case utils.GameType.THESIMS2CASTAWAY:
            start_position = 886652
            end_position = 946662
            objects_file_path = main_directory / "quickdat" / "SimsObjects"
        case utils.GameType.THESIMS3:
            start_position = 847931
            end_position = 1026640
            objects_file_path = main_directory / "binaries" / "allobjects.odf"

    try:
        with objects_file_path.open(mode='rb') as file:
            file.seek(start_position)
            data = file.read(end_position - start_position)

            search_position = 0

            animation_ids = []

            found = False

            while True:
                find_position = data.find(struct.pack(endianness + 'I', model_id), search_position)
                if find_position != -1:
                    search_position = find_position + 4

                    found = True

                    animation_ids.append(
                        struct.unpack(endianness + 'I', data[find_position + 8 : find_position + 12])[0]
                    )

                else:
                    break

            return found, animation_ids

    except (OSError, struct.error) as _:
        return False, []

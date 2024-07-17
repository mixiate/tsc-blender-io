"""Lazy loading ID to file path maps."""

import pathlib

from . import checksum


def create_id_file_path_map(directory: pathlib.Path) -> dict[int, pathlib.Path]:
    """Create a map between checksum IDs and file paths."""
    if directory.is_dir():
        file_dict = {}
        for file_path in directory.glob("*"):
            file_dict[checksum.calculate(file_path.stem)] = file_path
        return file_dict
    return {}


class IDFilePathMap:
    """Lazy loading ID to file path map."""

    _directory: pathlib.Path
    _map: dict[int, pathlib.Path] | None

    def __init__(
        self,
        directory: pathlib.Path,
    ) -> None:
        """Initialize IDFilePathMap."""
        self._directory = directory
        self._map = None

    def get(self) -> dict[int, pathlib.Path]:
        """Get the map."""
        if self._map:
            return self._map

        self._map = create_id_file_path_map(self._directory)
        return self._map


class IDFilePathMaps:
    """Lazy Loading ID to file path maps."""

    the_sims: IDFilePathMap
    the_sims_bustin_out: IDFilePathMap
    the_urbz: IDFilePathMap
    the_sims_2: IDFilePathMap
    the_sims_2_pets: IDFilePathMap
    the_sims_2_castaway: IDFilePathMap

    characters: IDFilePathMap
    animations: IDFilePathMap

    def __init__(
        self,
        the_sims: pathlib.Path,
        the_sims_bustin_out: pathlib.Path,
        the_urbz: pathlib.Path,
        the_sims_2: pathlib.Path,
        the_sims_2_pets: pathlib.Path,
        the_sims_2_castaway: pathlib.Path,
        characters: pathlib.Path,
        animations: pathlib.Path,
    ) -> None:
        """Initialize IDFilePathMaps."""
        self.the_sims = IDFilePathMap(the_sims)
        self.the_sims_bustin_out = IDFilePathMap(the_sims_bustin_out)
        self.the_urbz = IDFilePathMap(the_urbz)
        self.the_sims_2 = IDFilePathMap(the_sims_2)
        self.the_sims_2_pets = IDFilePathMap(the_sims_2_pets)
        self.the_sims_2_castaway = IDFilePathMap(the_sims_2_castaway)
        self.characters = IDFilePathMap(characters)
        self.animations = IDFilePathMap(animations)

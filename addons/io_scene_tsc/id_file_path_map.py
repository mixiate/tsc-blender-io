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

    characters: IDFilePathMap
    animations: IDFilePathMap
    textures: IDFilePathMap

    def __init__(
        self,
        characters: pathlib.Path,
        animations: pathlib.Path,
        textures: pathlib.Path,
    ) -> None:
        """Initialize IDFilePathMaps."""
        self.characters = IDFilePathMap(characters)
        self.animations = IDFilePathMap(animations)
        self.textures = IDFilePathMap(textures)

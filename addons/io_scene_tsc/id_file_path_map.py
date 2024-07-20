"""Lazy loading ID to file path maps."""

import pathlib

from . import checksum


def create_id_file_path_map(directory: pathlib.Path, *, with_extension: bool) -> dict[int, pathlib.Path]:
    """Create a map between checksum IDs and file paths."""
    if directory.is_dir():
        file_dict = {}
        for file_path in directory.rglob("*"):
            if with_extension:
                file_dict[checksum.calculate(file_path.name)] = file_path
            else:
                file_dict[checksum.calculate(file_path.stem)] = file_path
        return file_dict
    return {}


class IDFilePathMap:
    """Lazy loading ID to file path map."""

    _directory: pathlib.Path
    _map: dict[int, pathlib.Path] | None
    _with_extension: bool

    def __init__(
        self,
        directory: pathlib.Path,
        *,
        with_extension: bool,
    ) -> None:
        """Initialize IDFilePathMap."""
        self._directory = directory
        self._map = None
        self._with_extension = with_extension

    def get(self) -> dict[int, pathlib.Path]:
        """Get the map."""
        if self._map:
            return self._map

        self._map = create_id_file_path_map(self._directory, with_extension=self._with_extension)
        return self._map


class IDFilePathMaps:
    """Lazy Loading ID to file path maps."""

    characters: IDFilePathMap
    animations: IDFilePathMap
    shaders: IDFilePathMap
    textures: IDFilePathMap

    def __init__(
        self,
        characters: pathlib.Path,
        animations: pathlib.Path,
        shaders: pathlib.Path,
        textures: pathlib.Path,
    ) -> None:
        """Initialize IDFilePathMaps."""
        self.characters = IDFilePathMap(characters, with_extension=True)
        self.animations = IDFilePathMap(animations, with_extension=True)
        self.shaders = IDFilePathMap(shaders, with_extension=True)
        self.textures = IDFilePathMap(textures, with_extension=False)

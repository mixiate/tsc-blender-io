"""The Sims Console Blender IO."""

bl_info = {
    "name": "Import The Sims, Bustin' Out, Urbz, 2, Pets, Castaway, 3 format",
    "description": "Import models from the first generation of The Sims console games.",
    "author": "mix",
    "version": (2, 2, 0),
    "blender": (4, 1, 0),
    "location": "File > Import",
    "warning": "",
    "doc_url": "https://github.com/mixsims/tsc-blender-io",
    "tracker_url": "https://github.com/mixsims/tsc-blender-io/issues",
    "support": "COMMUNITY",
    "category": "Import-Export",
}


if "bpy" in locals():
    import sys
    import importlib

    for name in tuple(sys.modules):
        if name.startswith(__name__ + "."):
            importlib.reload(sys.modules[name])


import bpy  # noqa: E402
import bpy_extras  # noqa: E402
import typing  # noqa: E402


class TS1IOImport(bpy.types.Operator, bpy_extras.io_utils.ImportHelper):
    """Import model operator."""

    bl_idname: str = "import.model"
    bl_label: str = "The Sims, Bustin' Out, Urbz, 2, Pets, Castaway, 3"
    bl_description: str = (
        "The Sims, The Sims Bustin' Out, The Urbz, The Sims 2, The Sims 2 Pets, The Sims 2 Castaway or The Sims 3 Model"
    )
    bl_options: typing.ClassVar[set[str]] = {'UNDO'}

    filename_ext = ""

    filter_glob: bpy.props.StringProperty(  # type: ignore[valid-type]
        default="*",
        options={'HIDDEN'},
    )
    files: bpy.props.CollectionProperty(  # type: ignore[valid-type]
        name="File Path",
        type=bpy.types.OperatorFileListElement,
    )
    directory: bpy.props.StringProperty(  # type: ignore[valid-type]
        subtype='DIR_PATH',
    )

    import_animations: bpy.props.BoolProperty(  # type: ignore[valid-type]
        name="Import Skeletons and Animations",
        description="Import skeletons and animations for models",
        default=True,
    )

    flip_normals_x_axis: bpy.props.BoolProperty(  # type: ignore[valid-type]
        name="Flip Normals X Axis (The Sims 2+ Fix)",
        description="Flip the normals on the x axis. This is needed for some models from The Sims 2 + games",
        default=False,
    )

    invert_normals: bpy.props.BoolProperty(  # type: ignore[valid-type]
        name="Invert Normals (The Sims 3 Fix)",
        description="Invert all normals. This is needed for some models from The Sims 3",
        default=False,
    )

    cleanup_meshes: bpy.props.BoolProperty(  # type: ignore[valid-type]
        name="Cleanup Meshes (Lossy)",
        description="Merge the vertices of the mesh, add sharp edges, remove original normals and shade smooth",
        default=False,
    )

    def execute(self, context: bpy.context) -> set[str]:
        """Execute the importing function."""
        import io
        import logging
        import pathlib
        from . import import_files

        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)
        log_stream = io.StringIO()
        logger.addHandler(logging.StreamHandler(stream=log_stream))

        directory = pathlib.Path(self.directory)
        paths = [directory / file.name for file in self.files]

        import_files.import_files(
            context,
            logger,
            paths,
            import_animations=self.import_animations,
            flip_normals_x_axis=self.flip_normals_x_axis,
            invert_normals=self.invert_normals,
            cleanup_meshes=self.cleanup_meshes,
        )

        log_output = log_stream.getvalue()
        if log_output != "":
            self.report({"ERROR"}, log_output)

        return {'FINISHED'}

    def draw(self, _: bpy.context) -> None:
        """Draw the import options ui."""
        col = self.layout.column()
        col.prop(self, "import_animations")
        col.prop(self, "flip_normals_x_axis")
        col.prop(self, "invert_normals")
        col.prop(self, "cleanup_meshes")


def menu_import(self: bpy.types.TOPBAR_MT_file_import, _: bpy.context) -> None:
    """Add an entry to the import menu."""
    self.layout.operator(TS1IOImport.bl_idname)


def register() -> None:
    """Register with Blender."""
    bpy.utils.register_class(TS1IOImport)

    bpy.types.TOPBAR_MT_file_import.append(menu_import)


def unregister() -> None:
    """Unregister with Blender."""
    bpy.utils.unregister_class(TS1IOImport)

    bpy.types.TOPBAR_MT_file_import.remove(menu_import)


if __name__ == "__main__":
    register()

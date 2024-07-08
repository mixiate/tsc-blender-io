"""The Sims Console Blender IO."""

bl_info = {
    "name": "The Sims, Bustin' Out, Urbz, 2, 2 Pets Model Formats",
    "description": "Import The Sims, The Sims Bustin' Out, The Urbz, The Sims 2 and The Sims 2 Pets models.",
    "author": "mix",
    "version": (1, 1, 0),
    "blender": (4, 1, 0),
    "location": "File > Import-Export",
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
    bl_label: str = "Import The Sims, Bustin' Out, Urbz, 2, Pets Model"
    bl_description: str = "Import The Sims, The Sims Bustin' Out, The Urbz, The Sims 2 or The Sims 2 Pets Model"
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
        from . import import_model

        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)
        log_stream = io.StringIO()
        logger.addHandler(logging.StreamHandler(stream=log_stream))

        directory = pathlib.Path(self.directory)
        paths = [directory / file.name for file in self.files]

        import_model.import_files(context, logger, paths, cleanup_meshes=self.cleanup_meshes)

        log_output = log_stream.getvalue()
        if log_output != "":
            self.report({"ERROR"}, log_output)

        return {'FINISHED'}

    def draw(self, _: bpy.context) -> None:
        """Draw the import options ui."""
        col = self.layout.column()
        col.prop(self, "cleanup_meshes")


def menu_import(self: bpy.types.TOPBAR_MT_file_import, _: bpy.context) -> None:
    """Add an entry to the import menu."""
    self.layout.operator(TS1IOImport.bl_idname)


class TS1IOAddonPreferences(bpy.types.AddonPreferences):
    """Preferences for the addon."""

    bl_idname = __name__

    the_sims_texture_directory: bpy.props.StringProperty(  # type: ignore[valid-type]
        name="The Sims Textures",
        description="Directory for The Sims textures",
        subtype='DIR_PATH',
        default="",
    )

    the_sims_bustin_out_texture_directory: bpy.props.StringProperty(  # type: ignore[valid-type]
        name="The Sims Bustin' Out Textures",
        description="Directory for The Sims Bustin' Out textures",
        subtype='DIR_PATH',
        default="",
    )

    the_urbz_texture_directory: bpy.props.StringProperty(  # type: ignore[valid-type]
        name="The Urbz Textures",
        description="Directory for The Urbz textures",
        subtype='DIR_PATH',
        default="",
    )

    the_sims_2_texture_directory: bpy.props.StringProperty(  # type: ignore[valid-type]
        name="The Sims 2 Textures",
        description="Directory for The Sims 2 textures",
        subtype='DIR_PATH',
        default="",
    )

    the_sims_2_pets_texture_directory: bpy.props.StringProperty(  # type: ignore[valid-type]
        name="The Sims 2 Pets Textures",
        description="Directory for The Sims 2 Pets textures",
        subtype='DIR_PATH',
        default="",
    )

    def draw(self, _: bpy.context) -> None:
        """Draw the addon preferences ui."""
        self.layout.prop(self, "the_sims_texture_directory")
        self.layout.prop(self, "the_sims_bustin_out_texture_directory")
        self.layout.prop(self, "the_urbz_texture_directory")
        self.layout.prop(self, "the_sims_2_texture_directory")
        self.layout.prop(self, "the_sims_2_pets_texture_directory")


classes = (
    TS1IOImport,
    TS1IOAddonPreferences,
)


def register() -> None:
    """Register with Blender."""
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.TOPBAR_MT_file_import.append(menu_import)


def unregister() -> None:
    """Unregister with Blender."""
    for cls in classes:
        bpy.utils.unregister_class(cls)

    bpy.types.TOPBAR_MT_file_import.remove(menu_import)


if __name__ == "__main__":
    register()

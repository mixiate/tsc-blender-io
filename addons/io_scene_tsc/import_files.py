"""Import The Sims, The Sims Bustin' Out, The Urbz, The Sims 2, The Sims 2 Pets and The Sims 2 Castaway models."""

import bpy
import logging
import pathlib


from . import id_file_path_map
from . import import_animation
from . import import_model
from . import utils


def import_files(
    context: bpy.types.Context,
    logger: logging.Logger,
    file_paths: list[pathlib.Path],
    *,
    import_animations: bool,
    flip_normals_x_axis: bool,
    cleanup_meshes: bool,
) -> None:
    """Import all the models in the selected files."""
    if bpy.ops.object.mode_set.poll():
        bpy.ops.object.mode_set(mode='OBJECT')

    if bpy.ops.object.select_all.poll():
        bpy.ops.object.select_all(action='DESELECT')

    id_file_path_maps = id_file_path_map.IDFilePathMaps(
        file_paths[0].parent.parent / "characters",
        file_paths[0].parent.parent / "animations",
        file_paths[0].parent.parent / "shaders",
        file_paths[0].parent.parent / "textures",
    )

    object_list = []

    for file_path in file_paths:
        try:
            object_list += import_model.import_model(
                context,
                logger,
                file_path,
                id_file_path_maps,
                import_animations=import_animations,
                flip_normals_x_axis=flip_normals_x_axis,
            )
        except utils.FileReadError as _:  # noqa: PERF203
            if context.view_layer.objects.active is not None and context.view_layer.objects.active.type == 'ARMATURE':
                import_animation.import_animation(
                    context,
                    logger,
                    file_path,
                    None,
                    None,
                    context.view_layer.objects.active,
                )
                continue

            logger.info(f"Could not import {file_path} as model or animation")  # noqa: G004
            return

    if cleanup_meshes:
        previous_active_object = context.view_layer.objects.active
        bpy.ops.object.select_all(action='DESELECT')

        for obj in object_list:
            obj.select_set(state=True)

        context.view_layer.objects.active = object_list[0]

        bpy.ops.object.mode_set(mode='EDIT')

        bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='VERT')
        bpy.ops.mesh.select_all(action='SELECT')

        bpy.ops.mesh.merge_normals()
        bpy.ops.mesh.remove_doubles(use_sharp_edge_from_normals=True)
        bpy.ops.mesh.faces_shade_smooth()

        bpy.ops.mesh.select_all(action='DESELECT')

        bpy.ops.object.mode_set(mode='OBJECT')

        for obj in object_list:
            context.view_layer.objects.active = obj
            bpy.ops.mesh.customdata_custom_splitnormals_clear()

        bpy.ops.object.select_all(action='DESELECT')

        context.view_layer.objects.active = previous_active_object

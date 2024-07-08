"""Import The Sims, The Sims Bustin' Out, The Urbz and The Sims 2 models in to Blender."""

import bmesh
import bpy
import logging
import mathutils
import pathlib
import contextlib


from . import model
from . import texture_loader


def import_model(  # noqa: C901 PLR0912 PLR0913 PLR0915
    context: bpy.types.Context,
    logger: logging.Logger,
    file_path: pathlib.Path,
    the_sims_texture_list: list[pathlib.Path],
    the_sims_bustin_out_texture_list: list[pathlib.Path],
    the_urbz_texture_list: list[pathlib.Path],
    the_sims_2_texture_list: list[pathlib.Path],
    the_sims_2_pets_texture_list: list[pathlib.Path],
) -> list[bpy.types.Object]:
    """Import a model file."""
    try:
        model_desc = model.read_file(file_path)
    except model.FileReadError as _:
        logger.info(f"Could not load model {file_path}")  # noqa: G004
        return []

    object_list = []

    file_collection = bpy.data.collections.get(model_desc.name)
    if file_collection is None:
        file_collection = bpy.data.collections.new(model_desc.name)

    if file_collection.name not in context.collection.children:
        context.collection.children.link(file_collection)

    for object_index, object_desc in enumerate(model_desc.objects):
        object_collection_name = f"{model_desc.name} {object_index}"

        object_collection = bpy.data.collections.get(object_collection_name)
        if object_collection is None:
            object_collection = bpy.data.collections.new(object_collection_name)

        if object_collection.name not in file_collection.children:
            file_collection.children.link(object_collection)

        for mesh_index, mesh_desc in enumerate(object_desc.meshes):
            mesh_name = f"{model_desc.name} {object_index} {mesh_index}"

            mesh = bpy.data.meshes.new(mesh_name)
            obj = bpy.data.objects.new(mesh_name, mesh)

            object_list.append(obj)

            object_collection.objects.link(obj)

            b_mesh = bmesh.new()

            for vertex in mesh_desc.positions:
                position = mathutils.Vector(vertex.position)
                b_mesh.verts.new(position)

            b_mesh.verts.ensure_lookup_table()
            b_mesh.verts.index_update()

            if len(mesh_desc.faces):
                for i in range(len(mesh_desc.faces) - 2):
                    with contextlib.suppress(ValueError):
                        b_mesh.faces.new(
                            (
                                b_mesh.verts[mesh_desc.faces[i + 2]],
                                b_mesh.verts[mesh_desc.faces[i + 1]],
                                b_mesh.verts[mesh_desc.faces[i + 0]],
                            ),
                        )

            deform_layer = b_mesh.verts.layers.deform.verify()

            for index, strip in enumerate(mesh_desc.strips):
                vertex_group = obj.vertex_groups.new(name=str(index))

                for i in range(strip[0], strip[1] - 2):
                    if mesh_desc.positions[i + 2].unknown & 0b1000_0000_0000_0000:
                        continue

                    vert_a = b_mesh.verts[i + 0]
                    vert_b = b_mesh.verts[i + 1]
                    vert_c = b_mesh.verts[i + 2]

                    vert_a[deform_layer][vertex_group.index] = 1.0
                    vert_b[deform_layer][vertex_group.index] = 1.0
                    vert_c[deform_layer][vertex_group.index] = 1.0

                    if vert_a.co != vert_b.co and vert_a.co != vert_c.co and vert_b.co != vert_c.co:  # noqa: PLR1714
                        b_mesh.faces.new((vert_a, vert_b, vert_c))

            if len(mesh_desc.uvs):
                uv_layer = b_mesh.loops.layers.uv.verify()
                for face in b_mesh.faces:
                    for loop in face.loops:
                        loop[uv_layer].uv = mesh_desc.uvs[loop.vert.index]

            if len(mesh_desc.uvs_2):
                uv_layer = b_mesh.loops.layers.uv.new()
                for face in b_mesh.faces:
                    for loop in face.loops:
                        loop[uv_layer].uv = mesh_desc.uvs_2[loop.vert.index]

            b_mesh.to_mesh(mesh)
            b_mesh.free()

            if len(mesh_desc.normals) > 0:
                mesh.normals_split_custom_set_from_vertices(mesh_desc.normals)

                for polygon in mesh.polygons:
                    if polygon.normal.dot(mathutils.Vector(mesh_desc.normals[polygon.vertices[0]])) < 0.0:
                        polygon.flip()

                mesh.normals_split_custom_set_from_vertices(mesh_desc.normals)

                mesh.update()

            texture_id_string = f'{mesh_desc.texture_id:x}'

            match model_desc.game:
                case model.GameType.THESIMS:
                    texture_file_list = the_sims_texture_list
                    texture_id_string = texture_loader.lookup_shader_texture_id_the_sims(texture_id_string)
                case model.GameType.THESIMSBUSTINOUT:
                    texture_file_list = the_sims_bustin_out_texture_list
                    texture_id_string = texture_loader.lookup_shader_texture_id_the_sims_bustin_out(texture_id_string)
                case model.GameType.THEURBZ:
                    texture_file_list = the_urbz_texture_list
                    texture_id_string = texture_loader.lookup_shader_texture_id_the_urbz(texture_id_string)
                case model.GameType.THESIMS2:
                    texture_file_list = the_sims_2_texture_list
                    texture_id_string = texture_loader.lookup_shader_texture_id_the_sims_2(texture_id_string)
                case model.GameType.THESIMS2PETS:
                    texture_file_list = the_sims_2_pets_texture_list

            for file_path in texture_file_list:
                if file_path.stem.endswith(texture_id_string):
                    texture_loader.create_material(obj, file_path.stem, file_path)

    return object_list


def get_texture_file_list(directory_string: str) -> list[pathlib.Path]:
    """Get a list of all texture files from the given directory."""
    if directory_string != "":
        return list(pathlib.Path(directory_string).glob("*.png"))
    return []


def import_files(
    context: bpy.types.Context,
    logger: logging.Logger,
    file_paths: list[pathlib.Path],
    *,
    cleanup_meshes: bool,
) -> None:
    """Import all the models in the selected files."""
    if bpy.ops.object.mode_set.poll():
        bpy.ops.object.mode_set(mode='OBJECT')

    if bpy.ops.object.select_all.poll():
        bpy.ops.object.select_all(action='DESELECT')

    the_sims_texture_list = get_texture_file_list(
        context.preferences.addons["io_scene_tsc"].preferences.the_sims_texture_directory,
    )

    the_sims_bustin_out_texture_list = get_texture_file_list(
        context.preferences.addons["io_scene_tsc"].preferences.the_sims_bustin_out_texture_directory,
    )

    the_urbz_texture_list = get_texture_file_list(
        context.preferences.addons["io_scene_tsc"].preferences.the_urbz_texture_directory,
    )

    the_sims_2_texture_list = get_texture_file_list(
        context.preferences.addons["io_scene_tsc"].preferences.the_sims_2_texture_directory,
    )

    the_sims_2_pets_texture_list = get_texture_file_list(
        context.preferences.addons["io_scene_tsc"].preferences.the_sims_2_pets_texture_directory,
    )

    object_list = []

    for file_path in file_paths:
        object_list += import_model(
            context,
            logger,
            file_path,
            the_sims_texture_list,
            the_sims_bustin_out_texture_list,
            the_urbz_texture_list,
            the_sims_2_texture_list,
            the_sims_2_pets_texture_list,
        )

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

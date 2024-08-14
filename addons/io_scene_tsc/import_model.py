"""Import models."""

import bmesh
import bpy
import contextlib
import itertools
import logging
import mathutils
import pathlib


from . import animation_id_lookup
from . import checksum
from . import id_file_path_map
from . import import_animation
from . import import_character
from . import import_shader
from . import model
from . import utils


def import_model(
    context: bpy.types.Context,
    logger: logging.Logger,
    file_path: pathlib.Path,
    id_file_path_maps: id_file_path_map.IDFilePathMaps,
    *,
    import_animations: bool,
    flip_normals_x_axis: bool,
    invert_normals: bool,
) -> list[bpy.types.Object]:
    """Import a model file."""
    model_desc = model.read_file(file_path)

    object_list = []

    file_collection = bpy.data.collections.new(model_desc.name)

    if file_collection.name not in context.collection.children:
        context.collection.children.link(file_collection)

    model_id = checksum.calculate(file_path.stem)

    if import_animations:
        armature_object = import_character.import_character(
            context,
            logger,
            id_file_path_maps.characters.get(),
            model_desc.name,
            model_id,
            model_desc.game,
            model_desc.endianness,
            file_collection,
        )
    else:
        armature_object = None

    is_object, animation_ids = animation_id_lookup.list_animation_ids_from_model_id(
        file_path.parent.parent,
        model_desc.game,
        model_desc.endianness,
        model_id,
    )

    for sub_model_index, sub_model in enumerate(model_desc.sub_models):
        sub_model_collection_name = f"{model_desc.name} {sub_model_index}"

        sub_model_collection = bpy.data.collections.new(sub_model_collection_name)

        if sub_model_collection.name not in file_collection.children:
            file_collection.children.link(sub_model_collection)

        for mesh in itertools.chain([sub_model.main_mesh], sub_model.meshes):
            if not mesh:
                continue

            if (
                is_object
                and flip_normals_x_axis
                and model_desc.game
                in (
                    utils.GameType.THESIMS2,
                    utils.GameType.THESIMS2PETS,
                    utils.GameType.THESIMS2CASTAWAY,
                    utils.GameType.THESIMS3,
                )
            ):
                for normal in mesh.normals:
                    normal[0] = -normal[0]

            if is_object and model_desc.game == utils.GameType.THESIMS3 and invert_normals:
                for normal in mesh.normals:
                    normal.negate()

        for mesh_index, mesh_desc in enumerate(sub_model.meshes):
            mesh_name = f"{model_desc.name} {sub_model_index} {mesh_index}"

            mesh = bpy.data.meshes.new(mesh_name)
            obj = bpy.data.objects.new(mesh_name, mesh)

            object_list.append(obj)

            sub_model_collection.objects.link(obj)

            b_mesh = bmesh.new()

            if sub_model.main_mesh:
                positions = [sub_model.main_mesh.positions[x] for x in mesh_desc.indices]
                uvs = [sub_model.main_mesh.uvs[x] for x in mesh_desc.indices_uvs]
                normals = [sub_model.main_mesh.normals[x] for x in mesh_desc.indices_normals]
                colors = [sub_model.main_mesh.colors[x] for x in mesh_desc.indices_colors]
            else:
                positions = mesh_desc.positions
                uvs = mesh_desc.uvs
                normals = mesh_desc.normals
                colors = mesh_desc.colors

            for vertex in positions:
                position = mathutils.Vector(vertex.position)
                b_mesh.verts.new(position)

            b_mesh.verts.ensure_lookup_table()
            b_mesh.verts.index_update()

            if sub_model.main_mesh:
                for vertex_index in range(len(positions) - 2):
                    vert_a = b_mesh.verts[vertex_index + 0]
                    vert_b = b_mesh.verts[vertex_index + 1]
                    vert_c = b_mesh.verts[vertex_index + 2]

                    if vert_a.co != vert_b.co and vert_a.co != vert_c.co and vert_b.co != vert_c.co:  # noqa: PLR1714
                        b_mesh.faces.new((vert_a, vert_b, vert_c))
            else:
                for vertex_index in range(len(mesh_desc.indices) - 2):
                    with contextlib.suppress(ValueError):
                        b_mesh.faces.new(
                            (
                                b_mesh.verts[mesh_desc.indices[vertex_index + 0]],
                                b_mesh.verts[mesh_desc.indices[vertex_index + 1]],
                                b_mesh.verts[mesh_desc.indices[vertex_index + 2]],
                            ),
                        )

                for strip in mesh_desc.strips:
                    for vertex_index in range(strip[0], strip[1] - 2):
                        if mesh_desc.positions[vertex_index + 2].unknown & 0b1000_0000_0000_0000:
                            continue

                        vert_a = b_mesh.verts[vertex_index + 0]
                        vert_b = b_mesh.verts[vertex_index + 1]
                        vert_c = b_mesh.verts[vertex_index + 2]

                        if vert_a.co != vert_b.co and vert_a.co != vert_c.co and vert_b.co != vert_c.co:  # noqa: PLR1714
                            b_mesh.faces.new((vert_a, vert_b, vert_c))

            if uvs:
                uv_layer = b_mesh.loops.layers.uv.verify()
                for face in b_mesh.faces:
                    for loop in face.loops:
                        loop[uv_layer].uv = uvs[loop.vert.index]

            if mesh_desc.uvs_2:
                uv_layer = b_mesh.loops.layers.uv.new()
                for face in b_mesh.faces:
                    for loop in face.loops:
                        loop[uv_layer].uv = mesh_desc.uvs_2[loop.vert.index]

            if colors:
                color_layer = b_mesh.loops.layers.color.verify()
                for face in b_mesh.faces:
                    for loop in face.loops:
                        loop[color_layer] = [float(x) / 255.0 for x in colors[loop.vert.index]]

            if armature_object:
                deform_layer = b_mesh.verts.layers.deform.verify()
                vertex_groups = [obj.vertex_groups.new(name=bone.name) for bone in armature_object.data.bones]

                for vertex_index, (bones, weights) in enumerate(zip(mesh_desc.bones, mesh_desc.bone_weights)):
                    vertex = b_mesh.verts[vertex_index]
                    for bone_weight_index, bone_index in enumerate(bones):
                        weight = weights[bone_weight_index]
                        if weight > 0:
                            vertex[deform_layer][vertex_groups[bone_index].index] = float(weight) / 255.0

            if sub_model.main_mesh:
                loose_vertices = [x for x in b_mesh.verts if not x.link_faces]

                for i in sorted([x.index for x in loose_vertices], reverse=True):
                    del normals[i]

                for vertex in loose_vertices:
                    b_mesh.verts.remove(vertex)

            b_mesh.to_mesh(mesh)
            b_mesh.free()

            if normals:
                mesh.normals_split_custom_set_from_vertices(normals)

                for polygon in mesh.polygons:
                    if polygon.normal.dot(mathutils.Vector(normals[polygon.vertices[0]])) < 0.0:
                        polygon.flip()

                mesh.normals_split_custom_set_from_vertices(normals)

            if armature_object:
                bpy.ops.object.select_all(action='DESELECT')
                obj.select_set(state=True)
                armature_object.select_set(state=True)
                context.view_layer.objects.active = armature_object
                bpy.ops.object.parent_set(type='ARMATURE')
                bpy.ops.object.select_all(action='DESELECT')

            elif is_object:
                obj.scale.x = -obj.scale.x

            material = import_shader.import_shader(
                logger,
                model_desc.game,
                model_desc.endianness,
                mesh_desc.shader_id,
                id_file_path_maps.shaders.get(),
                id_file_path_maps.textures.get(),
            )

            if material:
                obj.data.materials.append(material)

    if armature_object:
        for animation_id in animation_ids:
            animation_file_path = id_file_path_maps.animations.get().get(animation_id)
            if animation_file_path:
                import_animation.import_animation(
                    context,
                    logger,
                    animation_file_path,
                    model_desc.game,
                    model_desc.endianness,
                    armature_object,
                )

        if (
            armature_object.animation_data
            and armature_object.animation_data.nla_tracks
            and armature_object.animation_data.nla_tracks[0].strips
        ):
            armature_object.animation_data.action = armature_object.animation_data.nla_tracks[0].strips[0].action

        if is_object:
            armature_object.scale.x = -armature_object.scale.x

    return object_list

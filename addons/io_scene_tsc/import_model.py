"""Import The Sims, The Sims Bustin' Out, The Urbz, The Sims 2, The Sims 2 Pets and The Sims 2 Castaway models."""

import bmesh
import bpy
import contextlib
import copy
import itertools
import logging
import math
import mathutils
import pathlib


from . import animation
from . import animation_id_lookup
from . import character
from . import character_id_lookup
from . import checksum
from . import id_file_path_map
from . import model
from . import texture_loader
from . import utils


def import_character(
    context: bpy.types.Context,
    logger: logging.Logger,
    character_id_file_path_map: dict[int, pathlib.Path],
    model_name: str,
    model_id: int,
    game_type: utils.GameType,
    endianness: str,
    collection: bpy.types.Collection,
) -> bpy.types.Object | None:
    """Import a character file."""
    character_id = character_id_lookup.get_character_id_from_model(model_name, model_id, game_type)

    character_file_path = character_id_file_path_map.get(character_id)
    if character_file_path is None:
        return None

    try:
        char_desc = character.read_file(character_file_path, game_type, endianness)
    except utils.FileReadError as _:
        logger.info(f"Could not load character {character_file_path}")  # noqa: G004
        return None

    armature = bpy.data.armatures.new(name=char_desc.name)
    armature_object = bpy.data.objects.new(name=char_desc.name, object_data=armature)

    collection.objects.link(armature_object)

    context.view_layer.objects.active = armature_object
    bpy.ops.object.mode_set(mode='EDIT')

    for bone in char_desc.bones:
        armature_bone = armature.edit_bones.new(name=bone.name)

        armature_bone.length = 0.075
        armature_bone.matrix = mathutils.Matrix.LocRotScale(bone.translation, bone.rotation, None)
        armature_bone.matrix @= utils.BONE_ROTATION_OFFSET

    for bone_index, bone in enumerate(char_desc.bones):
        for child_index in bone.children:
            armature.edit_bones[child_index].parent = armature.edit_bones[bone_index]

    for bone in armature.edit_bones:
        if bone.parent and bone.head != bone.parent.head:
            previous_parent_tail = copy.copy(bone.parent.tail)
            previous_parent_quat = bone.parent.matrix.to_4x4().to_quaternion()
            bone.parent.tail = bone.head
            quaternion_difference = bone.parent.matrix.to_4x4().to_quaternion().dot(previous_parent_quat)
            if not math.isclose(quaternion_difference, 1.0, rel_tol=1e-05):
                bone.parent.tail = previous_parent_tail
            else:
                bone.use_connect = True

            if len(bone.children) == 0:
                bone.length = bone.parent.length

    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')

    return armature_object


def create_fcurve_data(action: bpy.types.Action, data_path: str, index: int, data: list[float]) -> None:
    """Create the fcurve data for all frames at once."""
    f_curve = action.fcurves.new(data_path, index=index)
    f_curve.keyframe_points.add(count=int(len(data) / 2))
    f_curve.keyframe_points.foreach_set("co", data)
    f_curve.update()


def import_animation(
    context: bpy.types.Context,
    logger: logging.Logger,
    file_path: pathlib.Path,
    game_type: utils.GameType | None,
    endianness: str | None,
    armature_object: bpy.types.Object,
) -> None:
    """Import an animation file."""
    anim_desc = None

    if game_type is not None and endianness is not None:
        try:
            anim_desc = animation.read_file(file_path, game_type, endianness)
        except utils.FileReadError as _:
            logger.info(f"Could not load animation {file_path}")  # noqa: G004
            return
    else:
        game_types = [x for x in utils.GameType for _ in range(2)]
        for game_type, endianness in zip(game_types, itertools.cycle(['<', '>'])):
            try:
                anim_desc = animation.read_file(file_path, game_type, endianness)
                break
            except utils.FileReadError as _:
                continue

    if anim_desc is None:
        logger.info(f"Could not load animation {file_path}")  # noqa: G004
        return

    if len(anim_desc.bones) != len(armature_object.data.bones):
        logger.info(f"Could not apply animation {anim_desc.name} to {armature_object.name}")  # noqa: G004
        return

    armature_object.animation_data_create()

    action = bpy.data.actions.get(anim_desc.name)
    if action is not None:
        armature_object.animation_data.action = action

        track = armature_object.animation_data.nla_tracks.new(prev=None)
        track.name = anim_desc.name
        track.strips.new(anim_desc.name, 1, action)

        return

    action = bpy.data.actions.new(name=anim_desc.name)
    armature_object.animation_data.action = action

    action.frame_range = (1.0, anim_desc.frame_count)

    for pose_bone, keyframes in zip(armature_object.pose.bones, anim_desc.bones):
        bone_rotation = pose_bone.bone.matrix_local.to_quaternion()

        rotation_keyframes_w = []
        rotation_keyframes_x = []
        rotation_keyframes_y = []
        rotation_keyframes_z = []
        for keyframe in keyframes.rotation_keyframes:
            frame = float(keyframe.frame + 1)

            rotation = ((bone_rotation.inverted() @ keyframe.rotation) @ bone_rotation).normalized()

            rotation_keyframes_w += (frame, rotation.w)
            rotation_keyframes_x += (frame, rotation.x)
            rotation_keyframes_y += (frame, rotation.y)
            rotation_keyframes_z += (frame, rotation.z)

        if rotation_keyframes_w:
            data_path = pose_bone.path_from_id("rotation_quaternion")
            create_fcurve_data(action, data_path, 0, rotation_keyframes_w)
            create_fcurve_data(action, data_path, 1, rotation_keyframes_x)
            create_fcurve_data(action, data_path, 2, rotation_keyframes_y)
            create_fcurve_data(action, data_path, 3, rotation_keyframes_z)

        scale_keyframes_x = []
        scale_keyframes_y = []
        scale_keyframes_z = []
        for keyframe in keyframes.scale_keyframes:
            frame = float(keyframe.frame + 1)

            scale = (mathutils.Matrix.LocRotScale(None, None, keyframe.vector) @ utils.BONE_ROTATION_OFFSET).to_scale()

            scale_keyframes_x += (frame, scale.x)
            scale_keyframes_y += (frame, scale.y)
            scale_keyframes_z += (frame, scale.z)

        if scale_keyframes_x:
            data_path = pose_bone.path_from_id("scale")
            create_fcurve_data(action, data_path, 0, scale_keyframes_x)
            create_fcurve_data(action, data_path, 1, scale_keyframes_y)
            create_fcurve_data(action, data_path, 2, scale_keyframes_z)

        location_keyframes_x = []
        location_keyframes_y = []
        location_keyframes_z = []
        for keyframe in keyframes.location_keyframes:
            frame = float(keyframe.frame + 1)

            location = bone_rotation.inverted() @ keyframe.vector

            location_keyframes_x += (frame, location.x)
            location_keyframes_y += (frame, location.y)
            location_keyframes_z += (frame, location.z)

        if location_keyframes_x:
            data_path = pose_bone.path_from_id("location")
            create_fcurve_data(action, data_path, 0, location_keyframes_x)
            create_fcurve_data(action, data_path, 1, location_keyframes_y)
            create_fcurve_data(action, data_path, 2, location_keyframes_z)

    track = armature_object.animation_data.nla_tracks.new(prev=None)
    track.name = anim_desc.name
    track.strips.new(anim_desc.name, 1, action)

    context.scene.render.fps = 60
    context.scene.frame_end = max(context.scene.frame_end, anim_desc.frame_count)


def import_model(
    context: bpy.types.Context,
    logger: logging.Logger,
    file_path: pathlib.Path,
    id_file_path_maps: id_file_path_map.IDFilePathMaps,
    *,
    import_animations: bool,
) -> list[bpy.types.Object]:
    """Import a model file."""
    model_desc = model.read_file(file_path)

    object_list = []

    file_collection = bpy.data.collections.new(model_desc.name)

    if file_collection.name not in context.collection.children:
        context.collection.children.link(file_collection)

    model_id = checksum.calculate(file_path.stem)

    if import_animations:
        armature_object = import_character(
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

    for object_index, object_desc in enumerate(model_desc.objects):
        object_collection_name = f"{model_desc.name} {object_index}"

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

            if armature_object:
                deform_layer = b_mesh.verts.layers.deform.verify()
                vertex_groups = [obj.vertex_groups.new(name=bone.name) for bone in armature_object.data.bones]

            for vertex_index in range(len(mesh_desc.indices) - 2):
                with contextlib.suppress(ValueError):
                    b_mesh.faces.new(
                        (
                            b_mesh.verts[mesh_desc.indices[vertex_index + 2]],
                            b_mesh.verts[mesh_desc.indices[vertex_index + 1]],
                            b_mesh.verts[mesh_desc.indices[vertex_index + 0]],
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

            if armature_object is not None:
                for vertex_index, (bones, weights) in enumerate(zip(mesh_desc.bones, mesh_desc.bone_weights)):
                    if weights is not None:
                        vertex = b_mesh.verts[vertex_index]
                        for bone_index, bone in enumerate(bones):
                            weight = weights[bone_index]
                            if weight > 0:
                                vertex[deform_layer][vertex_groups[bone].index] = float(weight) / 255.0

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

            if armature_object:
                bpy.ops.object.select_all(action='DESELECT')
                obj.select_set(state=True)
                armature_object.select_set(state=True)
                context.view_layer.objects.active = armature_object
                bpy.ops.object.parent_set(type='ARMATURE')
                bpy.ops.object.select_all(action='DESELECT')

            match model_desc.game:
                case utils.GameType.THESIMS:
                    texture_id_file_path_map = id_file_path_maps.the_sims.get()
                case utils.GameType.THESIMSBUSTINOUT:
                    texture_id_file_path_map = id_file_path_maps.the_sims_bustin_out.get()
                case utils.GameType.THEURBZ:
                    texture_id_file_path_map = id_file_path_maps.the_urbz.get()
                case utils.GameType.THESIMS2:
                    texture_id_file_path_map = id_file_path_maps.the_sims_2.get()
                case utils.GameType.THESIMS2PETS:
                    texture_id_file_path_map = id_file_path_maps.the_sims_2_pets.get()
                case utils.GameType.THESIMS2CASTAWAY:
                    texture_id_file_path_map = id_file_path_maps.the_sims_2_castaway.get()

            texture_id = texture_loader.lookup_shader_id_texture_id(mesh_desc.texture_id, model_desc.game)

            texture_file_path = texture_id_file_path_map.get(texture_id, None)

            if texture_file_path:
                texture_loader.create_material(obj, texture_file_path.stem, texture_file_path)

    if armature_object:
        animation_model_id = animation_id_lookup.get_animation_model_id_from_model_id(model_id, model_desc.game)

        animation_ids = animation_id_lookup.list_animation_ids_from_model_id(
            file_path.parent / "animations" / "quickdat.arc",
            model_desc.game,
            model_desc.endianness,
            animation_model_id,
        )

        for animation_id in animation_ids:
            animation_file_path = id_file_path_maps.animations.get().get(animation_id)
            if animation_file_path:
                import_animation(
                    context,
                    logger,
                    animation_file_path,
                    model_desc.game,
                    model_desc.endianness,
                    armature_object,
                )

        if armature_object.animation_data is not None and armature_object.animation_data.nla_tracks is not None:
            armature_object.animation_data.action = armature_object.animation_data.nla_tracks[0].strips[0].action

    return object_list


def import_files(
    context: bpy.types.Context,
    logger: logging.Logger,
    file_paths: list[pathlib.Path],
    *,
    import_animations: bool,
    cleanup_meshes: bool,
) -> None:
    """Import all the models in the selected files."""
    if bpy.ops.object.mode_set.poll():
        bpy.ops.object.mode_set(mode='OBJECT')

    if bpy.ops.object.select_all.poll():
        bpy.ops.object.select_all(action='DESELECT')

    id_file_path_maps = id_file_path_map.IDFilePathMaps(
        pathlib.Path(context.preferences.addons["io_scene_tsc"].preferences.the_sims_texture_directory),
        pathlib.Path(context.preferences.addons["io_scene_tsc"].preferences.the_sims_bustin_out_texture_directory),
        pathlib.Path(context.preferences.addons["io_scene_tsc"].preferences.the_urbz_texture_directory),
        pathlib.Path(context.preferences.addons["io_scene_tsc"].preferences.the_sims_2_texture_directory),
        pathlib.Path(context.preferences.addons["io_scene_tsc"].preferences.the_sims_2_pets_texture_directory),
        pathlib.Path(context.preferences.addons["io_scene_tsc"].preferences.the_sims_2_castaway_texture_directory),
        file_paths[0].parent / "characters",
        file_paths[0].parent / "animations",
    )

    object_list = []

    for file_path in file_paths:
        try:
            object_list += import_model(
                context,
                logger,
                file_path,
                id_file_path_maps,
                import_animations=import_animations,
            )
        except utils.FileReadError as _:  # noqa: PERF203
            if context.view_layer.objects.active is not None and context.view_layer.objects.active.type == 'ARMATURE':
                import_animation(
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

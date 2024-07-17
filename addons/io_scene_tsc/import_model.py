"""Import The Sims, The Sims Bustin' Out, The Urbz, The Sims 2, The Sims 2 Pets and The Sims 2 Castaway models."""

import bmesh
import bpy
import contextlib
import copy
import logging
import math
import mathutils
import pathlib
import struct
import typing


from . import animation
from . import character
from . import checksum
from . import model
from . import texture_loader
from . import utils


THE_SIMS_MODEL_ID_CHARACTER_ID_MAP = {
    0x8414147C: 0x64E0E172,  # blue_plate_sconce_a_00
    0x5BC8DEA: 0x9C9B1CAF,  # bottle_lamp_a_00
    0x5E13146F: 0x8DE4B3FD,  # carry_pizzabox_a_00
    0xCE23A4EF: 0x91E7088E,  # elite_reflections_chrome_lamp_a_00
    0x87AFD27C: 0xE63138FA,  # fight_3d_part
    0xF96953D1: 0x9CC7775E,  # halogen_heaven_lamp_by_contempto_a_00
    0x1274B029: 0x3A5EE732,  # hydrothera_bathtub_a_00
    0x9AEE727: 0xCD98A854,  # master_suite_tub_a_00
    0xCA88340B: 0xA2B792A8,  # oval_glass_sconce_a_00
    0x1DCC5C48: 0x85AFAB17,  # sani_queen_bathtub_a_00
    0x9CD3E29: 0x5E9076EB,  # top_brass_sconce_a_00
    0x24F1E2A2: 0x3E88D019,  # torchosterone_floor_lamp_a_00
    0xC890DFE1: 0x58A25BF4,  # torchosterone_table_lamp_a_00
    0xABCE6013: 0x419B5794,  # vanity_mirror_a_00
}


THE_SIMS_BUSTIN_OUT_MODEL_ID_CHARACTER_ID_MAP = {
    0x8414147C: 0x64E0E172,  # blue_plate_sconce_a_00
    0x5BC8DEA: 0x9C9B1CAF,  # bottle_lamp_a_00
    0xB29EE31A: 0x86D94398,  # cabinet_locker
    0x5E13146F: 0x8DE4B3FD,  # carry_pizzabox_a_00
    0xCE23A4EF: 0x91E7088E,  # elite_reflections_chrome_lamp_a_00
    0x87AFD27C: 0xE63138FA,  # fight_3d_part
    0xBF4F0A81: 0x868669BE,  # game_pooltable_club_x
    0xF96953D1: 0x9CC7775E,  # halogen_heaven_lamp_by_contempto_a_00
    0x1274B029: 0x3A5EE732,  # hydrothera_bathtub_a_00
    0x9D84F77C: 0x911367DE,  # lamp_garden_streetlamp_industrial_off
    0x7515D4F0: 0x9414BD62,  # lamp_table_x_gooseneck_widehead_off
    0x9AEE727: 0xCD98A854,  # master_suite_tub_a_00
    0xB1BE609A: 0x148FF674,  # o_lamp_wall_torch_arm_00
    0xCA88340B: 0xA2B792A8,  # oval_glass_sconce_a_00
    0x42D0B2AD: 0xB9665E3,  # pool_lshape
    0x1DCC5C48: 0x85AFAB17,  # sani_queen_bathtub_a_00
    0x9CD3E29: 0x5E9076EB,  # top_brass_sconce_a_00
    0x24F1E2A2: 0x3E88D019,  # torchosterone_floor_lamp_a_00
    0xC890DFE1: 0x58A25BF4,  # torchosterone_table_lamp_a_00
    0x2D24440B: 0xC5C69E99,  # zz_visit_tron
}


THE_URBZ_MODEL_ID_CHARACTER_ID_MAP = {
    0xFD7F6441: 0x24C58257,  # loading_dut
    0x89A7EA61: 0x24C58257,  # loading_english
    0x4D58E53C: 0x24C58257,  # loading_finn
    0xDC67C203: 0x24C58257,  # loading_fra
    0x5C986D7C: 0x24C58257,  # loading_ger
    0x816122B8: 0x24C58257,  # loading_ita
    0xBE91480: 0x24C58257,  # loading_japanese
    0xAF6D7C92: 0x24C58257,  # loading_kor
    0xE7D44FC: 0x24C58257,  # loading_norw
    0x45110D60: 0x24C58257,  # loading_pol
    0xF4BCC11A: 0x24C58257,  # loading_spa
    0x2AB2ED87: 0x24C58257,  # loading_tchinese
}


THE_SIMS_2_MODEL_ID_CHARACTER_ID_MAP = {
    0xFCDCC7AA: 0xDDA1A5D3,  # dm_bulldog
    0x6BF6C17F: 0xF2FF90C5,  # o_painting_eyetoy_2
    0x1CF1F1E9: 0xF2FF90C5,  # o_painting_eyetoy_3
    0x8295644A: 0xF2FF90C5,  # o_painting_eyetoy_4
    0xF59254DC: 0xF2FF90C5,  # o_painting_eyetoy_5
    0x6143FD5: 0x9F1D6E6F,  # o_painting_landscape_eyetoy_2
    0x71130F43: 0x9F1D6E6F,  # o_painting_landscape_eyetoy_3
    0xEF779AE0: 0x9F1D6E6F,  # o_painting_landscape_eyetoy_4
    0x9870AA76: 0x9F1D6E6F,  # o_painting_landscape_eyetoy_5
    0xA1DC2732: 0x38D57688,  # o_poster_eyetoy_2
    0xD6DB17A4: 0x38D57688,  # o_poster_eyetoy_3
    0x48BF8207: 0x38D57688,  # o_poster_eyetoy_4
    0x3FB8B291: 0x38D57688,  # o_poster_eyetoy_5
    0x82FAC10A: 0xFA1581E6,  # plumbing_bathtub_ornate_2x1
    0x14D1270F: 0xFA1581E6,  # plumbing_bathtub_ornate_2x1_empty_clean
    0x84ACF84F: 0xFA1581E6,  # plumbing_bathtub_ornate_new
    0x28261DF3: 0xFA1581E6,  # plumbing_bathtub_ornate_new_empty_clean
    0x1A8C4249: 0x94D1D6CA,  # plumbing_hottub_antigrav_doliphin
    0xEC5384BD: 0x94D1D6CA,  # plumbing_hottub_antigrav_waterblob
}


def get_character_id_from_model_id(model_name: str, model_id: int, game_type: utils.GameType) -> int:
    """Get the character ID from the model name or ID."""
    if model_name.startswith(("fa_", "af_")):
        return 0x1FB80AF4

    if model_name.startswith(("ma_", "am_")):
        return 0xFFA60350

    if game_type in (utils.GameType.THESIMS, utils.GameType.THESIMSBUSTINOUT) and model_name.startswith(
        ("fc_", "cf_", "mc_", "cm_"),
    ):
        return 0xD5E79699

    character_id = model_id

    match game_type:
        case utils.GameType.THESIMS:
            character_id = THE_SIMS_MODEL_ID_CHARACTER_ID_MAP.get(model_id, model_id)
        case utils.GameType.THESIMSBUSTINOUT:
            character_id = THE_SIMS_BUSTIN_OUT_MODEL_ID_CHARACTER_ID_MAP.get(model_id, model_id)
        case utils.GameType.THEURBZ:
            character_id = THE_URBZ_MODEL_ID_CHARACTER_ID_MAP.get(model_id, model_id)
        case utils.GameType.THESIMS2:
            character_id = THE_SIMS_2_MODEL_ID_CHARACTER_ID_MAP.get(model_id, model_id)

    return character_id


def read_animation_id(file: typing.BinaryIO, game_type: utils.GameType, endianness: str) -> int | None:
    """Read an animation id from a quickdat file."""
    file.read(8)

    animation_id = struct.unpack(endianness + 'I', file.read(4))[0]

    if game_type != utils.GameType.THESIMS:
        file.read(4)

    file.read(16)

    if animation_id != 0:
        return animation_id
    return None


def read_animation_ids_from_model_id(
    quickdat_file_path: pathlib.Path,
    game_type: utils.GameType,
    endianness: str,
    model_id: int,
) -> list[int]:
    """Read animation ids from a quickdat file."""
    # bustin' out map
    if game_type == utils.GameType.THESIMSBUSTINOUT and model_id == 0x50AE831:
        return [0x92D8AE4A, 0x30AA9779, 0x6BCF6EE9]

    # urbz map
    if game_type == utils.GameType.THEURBZ and model_id == 0x95B8888F:
        return [0x95B8888F]

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
        return [0x24C58257]

    match game_type:
        case utils.GameType.THESIMS:
            start_position = 1792483
            end_position = 1833523
        case utils.GameType.THESIMSBUSTINOUT:
            start_position = 2868768
            end_position = 2934816
        case utils.GameType.THEURBZ:
            start_position = 1567008
            end_position = 1615672
        case utils.GameType.THESIMS2:
            start_position = 982320
            end_position = 1040972
        case _:
            return []

    try:
        with quickdat_file_path.open(mode='rb') as file:
            file.seek(start_position)
            while True:
                if file.tell() > end_position:
                    break
                if struct.unpack(endianness + 'I', file.read(4))[0] != model_id:
                    file.seek(file.tell() - 3)
                else:
                    file.seek(file.tell() - 8)
                    break

            count = struct.unpack(endianness + 'I', file.read(4))[0]

            animation_ids = [read_animation_id(file, game_type, endianness) for _ in range(count)]
            animation_ids = [x for x in animation_ids if x is not None]

            return list(dict.fromkeys(animation_ids))

    except (OSError, struct.error) as _:
        return []


SIMS_2_MODEL_ID_ANIMATION_MODEL_ID_LOOKUP = {
    0x1A8C4249: 0xEC5384BD,
    0x1CF1F1E9: 0xF2FF90C5,
    0x3FB8B291: 0x38D57688,
    0x48BF8207: 0x38D57688,
    0x6143FD5: 0x9F1D6E6F,
    0x6BF6C17F: 0xF2FF90C5,
    0x71130F43: 0x9F1D6E6F,
    0x8295644A: 0xF2FF90C5,
    0x9870AA76: 0x9F1D6E6F,
    0xA1DC2732: 0x38D57688,
    0xD6DB17A4: 0x38D57688,
    0xEF779AE0: 0x9F1D6E6F,
    0xF59254DC: 0xF2FF90C5,
}


def get_animation_model_id_from_model_id(model_id: int, game_type: utils.GameType) -> int:
    """Get the animation model id from the model id."""
    animation_model_id = model_id
    match game_type:
        case utils.GameType.THESIMS2:
            animation_model_id = SIMS_2_MODEL_ID_ANIMATION_MODEL_ID_LOOKUP.get(model_id, model_id)

    return animation_model_id


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
    character_id = get_character_id_from_model_id(model_name, model_id, game_type)

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
        armature_bone.matrix = (
            mathutils.Matrix.LocRotScale(bone.translation, bone.rotation, None) @ utils.BONE_ROTATION_OFFSET
        )

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


def import_animation(
    context: bpy.types.Context,
    logger: logging.Logger,
    file_path: pathlib.Path,
    game_type: utils.GameType,
    endianness: str,
    armature_object: bpy.types.Object,
) -> None:
    """Import an animation file."""
    try:
        anim_desc = animation.read_file(file_path, game_type, endianness)
    except utils.FileReadError as _:
        logger.info(f"Could not load animation {file_path}")  # noqa: G004
        return

    armature_object.animation_data_create()

    action = bpy.data.actions.get(anim_desc.name)
    if action is not None:
        armature_object.animation_data.action = action
        return

    action = bpy.data.actions.new(name=anim_desc.name)
    armature_object.animation_data.action = action

    action.frame_range = (1.0, anim_desc.frame_count)

    for pose_bone, keyframes in zip(armature_object.pose.bones, anim_desc.bones):
        for keyframe in keyframes.rotation_keyframes:
            rotation = keyframe.rotation

            bone_rotation = pose_bone.bone.matrix_local.to_quaternion()

            pose_bone.rotation_quaternion = ((bone_rotation.inverted() @ rotation) @ bone_rotation).normalized()

            pose_bone.keyframe_insert(data_path="rotation_quaternion", frame=keyframe.frame + 1)

        for keyframe in keyframes.scale_keyframes:
            scale = keyframe.vector

            scale = mathutils.Matrix.LocRotScale(None, None, scale)

            pose_bone.scale = (scale @ utils.BONE_ROTATION_OFFSET).to_scale()

            pose_bone.keyframe_insert(data_path="scale", frame=keyframe.frame + 1)

        for keyframe in keyframes.location_keyframes:
            location = keyframe.vector

            bone_rotation = pose_bone.bone.matrix_local.to_quaternion().to_matrix()

            pose_bone.location = bone_rotation.inverted() @ location

            pose_bone.keyframe_insert(data_path="location", frame=keyframe.frame + 1)

    track = armature_object.animation_data.nla_tracks.new(prev=None)
    track.name = anim_desc.name
    track.strips.new(anim_desc.name, 1, action)

    context.scene.render.fps = 60
    context.scene.frame_end = max(context.scene.frame_end, anim_desc.frame_count)


def import_model(
    context: bpy.types.Context,
    logger: logging.Logger,
    file_path: pathlib.Path,
    the_sims_texture_list: dict[int, pathlib.Path],
    the_sims_bustin_out_texture_list: dict[int, pathlib.Path],
    the_urbz_texture_list: dict[int, pathlib.Path],
    the_sims_2_texture_list: dict[int, pathlib.Path],
    the_sims_2_pets_texture_list: dict[int, pathlib.Path],
    the_sims_2_castaway_texture_list: dict[int, pathlib.Path],
    character_id_file_path_map: dict[int, pathlib.Path],
    animation_id_file_path_map: dict[int, pathlib.Path],
    *,
    import_animations: bool,
) -> list[bpy.types.Object]:
    """Import a model file."""
    try:
        model_desc = model.read_file(file_path)
    except utils.FileReadError as _:
        logger.info(f"Could not load model {file_path}")  # noqa: G004
        return []

    object_list = []

    file_collection = bpy.data.collections.new(model_desc.name)

    if file_collection.name not in context.collection.children:
        context.collection.children.link(file_collection)

    model_id = checksum.calculate(file_path.stem)

    if import_animations:
        armature_object = import_character(
            context,
            logger,
            character_id_file_path_map,
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
                    texture_file_list = the_sims_texture_list
                case utils.GameType.THESIMSBUSTINOUT:
                    texture_file_list = the_sims_bustin_out_texture_list
                case utils.GameType.THEURBZ:
                    texture_file_list = the_urbz_texture_list
                case utils.GameType.THESIMS2:
                    texture_file_list = the_sims_2_texture_list
                case utils.GameType.THESIMS2PETS:
                    texture_file_list = the_sims_2_pets_texture_list
                case utils.GameType.THESIMS2CASTAWAY:
                    texture_file_list = the_sims_2_castaway_texture_list

            texture_id = texture_loader.lookup_shader_id_texture_id(mesh_desc.texture_id, model_desc.game)

            texture_file_path = texture_file_list.get(texture_id, None)

            if texture_file_path:
                texture_loader.create_material(obj, texture_file_path.stem, texture_file_path)

    if armature_object:
        animation_model_id = get_animation_model_id_from_model_id(model_id, model_desc.game)

        animation_ids = read_animation_ids_from_model_id(
            file_path.parent / "animations" / "quickdat.arc",
            model_desc.game,
            model_desc.endianness,
            animation_model_id,
        )

        for animation_id in animation_ids:
            animation_file_path = animation_id_file_path_map.get(animation_id)
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


def create_id_file_path_map(directory: pathlib.Path) -> dict[int, pathlib.Path]:
    """Create a map between checksum IDs and file paths."""
    if directory.is_dir():
        file_dict = {}
        for file_path in directory.glob("*"):
            file_dict[checksum.calculate(file_path.stem)] = file_path
        return file_dict
    return {}


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

    the_sims_texture_list = create_id_file_path_map(
        pathlib.Path(context.preferences.addons["io_scene_tsc"].preferences.the_sims_texture_directory),
    )

    the_sims_bustin_out_texture_list = create_id_file_path_map(
        pathlib.Path(context.preferences.addons["io_scene_tsc"].preferences.the_sims_bustin_out_texture_directory),
    )

    the_urbz_texture_list = create_id_file_path_map(
        pathlib.Path(context.preferences.addons["io_scene_tsc"].preferences.the_urbz_texture_directory),
    )

    the_sims_2_texture_list = create_id_file_path_map(
        pathlib.Path(context.preferences.addons["io_scene_tsc"].preferences.the_sims_2_texture_directory),
    )

    the_sims_2_pets_texture_list = create_id_file_path_map(
        pathlib.Path(context.preferences.addons["io_scene_tsc"].preferences.the_sims_2_pets_texture_directory),
    )

    the_sims_2_castaway_texture_list = create_id_file_path_map(
        pathlib.Path(context.preferences.addons["io_scene_tsc"].preferences.the_sims_2_castaway_texture_directory),
    )

    character_id_file_path_map = create_id_file_path_map(file_paths[0].parent / "characters")
    animation_id_file_path_map = create_id_file_path_map(file_paths[0].parent / "animations")

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
            the_sims_2_castaway_texture_list,
            character_id_file_path_map,
            animation_id_file_path_map,
            import_animations=import_animations,
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

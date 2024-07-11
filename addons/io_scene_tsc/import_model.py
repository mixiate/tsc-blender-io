"""Import The Sims, The Sims Bustin' Out, The Urbz, The Sims 2, The Sims 2 Pets and The Sims 2 Castaway models."""

import bmesh
import bpy
import contextlib
import logging
import mathutils
import pathlib
import struct
import typing


from . import animation
from . import character
from . import model
from . import texture_loader
from . import utils


THE_SIMS_CHARACTER_FILE_NAME_LOOKUP = {
    "blue_plate_sconce_a_00 8414147c": "blue_plate_sconce 64e0e172",
    "bottle_lamp_a_00 5bc8dea": "bottle_lamp 9c9b1caf",
    "carry_pizzabox_a_00 5e13146f": "carry_pizzabox 8de4b3fd",
    "elite_reflections_chrome_lamp_a_00 ce23a4ef": "elite_reflections_chrome_lamp 91e7088e",
    "fight_3d_part 87afd27c": "fighting_strip e63138fa",
    "halogen_heaven_lamp_by_contempto_a_00 f96953d1": "halogen_heaven_lamp_by_contempto 9cc7775e",
    "hydrothera_bathtub_a_00 1274b029": "hydrothera_bathtub 3a5ee732",
    "master_suite_tub_a_00 9aee727": "master_suite_tub cd98a854",
    "oval_glass_sconce_a_00 ca88340b": "oval_glass_sconce a2b792a8",
    "sani_queen_bathtub_a_00 1dcc5c48": "sani_queen_bathtub 85afab17",
    "top_brass_sconce_a_00 9cd3e29": "top_brass_sconce 5e9076eb",
    "torchosterone_floor_lamp_a_00 24f1e2a2": "torchosterone_floor_lamp 3e88d019",
    "torchosterone_table_lamp_a_00 c890dfe1": "torchosterone_table_lamp 58a25bf4",
    "vanity_mirror_a_00 abce6013": "vanity_mirror 419b5794",
}


THE_SIMS_BUSTIN_OUT_CHARACTER_FILE_NAME_LOOKUP = {
    "blue_plate_sconce_a_00 8414147c": "blue_plate_sconce 64e0e172",
    "bottle_lamp_a_00 5bc8dea": "bottle_lamp 9c9b1caf",
    "cabinet_locker b29ee31a": "cabinet_amoire_locker 86d94398",
    "carry_pizzabox_a_00 5e13146f": "carry_pizzabox 8de4b3fd",
    "elite_reflections_chrome_lamp_a_00 ce23a4ef": "elite_reflections_chrome_lamp 91e7088e",
    "fight_3d_part 87afd27c": "fighting_strip e63138fa",
    "game_pooltable_club_x bf4f0a81": "aristoscratch_pool_table 868669be",
    "halogen_heaven_lamp_by_contempto_a_00 f96953d1": "halogen_heaven_lamp_by_contempto 9cc7775e",
    "hydrothera_bathtub_a_00 1274b029": "hydrothera_bathtub 3a5ee732",
    "lamp_garden_streetlamp_industrial_off 9d84f77c": "lamp_garden_streetlamp_industrial 911367de",
    "lamp_table_x_gooseneck_widehead_off 7515d4f0": "lamp_table_x_gooseneck_widehead 9414bd62",
    "master_suite_tub_a_00 9aee727": "master_suite_tub cd98a854",
    "o_lamp_wall_torch_arm_00 b1be609a": "lamp_wall_torch_arm 148ff674",
    "oval_glass_sconce_a_00 ca88340b": "oval_glass_sconce a2b792a8",
    "pool_lshape 42d0b2ad": "pool_lshaped b9665e3",
    "sani_queen_bathtub_a_00 1dcc5c48": "sani_queen_bathtub 85afab17",
    "top_brass_sconce_a_00 9cd3e29": "top_brass_sconce 5e9076eb",
    "torchosterone_floor_lamp_a_00 24f1e2a2": "torchosterone_floor_lamp 3e88d019",
    "torchosterone_table_lamp_a_00 c890dfe1": "torchosterone_table_lamp 58a25bf4",
    "zz_visit_tron 2d24440b": "electronics_laser_light_show c5c69e99",
}


THE_URBZ_CHARACTER_FILE_NAME_LOOKUP = {
    "Loading_Dut 0xfd7f6441": "load_urbz_cas 24c58257",
    "Loading_English 0x89a7ea61": "load_urbz_cas 24c58257",
    "Loading_Finn 0x4d58e53c": "load_urbz_cas 24c58257",
    "Loading_Fra 0xdc67c203": "load_urbz_cas 24c58257",
    "Loading_Ger 0x5c986d7c": "load_urbz_cas 24c58257",
    "Loading_Ita 0x816122b8": "load_urbz_cas 24c58257",
    "Loading_Japanese 0xbe91480": "load_urbz_cas 24c58257",
    "Loading_Kor 0xaf6d7c92": "load_urbz_cas 24c58257",
    "Loading_Norw 0xe7d44fc": "load_urbz_cas 24c58257",
    "Loading_Pol 0x45110d60": "load_urbz_cas 24c58257",
    "Loading_Spa 0xf4bcc11a": "load_urbz_cas 24c58257",
    "Loading_tChinese 0x2ab2ed87": "load_urbz_cas 24c58257",
}


THE_SIMS_2_CHARACTER_FILE_NAME_LOOKUP = {
    "dm_bulldog fcdcc7aa": "dm dda1a5d3",
    "o_painting_eyetoy_2 6bf6c17f": "o_painting_eyetoy_1 f2ff90c5",
    "o_painting_eyetoy_3 1cf1f1e9": "o_painting_eyetoy_1 f2ff90c5",
    "o_painting_eyetoy_4 8295644a": "o_painting_eyetoy_1 f2ff90c5",
    "o_painting_eyetoy_5 f59254dc": "o_painting_eyetoy_1 f2ff90c5",
    "o_painting_landscape_eyetoy_2 6143fd5": "o_painting_landscape_eyetoy_1 9f1d6e6f",
    "o_painting_landscape_eyetoy_3 71130f43": "o_painting_landscape_eyetoy_1 9f1d6e6f",
    "o_painting_landscape_eyetoy_4 ef779ae0": "o_painting_landscape_eyetoy_1 9f1d6e6f",
    "o_painting_landscape_eyetoy_5 9870aa76": "o_painting_landscape_eyetoy_1 9f1d6e6f",
    "o_poster_eyetoy_2 a1dc2732": "o_poster_eyetoy_1 38d57688",
    "o_poster_eyetoy_3 d6db17a4": "o_poster_eyetoy_1 38d57688",
    "o_poster_eyetoy_4 48bf8207": "o_poster_eyetoy_1 38d57688",
    "o_poster_eyetoy_5 3fb8b291": "o_poster_eyetoy_1 38d57688",
    "plumbing_bathtub_ornate_2x1 82fac10a": "oriental_tub fa1581e6",
    "plumbing_bathtub_ornate_2x1_empty_clean 14d1270f": "oriental_tub fa1581e6",
    "plumbing_bathtub_ornate_new 84acf84f": "oriental_tub fa1581e6",
    "plumbing_bathtub_ornate_new_empty_clean 28261df3": "oriental_tub fa1581e6",
    "plumbing_hottub_antigrav_doliphin 1a8c4249": "plumbing_hottub_antigrav 94d1d6ca",
    "plumbing_hottub_antigrav_waterblob ec5384bd": "plumbing_hottub_antigrav 94d1d6ca",
}


def get_character_file_path_from_model_file_path(file_path: pathlib.Path, game_type: utils.GameType) -> pathlib.Path:
    """Get the character file path from the given model file path."""
    directory = file_path.parent
    file_name = file_path.stem.casefold()

    if file_name.startswith(("fa_", "af_")):
        return directory / "characters" / "female_adult 1fb80af4"

    if file_name.startswith(("ma_", "am_")):
        return directory / "characters" / "Male_adult ffa60350"

    if game_type in (utils.GameType.THESIMS, utils.GameType.THESIMSBUSTINOUT) and file_name.startswith(
        ("fc_", "cf_", "mc_", "cm_"),
    ):
        return directory / "characters" / "child d5e79699"

    match game_type:
        case utils.GameType.THESIMS:
            file_name = THE_SIMS_CHARACTER_FILE_NAME_LOOKUP.get(file_name, file_name)
        case utils.GameType.THESIMSBUSTINOUT:
            file_name = THE_SIMS_BUSTIN_OUT_CHARACTER_FILE_NAME_LOOKUP.get(file_name, file_name)
        case utils.GameType.THEURBZ:
            file_name = THE_URBZ_CHARACTER_FILE_NAME_LOOKUP.get(file_name, file_name)
        case utils.GameType.THESIMS2:
            file_name = THE_SIMS_2_CHARACTER_FILE_NAME_LOOKUP.get(file_name, file_name)

    return directory / "characters" / file_name


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


def read_animation_ids_from_model_id(  # noqa: C901 PLR0912
    quickdat_file_path: pathlib.Path,
    game_type: utils.GameType,
    endianness: str,
    model_id: int,
) -> list[int]:
    """Read animation ids from a quickdat file."""
    # bustin' out map
    if game_type == utils.GameType.THESIMSBUSTINOUT and model_id == 0x50AE831:  # noqa: PLR2004
        return [0x30AA9779, 0x92D8AE4A, 0x6BCF6EE9]

    # urbz map
    if game_type == utils.GameType.THEURBZ and model_id == 0x95B8888F:  # noqa: PLR2004
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

            return set(animation_ids)

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


def import_character(  # noqa: PLR0913
    context: bpy.types.Context,
    logger: logging.Logger,
    file_path: pathlib.Path,
    game_type: utils.GameType,
    endianness: str,
    collection: bpy.types.Collection,
) -> bpy.types.Object | None:
    """Import a character file."""
    character_file_path = get_character_file_path_from_model_file_path(file_path, game_type)
    if not character_file_path.is_file():
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
        armature_bone.head = mathutils.Vector((0.0, 0.0, 0.0))
        armature_bone.tail = mathutils.Vector((0.0, 0.1, 0.0))

        armature_bone.matrix = bone.matrix

    for bone_index, bone in enumerate(char_desc.bones):
        for child_index in bone.children:
            armature.edit_bones[child_index].parent = armature.edit_bones[bone_index]

    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')

    return armature_object


def import_animation(
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

    armature_object.animation_data.action = bpy.data.actions.new(name=anim_desc.name)

    for pose_bone, bone in zip(armature_object.pose.bones, anim_desc.bones):
        pose_bone.rotation_quaternion = bone.rotation
        pose_bone.scale = bone.scale
        pose_bone.location = bone.location

        pose_bone.keyframe_insert(data_path="rotation_quaternion", frame=1)
        pose_bone.keyframe_insert(data_path="scale", frame=1)
        pose_bone.keyframe_insert(data_path="location", frame=1)

    track = armature_object.animation_data.nla_tracks.new(prev=None)
    track.name = anim_desc.name
    track.strips.new(anim_desc.name, 1, armature_object.animation_data.action)


def import_model(  # noqa: C901 PLR0912 PLR0913 PLR0915
    context: bpy.types.Context,
    logger: logging.Logger,
    file_path: pathlib.Path,
    the_sims_texture_list: list[pathlib.Path],
    the_sims_bustin_out_texture_list: list[pathlib.Path],
    the_urbz_texture_list: list[pathlib.Path],
    the_sims_2_texture_list: list[pathlib.Path],
    the_sims_2_pets_texture_list: list[pathlib.Path],
    the_sims_2_castaway_texture_list: list[pathlib.Path],
    animation_file_list: list[pathlib.Path],
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

    if import_animations:
        armature_object = import_character(
            context,
            logger,
            file_path,
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
            texture_id_string = f'{texture_id:x}'

            for texture_file_path in texture_file_list:
                if texture_file_path.stem.endswith(texture_id_string):
                    texture_loader.create_material(obj, texture_file_path.stem, texture_file_path)

    if armature_object:
        model_id = int(file_path.stem.split()[-1], 16)
        animation_model_id = get_animation_model_id_from_model_id(model_id, model_desc.game)

        animation_ids = read_animation_ids_from_model_id(
            file_path.parent / "animations" / "quickdat.arc",
            model_desc.game,
            model_desc.endianness,
            animation_model_id,
        )

        for animation_file_path in animation_file_list:
            for animation_id in animation_ids:
                animation_id_string = f"{animation_id:x}"
                if animation_file_path.stem.endswith(animation_id_string):
                    import_animation(
                        logger,
                        animation_file_path,
                        model_desc.game,
                        model_desc.endianness,
                        armature_object,
                    )

        if armature_object.animation_data is not None and armature_object.animation_data.nla_tracks is not None:
            armature_object.animation_data.action = armature_object.animation_data.nla_tracks[0].strips[0].action

            # set bustin' out vehicles to default pose
            if "static_model" in armature_object.name:
                armature_object.animation_data.action = armature_object.animation_data.nla_tracks[-1].strips[0].action

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
    import_animations: bool,
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

    the_sims_2_castaway_texture_list = get_texture_file_list(
        context.preferences.addons["io_scene_tsc"].preferences.the_sims_2_castaway_texture_directory,
    )

    animations_directory = file_paths[0].parent / "animations"
    animation_file_list = list(animations_directory.glob("*"))

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
            animation_file_list,
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

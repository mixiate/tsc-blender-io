"""Import characters."""

import bpy
import copy
import logging
import math
import mathutils
import pathlib


from . import character
from . import character_id_lookup
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

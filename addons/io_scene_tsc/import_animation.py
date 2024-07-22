"""Import animations."""

import bpy
import itertools
import logging
import mathutils
import pathlib


from . import animation
from . import utils


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
    track.mute = True

    context.scene.render.fps = 60
    context.scene.frame_end = max(context.scene.frame_end, anim_desc.frame_count)

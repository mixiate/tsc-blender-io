"""Find and load textures for imported meshes."""

import bpy
import pathlib


def create_material(obj: bpy.types.Object, texture_name: str, texture_file_path: pathlib.Path) -> None:
    """Load the texture file, create a Blender material using it and add it to a material slot in the object."""
    material_list = [material.name.casefold() for material in bpy.data.materials]
    try:
        material_index = material_list.index(texture_name.casefold())
        material = bpy.data.materials[material_index]
    except ValueError as _:
        material = None

    if material is None:
        material = bpy.data.materials.new(name=texture_name)

        image = bpy.data.images.get(texture_file_path.as_posix())
        if image is None:
            image = bpy.data.images.load(texture_file_path.as_posix())
        material.use_nodes = True

        image_node = material.node_tree.nodes.new('ShaderNodeTexImage')
        image_node.image = image

        principled_bsdf = material.node_tree.nodes.get('Principled BSDF')
        material.node_tree.links.new(image_node.outputs[0], principled_bsdf.inputs[0])
        principled_bsdf.inputs[2].default_value = 1.0
        principled_bsdf.inputs[12].default_value = 0.0

        if texture_file_path.suffix.lower() == ".png":
            material.node_tree.links.new(image_node.outputs[1], principled_bsdf.inputs[4])
            material.blend_method = 'HASHED'

    if material.name not in obj.data.materials:
        obj.data.materials.append(material)

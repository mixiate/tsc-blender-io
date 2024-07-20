"""Load textures for imported models."""

import bpy
import pathlib


def create_material(obj: bpy.types.Object, shader_name: str, texture_file_path: pathlib.Path) -> None:
    """Load the texture file, create a Blender material using it and add it to a material slot in the object."""
    material_list = [material.name.casefold() for material in bpy.data.materials]
    try:
        material_index = material_list.index(shader_name.casefold())
        material = bpy.data.materials[material_index]
    except ValueError as _:
        material = None

    if material is None:
        material = bpy.data.materials.new(name=shader_name)

        image = bpy.data.images.get(texture_file_path.as_posix())
        if image is None:
            image = bpy.data.images.load(texture_file_path.as_posix())
        material.use_nodes = True

        image_node = material.node_tree.nodes.new('ShaderNodeTexImage')
        image_node.image = image

        principled_bsdf = material.node_tree.nodes.get('Principled BSDF')
        material.node_tree.links.new(image_node.outputs[0], principled_bsdf.inputs[0])
        principled_bsdf.inputs[2].default_value = 0.5
        principled_bsdf.inputs[12].default_value = 0.0

        if image.depth == 32:
            material.node_tree.links.new(image_node.outputs[1], principled_bsdf.inputs[4])
            material.blend_method = 'HASHED'

        specular_file_path = pathlib.Path(
            texture_file_path.parent,
            texture_file_path.stem + " specular" + texture_file_path.suffix,
        )
        if specular_file_path.is_file():
            specular_image = bpy.data.images.get(specular_file_path.as_posix())
            if specular_image is None:
                specular_image = bpy.data.images.load(specular_file_path.as_posix())

            specular_image_node = material.node_tree.nodes.new('ShaderNodeTexImage')
            specular_image_node.image = specular_image

            material.node_tree.links.new(specular_image_node.outputs[0], principled_bsdf.inputs[12])

    if material.name not in obj.data.materials:
        obj.data.materials.append(material)

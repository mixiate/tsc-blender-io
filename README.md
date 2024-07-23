### TSC Blender IO is an add-on for [Blender](https://www.blender.org/) which allows you to import models from The Sims, The Sims Bustin' Out, The Urbz, The Sims 2, The Sims 2 Pets and The Sims 2 Castaway.

Blender 4.1.1 is supported.

### Supported Games
- The Sims (Xbox)
- The Sims Bustin' Out (Xbox)
- The Urbz (Xbox)
- The Sims 2 (Xbox)
- The Sims 2 Pets (Wii)
- The Sims 2 Castaway (Wii)

### Features
- Import models with skeletons and animations
- Automatically load textures
- Option to attempt to cleanup meshes on import

### How To Use
- You will need to extract the archive files from each game in to folders like this example:
```
    The Sims 2
    ├───animations
    ├───characters
    ├───models
    ├───quickdat
    ├───shaders
    └───textures
```
- Only files from the supported versions above will work!
- Textures must be extracted to image files.
- To import a model, go to File -> Import -> Import The Sims, Bustin' Out, Urbz, 2, Pets, Castaway Model.
- Skeletons, object animations and textures will be automatically imported.
- To import a sim animation, select the armature you want to apply it to and then import the animation file.

### Known Issues
- Models will probably need to be cleaned up in some way for use elsewhere. There is an option to do this for you when importing. It will merge vertices and try to reconstruct sharp edges from the normals. You may want to do this manually for best results. Clear the custom split normals data if you want to redo them.
- Object models need to be flipped on the X axis. Sim parts, lots and other misc models do not need to be flipped.
- Some models from The Sims 2, The Sims 2 Pets and The Sims 2 Castaway are imported with incorrect normals.
- Some animal face parts from The Sims 2 Pets do not import.
- Game materials are not fully imported. Only the main texture is used.
- Some character skeletons are imported incorrectly.
- Animation keyframes are imported as is. The games have their own way of blending keyframes that is not recreated, so animations are not totally accurate.
- Animations from The Urbz have a lot of issues but are mostly correct.
- Some animations from The Sims 2 may have some slight issues also.
- Animation importing is not supported for The Sims 2 Pets and The Sims 2 Castaway.

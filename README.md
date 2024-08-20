### TSC Blender IO is an add-on for [Blender](https://www.blender.org/) which allows you to import models from The Sims, The Sims Bustin' Out, The Urbz, The Sims 2, The Sims 2 Pets, The Sims 2 Castaway and The Sims 3.

Blender 4.1.1 and 4.2 are supported.

### Supported Games
- The Sims (Xbox)
- The Sims Bustin' Out (Playstation 2, GameCube, Xbox)
- The Urbz (Xbox)
- The Sims 2 (Xbox)
- The Sims 2 Pets (Wii)
- The Sims 2 Castaway (Wii)
- The Sims 3 (Wii)

### Features
- Import models with skeletons and animations
- Automatically load textures
- Option to attempt to cleanup meshes on import

### How To Use
- You will need to extract these archive files from each game in to folders like this example:
```
    The Sims 2
    ├───animations
    ├───binaries
    ├───characters
    ├───models
    ├───quickdat
    ├───shaders
    └───textures
```
- Only files from the supported versions above will work!
- The Xbox versions are recommended where available as they have uncompressed vertex data.
- [Textures must be extracted to image files](https://github.com/mixsims/tsc-texture-extractor).
- To import a model, go to File -> Import -> The Sims, Bustin' Out, Urbz, 2, Pets, Castaway, 3.
- Skeletons, object animations and textures will be automatically imported.
- To import a sim animation, select the armature you want to apply it to and then import the animation file.

### Known Issues
- Models will probably need to be cleaned up in some way for use elsewhere. There is an option to do this for you when importing. It will merge vertices and try to reconstruct sharp edges from the normals. You may want to do this manually for best results. Clear the custom split normals data if you want to redo them.
- Object models are flipped on the X axis by setting their objects or armature scale to -1. You may need to account for this depending on what you are doing with them.
- Some object models from The Sims 2, Pets, Castaway and The Sims 3 have their normals flipped on the X axis. There is an option when importing to correct this.
- Some object models from The Sims 3 have inverted normals. There is an option when importing to correct this. You may need to use both normal fixes at once.
- Sim body variation models from The Sims 3 do not import correctly.
- Materials are not fully imported. Only the main texture is used.
- Some skeletons are imported without correctly connected bones.
- Animation keyframes are imported as is. The games have their own way of blending keyframes that is not recreated, so animations are not totally accurate.
- Animations from The Urbz and The Sims 3 have a lot of issues but are mostly correct.
- Some animations from The Sims 2, Pets and Castaway have some slight issues.

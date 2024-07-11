TSC Blender IO is an add-on for [Blender](https://www.blender.org/) which allows you to import models from The Sims, The Sims Bustin' Out, The Urbz, The Sims 2, The Sims 2 Pets and The Sims 2 Castaway.

Blender 4.1.1 is supported.

### Supported Games
- The Sims (Xbox)
- The Sims Bustin' Out (Xbox)
- The Urbz (Xbox)
- The Sims 2 (Xbox)
- The Sims 2 Pets (PS2, GC, Wii)
- The Sims 2 Castaway (Wii)

### Features
- Import models with skeletons and animations
- Automatically load textures (Set the directories in the add-on preferences)
- Option to attempt to cleanup meshes on import

### Known Issues
- Models will probably need to be cleaned up in some way for use elsewhere. There is an option to do this for you when importing. It will merge vertices and try to reconstruct sharp edges from the normals. You may want to do this manually for best results. Clear the custom split normals data if you want to redo them.
- Some models from The Sims 2, The Sims 2 Pets and The Sims 2 Castaway are imported with incorrect normals.
- Not all textures are found and loaded automatically.
- Some animal face parts from The Sims 2 Pets do not import.
- Animations are currently imported as single keyframe poses.
- Skeleton and animation importing is experimental and not perfect. You can turn off animation importing if necessary.
- If an object looks wrong, try changing the animation. The majority of objects have at least one animation pose that looks correct.
- Animated character skeletons are imported incorrectly.
- Animation importing is not supported for The Sims 2 Pets and The Sims 2 Castaway.

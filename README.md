TSC Blender IO is an add-on for [Blender](https://www.blender.org/) which allows you to import 3d models from The Sims, The Sims Bustin' Out, The Urbz and The Sims 2 for Xbox.

Blender 4.1.1 is supported.

### Features
- Import models from The Sims, The Sims Bustin' Out, The Urbz and The Sims 2 for Xbox
- Automatically load textures (Set the directories in the add-on preferences)
- Option to attempt to cleanup meshes on import

### Known Issues
- Only models from the Xbox versions of the games will work
- Models are imported without bones. As many objects are animated, their parts will be out of position and will need reconstructing.
- Models are separated in to 3 groups in the file. The first two are put in collections and the third is in vertex groups. You may need to do some separating or merging.
- Models will probably need to be cleaned up in some way for use elsewhere. There is an option to do this for you when importing. It will merge vertices and try to reconstruct sharp edges from the normals. You may want to do this manually for best results. Clear the custom split normals data if you want to redo them.
- Not all textures are found and loaded automatically
- Some models from The Sims 2 are imported with incorrect normals

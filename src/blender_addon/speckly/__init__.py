import sys

bl_info = {
        'name': 'Speckly for BlenderBIM',
        'author': 'return Name; team',
        'version': (0, 0, 1),
        'blender': (3, 0, 0),
        'location': '3d viewport toolbar (N), under the Speckly tab.',
        'category': 'Scene',
        'description': 'Speckly client to receive and execute chat commits within BlenderBIM.',
        'tracker_url': 'https://github.com/antonrafael/returnName/issues',
        'warning': '',
    }

if 'blender' in sys.executable:
    import bpy

    try:
        import specklepy
    except ModuleNotFoundError as error:
        print('Speckly add-on error: Speckle not found.')
        raise error

    try:
        import blenderbim
    except ModuleNotFoundError as error:
        print('Speckly add-on error: BlenderBIM not found.')
        raise error

    from bpy.app.handlers import persistent
    from .prop import SpecklyBranchObject, SpecklyStreamObject, SpecklyUserObject, SpecklySceneSettings
    from .operator import LoadSpecklyUsers, LoadSpecklyStreams, ApplySpecklyRequest
    from .ui import VIEW3D_PT_SpecklyUser, VIEW3D_PT_SpecklyStreams, VIEW3D_PT_SpecklyCommits

    classes = [
        SpecklyBranchObject, SpecklyStreamObject, SpecklyUserObject, SpecklySceneSettings,
        LoadSpecklyUsers, LoadSpecklyStreams, ApplySpecklyRequest,
        VIEW3D_PT_SpecklyUser, VIEW3D_PT_SpecklyStreams, VIEW3D_PT_SpecklyCommits
    ]
    props = {
        'speckly': bpy.props.PointerProperty(type=SpecklySceneSettings)
    }

    @persistent
    def load_handler(_):
        bpy.ops.speckly.users_load()

    def register():
        for cls in classes:
            bpy.utils.register_class(cls)

        for prop_name, prop_value in props.items():
            setattr(bpy.types.Scene, prop_name, prop_value)

        bpy.app.handlers.load_post.append(load_handler)

    def unregister():
        bpy.app.handlers.load_post.remove(load_handler)

        for prop_name in props.keys():
            delattr(bpy.types.Scene, prop_name)

        for cls in classes:
            bpy.utils.unregister_class(cls)

import bpy
from bpy_speckle.functions import _report
from bpy_speckle.operators.users import add_user_stream
from bpy_speckle.clients import speckle_clients
from specklepy.api.client import SpeckleClient
from specklepy.api.credentials import get_local_accounts
from .data import SpecklyData


class LoadSpecklyUsers(bpy.types.Operator):
    """Load all users from local user database"""

    bl_idname = 'speckly.users_load'
    bl_label = 'Load users'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        _report('Loading Speckly users...')
        SpecklyData.load_item('speckle')
        SpecklyData.load_item('speckly')
        users = SpecklyData.data['speckly'].users
        users.clear()
        speckle_clients.clear()
        profiles = get_local_accounts()

        for profile in profiles:
            user = users.add()
            user.server_name = profile.serverInfo.name or 'Speckle Server'
            user.server_url = profile.serverInfo.url
            user.name = profile.userInfo.name
            user.email = profile.userInfo.email
            user.company = profile.userInfo.company or ''
            user.authToken = profile.token
            try:
                client = SpeckleClient(host=profile.serverInfo.url, use_ssl='https' in profile.serverInfo.url)
                client.authenticate(user.authToken)
                speckle_clients.append(client)
            except Exception as ex:
                _report(ex)
                users.remove(len(users) - 1)
            if profile.isDefault:
                context.scene.speckly.active_user = str(len(users) - 1)

        # SpecklyData.data['speckly'].active_user_index = int(SpecklyData.data['speckly'].active_user)
        bpy.ops.speckly.load_speckly_streams()
        # bpy.context.view_layer.update()

        if context.area:
            context.area.tag_redraw()
        return {"FINISHED"}


class LoadSpecklyStreams(bpy.types.Operator):
    """Load all available streams for Speckly"""

    bl_idname = 'speckly.load_speckly_streams'
    bl_label = 'Load Speckly streams'
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = '(Re)load all available Speckly streams'

    def execute(self, context):
        # if not SpecklyData.is_loaded:
        #     SpecklyData.load()

        SpecklyData.load_item('exist_users')

        if SpecklyData.data['exist_users']:
            SpecklyData.load_item('user')
            SpecklyData.load_item('client')

            try:
                streams = SpecklyData.data['client'].stream.list(stream_limit=20)
            except Exception as e:
                _report(f'Failed to retrieve streams: {e}')
                return
            if not streams:
                _report('Failed to retrieve streams.')
                return

            user = SpecklyData.data['user']
            user.streams.clear()

            for s in streams:
                sstream = SpecklyData.data['client'].stream.get(id=s.id, branch_limit=20)
                add_user_stream(user, sstream)

            SpecklyData.load_item('stream')
            SpecklyData.load_item('branch')
            SpecklyData.load_item('commit')
            SpecklyData.load_item('connection')
            SpecklyData.load_item('bot_commit')

            # bpy.context.view_layer.update()
            return {'FINISHED'}

        if context.area:
            context.area.tag_redraw()
        return {'CANCELLED'}


class ApplySpecklyRequest(bpy.types.Operator):
    """Apply active Speckly commit to current project"""

    bl_idname = 'speckly.apply_commit'
    bl_label = 'Apply active Speckly commit'
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = 'Apply active Speckly commit'

    def execute(self, context):
        if not SpecklyData.is_loaded:
            SpecklyData.load()

        SpecklyData.apply_commit()
        return {'FINISHED'}

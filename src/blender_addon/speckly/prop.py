import bpy
from bpy.props import StringProperty, BoolProperty, IntProperty, FloatProperty, CollectionProperty, EnumProperty
from bpy_speckle.properties.scene import (
    SpeckleUserObject, SpeckleStreamObject, SpeckleBranchObject, SpeckleCommitObject
)
from .data import SpecklyData


class SpecklyBranchObject(SpeckleBranchObject):

    def get_commits(self, context):
        return super().get_commits(context)

    def set_commits(self, context):
        SpecklyData.load_item('commit')
        SpecklyData.load_item('connection')
        SpecklyData.load_item('bot_commit')

    commits: CollectionProperty(type=SpeckleCommitObject)
    commit: EnumProperty(name='Commit', description='Active commit', items=get_commits, update=set_commits)


class SpecklyStreamObject(SpeckleStreamObject):
    branches: CollectionProperty(type=SpecklyBranchObject)


class SpecklyUserObject(SpeckleUserObject):
    streams: CollectionProperty(type=SpecklyStreamObject)


class SpecklySceneSettings(bpy.types.PropertyGroup):
    users: CollectionProperty(type=SpecklyUserObject)

    def get_users(self, context):
        return [(str(i), f'{user.email} ({user.server_name})', user.server_url, i) for i, user in enumerate(self.users)]

    def set_user(self, context):
        bpy.ops.speckly.load_speckly_streams()

    user: StringProperty(name='User', description='Speckly user.', default='Speckly User')
    active_user: EnumProperty(items=get_users, name='Speckly user', description='Select user', update=set_user,
                              get=None, set=None)
    streams: EnumProperty(name='Available streams', description='Available streams associated with Speckly.', items=[])
    scale: FloatProperty(default=0.001)

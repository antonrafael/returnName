import bpy
from bpy_speckle.ui.view3d import VIEW3D_UL_SpeckleStreams
from .data import SpecklyData


class BaseSpecklyPanel(SpecklyData):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Speckly'
    bl_context = 'objectmode'

    def draw_base(self, context, no_users_label):
        if not SpecklyData.is_loaded:
            SpecklyData.load()

        layout = self.layout
        col = layout.column()

        if not SpecklyData.data['exist_users']:
            col.label(text=no_users_label)
        return layout, col

    @staticmethod
    def draw_stream(col, no_stream_label=None):
        stream = SpecklyData.data['stream']
        if stream is None and no_stream_label is not None:
            col.label(text=no_stream_label)

    @staticmethod
    def draw_branch(col, no_branch_label=None):
        branch = SpecklyData.data['branch']
        if branch is None and no_branch_label is not None:
            col.label(text=no_branch_label)

    @staticmethod
    def draw_commit(col, no_commit_label=None):
        commit = SpecklyData.data['commit']
        if commit is None and no_commit_label is not None:
            col.label(text=no_commit_label)


class VIEW3D_PT_SpecklyUser(BaseSpecklyPanel, bpy.types.Panel):
    """Speckly User Selector UI panel in the 3d viewport"""

    bl_label = 'Select Speckly Account'

    def draw(self, context):
        no_users_label = 'Setup Speckly token to begin.'
        layout, col = self.draw_base(context, no_users_label)
        if not SpecklyData.data['exist_users']: return

        col.prop(SpecklyData.data['speckly'], 'active_user', text='')
        user = SpecklyData.data['user']
        col.label(text=f'{user.name} ({user.email})')


class VIEW3D_PT_SpecklyStreams(BaseSpecklyPanel, bpy.types.Panel):
    """Speckly Streams UI panel in the 3d viewport"""

    bl_label = 'Select Project Stream'

    def draw(self, context):
        no_users_label = 'No streams found for Speckly.'
        layout, col = self.draw_base(context, no_users_label)
        if not SpecklyData.data['exist_users']: return

        user = SpecklyData.data['user']
        stream = SpecklyData.data['stream']
        self.draw_stream(col)
        if stream is None: return

        col.template_list('VIEW3D_UL_SpeckleStreams', '', user, 'streams', user, 'active_stream')
        row = col.row()
        row.operator('speckly.load_speckly_streams', text='Reload', icon='FILE_REFRESH')
        col.separator()
        row = col.row()
        row.label(text=f'Branch:')
        row = col.row()
        row.prop(stream, 'branch', text='')


class VIEW3D_PT_SpecklyCommits(BaseSpecklyPanel, bpy.types.Panel):
    """Speckly Commits UI panel in the 3d viewport"""

    bl_label = 'Select Request'

    def draw(self, context):
        no_users_label = 'No commits found for Speckly.'
        layout, col = self.draw_base(context, no_users_label)
        if not SpecklyData.data['exist_users']: return

        stream = SpecklyData.data['stream']
        branch = SpecklyData.data['branch']
        commit = SpecklyData.data['commit']

        no_stream_label = 'No commits found for Speckly.'
        self.draw_stream(col, no_stream_label)
        if stream is None: return

        no_branch_label = 'No branches found for Speckly.'
        self.draw_branch(col, no_branch_label)
        if branch is None: return

        row = col.row()
        row.prop(branch, 'commit', text='')
        self.draw_commit(col)
        if commit is None: return

        self.draw_request(col)
        if len(SpecklyData.data['elements']) < 5: return
        row = col.row()
        row.operator('speckly.apply_commit', text='Apply to project', icon='FILE_TICK')

        request_result = SpecklyData.data['request_result']
        if request_result == '': return
        row = col.row()
        row.label(text=request_result)

    def draw_request(self, col):
        if SpecklyData.data['elements'] is None:
            row = col.row()
            row.label(text=f'Not a Speckly request!')
            return

        for curr_elements, detail in zip(SpecklyData.data['elements'], SpecklyData.data['request_details']):
            elements_fmt = curr_elements
            if 'fmt' in detail:
                if not isinstance(detail['fmt'], list):
                    detail['fmt'] = [detail['fmt']]
                elements_fmt = [f'{element:{fmt}}' for element, fmt in zip(elements_fmt, detail['fmt'])]
            txt = detail['txt']
            for element in elements_fmt:
                txt = txt.replace('__', element, 1)
            row = col.row()
            row.label(text=txt)

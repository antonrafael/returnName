from datetime import datetime
import bpy
from bpy_speckle.clients import speckle_clients
from blenderbim import tool
import mathutils
from .io import SpeckleConnection, BotCommit


class SpecklyData:
    data: dict = {}
    is_loaded: bool = False

    @classmethod
    def load_item(cls, item):
        if item == 'speckle':
            cls.data['speckle'] = cls.speckle
        elif item == 'speckly':
            cls.data['speckly'] = cls.speckly
        elif item == 'user':
            cls.data['user'] = cls.user
        elif item == 'client':
            cls.data['client'] = cls.client
        elif item == 'stream':
            cls.data['stream'] = cls.stream
        elif item == 'branch':
            cls.data['branch'] = cls.branch
        elif item == 'commit':
            cls.data['commit'] = cls.commit
        elif item == 'exist_users':
            cls.data['exist_users'] = cls.exist_users
        elif item == 'connection':
            cls.data['connection'] = cls.setup_connection()
        elif item == 'bot_commit':
            bot_commit, elements, request_details = cls.bot_commit_details
            cls.data['bot_commit'] = bot_commit
            cls.data['elements'] = elements
            cls.data['request_details'] = request_details
        else:
            raise ValueError(f'Non existent item {item}')

    @classmethod
    def load(cls):
        for item in [
            'speckle', 'speckly', 'user', 'client', 'stream', 'branch', 'commit', 'exist_users', 'connection',
            'bot_commit'
        ]:
            cls.load_item(item)
        cls.data['request_result'] = ''
        cls.is_loaded = True

    @classmethod
    @property
    def speckle(cls):
        return bpy.data.scenes[0].speckle

    @classmethod
    @property
    def speckly(cls):
        return bpy.data.scenes[0].speckly

    @classmethod
    @property
    def exist_users(cls):
        return False if len(cls.data['speckly'].users) == 0 else True

    @classmethod
    def ifc_class(cls, element_type):
        ifc_classes = {
            'beam': 'IfcBeam',
            'wall': 'IfcWall',
            'slab': 'IfcSlab',
            'column': 'IfcColumn'
        }
        return ifc_classes[element_type] if element_type in ifc_classes else None

    @classmethod
    def get_ifc_element(cls, element_name, ifc_class):
        if ifc_class is None:
            return None
        else:
            file = tool.Ifc.get()
            cls.data['file'] = file
            if file is None: return None
            elements = cls.data['file'].by_type(ifc_class)
            elements_dict = {element.Name: element for element in elements}
            return elements_dict[element_name] if element_name in elements_dict else None

    @classmethod
    def get_bl_element(cls, ifc_element):
        if ifc_element is None: return None
        matches = [obj for obj in bpy.data.objects
                   if obj.BIMObjectProperties.ifc_definition_id == ifc_element.id()]
        return None if len(matches) == 0 else matches[0]

    @classmethod
    def move(cls, bl_element, disp_vector):
        bl_element.location += mathutils.Vector(disp_vector)

    @classmethod
    def apply_commit(cls):
        ifc_class = cls.ifc_class(cls.data['element_type'])
        if ifc_class is None:
            cls.data['request_result'] = 'IFC class not found!'
            return
        ifc_element = cls.get_ifc_element(cls.data['element_name'], ifc_class)
        if ifc_element is None:
            cls.data['request_result'] = 'IFC element not found!'
            return
        bl_element = cls.get_bl_element(ifc_element)
        if bl_element is None:
            cls.data['request_result'] = 'Blender element not found!'
            return
        cls.move(bl_element, cls.data['disp_vector'])
        cls.data['request_result'] = 'Done!'

    @classmethod
    @property
    def user(cls):
        return cls.data['speckly'].users[int(cls.data['speckly'].active_user)]

    @classmethod
    @property
    def client(cls):
        return speckle_clients[int(cls.data['speckly'].active_user)]

    @classmethod
    @property
    def stream(cls):
        user = cls.data['user']
        return None if len(user.streams) == 0 else user.streams[user.active_stream]

    @classmethod
    @property
    def branch(cls):
        stream = cls.data['stream']
        return None if len(stream.branches) == 0 else stream.branches[int(stream.branch)]

    @classmethod
    @property
    def commit(cls):
        branch = cls.data['branch']
        return None if len(branch.commits) == 0 else branch.commits[int(branch.commit)]

    @classmethod
    def setup_connection(cls):
        connection = SpeckleConnection(token=cls.data['user'].authToken)
        connection.stream_id = cls.data['stream'].id
        connection.branch_name = cls.data['branch'].name
        connection.commit_id = cls.data['commit'].id
        connection.setup_server_transport()
        return connection

    @classmethod
    @property
    def bot_commit_details(cls):
        commit = cls.data['commit']
        bot_commit = cls.data['connection'].receive()
        if not isinstance(bot_commit, BotCommit) or not hasattr(bot_commit, 'request'):
            request = None
            request_details = None
            elements = None
        else:
            request = bot_commit.request
            request_details = [
                {'obj': bot_commit, 'attr': 'user_id', 'txt': f'Request by: __'},
                {'obj': commit, 'attr': 'created_at', 'func': cls.request_time, 'txt': f'On: __'},
                {'obj': request, 'item': 'field', 'txt': f'Field: __'},
                {'obj': request, 'item': ['element', 'element_name'], 'txt': f'Element: __ __'},
                {'obj': request,
                 'item': ['number', 'unit', 'direction'], 'fmt': ['.3f', '', ''], 'txt': f'Displacement: __ __ __'}
            ]
            elements = cls.get_requested_elements(request_details)
        cls.store_bot_commit_params(request)
        return bot_commit, elements, request_details

    @classmethod
    def store_bot_commit_params(cls, request):
        cls.data['element_type'] = request['element'] if 'element' in request else ''
        cls.data['element_name'] = request['element_name'] if 'element_name' in request else ''
        cls.setup_unit_vector(request['direction'])

    @classmethod
    def setup_unit_vector(cls, direction):
        vectors = {
            'up': mathutils.Vector((0., 0., 1.)),
            'down': mathutils.Vector((0., 0., -1.)),
            'front': mathutils.Vector((0., -1., 0.)),
            'back': mathutils.Vector((0., 1., 0.)),
            'left': mathutils.Vector((-1., 0., 0.)),
            'right': mathutils.Vector((1., 0., 0.))
        }
        if direction not in vectors:
            cls.data['request_result'] = 'Unknown direction!'
            cls.data['disp_vector'] = mathutils.Vector((0., 0., 0.))
        cls.data['disp_vector'] = vectors[direction]

    @staticmethod
    def request_time(created_at):
        return datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S.%f%Z').ctime()

    @staticmethod
    def get_requested_elements(request_details):
        elements = []
        for detail in request_details:
            curr_elements = []
            all_attributes_found = False
            if 'attr' in detail:
                if not isinstance(detail['attr'], list):
                    detail['attr'] = [detail['attr']]
                for attr in detail['attr']:
                    if not hasattr(detail['obj'], attr):
                        break
                    element = getattr(detail['obj'], attr)
                    if 'func' in detail:
                        element = detail['func'](element)
                    curr_elements.append(element)
                else:
                    all_attributes_found = True
            elif 'item' in detail:
                if not isinstance(detail['item'], list):
                    detail['item'] = [detail['item']]
                for item in detail['item']:
                    if item not in detail['obj']:
                        break
                    element = detail['obj'][item]
                    if 'func' in detail:
                        element = detail['func'](element)
                    curr_elements.append(element)
                else:
                    all_attributes_found = True
            else:
                break
            if not all_attributes_found:
                break
            elements.append(curr_elements)
        return elements

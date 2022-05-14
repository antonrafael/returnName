from dataclasses import dataclass
from collections import OrderedDict
from pathlib import Path
import sys
import copy
import json
import re
import requests
import pandas as pd
from transformers import pipeline

path = Path().resolve().parent.parent
sys.path.append(str(path))

from returnName.nlp.speckle_io import SpeckleConnection, BotCommit
from returnName.nlp.my_token import token
from returnName.nlp.my_token_hf import token_hf

# from speckle_io import SpeckleConnection, BotCommit
# from my_token import token

hugging_face_inference = False


def query_hf(payload, model_id, api_token):
    headers = {'Authorization': f'Bearer {api_token}'}
    API_URL = f'https://api-inference.huggingface.co/models/{model_id}'
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()


class NLPModels:
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(NLPModels, cls).__new__(cls)
            model_zero_shot = 'facebook/bart-large-mnli'
            model_question_answerer = 'distilbert-base-cased-distilled-squad'
            if hugging_face_inference:
                cls.zero_shot = lambda x: query_hf(x, model_zero_shot, token_hf)
                cls.question_answerer = lambda x: query_hf(x, model_question_answerer, token_hf)
            else:
                cls.zero_shot = pipeline('zero-shot-classification', model=model_zero_shot)
                cls.question_answerer = pipeline('question-answering', model=model_question_answerer)
        return cls.instance


@dataclass
class NLPModelsHelper:
    zero_shot_threshold: float = 0.6

    def __post_init__(self):
        self.nlp_models = NLPModels()

    def zero_shot(self, prompt, candidate_label):
        return (self.nlp_models.zero_shot(prompt, candidate_labels=[candidate_label])['scores'][0]
                > self.zero_shot_threshold)

    def zero_shot_multiple(self, prompt, candidate_labels):
        df = pd.DataFrame(self.nlp_models.zero_shot(prompt, candidate_labels=candidate_labels))
        return df.iloc[df['scores'].idxmax()]['labels']

    def question_answerer(self, question, context):
        return self.nlp_models.question_answerer(question=question, context=context)['answer']


class BotMessages:
    @staticmethod
    def message_welcoming(user_txt):
        answer = f'Hi{user_txt}! I am Speckly, the friendly agent for your interactions with the Speckle '
        answer += 'universe. I was created for the scope of the Hackathon *Into The Speckleverse*, in May 2022, '
        answer += 'by the awesome team *return Name;* and I am ready to translate your words into commits to the '
        answer += 'Speckle Server. Do you want to start? Great, just tell me a Stream ID and start requiring '
        answer += 'changes. Remember that you need to start your message with **!speckly** for me to notice. '
        answer += 'See you around!'
        return answer

    @staticmethod
    def message_not_request(user_txt):
        answer = f'Hey{user_txt}! I can only accept requests to move elements within a BIM model. '
        answer += f"I didn't understand very well what you said. Could you please try again?"
        return answer

    @staticmethod
    def message_linking_stream(user_txt, stream_id):
        answer = f'Hey there{user_txt}! Alright, from now on, '
        answer += f"I'm linking the comments I receive on this channel to stream {stream_id}."
        return answer

    @staticmethod
    def message_no_stream(user_txt):
        answer = f'Hey there{user_txt}! Before anything else, someone should tell me to which Speckle Stream I am '
        answer += 'expected to push my commits within this channel. For more info about me, type '
        answer += '**!speckly hello**.'
        return answer

    @staticmethod
    def message_connection_error(user_txt):
        answer = f'Sorry{user_txt}, an error occurred while attempting to commit to the Speckle Server. '
        answer += f'Please, kindly revise the data and try again.'
        return answer

    @staticmethod
    def message_commit_ok(user_txt, server, stream_id, commit_id):
        answer = f'Ok{user_txt}, green light then! your request has been committed (id: {commit_id}). '
        answer += f'Now you can pull it from within the authoring software.\n'
        answer += f'https://{server}/streams/{stream_id}/commits/{commit_id}.'
        return answer

    @staticmethod
    def message_commit_not_ok(user_txt):
        return f'No? Ok{user_txt}, noted! If you happen to change your mind, here I am!'


@dataclass
class NLPField(NLPModelsHelper):
    name: str = ''
    other_names: list = None

    def __post_init__(self):
        super().__post_init__()
        self.directions = ['up', 'down', 'front', 'back', 'left', 'right']
        self.other_names = [] if self.other_names is None else self.other_names

    @property
    def nlp_recipe(self):
        return OrderedDict({
            'element': {
                'func': self.which_element,
                'args': 'prompt'
            },
            'element_name': {
                'func': self.element_name,
                'args': ['prompt', 'element']
            },
            'action': {
                'func': self.action,
                'args': ['prompt', 'element', 'element_name']
            },
            'direction': {
                'func': self.direction,
                'args': 'prompt'
            },
            'amount': {
                'func': self.amount,
                'args': 'action'
            },
            'number_unit': {
                'func': self.amount_breakdown,
                'args': 'amount',
                'readable_value_name': 'amount'
            }
        })

    @property
    def parsed_items_to_discard(self):
        return ['prompt', 'action', 'amount', 'number_unit']

    @property
    def all_field_names(self):
        return [self.name] if len(self.other_names) == 0 else self.other_names

    def belongs(self, name):
        return True if name in self.all_field_names else False

    def found_inside(self, prompt):
        if self.zero_shot(prompt, self.name):
            return True
        else:
            for name in self.other_names:
                if self.zero_shot(prompt, name):
                    return True
            return False

    def which_element(self, prompt):
        candidate = self.zero_shot_multiple(prompt, self.elements)
        return candidate if self.zero_shot(prompt, candidate) else None

    def element_name(self, prompt, element):
        question = f'Which is the name of the {element}?'
        name = self.question_answerer(question, prompt)
        return None if name == '' else name.split()[0]

    def action(self, prompt, element, element_name):
        question = f'What should we do with the {element} {element_name}?'
        return self.question_answerer(question, prompt)

    def direction(self, prompt):
        return self.zero_shot_multiple(prompt, self.directions)

    def amount(self, prompt):
        question = f'By how much?'
        return self.question_answerer(question, prompt)

    def amount_breakdown(self, amount):
        numbers = re.findall(r'(?<![a-zA-Z:])[-+]?\d*\.?\d+', amount)
        unit = None
        if len(numbers) == 0:
            elements = amount.split()
            number_found = False
            for element in elements:
                if self.zero_shot(element, 'number'):
                    number = element
                    elements.remove(number)
                    number = float(self.zero_shot_multiple(number, [str(i) for i in range(10)]))
                    number_found = True
                    break
            if not number_found:
                return None
            unit = elements[-1]
        else:
            number = numbers[0]
        if unit is None:
            unit = ''.join([letter for letter in amount if letter.isalnum() and not letter.isdigit()])
            unit = 'm' if unit == '' else unit  # defaulting to meters
        unit_names_short = ['m', 'cm', 'mm', 'in']
        unit_names_long = ['meters', 'centimeters', 'millimeters', 'inches']
        factors = [1., 1e-2, 1e-3, 0.0254]
        unit_names = [*unit_names_short, *unit_names_long]
        unit_idx = [idx for idx, u in enumerate(unit_names) if u == unit]
        if len(unit_idx) == 0:
            unit = self.zero_shot_multiple(unit, unit_names)
            unit_idx = [idx for idx, u in enumerate(unit_names) if u == unit][0]
        else:
            unit = [*unit_names_short, *unit_names_short][unit_idx[0]]
            unit_idx = unit_idx[0]
        number = [*factors, *factors][unit_idx] * float(number)
        return number, 'm'

    def on_fail(self, item, parsed_items=None):
        if parsed_items is None:
            txt = 'Sorry, '
        else:
            txt = f'Hey! I understood {self.summary(parsed_items)}. However, '
        txt += f'I could not understand which {item} you are talking about. '
        txt += f'Would you mind to rephrase it in a clear way for me and try again? Thanks in advance!'
        return txt

    def discard_items(self, parsed_items):
        return {key: value for key, value in parsed_items.items() if key not in self.parsed_items_to_discard}

    @staticmethod
    def parse_amount(parsed_items):
        parsed_items['number'], parsed_items['unit'] = parsed_items['number_unit']
        return parsed_items

    @staticmethod
    def summary(parsed_items):
        txt = ''
        if 'element' not in parsed_items:
            return 'you are placing a request'
        txt += f'a {parsed_items["element"]}'
        if 'element_name' not in parsed_items:
            return txt
        txt += f' named {parsed_items["element_name"]}'
        if 'direction' not in parsed_items:
            return txt
        txt += f' is requested to be moved {parsed_items["direction"]}'
        if 'number' not in parsed_items:
            return txt
        txt += f' by {parsed_items["number"]:.3f} {parsed_items["unit"]}'
        return txt

    def on_success(self, parsed_items, user_name=None):
        user_txt = '' if user_name is None else f' @{user_name}'
        txt = f'Hey there{user_txt}! Perfect, I understood that {self.summary(parsed_items)}. '
        txt += f'Do you want to commit that action to the Speckle Server?'
        return txt

    def process_one_step(self, value_name, parsed_items, func, args=None, readable_value_name=None):
        if args is None:
            args = []
        else:
            args = args if isinstance(args, list) else [args]
            args = [parsed_items[arg] for arg in args]
        value = func(*args)
        if value is None:
            value_name = value_name if readable_value_name is None else readable_value_name
            return {**parsed_items, **{'answer': self.on_fail(value_name, parsed_items)}}
        parsed_items[value_name] = value
        return parsed_items

    def process_prompt(self, prompt, user_name=None):
        parsed_items = {'success': False, 'prompt': prompt}
        for step_name, step_data in self.nlp_recipe.items():
            func = step_data['func']
            args = step_data['args'] if 'args' in step_data else []
            readable_value_name = step_data['readable_value_name'] if 'readable_value_name' in step_data else None
            parsed_items = self.process_one_step(step_name, parsed_items, func, args, readable_value_name)
            if step_name not in parsed_items:
                return self.discard_items(parsed_items)
        parsed_items['success'] = True
        parsed_items = self.parse_amount(parsed_items)
        parsed_items = self.discard_items(parsed_items)
        return {**parsed_items, **{'answer': self.on_success(parsed_items, user_name=user_name)}}


@dataclass
class NLPStructuralField(NLPField):
    def __post_init__(self):
        super().__post_init__()
        self.name = 'structural'
        self.elements = ['wall', 'slab', 'beam', 'column']
        self.other_names = ['structural', *self.elements]


@dataclass
class NLPMepField(NLPField):
    def __post_init__(self):
        super().__post_init__()
        self.name = 'MEP'
        self.other_names = ['mechanical', 'electrical', 'plumbing', 'fire protection']
        self.elements = ['duct', 'pipe', 'tray']


@dataclass
class NLPAgent(NLPModelsHelper, BotMessages):
    active_users_filename: str = 'active_users.json'
    channel_streams_filename: str = 'channel_streams.json'
    connection: ... = None

    def __post_init__(self):
        self.fields = self.setup_fields()
        self.nlp_models = NLPModels()
        self.active_users = self.load_active_users()
        self.channel_streams = self.load_channel_streams()

    @property
    def active_users_path(self):
        return Path().resolve() / self.active_users_filename

    @property
    def channel_streams_path(self):
        return Path().resolve() / self.channel_streams_filename

    @staticmethod
    def load_json(filepath):
        if filepath.exists():
            with open(filepath, 'r+') as f:
                json_data = json.load(f)
        else:
            json_data = {}
        return json_data

    def load_active_users(self):
        return self.load_json(self.active_users_path)

    def load_channel_streams(self):
        return self.load_json(self.channel_streams_path)

    @staticmethod
    def save_json(json_data, filepath):
        with open(filepath, 'w') as f:
            json.dump(json_data, f)

    def save_active_users(self):
        self.save_json(self.active_users, self.active_users_path)

    def save_channel_streams(self):
        self.save_json(self.channel_streams, self.channel_streams_path)

    def setup_connection(self, stream_id):
        self.connection = SpeckleConnection(token=token, stream_id=stream_id)

    def commit(self, user_id, request):
        bot_commit = BotCommit(user_id=user_id, request=request)
        return self.connection.send_to_stream(bot_commit, f'Request from {user_id} in the chat')

    @staticmethod
    def setup_fields():
        return [NLPStructuralField(), NLPMepField()]

    @property
    def all_field_names(self):
        names = []
        for field in self.fields:
            names.extend(field.all_field_names)
        return names

    def which_field(self, name):
        for field in self.fields:
            if field.belongs(name):
                return field.name
        return None

    def field_by_name(self, name):
        for field in self.fields:
            if field.name == name:
                return field
        return None

    def process_prompt(self, prompt, user_name=None, channel_id=None):
        user_txt = '' if user_name is None else f' @{user_name}'
        if not self.zero_shot(prompt, candidate_label='request'):
            return {'success': False, 'answer': self.message_not_request(user_txt)}
        if 'stream' in prompt.lower():
            stream_id = self.question_answerer('what is the stream id?', prompt)
            stream_id = stream_id.split()[-1]
            if len(stream_id) == 10:
                self.channel_streams[channel_id] = stream_id
                self.save_channel_streams()
                return {'success': False, 'answer': self.message_linking_stream(user_txt, stream_id)}
            elif channel_id not in self.channel_streams:
                return {'success': False, 'answer': self.message_not_request(user_txt)}
        related_field = self.zero_shot_multiple(prompt, self.all_field_names)
        related_field = self.which_field(related_field)
        field = self.field_by_name(related_field)
        return {**{'field': related_field}, **field.process_prompt(prompt, user_name=user_name)}

    def push_prompt(self, user, prompt, channel_id, debug=False):
        user_txt = '' if user is None else f' @{user}'
        if prompt.lower() == 'hello':
            return {'answer': self.message_welcoming(user_txt)}
        if channel_id not in self.channel_streams and 'stream' not in prompt.lower():
            return {'answer': self.message_no_stream(user_txt)}
        if user in self.active_users:
            second_comment = self.check_if_second_comment(user, user_txt, channel_id, prompt)
            if second_comment is not None:
                return second_comment
        request = self.process_prompt(prompt, user_name=user, channel_id=channel_id)
        if 'success' in request and request['success']:
            self.active_users[user] = {'active': True, 'request': request}
            self.save_active_users()
        if debug:
            self.debug_push_prompt(user, prompt, request)
        return request

    def check_if_second_comment(self, user, user_txt, channel_id, prompt):
        if self.active_users[user]['active']:
            self.active_users[user]['active'] = False
            self.save_active_users()
            if self.zero_shot(prompt, 'yes'):
                prev_request = self.active_users[user]['request']
                stream_id = self.channel_streams[channel_id]
                try:
                    self.setup_connection(stream_id)
                    commit_id = self.commit(user, prev_request)
                except:
                    return {'answer': self.message_connection_error(user_txt)}
                return {'answer': self.message_commit_ok(user_txt, self.connection.server, stream_id, commit_id)}
            else:
                return {'answer': self.message_commit_not_ok(user_txt)}
        return None

    @staticmethod
    def debug_push_prompt(user, prompt, request):
        req = copy.deepcopy(request)
        req['input_user'] = user
        req['input_prompt'] = prompt
        with open('data.json', 'w') as f:
            data = json.dumps(req)
            json.dump(data, f)


if __name__ == '__main__':
    queries = [
        'Please, lower by 0.2 m the height of beam B125',
        'Can you move 0.5m to the front a wall W15?',
        'Displace column C27 one meter to the left, please',
        'Displace column C27 1 mm to the left, please',
        'Displace column C27 two inches to the left, please',
        'Change the position of duct D01 by moving it back 32 cm, please'
    ]

    nlp_agent = NLPAgent()
    for query in queries:
        request_data = nlp_agent.process_prompt(query)
        print(request_data)

    # nlp_agent.push_prompt('carlos', 'hey, can you set this channel to stream 8e6d1d1c53', '123456')

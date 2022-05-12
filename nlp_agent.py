from dataclasses import dataclass
from collections import OrderedDict
import re
import pandas as pd
from transformers import pipeline


class NLPModels:
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(NLPModels, cls).__new__(cls)
            cls.zero_shot = pipeline('zero-shot-classification', model='facebook/bart-large-mnli')
            cls.question_answerer = pipeline('question-answering', model='distilbert-base-cased-distilled-squad')
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


@dataclass
class NLPField(NLPModelsHelper):
    name: str = ''
    other_names: list = None

    def __post_init__(self):
        super().__post_init__()
        self.other_names = [] if self.other_names is None else self.other_names

    def found_inside(self, prompt):
        if self.zero_shot(prompt, self.name):
            return True
        else:
            for name in self.other_names:
                if self.zero_shot(prompt, name):
                    return True
            return False

    @staticmethod
    def amount_breakdown(amount):
        try:
            number = re.findall(r'(?<![a-zA-Z:])[-+]?\d*\.?\d+', amount)[0]
        except IndexError:
            return None, None
        unit = ''.join([letter for letter in amount if letter.isalnum() and not letter.isdigit()])
        unit = 'm' if unit == '' else unit  # defaulting to meters
        return float(number), unit

    def on_fail(self, item, parsed_items=None):
        if parsed_items is None:
            txt = 'Sorry, '
        else:
            txt = f'Hey! I understood you are referring to {self.summary(parsed_items)}. However, '
        txt += f'I could not understand which {item} you are talking about. '
        txt += f'Would you mind to rephrase it in a clear way for me and try again? Thanks in advance!'
        return txt

    def discard_items(self, parsed_items):
        return {key: value for key, value in parsed_items.items() if key not in self.parsed_items_to_discard}

    @staticmethod
    def parse_amount(parsed_items):
        parsed_items['number'], parsed_items['unit'] = parsed_items['number_unit']
        return parsed_items


@dataclass
class NLPStructuralField(NLPField):
    def __post_init__(self):
        super().__post_init__()
        self.elements = ['wall', 'slab', 'beam', 'column']
        self.directions = ['up', 'down', 'front', 'back', 'left', 'right']

    def which_element(self, prompt):
        candidate = self.zero_shot_multiple(prompt, self.elements)
        return candidate if self.zero_shot(prompt, candidate) else None

    def element_name(self, prompt, element):
        question = f'Which is the name of the {element}?'
        return self.question_answerer(question, prompt)

    def action(self, prompt, element, element_name):
        question = f'What should we do with the {element} {element_name}?'
        return self.question_answerer(question, prompt)

    def direction(self, prompt):
        return self.zero_shot_multiple(prompt, self.directions)

    def amount(self, prompt):
        question = f'By how much?'
        return self.question_answerer(question, prompt)

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
                'args': 'action'
            },
            'amount': {
                'func': self.amount,
                'args': 'action'
            },
            'number_unit': {
                'func': self.amount_breakdown,
                'args': 'amount'
            }
        })

    @property
    def parsed_items_to_discard(self):
        return ['prompt', 'action', 'amount', 'number_unit']

    @staticmethod
    def summary(parsed_items):
        txt = ''
        if 'element' not in parsed_items:
            return txt
        txt += f'a {parsed_items["element"]}'
        if 'element_name' not in parsed_items:
            return txt
        txt += f' named {parsed_items["element_name"]}'
        if 'direction' not in parsed_items:
            return txt
        txt += f' is requested to be moved {parsed_items["direction"]}'
        if 'number' not in parsed_items:
            return txt
        txt += f' by {parsed_items["number"]} {parsed_items["unit"]}'
        return txt

    def on_success(self, parsed_items):
        return f'Hey! Perfect, I understood that {self.summary(parsed_items)}. Doing my job now!'

    def process_one_step(self, value_name, parsed_items, func, args=None):
        if args is None:
            args = []
        else:
            args = args if isinstance(args, list) else [args]
            args = [parsed_items[arg] for arg in args]
        value = func(*args)
        if value is None:
            return {**parsed_items, **{'answer': self.on_fail('element', parsed_items)}}
        parsed_items[value_name] = value
        return parsed_items

    def process_prompt(self, prompt):
        parsed_items = {'success': False, 'prompt': prompt}
        for step_name, step_data in self.nlp_recipe.items():
            func = step_data['func']
            args = step_data['args'] if 'args' in step_data else []
            parsed_items = self.process_one_step(step_name, parsed_items, func, args)
            if step_name not in parsed_items:
                return self.discard_items(parsed_items)

        parsed_items['success'] = True
        parsed_items = self.parse_amount(parsed_items)
        parsed_items = self.discard_items(parsed_items)
        return {**parsed_items, **{'answer': self.on_success(parsed_items)}}


structural = NLPStructuralField(name='structural')
mep = NLPField(name='MEP', other_names=['mechanical', 'electrical', 'plumbing', 'fire protection'])


@dataclass
class NLPAgent(NLPModelsHelper):
    def __post_init__(self):
        self.fields = [structural, mep]
        self.nlp_models = NLPModels()

    def process_prompt(self, prompt):
        if not self.zero_shot(prompt, candidate_label='request'):
            print('Please, a request must be placed.')
            return None
        for field in self.fields:
            if field.found_inside(prompt):
                return field.process_prompt(prompt)
        return None


if __name__ == '__main__':
    query = 'Please, lower by 0.2 m the height of beam B125'

    nlp_agent = NLPAgent()
    request_data = nlp_agent.process_prompt(query)
    print(request_data)

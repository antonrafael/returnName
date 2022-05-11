from dataclasses import dataclass
import re
import pandas as pd
from transformers import pipeline


class NLPModels:
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(NLPModels, cls).__new__(cls)
            cls.zero_shot = pipeline('zero-shot-classification')
            cls.question_answerer = pipeline('question-answering')
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


@dataclass
class NLPStructuralField(NLPField):
    def __post_init__(self):
        super().__post_init__()
        self.elements = ['wall', 'slab', 'beam', 'column']
        self.directions = ['up', 'down', 'front', 'back', 'left', 'right']

    def which_element(self, prompt):
        candidate = self.zero_shot_multiple(prompt, self.elements)
        return candidate # if self.zero_shot(prompt, candidate) else None

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

    def amount_breakdown(self, amount):
        number = re.findall(r'(?<![a-zA-Z:])[-+]?\d*\.?\d+', amount)[0]
        unit = ''.join([letter for letter in amount if not letter.isdigit()])
        return number, unit

    def process_prompt(self, prompt):
        element = self.which_element(prompt)
        element_name = self.element_name(prompt, element)
        action = self.action(prompt, element, element_name)
        direction = self.direction(action)
        amount = self.amount(action)
        number, unit = self.amount_breakdown(amount)
        return {'element': element, 'name': element_name, 'direction': direction, 'number': number, 'unit': unit}


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

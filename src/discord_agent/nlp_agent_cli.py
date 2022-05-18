import sys
from pathlib import Path
import json


debug = False

path = Path().resolve().parent.parent
sys.path.append(str(path))
from src.natural_language_processing.nlp_agent import NLPAgent

nlp_agent = NLPAgent()
user, prompt, channel_id = [sys.argv[i + 1] for i in range(3)]

if debug:
    info = {'user': user, 'prompt': prompt}
    with open('data.json', 'w') as f:
        data = json.dumps(info)
        json.dump(data, f)

result = nlp_agent.push_prompt(user, prompt, channel_id)
result = json.dumps(result, separators=(',', ':'))
print(str(result))

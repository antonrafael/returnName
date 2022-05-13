import sys
from pathlib import Path
import json

path = Path().resolve().parent.parent
sys.path.append(str(path))
from returnName.nlp.nlp_agent import NLPAgent

debug = False

nlp_agent = NLPAgent()
user = sys.argv[1]
prompt = sys.argv[2]

if debug:
    info = {'user': user, 'prompt': prompt}
    with open('data.json', 'w') as f:
        data = json.dumps(info)
        json.dump(data, f)

result = nlp_agent.push_prompt(user, prompt)
result = json.dumps(result, separators=(',', ':'))
print(str(result))

import sys
from pathlib import Path
import json

path = Path().resolve().parent.parent
sys.path.append(str(path))
from returnName.nlp.nlp_agent import NLPAgent

nlp_agent = NLPAgent()
user = sys.argv[1]
prompt = sys.argv[2]
result = nlp_agent.push_prompt(user, prompt)
result = json.dumps(result, separators=(',', ':'))
print(str(result))

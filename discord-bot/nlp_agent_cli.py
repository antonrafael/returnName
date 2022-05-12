import sys
from ..nlp_agent import NLPAgent

nlp_agent = NLPAgent()
user = sys.argv[1]
prompt = sys.argv[2]
result = nlp_agent.push_prompt(user, prompt)
print(result)

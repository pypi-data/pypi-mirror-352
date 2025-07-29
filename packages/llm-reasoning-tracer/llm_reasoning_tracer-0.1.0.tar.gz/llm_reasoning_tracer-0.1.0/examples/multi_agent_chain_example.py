import os
import sys
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from langchain.agents import initialize_agent, AgentType, Tool
from langchain_openai import OpenAI
from langchain_community.utilities import SerpAPIWrapper
from cognitive_tracer.tracer import CognitiveTracer

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("Missing OPENAI_API_KEY")

search = SerpAPIWrapper()
tools = [
    Tool(
        name="Search",
        func=search.run,
        description="Useful for answering factual questions."
    )
]

llm = OpenAI(temperature=0, openai_api_key=api_key)
agent = initialize_agent(tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True)

tracer = CognitiveTracer(output_path="traces/trace_multi.json")
prompt = "Find the author of 'Thinking, Fast and Slow' and describe one cognitive bias discussed in the book."

result = agent.run(prompt, callbacks=[tracer])
print(result)
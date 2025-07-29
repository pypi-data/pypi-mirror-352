import os
import sys
from dotenv import load_dotenv
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from langchain.agents import initialize_agent, AgentType, Tool
from langchain_openai import OpenAI
from cognitive_tracer.tracer import CognitiveTracer

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("Missing OPENAI_API_KEY")

llm = OpenAI(temperature=0, openai_api_key=api_key)

def echo_tool(input_text):
    return f"Echo: {input_text}"

tools = [
    Tool(
        name="EchoTool",
        func=echo_tool,
        description="Repeats whatever you say"
    )
]

agent = initialize_agent(tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True)
tracer = CognitiveTracer(output_path="traces/trace_simple.json")

query = "talk about the University of Louisville campus and about Louisville!"
result = agent.run(query, callbacks=[tracer])
print(result)

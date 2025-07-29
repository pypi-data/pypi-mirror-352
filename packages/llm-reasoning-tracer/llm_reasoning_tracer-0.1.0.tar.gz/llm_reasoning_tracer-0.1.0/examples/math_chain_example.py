import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dotenv import load_dotenv
load_dotenv()

from langchain.agents import initialize_agent, AgentType, Tool
from langchain_openai import OpenAI
from cognitive_tracer.tracer import CognitiveTracer

# --- Check for API Key ---
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("Missing environment variable: OPENAI_API_KEY")

# --- Define Tip Calculator Tool ---
def calculate_tip(inputs):
    question = inputs.lower()
    if "tip" in question and "%" in question:
        try:
            parts = question.replace("%", " percent").split()
            percent = float([p for p in parts if p.replace('.', '', 1).isdigit()][0])
            amount = float([p for p in parts if "$" in p][0].replace("$", ""))
            tip = round((percent / 100) * amount, 2)
            return f"Tip is ${tip}"
        except:
            return "Could not calculate tip."
    return "Invalid input."

tip_tool = Tool(
    name="Tip Calculator",
    func=calculate_tip,
    description="Calculates tip from questions like 'What is 20% tip for $60?'"
)

# --- Define Total Calculator Tool ---
def total_calculator(inputs):
    try:
        parts = inputs.replace("$", "").split("+")
        bill = float(parts[0].strip())
        tip = float(parts[1].strip())
        total = round(bill + tip, 2)
        return f"The total bill including tip is ${total}"
    except Exception:
        return "Could not calculate total."

total_tool = Tool(
    name="Total Calculator",
    func=total_calculator,
    description="Adds bill and tip like '$80 + $12.5' to compute total"
)

# --- Initialize LLM Agent ---
llm = OpenAI(temperature=0, openai_api_key=api_key)

agent = initialize_agent(
    [tip_tool, total_tool],
    llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# --- Run with Tracer ---
tracer = CognitiveTracer(output_path="traces/trace_math.json")
query = "What's 15% tip for $80 dinner, and add it to the bill?"
result = agent.run(query, callbacks=[tracer])
print(result)

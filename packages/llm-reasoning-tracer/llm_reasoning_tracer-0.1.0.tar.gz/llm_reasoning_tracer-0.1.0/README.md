# LLM Reasoning Tracer

A modular tracing and explainability toolkit for LangChain agents. Capture step-by-step tool usage, visualize the reasoning process, and analyze how your agent chains behave.

## Features
- Traces agent steps (inputs, tool used, outputs)
- Visualizes tool usage and outcomes
- Includes dashboards for Streamlit and Matplotlib
- Supports RAG, search chains, math pipelines, and multi-tool agents

## Installation
```bash
pip install .
```

## Setup
Create a `.env` file:
```env
OPENAI_API_KEY=your-key-here
```

## Trace Examples
Run one of the provided pipelines:
```bash
python examples/use_with_langchain_agent.py
python examples/math_chain_example.py
python examples/multi_agent_chain_example.py
python examples/rag_pipeline_example.py
```

## Create RAG DB
```bash
python examples/create_db.py
```
It loads `data/solar_energy_notes.txt` and builds `db/` for retrieval.

## View Your Trace
1. Streamlit Dashboard
```bash
streamlit run examples/streamlit_viewer.py
```

2. Timeline Plot (if added)
```bash
python examples/visualize_trace.py
```

## Output Example (trace_math.json)
```json
{
  "step_1": {
    "input": "What's 15% tip for $80 dinner, and add it to the bill?",
    "tool_used": "Tip Calculator",
    "output": "Tip is $12.0"
  },
  "step_2": {
    "input": "Add 80 + 12.0",
    "tool_used": "Total Calculator",
    "output": "The total bill including tip is $92.0"
  }
}
```

## Structure
- `cognitive_tracer/` — the Python module
- `examples/` — usage scripts
- `traces/` — generated trace files
- `data/` — text input for vector DB

## Dependencies
```
langchain
langchain-openai
langchain-community
openai
streamlit
matplotlib
python-dotenv
```

## License
MIT © Nisaharan Genhatharan
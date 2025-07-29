from langchain.callbacks.base import BaseCallbackHandler
import json

class CognitiveTracer(BaseCallbackHandler):
    def __init__(self, output_path="trace.json"):
        self.output_path = output_path
        self.trace_log = {}
        self.step_id = 1

    def on_tool_end(self, output, **kwargs):
        self.trace_log[f"step_{self.step_id}"] = {
            "input": kwargs.get("input"),
            "tool_used": kwargs.get("tool", "unknown"),
            "output": output
        }
        self.step_id += 1

    def on_chain_end(self, outputs, **kwargs):
        with open(self.output_path, "w") as f:
            json.dump(self.trace_log, f, indent=2)

from langgraph.graph import StateGraph
from app.agents.stream_watcher import fetch_log_from_stream
from agents.preprocessor import normalize_log
from agents.detector import detect_anomaly
from agents.alert import alert
from agents.sink import sink_log
import time
from typing import TypedDict, Tuple

class State(TypedDict):
    log: dict | None
    AnomalyDetector: Tuple[bool, str]  # (is_anomaly, explanation)


builder = StateGraph(State)

builder.add_node("StreamWatcher", fetch_log_from_stream)
builder.add_node("Preprocessor", normalize_log)
builder.add_node("AnomalyDetector", detect_anomaly)
builder.add_node("AlertAgent", alert)
builder.add_node("LogSink", sink_log)

builder.set_entry_point("StreamWatcher")
builder.add_edge("StreamWatcher", "Preprocessor")
builder.add_edge("Preprocessor", "AnomalyDetector")

# Conditional routing based on anomaly detection
def route(result):
    is_anomaly, _ = result
    return "AlertAgent" if is_anomaly else "LogSink"

builder.add_conditional_edges("AnomalyDetector", route, ["AlertAgent", "LogSink"])

graph = builder.compile()
mermaid_code = graph.get_graph().draw_mermaid_png()
with open("mermaid_graph.png", "wb") as f:
    f.write(graph.get_graph().draw_mermaid_png())

if __name__ == "__main__":
    while True:
        graph.invoke({})
        time.sleep(0.1)
        print("\n=================================\nWaiting for new log entry...\n")
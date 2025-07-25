import json

from langchain_core.messages import HumanMessage
from langchain_community.chat_models import ChatOllama

# llm = ChatOllama(model="llama3.1:latest")

PROMPT_TEMPLATE = """
You are an expert log analyzer. Given a log line, determine if it represents an anomaly.

Anomalies include errors, security threats, failed connections, timeouts, or anything unexpected.

Respond ONLY in strict JSON format with lowercase true/false values.

Example:
{
  "anomaly": true,
  "explanation": "why this log is or is not anomalous"
}

Log:
"""

def detect_anomaly(state):
    log = state.get("log")
    if not log:
        return {"AnomalyDetector": (False, "No log to analyze")}

    log_line = f"[{log['timestamp']}] {log['level'].upper()} {log['source']}: {log['message']}"
    prompt = PROMPT_TEMPLATE + log_line

    print("[AnomalyDetector] Sending to LLaMA:", log_line)

    return prompt

    # response = llm.invoke([HumanMessage(content=prompt)])
    #
    # try:
    #     content = response.content.strip()
    #     content = content.replace("true", "true").replace("false", "false")
    #     result = json.loads(content)  # okay only for trusted, local LLM
    #     return {"AnomalyDetector": (result.get("anomaly", False), result.get("explanation", "No explanation"))}
    # except Exception as e:
    #     print("[AnomalyDetector] Failed to parse response:", response.content)
    #     return {"AnomalyDetector": (False, f"Error parsing model response: {str(e)}")}


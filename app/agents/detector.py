import json

from langchain_core.messages import HumanMessage
from langchain_community.chat_models import ChatOllama

# llm = ChatOllama(model="llama3.1:latest")

PROMPT_TEMPLATE = """
You are an expert log analyzer. Given a log line, determine if it represents an anomaly and call search_solution to find solutions from knowledge base.

Anomalies include errors, security threats, failed connections, timeouts, or anything unexpected.

Respond ONLY in strict JSON format with lowercase true/false values 

Example:
{
  "anomaly": true,
  "explanation": "why this log is or is not anomalous"
  "solution": "solution from knowledge base if available"
}

If there is any anomaly in the log line, alert the user with a clear explanation of the anomaly with tool call.

Log:
"""

PROMPT = """
You are a professional log analysis expert.

Given a log line, decide whether it contains an anomaly.

### Anomalies include:
- Errors
- Timeouts
- Failed connections
- Unauthorized or security threats
- Anything unexpected or unusual in system behavior

---

### If the log is anomalous:
1. Set "anomaly": true
2. Explain what makes it anomalous
3. Call the `search_solution` tool with a concise, relevant search query
4. Include the tool's response in the "solution" field

### If the log is NOT anomalous:
- Set "anomaly": false
- Still explain why it is normal
- Leave "solution" as an empty string

---

### Always respond in **this JSON** format:
```json
{
  "anomaly": true | false,
  "explanation": "short explanation",
  "solution": "tool result or empty string"
}

Available tool:
    search_solution(query: string) => string
    Use this tool to find a fix or explanation from the knowledge base for any detected anomaly.

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


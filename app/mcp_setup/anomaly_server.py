import redis
import json
import os

from langchain_core.messages import BaseMessage
from mcp.server.fastmcp import FastMCP

from app.agents.detector import detect_anomaly

mcp = FastMCP("Log Anomaly Detection")

redis_host = os.environ.get("REDIS_HOST", "localhost")
r = redis.Redis(host=redis_host, port=6379, decode_responses=True)

# Fetch a single log entry from the Redis stream
# Returns the raw log dictionary or None if empty

# @mcp.tool()
def fetch_log_from_redis_stream():
    """
    Fetches a single log entry from the Redis stream.
    This function reads from the Redis stream "logs:incoming" and retrieves the latest log entry.
    If no log entry is available, it returns None.
    It is designed to be used in a tool that processes logs for anomaly detection.
    :return:
        A dictionary containing the log entry if available, otherwise None.
        The log entry is expected to be in the format of a dictionary with keys corresponding to log attributes.
    :rtype: dict
    :example:
        >>> fetch_log_from_redis_stream()
        {"log": {"source": "web", "level": "info", "message": "User logged in", "timestamp": "2023-10-01 12:00:00"}}
    """
    print("[StreamWatcher] Fetching log from Redis stream...")
    result = r.xread({"logs:incoming": "$"}, block=1000, count=1)
    if result:
        _, entries = result[0]
        stream_id, data = entries[0]
        log = {k: v for k, v in data.items()}
        print("[StreamWatcher] New log:", log)
        return {"log": log}
    return {"log": None}


@mcp.tool(name="AnomalyAlerter", description="Detects anomalies in logs and alerts the user if an anomaly is found.")
def alert_anomaly_to_user(anomaly: bool = True, explanation: str = ""):
    """
    Alerts the user about an anomaly detected in the log.
    This function is designed to be called when an anomaly is detected, providing a clear explanation.
    :param anomaly:
        A boolean indicating whether an anomaly was detected.
    :param explanation:
        A string explaining the nature of the anomaly.
    """
    if anomaly:
        print("[Alert Created] Anomaly detected:", explanation)
        # return {"alert": {"anomaly": True, "explanation": explanation}}
    else:
        print("[Alert] No anomaly detected.")
        # return {"alert": {"anomaly": False, "explanation": "No anomalies detected."}}

@mcp.tool()
def get_anomaly_from_llm(response: BaseMessage) -> dict:
    """
    Extracts anomaly detection result from the LLM response.
    This function assumes the response is in JSON format with keys "anomaly" and "explanation".
    :param response:
        The response from the LLM containing anomaly detection results.
    :return:
        A dictionary with keys "anomaly" (boolean) and "explanation" (string).
    """
    try:
        content = response.content.strip()
        content = content.replace("true", "true").replace("false", "false")
        result = json.loads(content)  # okay only for trusted, local LLM
        return {"AnomalyDetector": (result.get("anomaly", False), result.get("explanation", "No explanation"))}
    except Exception as e:
        print("[AnomalyDetector] Failed to parse response:", response.content)
        return {"AnomalyDetector": (False, f"Error parsing model response: {str(e)}")}

# Run the server
if __name__ == "__main__":
    print("Starting MCP server for Log Anomaly Detection...")
    mcp.run(transport="stdio")
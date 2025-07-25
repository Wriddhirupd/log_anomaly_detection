import json

from langchain_core.messages import BaseMessage
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Log Anomaly Detection")

@mcp.tool()
def get_anomaly(response: BaseMessage) -> dict:
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
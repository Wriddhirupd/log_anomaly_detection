import asyncio
import os

from langchain_community.chat_models import ChatOllama
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.constants import END
from langgraph.graph import StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from app.agents.stream_watcher import fetch_log_from_stream
from agents.preprocessor import normalize_log
from agents.detector import detect_anomaly
from agents.alert import alert
from agents.sink import sink_log
# from langgraph.graph.runner import start_visual_server
import threading
import time
from typing import TypedDict, Tuple
from mcp import StdioServerParameters, stdio_client, ClientSession

class State(TypedDict):
    log: dict | None
    AnomalyDetector: Tuple[bool, str]  # (is_anomaly, explanation)

print("Current working directory:", os.getcwd())

print("Starting MCP client...")
server_params = StdioServerParameters(
    command="python",
    # args=["agents", "mcp_setup", "server.py"],
    args=[os.path.join(os.getcwd(), "app", "mcp_setup", "server.py")],
    env=None,
)

async def create_llm(session):
    llm = ChatOllama(model="llama3.1:latest")

    tools = await load_mcp_tools(session)
    llm_with_tool = llm.bind_tools(tools)

    return llm_with_tool, tools

async def build_graph(session):

    builder = StateGraph(State)

    # llm, tools = await create_llm(session)  # Replace None with actual session if needed

    llm = ChatOllama(model="llama3.2:latest")

    tools = await load_mcp_tools(session)
    # llm = llm.bind_tools(tools)

    builder.add_node("StreamWatcher", fetch_log_from_stream)
    builder.add_node("Preprocessor", normalize_log)
    builder.add_node("tool_node", ToolNode(tools=tools))
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

    builder.add_conditional_edges("AnomalyDetector", tools_condition, {"tools": "tool_node", "__end__": "AnomalyDetector"})
    builder.add_conditional_edges("AnomalyDetector", route, ["AlertAgent", "LogSink"])

    graph = builder.compile()

    return graph

async def main():
    config = {"configurable": {"thread_id": 1234}}
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            graph = await build_graph(session)
            print("Graph built successfully")

            # Start the graph
            while True:
                graph.invoke({}, config=config)
                time.sleep(0.1)


if __name__ == "__main__":
    # Start visual server in separate thread
    # threading.Thread(target=start_visual_server, args=(graph,), daemon=True).start()

    # while True:
    #     graph.invoke({})
    #     time.sleep(0.1)

    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(main())
    # loop.close()

    asyncio.run(main())
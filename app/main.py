import asyncio
import os

from langchain_community.chat_models import ChatOllama
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.constants import END
from langgraph.graph import StateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from IPython.display import Image, display

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

from app.models import State

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

# Debugging state transitions
def debug_state_transition(state):
    print("Current state:", state)
    return state

async def build_graph(session):
    builder = StateGraph(State)

    # Initialize the LLM
    llm = ChatOllama(model="llama3.2:latest")

    # Load tools
    tools = await load_mcp_tools(session)
    print("Available tools:", [tool.name for tool in tools])

    # Manually integrate tools
    async def call_llm_with_tool(state: State) -> Tuple[State, str]:
        print("[ToolNode] Calling LLM with state:", state)
        tool_output = await tools[0].ainvoke(state)  # Use asynchronous invocation
        response = await llm.ainvoke([tool_output])  # Pass tool output to LLM asynchronously
        print("[ToolNode] LLM response:", response)
        return state, response.content

    builder.add_node("StreamWatcher", fetch_log_from_stream)
    builder.add_node("Preprocessor", normalize_log)
    builder.add_node("call_model", call_llm_with_tool)
    builder.add_node("AlertAgent", alert)
    builder.add_node("LogSink", sink_log)

    builder.set_entry_point("StreamWatcher")
    builder.add_edge("StreamWatcher", "Preprocessor")
    builder.add_edge("Preprocessor", "call_model")
    builder.add_edge("call_model", "AlertAgent")
    builder.add_edge("call_model", "LogSink")

    graph = builder.compile()

    with open("mermaid_graph.png", "wb") as f:
        f.write(graph.get_graph().draw_mermaid_png())

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
                response = await graph.ainvoke({}, config=config)
                print("AI: "+response["messages"][-1].content)
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
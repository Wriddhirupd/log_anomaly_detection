import json
import os
import time
from typing import Any

from IPython.core.debugger import prompt
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent
from langgraph.prebuilt.chat_agent_executor import AgentState
from mcp import stdio_client, StdioServerParameters, ClientSession

from app.agents.detector import PROMPT_TEMPLATE
from app.mcp_setup.server import fetch_log_from_redis_stream

# from app.models import State

print("Starting MCP client...")
server_params = StdioServerParameters(
    command="python",
    # args=["agents", "mcp_setup", "server.py"],
    args=[os.path.join(os.getcwd(), "app", "mcp_setup", "server.py")],
    env=None,
)

class State(AgentState):
    context: dict[str, Any]

async def main():
    config = {"configurable": {"thread_id": 1234}}
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # List available tools
            # tools = await session.list_tools()
            tools = await load_mcp_tools(session)
            print("\n/////////////////tools//////////////////")
            for tool in tools:
                print(tool.name)

            # Create LLM with tools
            llm = ChatOllama(model="llama3.2:latest")



            agent = create_react_agent(
                model=llm,
                tools=tools,
                state_schema=State,
            )

            # Run the agent
            print("Starting agent...")
            log = fetch_log_from_redis_stream()
            log = log["log"]  # Extract the log from the dictionary
            # Preprocess log to match the required format
            if log is not None:
                # logVal = log["log"]
                input_message = {
                    "messages": [
                        {
                            "role": "system",
                            "content":  PROMPT_TEMPLATE
                        },
                        {
                            "role": "user",
                            "content": f"Log entry: {log['message']} (Level: {log['level']}, Source: {log['source']}, Timestamp: {log['timestamp']})"
                        }
                    ]
                }
            else:
                input_message = {"messages": [{"role": "user", "content": "No log available"}]}
            print(f"Input to agent: {input_message}")

            if input_message["messages"][0]["content"] == "No log available":
                return

            response = await agent.ainvoke(
                input=input_message,
                config=config,
            )
            output = response["messages"][-1].content
            print("AI: "+output)

            if "anomaly" in eval(output.lower()):
                content = output.strip()
                content = content.replace("true", "true").replace("false", "false")
                result = json.loads(content)  # okay only for trusted, local LLM
                print("Anomaly detection result:", result)

                if result["anomaly"]:
                    print(f"Anomaly detected: {result['explanation']}")

                    alert = {
                        "source": log.get("source"),
                        "level": log.get("level"),
                        "message": log.get("message"),
                        "timestamp": log.get("timestamp"),
                        "explanation": result['explanation']
                    }

                    print("[AlertAgent] ALERT TRIGGERED:", alert)




if __name__ == "__main__":
    import asyncio
    while True:
        asyncio.run(main())
        time.sleep(0.1)
        # print("MCP client started successfully.")

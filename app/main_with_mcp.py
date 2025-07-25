import json
import os
import time
from typing import Any, TypedDict

from langchain.chains.retrieval_qa.base import RetrievalQA
from langchain_core.callbacks import StdOutCallbackHandler
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_ollama import ChatOllama
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.graph import StateGraph
from langgraph.prebuilt import create_react_agent
from langgraph.prebuilt.chat_agent_executor import AgentState
from mcp import stdio_client, StdioServerParameters, ClientSession

from app.agents.detector import PROMPT_TEMPLATE, PROMPT
from app.knowledge_base.json_to_kb import load_faiss_store
from app.mcp_setup.anomaly_server import fetch_log_from_redis_stream

# from app.models import State

print("Starting MCP client...")
server_params = StdioServerParameters(
    command="python",
    args=[os.path.join(os.getcwd(), "app", "mcp_setup", "anomaly_server.py")],
    env=None,
)

client = MultiServerMCPClient(
    {
        "anomaly": {
            "command": "python",
            "args": [os.path.join(os.getcwd(), "app", "mcp_setup", "anomaly_server.py")],
            "transport": "stdio",
        },
        "solution": {
            "command": "python",
            "args": [os.path.join(os.getcwd(), "app", "mcp_setup", "rag_server.py")],
            "transport": "stdio",
            # "url": "http://localhost:8000/mcp",
            # "transport": "streamable_http",
        }
    }
)

vectorstore = load_faiss_store()

class State(AgentState):
    context: dict[str, Any]

llm = ChatOllama(model="llama3.2:latest")

async def create_agent(anomaly_session: ClientSession, solution_session: ClientSession):
    # Load tools from both sessions
    anomaly_tools = await load_mcp_tools(anomaly_session)
    solution_tools = await load_mcp_tools(solution_session)
    tools = anomaly_tools + solution_tools

    print("Available tools:", [tool.name for tool in tools])

    # Create the agent with the loaded tools
    agent = create_react_agent(
        model=llm,
        tools=tools,
        state_schema=State,
    )
    return agent, tools

async def multiserver_main():
    async with client.session("anomaly") as anomaly_session, client.session("solution") as solution_session:
        agent, tools = await create_agent(anomaly_session, solution_session)
        return agent, tools


async def run_agent(agent, tools, config):
        # Run the agent
        print("Starting agent...")
        log = fetch_log_from_redis_stream()
        log = log["log"]  # Extract the log from the dictionary
        # Preprocess log to match the required format
        if log is not None:
            input_message = {
                "messages": [
                    {
                        "role": "system",
                        "content": PROMPT
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
        print("Agent response:", response)
        output = response["messages"][-1].content
        print("AI: " + output)

        if 'anomaly": ' in output.lower():
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

                print("ALERT TRIGGERED:", alert)

async def main():
    config = {"configurable": {"thread_id": 1234}}
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # List available tools
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

            if 'anomaly": ' in output.lower():
                content = output.strip()
                content = content.replace("true", "True").replace("false", "false")
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

    async def loop_main():
        agent, tools = await multiserver_main()
        while True:
            await run_agent(
                agent=agent,
                tools=tools,
                config={"configurable": {"thread_id": 1234}, "recursion_limit": 100}
            )
            await asyncio.sleep(1)

    asyncio.run(loop_main())


# if __name__ == "__main__":
#     import asyncio
#     while True:
#         asyncio.run(multiserver_main())
#         time.sleep(0.1)
#         # print("MCP client started successfully.")

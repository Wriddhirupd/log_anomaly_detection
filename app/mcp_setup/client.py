# from langchain_community.chat_models import ChatOllama
# from langchain_mcp_adapters.tools import load_mcp_tools
# from mcp import StdioServerParameters, stdio_client, ClientSession
#
# server_params = StdioServerParameters(
#     command="python",
#     args=["server.py"],
#     env=None,
# )
#
# async def create_llm(session):
#     llm = ChatOllama(model="llama3.1:latest")
#
#     tools = await load_mcp_tools(session)
#     llm_with_tool = llm.bind_tools(tools)
#
#     return llm_with_tool
#
# async def main():
#     async with stdio_client(server_params) as (read, write):
#         async with ClientSession(read, write) as session:
#             await session.initialize()
#
#             # List available tools
#             response = await session.list_tools()
#             print("\n/////////////////tools//////////////////")
#             for tool in response.tools:
#                 print(tool)
from mcp.server import FastMCP

from app.main_with_mcp import vectorstore

mcp = FastMCP("Retrieval Augmented Generation (RAG) Server")

@mcp.tool()
async def search_solution(log_msg: str):
    """
    Queries the knowledge base for a solution to the given log message.
    :param log_msg:
        The log message to search for a solution.
    :type log_msg: str
    :return:
        The solution found in the knowledge base, or a message indicating no solution was found.
    """
    matches = vectorstore.similarity_search(log_msg, k=1)
    print("[RAGSolution] Searching KB for log message:", log_msg)
    if matches:
        print("[RAGSolution] Found solution in KB:", matches)
        return matches[0].metadata.get("solution", "No solution found in metadata.")
    return "No solution found in KB."

def provide_solution(log, qa):
    query = f"What solution can you suggest for this log issue: {log}"
    answer = qa.invoke(query)
    print("[RAGSolution] KB response:", answer)
    return {"solution": answer}

if __name__ == "__main__":
    # Example usage of the query_solution tool
    print("Starting RAG server in streamable-http...")
    mcp.run(transport="stdio")

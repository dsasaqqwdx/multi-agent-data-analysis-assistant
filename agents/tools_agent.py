from langgraph.prebuilt import create_react_agent
from langchain_core.tools import tool
from config.llm import get_llm

@tool
def calculator_tool(expression: str) -> str:
    """Useful for math calculations. Input should be a valid Python math expression, e.g. '5*12'."""
    try:
        result = eval(expression, {"__builtins__": {}})
        return str(result)
    except Exception as e:
        return f"Error evaluating expression: {e}"

@tool
def mock_search_tool(query: str) -> str:
    """Useful for general lookups when no other tool fits. Input should be a search query string."""
    return f"[Mock search result for: '{query}'] — replace this with a real tool/MCP call later."

def run_tools_agent(query: str) -> str:
    tools = [calculator_tool, mock_search_tool]
    agent = create_react_agent(get_llm(), tools)

    result = agent.invoke({"messages": [{"role": "user", "content": query}]})
    final_message = result["messages"][-1]
    return final_message.content


if __name__ == "__main__":
    answer = run_tools_agent("What is 45 * 12?")
    print("ANSWER:", answer)
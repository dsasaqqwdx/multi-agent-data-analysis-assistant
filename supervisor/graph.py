
from langgraph.graph import StateGraph, END
from typing import TypedDict, Any

from agents.data_agent import run_data_agent
from agents.rag_agent import run_rag_agent
from agents.ml_agent import run_ml_agent
from agents.tools_agent import run_tools_agent

from config.llm import get_llm


class AgentState(TypedDict):
    query: str
    route: str
    result: Any
    csv_path: str
    history: str


PLOT_KEYWORDS = [
    "plot",
    "chart",
    "graph",
    "bar plot",
    "barplot",
    "bar chart",
    "bar graph",
    "line plot",
    "line chart",
    "line graph",
    "histogram",
    "scatter",
    "scatter plot",
    "pie chart",
    "pie plot",
    "pie",
    "visualize",
    "visualise",
    "visualization",
    "visualisation",
    "trend",
    "vector plot",
    "quiver",
]


DATA_KEYWORDS = [
    "dataset",
    "data",
    "csv",
    "row",
    "rows",
    "column",
    "columns",
    "null",
    "missing",
    "nan",
    "average",
    "mean",
    "median",
    "maximum",
    "minimum",
    "max",
    "min",
    "sum",
    "count",
    "statistics",
    "stats",
    "distribution",
    "highest",
    "lowest",
    "show me",
    "describe",
]


ML_KEYWORDS = [
    "predict",
    "prediction",
    "forecast",
    "estimate",
    "classify",
    "classification",
    "regression",
    "train model",
    "machine learning",
    "ml model",
]


def route_query(state: AgentState) -> AgentState:
    query = state["query"]
    history = state.get("history", "")
    query_lower = query.lower()

    if any(keyword in query_lower for keyword in PLOT_KEYWORDS):
        print("ROUTER: Plot request detected -> DATA")
        state["route"] = "data"
        return state

    if any(keyword in query_lower for keyword in ML_KEYWORDS):
        print("ROUTER: ML request detected -> ML")
        state["route"] = "ml"
        return state

    if any(keyword in query_lower for keyword in DATA_KEYWORDS):
        print("ROUTER: Dataset request detected -> DATA")
        state["route"] = "data"
        return state

    llm = get_llm()

    routing_prompt = f"""
Classify the user's CURRENT question into exactly one category.

Reply with ONLY one word:

data
rag
ml
tools

CATEGORY DEFINITIONS:

data:
Questions about analyzing the uploaded CSV dataset.

Examples:
- number of rows
- columns
- averages
- statistics
- missing values
- filtering
- grouping
- plots
- charts
- graphs

rag:
Questions about company documents or company policies.

Examples:
- leave policy
- remote work policy
- reimbursement policy
- company rules

ml:
Requests involving machine learning on the uploaded dataset.

Examples:
- predict a column
- train a model
- classification
- regression
- forecasting

tools:
General knowledge, mathematics, code explanations,
or anything unrelated to the uploaded dataset.

Recent conversation:
{history}

Current question:
{query}

Category:
"""

    try:
        route = (
            llm.invoke(routing_prompt)
            .content
            .strip()
            .lower()
        )
    except Exception as e:
        print(f"ROUTER ERROR: {e}")
        route = "tools"

    if route not in ["data", "rag", "ml", "tools"]:
        print(f"ROUTER: Invalid route '{route}' -> TOOLS")
        route = "tools"

    print(f"ROUTER: LLM selected -> {route.upper()}")

    state["route"] = route

    return state


def data_node(state: AgentState) -> AgentState:
    history = state.get("history", "")

    contextual_query = (
        f"""
Recent conversation:

{history}

Current question:

{state["query"]}
"""
        if history
        else state["query"]
    )

    state["result"] = run_data_agent(
        query=contextual_query,
        csv_path=state.get(
            "csv_path",
            "data/sample.csv"
        ),
        current_query=state["query"],
    )

    return state


def rag_node(state: AgentState) -> AgentState:

    history = state.get(
        "history",
        ""
    )

    contextual_query = (

        f"""
Recent conversation:

{history}


Current question:

{state["query"]}
"""

        if history

        else state["query"]

    )

    state["result"] = run_rag_agent(

        query=contextual_query,

        csv_path=state.get(
            "csv_path",
            "data/sample.csv"
        )

    )

    return state


def ml_node(state: AgentState) -> AgentState:
    history = state.get("history", "")

    contextual_query = (
        f"""
Recent conversation:

{history}

Current question:

{state["query"]}
"""
        if history
        else state["query"]
    )

    state["result"] = run_ml_agent(
        query=contextual_query,
        csv_path=state.get(
            "csv_path",
            "data/sample.csv"
        ),
        
    )

    return state


def tools_node(state: AgentState) -> AgentState:
    history = state.get("history", "")

    contextual_query = (
        f"""
For context only, do not re-answer the previous conversation:

{history}

Answer ONLY this current question:

{state["query"]}
"""
        if history
        else state["query"]
    )

    state["result"] = run_tools_agent(
        contextual_query
    )

    return state


graph = StateGraph(AgentState)


graph.add_node(
    "route",
    route_query
)

graph.add_node(
    "data",
    data_node
)

graph.add_node(
    "rag",
    rag_node
)

graph.add_node(
    "ml",
    ml_node
)

graph.add_node(
    "tools",
    tools_node
)


graph.set_entry_point("route")


graph.add_conditional_edges(
    "route",
    lambda state: state["route"],
    {
        "data": "data",
        "rag": "rag",
        "ml": "ml",
        "tools": "tools",
    }
)


graph.add_edge("data", END)
graph.add_edge("rag", END)
graph.add_edge("ml", END)
graph.add_edge("tools", END)


supervisor_graph = graph.compile()


if __name__ == "__main__":

    tests = [
        "What is the average salary?",
        "How many days of paid leave do employees get?",
        "Predict the price",
        "What is 45 * 12?",
        "Can you plot a barplot for the first 6 rows?",
        "Show a histogram",
        "Create a scatter plot",
    ]

    for q in tests:

        result = supervisor_graph.invoke(
            {
                "query": q,
                "route": "",
                "result": None,
                "csv_path": "data/sample.csv",
                "history": "",
            }
        )

        print("\n" + "=" * 60)
        print(f"QUERY: {q}")
        print(f"ROUTE: {result['route']}")
        print(f"RESULT: {result['result']}")
        print("=" * 60)
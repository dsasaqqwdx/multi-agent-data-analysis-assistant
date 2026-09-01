
# from langgraph.graph import StateGraph, END
# from typing import TypedDict, Any

# from agents.data_agent import run_data_agent
# from agents.rag_agent import run_rag_agent
# from agents.ml_agent import run_ml_agent
# from agents.tools_agent import run_tools_agent

# from config.llm import get_llm


# class AgentState(TypedDict):
#     query: str
#     route: str
#     result: Any
#     csv_path: str
#     history: str


# PLOT_KEYWORDS = [
#     "plot",
#     "chart",
#     "graph",
#     "bar plot",
#     "barplot",
#     "bar chart",
#     "bar graph",
#     "line plot",
#     "line chart",
#     "line graph",
#     "histogram",
#     "scatter",
#     "scatter plot",
#     "pie chart",
#     "pie plot",
#     "pie",
#     "visualize",
#     "visualise",
#     "visualization",
#     "visualisation",
#     "trend",
#     "vector plot",
#     "quiver",
# ]


# DATA_KEYWORDS = [
#     "dataset",
#     "data",
#     "csv",
#     "row",
#     "rows",
#     "column",
#     "columns",
#     "null",
#     "missing",
#     "nan",
#     "average",
#     "mean",
#     "median",
#     "maximum",
#     "minimum",
#     "max",
#     "min",
#     "sum",
#     "count",
#     "statistics",
#     "stats",
#     "distribution",
#     "highest",
#     "lowest",
#     "show me",
#     "describe",
# ]


# ML_KEYWORDS = [
#     "predict",
#     "prediction",
#     "forecast",
#     "estimate",
#     "classify",
#     "classification",
#     "regression",
#     "train model",
#     "machine learning",
#     "ml model",
# ]


# def route_query(state: AgentState) -> AgentState:
#     query = state["query"]
#     history = state.get("history", "")
#     query_lower = query.lower()

#     if any(keyword in query_lower for keyword in PLOT_KEYWORDS):
#         print("ROUTER: Plot request detected -> DATA")
#         state["route"] = "data"
#         return state

#     if any(keyword in query_lower for keyword in ML_KEYWORDS):
#         print("ROUTER: ML request detected -> ML")
#         state["route"] = "ml"
#         return state

#     if any(keyword in query_lower for keyword in DATA_KEYWORDS):
#         print("ROUTER: Dataset request detected -> DATA")
#         state["route"] = "data"
#         return state

#     llm = get_llm()

#     routing_prompt = f"""
# Classify the user's CURRENT question into exactly one category.

# Reply with ONLY one word:

# data
# rag
# ml
# tools

# CATEGORY DEFINITIONS:

# data:
# Questions about analyzing the uploaded CSV dataset.

# Examples:
# - number of rows
# - columns
# - averages
# - statistics
# - missing values
# - filtering
# - grouping
# - plots
# - charts
# - graphs

# rag:
# Questions about company documents or company policies.

# Examples:
# - leave policy
# - remote work policy
# - reimbursement policy
# - company rules

# ml:
# Requests involving machine learning on the uploaded dataset.

# Examples:
# - predict a column
# - train a model
# - classification
# - regression
# - forecasting

# tools:
# General knowledge, mathematics, code explanations,
# or anything unrelated to the uploaded dataset.

# Recent conversation:
# {history}

# Current question:
# {query}

# Category:
# """

#     try:
#         route = (
#             llm.invoke(routing_prompt)
#             .content
#             .strip()
#             .lower()
#         )
#     except Exception as e:
#         print(f"ROUTER ERROR: {e}")
#         route = "tools"

#     if route not in ["data", "rag", "ml", "tools"]:
#         print(f"ROUTER: Invalid route '{route}' -> TOOLS")
#         route = "tools"

#     print(f"ROUTER: LLM selected -> {route.upper()}")

#     state["route"] = route

#     return state


# def data_node(state: AgentState) -> AgentState:
#     history = state.get("history", "")

#     contextual_query = (
#         f"""
# Recent conversation:

# {history}

# Current question:

# {state["query"]}
# """
#         if history
#         else state["query"]
#     )

#     state["result"] = run_data_agent(
#         query=contextual_query,
#         csv_path=state.get(
#             "csv_path",
#             "data/sample.csv"
#         ),
#         current_query=state["query"],
#     )

#     return state


# def rag_node(state: AgentState) -> AgentState:

#     history = state.get(
#         "history",
#         ""
#     )

#     contextual_query = (

#         f"""
# Recent conversation:

# {history}


# Current question:

# {state["query"]}
# """

#         if history

#         else state["query"]

#     )

#     state["result"] = run_rag_agent(

#         query=contextual_query,

#         csv_path=state.get(
#             "csv_path",
#             "data/sample.csv"
#         )

#     )

#     return state


# def ml_node(state: AgentState) -> AgentState:
#     history = state.get("history", "")

#     contextual_query = (
#         f"""
# Recent conversation:

# {history}

# Current question:

# {state["query"]}
# """
#         if history
#         else state["query"]
#     )

#     state["result"] = run_ml_agent(
#         query=contextual_query,
#         csv_path=state.get(
#             "csv_path",
#             "data/sample.csv"
#         ),
        
#     )

#     return state


# def tools_node(state: AgentState) -> AgentState:
#     history = state.get("history", "")

#     contextual_query = (
#         f"""
# For context only, do not re-answer the previous conversation:

# {history}

# Answer ONLY this current question:

# {state["query"]}
# """
#         if history
#         else state["query"]
#     )

#     state["result"] = run_tools_agent(
#         contextual_query
#     )

#     return state


# graph = StateGraph(AgentState)


# graph.add_node(
#     "route",
#     route_query
# )

# graph.add_node(
#     "data",
#     data_node
# )

# graph.add_node(
#     "rag",
#     rag_node
# )

# graph.add_node(
#     "ml",
#     ml_node
# )

# graph.add_node(
#     "tools",
#     tools_node
# )


# graph.set_entry_point("route")


# graph.add_conditional_edges(
#     "route",
#     lambda state: state["route"],
#     {
#         "data": "data",
#         "rag": "rag",
#         "ml": "ml",
#         "tools": "tools",
#     }
# )


# graph.add_edge("data", END)
# graph.add_edge("rag", END)
# graph.add_edge("ml", END)
# graph.add_edge("tools", END)


# supervisor_graph = graph.compile()


# if __name__ == "__main__":

#     tests = [
#         "What is the average salary?",
#         "How many days of paid leave do employees get?",
#         "Predict the price",
#         "What is 45 * 12?",
#         "Can you plot a barplot for the first 6 rows?",
#         "Show a histogram",
#         "Create a scatter plot",
#     ]

#     for q in tests:

#         result = supervisor_graph.invoke(
#             {
#                 "query": q,
#                 "route": "",
#                 "result": None,
#                 "csv_path": "data/sample.csv",
#                 "history": "",
#             }
#         )

#         print("\n" + "=" * 60)
#         print(f"QUERY: {q}")
#         print(f"ROUTE: {result['route']}")
#         print(f"RESULT: {result['result']}")
#         print("=" * 60)
from langgraph.graph import (
    StateGraph,
    END
)

from typing import (
    TypedDict,
    Any
)


from agents.data_agent import run_data_agent

from agents.rag_agent import run_rag_agent

from agents.ml_agent import run_ml_agent

from agents.tools_agent import run_tools_agent


from config.llm import get_llm



class AgentState(
    TypedDict
):

    query: str

    route: str

    result: Any

    csv_path: str

    history: str

    long_term_memory: str



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


MEMORY_KEYWORDS = [

    "my name",

    "what is my name",

    "who am i",

    "remember me",

    "what do you know about me",

]


# ==========================================
# ROUTER
# ==========================================

def route_query(
    state: AgentState
) -> AgentState:


    query = state["query"]


    history = state.get(
        "history",
        ""
    )


    long_term_memory = state.get(
        "long_term_memory",
        ""
    )


    query_lower = query.lower()


    
    if any(

        keyword in query_lower

        for keyword in MEMORY_KEYWORDS

    ):

        if long_term_memory:

            state["route"] = "memory"

            return state


    

    if any(

        keyword in query_lower

        for keyword in PLOT_KEYWORDS

    ):

        print(
            "ROUTER: Plot -> DATA"
        )

        state["route"] = "data"

        return state


    if any(

        keyword in query_lower

        for keyword in ML_KEYWORDS

    ):

        print(
            "ROUTER: ML -> ML"
        )

        state["route"] = "ml"

        return state


    

    if any(

        keyword in query_lower

        for keyword in DATA_KEYWORDS

    ):

        print(
            "ROUTER: DATA -> DATA"
        )

        state["route"] = "data"

        return state


   

    llm = get_llm()


    routing_prompt = f"""

Classify the user's CURRENT question.

Reply with ONLY one word.

Allowed categories:

data
rag
ml
tools
memory


MEMORY:

Questions about information
the user previously told the assistant.

Examples:

What is my name?
What do you know about me?


DATA:

Questions about analyzing
the uploaded CSV dataset.


RAG:

Questions about documents
or policies.


ML:

Machine learning,
prediction,
classification,
regression.


TOOLS:

General knowledge,
mathematics,
coding,
or unrelated questions.


LONG TERM MEMORY:

{long_term_memory}


RECENT CONVERSATION:

{history}


CURRENT QUESTION:

{query}


CATEGORY:

"""


    try:

        route = (

            llm.invoke(
                routing_prompt
            )

            .content

            .strip()

            .lower()

        )


    except Exception as e:

        print(
            f"ROUTER ERROR: {e}"
        )

        route = "tools"


    valid_routes = [

        "data",

        "rag",

        "ml",

        "tools",

        "memory"

    ]


    if route not in valid_routes:

        route = "tools"


    state["route"] = route


    return state




def memory_node(
    state: AgentState
) -> AgentState:


    memory = state.get(
        "long_term_memory",
        ""
    )


    if not memory:

        state["result"] = (

            "I don't have any saved "
            "long-term information about you yet."

        )


        return state


    llm = get_llm()


    prompt = f"""

You are a helpful assistant.

Answer the user's question using ONLY
the long-term memory below.

If the answer is not available,
say you do not know.

LONG TERM MEMORY:

{memory}


QUESTION:

{state["query"]}


ANSWER:

"""


    try:

        response = llm.invoke(
            prompt
        )


        state["result"] = (
            response.content
        )


    except Exception:

        state["result"] = memory


    return state




def data_node(
    state: AgentState
) -> AgentState:


    history = state.get(
        "history",
        ""
    )


    memory = state.get(
        "long_term_memory",
        ""
    )


    contextual_query = f"""

LONG TERM MEMORY:

{memory}


RECENT CONVERSATION:

{history}


CURRENT QUESTION:

{state["query"]}

"""


    state["result"] = run_data_agent(

        query=contextual_query,

        csv_path=state.get(
            "csv_path",
            "data/sample.csv"
        ),

        current_query=state[
            "query"
        ]

    )


    return state




def rag_node(
    state: AgentState
) -> AgentState:


    history = state.get(
        "history",
        ""
    )


    memory = state.get(
        "long_term_memory",
        ""
    )


    contextual_query = f"""

LONG TERM MEMORY:

{memory}


RECENT CONVERSATION:

{history}


CURRENT QUESTION:

{state["query"]}

"""


    state["result"] = run_rag_agent(

        query=contextual_query,

        csv_path=state.get(
            "csv_path",
            "data/sample.csv"
        )

    )


    return state




def ml_node(
    state: AgentState
) -> AgentState:


    history = state.get(
        "history",
        ""
    )


    memory = state.get(
        "long_term_memory",
        ""
    )


    contextual_query = f"""

LONG TERM MEMORY:

{memory}


RECENT CONVERSATION:

{history}


CURRENT QUESTION:

{state["query"]}

"""


    state["result"] = run_ml_agent(

        query=contextual_query,

        csv_path=state.get(
            "csv_path",
            "data/sample.csv"
        )

    )


    return state



def tools_node(
    state: AgentState
) -> AgentState:


    history = state.get(
        "history",
        ""
    )


    memory = state.get(
        "long_term_memory",
        ""
    )


    contextual_query = f"""

LONG TERM MEMORY:

{memory}


RECENT CONVERSATION:

{history}


Answer ONLY the current question.


CURRENT QUESTION:

{state["query"]}

"""


    state["result"] = run_tools_agent(

        contextual_query

    )


    return state




graph = StateGraph(
    AgentState
)


graph.add_node(
    "route",
    route_query
)


graph.add_node(
    "memory",
    memory_node
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



graph.set_entry_point(
    "route"
)



graph.add_conditional_edges(

    "route",

    lambda state: state["route"],

    {

        "memory": "memory",

        "data": "data",

        "rag": "rag",

        "ml": "ml",

        "tools": "tools",

    }

)



graph.add_edge(
    "memory",
    END
)


graph.add_edge(
    "data",
    END
)


graph.add_edge(
    "rag",
    END
)


graph.add_edge(
    "ml",
    END
)


graph.add_edge(
    "tools",
    END
)




supervisor_graph = graph.compile()


import re
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

from langgraph.prebuilt import create_react_agent
from langchain_experimental.agents import create_pandas_dataframe_agent
from langchain_core.tools import tool

from config.llm import get_llm

PLOT_KEYWORDS = [
    "plot",
    "chart",
    "graph",
    "visualize",
    "visualise",
    "visualization",
    "visualisation",
    "histogram",
    "scatter",
    "pie",
    "vector",
    "quiver",
    "trend",
]


def is_plot_request(query: str) -> bool:
    """
    Check whether the CURRENT user query asks for a visualization.
    """

    query = query.lower()

    return any(keyword in query for keyword in PLOT_KEYWORDS)


def detect_plot_type(query: str) -> str:
    """
    Detect the requested plot type.
    Default = bar chart.
    """

    query = query.lower()

    if "vector" in query or "quiver" in query:
        return "vector"

    if "scatter" in query:
        return "scatter"

    if "histogram" in query or "hist " in query:
        return "histogram"

    if "pie" in query:
        return "pie"

    if "line" in query or "trend" in query:
        return "line"

    if "bar" in query:
        return "bar"

    return "bar"


def extract_row_count(query: str, default: int = 5) -> int:
    """
    Extract row count from queries such as:

    - first 10 rows
    - top 20 rows
    - plot 15 rows
    """

    query = query.lower()

    patterns = [
        r"first\s+(\d+)",
        r"top\s+(\d+)",
        r"(\d+)\s+rows",
    ]

    for pattern in patterns:

        match = re.search(pattern, query)

        if match:
            return int(match.group(1))

    return default




def make_plot(df: pd.DataFrame, query: str):

    n_rows = extract_row_count(query)

    
    n_rows = min(n_rows, len(df))

    subset = df.iloc[:n_rows]

    numeric_cols = list(
        subset.select_dtypes(include="number").columns
    )

    plot_type = detect_plot_type(query)

    
    if len(numeric_cols) == 0:

        print("No numeric columns found for plotting.")

        return None

    
    label_col = df.columns[0]

    fig, ax = plt.subplots(figsize=(10, 6))

    try:

       
        if plot_type == "bar":

            subset.set_index(label_col)[numeric_cols].plot(
                kind="bar",
                ax=ax
            )

            ax.set_title(
                f"Bar Plot - First {n_rows} Rows"
            )

            ax.set_xlabel(label_col)

            ax.set_ylabel("Value")

            plt.xticks(
                rotation=45,
                ha="right"
            )

        
        elif plot_type == "line":

            subset.set_index(label_col)[numeric_cols].plot(
                kind="line",
                marker="o",
                ax=ax
            )

            ax.set_title(
                f"Line Plot - First {n_rows} Rows"
            )

            ax.set_xlabel(label_col)

            ax.set_ylabel("Value")

            plt.xticks(
                rotation=45,
                ha="right"
            )

       
        elif plot_type == "histogram":

            subset[numeric_cols].plot(
                kind="hist",
                alpha=0.6,
                ax=ax
            )

            ax.set_title(
                f"Histogram - First {n_rows} Rows"
            )

            ax.set_xlabel("Value")

            ax.set_ylabel("Frequency")

        
        elif plot_type == "pie":

            column = numeric_cols[0]

            labels = subset[label_col].astype(str)

            ax.pie(
                subset[column],
                labels=labels,
                autopct="%1.1f%%"
            )

            ax.set_title(
                f"Pie Chart - {column}"
            )

       
        elif plot_type == "scatter":

            if len(numeric_cols) >= 2:

                x_col = numeric_cols[0]

                y_col = numeric_cols[1]

                ax.scatter(
                    subset[x_col],
                    subset[y_col]
                )

                ax.set_xlabel(x_col)

                ax.set_ylabel(y_col)

                ax.set_title(
                    f"Scatter Plot: {x_col} vs {y_col}"
                )

            else:

                column = numeric_cols[0]

                ax.scatter(
                    range(len(subset)),
                    subset[column]
                )

                ax.set_xlabel("Row Index")

                ax.set_ylabel(column)

                ax.set_title(
                    f"Scatter Plot - First {n_rows} Rows"
                )

       
        elif plot_type == "vector":

            if len(numeric_cols) >= 4:

                x, y, u, v = [

                    subset[column].to_numpy()

                    for column in numeric_cols[:4]

                ]

            elif len(numeric_cols) >= 2:

                x = np.arange(len(subset))

                y = np.zeros(len(subset))

                u = subset[numeric_cols[0]].to_numpy()

                v = subset[numeric_cols[1]].to_numpy()

            else:

                plt.close(fig)

                return None

            ax.quiver(

                x,
                y,
                u,
                v,

                angles="xy",

                scale_units="xy",

                scale=1

            )

            ax.set_title(
                f"Vector Plot - First {n_rows} Rows"
            )

            ax.set_xlabel("X")

            ax.set_ylabel("Y")

        else:

            plt.close(fig)

            return None

        plt.tight_layout()

        return fig

    except Exception as e:

        print(f"Plot creation error: {e}")

        plt.close(fig)

        return None



def build_data_tools(df: pd.DataFrame):

    @tool
    def check_nulls() -> str:
        """
        Check for null, missing, or NaN values
        in the entire dataset.
        """

        counts = df.isnull().sum()

        total = int(counts.sum())

        if total == 0:

            return "No null values found in any column."

        lines = [

            f"- {column}: {int(count)} missing value(s)"

            for column, count in counts.items()

            if count > 0

        ]

        return (

            f"Found {total} missing value(s):\n"

            + "\n".join(lines)

        )


    @tool
    def get_row_count() -> str:
        """
        Return the total number of rows.
        """

        return f"The dataset has {len(df)} rows."


    @tool
    def get_column_count() -> str:
        """
        Return the total number of columns.
        """

        return f"The dataset has {len(df.columns)} columns."


    @tool
    def get_shape() -> str:
        """
        Return dataset shape.
        """

        return (

            f"The dataset has "

            f"{df.shape[0]} rows and "

            f"{df.shape[1]} columns."

        )


    @tool
    def get_column_names() -> str:
        """
        List all dataset column names.
        """

        return (

            "Columns: "

            + ", ".join(df.columns)

        )


    @tool
    def get_dtypes() -> str:
        """
        Return the datatype of each column.
        """

        lines = [

            f"- {column}: {dtype}"

            for column, dtype

            in df.dtypes.items()

        ]

        return (

            "Column data types:\n"

            + "\n".join(lines)

        )


    @tool
    def query_dataframe(question: str) -> str:
        """
        Answer questions about the actual dataframe.

        Use this for:
        - averages
        - sums
        - maximum/minimum
        - filtering
        - grouping
        - statistics
        - comparisons
        """

        pandas_agent = create_pandas_dataframe_agent(

            get_llm(),

            df,

            verbose=True,

            allow_dangerous_code=True,

            handle_parsing_errors=True,

            max_iterations=8,

            early_stopping_method="force",

        )

        result = pandas_agent.invoke(question)

        return result["output"]


    return [

        check_nulls,

        get_row_count,

        get_column_count,

        get_shape,

        get_column_names,

        get_dtypes,

        query_dataframe,

    ]




def run_data_agent(

    query: str,

    csv_path: str = "data/sample.csv",

    current_query: str = None,

):

    # Load currently selected dataset
    df = pd.read_csv(csv_path)


    
    check_query = (

        current_query

        if current_query is not None

        else query

    )


    print("\n==============================")

    print("DATA AGENT")

    print("CSV PATH:", csv_path)

    print("CURRENT QUERY:", check_query)

    print("==============================\n")



    if is_plot_request(check_query):

        print("PLOT REQUEST DETECTED")

        fig = make_plot(

            df,

            check_query

        )

        if fig is not None:

            print("PLOT CREATED SUCCESSFULLY")

            return fig

        print("PLOT CREATION FAILED - FALLING BACK TO AGENT")



    tools = build_data_tools(df)


    agent = create_react_agent(

        get_llm(),

        tools

    )


   
    if current_query:

        message = f"""

You are a Data Analysis Agent.

Use the recent conversation only to understand references.

Recent conversation:

{query}

IMPORTANT:

Answer ONLY this current question:

{current_query}

Use the available tools when needed.
"""

    else:

        message = query


    result = agent.invoke(

        {

            "messages": [

                {

                    "role": "user",

                    "content": message

                }

            ]

        }

    )


   

    final_message = result["messages"][-1]


    return final_message.content



if __name__ == "__main__":

    answer = run_data_agent(

        query="Create a bar chart of the first 5 rows",

        csv_path="data/sample.csv",

        current_query="Create a bar chart of the first 5 rows",

    )


    if isinstance(answer, plt.Figure):

        print("Figure created successfully.")

        plt.show()

    else:

        print("ANSWER:")

        print(answer)


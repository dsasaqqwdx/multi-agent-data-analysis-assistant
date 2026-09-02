

import re
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.impute import SimpleImputer

from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
    accuracy_score,
    f1_score,
)

from sklearn.linear_model import (
    LinearRegression,
    Ridge,
    LogisticRegression,
)

from sklearn.ensemble import (
    RandomForestRegressor,
    RandomForestClassifier,
    GradientBoostingRegressor,
    GradientBoostingClassifier,
)

from sklearn.tree import (
    DecisionTreeRegressor,
    DecisionTreeClassifier,
)

from sklearn.neighbors import (
    KNeighborsRegressor,
    KNeighborsClassifier,
)



def get_dataset_summary(df: pd.DataFrame) -> str:

    lines = []

    lines.append(f"Rows: {df.shape[0]}")
    lines.append(f"Columns: {df.shape[1]}")
    lines.append("")

    for col in df.columns:

        dtype = str(df[col].dtype)

        unique = df[col].nunique(
            dropna=True
        )

        missing = int(
            df[col].isnull().sum()
        )

        lines.append(
            f"{col} | "
            f"dtype={dtype} | "
            f"unique={unique} | "
            f"missing={missing}"
        )

    return "\n".join(lines)


def normalize_text(text: str) -> str:

    return re.sub(
        r"[^a-z0-9]+",
        "",
        str(text).lower()
    )



def detect_target_column(query: str, df: pd.DataFrame):
    query_lower = query.lower()
    columns = list(df.columns)


    prediction_patterns = [
        r"predict\s+(?:the\s+)?([a-zA-Z0-9_ ]+?)(?:\s+of\b|\s+for\b|\s+using\b|\.|,|$)",
        r"prediction\s+for\s+([a-zA-Z0-9_ ]+?)(?:\.|,|$)",
        r"estimate\s+(?:the\s+)?([a-zA-Z0-9_ ]+?)(?:\s+of\b|\s+for\b|\.|,|$)",
        r"forecast\s+(?:the\s+)?([a-zA-Z0-9_ ]+?)(?:\s+of\b|\s+for\b|\.|,|$)",
    ]

    for pattern in prediction_patterns:
        match = re.search(pattern, query_lower)
        if match:
            candidate = match.group(1).strip()
            for col in columns:
                if normalize_text(col) == normalize_text(candidate):
                    return col

    target_patterns = [
        (r"predict\s+(?:the\s+)?salary", ["salary"]),
        (r"predict\s+(?:the\s+)?income", ["income"]),
        (r"predict\s+(?:the\s+)?department", ["department"]),
        (r"predict\s+(?:the\s+)?age", ["age"]),
    ]

    for pattern, possible_names in target_patterns:
        if re.search(pattern, query_lower):
            for possible_name in possible_names:
                for col in columns:
                    if normalize_text(col) == normalize_text(possible_name):
                        return col

    prediction_words = ["predict", "prediction", "estimate", "forecast", "calculate"]

    if any(word in query_lower for word in prediction_words):
        best_col = None
        best_pos = None

        for col in columns:
            col_lower = col.lower()
            pattern = r"\b" + re.escape(col_lower) + r"\b"
            m = re.search(pattern, query_lower)
            if m and (best_pos is None or m.start() < best_pos):
                best_pos = m.start()
                best_col = col

        if best_col:
            return best_col

    return None


def detect_problem_type(
    df: pd.DataFrame,
    target: str
):

    series = df[target].dropna()

    if len(series) == 0:

        return None

    
    if not pd.api.types.is_numeric_dtype(
        series
    ):

        return "classification"

    unique_values = series.nunique()

    unique_ratio = (
        unique_values /
        max(len(series), 1)
    )

  
    if pd.api.types.is_integer_dtype(
        series
    ):

        if (
            unique_values <= 20
            and unique_ratio < 0.5
        ):

            return "classification"

    if unique_values <= 10:

        return "classification"

    return "regression"


def determine_features(
    df: pd.DataFrame,
    target: str
):

    features = []

    for col in df.columns:

        if col == target:

            continue

        non_null = df[col].dropna()

        if len(non_null) == 0:

            continue

        
        if df[col].nunique(
            dropna=True
        ) <= 1:

            continue

        unique_ratio = (

            df[col].nunique(
                dropna=True
            )

            /

            max(
                len(df),
                1
            )

        )

        col_lower = col.lower()


        likely_id = any(

            keyword in col_lower

            for keyword in [

                "id",
                "uuid",
                "identifier",
                "serial",
                "registration",

            ]

        )


        likely_name = (

            "name" in col_lower

            and unique_ratio > 0.7

        )

        
        if (

            likely_id

            and unique_ratio > 0.5

        ):

            continue

        if likely_name:

            continue

        features.append(
            col
        )

    return features



def build_preprocessor(
    X: pd.DataFrame
):

    numeric_features = list(

        X.select_dtypes(

            include=["number"]

        ).columns

    )

    categorical_features = [

        col

        for col in X.columns

        if col not in numeric_features

    ]


    numeric_transformer = Pipeline(

        steps=[

            (

                "imputer",

                SimpleImputer(
                    strategy="median"
                ),

            )

        ]

    )

    categorical_transformer = Pipeline(

        steps=[

            (

                "imputer",

                SimpleImputer(
                    strategy="most_frequent"
                ),

            ),

            (

                "encoder",

                OneHotEncoder(
                    handle_unknown="ignore"
                ),

            ),

        ]

    )

    transformers = []

    if numeric_features:

        transformers.append(

            (

                "num",

                numeric_transformer,

                numeric_features,

            )

        )

    if categorical_features:

        transformers.append(

            (

                "cat",

                categorical_transformer,

                categorical_features,

            )

        )

    return ColumnTransformer(

        transformers=transformers

    )


def get_models(
    problem_type: str,
    train_size: int
):

    if problem_type == "regression":

        n_neighbors = max(

            1,

            min(
                5,
                train_size
            )

        )

        return {

            "Linear Regression":

                LinearRegression(),

            "Ridge Regression":

                Ridge(),

            "Decision Tree":

                DecisionTreeRegressor(
                    random_state=42
                ),

            "Random Forest":

                RandomForestRegressor(
                    n_estimators=100,
                    random_state=42
                ),

            "Gradient Boosting":

                GradientBoostingRegressor(
                    random_state=42
                ),

            "KNN":

                KNeighborsRegressor(
                    n_neighbors=n_neighbors
                ),

        }

    n_neighbors = max(

        1,

        min(
            5,
            train_size
        )

    )

    return {

        "Logistic Regression":

            LogisticRegression(
                max_iter=2000
            ),

        "Decision Tree":

            DecisionTreeClassifier(
                random_state=42
            ),

        "Random Forest":

            RandomForestClassifier(
                n_estimators=100,
                random_state=42
            ),

        "Gradient Boosting":

            GradientBoostingClassifier(
                random_state=42
            ),

        "KNN":

            KNeighborsClassifier(
                n_neighbors=n_neighbors
            ),

    }



def safe_train_test_split(
    X,
    y,
    problem_type
):

    if len(X) < 8:

        return None

    test_size = max(

        2,

        int(
            round(
                len(X) * 0.2
            )
        )

    )

    test_size = min(

        test_size,

        len(X) - 2

    )

    if test_size <= 0:

        return None

    try:

        if problem_type == "classification":

            class_counts = y.value_counts()

            if (

                len(class_counts) > 1

                and

                class_counts.min() >= 2

            ):

                return train_test_split(

                    X,

                    y,

                    test_size=test_size,

                    random_state=42,

                    stratify=y,

                )

        return train_test_split(

            X,

            y,

            test_size=test_size,

            random_state=42,

        )

    except Exception:

        return train_test_split(

            X,

            y,

            test_size=test_size,

            random_state=42,

        )



def evaluate_model(

    pipeline,

    X_train,

    X_test,

    y_train,

    y_test,

    problem_type

):

    pipeline.fit(

        X_train,

        y_train

    )

    predictions = pipeline.predict(

        X_test

    )


    if problem_type == "regression":

        mae = mean_absolute_error(

            y_test,

            predictions

        )

        mse = mean_squared_error(

            y_test,

            predictions

        )

        rmse = mse ** 0.5

        try:

            r2 = r2_score(

                y_test,

                predictions

            )

        except Exception:

            r2 = None

        return {

            "pipeline":

                pipeline,

            "score":

                -mae,

            "metrics": {

                "MAE":

                    mae,

                "RMSE":

                    rmse,

                "R2":

                    r2,

            },

        }

    accuracy = accuracy_score(

        y_test,

        predictions

    )

    f1 = f1_score(

        y_test,

        predictions,

        average="weighted",

        zero_division=0,

    )

    return {

        "pipeline":

            pipeline,

        "score":

            accuracy,

        "metrics": {

            "Accuracy":

                accuracy,

            "F1 Score":

                f1,

        },

    }



def normalize_model_name(
    name: str
):

    name = name.lower()

    mappings = {

        "linear regression":

            "Linear Regression",

        "linear":

            "Linear Regression",

        "ridge":

            "Ridge Regression",

        "ridge regression":

            "Ridge Regression",

        "decision tree":

            "Decision Tree",

        "tree":

            "Decision Tree",

        "random forest":

            "Random Forest",

        "forest":

            "Random Forest",

        "gradient boosting":

            "Gradient Boosting",

        "boosting":

            "Gradient Boosting",

        "knn":

            "KNN",

        "k nearest neighbors":

            "KNN",

        "logistic regression":

            "Logistic Regression",

        "logistic":

            "Logistic Regression",

    }

    for key, value in mappings.items():

        if key in name:

            return value

    return None



def detect_requested_model(
    query: str
):

    query_lower = query.lower()

    model_names = [

        "linear regression",

        "ridge regression",

        "decision tree",

        "random forest",

        "gradient boosting",

        "knn",

        "k nearest neighbors",

        "logistic regression",

    ]

    for name in model_names:

        if name in query_lower:

            return normalize_model_name(
                name
            )

    return None


def find_person_row(
    query: str,
    df: pd.DataFrame
):

    name_columns = [

        col

        for col in df.columns

        if "name" in col.lower()

    ]

    if not name_columns:

        return None, None

    name_column = name_columns[0]

    query_lower = query.lower()

    for value in df[name_column].dropna():

        person_name = str(value).strip()

        if not person_name:

            continue

        pattern = (

            r"\b" +

            re.escape(
                person_name.lower()
            ) +

            r"\b"

        )

        if re.search(

            pattern,

            query_lower

        ):

            matched_rows = df[

                df[name_column]

                .astype(str)

                .str.lower()

                == person_name.lower()

            ]

            if not matched_rows.empty:

                return (

                    matched_rows.iloc[0],

                    name_column

                )

    return None, None


def clean_categorical_value(
    value: str
):

    value = value.strip()

    value = re.sub(

        r"\s+",

        " ",

        value

    )

    value = re.sub(

        r"[.,;!?]+$",

        "",

        value

    )

    return value



def extract_prediction_values(

    query: str,

    features,

    df: pd.DataFrame

):

    values = {}

    query_lower = query.lower()


    person_row, name_column = find_person_row(

        query,

        df

    )


    if person_row is not None:

        for feature in features:

            if feature in person_row.index:

                value = person_row[feature]

                if pd.notna(value):

                    values[feature] = value


    for feature in features:

        feature_lower = feature.lower()


        if pd.api.types.is_numeric_dtype(

            df[feature]

        ):

            patterns = [

                # age is 25
                rf"\b{re.escape(feature_lower)}\b\s*(?:is|=|:)\s*(-?\d+(?:\.\d+)?)",

                # age 25
                rf"\b{re.escape(feature_lower)}\b\s+(-?\d+(?:\.\d+)?)",

            ]

           
            if feature_lower in [

                "age",
                "years old",

            ]:

                patterns.extend(

                    [

                        r"\b(\d+(?:\.\d+)?)\s+years?\s+old\b",

                        r"\bage\s+(\d+(?:\.\d+)?)\b",

                    ]

                )

            for pattern in patterns:

                match = re.search(

                    pattern,

                    query_lower,

                    flags=re.IGNORECASE

                )

                if match:

                    values[feature] = float(

                        match.group(1)

                    )

                    break

        else:

            
            categories = (

                df[feature]

                .dropna()

                .astype(str)

                .unique()

            )

            found_category = None

            
            for category in categories:

                category_text = str(

                    category

                ).strip()

                if not category_text:

                    continue

                pattern = (

                    r"\b" +

                    re.escape(
                        category_text.lower()
                    ) +

                    r"\b"

                )

                if re.search(

                    pattern,

                    query_lower

                ):

                    found_category = category_text

                    break

            
            if found_category is None:

                patterns = [

                    rf"\b{re.escape(feature_lower)}\b\s*(?:is|=|:)\s*([a-zA-Z][a-zA-Z ]+?)(?=\.|,|$)",

                    rf"\bworks?\s+in\s+(?:the\s+)?([a-zA-Z ]+?)(?:\s+{re.escape(feature_lower)}|\s+department|\.|,|$)",

                ]

                for pattern in patterns:

                    match = re.search(

                        pattern,

                        query_lower,

                        flags=re.IGNORECASE

                    )

                    if match:

                        candidate = clean_categorical_value(

                            match.group(1)

                        )

                        for category in categories:

                            if (

                                normalize_text(
                                    candidate
                                )

                                ==

                                normalize_text(
                                    category
                                )

                            ):

                                found_category = str(

                                    category

                                )

                                break

                        if found_category:

                            break

            if found_category is not None:

                values[feature] = found_category

    return values


def build_prediction_input(

    features,

    extracted_values,

    df

):

    row = {}

    for feature in features:

        if feature in extracted_values:

            row[feature] = (

                extracted_values[
                    feature
                ]

            )

        else:

            row[feature] = None

    return pd.DataFrame(

        [row]

    )

def train_and_select_model(

    df,

    target,

    features,

    problem_type,

    requested_model=None

):

    working_df = df[

        features + [target]

    ].copy()

    working_df = working_df.dropna(

        subset=[target]

    )

    X = working_df[

        features

    ]

    y = working_df[

        target

    ]

    split = safe_train_test_split(

        X,

        y,

        problem_type

    )

    if split is None:

        return {

            "error":

                (
                    "The dataset is too small for reliable "
                    "train/test model evaluation. "
                    "Please upload at least 8 usable rows."
                )

        }

    (

        X_train,

        X_test,

        y_train,

        y_test,

    ) = split

    models = get_models(

        problem_type,

        len(X_train)

    )


    if requested_model:

        if requested_model not in models:

            return {

                "error":

                    (
                        f"{requested_model} is not suitable "
                        f"for this {problem_type} task."
                    )

            }

        models = {

            requested_model:

                models[
                    requested_model
                ]

        }

    results = {}

    for model_name, model in models.items():

        try:

            preprocessor = build_preprocessor(

                X_train

            )

            pipeline = Pipeline(

                steps=[

                    (

                        "preprocessor",

                        preprocessor

                    ),

                    (

                        "model",

                        model

                    ),

                ]

            )

            evaluation = evaluate_model(

                pipeline,

                X_train,

                X_test,

                y_train,

                y_test,

                problem_type

            )

            results[model_name] = evaluation

        except Exception as e:

            print(

                f"Model failed: "
                f"{model_name} -> {e}"

            )

            continue

    if not results:

        return {

            "error":

                (
                    "No model could be trained successfully "
                    "on this dataset."
                )

        }

    best_model_name = max(

        results,

        key=lambda name:

            results[name][
                "score"
            ]

    )

    best_result = results[

        best_model_name

    ]


    final_preprocessor = build_preprocessor(

        X

    )

    final_model = get_models(

        problem_type,

        len(X)

    )[

        best_model_name

    ]

    final_pipeline = Pipeline(

        steps=[

            (

                "preprocessor",

                final_preprocessor

            ),

            (

                "model",

                final_model

            ),

        ]

    )

    final_pipeline.fit(

        X,

        y

    )

    return {

        "pipeline":

            final_pipeline,

        "model_name":

            best_model_name,

        "problem_type":

            problem_type,

        "features":

            features,

        "metrics":

            best_result[
                "metrics"
            ],

        "all_results":

            results,

    }



def format_metrics(
    metrics
):

    lines = []

    for key, value in metrics.items():

        if value is None:

            lines.append(

                f"{key}: "
                f"Not available"

            )

        else:

            lines.append(

                f"{key}: "
                f"{value:.4f}"

            )

    return "\n".join(

        lines

    )


def run_ml_agent(

    query: str,

    csv_path: str = "data/sample.csv"

) -> str:


    try:

        df = pd.read_csv(

            csv_path

        )

    except Exception as e:

        return (

            f"Could not read the dataset: {e}"

        )

    if df.empty:

        return (

            "The uploaded dataset is empty."

        )


    target = detect_target_column(

        query,

        df

    )

    if target is None:

        columns = ", ".join(

            df.columns

        )

        return (

            "I could not determine which column "
            "you want to predict.\n\n"

            f"Available columns: {columns}\n\n"

            "Try asking:\n"

            f"'Predict the {df.columns[-1]}'"
        )


    problem_type = detect_problem_type(

        df,

        target

    )

    if problem_type is None:

        return (

            f"Unable to determine the ML problem "
            f"type for target column '{target}'."

        )


    features = determine_features(

        df,

        target

    )

    if not features:

        return (

            f"No useful feature columns were found "
            f"to predict '{target}'."

        )


    requested_model = detect_requested_model(

        query

    )


    training_result = train_and_select_model(

        df=df,

        target=target,

        features=features,

        problem_type=problem_type,

        requested_model=requested_model

    )

    if "error" in training_result:

        return training_result[

            "error"

        ]


    extracted_values = extract_prediction_values(

        query,

        features,

        df

    )


    prediction_input = build_prediction_input(

        features,

        extracted_values,

        df

    )


    try:

        prediction = training_result[

            "pipeline"

        ].predict(

            prediction_input

        )[0]

    except Exception as e:

        return (

            "Model trained successfully, "
            f"but prediction failed: {e}"

        )

    model_name = training_result[

        "model_name"

    ]

    metrics = training_result[

        "metrics"

    ]


    result_lines = [

        f"Target: {target}",

        f"Problem type: {problem_type}",

        f"Model used: {model_name}",

        "",

        "Model performance:",

        format_metrics(
            metrics
        ),

        "",

        "Features used:",

        ", ".join(
            features
        ),

        "",

        f"Prediction for {target}: {prediction}",

    ]

    if extracted_values:

        result_lines.extend(

            [

                "",

                "Values used:",

                ", ".join(

                    f"{key}={value}"

                    for key, value

                    in extracted_values.items()

                ),

            ]

        )

    else:

        result_lines.extend(

            [

                "",

                "No feature values were detected.",

                "Missing values were handled "
                "using the preprocessing pipeline.",

            ]

        )


    if len(df) < 30:

        result_lines.extend(

            [

                "",

                "Warning: This dataset is relatively small, "
                "so model performance and predictions may "
                "not be reliable.",

            ]

        )

    return "\n".join(

        result_lines

    )


if __name__ == "__main__":

    answer = run_ml_agent(

        query=(
            "Predict the salary of Teju. "
            "Teju is 25 years old and works "
            "in the Engineering department."
        ),

        csv_path="data/sample.csv"

    )

    print(answer)
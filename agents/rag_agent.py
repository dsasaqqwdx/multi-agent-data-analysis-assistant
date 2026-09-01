
import os
import hashlib
import pandas as pd

from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

from config.llm import get_llm


EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


def get_persist_dir(csv_path: str) -> str:
    csv_hash = hashlib.md5(
        os.path.abspath(csv_path).encode()
    ).hexdigest()

    return os.path.join(
        "vectorstore",
        "db",
        csv_hash
    )


def build_vectorstore(csv_path: str):
    persist_dir = get_persist_dir(csv_path)

    df = pd.read_csv(csv_path)

    documents = []

    for index, row in df.iterrows():

        row_text = "\n".join(
            f"{column}: {value}"
            for column, value in row.items()
        )

        documents.append(
            Document(
                page_content=row_text,
                metadata={
                    "row_index": int(index),
                    "source": csv_path
                }
            )
        )

    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL
    )

    db = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        persist_directory=persist_dir
    )

    return db


def load_or_create_vectorstore(csv_path: str):

    persist_dir = get_persist_dir(csv_path)

    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL
    )

    if os.path.exists(persist_dir) and os.listdir(persist_dir):

        print("Loading existing ChromaDB...")

        db = Chroma(
            persist_directory=persist_dir,
            embedding_function=embeddings
        )

        return db

    print("Creating new ChromaDB...")

    return build_vectorstore(csv_path)


def run_rag_agent(
    query: str,
    csv_path: str
) -> str:

    if not os.path.exists(csv_path):

        return f"Dataset not found: {csv_path}"

    try:

        db = load_or_create_vectorstore(
            csv_path
        )

        retriever = db.as_retriever(
            search_kwargs={
                "k": 5
            }
        )

        docs = retriever.invoke(
            query
        )

        if not docs:

            return (
                "I could not find relevant information "
                "in the uploaded dataset."
            )

        context = "\n\n".join(

            f"Dataset row {doc.metadata.get('row_index')}:\n"
            f"{doc.page_content}"

            for doc in docs

        )

        llm = get_llm()

        prompt = f"""
You are a dataset question-answering assistant.

Answer the user's question using ONLY the dataset context below.

Do not use outside knowledge.

If the answer is not available in the retrieved context, say:

"I don't know based on the uploaded dataset."

Dataset context:

{context}

Question:

{query}

Answer:
"""

        response = llm.invoke(
            prompt
        )

        return response.content

    except Exception as e:

        return (
            f"RAG Agent Error: {str(e)}"
        )


if __name__ == "__main__":

    answer = run_rag_agent(

        query="What medicines are used for bacterial infections?",

        csv_path="data/sample.csv"

    )

    print(answer)
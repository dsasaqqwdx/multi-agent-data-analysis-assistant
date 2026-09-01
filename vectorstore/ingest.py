from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
import os

def build_vectorstore():
    loader = TextLoader("vectorstore/sample_docs/company_policy.txt")
    docs = loader.load()

    splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=20)
    chunks = splitter.split_documents(docs)

    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    db = Chroma.from_documents(
        chunks,
        embeddings,
        persist_directory="vectorstore/db"
    )
    print(f"Vectorstore built with {len(chunks)} chunks.")

if __name__ == "__main__":
    build_vectorstore()
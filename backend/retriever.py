from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
import chromadb
from config import (
    OPENAI_API_KEY,
    EMBEDDING_MODEL,
    CHROMA_DB_PATH,
    COLLECTION_NAME
)

def load_vectorstore() -> Chroma:
    embeddings = OpenAIEmbeddings(
        model=EMBEDDING_MODEL,
        openai_api_key=OPENAI_API_KEY
    )

    vectorstore = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=CHROMA_DB_PATH
    )

    return vectorstore

def retrieve_relevant_chunks(question: str, top_k: int = 5) -> list[dict]:
    vectorstore = load_vectorstore()

    results = vectorstore.similarity_search_with_score(
        query=question,
        k=top_k
    )

    chunks = []
    for document, score in results:
        source = document.metadata.get("source", "unknown")
        source = source.replace("\\", "/")  
        chunks.append({
            "text": document.page_content,
            "source": source,
            "language": document.metadata.get("language", "unknown"),
            "chunk_index": document.metadata.get("chunk_index", 0),
            "similarity_score": round(score, 4)
        })

    return chunks

def is_vectorstore_empty() -> bool:
    client = chromadb.PersistentClient(path=CHROMA_DB_PATH)

    try:
        collection = client.get_collection(name=COLLECTION_NAME)
        return collection.count() == 0
    except Exception:
        return True
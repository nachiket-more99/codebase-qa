import os
from pathlib import Path
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from config import (
    OPENAI_API_KEY,
    EMBEDDING_MODEL,
    CHROMA_DB_PATH,
    COLLECTION_NAME,
    CHUNK_SIZE,
    CHUNK_OVERLAP
)

EXTENSION_TO_LANGUAGE = {
    ".py": "python",
    ".js": "js",
    ".jsx": "js",
    ".ts": "ts",
    ".tsx": "ts",
    ".java": "java",
    ".cpp": "cpp",
    ".c": "c",
    ".go": "go",
    ".rb": "ruby",
    ".rs": "rust",
}

IGNORED_EXTENSIONS = {
    ".json", ".lock", ".md", ".txt", ".env",
    ".png", ".jpg", ".svg", ".ico", ".gif",
    ".css", ".scss", ".yaml", ".yml", ".xml",
}

def get_language(file_path: str) -> str | None:
    ext = Path(file_path).suffix.lower()
    return EXTENSION_TO_LANGUAGE.get(ext, None)

def chunk_file(file_path: str, file_content: str) -> list[dict]:
    language = get_language(file_path)

    if language:
        splitter = RecursiveCharacterTextSplitter.from_language(
            language=language,
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP
        )
    else:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP
        )

    raw_chunks = splitter.split_text(file_content)

    chunks = []
    for index, chunk_text in enumerate(raw_chunks):
        chunks.append({
            "text": chunk_text,
            "metadata": {
                "source": file_path,
                "language": language or "unknown",
                "chunk_index": index,
                "total_chunks": len(raw_chunks)
            }
        })

    return chunks

def ingest_file(file_path: str, file_content: str) -> dict:
    chunks = chunk_file(file_path, file_content)

    if not chunks:
        return {"status": "error", "message": "No chunks generated from file"}

    texts = [chunk["text"] for chunk in chunks]
    metadatas = [chunk["metadata"] for chunk in chunks]

    embeddings = OpenAIEmbeddings(
        model=EMBEDDING_MODEL,
        openai_api_key=OPENAI_API_KEY
    )

    Chroma.from_texts(
        texts=texts,
        metadatas=metadatas,
        embedding=embeddings,
        persist_directory=CHROMA_DB_PATH,
        collection_name=COLLECTION_NAME
    )

    return {
        "status": "success",
        "file": file_path,
        "chunks_created": len(chunks),
        "language": chunks[0]["metadata"]["language"]
    }
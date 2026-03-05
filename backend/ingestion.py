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
    
def ingest_multiple_files(files: list[dict]) -> dict:
    import time

    total_chunks = 0
    ingested_files = []
    failed_files = []
    all_texts = []
    all_metadatas = []

    for file in files:
        file_name = file["name"]
        file_content = file["content"]

        ext = Path(file_name).suffix.lower()
        if ext in IGNORED_EXTENSIONS:
            continue

        if not file_content.strip():
            continue

        try:
            chunks = chunk_file(file_name, file_content)

            if not chunks:
                continue

            all_texts.extend([chunk["text"] for chunk in chunks])
            all_metadatas.extend([chunk["metadata"] for chunk in chunks])

            ingested_files.append({
                "file": file_name,
                "chunks": len(chunks),
                "language": chunks[0]["metadata"]["language"]
            })
            total_chunks += len(chunks)

        except Exception as e:
            failed_files.append({"file": file_name, "error": str(e)})

    BATCH_SIZE = 50
    embeddings = OpenAIEmbeddings(
        model=EMBEDDING_MODEL,
        openai_api_key=OPENAI_API_KEY
    )

    for i in range(0, len(all_texts), BATCH_SIZE):
        batch_texts = all_texts[i:i + BATCH_SIZE]
        batch_metadatas = all_metadatas[i:i + BATCH_SIZE]

        Chroma.from_texts(
            texts=batch_texts,
            metadatas=batch_metadatas,
            embedding=embeddings,
            persist_directory=CHROMA_DB_PATH,
            collection_name=COLLECTION_NAME
        )

        time.sleep(0.5)

    return {
        "status": "success",
        "total_files_ingested": len(ingested_files),
        "total_chunks_created": total_chunks,
        "ingested_files": ingested_files,
        "failed_files": failed_files
    }
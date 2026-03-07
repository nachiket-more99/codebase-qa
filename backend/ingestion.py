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

IGNORED_FILENAMES = {
    "index.ts", "index.js",
    "index.tsx", "index.jsx",
    "vite.config.ts",
    "eslint.config.js",
    "eslint.config.mjs",
    "jest.config.ts",
    "jest.config.js",
    ".gitignore",
    ".env.example",
    "index.html",
    "migration_lock.toml",
    "LICENSE",
    ".prettierrc",
    "app.e2e-spec.ts",
    "mock-data.ts",
}

IGNORED_FOLDERS = {
    ".git", "node_modules", "__pycache__",
    "dist", "build", ".next", "coverage",
    "venv", ".venv", "vendor",
    "ui",
    "migrations",
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

def ingest_github_repo(repo_url: str) -> dict:
    import tempfile
    import shutil
    import git

    temp_dir = tempfile.mkdtemp()

    try:
        print(f"Cloning {repo_url}...")
        git.Repo.clone_from(repo_url, temp_dir)
        print("Clone complete.")

        files_data = []
        for root, dirs, files in os.walk(temp_dir):
            dirs[:] = [d for d in dirs if d not in IGNORED_FOLDERS]

            for file_name in files:
                file_path = os.path.join(root, file_name)
                ext = Path(file_name).suffix.lower()

                if ext in IGNORED_EXTENSIONS:
                    continue

                if file_name in IGNORED_FILENAMES:
                    continue

                if os.path.getsize(file_path) > 100_000:
                    continue

                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                except (UnicodeDecodeError, PermissionError):
                    continue

                if not content.strip():
                    continue

                relative_path = os.path.relpath(file_path, temp_dir)
                relative_path = relative_path.replace("\\", "/")

                files_data.append({
                    "name": relative_path,
                    "content": content
                })

        print(f"Found {len(files_data)} code files to ingest.")

        all_file_paths = [f["name"] for f in files_data]
        meaningful_paths = filter_files_with_llm(all_file_paths)
        meaningful_paths_set = set(meaningful_paths)
        files_data = [f for f in files_data if f["name"] in meaningful_paths_set]
        print(f"Ingesting {len(files_data)} files after LLM filter.")

        result = ingest_multiple_files(files_data)
        result["repo_url"] = repo_url
        result["files_found"] = len(files_data)

        return result

    except git.exc.GitCommandError as e:
        return {"status": "error", "message": f"Failed to clone repo: {str(e)}"}

    except Exception as e:
        return {"status": "error", "message": f"Ingestion failed: {str(e)}"}

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
        print("Temp directory cleaned up.")

def filter_files_with_llm(file_paths: list[str]) -> list[str]:
    import json
    from langchain_openai import ChatOpenAI
    from langchain_core.messages import SystemMessage, HumanMessage

    file_list = "\n".join(file_paths)

    system = SystemMessage(content="""You are a code analysis assistant.
Given a list of files from a software repository, return ONLY the files
that contain meaningful source code worth indexing for a codebase Q&A tool.

EXCLUDE:
- Config files (.prettierrc, eslint.config, jest.config, vite.config etc)
- Lock files, dotfiles, environment files (.env.example, .gitignore etc)
- Generated or compiled output (dist/, build/)
- Database migration files
- Test fixtures and mock data files
- License, readme, documentation files
- Barrel/re-export only files (index.ts, index.js that just re-export)
- Auto-generated UI component libraries (shadcn/ui, radix etc)
- Package manager files (package.json, requirements.txt etc)

INCLUDE:
- Application source code with real business logic
- API handlers, controllers, routes
- Services and repositories
- Database models and schemas
- Custom hooks and utilities
- Core application components you wrote
- Guards, middleware, decorators
- DTOs with meaningful validation logic

Respond with ONLY a valid JSON array of file paths to keep.
No explanation, no markdown, no code fences. Just the JSON array.""")

    human = HumanMessage(content=f"Here are the repository files:\n\n{file_list}")

    llm = ChatOpenAI(
        model=LLM_MODEL,
        openai_api_key=OPENAI_API_KEY,
        temperature=0
    )

    response = llm.invoke([system, human])

    try:
        content = response.content.strip()
        content = content.replace("```json", "").replace("```", "").strip()
        filtered = json.loads(content)
        print(f"LLM kept {len(filtered)} / {len(file_paths)} files")
        return filtered
    except Exception as e:
        print(f"LLM filtering failed: {e}. Using original file list.")
        return file_paths
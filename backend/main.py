from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from ingestion import ingest_file, ingest_multiple_files, ingest_github_repo, clear_collection
from retriever import retrieve_relevant_chunks, is_vectorstore_empty
from qa_chain import answer_question

app = FastAPI(title="Codebase Q&A API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

class QuestionModel(BaseModel):
    question: str
    top_k: int = 5

class RepoRequest(BaseModel):
    repo_url: str


@app.get("/")
def root():
    return {
        "status": "running",
        "message": "Codebase Q&A API is live",
        "endpoints": {
            "ingest": "POST /ingest - upload a code file",
            "ask": "POST /ask - ask a question about the code",
            "status": "GET /status - check if a file has been ingested",
            "clear": "DELETE /clear - clear all ingested data"
        }
    }

# @app.get("/status")
# def status():
#     empty = is_vectorstore_empty()
#     return {
#         "status": "ready" if not empty else "empty",
#         "has_data": not empty,
#         "message": "Code is ingested and ready for questions" if not empty else "No code ingested yet. Use POST /ingest first."
#     }
@app.get("/status")
def status():
    import chromadb
    client = chromadb.PersistentClient(path="./chroma_db")
    try:
        collection = client.get_collection(name="codebase")
        count = collection.count()
        files = list(set([
            m["source"] for m in 
            collection.get(include=["metadatas"])["metadatas"]
        ]))
        return {
            "status": "ready" if count > 0 else "empty",
            "has_data": count > 0,
            "total_chunks": count,
            "total_files": len(files),
        }
    except Exception:
        return {
            "status": "empty",
            "has_data": False,
            "total_chunks": 0,
            "total_files": 0,
        }

@app.post("/ingest")
async def ingest(file: UploadFile = File(...)):
    content_bytes = await file.read()

    try:
        content = content_bytes.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="File must be a text/code file")

    if not content.strip():
        raise HTTPException(status_code=400, detail="File is empty")

    result = ingest_file(file.filename, content)

    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result["message"])

    return result

@app.post("/ingest-multiple")
async def ingest_multiple(files: list[UploadFile] = File(...)):
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")

    files_data = []
    for file in files:
        content_bytes = await file.read()
        try:
            content = content_bytes.decode("utf-8")
            files_data.append({"name": file.filename, "content": content})
        except UnicodeDecodeError:
            continue

    if not files_data:
        raise HTTPException(status_code=400, detail="No readable files provided")

    result = ingest_multiple_files(files_data)
    return result

@app.post("/ingest-repo")
def ingest_repo(request: RepoRequest):
    if not request.repo_url.startswith("https://github.com/"):
        raise HTTPException(
            status_code=400,
            detail="Please provide a valid GitHub URL starting with https://github.com/"
        )

    result = ingest_github_repo(request.repo_url)
    return result

@app.post("/ask")
def ask(request: QuestionModel):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    result = answer_question(request.question, top_k=request.top_k)

    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result["message"])

    return result

@app.delete("/clear")
def clear():
    result = clear_collection()
    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result["message"])
    return result
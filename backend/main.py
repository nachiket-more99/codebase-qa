from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from ingestion import ingest_file, ingest_multiple_files

app = FastAPI(title="Codebase Q&A API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/")
def root():
    return {"status": "running", "message": "Codebase Q&A API is live"}

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
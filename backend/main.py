from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from ingestion import ingest_file

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
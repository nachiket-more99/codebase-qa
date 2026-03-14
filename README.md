# Codebase Q&A

A RAG-powered API that lets you ask natural language questions about any codebase.

Point it at a GitHub repository or upload a code file - then ask questions like:
- *"How is authentication handled?"*
- *"Where is Redis used?"*
- *"What happens when a transfer is made?"*

Built with React, TypeScript, Tailwind CSS, shadcn, FastAPI, LangChain, ChromaDB, and OpenAI.

---

## How It Works
```
GitHub Repo URL
      ↓
Clone → Smart file filtering (LLM-powered)
      ↓
Chunk code files by language structure
      ↓
Embed chunks using OpenAI text-embedding-3-small
      ↓
Store vectors in ChromaDB
      ↓
User asks a question
      ↓
Question → embedding → similarity search → top 5 chunks
      ↓
GPT-4o-mini answers using only retrieved chunks
      ↓
Answer + source file references
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| API | FastAPI |
| AI Orchestration | LangChain |
| Embeddings | OpenAI text-embedding-3-small |
| LLM | GPT-4o-mini |
| Vector Database | ChromaDB |
| Repo Cloning | GitPython |
| Frontend | React, TypeScript, Tailwind CSS, shadcn |

---

## Getting Started

### Prerequisites
- Python 3.11
- OpenAI API key

### Installation
```bash
git clone https://github.com/your-username/codebase-qa
cd codebase-qa
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # Mac/Linux
pip install -r requirements.txt
```

### Environment Setup

Create a `.env` file in the root:
```
OPENAI_API_KEY=your_openai_api_key_here
```

### Run the API
```bash
cd backend
uvicorn main:app --reload
```

API is live at `http://localhost:8000`

### Run the Frontend
```bash
cd frontend
npm install
cp .env.example .env.local   # set VITE_API_URL=http://localhost:8000
npm run dev
```

Frontend is live at `http://localhost:5173`

---

## API Endpoints

### `POST /ingest-repo`
Ingest an entire GitHub repository.
```json
{
  "repo_url": "https://github.com/username/repo"
}
```

### `POST /ingest-multiple`
Upload multiple code files at once via multipart form.

### `POST /ingest`
Upload a single code file.

### `POST /ask`
Ask a question about the ingested code.
```json
{
  "question": "How is JWT authentication implemented?",
  "top_k": 5
}
```

Response:
```json
{
  "status": "success",
  "question": "How is JWT authentication implemented?",
  "answer": "JWT authentication is handled via...",
  "sources": [
    {
      "file": "backend/src/auth/jwt.strategy.ts",
      "chunk_index": 0,
      "similarity_score": 0.821
    }
  ]
}
```

### `GET /status`
Check if a repo has been ingested and is ready for questions.

### `DELETE /clear`
Clear all ingested data from ChromaDB.

---

## Key Design Decisions

**LLM-powered file filtering** - Instead of a hardcoded ignore list, filenames are sent to GPT which intelligently filters out config files, generated code, and tooling - works for any language ecosystem.

**Batched embeddings** - All files are chunked first, then embedded in batches of 50. Ingesting a 100+ file repo completes in ~16 seconds.

**Language-aware chunking** - Uses LangChain's language-specific splitters for TypeScript, JavaScript, Python and more - splits at function and class boundaries rather than arbitrary character counts.

**Source citations** - Every answer includes the exact files and chunk indices it was derived from, so you can verify accuracy.

## Live Demo
- **Frontend**: https://codebase-qa-iota.vercel.app/
- **Backend**: https://codebase-qa-m8p5.onrender.com/
import sys
import os

# This lets Python find your backend folder
sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))

from ingestion import ingest_file
from retriever import retrieve_relevant_chunks, is_vectorstore_empty

# Read your actual file
file_name = "wallet.service.ts"
with open(file_name, "r", encoding="utf-8") as f:
    sample_code = f.read()

# ── Test 1 — Retrieval ─────────────────────────────────────────────
print("\n🧪 TEST 1: Re-ingesting for retrieval test")

# Re-ingest first
ingest_result = ingest_file(file_name, sample_code)
print(f"Re-ingested: {ingest_result}")

# Check DB is not empty
print(f"\nIs vectorstore empty: {is_vectorstore_empty()}")

# Ask a real question about your code
question = "How is caching handled in the wallet service?"
print(f"\nQuestion: {question}")

chunks = retrieve_relevant_chunks(question, top_k=3)
print(f"Retrieved {len(chunks)} chunks\n")

for i, chunk in enumerate(chunks):
    print(f"--- Result {i+1} ---")
    print(f"Source     : {chunk['source']}")
    print(f"Similarity : {chunk['similarity_score']}")
    print(f"Preview    : {chunk['text'][:150]}...")
    print()
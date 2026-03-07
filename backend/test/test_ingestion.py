import sys
import os

# This lets Python find your backend folder
sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))

from ingestion import ingest_file, clear_collection, chunk_file

# ── Test 1 — Chunking ──────────────────────────────────────────────
print("\n🧪 TEST 1: Chunking a sample TS file")

# Read your actual file
file_name = "wallet.service.ts"
with open(file_name, "r", encoding="utf-8") as f:
    sample_code = f.read()


chunks = chunk_file(file_name, sample_code)
print(f"✅ Chunks created: {len(chunks)}")
for i, chunk in enumerate(chunks):
    print(f"\n--- Chunk {i+1} ---")
    print(f"Language : {chunk['metadata']['language']}")
    print(f"Source   : {chunk['metadata']['source']}")
    print(f"Text preview: {chunk['text'][:100]}...")


# ── Test 2 — Ingestion into ChromaDB ──────────────────────────────
print("\n🧪 TEST 2: Ingesting into ChromaDB")

result = ingest_file(file_name, sample_code)
print(f"Result: {result}")


# ── Test 3 — Clear collection ──────────────────────────────────────
print("\n🧪 TEST 3: Clearing ChromaDB collection")

clear_result = clear_collection()
print(f"Result: {clear_result}")
import sys
import os
import requests

# Make sure your FastAPI server is running first
# cd backend && uvicorn main:app --reload

BASE_URL = "http://127.0.0.1:8000"

# First clear existing data
print("🗑️  Clearing existing data...")
clear = requests.delete(f"{BASE_URL}/clear")
print(f"Result: {clear.json()}\n")

# Pick 2-3 files from your Ledger Wallet
# Copy them into codebase-qa root first
files_to_test = [
    "wallet.service.ts",
    "wallet.controller.ts",
]

# Check files exist
existing_files = [f for f in files_to_test if os.path.exists(f)]
print(f"📁 Files found: {existing_files}\n")

# Ingest multiple files
print("📥 Ingesting multiple files...")
files = [
    ("files", (f, open(f, "rb"), "text/plain"))
    for f in existing_files
]

response = requests.post(f"{BASE_URL}/ingest-multiple", files=files)
print(f"Result: {response.json()}\n")

# Ask a question that spans both files
print("❓ Asking a question...")
question = requests.post(
    f"{BASE_URL}/ask",
    json={"question": "How does the wallet controller use the wallet service?"}
)
result = question.json()
print(f"✅ Answer:\n{result['answer']}\n")
print(f"📁 Sources: {[s['file'] for s in result['sources']]}")
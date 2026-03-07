import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from ingestion import ingest_file
from qa_chain import answer_question

# # Read the file
# with open("wallet.service.ts", "r", encoding="utf-8") as f:
#     content = f.read()

# # Ingest it first
# print("📥 Ingesting wallet.service.ts...")
# ingest_result = ingest_file("wallet.service.ts", content)
# print(f"Result: {ingest_result}\n")

# Ask questions
test_questions = [
    "How is JWT authentication implemented?",
    "How is wallet balance calculated?",
    "What happens when a transfer is made?",
    "How is Redis used in this project?",
    "How does the SendMoney page work?"
]

for q in test_questions:
    print(f"❓ {q}")
    result = answer_question(q)
    if result["status"] == "success":
        print(f"✅ Answer:\n{result['answer']}")
        print(f"\n📁 Sources: {[s['file'] for s in result['sources']]}")
    else:
        print(f"❌ {result['message']}")
    print("\n" + "="*60 + "\n")
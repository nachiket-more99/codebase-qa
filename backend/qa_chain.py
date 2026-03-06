from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from retriever import retrieve_relevant_chunks, is_vectorstore_empty
from config import OPENAI_API_KEY, LLM_MODEL

def build_prompt(question: str, chunks: list[dict]) -> tuple[SystemMessage, HumanMessage]:
    """
    Takes a question and retrieved chunks.
    Builds a system + human message pair for GPT.
    """

    # Build the context block from retrieved chunks
    context_parts = []
    for i, chunk in enumerate(chunks):
        context_parts.append(
            f"--- Code Chunk {i+1} ---\n"
            f"File: {chunk['source']}\n"
            f"Language: {chunk['language']}\n\n"
            f"{chunk['text']}"
        )

    context = "\n\n".join(context_parts)

    # System message — tells GPT how to behave
    system = SystemMessage(content="""You are an expert code assistant that helps developers understand codebases.

You will be given relevant code chunks from a codebase and a question about that code.

Your job is to:
- Answer the question based ONLY on the provided code chunks
- Be specific and reference actual function names, variables, and logic from the code
- If the answer isn't in the provided chunks, say "I couldn't find relevant code for this in the ingested files"
- Format code references using backticks
- Keep answers clear and concise
""")

    # Human message — the actual question + context
    human = HumanMessage(content=f"""Here are the relevant code chunks:

{context}

Question: {question}
""")

    return system, human

def answer_question(question: str, top_k: int = 5) -> dict:
    """
    Main function — takes a question, returns an answer.
    This is what your FastAPI endpoint will call.
    """

    # Guard — don't try to answer if nothing is ingested
    if is_vectorstore_empty():
        return {
            "status": "error",
            "message": "No code has been ingested yet. Please upload a file first."
        }

    # Step 1 — Retrieve relevant chunks
    chunks = retrieve_relevant_chunks(question, top_k=top_k)

    if not chunks:
        return {
            "status": "error",
            "message": "No relevant code found for this question."
        }

    # Step 2 — Build the prompt
    system_message, human_message = build_prompt(question, chunks)

    # Step 3 — Call GPT
    llm = ChatOpenAI(
        model=LLM_MODEL,
        openai_api_key=OPENAI_API_KEY,
        temperature=0  # 0 = deterministic, no creativity — you want factual answers
    )

    response = llm.invoke([system_message, human_message])

    # Step 4 — Return structured response
    return {
        "status": "success",
        "question": question,
        "answer": response.content,
        "sources": [
            {
                "file": chunk["source"],
                "chunk_index": chunk["chunk_index"],
                "similarity_score": chunk["similarity_score"]
            }
            for chunk in chunks
        ]
    }
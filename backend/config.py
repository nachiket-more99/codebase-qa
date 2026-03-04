from dotenv import load_dotenv
import os

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Embedding model
EMBEDDING_MODEL = "text-embedding-3-small"

# LLM model — GPT-4o-mini is cheap and very capable
LLM_MODEL = "gpt-4o-mini"

# ChromaDB will create this folder automatically
CHROMA_DB_PATH = "./chroma_db"

# Collection name inside ChromaDB
COLLECTION_NAME = "codebase"

# Chunk settings
CHUNK_SIZE = 1000      # characters per chunk
CHUNK_OVERLAP = 150    # overlap between chunks to preserve context
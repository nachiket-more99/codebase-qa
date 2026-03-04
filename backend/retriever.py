import chromadb
from chromadb.config import Settings
from backend.config import settings

client = chromadb.PersistentClient(path=settings.CHROMA_DB_PATH)
collection = client.get_or_create_collection(name="codebase")
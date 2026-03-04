from langchain.text_splitter import RecursiveCharacterTextSplitter

def chunk_text(content: str, filename: str):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
    )
    chunks = splitter.split_text(content)
    return chunks
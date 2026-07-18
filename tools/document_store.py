import chromadb
from pypdf import PdfReader

_client = chromadb.Client()
_collection = _client.get_or_create_collection(name="uploaded_docs")

def _chunk_text(text: str, chunk_size: int = 800, overlap: int = 100) -> list[str]:
    """Splits text into overlapping chunks."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return [c.strip() for c in chunks if c.strip()]

def add_pdf(file_path: str, doc_name: str):
    """Extracts text from a PDF, chunks it, and stores it in the vector DB."""
    reader = PdfReader(file_path)
    full_text = ""
    for page in reader.pages:
        full_text += page.extract_text() + "\n"

    chunks = _chunk_text(full_text)
    ids = [f"{doc_name}_{i}" for i in range(len(chunks))]
    metadatas = [{"source": doc_name} for _ in chunks]

    _collection.add(documents=chunks, ids=ids, metadatas=metadatas)
    return len(chunks)

def search_documents(query: str, n_results: int = 3) -> list[dict]:
    """Searches uploaded documents for relevant chunks."""
    if _collection.count() == 0:
        return []

    results = _collection.query(query_texts=[query], n_results=min(n_results, _collection.count()))

    matches = []
    for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
        matches.append({"text": doc, "source": meta["source"]})
    return matches

def clear_documents():
    """Clears all uploaded documents."""
    global _collection
    _client.delete_collection("uploaded_docs")
    _collection = _client.get_or_create_collection(name="uploaded_docs")

def has_documents() -> bool:
    return _collection.count() > 0


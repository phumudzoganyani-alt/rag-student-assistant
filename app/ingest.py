from pathlib import Path

from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
import chromadb


# Paths
PDF_PATH = Path("data/handbook.pdf")
CHROMA_PATH = "chroma_db"


def load_handbook():
    """Load the handbook and extract text page by page."""
    reader = PdfReader(PDF_PATH)

    documents = []

    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text()

        if text and text.strip():
            documents.append({
                "text": text,
                "page": page_number
            })

    return documents


def split_documents(documents):
    """Split handbook text into smaller chunks."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150
    )

    chunks = []

    for document in documents:
        split_texts = splitter.split_text(document["text"])

        for text in split_texts:
            chunks.append({
                "text": text,
                "page": document["page"]
            })

    return chunks


def store_embeddings(chunks):
    """Generate embeddings and store them in ChromaDB."""

    print("Loading embedding model...")

    model = SentenceTransformer(
        "all-MiniLM-L6-v2"
    )

    print("Connecting to ChromaDB...")

    client = chromadb.PersistentClient(
        path=CHROMA_PATH
    )

    collection = client.get_or_create_collection(
        name="handbook"
    )

    # Remove old data so we don't create duplicates
    existing = collection.get()

    if existing["ids"]:
        collection.delete(ids=existing["ids"])

    texts = [chunk["text"] for chunk in chunks]

    print(f"Generating embeddings for {len(texts)} chunks...")

    embeddings = model.encode(
        texts,
        show_progress_bar=True
    ).tolist()

    ids = [
        f"chunk-{i}"
        for i in range(len(chunks))
    ]

    metadatas = [
        {
            "page": chunk["page"]
        }
        for chunk in chunks
    ]

    collection.add(
        ids=ids,
        documents=texts,
        embeddings=embeddings,
        metadatas=metadatas
    )

    print()
    print("Successfully stored handbook in ChromaDB!")
    print(f"Total chunks: {len(chunks)}")


def main():
    print("Loading handbook...")

    documents = load_handbook()

    print(
        f"Extracted text from {len(documents)} pages."
    )

    chunks = split_documents(documents)

    print(
        f"Created {len(chunks)} text chunks."
    )

    store_embeddings(chunks)


if __name__ == "__main__":
    main()
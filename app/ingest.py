from pathlib import Path

from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
import chromadb

from app.website import get_website_pages


PDF_PATH = Path("data/handbook.pdf")
CHROMA_PATH = "chroma_db"


def load_handbook():
    reader = PdfReader(PDF_PATH)

    documents = []

    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text()

        if text and text.strip():
            documents.append({
                "text": text,
                "source": "Student Handbook",
                "page": page_number,
                "url": None
            })

    return documents


def load_website():
    print("Crawling ZAIO website...")

    pages = get_website_pages()

    documents = []

    for page in pages:
        documents.append({
            "text": page["text"],
            "source": "ZAIO Website",
            "page": None,
            "url": page["url"]
        })

    return documents


def split_documents(documents):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150
    )

    chunks = []

    for document in documents:
        split_texts = splitter.split_text(
            document["text"]
        )

        for text in split_texts:
            chunks.append({
                "text": text,
                "source": document["source"],
                "page": document["page"],
                "url": document["url"]
            })

    return chunks


def store_embeddings(chunks):
    print("Loading embedding model...")

    model = SentenceTransformer(
        "all-MiniLM-L6-v2"
    )

    print("Connecting to ChromaDB...")

    client = chromadb.PersistentClient(
        path=CHROMA_PATH
    )

    collection = client.get_or_create_collection(
        name="knowledge_base"
    )

    # Remove old data so we do not create duplicates
    existing = collection.get()

    if existing["ids"]:
        collection.delete(
            ids=existing["ids"]
        )

    texts = [
        chunk["text"]
        for chunk in chunks
    ]

    print(
        f"Generating embeddings for {len(texts)} chunks..."
    )

    embeddings = model.encode(
        texts,
        show_progress_bar=True
    ).tolist()

    ids = [
        f"chunk-{i}"
        for i in range(len(chunks))
    ]

    metadatas = []

    for chunk in chunks:
        metadatas.append({
            "source": chunk["source"],
            "page": chunk["page"] or 0,
            "url": chunk["url"] or ""
        })

    collection.add(
        ids=ids,
        documents=texts,
        embeddings=embeddings,
        metadatas=metadatas
    )

    print()
    print("Successfully stored knowledge base in ChromaDB!")
    print(f"Total chunks: {len(chunks)}")

    handbook_chunks = sum(
        1 for chunk in chunks
        if chunk["source"] == "Student Handbook"
    )

    website_chunks = sum(
        1 for chunk in chunks
        if chunk["source"] == "ZAIO Website"
    )

    print(f"Handbook chunks: {handbook_chunks}")
    print(f"Website chunks: {website_chunks}")


def main():
    print("Loading Student Handbook...")

    handbook_documents = load_handbook()

    print(
        f"Extracted handbook text from "
        f"{len(handbook_documents)} pages."
    )

    website_documents = load_website()

    print(
        f"Extracted ZAIO content from "
        f"{len(website_documents)} pages."
    )

    all_documents = (
        handbook_documents +
        website_documents
    )

    print(
        f"Total documents: {len(all_documents)}"
    )

    chunks = split_documents(
        all_documents
    )

    print(
        f"Created {len(chunks)} total chunks."
    )

    store_embeddings(chunks)


if __name__ == "__main__":
    main()
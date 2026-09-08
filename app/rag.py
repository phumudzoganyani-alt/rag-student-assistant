import json
import os

import chromadb
from dotenv import load_dotenv
from openai import OpenAI
from sentence_transformers import SentenceTransformer


load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

CHROMA_PATH = "chroma_db"

model = SentenceTransformer("all-MiniLM-L6-v2")

chroma_client = chromadb.PersistentClient(
    path=CHROMA_PATH
)

collection = chroma_client.get_collection(
    name="handbook"
)


def retrieve(question, top_k=5):
    """Retrieve relevant handbook chunks."""

    question_embedding = model.encode(
        question
    ).tolist()

    results = collection.query(
        query_embeddings=[question_embedding],
        n_results=top_k
    )

    retrieved_chunks = []

    for i in range(len(results["documents"][0])):
        retrieved_chunks.append({
            "text": results["documents"][0][i],
            "page": results["metadatas"][0][i]["page"],
            "distance": results["distances"][0][i]
        })

    return retrieved_chunks


def build_context(results):
    """Build context for the AI."""

    context_parts = []

    for result in results:
        context_parts.append(
            f"Page {result['page']}:\n"
            f"{result['text']}"
        )

    return "\n\n".join(context_parts)


def generate_answer(question, results):
    """Generate an answer and identify its source page."""

    context = build_context(results)

    prompt = f"""
You are a student assistant for the Full Stack Development Bootcamp.

Answer the student's question using ONLY the handbook context below.

IMPORTANT RULES:
1. Do not use outside knowledge.
2. Do not make up information.
3. If the answer is not clearly available in the context, return:
   "The information is not available in the handbook."
4. Identify the page that directly contains the information used for the answer.
5. Return ONLY valid JSON.
6. Use this exact format:

{{
  "answer": "your answer here",
  "source_page": 6
}}

If the information is unavailable, use:

{{
  "answer": "The information is not available in the handbook.",
  "source_page": null
}}

HANDBOOK CONTEXT:
{context}

STUDENT QUESTION:
{question}
"""

    response = client.responses.create(
        model="gpt-5.6-luna",
        input=prompt
    )

    try:
        result = json.loads(response.output_text)

        return {
            "answer": result.get(
                "answer",
                "The information is not available in the handbook."
            ),
            "source_page": result.get("source_page")
        }

    except json.JSONDecodeError:
        return {
            "answer": response.output_text,
            "source_page": None
        }
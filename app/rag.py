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

model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

chroma_client = chromadb.PersistentClient(
    path=CHROMA_PATH
)

collection = chroma_client.get_collection(
    name="knowledge_base"
)


FALLBACK_MESSAGE = (
    "I could not find that information "
    "in the available knowledge base."
)


def retrieve(question, top_k=5):
    """Retrieve relevant chunks from all knowledge sources."""

    question_embedding = model.encode(
        question
    ).tolist()

    results = collection.query(
        query_embeddings=[question_embedding],
        n_results=top_k
    )

    retrieved_chunks = []

    for i in range(
        len(results["documents"][0])
    ):
        metadata = results["metadatas"][0][i]

        retrieved_chunks.append({
            "text": results["documents"][0][i],
            "source": metadata.get("source"),
            "page": metadata.get("page"),
            "url": metadata.get("url"),
            "distance": results["distances"][0][i]
        })

    return retrieved_chunks


def build_context(results):
    """Build context containing source information."""

    context_parts = []

    for index, result in enumerate(results, start=1):

        if result["source"] == "Student Handbook":

            source_info = (
                f"Source: Student Handbook\n"
                f"Page: {result['page']}"
            )

        else:

            source_info = (
                f"Source: ZAIO Website\n"
                f"URL: {result['url']}"
            )

        context_parts.append(
            f"CONTEXT {index}\n"
            f"{source_info}\n"
            f"Content:\n"
            f"{result['text']}"
        )

    return "\n\n".join(context_parts)


def generate_answer(question, results):
    """Generate an answer using the retrieved knowledge."""

    if not results:
        return {
            "answer": FALLBACK_MESSAGE,
            "source": None
        }

    context = build_context(results)

    prompt = f"""
You are a student assistant for the ZAIO Full Stack Development Bootcamp.

You have access to two knowledge sources:

1. Student Handbook
2. ZAIO Website

Answer the student's question using ONLY the information
contained in the retrieved context below.

IMPORTANT RULES:

1. Do not use outside knowledge.

2. Do not make up information.

3. If the answer cannot be found clearly in the
retrieved context, return exactly:

"{FALLBACK_MESSAGE}"

4. Choose the most appropriate source that directly
supports your answer.

5. If the answer comes from the Student Handbook,
return its page number.

6. If the answer comes from the ZAIO Website,
return its URL.

7. Return ONLY valid JSON.

If the answer comes from the Student Handbook, use:

{{
    "answer": "your answer here",
    "source_type": "Student Handbook",
    "source_page": 6,
    "source_url": null
}}

If the answer comes from the ZAIO Website, use:

{{
    "answer": "your answer here",
    "source_type": "ZAIO Website",
    "source_page": null,
    "source_url": "https://www.zaio.io/..."
}}

If the information is unavailable, use:

{{
    "answer": "{FALLBACK_MESSAGE}",
    "source_type": null,
    "source_page": null,
    "source_url": null
}}

RETRIEVED CONTEXT:

{context}

STUDENT QUESTION:

{question}
"""

    response = client.responses.create(
        model="gpt-5.6-luna",
        input=prompt
    )

    try:
        result = json.loads(
            response.output_text
        )

        answer = result.get(
            "answer",
            FALLBACK_MESSAGE
        )

        source_type = result.get(
            "source_type"
        )

        source_page = result.get(
            "source_page"
        )

        source_url = result.get(
            "source_url"
        )

        if answer == FALLBACK_MESSAGE:
            return {
                "answer": FALLBACK_MESSAGE,
                "source": None
            }

        if source_type == "Student Handbook":
            if source_page is not None:
                return {
                    "answer": answer,
                    "source": (
                        f"Student Handbook - "
                        f"Page {source_page}"
                    )
                }

        if source_type == "ZAIO Website":
            if source_url:
                return {
                    "answer": answer,
                    "source": source_url
                }

        # Safety fallback if the model gives an
        # answer but an invalid source.
        return {
            "answer": FALLBACK_MESSAGE,
            "source": None
        }

    except json.JSONDecodeError:

        return {
            "answer": FALLBACK_MESSAGE,
            "source": None
        }
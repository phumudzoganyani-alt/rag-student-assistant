from fastapi import FastAPI
from pydantic import BaseModel

from app.rag import retrieve, generate_answer


app = FastAPI(
    title="Student Handbook RAG Assistant",
    description="AI assistant that answers questions using the student handbook.",
    version="1.0.0"
)


class QuestionRequest(BaseModel):
    question: str


@app.get("/")
def home():
    return {
        "message": "Student Handbook RAG Assistant is running"
    }


@app.post("/ask")
def ask_question(request: QuestionRequest):

    question = request.question.strip()

    if not question:
        return {
            "answer": "Please provide a question.",
            "source": None
        }

    results = retrieve(question)

    if not results:
        return {
            "answer": "The information is not available in the handbook.",
            "source": None
        }

    result = generate_answer(
        question,
        results
    )

    source_page = result["source_page"]

    source = None

    if source_page is not None:
        source = f"Page {source_page}"

    return {
        "answer": result["answer"],
        "source": source
    }
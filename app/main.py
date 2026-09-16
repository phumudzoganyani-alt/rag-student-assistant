from fastapi import FastAPI
from pydantic import BaseModel

from app.rag import retrieve, generate_answer


app = FastAPI(
    title="ZAIO Student RAG Assistant",
    description="AI assistant that answers questions using the ZAIO Student Handbook and Website.",
    version="2.0.0"
)


class QuestionRequest(BaseModel):
    question: str


@app.get("/")
def home():
    return {
        "message": "ZAIO Student RAG Assistant is running"
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

    result = generate_answer(
        question,
        results
    )

    return {
        "answer": result["answer"],
        "source": result["source"]
    }
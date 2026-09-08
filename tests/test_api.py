from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_home():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["message"] == (
        "Student Handbook RAG Assistant is running"
    )


def test_empty_question():
    response = client.post(
        "/ask",
        json={"question": ""}
    )

    assert response.status_code == 200

    data = response.json()

    assert data["answer"] == "Please provide a question."
    assert data["source"] is None


def test_valid_question():
    response = client.post(
        "/ask",
        json={
            "question": "What is the duration of the bootcamp?"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert "answer" in data
    assert "source" in data

    assert "6 months" in data["answer"].lower()
    assert data["source"] == "Page 6"


def test_unknown_question():
    response = client.post(
        "/ask",
        json={
            "question": "What is the university's refund policy?"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["answer"] == (
        "The information is not available in the handbook."
    )

    assert data["source"] is None
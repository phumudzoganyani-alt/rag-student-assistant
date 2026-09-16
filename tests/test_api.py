from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_home():
    response = client.get("/")

    assert response.status_code == 200

    assert response.json()["message"] == (
        "ZAIO Student RAG Assistant is running"
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


def test_handbook_question():
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
    assert data["source"] == "Student Handbook - Page 6"


def test_website_question():
    response = client.post(
        "/ask",
        json={
            "question": "What bootcamps does ZAIO offer?"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert "answer" in data
    assert "source" in data

    assert "bootcamp" in data["answer"].lower()
    assert data["source"] == "https://www.zaio.io/bootcamps"


def test_unknown_question():
    response = client.post(
        "/ask",
        json={
            "question": "What is ZAIO's refund policy for university tuition?"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["answer"] == (
        "I could not find that information in the available knowledge base."
    )

    assert data["source"] is None
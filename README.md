# Student Handbook RAG Assistant

An AI-powered assistant that answers student questions using information from the Full Stack Development Bootcamp handbook.

The system uses **Retrieval-Augmented Generation (RAG)** to retrieve relevant information from the handbook before generating an answer.

## Features

* 📖 Reads the student handbook PDF
* ✂️ Splits handbook content into smaller text chunks
* 🧠 Generates vector embeddings using Sentence Transformers
* 🗄️ Stores embeddings in ChromaDB
* 🔎 Retrieves relevant handbook sections for each question
* 🤖 Uses an OpenAI model to generate answers
* 📄 Returns the source page for the answer
* 🚫 Avoids making up information when the answer is not in the handbook
* 🌐 Provides a FastAPI REST API
* 🧪 Includes automated API tests
* 🔗 Ready to be connected to n8n

---

## Project Structure

```text
rag-student-assistant/
│
├── data/
│   └── handbook.pdf
│
├── app/
│   ├── __init__.py
│   ├── ingest.py
│   ├── rag.py
│   └── main.py
│
├── tests/
│   └── test_api.py
│
├── chroma_db/
│
├── .env
├── .gitignore
├── pytest.ini
├── requirements.txt
└── README.md
```

---

## Technologies Used

* **Python**
* **FastAPI** - REST API
* **Sentence Transformers** - text embeddings
* **ChromaDB** - vector database
* **LangChain Text Splitters** - document chunking
* **PyPDF** - PDF text extraction
* **OpenAI API** - answer generation
* **Pytest** - automated testing

---

# How the RAG System Works

The system follows this process:

```text
Student Question
       ↓
Generate Question Embedding
       ↓
Search ChromaDB
       ↓
Retrieve Relevant Handbook Chunks
       ↓
Build Context
       ↓
Send Context + Question to OpenAI
       ↓
Generate Answer
       ↓
Return Answer + Source Page
```

---

# 1. Install the Project

Clone the repository:

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
```

Move into the project:

```bash
cd rag-student-assistant
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate it on Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

---

# 2. Install Dependencies

Install the required packages:

```bash
pip install -r requirements.txt
```

---

# 3. Configure the OpenAI API Key

Create a `.env` file in the project root:

```text
OPENAI_API_KEY=your_api_key_here
```

Do not commit the `.env` file to GitHub.

The `.gitignore` file excludes it from Git.

---

# 4. Add the Handbook

Place the student handbook PDF inside:

```text
data/handbook.pdf
```

The application uses this file as its knowledge source.

---

# 5. Build the Vector Database

Run:

```bash
python app/ingest.py
```

The ingestion process:

1. Loads the handbook PDF.
2. Extracts text from each page.
3. Splits the text into smaller chunks.
4. Generates embeddings for each chunk.
5. Stores the embeddings and page metadata in ChromaDB.

Example result:

```text
Loading handbook...
Extracted text from 14 pages.
Created 19 text chunks.
Loading embedding model...
Connecting to ChromaDB...
Generating embeddings for 19 chunks...

Successfully stored handbook in ChromaDB!
Total chunks: 19
```

The generated vector database is stored in:

```text
chroma_db/
```

---

# 6. Start the API

Run:

```bash
uvicorn app.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

FastAPI documentation is available at:

```text
http://127.0.0.1:8000/docs
```

---

# 7. Ask a Question

Send a POST request to:

```text
/ask
```

### Request

```json
{
  "question": "What is the duration of the bootcamp?"
}
```

### Response

```json
{
  "answer": "The bootcamp takes 6 months to complete.",
  "source": "Page 6"
}
```

---

# 8. Example Questions

### Question 1

```text
What is the duration of the bootcamp?
```

Example answer:

```text
The bootcamp takes 6 months to complete.
```

Source:

```text
Page 6
```

### Question 2

```text
What communication platform is used after orientation day?
```

Example answer:

```text
Discord is used for communication after Orientation Day.
```

Source:

```text
Page 8
```

### Question 3

```text
What can students expect to achieve by the end of the bootcamp?
```

The assistant retrieves the relevant section and provides an answer with the source page.

### Question 4

```text
What happens if students do not complete their daily tasks on time?
```

The assistant explains the late-task indicators and provides the relevant source page.

### Question 5

```text
What is the university's refund policy?
```

Because this information is not available in the handbook, the assistant responds:

```json
{
  "answer": "The information is not available in the handbook.",
  "source": null
}
```

---

# 9. API Validation

The API accepts JSON requests using the following format:

```json
{
  "question": "Your question here"
}
```

If an empty question is submitted:

```json
{
  "question": ""
}
```

The API responds:

```json
{
  "answer": "Please provide a question.",
  "source": null
}
```

This allows the API to handle invalid or empty questions gracefully.

---

# 10. Running Tests

Run the automated tests with:

```bash
python -m pytest -v
```

Current test results:

```text
4 passed
```

The tests cover:

* Home endpoint
* Empty question handling
* Valid handbook question
* Unknown question handling

---

# 11. n8n Integration

The API is designed to be used as an HTTP endpoint in an n8n workflow.

### n8n HTTP Request

Method:

```text
POST
```

Endpoint:

```text
http://127.0.0.1:8000/ask
```

Headers:

```text
Content-Type: application/json
```

Body:

```json
{
  "question": "What is the duration of the bootcamp?"
}
```

The response can then be used by later n8n nodes.

Example response:

```json
{
  "answer": "The bootcamp takes 6 months to complete.",
  "source": "Page 6"
}
```

---

# RAG Components

## Document Loading

`PyPDF` extracts text from the handbook PDF page by page.

## Text Splitting

`RecursiveCharacterTextSplitter` divides the extracted text into manageable chunks.

The current configuration is:

```text
Chunk size: 800 characters
Chunk overlap: 150 characters
```

## Embeddings

The system uses:

```text
all-MiniLM-L6-v2
```

from Sentence Transformers to convert text into numerical vectors.

## Vector Database

ChromaDB stores:

* Text chunks
* Embeddings
* Page metadata

## Retrieval

When a student asks a question, the question is converted into an embedding and compared against the handbook embeddings.

The most relevant chunks are retrieved and provided to the language model as context.

## Generation

The OpenAI API generates the final answer using the retrieved handbook context.

The model is instructed to use only the provided handbook information and to respond that the information is unavailable when the handbook does not contain the answer.

---

# Security

The OpenAI API key is stored in an environment variable:

```text
OPENAI_API_KEY
```

The `.env` file is excluded from Git using `.gitignore`.

Never upload your API key to GitHub or share it publicly.

---

# Assignment Requirements

| Requirement                              | Status |
| ---------------------------------------- | ------ |
| Load handbook PDF                        | ✅      |
| Extract text                             | ✅      |
| Split text into chunks                   | ✅      |
| Generate embeddings                      | ✅      |
| Store embeddings in vector database      | ✅      |
| Retrieve relevant chunks                 | ✅      |
| Generate answers using retrieved context | ✅      |
| Return source page                       | ✅      |
| POST `/ask` endpoint                     | ✅      |
| JSON request/response                    | ✅      |
| Handle invalid questions                 | ✅      |
| Automated tests                          | ✅      |
| n8n-ready API                            | ✅      |
| GitHub-ready project                     | ✅      |

---

# Author

Student Handbook RAG Assistant

Built as part of the Full Stack Development Bootcamp assignment.

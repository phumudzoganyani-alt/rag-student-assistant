Student RAG Assistant

An AI-powered student assistant that uses Retrieval-Augmented Generation (RAG) to answer questions using two knowledge sources:

📖 ZAIO Full Stack Development Bootcamp Student Handbook
🌐 ZAIO Website

The system retrieves relevant information from the knowledge base before generating an answer. Every response includes the most appropriate source.

Features
📖 Reads the ZAIO Student Handbook PDF
🌐 Crawls selected ZAIO website pages
✂️ Splits documents into smaller text chunks
🧠 Generates embeddings using Sentence Transformers
🗄️ Stores embeddings in ChromaDB
🔎 Searches across both knowledge sources
📄 Stores Student Handbook page metadata
🔗 Stores website URL metadata
🤖 Generates answers using the OpenAI API
🚫 Uses a fixed fallback when information cannot be found
🌐 Provides a FastAPI REST API
🧪 Includes automated API tests
🔗 Integrates with n8n

Configuration

Create a .env file in the project root:

OPENAI_API_KEY=your_api_key_here

Do not commit the .env file to GitHub.

The .gitignore file excludes the environment file.

Building the Knowledge Base

Run the ingestion process using:

python -m app.ingest

The ingestion process:

Loads the Student Handbook PDF.
Extracts text from each page.
Crawls the ZAIO website.
Cleans website content.
Splits both sources into chunks.
Generates embeddings.
Stores the embeddings in ChromaDB.
Stores source metadata.

Example final result:

Extracted handbook text from 14 pages.
Extracted ZAIO content from 3 pages.
Total documents: 17
Created 50 total chunks.

Handbook chunks: 19
Website chunks: 31
Metadata

Each knowledge-base chunk contains source information.

Student Handbook
Source: Student Handbook
Page: <page number>
ZAIO Website
Source: ZAIO Website
URL: <website URL>

This allows the API to return the most appropriate source for an answer.

Starting the API

Start FastAPI with:

python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

The API runs at:

http://127.0.0.1:8000

FastAPI documentation:

http://127.0.0.1:8000/docs
API Endpoint
POST /ask

The API accepts a question in JSON format.

Request
{
"question": "What is the duration of the bootcamp?"
}
Example Handbook Response
{
"answer": "The bootcamp lasts 6 months.",
"source": "Student Handbook - Page 6"
}
Example Website Response
{
"answer": "ZAIO offers several bootcamp programmes...",
"source": "https://www.zaio.io/bootcamps"
}
Example Questions

1. Student Handbook Question
   What is the duration of the bootcamp?

Example result:

The bootcamp lasts 6 months.

Source:

Student Handbook - Page 6 2. ZAIO Website Question
What bootcamps does ZAIO offer?

The system retrieves information from the ZAIO website and returns the website URL as the source.

Example source:

https://www.zaio.io/bootcamps 3. Unknown Question

If the information cannot be found in either knowledge source, the system returns exactly:

I could not find that information in the available knowledge base.

The source is returned as:

null
API Validation

The API also handles empty questions.

Request:

{
"question": ""
}

Response:

{
"answer": "Please provide a question.",
"source": null
}
Testing

Run the automated tests with:

python -m pytest -v
Test Results

The final test suite contains 5 tests.

5 passed, 2 warnings

The tests cover:

Home endpoint
Empty question handling
Student Handbook question
ZAIO Website question
Unknown question and fallback response

All 5 tests passed successfully.

The warnings are non-failing dependency/telemetry warnings.

n8n Integration

The RAG API is integrated with n8n.

The workflow is:

Webhook
↓
HTTP Request
↓
FastAPI /ask
↓
RAG Assistant
↓
Respond to Webhook
↓
User receives the answer
Webhook

The n8n webhook receives:

{
"question": "What bootcamps does ZAIO offer?"
}
HTTP Request

The HTTP Request node sends the question to:

http://host.docker.internal:8000/ask

Method:

POST

Content type:

application/json
Response

The Respond to Webhook node presents the RAG response to the user.

This satisfies the automation requirement of forwarding/presenting the RAG result to the user.

RAG Components
Document Loading

PyPDF extracts text from the Student Handbook page by page.

Website Crawling

Playwright loads the ZAIO website pages.

BeautifulSoup is used to clean the HTML and remove navigation, headers, footers, scripts and styles.

Text Splitting

RecursiveCharacterTextSplitter is used to divide documents into smaller chunks.

Current configuration:

Chunk size: 800 characters
Chunk overlap: 150 characters
Embeddings

The system uses:

all-MiniLM-L6-v2

from Sentence Transformers.

Vector Database

ChromaDB stores:

Text chunks
Embeddings
Source metadata
Student Handbook page numbers
Website URLs
Retrieval

When a student asks a question:

The question is converted into an embedding.
ChromaDB searches the knowledge base.
Relevant chunks are retrieved.
The retrieved chunks are provided as context to the language model.
Generation

The OpenAI API generates the final answer using only the retrieved context.

Security

The OpenAI API key is stored in an environment variable:

OPENAI_API_KEY

The .env file is excluded from Git.

The following project-generated resources are also excluded from Git:

.env
venv/
chroma_db/
Author

Phumudzo Ganyani

Student RAG Assistant project built as part of the ZAIO Full Stack Development Bootcamp assignment.


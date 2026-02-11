```bash
cat > README.md << 'ENDOFFILE'
# 📄 DocSearch - AI-Powered Document Search Engine

DocSearch is an intelligent document search engine that leverages artificial intelligence to enable users to upload documents and perform semantic searches using natural language queries. Unlike traditional keyword-based search, DocSearch understands the **meaning** and **context** behind your queries, delivering highly relevant results even when exact keywords don't match.

---

## 🎯 Problem Statement

Organizations and individuals deal with large volumes of documents daily. Finding specific information across multiple documents is time-consuming and inefficient. Traditional search methods rely on exact keyword matching, which often fails to find relevant content when different words are used to express the same concept.

**DocSearch solves this by:**
- Understanding the semantic meaning of your queries
- Searching across multiple document formats simultaneously
- Returning the most contextually relevant passages
- Providing AI-generated answers based on document content

---

## 🚀 Features

### Core Features
- **Multi-Format Document Upload** - Support for PDF, DOCX, and TXT files
- **AI-Powered Semantic Search** - Search using natural language instead of exact keywords
- **Context-Aware Results** - Returns relevant passages with source document references
- **AI-Generated Answers** - Uses Groq LLM to generate human-readable answers from document content

### Technical Features
- **Vector Embeddings** - Converts document text into high-dimensional vectors using Sentence Transformers
- **Efficient Storage** - ChromaDB vector database for fast similarity search
- **Document Chunking** - Intelligently splits documents into searchable chunks
- **RESTful API** - Clean, well-documented API endpoints
- **Interactive API Documentation** - Auto-generated Swagger UI for testing endpoints
- **Responsive Frontend** - Modern, mobile-friendly user interface

---

## 🛠️ Tech Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Backend Framework** | FastAPI | High-performance async web framework |
| **AI Embeddings** | Sentence Transformers | Convert text to semantic vectors |
| **Vector Database** | ChromaDB | Store and query document embeddings |
| **LLM Integration** | Groq API | Generate natural language answers |
| **PDF Parsing** | PyPDF2 | Extract text from PDF documents |
| **DOCX Parsing** | python-docx | Extract text from Word documents |
| **Frontend** | HTML, CSS, JavaScript | User interface |
| **Server** | Uvicorn | ASGI server for FastAPI |
| **Language** | Python 3.10+ | Backend programming language |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│                    Frontend (UI)                     │
│              HTML / CSS / JavaScript                 │
└─────────────────┬───────────────────┬───────────────┘
                  │                   │
           Upload Request       Search Query
                  │                   │
┌─────────────────▼───────────────────▼───────────────┐
│                 FastAPI Backend                       │
│                                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────┐ │
│  │   Document   │  │   Search     │  │   Answer   │ │
│  │   Processor  │  │   Engine     │  │  Generator │ │
│  └──────┬───────┘  └──────┬───────┘  └─────┬──────┘ │
└─────────┼─────────────────┼────────────────┼────────┘
          │                 │                │
┌─────────▼─────────┐ ┌────▼─────┐  ┌───────▼───────┐
│ Sentence           │ │ ChromaDB │  │   Groq API    │
│ Transformers       │ │ (Vector  │  │   (LLM)       │
│ (Embeddings)       │ │   DB)    │  │               │
└───────────────────┘ └──────────┘  └───────────────┘
```

### How It Works

1. **Document Upload**: User uploads a PDF, DOCX, or TXT file
2. **Text Extraction**: The system extracts raw text from the document
3. **Chunking**: Text is split into smaller, overlapping chunks for better search granularity
4. **Embedding Generation**: Each chunk is converted into a vector embedding using Sentence Transformers
5. **Storage**: Embeddings are stored in ChromaDB along with the original text and metadata
6. **Search Query**: User enters a natural language question
7. **Query Embedding**: The question is converted into a vector embedding
8. **Similarity Search**: ChromaDB finds the most similar document chunks using cosine similarity
9. **Answer Generation**: Retrieved chunks are sent to Groq LLM to generate a coherent answer
10. **Response**: The answer along with source references is returned to the user

---

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.10 or higher** - [Download Python](https://www.python.org/downloads/)
- **pip** - Python package manager (comes with Python)
- **Git** - [Download Git](https://git-scm.com/downloads/)
- **Groq API Key** - [Get free API key](https://console.groq.com/keys)

---

## ⚙️ Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/Shreeshail-sp/docsearch.git
cd docsearch
```

### Step 2: Create a Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate it
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

> **Note**: The first run will download the Sentence Transformer model (~90MB). This is a one-time download.

### Step 4: Set Up Environment Variables

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit the `.env` file and add your API key:

```env
GROQ_API_KEY=your_groq_api_key_here
```

#### How to Get a Groq API Key:
1. Go to [https://console.groq.com](https://console.groq.com)
2. Sign up for a free account
3. Navigate to **API Keys** section
4. Click **Create API Key**
5. Copy and paste it into your `.env` file

---

## 🏃 Running the Application

### Start the Server

```bash
uvicorn main:app --reload
```

### Access the Application

| URL | Description |
|-----|-------------|
| [http://localhost:8000](http://localhost:8000) | Main Application |
| [http://localhost:8000/docs](http://localhost:8000/docs) | Swagger API Documentation |
| [http://localhost:8000/redoc](http://localhost:8000/redoc) | ReDoc API Documentation |

### Using the Application

1. **Open** your browser and go to `http://localhost:8000`
2. **Upload** one or more documents (PDF, DOCX, or TXT)
3. **Wait** for the documents to be processed (you'll see a success message)
4. **Type** your question in the search bar
5. **Get** AI-powered answers with source references

---

## 📁 Project Structure

```
docsearch/
│
├── main.py                     # FastAPI application entry point & API routes
├── requirements.txt            # Python package dependencies
├── .env                        # Environment variables (not tracked by git)
├── .env.example                # Example environment variables template
├── .gitignore                  # Git ignore rules
├── README.md                   # Project documentation (this file)
│
├── static/                     # Frontend files
│   ├── index.html              # Main HTML page
│   ├── style.css               # CSS styles
│   └── script.js               # Frontend JavaScript logic
│
├── uploads/                    # Uploaded documents storage (auto-created)
│
└── chroma_db/                  # ChromaDB vector database (auto-created)
```

---

## 🔌 API Endpoints

### Upload Document

```http
POST /upload
Content-Type: multipart/form-data
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `file` | `File` | Document file (PDF, DOCX, or TXT) |

**Response:**
```json
{
    "message": "Document uploaded and processed successfully",
    "filename": "document.pdf",
    "chunks": 15
}
```

### Search Documents

```http
POST /search
Content-Type: application/json
```

**Request Body:**
```json
{
    "query": "What is the company's revenue policy?"
}
```

**Response:**
```json
{
    "answer": "Based on the documents, the company's revenue policy...",
    "sources": [
        {
            "document": "policy.pdf",
            "chunk": "Revenue recognition follows...",
            "relevance_score": 0.92
        }
    ]
}
```

### List Documents

```http
GET /documents
```

**Response:**
```json
{
    "documents": [
        {
            "id": "1",
            "filename": "policy.pdf",
            "upload_date": "2024-01-15T10:30:00",
            "chunks": 15
        }
    ]
}
```

### Delete Document

```http
DELETE /documents/{document_id}
```

**Response:**
```json
{
    "message": "Document deleted successfully"
}
```

---

## 🧪 Example Usage

### Using the Web Interface

1. Navigate to `http://localhost:8000`
2. Click the upload button and select a document
3. Once processed, type a question like:
   - *"What are the main findings in the report?"*
   - *"Summarize the key points about budget allocation"*
   - *"What does the document say about employee benefits?"*

### Using cURL

```bash
# Upload a document
curl -X POST "http://localhost:8000/upload" \
  -F "file=@/path/to/your/document.pdf"

# Search
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the main topic?"}'

# List all documents
curl -X GET "http://localhost:8000/documents"

# Delete a document
curl -X DELETE "http://localhost:8000/documents/1"
```

### Using Python Requests

```python
import requests

# Upload a document
with open("document.pdf", "rb") as f:
    response = requests.post(
        "http://localhost:8000/upload",
        files={"file": f}
    )
print(response.json())

# Search
response = requests.post(
    "http://localhost:8000/search",
    json={"query": "What is the main topic?"}
)
print(response.json())
```

---

## ⚡ Performance

| Metric | Value |
|--------|-------|
| Document Processing | ~2-5 seconds per page |
| Search Query | ~0.5-2 seconds |
| Embedding Model | all-MiniLM-L6-v2 (fast & accurate) |
| Max File Size | 10 MB per document |
| Supported Formats | PDF, DOCX, TXT |

---

## 🔧 Configuration

You can customize the application by modifying these settings:

| Setting | Default | Description |
|---------|---------|-------------|
| `CHUNK_SIZE` | 500 | Number of characters per text chunk |
| `CHUNK_OVERLAP` | 50 | Overlap between consecutive chunks |
| `TOP_K_RESULTS` | 5 | Number of search results to return |
| `EMBEDDING_MODEL` | all-MiniLM-L6-v2 | Sentence transformer model |
| `MAX_FILE_SIZE` | 10 MB | Maximum upload file size |

---

## 🐛 Troubleshooting

### Common Issues

**1. "Module not found" error**
```bash
# Make sure virtual environment is activated
source venv/bin/activate
pip install -r requirements.txt
```

**2. "GROQ_API_KEY not set" error**
```bash
# Check if .env file exists
cat .env
# Make sure it contains: GROQ_API_KEY=your_key_here
```

**3. "Port already in use" error**
```bash
# Use a different port
uvicorn main:app --reload --port 8001
```

**4. Slow first startup**
- The first run downloads the embedding model (~90MB)
- Subsequent startups will be much faster

**5. Large PDF processing fails**
- Ensure the PDF is not password-protected
- Try with a smaller document first
- Check if the PDF contains extractable text (not scanned images)

---

## 🗺️ Roadmap

- [ ] Support for more file formats (XLSX, PPTX, CSV)
- [ ] Multi-language document support
- [ ] User authentication and document access control
- [ ] Batch document upload
- [ ] Document summarization feature
- [ ] Chat-based interface with conversation history
- [ ] Docker containerization
- [ ] Cloud deployment (AWS/GCP)
- [ ] OCR support for scanned documents

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

### Getting Started

1. **Fork** the repository
2. **Clone** your fork
   ```bash
   git clone https://github.com/your-username/docsearch.git
   ```
3. **Create** a feature branch
   ```bash
   git checkout -b feature/amazing-feature
   ```
4. **Make** your changes
5. **Test** your changes thoroughly
6. **Commit** your changes
   ```bash
   git commit -m "Add amazing feature"
   ```
7. **Push** to your branch
   ```bash
   git push origin feature/amazing-feature
   ```
8. **Open** a Pull Request

### Guidelines

- Follow PEP 8 coding standards
- Add comments for complex logic
- Update documentation for new features
- Write meaningful commit messages

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2024 Shreeshail SP

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 👤 Author

**Shreeshail SP**

- GitHub: [@Shreeshail-sp](https://github.com/Shreeshail-sp)

---

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [Sentence Transformers](https://www.sbert.net/) - State-of-the-art text embeddings
- [ChromaDB](https://www.trychroma.com/) - AI-native vector database
- [Groq](https://groq.com/) - Ultra-fast LLM inference
- [Uvicorn](https://www.uvicorn.org/) - Lightning-fast ASGI server

---

⭐ **If you found this project useful, please give it a star!**
ENDOFFILE

git add README.md
git commit -m "Add detailed README documentation"
git push
```

Copy and paste this entire block into your terminal. It will create the detailed README, commit, and push it to GitHub.

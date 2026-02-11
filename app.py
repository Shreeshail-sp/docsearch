from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import shutil
from search_service import SearchService
from config import config

app = FastAPI(title="Document Search with Endee")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

search_service = SearchService()


class SearchRequest(BaseModel):
    query: str
    top_k: Optional[int] = 5


@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>DocSearch - Endee</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: 'Inter', sans-serif;
                background: #0a0e1a;
                color: #e2e8f0;
                min-height: 100vh;
            }

            .header {
                text-align: center;
                padding: 40px 20px 20px;
                background: linear-gradient(135deg, #0a0e1a 0%, #1a1f3a 100%);
                border-bottom: 1px solid #1e293b;
            }
            .header h1 {
                font-size: 2.8em;
                font-weight: 700;
                background: linear-gradient(135deg, #38bdf8, #818cf8);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                margin-bottom: 8px;
            }
            .header p { color: #64748b; font-size: 1.1em; }
            .badge {
                display: inline-block;
                background: #1e293b;
                color: #38bdf8;
                padding: 4px 12px;
                border-radius: 20px;
                font-size: 0.8em;
                margin-top: 10px;
                border: 1px solid #334155;
            }

            .container { max-width: 950px; margin: auto; padding: 30px 20px; }

            .card {
                background: #111827;
                border-radius: 16px;
                padding: 28px;
                margin-bottom: 24px;
                border: 1px solid #1e293b;
            }
            .card h2 {
                font-size: 1.2em;
                font-weight: 600;
                margin-bottom: 18px;
                display: flex;
                align-items: center;
                gap: 10px;
            }

            /* Upload */
            .upload-area {
                border: 2px dashed #2d3748;
                border-radius: 12px;
                padding: 40px;
                text-align: center;
                cursor: pointer;
                transition: all 0.3s;
                background: #0a0e1a;
            }
            .upload-area:hover { border-color: #38bdf8; background: #0d1321; }
            .upload-area .upload-icon { font-size: 3em; margin-bottom: 10px; }
            .upload-area p { color: #64748b; margin: 5px 0; }
            .upload-area .formats { font-size: 0.85em; color: #475569; }
            input[type="file"] { display: none; }

            .upload-btn {
                background: linear-gradient(135deg, #38bdf8, #818cf8);
                color: white;
                padding: 12px 30px;
                border: none;
                border-radius: 10px;
                font-size: 1em;
                font-weight: 600;
                cursor: pointer;
                margin-top: 15px;
                display: none;
            }
            .upload-btn.visible { display: inline-block; }

            .file-name {
                color: #38bdf8;
                font-weight: 500;
                margin-top: 10px;
                display: none;
            }
            .file-name.visible { display: block; }

            /* Search */
            .search-box { display: flex; gap: 10px; }
            .search-box input {
                flex: 1;
                padding: 14px 20px;
                background: #0a0e1a;
                border: 1px solid #2d3748;
                border-radius: 12px;
                color: #e2e8f0;
                font-size: 1em;
                font-family: 'Inter', sans-serif;
                outline: none;
            }
            .search-box input:focus { border-color: #38bdf8; }
            .search-box input::placeholder { color: #475569; }
            .search-box button {
                background: linear-gradient(135deg, #38bdf8, #818cf8);
                color: white;
                padding: 14px 28px;
                border: none;
                border-radius: 12px;
                font-size: 1em;
                font-weight: 600;
                cursor: pointer;
                font-family: 'Inter', sans-serif;
            }
            .search-box button:disabled { opacity: 0.5; cursor: not-allowed; }

            /* Status */
            .status {
                padding: 14px 18px;
                border-radius: 10px;
                margin-top: 16px;
                font-size: 0.95em;
                display: flex;
                align-items: center;
                gap: 10px;
            }
            .status.success { background: #052e16; border: 1px solid #166534; color: #86efac; }
            .status.error { background: #450a0a; border: 1px solid #991b1b; color: #fca5a5; }
            .status.loading { background: #0c1a33; border: 1px solid #1e40af; color: #93c5fd; }

            /* Answer Box */
            .answer-box {
                margin-top: 20px;
            }
            .answer-label {
                color: #38bdf8;
                font-weight: 600;
                font-size: 0.9em;
                text-transform: uppercase;
                letter-spacing: 1px;
                margin-bottom: 12px;
            }
            .answer-content {
                background: #0f1729;
                border: 1px solid #1e3a5f;
                border-left: 4px solid #38bdf8;
                border-radius: 12px;
                padding: 24px;
                line-height: 1.8;
                font-size: 1.05em;
                color: #e2e8f0;
            }
            .answer-query {
                color: #94a3b8;
                font-size: 0.9em;
                margin-bottom: 15px;
                font-style: italic;
            }

            /* Confidence */
            .confidence-bar {
                margin-top: 16px;
                display: flex;
                align-items: center;
                gap: 12px;
            }
            .confidence-label {
                color: #64748b;
                font-size: 0.85em;
                white-space: nowrap;
            }
            .confidence-track {
                flex: 1;
                height: 6px;
                background: #1e293b;
                border-radius: 3px;
                overflow: hidden;
            }
            .confidence-fill {
                height: 100%;
                border-radius: 3px;
                transition: width 0.5s ease;
            }
            .confidence-fill.high { background: linear-gradient(90deg, #22c55e, #4ade80); }
            .confidence-fill.medium { background: linear-gradient(90deg, #eab308, #facc15); }
            .confidence-fill.low { background: linear-gradient(90deg, #ef4444, #f87171); }
            .confidence-value {
                color: #94a3b8;
                font-size: 0.85em;
                font-weight: 600;
                min-width: 45px;
            }

            /* Sources */
            .sources {
                margin-top: 16px;
                display: flex;
                gap: 8px;
                flex-wrap: wrap;
            }
            .source-tag {
                background: #1e293b;
                border: 1px solid #334155;
                padding: 6px 14px;
                border-radius: 8px;
                font-size: 0.85em;
                color: #94a3b8;
                display: flex;
                align-items: center;
                gap: 6px;
            }

            /* Toggle */
            .toggle-details {
                color: #38bdf8;
                font-size: 0.85em;
                cursor: pointer;
                margin-top: 16px;
                display: inline-flex;
                align-items: center;
                gap: 5px;
                padding: 6px 0;
            }
            .toggle-details:hover { color: #7dd3fc; }
            .details-content {
                display: none;
                margin-top: 12px;
            }
            .details-content.visible { display: block; }

            .chunk-item {
                background: #0a0e1a;
                padding: 16px;
                margin: 8px 0;
                border-radius: 10px;
                border: 1px solid #1e293b;
                font-size: 0.9em;
            }
            .chunk-text { color: #cbd5e1; line-height: 1.6; }
            .chunk-meta {
                display: flex; gap: 8px; margin-top: 10px; flex-wrap: wrap;
            }
            .chunk-tag {
                background: #1e293b;
                padding: 3px 10px;
                border-radius: 5px;
                font-size: 0.8em;
                color: #64748b;
            }

            /* Documents */
            .doc-grid { display: grid; gap: 10px; }
            .doc-item {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 14px 18px;
                background: #0a0e1a;
                border-radius: 10px;
                border: 1px solid #1e293b;
            }
            .doc-info { display: flex; align-items: center; gap: 12px; }
            .doc-icon { font-size: 1.5em; }
            .doc-name { color: #e2e8f0; font-weight: 500; }
            .doc-chunks {
                background: #1e293b;
                padding: 4px 12px;
                border-radius: 6px;
                font-size: 0.85em;
                color: #94a3b8;
            }

            .empty-state {
                text-align: center;
                color: #475569;
                padding: 40px;
            }
            .empty-state .empty-icon { font-size: 2.5em; margin-bottom: 10px; }

            .spinner {
                display: inline-block;
                width: 18px; height: 18px;
                border: 2px solid #334155;
                border-top-color: #38bdf8;
                border-radius: 50%;
                animation: spin 0.8s linear infinite;
            }
            @keyframes spin { to { transform: rotate(360deg); } }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>DocSearch</h1>
            <p>Ask questions, get answers from your documents</p>
            <span class="badge">Powered by Endee Vector Database</span>
        </div>

        <div class="container">
            <!-- Upload -->
            <div class="card">
                <h2>📄 Upload Document</h2>
                <div class="upload-area" id="dropZone" onclick="document.getElementById('fileInput').click()">
                    <div class="upload-icon">📁</div>
                    <p>Drop your file here or click to browse</p>
                    <p class="formats">Supports: PDF, DOCX, DOC, TXT</p>
                    <div class="file-name" id="fileName"></div>
                    <input type="file" id="fileInput" accept=".pdf,.docx,.doc,.txt">
                    <button class="upload-btn" id="uploadBtn" onclick="event.stopPropagation(); uploadFile()">Upload & Index</button>
                </div>
                <div id="uploadStatus"></div>
            </div>

            <!-- Search -->
            <div class="card">
                <h2>🔍 Ask a Question</h2>
                <form class="search-box" id="searchForm" onsubmit="askQuestion(event)">
                    <input type="text" id="queryInput" placeholder="e.g. What is the eligibility criteria?" required>
                    <button type="submit" id="askBtn">Ask</button>
                </form>
                <div id="answerBox"></div>
            </div>

            <!-- Documents -->
            <div class="card">
                <h2>📚 Indexed Documents</h2>
                <div class="doc-grid" id="documentList"></div>
            </div>
        </div>

        <script>
            const dropZone = document.getElementById('dropZone');
            const fileInput = document.getElementById('fileInput');

            ['dragenter', 'dragover'].forEach(e => {
                dropZone.addEventListener(e, (ev) => { ev.preventDefault(); dropZone.classList.add('dragover'); });
            });
            ['dragleave', 'drop'].forEach(e => {
                dropZone.addEventListener(e, (ev) => { ev.preventDefault(); dropZone.classList.remove('dragover'); });
            });
            dropZone.addEventListener('drop', (e) => {
                fileInput.files = e.dataTransfer.files;
                showFileName();
            });
            fileInput.addEventListener('change', showFileName);

            function showFileName() {
                if (fileInput.files[0]) {
                    document.getElementById('fileName').textContent = fileInput.files[0].name;
                    document.getElementById('fileName').classList.add('visible');
                    document.getElementById('uploadBtn').classList.add('visible');
                }
            }

            async function uploadFile() {
                const btn = document.getElementById('uploadBtn');
                const status = document.getElementById('uploadStatus');
                if (!fileInput.files[0]) return;

                btn.disabled = true;
                btn.textContent = 'Processing...';
                status.innerHTML = '<div class="status loading"><span class="spinner"></span> Extracting text & indexing...</div>';

                try {
                    const formData = new FormData();
                    formData.append('file', fileInput.files[0]);
                    const response = await fetch('/upload', { method: 'POST', body: formData });
                    const result = await response.json();

                    if (response.ok) {
                        status.innerHTML = '<div class="status success">✅ ' + result.details.filename + ' indexed — ' + result.details.chunks_indexed + ' chunks</div>';
                        loadDocuments();
                        fileInput.value = '';
                        document.getElementById('fileName').classList.remove('visible');
                        btn.classList.remove('visible');
                    } else {
                        status.innerHTML = '<div class="status error">❌ ' + (result.detail || 'Failed') + '</div>';
                    }
                } catch (error) {
                    status.innerHTML = '<div class="status error">❌ ' + error.message + '</div>';
                }
                btn.disabled = false;
                btn.textContent = 'Upload & Index';
            }

            async function askQuestion(e) {
                e.preventDefault();
                const btn = document.getElementById('askBtn');
                const query = document.getElementById('queryInput').value;
                const answerDiv = document.getElementById('answerBox');

                btn.disabled = true;
                btn.textContent = 'Thinking...';
                answerDiv.innerHTML = '<div class="status loading"><span class="spinner"></span> Finding answer in your documents...</div>';

                try {
                    const response = await fetch('/answer', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({query: query, top_k: 3})
                    });
                    const result = await response.json();

                    if (result.answer) {
                        const conf = result.confidence;
                        const confPercent = Math.min(Math.round(conf * 100), 100);
                        const confClass = conf >= 0.5 ? 'high' : conf >= 0.25 ? 'medium' : 'low';
                        const confLabel = conf >= 0.5 ? 'High' : conf >= 0.25 ? 'Medium' : 'Low';

                        let html = '<div class="answer-box">';

                        // Answer
                        html += '<div class="answer-label">Answer</div>';
                        html += '<div class="answer-content">';
                        html += '  <div class="answer-query">Q: ' + query + '</div>';
                        html += '  ' + result.answer;
                        html += '</div>';

                        // Confidence
                        html += '<div class="confidence-bar">';
                        html += '  <span class="confidence-label">Confidence:</span>';
                        html += '  <div class="confidence-track"><div class="confidence-fill ' + confClass + '" style="width:' + confPercent + '%"></div></div>';
                        html += '  <span class="confidence-value">' + confLabel + ' (' + confPercent + '%)</span>';
                        html += '</div>';

                        // Sources
                        if (result.sources && result.sources.length > 0) {
                            html += '<div class="sources">';
                            result.sources.forEach(src => {
                                const ext = src.filename.split('.').pop().toLowerCase();
                                const icon = ext === 'pdf' ? '📕' : ext === 'docx' || ext === 'doc' ? '📘' : '📄';
                                html += '<span class="source-tag">' + icon + ' ' + src.filename + '</span>';
                            });
                            html += '</div>';
                        }

                        // Show details toggle
                        if (result.chunks && result.chunks.length > 0) {
                            html += '<div class="toggle-details" onclick="toggleDetails()">▶ Show source passages</div>';
                            html += '<div class="details-content" id="detailsContent">';
                            result.chunks.forEach((chunk, i) => {
                                html += '<div class="chunk-item">';
                                html += '  <div class="chunk-text">' + chunk.text + '</div>';
                                html += '  <div class="chunk-meta">';
                                html += '    <span class="chunk-tag">' + chunk.filename + '</span>';
                                html += '    <span class="chunk-tag">Score: ' + chunk.score.toFixed(4) + '</span>';
                                html += '  </div>';
                                html += '</div>';
                            });
                            html += '</div>';
                        }

                        html += '</div>';
                        answerDiv.innerHTML = html;
                    } else {
                        answerDiv.innerHTML = '<div class="empty-state"><div class="empty-icon">🔍</div>No answer found. Try uploading more documents.</div>';
                    }
                } catch (error) {
                    answerDiv.innerHTML = '<div class="status error">❌ ' + error.message + '</div>';
                }
                btn.disabled = false;
                btn.textContent = 'Ask';
            }

            function toggleDetails() {
                const content = document.getElementById('detailsContent');
                const toggle = document.querySelector('.toggle-details');
                if (content.classList.contains('visible')) {
                    content.classList.remove('visible');
                    toggle.textContent = '▶ Show source passages';
                } else {
                    content.classList.add('visible');
                    toggle.textContent = '▼ Hide source passages';
                }
            }

            async function loadDocuments() {
                try {
                    const response = await fetch('/documents');
                    const docs = await response.json();
                    const listDiv = document.getElementById('documentList');
                    const entries = Object.entries(docs);

                    if (entries.length === 0) {
                        listDiv.innerHTML = '<div class="empty-state"><div class="empty-icon">📂</div>No documents indexed yet.</div>';
                        return;
                    }

                    let html = '';
                    entries.forEach(([name, info]) => {
                        const ext = name.split('.').pop().toLowerCase();
                        const icon = ext === 'pdf' ? '📕' : ext === 'docx' || ext === 'doc' ? '📘' : '📄';
                        html += '<div class="doc-item">';
                        html += '  <div class="doc-info"><span class="doc-icon">' + icon + '</span><span class="doc-name">' + name + '</span></div>';
                        html += '  <span class="doc-chunks">' + info.chunks + ' chunks</span>';
                        html += '</div>';
                    });
                    listDiv.innerHTML = html;
                } catch (error) {
                    console.error('Error:', error);
                }
            }

            loadDocuments();
        </script>
    </body>
    </html>
    """


@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    try:
        file_path = config.UPLOAD_DIR / file.filename
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        result = search_service.index_document(str(file_path))

        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])

        return {
            "status": "success",
            "message": f"Indexed {file.filename}",
            "details": result
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/search")
async def search(request: SearchRequest):
    try:
        results = search_service.search(request.query, request.top_k)
        return {
            "query": request.query,
            "results": results,
            "count": len(results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/answer")
async def answer(request: SearchRequest):
    try:
        result = search_service.answer(request.query, request.top_k)
        # Also include raw chunks for "show details"
        chunks = search_service.search(request.query, request.top_k)
        result["chunks"] = chunks
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/documents")
async def get_documents():
    return search_service.get_documents()


@app.get("/health")
async def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host=config.APP_HOST, port=config.APP_PORT)

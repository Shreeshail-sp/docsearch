import os
from pathlib import Path

class Config:
    ENDEE_BASE_URL = os.getenv("ENDEE_BASE_URL", "http://localhost:8080")
    ENDEE_AUTH_TOKEN = os.getenv("ENDEE_AUTH_TOKEN", "")

    BASE_DIR = Path(__file__).parent
    UPLOAD_DIR = BASE_DIR / "uploads"
    DATA_DIR = BASE_DIR / "data"
    EMBEDDINGS_DIR = BASE_DIR / "embeddings"

    CHUNK_SIZE = 500
    CHUNK_OVERLAP = 50
    SUPPORTED_FORMATS = ['.pdf', '.docx', '.doc', '.txt']

    EMBEDDING_MODEL = "all-MiniLM-L6-v2"
    VECTOR_DIMENSION = 384

    INDEX_NAME = "documents"
    TOP_K_RESULTS = 5

    APP_HOST = "0.0.0.0"
    APP_PORT = 8000

    def __init__(self):
        self.UPLOAD_DIR.mkdir(exist_ok=True)
        self.DATA_DIR.mkdir(exist_ok=True)
        self.EMBEDDINGS_DIR.mkdir(exist_ok=True)

config = Config()

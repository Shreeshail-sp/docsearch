from typing import List, Dict
from pathlib import Path
import PyPDF2
from docx import Document
from config import config

class DocumentProcessor:
    @staticmethod
    def extract_text(file_path: str) -> str:
        ext = Path(file_path).suffix.lower()

        if ext == '.pdf':
            return DocumentProcessor._extract_pdf(file_path)
        elif ext in ['.docx', '.doc']:
            return DocumentProcessor._extract_docx(file_path)
        elif ext == '.txt':
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        else:
            raise ValueError(f"Unsupported file format: {ext}")

    @staticmethod
    def _extract_pdf(file_path: str) -> str:
        text = ""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text

    @staticmethod
    def _extract_docx(file_path: str) -> str:
        doc = Document(file_path)
        return "\n".join([para.text for para in doc.paragraphs if para.text.strip()])

    @staticmethod
    def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[Dict]:
        chunks = []
        text = text.strip()
        if not text:
            return chunks

        start = 0
        while start < len(text):
            end = start + chunk_size
            chunk_text = text[start:end]

            if end < len(text):
                last_period = chunk_text.rfind('.')
                last_newline = chunk_text.rfind('\n')
                boundary = max(last_period, last_newline)
                if boundary > chunk_size // 2:
                    end = start + boundary + 1
                    chunk_text = text[start:end]

            chunks.append({
                'text': chunk_text.strip(),
                'start': start,
                'end': end
            })

            start = end - overlap

        return chunks

    @staticmethod
    def process_document(file_path: str) -> Dict:
        print(f"Processing: {file_path}")
        text = DocumentProcessor.extract_text(file_path)

        if not text.strip():
            return {"error": "No text extracted from document"}

        chunks = DocumentProcessor.chunk_text(text, config.CHUNK_SIZE, config.CHUNK_OVERLAP)

        filename = Path(file_path).name
        for i, chunk in enumerate(chunks):
            chunk['metadata'] = {
                'filename': filename,
                'chunk_id': i,
                'total_chunks': len(chunks)
            }

        print(f"Created {len(chunks)} chunks from {filename}")
        return {
            'filename': filename,
            'chunks': chunks,
            'total_length': len(text)
        }

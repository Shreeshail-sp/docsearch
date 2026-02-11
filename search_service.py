from typing import List, Dict
import json
import re
from document_processor import DocumentProcessor
from embedding_service import EmbeddingService
from endee_client import EndeeClient
from config import config

class SearchService:
    def __init__(self):
        self.processor = DocumentProcessor()
        self.embedder = EmbeddingService()
        self.endee = EndeeClient()
        self.metadata_file = config.DATA_DIR / "document_metadata.json"
        self.chunks_store = config.DATA_DIR / "chunks_store.json"

        self._init_index()
        self._load_metadata()
        self._load_chunks()

    def _init_index(self):
        if not self.endee.index_exists(config.INDEX_NAME):
            print(f"Creating index: {config.INDEX_NAME}")
            self.endee.create_index(
                config.INDEX_NAME,
                config.VECTOR_DIMENSION,
                "cosine"
            )
        else:
            print(f"Index '{config.INDEX_NAME}' already exists")

    def _load_metadata(self):
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r') as f:
                self.metadata = json.load(f)
        else:
            self.metadata = {"documents": {}}

    def _save_metadata(self):
        with open(self.metadata_file, 'w') as f:
            json.dump(self.metadata, f, indent=2)

    def _load_chunks(self):
        if self.chunks_store.exists():
            with open(self.chunks_store, 'r') as f:
                self.chunks_data = json.load(f)
        else:
            self.chunks_data = {}

    def _save_chunks(self):
        with open(self.chunks_store, 'w') as f:
            json.dump(self.chunks_data, f, indent=2)

    def index_document(self, file_path: str) -> Dict:
        result = self.processor.process_document(file_path)

        if "error" in result:
            return result

        filename = result['filename']
        chunks = result['chunks']

        print(f"Generating embeddings for {len(chunks)} chunks...")
        texts = [chunk['text'] for chunk in chunks]
        embeddings = self.embedder.embed_batch(texts)

        vectors = []
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            vector_id = f"{filename}_{i}"
            vectors.append({
                "id": vector_id,
                "vector": embedding
            })
            self.chunks_data[vector_id] = {
                "text": chunk['text'],
                "filename": filename,
                "chunk_id": i,
                "total_chunks": len(chunks)
            }

        print(f"Inserting {len(vectors)} vectors into Endee...")
        insert_result = self.endee.insert_vectors(config.INDEX_NAME, vectors)

        self.metadata["documents"][filename] = {
            "path": file_path,
            "chunks": len(chunks)
        }
        self._save_metadata()
        self._save_chunks()

        return {
            "status": "success",
            "filename": filename,
            "chunks_indexed": len(chunks)
        }

    def _extract_answer(self, query: str, text: str) -> str:
        """Extract the most relevant sentences from text based on query"""
        query_words = set(query.lower().split())
        # Remove common words
        stop_words = {'what', 'is', 'the', 'a', 'an', 'of', 'in', 'to', 'for',
                      'and', 'or', 'on', 'at', 'by', 'how', 'who', 'where',
                      'when', 'why', 'which', 'are', 'was', 'were', 'be', 'been',
                      'do', 'does', 'did', 'have', 'has', 'had', 'can', 'could',
                      'will', 'would', 'should', 'may', 'might', 'about', 'with',
                      'from', 'this', 'that', 'these', 'those', 'it', 'its'}
        query_keywords = query_words - stop_words

        # Split into sentences
        sentences = re.split(r'[.!?\n]+', text)
        sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 10]

        if not sentences:
            return text[:300]

        # Score each sentence by keyword overlap
        scored = []
        for sentence in sentences:
            sentence_lower = sentence.lower()
            score = 0
            for word in query_keywords:
                if word in sentence_lower:
                    score += 1
            scored.append((score, sentence))

        # Sort by score descending
        scored.sort(key=lambda x: x[0], reverse=True)

        # Take top relevant sentences (up to 3)
        top_sentences = []
        total_len = 0
        for score, sentence in scored:
            if total_len + len(sentence) > 500:
                break
            top_sentences.append(sentence)
            total_len += len(sentence)
            if len(top_sentences) >= 3:
                break

        if not top_sentences:
            return sentences[0] if sentences else text[:300]

        return '. '.join(top_sentences) + '.'

    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        print(f"Searching: {query}")

        query_embedding = self.embedder.embed_text(query)
        results = self.endee.search(config.INDEX_NAME, query_embedding, top_k)

        result_list = results.get("results", [])
        print(f"Raw results from Endee: {result_list}")

        formatted = []
        for i, result in enumerate(result_list):
            if isinstance(result, (list, tuple)) and len(result) >= 2:
                score = float(result[0])
                vector_id = str(result[1])
            elif isinstance(result, dict):
                score = float(result.get("score", result.get("distance", 0.0)))
                vector_id = str(result.get("id", ""))
            else:
                continue

            chunk_data = self.chunks_data.get(vector_id, {})
            text = chunk_data.get("text", "")
            filename = chunk_data.get("filename", "unknown")
            chunk_id = chunk_data.get("chunk_id", 0)

            if text:
                formatted.append({
                    "rank": i + 1,
                    "text": text,
                    "filename": filename,
                    "chunk_id": chunk_id,
                    "score": score
                })

        return formatted

    def answer(self, query: str, top_k: int = 3) -> Dict:
        """Generate a direct answer from the most relevant chunks"""
        print(f"Answering: {query}")

        query_embedding = self.embedder.embed_text(query)
        results = self.endee.search(config.INDEX_NAME, query_embedding, top_k)

        result_list = results.get("results", [])

        if not result_list:
            return {
                "answer": "No relevant information found in the uploaded documents.",
                "sources": [],
                "confidence": 0.0
            }

        # Collect relevant chunks
        chunks_found = []
        for result in result_list:
            if isinstance(result, (list, tuple)) and len(result) >= 2:
                score = float(result[0])
                vector_id = str(result[1])
            elif isinstance(result, dict):
                score = float(result.get("score", 0.0))
                vector_id = str(result.get("id", ""))
            else:
                continue

            chunk_data = self.chunks_data.get(vector_id, {})
            text = chunk_data.get("text", "")
            filename = chunk_data.get("filename", "unknown")

            if text:
                chunks_found.append({
                    "text": text,
                    "filename": filename,
                    "score": score
                })

        if not chunks_found:
            return {
                "answer": "No relevant information found.",
                "sources": [],
                "confidence": 0.0
            }

        # Build answer from top chunks
        top_chunk = chunks_found[0]
        answer_text = self._extract_answer(query, top_chunk["text"])

        # If top score is low, combine multiple chunks
        if top_chunk["score"] < 0.3 and len(chunks_found) > 1:
            combined_text = " ".join([c["text"] for c in chunks_found[:2]])
            answer_text = self._extract_answer(query, combined_text)

        # Build source list
        sources = []
        seen_files = set()
        for chunk in chunks_found:
            if chunk["filename"] not in seen_files:
                sources.append({
                    "filename": chunk["filename"],
                    "score": chunk["score"]
                })
                seen_files.add(chunk["filename"])

        confidence = top_chunk["score"]

        return {
            "answer": answer_text,
            "sources": sources,
            "confidence": confidence
        }

    def get_documents(self) -> Dict:
        return self.metadata.get("documents", {})

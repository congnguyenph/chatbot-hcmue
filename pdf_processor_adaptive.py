import os
import hashlib
import json
import fitz  # PyMuPDF
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyMuPDFLoader
from langchain.schema import Document
from datetime import datetime
import pdf2image
import pytesseract
from typing import List
import concurrent.futures
from chromadb.config import Settings
from sentence_transformers import CrossEncoder
import logging
import re
from cachetools import TTLCache

logging.basicConfig(filename="processing.log", level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class CustomOCRPDFLoader:
    def __init__(self, file_path: str, language: str = os.getenv("OCR_LANGUAGE", "vie")):
        self.file_path = file_path
        self.language = language

    def _clean_text(self, text: str) -> str:
        """Làm sạch văn bản: loại bỏ ký tự đặc biệt, chuẩn hóa khoảng trắng."""
        text = re.sub(r'\s+', ' ', text)  # Chuẩn hóa khoảng trắng
        text = re.sub(r'[^\w\s.,!?]', '', text)  # Loại bỏ ký tự đặc biệt
        return text.strip()

    def load(self) -> List[Document]:
        try:
            images = pdf2image.convert_from_path(self.file_path)
        except Exception as e:
            raise RuntimeError(f"Không thể convert PDF sang ảnh. Lỗi: {e}")

        def process_page(i, image):
            text = pytesseract.image_to_string(image, lang=self.language)
            text = self._clean_text(text)
            return Document(
                page_content=text,
                metadata={
                    "source": self.file_path,
                    "page": i + 1,
                    "total_pages": len(images),
                    "processing_method": "ocr"
                }
            )

        documents = []
        with concurrent.futures.ThreadPoolExecutor() as executor:
            documents = list(executor.map(lambda x: process_page(*x), enumerate(images)))
        return documents

class PDFProcessor:
    def __init__(self, pdf_folder="pdf_documents", db_directory="db", processed_files_path="processed_files.json"):
        self.pdf_folder = pdf_folder
        self.db_directory = db_directory
        self.processed_files_path = processed_files_path
        self.embeddings = HuggingFaceEmbeddings(
            model_name="thanhtantran/Vietnamese_Embedding_v2",
            model_kwargs={"device": "cpu"}
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=200,
            separators=["\n\n", "\n", " ", ""],
            length_function=len
        )
        os.makedirs(pdf_folder, exist_ok=True)
        os.makedirs(db_directory, exist_ok=True)
        self.processed_files = self._load_processed_files()
        self._initialize_db()
        self._reranker = None
        self.rerank_cache = TTLCache(maxsize=100, ttl=3600)  # Cache với TTL 1 giờ
        self.query_complexity_threshold = 8
        self.confidence_threshold = 0.75

    def _get_file_hash(self, filepath):
        hasher = hashlib.md5()
        with open(filepath, 'rb') as f:
            buf = f.read(65536)
            while len(buf) > 0:
                hasher.update(buf)
                buf = f.read(65536)
        return hasher.hexdigest()

    def _load_processed_files(self):
        if os.path.exists(self.processed_files_path):
            with open(self.processed_files_path, 'r') as f:
                return json.load(f)
        return {}

    def _save_processed_files(self):
        with open(self.processed_files_path, 'w') as f:
            json.dump(self.processed_files, f, indent=2)

    def _initialize_db(self):
        self.db = Chroma(
            persist_directory=self.db_directory,
            embedding_function=self.embeddings,
            client_settings=Settings(anonymized_telemetry=False)
        )

    def _is_scanned_pdf(self, pdf_path):
        try:
            doc = fitz.open(pdf_path)
            total_pages = len(doc)
            text_content = sum(len(doc[i].get_text()) for i in range(min(5, total_pages)))
            doc.close()
            return text_content / min(5, total_pages) < 100
        except:
            return False

    def _process_single_pdf(self, file):
        pdf_path = os.path.join(self.pdf_folder, file)
        try:
            current_hash = self._get_file_hash(pdf_path)
            if (file not in self.processed_files or
                self.processed_files[file]['hash'] != current_hash):
                is_scanned = self._is_scanned_pdf(pdf_path)
                loader = CustomOCRPDFLoader(pdf_path, os.getenv("OCR_LANGUAGE", "vie")) if is_scanned else PyMuPDFLoader(pdf_path)
                documents = loader.load()
                for doc in documents:
                    doc.metadata["file_name"] = file
                    doc.metadata["source"] = pdf_path
                    doc.metadata["is_scanned"] = is_scanned
                splits = self.text_splitter.split_documents(documents)
                self.db.add_documents(splits)
                self.processed_files[file] = {
                    'hash': current_hash,
                    'processed_date': datetime.now().isoformat(),
                    'num_pages': len(documents),
                    'num_chunks': len(splits),
                    'is_scanned': is_scanned
                }
                logging.info(f"✅ Đã xử lý: {file} ({len(documents)} trang, {len(splits)} đoạn)")
        except Exception as e:
            logging.error(f"❌ Lỗi xử lý file {file}: {str(e)}")

    def process_pdfs(self):
        pdf_files = [f for f in os.listdir(self.pdf_folder) if f.endswith('.pdf')]
        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.map(self._process_single_pdf, pdf_files)
        self._save_processed_files()

    def _get_reranker(self):
        if self._reranker is None:
            try:
                self._reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
            except Exception as e:
                logging.warning(f"Không thể tải reranker: {str(e)}")
                self._reranker = None
        return self._reranker

    def search_similar(self, query, k=5):
        cache_key = hashlib.md5(query.encode()).hexdigest()
        if cache_key in self.rerank_cache:
            return self.rerank_cache[cache_key][:k]

        query_complexity = len(query.split())
        try:
            initial_results = self.db.similarity_search_with_relevance_scores(query, k=10)
        except:
            initial_results = [(doc, 0.5) for doc in self.db.similarity_search(query, k=10)]

        high_conf = [doc for doc, score in initial_results if score >= self.confidence_threshold]
        if query_complexity < self.query_complexity_threshold and len(high_conf) >= k:
            results = high_conf[:k]
        else:
            docs_to_rerank = [doc for doc, _ in initial_results]
            reranker = self._get_reranker()
            if reranker:
                pairs = [(query, doc.page_content) for doc in docs_to_rerank]
                scores = reranker.predict(pairs)
                scored = [(doc, score) for doc, score in zip(docs_to_rerank, scores) if score >= 0.4]
                scored.sort(key=lambda x: x[1], reverse=True)
                results = [doc for doc, _ in scored[:k]]
            else:
                results = docs_to_rerank[:k]

        self.rerank_cache[cache_key] = results
        return results
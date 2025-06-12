import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Mistral AI Configuration
    MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "")
    MISTRAL_MODEL = "mistral-tiny"  # ou "mistral-small", "mistral-medium"
    
    # ChromaDB Configuration
    CHROMADB_PATH = "./data/vectorstore"
    COLLECTION_NAME = "document_embeddings"
    
    # Text Processing
    DEFAULT_CHUNK_SIZE = 1000
    DEFAULT_CHUNK_OVERLAP = 200
    DEFAULT_K_DOCUMENTS = 3
    
    # Supported file types
    SUPPORTED_EXTENSIONS = ['.pdf', '.docx', '.txt']
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
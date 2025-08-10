"""
Configuration file for the Study Assistant
"""

import os
from typing import Dict, Any

# API Configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-pro")
GEMINI_TEMPERATURE = float(os.getenv("GEMINI_TEMPERATURE", "0.1"))
GEMINI_MAX_TOKENS = int(os.getenv("GEMINI_MAX_TOKENS", "8192"))

# Embedding Configuration
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
EMBEDDING_DEVICE = os.getenv("EMBEDDING_DEVICE", "cpu")

# Document Processing Configuration
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))

# Vector Store Configuration
VECTOR_STORE_TYPE = os.getenv("VECTOR_STORE_TYPE", "chroma")
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "study_materials")

# Search Configuration
DEFAULT_SEARCH_K = int(os.getenv("DEFAULT_SEARCH_K", "5"))
MAX_SEARCH_RESULTS = int(os.getenv("MAX_SEARCH_RESULTS", "10"))

# File Upload Configuration
SUPPORTED_FILE_TYPES = ['pdf', 'docx', 'pptx', 'txt']
MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "50"))
MAX_FILES_PER_UPLOAD = int(os.getenv("MAX_FILES_PER_UPLOAD", "10"))

# UI Configuration
APP_TITLE = "🎓 Personalized Study Assistant"
APP_ICON = "🎓"
SIDEBAR_WIDTH = 300

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", "study_assistant.log")

# Cache Configuration
ENABLE_CACHING = os.getenv("ENABLE_CACHING", "true").lower() == "true"
CACHE_TTL = int(os.getenv("CACHE_TTL", "3600"))  # 1 hour

# Performance Configuration
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "10"))
TIMEOUT_SECONDS = int(os.getenv("TIMEOUT_SECONDS", "30"))

def get_config() -> Dict[str, Any]:
    """Get all configuration as a dictionary"""
    return {
        'api': {
            'google_api_key': GOOGLE_API_KEY,
            'gemini_model': GEMINI_MODEL,
            'gemini_temperature': GEMINI_TEMPERATURE,
            'gemini_max_tokens': GEMINI_MAX_TOKENS
        },
        'embeddings': {
            'model': EMBEDDING_MODEL,
            'device': EMBEDDING_DEVICE
        },
        'document_processing': {
            'chunk_size': CHUNK_SIZE,
            'chunk_overlap': CHUNK_OVERLAP
        },
        'vector_store': {
            'type': VECTOR_STORE_TYPE,
            'persist_dir': CHROMA_PERSIST_DIR,
            'collection_name': COLLECTION_NAME
        },
        'search': {
            'default_k': DEFAULT_SEARCH_K,
            'max_results': MAX_SEARCH_RESULTS
        },
        'files': {
            'supported_types': SUPPORTED_FILE_TYPES,
            'max_size_mb': MAX_FILE_SIZE_MB,
            'max_files': MAX_FILES_PER_UPLOAD
        },
        'ui': {
            'title': APP_TITLE,
            'icon': APP_ICON,
            'sidebar_width': SIDEBAR_WIDTH
        },
        'logging': {
            'level': LOG_LEVEL,
            'file': LOG_FILE
        },
        'performance': {
            'enable_caching': ENABLE_CACHING,
            'cache_ttl': CACHE_TTL,
            'batch_size': BATCH_SIZE,
            'timeout': TIMEOUT_SECONDS
        }
    }

def validate_config() -> bool:
    """Validate configuration settings"""
    try:
        # Check required directories exist or can be created
        if not os.path.exists(CHROMA_PERSIST_DIR):
            os.makedirs(CHROMA_PERSIST_DIR, exist_ok=True)
        
        # Validate numeric values
        assert CHUNK_SIZE > 0, "CHUNK_SIZE must be positive"
        assert CHUNK_OVERLAP >= 0, "CHUNK_OVERLAP must be non-negative"
        assert CHUNK_OVERLAP < CHUNK_SIZE, "CHUNK_OVERLAP must be less than CHUNK_SIZE"
        assert DEFAULT_SEARCH_K > 0, "DEFAULT_SEARCH_K must be positive"
        assert MAX_FILE_SIZE_MB > 0, "MAX_FILE_SIZE_MB must be positive"
        
        return True
        
    except Exception as e:
        print(f"Configuration validation failed: {e}")
        return False

# Environment-specific configurations
DEVELOPMENT_CONFIG = {
    'debug': True,
    'log_level': 'DEBUG',
    'cache_enabled': False
}

PRODUCTION_CONFIG = {
    'debug': False,
    'log_level': 'INFO',
    'cache_enabled': True
}

def get_environment_config(env: str = "development") -> Dict[str, Any]:
    """Get environment-specific configuration"""
    if env.lower() == "production":
        return PRODUCTION_CONFIG
    return DEVELOPMENT_CONFIG

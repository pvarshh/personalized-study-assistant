"""
Vector Store Module
Handles embeddings generation and vector storage using simple implementation
"""

import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

# LangChain imports
from langchain.schema import Document

# Import simple implementation
try:
    from .simple_vector_store import SimpleVectorStore
except ImportError:
    from simple_vector_store import SimpleVectorStore


class VectorStore:
    """Manages vector storage and similarity search using simple implementation"""
    
    def __init__(self, 
                 collection_name: str = "study_materials",
                 embedding_model: str = "all-MiniLM-L6-v2",
                 persist_directory: str = None):
        
        self.collection_name = collection_name
        self.embedding_model = embedding_model
        
        # Use the simple implementation for better compatibility
        logger.info("Using SimpleVectorStore for Streamlit Cloud compatibility")
        try:
            self.store = SimpleVectorStore(
                collection_name=collection_name,
                embedding_model=embedding_model
            )
            logger.info("Vector store initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing vector store: {e}")
            raise
        
        self.document_count = 0
    
    def add_documents(self, documents: List[Document]) -> bool:
        """Add documents to the vector store"""
        try:
            success = self.store.add_documents(documents)
            if success:
                self.document_count = self.store.document_count
            return success
        except Exception as e:
            logger.error(f"Error adding documents: {e}")
            return False
    
    def similarity_search(self, query: str, k: int = 4) -> List[Document]:
        """Search for similar documents"""
        try:
            return self.store.similarity_search(query, k)
        except Exception as e:
            logger.error(f"Error in similarity search: {e}")
            return []
    
    def get_collection_info(self) -> Dict[str, Any]:
        """Get information about the collection"""
        try:
            return self.store.get_collection_info()
        except Exception as e:
            logger.error(f"Error getting collection info: {e}")
            return {"name": self.collection_name, "count": 0}
    
    def clear_collection(self) -> bool:
        """Clear all documents from the collection"""
        try:
            success = self.store.clear_collection()
            if success:
                self.document_count = 0
            return success
        except Exception as e:
            logger.error(f"Error clearing collection: {e}")
            return False
    
    def search_by_metadata(self, metadata_filter: Dict[str, Any], k: int = 10) -> List[Document]:
        """Search documents by metadata"""
        try:
            return self.store.search_by_metadata(metadata_filter, k)
        except Exception as e:
            logger.error(f"Error searching by metadata: {e}")
            return []
    
    def get_all_documents(self) -> List[Document]:
        """Get all documents in the collection"""
        try:
            return self.store.documents.copy() if hasattr(self.store, 'documents') else []
        except Exception as e:
            logger.error(f"Error getting all documents: {e}")
            return []
    
    def cleanup(self):
        """Clean up resources (no-op for simple store)"""
        pass
    
    def __del__(self):
        """Cleanup when object is destroyed"""
        self.cleanup()

"""
Vector Store Module
Handles embeddings generation and vector storage with ChromaDB fallback to simple implementation
"""

import logging
from typing import List, Dict, Any, Optional
import os
import tempfile
import shutil

logger = logging.getLogger(__name__)

# Try ChromaDB first, fall back to simple implementation
try:
    import chromadb
    from chromadb.config import Settings
    from langchain_community.vectorstores import Chroma
    from langchain_community.embeddings import HuggingFaceEmbeddings
    CHROMADB_AVAILABLE = True
    logger.info("ChromaDB available")
except ImportError as e:
    logger.warning(f"ChromaDB not available: {e}")
    CHROMADB_AVAILABLE = False

# LangChain imports
from langchain.schema import Document

# Import simple fallback
try:
    from .simple_vector_store import SimpleVectorStore
except ImportError:
    from simple_vector_store import SimpleVectorStore

class VectorStore:
    """Manages vector storage and similarity search with automatic fallback"""
    
    def __init__(self, 
                 collection_name: str = "study_materials",
                 embedding_model: str = "all-MiniLM-L6-v2",
                 persist_directory: str = None):
        
        self.collection_name = collection_name
        self.embedding_model = embedding_model
        
        # Always use the simple implementation for better compatibility
        logger.info("Using SimpleVectorStore for better Streamlit Cloud compatibility")
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
    
    def cleanup(self):
        """Clean up resources (no-op for simple store)"""
        pass
    
    def __del__(self):
        """Cleanup when object is destroyed"""
        self.cleanup()
    
    def add_documents(self, documents: List[Document]) -> bool:
        """Add documents to the vector store"""
        try:
            if not documents:
                logger.warning("No documents provided to add")
                return False
            
            # Initialize or update the vector store
            if self.vectorstore is None:
                self.vectorstore = Chroma(
                    collection_name=self.collection_name,
                    embedding_function=self.embeddings,
                    client=self.client,
                    persist_directory=self.persist_directory
                )
            
            # Add documents to the vector store
            self.vectorstore.add_documents(documents)
            self.document_count += len(documents)
            
            logger.info(f"Added {len(documents)} documents to vector store. Total: {self.document_count}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding documents to vector store: {e}")
            return False
    
    def similarity_search(self, 
                         query: str, 
                         k: int = 5, 
                         filter_dict: Optional[Dict] = None) -> List[Document]:
        """Perform similarity search on the vector store"""
        try:
            if self.vectorstore is None:
                logger.warning("Vector store not initialized. No documents added yet.")
                return []
            
            # Perform similarity search
            if filter_dict:
                results = self.vectorstore.similarity_search(
                    query=query,
                    k=k,
                    filter=filter_dict
                )
            else:
                results = self.vectorstore.similarity_search(
                    query=query,
                    k=k
                )
            
            logger.info(f"Similarity search for '{query}' returned {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Error performing similarity search: {e}")
            return []
    
    def similarity_search_with_score(self, 
                                   query: str, 
                                   k: int = 5) -> List[tuple]:
        """Perform similarity search with relevance scores"""
        try:
            if self.vectorstore is None:
                logger.warning("Vector store not initialized. No documents added yet.")
                return []
            
            results = self.vectorstore.similarity_search_with_score(
                query=query,
                k=k
            )
            
            logger.info(f"Similarity search with scores for '{query}' returned {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Error performing similarity search with scores: {e}")
            return []
    
    def get_all_documents(self, limit: Optional[int] = None) -> List[Document]:
        """Get all documents from the vector store"""
        try:
            if self.vectorstore is None:
                logger.warning("Vector store not initialized. No documents added yet.")
                return []
            
            # Get the collection
            collection = self.client.get_collection(name=self.collection_name)
            
            # Get all document IDs
            result = collection.get()
            
            if not result['documents']:
                return []
            
            # Convert to Document objects
            documents = []
            for i, (doc_text, metadata) in enumerate(zip(result['documents'], result['metadatas'])):
                if limit and i >= limit:
                    break
                    
                doc = Document(
                    page_content=doc_text,
                    metadata=metadata or {}
                )
                documents.append(doc)
            
            logger.info(f"Retrieved {len(documents)} documents from vector store")
            return documents
            
        except Exception as e:
            logger.error(f"Error getting all documents: {e}")
            return []
    
    def delete_collection(self) -> bool:
        """Delete the entire collection"""
        try:
            if self.vectorstore is not None:
                # Delete the collection
                self.client.delete_collection(name=self.collection_name)
                self.vectorstore = None
                self.document_count = 0
                
                logger.info(f"Deleted collection: {self.collection_name}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error deleting collection: {e}")
            return False
    
    def get_collection_info(self) -> Dict[str, Any]:
        """Get information about the current collection"""
        try:
            if self.vectorstore is None:
                return {
                    'collection_name': self.collection_name,
                    'document_count': 0,
                    'embedding_model': self.embeddings.model_name if hasattr(self.embeddings, 'model_name') else 'unknown',
                    'status': 'not_initialized'
                }
            
            # Get collection
            collection = self.client.get_collection(name=self.collection_name)
            doc_count = collection.count()
            
            return {
                'collection_name': self.collection_name,
                'document_count': doc_count,
                'embedding_model': self.embeddings.model_name if hasattr(self.embeddings, 'model_name') else 'unknown',
                'persist_directory': self.persist_directory,
                'status': 'initialized'
            }
            
        except Exception as e:
            logger.error(f"Error getting collection info: {e}")
            return {
                'collection_name': self.collection_name,
                'document_count': 0,
                'status': 'error',
                'error': str(e)
            }
    
    def search_by_metadata(self, 
                          metadata_filter: Dict[str, Any], 
                          limit: int = 10) -> List[Document]:
        """Search documents by metadata filters"""
        try:
            if self.vectorstore is None:
                logger.warning("Vector store not initialized. No documents added yet.")
                return []
            
            # Get the collection
            collection = self.client.get_collection(name=self.collection_name)
            
            # Build where clause for ChromaDB
            where_clause = {}
            for key, value in metadata_filter.items():
                where_clause[key] = {"$eq": value}
            
            # Query with metadata filter
            result = collection.get(
                where=where_clause,
                limit=limit
            )
            
            # Convert to Document objects
            documents = []
            for doc_text, metadata in zip(result['documents'], result['metadatas']):
                doc = Document(
                    page_content=doc_text,
                    metadata=metadata or {}
                )
                documents.append(doc)
            
            logger.info(f"Metadata search returned {len(documents)} documents")
            return documents
            
        except Exception as e:
            logger.error(f"Error searching by metadata: {e}")
            return []
    
    def cleanup(self):
        """Clean up temporary directories if used"""
        try:
            if (self.persist_directory and 
                self.persist_directory.startswith('/tmp') and 
                os.path.exists(self.persist_directory)):
                shutil.rmtree(self.persist_directory)
                logger.info(f"Cleaned up temporary directory: {self.persist_directory}")
        except Exception as e:
            logger.warning(f"Error cleaning up directory: {e}")
    
    def __del__(self):
        """Cleanup when object is destroyed"""
        self.cleanup()

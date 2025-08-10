"""
Vector Store Module
Handles embeddings generation and vector storage using ChromaDB
"""

import logging
from typing import List, Dict, Any, Optional
import os
import tempfile
import shutil

logger = logging.getLogger(__name__)

try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError as e:
    logger.warning(f"ChromaDB import failed: {e}")
    CHROMADB_AVAILABLE = False

# LangChain imports
from langchain.schema import Document
try:
    from langchain_community.vectorstores import Chroma
    from langchain_community.embeddings import HuggingFaceEmbeddings
    LANGCHAIN_AVAILABLE = True
except ImportError as e:
    logger.warning(f"LangChain imports failed: {e}")
    LANGCHAIN_AVAILABLE = False

class VectorStore:
    """Manages vector storage and similarity search using ChromaDB"""
    
    def __init__(self, 
                 collection_name: str = "study_materials",
                 embedding_model: str = "all-MiniLM-L6-v2",
                 persist_directory: str = None):
        
        self.collection_name = collection_name
        
        # Use temp directory for Streamlit Cloud
        if persist_directory is None:
            if 'STREAMLIT_CLOUD' in os.environ or '/mount/src/' in os.getcwd():
                # Running on Streamlit Cloud - use temp directory
                self.persist_directory = tempfile.mkdtemp(prefix="chroma_")
                logger.info(f"Using temporary directory for ChromaDB: {self.persist_directory}")
            else:
                # Local development
                self.persist_directory = "./chroma_db"
        else:
            self.persist_directory = persist_directory
        
        # Create directory if it doesn't exist
        os.makedirs(self.persist_directory, exist_ok=True)
        
        # Initialize embeddings
        if not LANGCHAIN_AVAILABLE:
            raise RuntimeError("LangChain dependencies not available")
            
        try:
            self.embeddings = HuggingFaceEmbeddings(
                model_name=embedding_model,
                model_kwargs={'device': 'cpu'},  # Use CPU for compatibility
                encode_kwargs={'normalize_embeddings': True}
            )
            logger.info(f"Initialized embeddings with model: {embedding_model}")
        except Exception as e:
            logger.error(f"Error initializing embeddings: {e}")
            raise
        
        # Initialize ChromaDB client with better error handling
        if not CHROMADB_AVAILABLE:
            raise RuntimeError("ChromaDB not available")
            
        try:
            # Configure ChromaDB for Streamlit Cloud
            settings = Settings(
                anonymized_telemetry=False,
                allow_reset=True,
                is_persistent=True
            )
            
            self.client = chromadb.PersistentClient(
                path=self.persist_directory,
                settings=settings
            )
            
            # Initialize the vector store
            self.vectorstore = None
            self.document_count = 0
            
            logger.info("ChromaDB client initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing ChromaDB: {e}")
            # Try in-memory database as fallback
            try:
                logger.info("Attempting to use in-memory ChromaDB as fallback")
                self.client = chromadb.Client(Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                ))
                self.vectorstore = None
                self.document_count = 0
                logger.info("In-memory ChromaDB client initialized successfully")
            except Exception as e2:
                logger.error(f"Fallback ChromaDB initialization also failed: {e2}")
                raise RuntimeError(f"Could not initialize ChromaDB: {e}")
    
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

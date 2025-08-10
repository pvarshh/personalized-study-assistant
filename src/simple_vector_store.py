"""
Simple Vector Store Module
A fallback implementation that doesn't rely on ChromaDB for better Streamlit Cloud compatibility
"""

import logging
import numpy as np
import pickle
import os
from typing import List, Dict, Any, Optional
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

# LangChain imports
from langchain.schema import Document

logger = logging.getLogger(__name__)

class SimpleVectorStore:
    """Simple vector store implementation using sentence transformers and numpy"""
    
    def __init__(self, 
                 collection_name: str = "study_materials",
                 embedding_model: str = "all-MiniLM-L6-v2"):
        
        self.collection_name = collection_name
        self.embedding_model_name = embedding_model
        
        # Initialize embeddings
        try:
            self.embedding_model = SentenceTransformer(embedding_model)
            logger.info(f"Initialized SentenceTransformer with model: {embedding_model}")
        except Exception as e:
            logger.error(f"Error initializing SentenceTransformer: {e}")
            raise
        
        # Storage for documents and embeddings
        self.documents = []
        self.embeddings = []
        self.document_count = 0
        
        logger.info("Simple vector store initialized successfully")
    
    def add_documents(self, documents: List[Document]) -> bool:
        """Add documents to the vector store"""
        try:
            if not documents:
                logger.warning("No documents provided to add")
                return False
            
            # Extract text content
            texts = [doc.page_content for doc in documents]
            
            # Generate embeddings
            logger.info(f"Generating embeddings for {len(texts)} documents...")
            new_embeddings = self.embedding_model.encode(texts, convert_to_tensor=False)
            
            # Store documents and embeddings
            self.documents.extend(documents)
            if len(self.embeddings) == 0:
                self.embeddings = new_embeddings
            else:
                self.embeddings = np.vstack([self.embeddings, new_embeddings])
            
            self.document_count = len(self.documents)
            
            logger.info(f"Successfully added {len(documents)} documents. Total: {self.document_count}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding documents: {e}")
            return False
    
    def similarity_search(self, query: str, k: int = 4) -> List[Document]:
        """Search for similar documents using cosine similarity"""
        try:
            if not self.documents or len(self.embeddings) == 0:
                logger.warning("No documents in vector store")
                return []
            
            # Generate query embedding
            query_embedding = self.embedding_model.encode([query], convert_to_tensor=False)
            
            # Calculate similarities
            similarities = cosine_similarity(query_embedding, self.embeddings)[0]
            
            # Get top k results
            top_indices = np.argsort(similarities)[::-1][:k]
            
            # Return top documents
            results = []
            for idx in top_indices:
                if idx < len(self.documents) and similarities[idx] > 0.05:  # Lower threshold for better recall
                    doc = self.documents[idx]
                    # Add similarity score to metadata
                    doc.metadata = doc.metadata or {}
                    doc.metadata['similarity_score'] = float(similarities[idx])
                    results.append(doc)
            
            # If no results with threshold, return top results anyway (but mark them)
            if not results and len(top_indices) > 0:
                logger.info("No results above threshold, returning top matches anyway")
                for idx in top_indices[:k]:
                    if idx < len(self.documents):
                        doc = self.documents[idx]
                        doc.metadata = doc.metadata or {}
                        doc.metadata['similarity_score'] = float(similarities[idx])
                        doc.metadata['low_confidence'] = True
                        results.append(doc)
            
            logger.info(f"Found {len(results)} similar documents for query")
            return results
            
        except Exception as e:
            logger.error(f"Error in similarity search: {e}")
            return []
    
    def get_collection_info(self) -> Dict[str, Any]:
        """Get information about the collection"""
        return {
            "name": self.collection_name,
            "count": self.document_count,
            "embedding_model": self.embedding_model_name
        }
    
    def clear_collection(self) -> bool:
        """Clear all documents from the collection"""
        try:
            self.documents = []
            self.embeddings = []
            self.document_count = 0
            logger.info("Collection cleared successfully")
            return True
        except Exception as e:
            logger.error(f"Error clearing collection: {e}")
            return False
    
    def search_by_metadata(self, metadata_filter: Dict[str, Any], k: int = 10) -> List[Document]:
        """Search documents by metadata"""
        try:
            filtered_docs = []
            
            for doc in self.documents:
                if doc.metadata:
                    match = True
                    for key, value in metadata_filter.items():
                        if key not in doc.metadata or doc.metadata[key] != value:
                            match = False
                            break
                    if match:
                        filtered_docs.append(doc)
            
            # Return up to k documents
            return filtered_docs[:k]
            
        except Exception as e:
            logger.error(f"Error searching by metadata: {e}")
            return []

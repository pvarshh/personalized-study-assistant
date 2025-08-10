"""
Personalized Study Assistant
A comprehensive AI-powered tool for students to upload study materials and get instant answers.
"""

import streamlit as st
import os
import sys
import tempfile
from typing import List, Dict, Any
import logging
from datetime import datetime

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Core imports
try:
    from document_processor import DocumentProcessor
    from vector_store import VectorStore
    from ai_assistant import AIAssistant
    from utils import setup_logging, validate_api_key
except ImportError:
    # Fallback for local development
    from src.document_processor import DocumentProcessor
    from src.vector_store import VectorStore
    from src.ai_assistant import AIAssistant
    from src.utils import setup_logging, validate_api_key

# Set up logging
setup_logging()
logger = logging.getLogger(__name__)

class StudyAssistant:
    """Main Study Assistant application class"""
    
    def __init__(self):
        self.document_processor = DocumentProcessor()
        self.vector_store = VectorStore()
        self.ai_assistant = None
        self.session_initialized = False
    
    def initialize_session(self, api_key: str):
        """Initialize the AI assistant with API key"""
        try:
            if validate_api_key(api_key):
                self.ai_assistant = AIAssistant(api_key)
                self.session_initialized = True
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to initialize session: {e}")
            return False
    
    def process_documents(self, uploaded_files: List) -> bool:
        """Process uploaded documents and add to vector store"""
        try:
            all_documents = []
            
            for uploaded_file in uploaded_files:
                # Save uploaded file temporarily
                with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    tmp_file_path = tmp_file.name
                
                # Process the document
                documents = self.document_processor.process_file(tmp_file_path, uploaded_file.name)
                all_documents.extend(documents)
                
                # Clean up temporary file
                os.unlink(tmp_file_path)
            
            if all_documents:
                # Add documents to vector store
                self.vector_store.add_documents(all_documents)
                logger.info(f"Successfully processed {len(all_documents)} document chunks")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error processing documents: {e}")
            return False
    
    def answer_question(self, question: str, chat_history: List[Dict]) -> str:
        """Answer a question using RAG approach"""
        try:
            if not self.session_initialized:
                return "Please initialize the session with a valid API key first."
            
            # Retrieve relevant documents
            relevant_docs = self.vector_store.similarity_search(question, k=5)
            
            # Generate answer using AI assistant
            answer = self.ai_assistant.generate_answer(
                question=question,
                context_documents=relevant_docs,
                chat_history=chat_history
            )
            
            return answer
            
        except Exception as e:
            logger.error(f"Error answering question: {e}")
            return f"Sorry, I encountered an error while processing your question: {str(e)}"
    
    def summarize_content(self, topic: str = None) -> str:
        """Generate a summary of uploaded content"""
        try:
            if not self.session_initialized:
                return "Please initialize the session with a valid API key first."
            
            # Get relevant documents for summarization
            if topic:
                relevant_docs = self.vector_store.similarity_search(topic, k=10)
            else:
                # Get a representative sample of all documents
                relevant_docs = self.vector_store.get_all_documents()[:10]
            
            summary = self.ai_assistant.generate_summary(relevant_docs, topic)
            return summary
            
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return f"Sorry, I encountered an error while generating the summary: {str(e)}"


def main():
    """Main Streamlit application"""
    st.set_page_config(
        page_title="Personalized Study Assistant",
        page_icon="🎓",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize session state
    if 'study_assistant' not in st.session_state:
        st.session_state.study_assistant = StudyAssistant()
    
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    if 'documents_uploaded' not in st.session_state:
        st.session_state.documents_uploaded = False
    
    # Main title
    st.title("🎓 Personalized Study Assistant")
    st.markdown("Upload your study materials and get instant, AI-powered answers to your questions!")
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("Configuration")
        
        # API Key input
        api_key = st.text_input(
            "Google API Key",
            type="password",
            help="Enter your Google API key to enable AI features (get one from https://aistudio.google.com/app/apikey)"
        )
        
        if api_key and not st.session_state.study_assistant.session_initialized:
            if st.button("Initialize Session"):
                if st.session_state.study_assistant.initialize_session(api_key):
                    st.success("✅ Session initialized successfully!")
                else:
                    st.error("❌ Invalid API key. Please check and try again.")
        
        st.markdown("---")
        
        # Document upload section
        st.header("📚 Upload Study Materials")
        uploaded_files = st.file_uploader(
            "Choose your study materials",
            accept_multiple_files=True,
            type=['pdf', 'docx', 'pptx', 'txt'],
            help="Upload PDFs, Word documents, PowerPoint presentations, or text files"
        )
        
        if uploaded_files and st.button("Process Documents"):
            with st.spinner("Processing documents..."):
                if st.session_state.study_assistant.process_documents(uploaded_files):
                    st.success(f"✅ Successfully processed {len(uploaded_files)} documents!")
                    st.session_state.documents_uploaded = True
                else:
                    st.error("❌ Error processing documents. Please try again.")
        
        # Document status
        if st.session_state.documents_uploaded:
            st.info("📄 Documents are ready for questions!")
        
        st.markdown("---")
        
        # Quick actions
        st.header("🔧 Quick Actions")
        if st.button("📝 Generate Summary"):
            if st.session_state.documents_uploaded and st.session_state.study_assistant.session_initialized:
                summary = st.session_state.study_assistant.summarize_content()
                st.session_state.chat_history.append({
                    "type": "summary",
                    "content": summary,
                    "timestamp": datetime.now()
                })
            else:
                st.warning("Please upload documents and initialize session first!")
        
        if st.button("🗑️ Clear Chat History"):
            st.session_state.chat_history = []
            st.success("Chat history cleared!")
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("💬 Ask Questions")
        
        # Chat interface
        if st.session_state.chat_history:
            st.subheader("Chat History")
            for i, entry in enumerate(st.session_state.chat_history):
                if entry["type"] == "question":
                    st.markdown(f"**🤔 You:** {entry['content']}")
                elif entry["type"] == "answer":
                    st.markdown(f"**🤖 Assistant:** {entry['content']}")
                elif entry["type"] == "summary":
                    st.markdown(f"**📋 Summary:** {entry['content']}")
                st.markdown("---")
        
        # Question input
        question = st.text_input(
            "Ask a question about your study materials:",
            placeholder="e.g., What are the key concepts in Chapter 3?",
            key="question_input"
        )
        
        col_ask, col_clear = st.columns([1, 1])
        
        with col_ask:
            if st.button("Ask Question", type="primary"):
                if question and st.session_state.documents_uploaded and st.session_state.study_assistant.session_initialized:
                    with st.spinner("Thinking..."):
                        answer = st.session_state.study_assistant.answer_question(
                            question, 
                            st.session_state.chat_history
                        )
                        
                        # Add to chat history
                        st.session_state.chat_history.append({
                            "type": "question",
                            "content": question,
                            "timestamp": datetime.now()
                        })
                        st.session_state.chat_history.append({
                            "type": "answer",
                            "content": answer,
                            "timestamp": datetime.now()
                        })
                        
                        # Clear the input
                        st.rerun()
                else:
                    if not question:
                        st.warning("Please enter a question!")
                    elif not st.session_state.documents_uploaded:
                        st.warning("Please upload and process documents first!")
                    elif not st.session_state.study_assistant.session_initialized:
                        st.warning("Please initialize session with API key first!")
    
    with col2:
        st.header("ℹ️ Features")
        
        st.markdown("""
        ### 🎯 What you can do:
        
        **📚 Document Processing:**
        - Upload PDFs, Word docs, PowerPoints, text files
        - Automatic text extraction and chunking
        - Smart embeddings generation
        
        **🤖 AI-Powered Q&A:**
        - Context-aware answers
        - Retrieval-augmented generation (RAG)
        - Follow-up question support
        
        **📋 Summarization:**
        - Generate summaries of your materials
        - Topic-specific summaries
        - Key points extraction
        
        **💭 Smart Features:**
        - Multi-source cross-referencing
        - Conversation memory
        - Citation support
        """)
        
        st.markdown("---")
        
        st.header("📊 Session Stats")
        stats_col1, stats_col2 = st.columns(2)
        
        with stats_col1:
            st.metric("Documents", len(uploaded_files) if uploaded_files else 0)
        
        with stats_col2:
            st.metric("Questions", len([x for x in st.session_state.chat_history if x["type"] == "question"]))
    
    # Footer
    st.markdown("---")
    st.markdown(
        "Built with ❤️ using Streamlit, LangChain, and OpenAI | "
        "Upload your study materials and start learning smarter!"
    )


if __name__ == "__main__":
    main()

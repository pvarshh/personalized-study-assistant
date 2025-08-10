"""
Utility functions for the Study Assistant
"""

import logging
import os
import re
from typing import Dict, Any, Optional
import streamlit as st

def setup_logging(log_level: str = "INFO"):
    """Set up logging configuration"""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('study_assistant.log')
        ]
    )

def validate_api_key(api_key: str) -> bool:
    """Validate Google API key format"""
    if not api_key:
        return False
    
    # Basic format validation for Google API keys
    # Google API keys typically start with 'AIza' and are around 39 characters long
    if not api_key.startswith('AIza'):
        return False
    
    if len(api_key) < 35:  # Minimum reasonable length
        return False
    
    return True

def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f}{size_names[i]}"

def clean_text(text: str) -> str:
    """Clean and normalize text"""
    if not text:
        return ""
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters that might cause issues
    text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)\[\]\{\}\"\'\/]', '', text)
    
    return text.strip()

def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text to specified length"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."

def extract_keywords(text: str, max_keywords: int = 10) -> list:
    """Extract keywords from text (simple implementation)"""
    # Remove common stop words
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
        'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
        'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
        'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those'
    }
    
    # Extract words
    words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
    
    # Filter out stop words and count frequencies
    word_freq = {}
    for word in words:
        if word not in stop_words:
            word_freq[word] = word_freq.get(word, 0) + 1
    
    # Sort by frequency and return top keywords
    sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    return [word for word, freq in sorted_words[:max_keywords]]

def create_download_link(content: str, filename: str, link_text: str) -> str:
    """Create a download link for content"""
    import base64
    
    b64_content = base64.b64encode(content.encode()).decode()
    href = f'<a href="data:text/plain;base64,{b64_content}" download="{filename}">{link_text}</a>'
    return href

def get_file_info(file) -> Dict[str, Any]:
    """Get information about uploaded file"""
    return {
        'name': file.name,
        'size': len(file.getvalue()),
        'type': file.type,
        'extension': file.name.split('.')[-1].lower() if '.' in file.name else ''
    }

def display_document_stats(documents: list) -> None:
    """Display statistics about processed documents"""
    if not documents:
        st.info("No documents processed yet.")
        return
    
    total_chunks = len(documents)
    sources = set(doc.metadata.get('source', 'Unknown') for doc in documents)
    total_content_length = sum(len(doc.page_content) for doc in documents)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Chunks", total_chunks)
    
    with col2:
        st.metric("Source Files", len(sources))
    
    with col3:
        st.metric("Total Characters", f"{total_content_length:,}")
    
    # Show source breakdown
    if len(sources) > 1:
        st.subheader("Source Breakdown")
        source_stats = {}
        for doc in documents:
            source = doc.metadata.get('source', 'Unknown')
            source_stats[source] = source_stats.get(source, 0) + 1
        
        for source, count in source_stats.items():
            st.write(f"📄 {source}: {count} chunks")

def display_search_results(results: list, max_results: int = 3) -> None:
    """Display search results in a formatted way"""
    if not results:
        st.info("No relevant documents found.")
        return
    
    st.subheader(f"📋 Found {len(results)} relevant sections:")
    
    for i, doc in enumerate(results[:max_results]):
        with st.expander(f"Result {i+1}: {doc.metadata.get('source', 'Unknown')}"):
            st.write(f"**Source:** {doc.metadata.get('source', 'Unknown')}")
            st.write(f"**Chunk:** {doc.metadata.get('chunk_id', 'N/A')}")
            st.write("**Content:**")
            st.write(truncate_text(doc.page_content, 500))

def save_chat_history(chat_history: list, filename: str = "chat_history.txt") -> bool:
    """Save chat history to file"""
    try:
        content = []
        for entry in chat_history:
            timestamp = entry.get('timestamp', 'Unknown time')
            content.append(f"[{timestamp}] {entry['type'].upper()}: {entry['content']}\n")
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.writelines(content)
        
        return True
    except Exception as e:
        logging.error(f"Error saving chat history: {e}")
        return False

def load_sample_questions() -> list:
    """Load sample questions for different subjects"""
    return [
        "What are the main concepts covered in this material?",
        "Can you summarize the key points from chapter 1?",
        "What are the important definitions I should remember?",
        "How do these concepts relate to each other?",
        "What examples are provided for this topic?",
        "What are the practical applications mentioned?",
        "Can you explain this concept in simpler terms?",
        "What are the common misconceptions about this topic?"
    ]

def format_citations(documents: list) -> str:
    """Format document citations"""
    citations = []
    sources = set()
    
    for doc in documents:
        source = doc.metadata.get('source', 'Unknown')
        if source not in sources:
            sources.add(source)
            citations.append(f"• {source}")
    
    if citations:
        return "**Sources:**\n" + "\n".join(citations)
    return ""

def estimate_reading_time(text: str, words_per_minute: int = 200) -> str:
    """Estimate reading time for text"""
    word_count = len(text.split())
    minutes = word_count / words_per_minute
    
    if minutes < 1:
        return "< 1 minute"
    elif minutes < 60:
        return f"{int(minutes)} minutes"
    else:
        hours = int(minutes / 60)
        remaining_minutes = int(minutes % 60)
        return f"{hours}h {remaining_minutes}m"

class StreamlitStateManager:
    """Manage Streamlit session state"""
    
    @staticmethod
    def initialize_state():
        """Initialize default session state values"""
        defaults = {
            'documents_processed': False,
            'chat_history': [],
            'current_question': '',
            'api_key_valid': False,
            'vector_store_ready': False
        }
        
        for key, default_value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = default_value
    
    @staticmethod
    def clear_chat():
        """Clear chat history"""
        st.session_state.chat_history = []
    
    @staticmethod
    def add_to_chat(message_type: str, content: str):
        """Add message to chat history"""
        from datetime import datetime
        
        st.session_state.chat_history.append({
            'type': message_type,
            'content': content,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
    
    @staticmethod
    def get_chat_history() -> list:
        """Get current chat history"""
        return st.session_state.get('chat_history', [])

def create_app_sidebar():
    """Create standardized sidebar for the app"""
    with st.sidebar:
        st.markdown("## 🎓 Study Assistant")
        st.markdown("---")
        
        # App info
        st.markdown("### 📋 Features")
        st.markdown("""
        - 📚 Multi-format document support
        - 🤖 AI-powered Q&A
        - 📊 Smart summarization
        - 🔍 Semantic search
        - 💬 Conversation memory
        """)
        
        st.markdown("---")
        
        # Tips
        st.markdown("### 💡 Tips")
        st.markdown("""
        - Upload multiple related documents
        - Ask specific questions for better answers
        - Use follow-up questions to dive deeper
        - Try different phrasings if needed
        """)
        
        st.markdown("---")
        st.markdown("*Built with Streamlit & LangChain*")

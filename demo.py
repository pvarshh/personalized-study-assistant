"""
Demo script for the Personalized Study Assistant
This script demonstrates the core functionality without the Streamlit UI
"""

import os
import tempfile
from src.document_processor import DocumentProcessor
from src.vector_store import VectorStore
from src.ai_assistant import AIAssistant
from src.utils import setup_logging

def demo_study_assistant():
    """Demonstrate the Study Assistant functionality"""
    print("🎓 Personalized Study Assistant Demo")
    print("=" * 50)
    
    # Setup logging
    setup_logging("INFO")
    
    # Create sample text document for testing
    sample_content = """
    Chapter 1: Introduction to Machine Learning
    
    Machine learning is a subset of artificial intelligence (AI) that focuses on the use of data and algorithms to imitate the way that humans learn, gradually improving its accuracy.
    
    Key Concepts:
    1. Supervised Learning: Learning with labeled examples
    2. Unsupervised Learning: Finding patterns in data without labels
    3. Reinforcement Learning: Learning through interaction and feedback
    
    Applications:
    - Image recognition
    - Natural language processing
    - Recommendation systems
    - Autonomous vehicles
    
    Chapter 2: Types of Machine Learning
    
    Supervised Learning:
    Supervised learning uses labeled training data to learn a mapping function from input variables to output variables. Common algorithms include:
    - Linear Regression
    - Decision Trees
    - Support Vector Machines
    - Neural Networks
    
    Unsupervised Learning:
    Unsupervised learning finds hidden patterns or structures in data without labeled examples:
    - Clustering (K-means, Hierarchical)
    - Association Rules
    - Principal Component Analysis (PCA)
    
    Deep Learning:
    Deep learning is a subset of machine learning that uses neural networks with multiple layers:
    - Convolutional Neural Networks (CNNs) for image processing
    - Recurrent Neural Networks (RNNs) for sequential data
    - Transformers for natural language processing
    """
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(sample_content)
        temp_file = f.name
    
    try:
        print("\n📚 Step 1: Processing Documents")
        print("-" * 30)
        
        # Initialize document processor
        doc_processor = DocumentProcessor(chunk_size=500, chunk_overlap=50)
        
        # Process the document
        documents = doc_processor.process_file(temp_file, "ML_Tutorial.txt")
        print(f"✅ Processed document into {len(documents)} chunks")
        
        print("\n🔍 Step 2: Setting up Vector Store")
        print("-" * 30)
        
        # Initialize vector store
        vector_store = VectorStore(collection_name="demo_collection")
        
        # Add documents to vector store
        success = vector_store.add_documents(documents)
        if success:
            print("✅ Documents added to vector store successfully")
            
            # Get collection info
            info = vector_store.get_collection_info()
            print(f"📊 Collection info: {info['document_count']} documents stored")
        else:
            print("❌ Failed to add documents to vector store")
            return
        
        print("\n🤖 Step 3: AI Assistant Demo")
        print("-" * 30)
        
        # Note: This requires a valid Google API key
        api_key = input("Enter your Google API key (or press Enter to skip AI demo): ").strip()
        
        if api_key:
            try:
                # Initialize AI assistant
                ai_assistant = AIAssistant(api_key)
                
                print("✅ AI Assistant initialized")
                
                # Demo questions
                demo_questions = [
                    "What is machine learning?",
                    "What are the main types of machine learning?",
                    "What are some applications of machine learning?",
                    "What is deep learning and how does it relate to machine learning?"
                ]
                
                print("\n💬 Asking Demo Questions:")
                print("-" * 30)
                
                chat_history = []
                
                for i, question in enumerate(demo_questions, 1):
                    print(f"\n🤔 Question {i}: {question}")
                    
                    # Get relevant documents
                    relevant_docs = vector_store.similarity_search(question, k=3)
                    print(f"📋 Found {len(relevant_docs)} relevant documents")
                    
                    # Generate answer
                    answer = ai_assistant.generate_answer(
                        question=question,
                        context_documents=relevant_docs,
                        chat_history=chat_history
                    )
                    
                    print(f"🤖 Answer: {answer}")
                    
                    # Add to chat history
                    chat_history.append({"type": "question", "content": question})
                    chat_history.append({"type": "answer", "content": answer})
                    
                    print("-" * 50)
                
                print("\n📋 Generating Summary")
                print("-" * 30)
                
                # Generate summary
                summary = ai_assistant.generate_summary(documents[:5])  # Use first 5 chunks
                print(f"📋 Summary: {summary}")
                
            except Exception as e:
                print(f"❌ AI Assistant error: {e}")
                print("Note: Make sure you have a valid Google API key and sufficient quota")
        
        else:
            print("⏭️  Skipping AI demo (no API key provided)")
            
            # Demo search functionality without AI
            print("\n🔍 Demo: Search Functionality")
            print("-" * 30)
            
            search_queries = [
                "supervised learning",
                "neural networks",
                "clustering algorithms"
            ]
            
            for query in search_queries:
                print(f"\n🔍 Searching for: '{query}'")
                results = vector_store.similarity_search(query, k=2)
                
                for i, doc in enumerate(results):
                    print(f"  Result {i+1}: {doc.page_content[:100]}...")
                    print(f"  Source: {doc.metadata.get('source', 'Unknown')}")
        
        print("\n✅ Demo completed successfully!")
        
    finally:
        # Clean up
        if os.path.exists(temp_file):
            os.unlink(temp_file)
        
        # Clean up vector store
        vector_store.delete_collection()
        print("\n🧹 Cleanup completed")

def test_document_processor():
    """Test document processor with different file types"""
    print("\n📄 Testing Document Processor")
    print("-" * 30)
    
    processor = DocumentProcessor()
    
    # Test supported formats
    supported = processor.get_supported_formats()
    print(f"✅ Supported formats: {supported}")
    
    # Test with sample text
    sample_text = "This is a test document. It contains multiple sentences. Each sentence adds to the content."
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(sample_text)
        temp_file = f.name
    
    try:
        documents = processor.process_file(temp_file, "test.txt")
        print(f"✅ Processed text file into {len(documents)} chunks")
        
        if documents:
            print(f"   First chunk: {documents[0].page_content[:50]}...")
            print(f"   Metadata: {documents[0].metadata}")
    
    finally:
        os.unlink(temp_file)

def test_vector_store():
    """Test vector store functionality"""
    print("\n🔍 Testing Vector Store")
    print("-" * 30)
    
    # Create test documents
    from langchain.schema import Document
    
    test_docs = [
        Document(
            page_content="Artificial intelligence is the simulation of human intelligence by machines.",
            metadata={"source": "ai_basics.txt", "chunk_id": 0}
        ),
        Document(
            page_content="Machine learning is a subset of AI that uses data to make predictions.",
            metadata={"source": "ml_intro.txt", "chunk_id": 0}
        ),
        Document(
            page_content="Deep learning uses neural networks with multiple layers for complex patterns.",
            metadata={"source": "dl_guide.txt", "chunk_id": 0}
        )
    ]
    
    # Initialize vector store
    vector_store = VectorStore(collection_name="test_collection")
    
    try:
        # Add documents
        success = vector_store.add_documents(test_docs)
        print(f"✅ Added documents: {success}")
        
        # Test search
        results = vector_store.similarity_search("What is artificial intelligence?", k=2)
        print(f"✅ Search returned {len(results)} results")
        
        for i, doc in enumerate(results):
            print(f"   Result {i+1}: {doc.page_content[:60]}...")
        
        # Test metadata search
        metadata_results = vector_store.search_by_metadata({"source": "ai_basics.txt"})
        print(f"✅ Metadata search returned {len(metadata_results)} results")
        
        # Get collection info
        info = vector_store.get_collection_info()
        print(f"✅ Collection info: {info}")
    
    finally:
        # Cleanup
        vector_store.delete_collection()

if __name__ == "__main__":
    print("🚀 Starting Personalized Study Assistant Demo")
    print("=" * 60)
    
    # Run individual component tests
    test_document_processor()
    test_vector_store()
    
    # Run full demo
    demo_study_assistant()
    
    print("\n🎉 All demos completed!")
    print("\nTo run the full Streamlit application:")
    print("   streamlit run study_assistant.py")
    print("\nMake sure to have your Google API key ready for full functionality!")

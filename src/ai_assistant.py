"""
AI Assistant Module
Handles interaction with Google Gemini for question answering and summarization
"""

import logging
from typing import List, Dict, Any, Optional
import json
import os

# Google GenAI imports
from google import genai
from google.genai import types

# LangChain imports for document handling
from langchain.schema import Document

logger = logging.getLogger(__name__)

class AIAssistant:
    """Handles AI-powered question answering and summarization using Google Gemini"""
    
    def __init__(self, 
                 api_key: str,
                 model_name: str = "gemini-2.5-pro",
                 temperature: float = 0.1,
                 max_tokens: int = 8192):
        
        self.api_key = api_key
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        # Initialize the Gemini client
        try:
            self.client = genai.Client(api_key=api_key)
            logger.info(f"Initialized Google Gemini client with model: {model_name}")
        except Exception as e:
            logger.error(f"Error initializing Google Gemini client: {e}")
            raise
        
        # Define prompts
        self.qa_system_prompt = self._create_qa_system_prompt()
        self.summary_system_prompt = self._create_summary_system_prompt()
    
    def _create_qa_system_prompt(self) -> str:
        """Create system prompt for question answering"""
        return """You are a helpful study assistant. Your role is to answer questions based on the provided study materials.

Guidelines:
- Use ONLY the information provided in the context documents
- Carefully search through ALL provided context documents for relevant information
- Look for specific details like dates, names, numbers, deadlines, and timelines
- If the answer cannot be found in the context, say "I don't have enough information in the provided materials to answer this question."
- For questions about graduation, education, degrees, or completion dates, pay special attention to:
  * Academic timelines and expected completion dates
  * Degree requirements and program duration
  * Educational background and university information
  * Any mentions of "graduation", "graduate", "degree", "completion", or specific dates
- Provide clear, detailed explanations with specific information from the documents
- Include relevant examples from the materials when helpful
- Structure your answers logically
- If multiple sources contain relevant information, synthesize them coherently
- Always cite the source document when providing specific facts or dates

Your responses should be educational, well-structured, and focused on helping students learn effectively."""
    
    def _create_summary_system_prompt(self) -> str:
        """Create system prompt for summarization"""
        return """You are a helpful study assistant specializing in creating comprehensive summaries.

Your task is to create a well-structured summary of the provided study materials.

Guidelines:
- Create a clear, organized summary with main points and key details
- Use bullet points and headers for better readability
- Include important concepts, definitions, and examples
- Maintain logical flow and hierarchy of information
- Focus on the most important and relevant information
- If a specific topic is requested, focus on that topic while providing context"""
    
    def generate_answer(self, 
                       question: str, 
                       context_documents: List[Document], 
                       chat_history: List[Dict] = None) -> str:
        """Generate an answer to a question using RAG"""
        try:
            # Prepare context from documents
            context = self._prepare_context(context_documents)
            
            # Prepare chat history
            chat_history_text = self._format_chat_history(chat_history or [])
            
            # Create the prompt
            prompt = f"""{self.qa_system_prompt}

Context Documents:
{context}

Previous Conversation:
{chat_history_text}

Question: {question}

Answer:"""
            
            # Generate response using Gemini
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=self.temperature,
                    max_output_tokens=self.max_tokens,
                    response_mime_type="text/plain"
                )
            )
            
            answer = response.text.strip()
            
            logger.info(f"Generated answer for question: {question[:50]}...")
            return answer
            
        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            return f"I apologize, but I encountered an error while processing your question: {str(e)}"
    
    def generate_summary(self, 
                        documents: List[Document], 
                        topic: Optional[str] = None) -> str:
        """Generate a summary of the provided documents"""
        try:
            # Prepare context from documents
            context = self._prepare_context(documents)
            
            # Prepare topic instruction
            if topic:
                topic_instruction = f"Focus your summary on the topic: '{topic}'"
            else:
                topic_instruction = "Provide a comprehensive summary of all the materials."
            
            # Create the prompt
            prompt = f"""{self.summary_system_prompt}

Study Materials:
{context}

{topic_instruction}

Summary:"""
            
            # Generate summary using Gemini
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=self.temperature,
                    max_output_tokens=self.max_tokens,
                    response_mime_type="text/plain"
                )
            )
            
            summary = response.text.strip()
            
            logger.info(f"Generated summary (topic: {topic or 'general'})")
            return summary
            
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return f"I apologize, but I encountered an error while generating the summary: {str(e)}"
    
    def _prepare_context(self, documents: List[Document]) -> str:
        """Prepare context string from documents"""
        if not documents:
            return "No relevant documents found."
        
        context_parts = []
        for i, doc in enumerate(documents):
            source = doc.metadata.get('source', 'Unknown')
            chunk_id = doc.metadata.get('chunk_id', i)
            
            context_part = f"--- Source: {source} (Chunk {chunk_id}) ---\n"
            context_part += doc.page_content
            context_parts.append(context_part)
        
        return "\n\n".join(context_parts)
    
    def _format_chat_history(self, chat_history: List[Dict]) -> str:
        """Format chat history for prompt"""
        if not chat_history:
            return "No previous conversation."
        
        formatted_history = []
        for entry in chat_history[-10:]:  # Last 10 entries to avoid token limits
            if entry["type"] == "question":
                formatted_history.append(f"User: {entry['content']}")
            elif entry["type"] == "answer":
                formatted_history.append(f"Assistant: {entry['content']}")
            elif entry["type"] == "summary":
                formatted_history.append(f"Summary: {entry['content']}")
        
        return "\n".join(formatted_history)
    
    def suggest_followup_questions(self, 
                                  question: str, 
                                  answer: str, 
                                  context_documents: List[Document]) -> List[str]:
        """Suggest relevant follow-up questions"""
        try:
            # Extract topics from documents
            topics = self._extract_topics_from_documents(context_documents)
            
            followup_prompt = f"""Based on the question, answer, and available study materials, suggest 3 relevant follow-up questions that would help the student learn more about this topic.

Original Question: {question}
Answer: {answer}

Available Topics in Materials:
{topics}

Suggest 3 follow-up questions (one per line, without numbering):"""
            
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=followup_prompt,
                config=types.GenerateContentConfig(
                    temperature=0.3,
                    max_output_tokens=200,
                    response_mime_type="text/plain"
                )
            )
            
            suggestions = response.text.strip().split('\n')
            
            # Clean up suggestions
            clean_suggestions = []
            for suggestion in suggestions[:3]:
                suggestion = suggestion.strip()
                if suggestion and not suggestion.startswith('#'):
                    # Remove numbering if present
                    suggestion = suggestion.lstrip('123456789. ')
                    clean_suggestions.append(suggestion)
            
            return clean_suggestions
            
        except Exception as e:
            logger.error(f"Error generating follow-up questions: {e}")
            return ["What are the key concepts related to this topic?",
                   "Can you provide more examples?",
                   "How does this connect to other topics?"]
    
    def _extract_topics_from_documents(self, documents: List[Document]) -> str:
        """Extract key topics from documents for follow-up suggestions"""
        sources = set()
        for doc in documents:
            source = doc.metadata.get('source', 'Unknown')
            sources.add(source)
        
        return ", ".join(sources)
    
    def validate_api_key(self) -> bool:
        """Validate if the API key is working"""
        try:
            # Try a simple request
            response = self.client.models.generate_content(
                model=self.model_name,
                contents="Hello",
                config=types.GenerateContentConfig(
                    max_output_tokens=10
                )
            )
            return bool(response.text)
        except Exception as e:
            logger.error(f"API key validation failed: {e}")
            return False
    
    def explain_concept(self, concept: str, context_documents: List[Document]) -> str:
        """Provide a detailed explanation of a specific concept"""
        try:
            context = self._prepare_context(context_documents)
            
            prompt = f"""You are an educational assistant. Explain the following concept in detail based on the provided study materials.

Concept to explain: {concept}

Study Materials:
{context}

Provide a comprehensive explanation including:
1. Definition
2. Key characteristics
3. Examples from the materials
4. How it relates to other concepts
5. Practical applications if mentioned

Explanation:"""
            
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=self.temperature,
                    max_output_tokens=self.max_tokens,
                    response_mime_type="text/plain"
                )
            )
            
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"Error explaining concept: {e}")
            return f"I encountered an error while explaining the concept: {str(e)}"
    
    def create_quiz_questions(self, documents: List[Document], num_questions: int = 5) -> List[Dict]:
        """Generate quiz questions based on the study materials"""
        try:
            context = self._prepare_context(documents)
            
            prompt = f"""Based on the provided study materials, create {num_questions} quiz questions that test understanding of the key concepts.

Study Materials:
{context}

For each question, provide:
1. The question
2. Multiple choice options (A, B, C, D)
3. The correct answer
4. A brief explanation

Format each question as:
Question: [question text]
A) [option A]
B) [option B]
C) [option C]
D) [option D]
Correct Answer: [letter]
Explanation: [brief explanation]

Generate {num_questions} questions:"""
            
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.2,
                    max_output_tokens=self.max_tokens,
                    response_mime_type="text/plain"
                )
            )
            
            # Parse the response into structured quiz questions
            quiz_text = response.text.strip()
            questions = self._parse_quiz_questions(quiz_text)
            
            return questions
            
        except Exception as e:
            logger.error(f"Error creating quiz questions: {e}")
            return []
    
    def _parse_quiz_questions(self, quiz_text: str) -> List[Dict]:
        """Parse quiz questions from text into structured format"""
        questions = []
        current_question = {}
        
        lines = quiz_text.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('Question:'):
                if current_question:
                    questions.append(current_question)
                current_question = {'question': line[9:].strip(), 'options': {}, 'answer': '', 'explanation': ''}
            elif line.startswith('A)'):
                current_question['options']['A'] = line[2:].strip()
            elif line.startswith('B)'):
                current_question['options']['B'] = line[2:].strip()
            elif line.startswith('C)'):
                current_question['options']['C'] = line[2:].strip()
            elif line.startswith('D)'):
                current_question['options']['D'] = line[2:].strip()
            elif line.startswith('Correct Answer:'):
                current_question['answer'] = line[15:].strip()
            elif line.startswith('Explanation:'):
                current_question['explanation'] = line[12:].strip()
        
        if current_question:
            questions.append(current_question)
        
        return questions

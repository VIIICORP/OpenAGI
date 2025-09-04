"""
Memory Management System for OpenAGI

This module provides both short-term (working) memory and long-term persistent
memory using ChromaDB as the vector database backend. The memory system allows
the agent to:

- Remember past conversations and interactions
- Store and retrieve learned information
- Build up knowledge over time
- Maintain context across sessions
"""

import os
import json
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
import chromadb
from chromadb.config import Settings
import logging

logger = logging.getLogger(__name__)

class MemoryManager:
    """
    Manages the agent's memory using ChromaDB for long-term persistence
    and in-memory storage for short-term working memory.
    """
    
    def __init__(self, memory_path: str = "./agent_memory"):
        """
        Initialize the memory management system.
        
        Args:
            memory_path: Path where ChromaDB will store persistent memory
        """
        self.memory_path = memory_path
        self.working_memory = {}  # Short-term memory
        self.conversation_history = []  # Current session history
        
        # Initialize ChromaDB for long-term memory
        self._initialize_persistent_memory()
        
    def _initialize_persistent_memory(self):
        """Initialize the ChromaDB client and collections."""
        try:
            # Create the memory directory if it doesn't exist
            os.makedirs(self.memory_path, exist_ok=True)
            
            # Initialize ChromaDB with persistent storage
            self.chroma_client = chromadb.PersistentClient(
                path=self.memory_path,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # Create or get collections for different types of memories
            self.long_term_memory = self.chroma_client.get_or_create_collection(
                name="agent_long_term_memory",
                metadata={"hnsw:space": "cosine"}
            )
            
            self.knowledge_base = self.chroma_client.get_or_create_collection(
                name="agent_knowledge_base", 
                metadata={"hnsw:space": "cosine"}
            )
            
            self.experiences = self.chroma_client.get_or_create_collection(
                name="agent_experiences",
                metadata={"hnsw:space": "cosine"}
            )
            
            logger.info(f"Memory system initialized at {self.memory_path}")
            
        except Exception as e:
            logger.error(f"Failed to initialize persistent memory: {e}")
            # Fallback to in-memory only
            self.chroma_client = None
            self.long_term_memory = None
            self.knowledge_base = None
            self.experiences = None
    
    def store_short_term(self, key: str, value: Any):
        """
        Store information in short-term working memory.
        
        Args:
            key: Memory key
            value: Value to store
        """
        self.working_memory[key] = {
            "value": value,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_short_term(self, key: str) -> Any:
        """
        Retrieve information from short-term memory.
        
        Args:
            key: Memory key
            
        Returns:
            The stored value or None if not found
        """
        memory_item = self.working_memory.get(key)
        return memory_item["value"] if memory_item else None
    
    def store_long_term(self, content: str, metadata: Optional[Dict] = None, 
                       memory_type: str = "general"):
        """
        Store information in long-term persistent memory.
        
        Args:
            content: The content to store
            metadata: Optional metadata about the memory
            memory_type: Type of memory (general, knowledge, experience)
        """
        if not self.chroma_client:
            logger.warning("Persistent memory not available, storing in working memory")
            self.store_short_term(f"long_term_{uuid.uuid4()}", content)
            return
            
        memory_id = str(uuid.uuid4())
        storage_metadata = {
            "timestamp": datetime.now().isoformat(),
            "type": memory_type,
            **(metadata or {})
        }
        
        try:
            # Choose the appropriate collection based on memory type
            if memory_type == "knowledge":
                collection = self.knowledge_base
            elif memory_type == "experience":
                collection = self.experiences
            else:
                collection = self.long_term_memory
                
            collection.add(
                documents=[content],
                metadatas=[storage_metadata],
                ids=[memory_id]
            )
            
            logger.debug(f"Stored long-term memory: {memory_id}")
            
        except Exception as e:
            logger.error(f"Failed to store long-term memory: {e}")
    
    def recall_memories(self, query: str, n_results: int = 5, 
                       memory_type: str = "all") -> List[Dict]:
        """
        Recall relevant memories based on a query.
        
        Args:
            query: Search query
            n_results: Number of results to return
            memory_type: Type of memory to search (all, general, knowledge, experience)
            
        Returns:
            List of relevant memory entries
        """
        if not self.chroma_client:
            logger.warning("Persistent memory not available")
            return []
            
        memories = []
        
        try:
            # Search appropriate collections
            collections_to_search = []
            if memory_type == "all":
                collections_to_search = [
                    self.long_term_memory, 
                    self.knowledge_base, 
                    self.experiences
                ]
            elif memory_type == "knowledge":
                collections_to_search = [self.knowledge_base]
            elif memory_type == "experience":
                collections_to_search = [self.experiences]
            else:
                collections_to_search = [self.long_term_memory]
            
            for collection in collections_to_search:
                if collection:
                    results = collection.query(
                        query_texts=[query],
                        n_results=n_results
                    )
                    
                    for i, doc in enumerate(results["documents"][0]):
                        memory_entry = {
                            "content": doc,
                            "metadata": results["metadatas"][0][i],
                            "distance": results["distances"][0][i] if "distances" in results else 0.0
                        }
                        memories.append(memory_entry)
            
            # Sort by relevance (lower distance is better)
            memories.sort(key=lambda x: x["distance"])
            return memories[:n_results]
            
        except Exception as e:
            logger.error(f"Failed to recall memories: {e}")
            return []
    
    def add_to_conversation(self, role: str, content: str):
        """
        Add a message to the current conversation history.
        
        Args:
            role: The role (user, assistant, system)
            content: The message content
        """
        self.conversation_history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        
        # Store significant conversations in long-term memory
        if len(self.conversation_history) % 10 == 0:  # Every 10 messages
            conversation_summary = self._summarize_conversation()
            self.store_long_term(
                conversation_summary,
                {"type": "conversation", "length": len(self.conversation_history)},
                "experience"
            )
    
    def get_conversation_context(self, max_messages: int = 20) -> List[Dict]:
        """
        Get recent conversation history for context.
        
        Args:
            max_messages: Maximum number of recent messages to return
            
        Returns:
            List of recent conversation messages
        """
        return self.conversation_history[-max_messages:]
    
    def _summarize_conversation(self) -> str:
        """Create a summary of the current conversation for long-term storage."""
        if not self.conversation_history:
            return "Empty conversation"
            
        # Simple summarization - could be enhanced with LLM
        user_messages = [msg for msg in self.conversation_history if msg["role"] == "user"]
        assistant_messages = [msg for msg in self.conversation_history if msg["role"] == "assistant"]
        
        summary = f"Conversation with {len(user_messages)} user messages and {len(assistant_messages)} responses. "
        
        if user_messages:
            recent_topics = [msg["content"][:100] for msg in user_messages[-3:]]
            summary += f"Recent topics: {'; '.join(recent_topics)}"
            
        return summary
    
    def clear_working_memory(self):
        """Clear the short-term working memory."""
        self.working_memory.clear()
        logger.info("Working memory cleared")
    
    def get_memory_stats(self) -> Dict:
        """
        Get statistics about the memory system.
        
        Returns:
            Dictionary with memory statistics
        """
        stats = {
            "working_memory_items": len(self.working_memory),
            "conversation_length": len(self.conversation_history),
            "persistent_available": self.chroma_client is not None
        }
        
        if self.chroma_client:
            try:
                stats["long_term_memories"] = self.long_term_memory.count()
                stats["knowledge_entries"] = self.knowledge_base.count()
                stats["experiences"] = self.experiences.count()
            except Exception as e:
                logger.error(f"Failed to get memory stats: {e}")
                
        return stats
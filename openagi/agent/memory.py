"""
Memory system for the OpenAGI agent.
"""
import json
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional

# Import ChromaDB and sentence transformers conditionally
try:
    import chromadb
    from sentence_transformers import SentenceTransformer
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False

class MemoryManager:
    """
    Manages the agent's memory using ChromaDB for long-term persistence.
    Provides both short-term working memory and long-term episodic memory.
    """
    
    def __init__(self, persist_directory: str = "./agent_memory"):
        """
        Initialize the memory manager.
        
        Args:
            persist_directory: Directory to persist the ChromaDB collection
        """
        self.persist_directory = persist_directory
        self.short_term_memory = {}  # Working memory for current session
        
        if CHROMADB_AVAILABLE:
            self._init_chromadb()
        else:
            print("WARNING: [Memory] ChromaDB not available. Using in-memory storage only.")
            self.long_term_collection = None
            self.embedding_model = None
    
    def _init_chromadb(self):
        """Initialize ChromaDB components."""
        try:
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            
            # Initialize ChromaDB for long-term memory
            self.chroma_client = chromadb.PersistentClient(path=self.persist_directory)
            self.long_term_collection = self.chroma_client.get_or_create_collection(
                name="agent_long_term_memory",
                metadata={"description": "Long-term episodic memory for the OpenAGI agent"}
            )
            
            print(f"INFO: [Memory] ChromaDB initialized at '{self.persist_directory}' with collection 'agent_long_term_memory'.")
        except Exception as e:
            print(f"WARNING: [Memory] ChromaDB initialization failed: {e}")
            self.long_term_collection = None
            self.embedding_model = None
    
    def store_short_term(self, key: str, value: Any) -> None:
        """Store information in short-term working memory."""
        self.short_term_memory[key] = {
            "value": value,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_short_term(self, key: str) -> Optional[Any]:
        """Retrieve information from short-term memory."""
        entry = self.short_term_memory.get(key)
        return entry["value"] if entry else None
    
    def clear_short_term(self) -> None:
        """Clear all short-term memory."""
        self.short_term_memory.clear()
    
    def store_long_term(self, content: str, metadata: Dict[str, Any] = None) -> str:
        """
        Store information in long-term memory with semantic search capabilities.
        
        Args:
            content: The content to store
            metadata: Optional metadata about the memory
            
        Returns:
            str: The ID of the stored memory
        """
        memory_id = str(uuid.uuid4())
        
        if not CHROMADB_AVAILABLE or not self.long_term_collection:
            # Store in short-term as fallback
            self.store_short_term(f"long_term_{memory_id}", {
                "content": content,
                "metadata": metadata or {},
                "timestamp": datetime.now().isoformat()
            })
            return memory_id
        
        if metadata is None:
            metadata = {}
        
        metadata.update({
            "timestamp": datetime.now().isoformat(),
            "memory_id": memory_id
        })
        
        try:
            # Generate embedding for semantic search
            embedding = self.embedding_model.encode([content])[0].tolist()
            
            self.long_term_collection.add(
                documents=[content],
                embeddings=[embedding],
                metadatas=[metadata],
                ids=[memory_id]
            )
        except Exception as e:
            print(f"WARNING: [Memory] Failed to store long-term memory: {e}")
            # Fallback to short-term storage
            self.store_short_term(f"long_term_{memory_id}", {
                "content": content,
                "metadata": metadata,
                "timestamp": datetime.now().isoformat()
            })
        
        return memory_id
    
    def recall_similar(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """
        Recall memories similar to the given query using semantic search.
        
        Args:
            query: The query to search for
            n_results: Number of results to return
            
        Returns:
            List of similar memories with content and metadata
        """
        if not CHROMADB_AVAILABLE or not self.long_term_collection:
            # Return empty list if ChromaDB not available
            return []
        
        try:
            query_embedding = self.embedding_model.encode([query])[0].tolist()
            
            results = self.long_term_collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results
            )
            
            memories = []
            if results["documents"]:
                for i, doc in enumerate(results["documents"][0]):
                    memory = {
                        "content": doc,
                        "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                        "distance": results["distances"][0][i] if results["distances"] else None
                    }
                    memories.append(memory)
            
            return memories
        except Exception as e:
            print(f"WARNING: [Memory] Failed to recall memories: {e}")
            return []
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get statistics about the memory system."""
        long_term_count = 0
        if CHROMADB_AVAILABLE and self.long_term_collection:
            try:
                long_term_count = self.long_term_collection.count()
            except:
                pass
        
        short_term_count = len(self.short_term_memory)
        
        return {
            "short_term_memories": short_term_count,
            "long_term_memories": long_term_count,
            "persist_directory": self.persist_directory,
            "chromadb_available": CHROMADB_AVAILABLE
        }
    
    def save_experience(self, experience: Dict[str, Any]) -> str:
        """
        Save a complete experience (goal, plan, execution, outcome) to long-term memory.
        
        Args:
            experience: Dictionary containing the experience details
            
        Returns:
            str: The ID of the stored experience
        """
        content = f"""
Experience: {experience.get('goal', 'Unknown goal')}
Plan: {json.dumps(experience.get('plan', {}), indent=2)}
Execution: {experience.get('execution_summary', 'No summary')}
Outcome: {experience.get('outcome', 'Unknown outcome')}
Lessons: {experience.get('lessons_learned', 'None recorded')}
        """.strip()
        
        metadata = {
            "type": "experience",
            "goal": experience.get('goal', ''),
            "success": experience.get('success', False),
            "tools_used": experience.get('tools_used', [])
        }
        
        return self.store_long_term(content, metadata)
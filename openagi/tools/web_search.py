"""
Web search tool for the OpenAGI agent.

This tool provides the agent with the ability to search the web for current
information using DuckDuckGo search.
"""

import logging
from typing import Dict, Any, List
from .base import BaseTool

logger = logging.getLogger(__name__)

try:
    from duckduckgo_search import DDGS
    SEARCH_AVAILABLE = True
except ImportError:
    SEARCH_AVAILABLE = False
    logger.warning("duckduckgo_search not available. Web search will be disabled.")

class WebSearchTool(BaseTool):
    """
    Tool for performing web searches using DuckDuckGo.
    
    This tool allows the agent to access current information from the internet,
    making it capable of answering questions about recent events and finding
    up-to-date information.
    """
    
    @property
    def name(self) -> str:
        return "web_search"
    
    @property
    def description(self) -> str:
        return "Search the web for current information using DuckDuckGo. Returns relevant search results with titles, snippets, and URLs."
    
    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query to look for on the web"
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of search results to return (default: 5, max: 10)",
                    "minimum": 1,
                    "maximum": 10,
                    "default": 5
                }
            },
            "required": ["query"]
        }
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Execute a web search.
        
        Args:
            query: The search query
            max_results: Maximum number of results to return (default: 5)
            
        Returns:
            Dictionary containing search results and metadata
        """
        if not SEARCH_AVAILABLE:
            return {
                "success": False,
                "error": "Web search is not available. DuckDuckGo search library not installed.",
                "results": []
            }
        
        query = kwargs.get("query", "")
        max_results = kwargs.get("max_results", 5)
        
        if not query:
            return {
                "success": False,
                "error": "Search query is required",
                "results": []
            }
        
        try:
            # Ensure max_results is within bounds
            max_results = max(1, min(10, max_results))
            
            # Perform the search
            with DDGS() as ddgs:
                search_results = list(ddgs.text(query, max_results=max_results))
            
            # Format results for the agent
            formatted_results = []
            for result in search_results:
                formatted_result = {
                    "title": result.get("title", ""),
                    "url": result.get("href", ""),
                    "snippet": result.get("body", ""),
                }
                formatted_results.append(formatted_result)
            
            return {
                "success": True,
                "query": query,
                "num_results": len(formatted_results),
                "results": formatted_results
            }
            
        except Exception as e:
            logger.error(f"Web search failed: {e}")
            return {
                "success": False,
                "error": f"Search failed: {str(e)}",
                "results": []
            }
    
    def get_usage_examples(self) -> List[Dict[str, Any]]:
        return [
            {
                "description": "Search for recent AI developments",
                "parameters": {
                    "query": "latest artificial intelligence breakthroughs 2024",
                    "max_results": 5
                }
            },
            {
                "description": "Find information about a specific topic",
                "parameters": {
                    "query": "how to implement neural networks",
                    "max_results": 3
                }
            }
        ]
    
    def get_safety_notes(self) -> List[str]:
        return [
            "Search results may contain inaccurate or biased information",
            "Always cross-reference important information from multiple sources",
            "Be aware that search results reflect current web content which may be outdated",
            "Respect rate limits and don't perform excessive searches"
        ]
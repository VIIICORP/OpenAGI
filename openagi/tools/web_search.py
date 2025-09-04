"""
A tool for performing web searches.
"""
from typing import Dict, Any
from duckduckgo_search import DDGS
from .base import BaseTool

class WebSearchTool(BaseTool):
    """
    Tool for searching the web using DuckDuckGo search.
    Provides real-time access to information on the internet.
    """
    
    @property
    def name(self) -> str:
        return "web_search"
    
    @property
    def description(self) -> str:
        return "Search the web for real-time information using DuckDuckGo. Useful for getting current information, news, or answering questions that require up-to-date data."
    
    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query to execute"
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of results to return (default: 5)",
                    "default": 5,
                    "minimum": 1,
                    "maximum": 20
                }
            },
            "required": ["query"]
        }
    
    def execute(self, query: str, max_results: int = 5, **kwargs) -> Dict[str, Any]:
        """
        Execute a web search.
        
        Args:
            query: The search query
            max_results: Maximum number of results to return
            
        Returns:
            Dict containing search results
        """
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=max_results))
            
            formatted_results = []
            for result in results:
                formatted_results.append({
                    "title": result.get("title", ""),
                    "url": result.get("href", ""),
                    "snippet": result.get("body", ""),
                    "source": "DuckDuckGo"
                })
            
            return {
                "success": True,
                "query": query,
                "results": formatted_results,
                "result_count": len(formatted_results)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Search failed: {str(e)}",
                "query": query,
                "results": []
            }
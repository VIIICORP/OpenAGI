"""
File system tools for the OpenAGI agent.
"""
import os
import json
from typing import Dict, Any, List
from .base import BaseTool

class ReadFileTool(BaseTool):
    """Tool for reading files from the file system."""
    
    @property
    def name(self) -> str:
        return "read_file"
    
    @property
    def description(self) -> str:
        return "Read the contents of a file from the file system. Supports text files and common formats."
    
    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to the file to read"
                },
                "encoding": {
                    "type": "string", 
                    "description": "File encoding (default: utf-8)",
                    "default": "utf-8"
                }
            },
            "required": ["file_path"]
        }
    
    def execute(self, file_path: str, encoding: str = "utf-8", **kwargs) -> Dict[str, Any]:
        """Read a file and return its contents."""
        try:
            if not os.path.exists(file_path):
                return {
                    "success": False,
                    "error": f"File not found: {file_path}",
                    "content": None
                }
            
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
            
            return {
                "success": True,
                "file_path": file_path,
                "content": content,
                "size_bytes": len(content.encode(encoding))
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to read file: {str(e)}",
                "content": None
            }

class WriteFileTool(BaseTool):
    """Tool for writing files to the file system."""
    
    @property
    def name(self) -> str:
        return "write_file"
    
    @property
    def description(self) -> str:
        return "Write content to a file on the file system. Creates directories if they don't exist."
    
    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path where to write the file"
                },
                "content": {
                    "type": "string",
                    "description": "Content to write to the file"
                },
                "encoding": {
                    "type": "string",
                    "description": "File encoding (default: utf-8)",
                    "default": "utf-8"
                },
                "create_dirs": {
                    "type": "boolean",
                    "description": "Create parent directories if they don't exist (default: true)",
                    "default": True
                }
            },
            "required": ["file_path", "content"]
        }
    
    def execute(self, file_path: str, content: str, encoding: str = "utf-8", create_dirs: bool = True, **kwargs) -> Dict[str, Any]:
        """Write content to a file."""
        try:
            if create_dirs:
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, 'w', encoding=encoding) as f:
                f.write(content)
            
            return {
                "success": True,
                "file_path": file_path,
                "bytes_written": len(content.encode(encoding))
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to write file: {str(e)}"
            }

class ListFilesTool(BaseTool):
    """Tool for listing files and directories."""
    
    @property
    def name(self) -> str:
        return "list_files"
    
    @property
    def description(self) -> str:
        return "List files and directories in a given path. Useful for exploring the file system."
    
    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "directory_path": {
                    "type": "string",
                    "description": "Path to the directory to list (default: current directory)",
                    "default": "."
                },
                "show_hidden": {
                    "type": "boolean",
                    "description": "Include hidden files (starting with .) (default: false)",
                    "default": False
                }
            },
            "required": []
        }
    
    def execute(self, directory_path: str = ".", show_hidden: bool = False, **kwargs) -> Dict[str, Any]:
        """List files and directories."""
        try:
            if not os.path.exists(directory_path):
                return {
                    "success": False,
                    "error": f"Directory not found: {directory_path}",
                    "files": []
                }
            
            items = []
            for item in os.listdir(directory_path):
                if not show_hidden and item.startswith('.'):
                    continue
                
                item_path = os.path.join(directory_path, item)
                item_info = {
                    "name": item,
                    "path": item_path,
                    "type": "directory" if os.path.isdir(item_path) else "file"
                }
                
                if os.path.isfile(item_path):
                    item_info["size_bytes"] = os.path.getsize(item_path)
                
                items.append(item_info)
            
            return {
                "success": True,
                "directory_path": directory_path,
                "files": items,
                "total_items": len(items)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to list directory: {str(e)}",
                "files": []
            }
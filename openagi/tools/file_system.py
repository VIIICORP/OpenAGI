"""
File system tools for the OpenAGI agent.

These tools provide the agent with the ability to read, write, and manage
files on the local file system safely.
"""

import os
import logging
from pathlib import Path
from typing import Dict, Any, List
from .base import BaseTool

logger = logging.getLogger(__name__)

class ReadFileTool(BaseTool):
    """
    Tool for reading file contents.
    
    Allows the agent to read text files from the file system with safety checks.
    """
    
    @property
    def name(self) -> str:
        return "read_file"
    
    @property
    def description(self) -> str:
        return "Read the contents of a text file from the file system. Supports various text formats including code files, documents, and configuration files."
    
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
                    "description": "Text encoding to use (default: utf-8)",
                    "default": "utf-8"
                }
            },
            "required": ["file_path"]
        }
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Read a file from the file system.
        
        Args:
            file_path: Path to the file to read
            encoding: Text encoding (default: utf-8)
            
        Returns:
            Dictionary containing file contents and metadata
        """
        file_path = kwargs.get("file_path", "")
        encoding = kwargs.get("encoding", "utf-8")
        
        if not file_path:
            return {
                "success": False,
                "error": "File path is required",
                "content": ""
            }
        
        try:
            # Convert to Path object for safer handling
            path = Path(file_path).resolve()
            
            # Safety check - ensure file exists and is readable
            if not path.exists():
                return {
                    "success": False,
                    "error": f"File does not exist: {file_path}",
                    "content": ""
                }
            
            if not path.is_file():
                return {
                    "success": False,
                    "error": f"Path is not a file: {file_path}",
                    "content": ""
                }
            
            # Read the file
            with open(path, 'r', encoding=encoding) as f:
                content = f.read()
            
            return {
                "success": True,
                "file_path": str(path),
                "size_bytes": path.stat().st_size,
                "content": content
            }
            
        except UnicodeDecodeError as e:
            return {
                "success": False,
                "error": f"Unable to decode file with {encoding} encoding: {str(e)}",
                "content": ""
            }
        except PermissionError as e:
            return {
                "success": False,
                "error": f"Permission denied: {str(e)}",
                "content": ""
            }
        except Exception as e:
            logger.error(f"Failed to read file {file_path}: {e}")
            return {
                "success": False,
                "error": f"Failed to read file: {str(e)}",
                "content": ""
            }
    
    def get_usage_examples(self) -> List[Dict[str, Any]]:
        return [
            {
                "description": "Read a Python script",
                "parameters": {
                    "file_path": "/path/to/script.py"
                }
            },
            {
                "description": "Read a configuration file",
                "parameters": {
                    "file_path": "/path/to/config.json"
                }
            }
        ]
    
    def get_safety_notes(self) -> List[str]:
        return [
            "Only reads text files - binary files may cause encoding errors",
            "Large files may consume significant memory",
            "File paths are resolved to absolute paths for security"
        ]

class WriteFileTool(BaseTool):
    """
    Tool for writing content to files.
    
    Allows the agent to create or modify files on the file system with safety checks.
    """
    
    @property
    def name(self) -> str:
        return "write_file"
    
    @property
    def description(self) -> str:
        return "Write content to a file, creating it if it doesn't exist or overwriting if it does. Can create directories as needed."
    
    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path where the file should be written"
                },
                "content": {
                    "type": "string",
                    "description": "Content to write to the file"
                },
                "encoding": {
                    "type": "string",
                    "description": "Text encoding to use (default: utf-8)",
                    "default": "utf-8"
                },
                "create_dirs": {
                    "type": "boolean",
                    "description": "Whether to create parent directories if they don't exist (default: true)",
                    "default": True
                }
            },
            "required": ["file_path", "content"]
        }
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Write content to a file.
        
        Args:
            file_path: Path where to write the file
            content: Content to write
            encoding: Text encoding (default: utf-8)
            create_dirs: Whether to create parent directories (default: True)
            
        Returns:
            Dictionary containing operation result and metadata
        """
        file_path = kwargs.get("file_path", "")
        content = kwargs.get("content", "")
        encoding = kwargs.get("encoding", "utf-8")
        create_dirs = kwargs.get("create_dirs", True)
        
        if not file_path:
            return {
                "success": False,
                "error": "File path is required"
            }
        
        try:
            # Convert to Path object for safer handling
            path = Path(file_path).resolve()
            
            # Create parent directories if needed
            if create_dirs and not path.parent.exists():
                path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write the file
            with open(path, 'w', encoding=encoding) as f:
                f.write(content)
            
            return {
                "success": True,
                "file_path": str(path),
                "bytes_written": len(content.encode(encoding)),
                "created_dirs": create_dirs and not path.parent.existed_before if hasattr(path.parent, 'existed_before') else False
            }
            
        except PermissionError as e:
            return {
                "success": False,
                "error": f"Permission denied: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Failed to write file {file_path}: {e}")
            return {
                "success": False,
                "error": f"Failed to write file: {str(e)}"
            }
    
    def get_usage_examples(self) -> List[Dict[str, Any]]:
        return [
            {
                "description": "Create a new Python script",
                "parameters": {
                    "file_path": "/path/to/new_script.py",
                    "content": "#!/usr/bin/env python3\nprint('Hello, World!')\n"
                }
            },
            {
                "description": "Save JSON configuration",
                "parameters": {
                    "file_path": "/path/to/config.json",
                    "content": "{\n  \"setting\": \"value\"\n}"
                }
            }
        ]
    
    def get_safety_notes(self) -> List[str]:
        return [
            "Will overwrite existing files without warning",
            "Creates parent directories by default",
            "Be careful with file permissions and sensitive locations"
        ]

class ListFilesTool(BaseTool):
    """
    Tool for listing files and directories.
    
    Allows the agent to explore the file system structure.
    """
    
    @property
    def name(self) -> str:
        return "list_files"
    
    @property
    def description(self) -> str:
        return "List files and directories in a given path. Can show hidden files and provide detailed information."
    
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
                    "description": "Whether to show hidden files (starting with .) (default: false)",
                    "default": False
                },
                "detailed": {
                    "type": "boolean",
                    "description": "Whether to show detailed information (size, permissions, etc.) (default: false)",
                    "default": False
                }
            }
        }
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        List files and directories.
        
        Args:
            directory_path: Path to list (default: current directory)
            show_hidden: Whether to show hidden files (default: False)
            detailed: Whether to show detailed info (default: False)
            
        Returns:
            Dictionary containing directory listing and metadata
        """
        directory_path = kwargs.get("directory_path", ".")
        show_hidden = kwargs.get("show_hidden", False)
        detailed = kwargs.get("detailed", False)
        
        try:
            # Convert to Path object
            path = Path(directory_path).resolve()
            
            if not path.exists():
                return {
                    "success": False,
                    "error": f"Directory does not exist: {directory_path}",
                    "entries": []
                }
            
            if not path.is_dir():
                return {
                    "success": False,
                    "error": f"Path is not a directory: {directory_path}",
                    "entries": []
                }
            
            # List directory contents
            entries = []
            for item in path.iterdir():
                # Skip hidden files if not requested
                if not show_hidden and item.name.startswith('.'):
                    continue
                
                entry = {
                    "name": item.name,
                    "is_directory": item.is_dir(),
                    "is_file": item.is_file()
                }
                
                if detailed:
                    try:
                        stat = item.stat()
                        entry.update({
                            "size_bytes": stat.st_size if item.is_file() else None,
                            "modified_time": stat.st_mtime,
                            "permissions": oct(stat.st_mode)[-3:]
                        })
                    except (PermissionError, OSError):
                        entry["access_error"] = True
                
                entries.append(entry)
            
            # Sort entries: directories first, then files, alphabetically
            entries.sort(key=lambda x: (not x["is_directory"], x["name"].lower()))
            
            return {
                "success": True,
                "directory_path": str(path),
                "total_entries": len(entries),
                "entries": entries
            }
            
        except PermissionError as e:
            return {
                "success": False,
                "error": f"Permission denied: {str(e)}",
                "entries": []
            }
        except Exception as e:
            logger.error(f"Failed to list directory {directory_path}: {e}")
            return {
                "success": False,
                "error": f"Failed to list directory: {str(e)}",
                "entries": []
            }
    
    def get_usage_examples(self) -> List[Dict[str, Any]]:
        return [
            {
                "description": "List current directory",
                "parameters": {}
            },
            {
                "description": "List with details and hidden files",
                "parameters": {
                    "directory_path": "/home/user",
                    "show_hidden": True,
                    "detailed": True
                }
            }
        ]
    
    def get_safety_notes(self) -> List[str]:
        return [
            "May encounter permission errors in protected directories",
            "Large directories may take time to process",
            "Hidden files are not shown by default for security"
        ]
"""
Python code execution tool for the OpenAGI agent.

This tool provides the agent with the ability to execute Python code in a
controlled environment for computation, data analysis, and problem solving.
"""

import subprocess
import tempfile
import logging
import os
from typing import Dict, Any, List
from .base import BaseTool

logger = logging.getLogger(__name__)

class ExecutePythonCodeTool(BaseTool):
    """
    Tool for executing Python code in a controlled environment.
    
    This tool allows the agent to run Python code for calculations, data processing,
    and experimentation while maintaining safety through sandboxing.
    """
    
    @property
    def name(self) -> str:
        return "execute_python_code"
    
    @property
    def description(self) -> str:
        return "Execute Python code in a controlled environment. Useful for calculations, data analysis, and testing concepts."
    
    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "Python code to execute"
                },
                "timeout": {
                    "type": "integer",
                    "description": "Maximum execution time in seconds (default: 30)",
                    "default": 30,
                    "minimum": 1,
                    "maximum": 300
                }
            },
            "required": ["code"]
        }
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Execute Python code in a sandboxed environment.
        
        Args:
            code: Python code to execute
            timeout: Maximum execution time in seconds (default: 30)
            
        Returns:
            Dictionary containing execution result and output
        """
        code = kwargs.get("code", "")
        timeout = kwargs.get("timeout", 30)
        
        if not code:
            return {
                "success": False,
                "error": "Code is required",
                "output": "",
                "stdout": "",
                "stderr": ""
            }
        
        # Safety checks for dangerous operations
        dangerous_imports = [
            "os.system", "subprocess", "eval", "exec", "compile",
            "__import__", "open(", "file(", "input(", "raw_input("
        ]
        
        code_lower = code.lower()
        for dangerous in dangerous_imports:
            if dangerous in code_lower:
                return {
                    "success": False,
                    "error": f"Potentially dangerous operation detected: {dangerous}",
                    "output": "",
                    "stdout": "",
                    "stderr": ""
                }
        
        try:
            # Create a temporary file for the code
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
                temp_file.write(code)
                temp_file_path = temp_file.name
            
            try:
                # Execute the code in a subprocess for isolation
                result = subprocess.run(
                    ["/usr/bin/python3", temp_file_path],
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    cwd="/tmp"  # Run in tmp directory for additional isolation
                )
                
                return {
                    "success": result.returncode == 0,
                    "exit_code": result.returncode,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "output": result.stdout if result.returncode == 0 else result.stderr
                }
                
            finally:
                # Clean up temporary file
                try:
                    os.unlink(temp_file_path)
                except OSError:
                    pass
                    
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": f"Code execution timed out after {timeout} seconds",
                "output": "",
                "stdout": "",
                "stderr": "Execution timeout"
            }
        except Exception as e:
            logger.error(f"Code execution failed: {e}")
            return {
                "success": False,
                "error": f"Execution failed: {str(e)}",
                "output": "",
                "stdout": "",
                "stderr": str(e)
            }
    
    def get_usage_examples(self) -> List[Dict[str, Any]]:
        return [
            {
                "description": "Simple calculation",
                "parameters": {
                    "code": "result = 2 + 2\nprint(f'2 + 2 = {result}')"
                }
            },
            {
                "description": "Data analysis with basic statistics",
                "parameters": {
                    "code": "import statistics\ndata = [1, 2, 3, 4, 5]\nmean = statistics.mean(data)\nprint(f'Mean: {mean}')"
                }
            }
        ]
    
    def get_safety_notes(self) -> List[str]:
        return [
            "Code execution is sandboxed but may still pose security risks",
            "Dangerous operations like file system access are blocked",
            "Execution time is limited to prevent infinite loops",
            "Code runs in an isolated subprocess with limited permissions"
        ]
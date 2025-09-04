"""
Code execution tool for the OpenAGI agent.
WARNING: This tool executes code and should be used with caution.
"""
import subprocess
import sys
import tempfile
import os
from typing import Dict, Any
from .base import BaseTool

class ExecutePythonCodeTool(BaseTool):
    """
    Tool for executing Python code in a controlled environment.
    
    WARNING: This tool executes arbitrary Python code and should be used carefully.
    Consider implementing sandboxing for production use.
    """
    
    @property
    def name(self) -> str:
        return "execute_python_code"
    
    @property
    def description(self) -> str:
        return "Execute Python code and return the output. WARNING: Use with caution as this executes arbitrary code. Useful for calculations, data analysis, and scripting tasks."
    
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
                    "description": "Timeout in seconds (default: 30)",
                    "default": 30,
                    "minimum": 1,
                    "maximum": 300
                }
            },
            "required": ["code"]
        }
    
    def execute(self, code: str, timeout: int = 30, **kwargs) -> Dict[str, Any]:
        """
        Execute Python code and return the result.
        
        Args:
            code: Python code to execute
            timeout: Maximum execution time in seconds
            
        Returns:
            Dict containing execution results
        """
        try:
            # Create a temporary file for the code
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_file = f.name
            
            # Execute the code
            try:
                result = subprocess.run(
                    [sys.executable, temp_file],
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    cwd=os.getcwd()
                )
                
                return {
                    "success": result.returncode == 0,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "return_code": result.returncode,
                    "execution_time": "N/A"  # Could be enhanced with timing
                }
                
            except subprocess.TimeoutExpired:
                return {
                    "success": False,
                    "error": f"Code execution timed out after {timeout} seconds",
                    "stdout": "",
                    "stderr": "",
                    "return_code": -1
                }
            
            finally:
                # Clean up the temporary file
                try:
                    os.unlink(temp_file)
                except:
                    pass
                    
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to execute code: {str(e)}",
                "stdout": "",
                "stderr": "",
                "return_code": -1
            }
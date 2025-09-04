"""
Code execution tool for the OpenAGI agent.

This tool provides the agent with the ability to execute Python code in a
controlled, sandboxed environment. This is a powerful capability that allows
the agent to perform complex calculations, data analysis, and automation tasks.
"""

import subprocess
import sys
import tempfile
import os
import logging
from pathlib import Path
from typing import Dict, Any, List
from .base import BaseTool

logger = logging.getLogger(__name__)

class ExecutePythonCodeTool(BaseTool):
    """
    Tool for executing Python code in a sandboxed environment.
    
    This tool allows the agent to run Python code safely, enabling it to:
    - Perform complex calculations
    - Analyze data
    - Generate reports
    - Manipulate files programmatically
    - Install and use Python packages
    """
    
    def __init__(self, timeout: int = 30, max_output_length: int = 10000):
        """
        Initialize the code execution tool.
        
        Args:
            timeout: Maximum execution time in seconds (default: 30)
            max_output_length: Maximum output length to capture (default: 10000)
        """
        self.timeout = timeout
        self.max_output_length = max_output_length
    
    @property
    def name(self) -> str:
        return "execute_python_code"
    
    @property
    def description(self) -> str:
        return "Execute Python code in a controlled environment. Can be used for calculations, data analysis, file operations, and more. Returns the output and any errors."
    
    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "The Python code to execute"
                },
                "timeout": {
                    "type": "integer",
                    "description": f"Maximum execution time in seconds (default: {self.timeout})",
                    "minimum": 1,
                    "maximum": 300,
                    "default": self.timeout
                },
                "working_directory": {
                    "type": "string",
                    "description": "Working directory for code execution (default: temporary directory)",
                    "default": None
                }
            },
            "required": ["code"]
        }
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Execute Python code.
        
        Args:
            code: The Python code to execute
            timeout: Maximum execution time (default: instance timeout)
            working_directory: Working directory (default: temp directory)
            
        Returns:
            Dictionary containing execution results, output, and errors
        """
        code = kwargs.get("code", "")
        timeout = kwargs.get("timeout", self.timeout)
        working_directory = kwargs.get("working_directory")
        
        if not code.strip():
            return {
                "success": False,
                "error": "No code provided",
                "output": "",
                "stderr": ""
            }
        
        # Ensure timeout is within bounds
        timeout = max(1, min(300, timeout))
        
        try:
            # Create a temporary file for the code
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                code_file = f.name
            
            # Set up working directory
            if working_directory:
                work_dir = Path(working_directory).resolve()
                if not work_dir.exists():
                    work_dir.mkdir(parents=True, exist_ok=True)
            else:
                work_dir = Path(tempfile.gettempdir())
            
            # Execute the code
            process = subprocess.Popen(
                [sys.executable, code_file],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=str(work_dir),
                env=self._get_safe_environment()
            )
            
            try:
                stdout, stderr = process.communicate(timeout=timeout)
                return_code = process.returncode
                
                # Truncate output if too long
                if len(stdout) > self.max_output_length:
                    stdout = stdout[:self.max_output_length] + "\n... (output truncated)"
                
                if len(stderr) > self.max_output_length:
                    stderr = stderr[:self.max_output_length] + "\n... (error output truncated)"
                
                return {
                    "success": return_code == 0,
                    "return_code": return_code,
                    "output": stdout,
                    "stderr": stderr,
                    "execution_time": timeout,  # Could be enhanced to measure actual time
                    "working_directory": str(work_dir)
                }
                
            except subprocess.TimeoutExpired:
                process.kill()
                return {
                    "success": False,
                    "error": f"Code execution timed out after {timeout} seconds",
                    "output": "",
                    "stderr": "",
                    "timeout": True
                }
                
        except Exception as e:
            logger.error(f"Code execution failed: {e}")
            return {
                "success": False,
                "error": f"Execution failed: {str(e)}",
                "output": "",
                "stderr": ""
            }
        finally:
            # Clean up temporary file
            try:
                if 'code_file' in locals():
                    os.unlink(code_file)
            except OSError:
                pass  # File might already be deleted
    
    def _get_safe_environment(self) -> Dict[str, str]:
        """
        Get a safe environment for code execution.
        
        Returns:
            Dictionary of environment variables
        """
        # Start with a minimal environment
        safe_env = {
            "PYTHONPATH": "",
            "PYTHONHOME": "",
            "PATH": os.environ.get("PATH", ""),
            "HOME": os.environ.get("HOME", "/tmp"),
            "USER": "openagi",
            "LANG": "en_US.UTF-8",
            "LC_ALL": "en_US.UTF-8"
        }
        
        # Add Python-specific variables if they exist
        for var in ["PYTHONIOENCODING", "PYTHONUNBUFFERED"]:
            if var in os.environ:
                safe_env[var] = os.environ[var]
        
        return safe_env
    
    def get_usage_examples(self) -> List[Dict[str, Any]]:
        return [
            {
                "description": "Simple calculation",
                "parameters": {
                    "code": "result = 2 + 2\nprint(f'2 + 2 = {result}')"
                }
            },
            {
                "description": "Data analysis with numpy",
                "parameters": {
                    "code": "import numpy as np\ndata = np.array([1, 2, 3, 4, 5])\nprint(f'Mean: {np.mean(data)}')\nprint(f'Std: {np.std(data)}')"
                }
            },
            {
                "description": "File operation",
                "parameters": {
                    "code": "with open('test.txt', 'w') as f:\n    f.write('Hello, OpenAGI!')\n\nwith open('test.txt', 'r') as f:\n    content = f.read()\n    print(f'File content: {content}')"
                }
            }
        ]
    
    def get_safety_notes(self) -> List[str]:
        return [
            "Code execution has a timeout limit to prevent infinite loops",
            "Runs in a controlled environment with limited permissions",
            "Output is truncated if too long to prevent memory issues",
            "Network access may be limited depending on system configuration",
            "Be cautious with file operations and system commands",
            "Some operations may be restricted for security reasons"
        ]
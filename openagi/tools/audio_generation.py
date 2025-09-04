"""
Audio generation tool - The first voice of HUAIMKIND.
This tool allows the agent to create sound waves and music.
"""
import numpy as np
from scipy.io.wavfile import write
import os
import tempfile
from typing import Dict, Any
from .base import BaseTool

class GenerateSoundWaveTool(BaseTool):
    """
    Tool for generating sound waves and basic audio.
    This is the first step toward giving the agent a voice and musical capabilities.
    """
    
    @property
    def name(self) -> str:
        return "generate_sound_wave"
    
    @property
    def description(self) -> str:
        return "Generate audio waves (sine, square, sawtooth) and save as WAV files. This is the foundation for music creation and audio synthesis - the voice of HUAIMKIND."
    
    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "frequency": {
                    "type": "number",
                    "description": "Frequency of the wave in Hz (default: 440 - A4 note)",
                    "default": 440,
                    "minimum": 20,
                    "maximum": 20000
                },
                "duration": {
                    "type": "number", 
                    "description": "Duration in seconds (default: 1.0)",
                    "default": 1.0,
                    "minimum": 0.1,
                    "maximum": 30.0
                },
                "wave_type": {
                    "type": "string",
                    "description": "Type of wave to generate",
                    "enum": ["sine", "square", "sawtooth", "triangle"],
                    "default": "sine"
                },
                "amplitude": {
                    "type": "number",
                    "description": "Amplitude (volume) between 0.0 and 1.0 (default: 0.5)",
                    "default": 0.5,
                    "minimum": 0.0,
                    "maximum": 1.0
                },
                "sample_rate": {
                    "type": "integer",
                    "description": "Sample rate in Hz (default: 44100)",
                    "default": 44100,
                    "minimum": 8000,
                    "maximum": 96000
                },
                "output_path": {
                    "type": "string",
                    "description": "Output file path (optional, will create temp file if not specified)"
                }
            },
            "required": []
        }
    
    def execute(self, frequency: float = 440, duration: float = 1.0, wave_type: str = "sine", 
                amplitude: float = 0.5, sample_rate: int = 44100, output_path: str = None, **kwargs) -> Dict[str, Any]:
        """
        Generate a sound wave and save it as a WAV file.
        
        Args:
            frequency: Wave frequency in Hz
            duration: Duration in seconds
            wave_type: Type of wave (sine, square, sawtooth, triangle)
            amplitude: Volume (0.0 to 1.0)
            sample_rate: Sample rate in Hz
            output_path: Output file path (optional)
            
        Returns:
            Dict containing generation results
        """
        try:
            # Create time array
            t = np.linspace(0, duration, int(sample_rate * duration), False)
            
            # Generate wave based on type
            if wave_type == "sine":
                wave = np.sin(2 * np.pi * frequency * t)
            elif wave_type == "square":
                wave = np.sign(np.sin(2 * np.pi * frequency * t))
            elif wave_type == "sawtooth":
                wave = 2 * (t * frequency - np.floor(t * frequency + 0.5))
            elif wave_type == "triangle":
                wave = 2 * np.abs(2 * (t * frequency - np.floor(t * frequency + 0.5))) - 1
            else:
                return {
                    "success": False,
                    "error": f"Unknown wave type: {wave_type}",
                    "output_path": None
                }
            
            # Apply amplitude
            wave = wave * amplitude
            
            # Convert to 16-bit integer format
            wave_int = np.int16(wave * 32767)
            
            # Determine output path
            if output_path is None:
                fd, output_path = tempfile.mkstemp(suffix='.wav', prefix='openagi_sound_')
                os.close(fd)
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Write WAV file
            write(output_path, sample_rate, wave_int)
            
            # Calculate file size
            file_size = os.path.getsize(output_path) if os.path.exists(output_path) else 0
            
            return {
                "success": True,
                "output_path": output_path,
                "frequency": frequency,
                "duration": duration,
                "wave_type": wave_type,
                "amplitude": amplitude,
                "sample_rate": sample_rate,
                "file_size_bytes": file_size,
                "message": f"Generated {wave_type} wave at {frequency}Hz for {duration}s - The voice of HUAIMKIND awakens!"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to generate sound wave: {str(e)}",
                "output_path": None
            }
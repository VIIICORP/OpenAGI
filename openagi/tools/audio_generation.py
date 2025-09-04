"""
Audio generation tool for the OpenAGI agent.

This tool provides the agent with the ability to generate sound waves and
audio content for creative expression and communication.
"""

import numpy as np
import logging
import tempfile
import os
from typing import Dict, Any, List
from .base import BaseTool

logger = logging.getLogger(__name__)

try:
    import soundfile as sf
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False
    logger.warning("soundfile not available. Audio generation will be limited.")

class GenerateSoundWaveTool(BaseTool):
    """
    Tool for generating sound waves and basic audio content.
    
    This tool allows the agent to create audio for creative expression,
    musical composition, and sound design as part of the HUAIMKIND vision.
    """
    
    @property
    def name(self) -> str:
        return "generate_sound_wave"
    
    @property
    def description(self) -> str:
        return "Generate audio waveforms including tones, chords, and simple musical patterns. Supports creative audio expression and sound design."
    
    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "wave_type": {
                    "type": "string",
                    "enum": ["sine", "square", "triangle", "sawtooth", "noise"],
                    "description": "Type of waveform to generate",
                    "default": "sine"
                },
                "frequency": {
                    "type": "number",
                    "description": "Frequency of the tone in Hz (default: 440)",
                    "default": 440,
                    "minimum": 20,
                    "maximum": 20000
                },
                "duration": {
                    "type": "number",
                    "description": "Duration of the audio in seconds (default: 1.0)",
                    "default": 1.0,
                    "minimum": 0.1,
                    "maximum": 10.0
                },
                "amplitude": {
                    "type": "number",
                    "description": "Amplitude of the wave (0.0 to 1.0, default: 0.5)",
                    "default": 0.5,
                    "minimum": 0.0,
                    "maximum": 1.0
                },
                "sample_rate": {
                    "type": "integer",
                    "description": "Sample rate in Hz (default: 44100)",
                    "default": 44100,
                    "enum": [22050, 44100, 48000]
                },
                "output_file": {
                    "type": "string",
                    "description": "Optional output file path to save the audio"
                }
            }
        }
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Generate an audio waveform.
        
        Args:
            wave_type: Type of waveform (sine, square, triangle, sawtooth, noise)
            frequency: Frequency in Hz
            duration: Duration in seconds
            amplitude: Amplitude (0.0 to 1.0)
            sample_rate: Sample rate in Hz
            output_file: Optional file path to save audio
            
        Returns:
            Dictionary containing generation result and metadata
        """
        wave_type = kwargs.get("wave_type", "sine")
        frequency = kwargs.get("frequency", 440)
        duration = kwargs.get("duration", 1.0)
        amplitude = kwargs.get("amplitude", 0.5)
        sample_rate = kwargs.get("sample_rate", 44100)
        output_file = kwargs.get("output_file")
        
        try:
            # Calculate number of samples
            num_samples = int(sample_rate * duration)
            
            # Generate time array
            t = np.linspace(0, duration, num_samples, False)
            
            # Generate waveform based on type
            if wave_type == "sine":
                wave = np.sin(2 * np.pi * frequency * t)
            elif wave_type == "square":
                wave = np.sign(np.sin(2 * np.pi * frequency * t))
            elif wave_type == "triangle":
                wave = 2 * np.arcsin(np.sin(2 * np.pi * frequency * t)) / np.pi
            elif wave_type == "sawtooth":
                wave = 2 * (t * frequency - np.floor(t * frequency + 0.5))
            elif wave_type == "noise":
                wave = np.random.normal(0, 1, num_samples)
            else:
                return {
                    "success": False,
                    "error": f"Unknown wave type: {wave_type}"
                }
            
            # Apply amplitude
            wave = wave * amplitude
            
            # Ensure wave is in valid range
            wave = np.clip(wave, -1.0, 1.0)
            
            # Save to file if requested
            saved_file = None
            if output_file and AUDIO_AVAILABLE:
                try:
                    sf.write(output_file, wave, sample_rate)
                    saved_file = output_file
                except Exception as e:
                    logger.warning(f"Failed to save audio file: {e}")
            
            # Generate a temporary file for preview
            temp_file = None
            if AUDIO_AVAILABLE:
                try:
                    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tf:
                        sf.write(tf.name, wave, sample_rate)
                        temp_file = tf.name
                except Exception as e:
                    logger.warning(f"Failed to create temporary audio file: {e}")
            
            return {
                "success": True,
                "wave_type": wave_type,
                "frequency": frequency,
                "duration": duration,
                "amplitude": amplitude,
                "sample_rate": sample_rate,
                "num_samples": num_samples,
                "temp_file": temp_file,
                "saved_file": saved_file,
                "audio_data_shape": wave.shape,
                "audio_available": AUDIO_AVAILABLE
            }
            
        except Exception as e:
            logger.error(f"Audio generation failed: {e}")
            return {
                "success": False,
                "error": f"Audio generation failed: {str(e)}"
            }
    
    def generate_chord(self, frequencies: List[float], duration: float = 1.0, 
                      amplitude: float = 0.3, sample_rate: int = 44100) -> np.ndarray:
        """
        Generate a chord by combining multiple frequencies.
        
        Args:
            frequencies: List of frequencies to combine
            duration: Duration in seconds
            amplitude: Amplitude per frequency
            sample_rate: Sample rate in Hz
            
        Returns:
            Combined waveform as numpy array
        """
        num_samples = int(sample_rate * duration)
        t = np.linspace(0, duration, num_samples, False)
        
        # Start with silence
        chord = np.zeros(num_samples)
        
        # Add each frequency
        for freq in frequencies:
            wave = np.sin(2 * np.pi * freq * t) * amplitude
            chord += wave
        
        # Normalize to prevent clipping
        if len(frequencies) > 1:
            chord = chord / len(frequencies)
        
        return np.clip(chord, -1.0, 1.0)
    
    def get_usage_examples(self) -> List[Dict[str, Any]]:
        return [
            {
                "description": "Generate a simple A4 tone",
                "parameters": {
                    "wave_type": "sine",
                    "frequency": 440,
                    "duration": 2.0,
                    "amplitude": 0.5
                }
            },
            {
                "description": "Create a C major chord effect",
                "parameters": {
                    "wave_type": "sine",
                    "frequency": 261.63,  # C4
                    "duration": 3.0,
                    "amplitude": 0.3
                }
            },
            {
                "description": "Generate white noise",
                "parameters": {
                    "wave_type": "noise",
                    "duration": 1.0,
                    "amplitude": 0.2
                }
            }
        ]
    
    def get_safety_notes(self) -> List[str]:
        return [
            "Audio generation uses memory for wave data - large durations may consume significant RAM",
            "Generated audio may be loud - start with low amplitude values",
            "Some wave types (square, sawtooth) contain high frequencies that may be harsh",
            "Temporary files are created but may need manual cleanup"
        ]
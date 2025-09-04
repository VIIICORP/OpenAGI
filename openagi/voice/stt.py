"""
Speech-to-Text Engine for OpenAGI

Provides speech recognition capabilities using OpenAI Whisper for
hands-free interaction with the agent.
"""

import logging
from typing import Optional, Dict, Any
import tempfile
import os

logger = logging.getLogger(__name__)

try:
    import whisper
    import soundfile as sf
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
    logger.warning("Whisper dependencies not available. Speech recognition will be disabled.")

try:
    import pyaudio
    import numpy as np
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False
    logger.warning("Audio recording dependencies not available.")
    # Create dummy np for type hints
    class _DummyNumpy:
        ndarray = object
    np = _DummyNumpy()

class SpeechToTextEngine:
    """
    Speech-to-text engine using OpenAI Whisper.
    
    Provides both real-time microphone input and audio file transcription.
    """
    
    def __init__(self, model_name: str = "base"):
        """
        Initialize the STT engine.
        
        Args:
            model_name: Whisper model to use (tiny, base, small, medium, large)
        """
        self.model_name = model_name
        self.model = None
        self.is_available = WHISPER_AVAILABLE and AUDIO_AVAILABLE
        
        if self.is_available:
            self._load_model()
    
    def _load_model(self):
        """Load the Whisper model."""
        try:
            logger.info(f"Loading Whisper model: {self.model_name}")
            self.model = whisper.load_model(self.model_name)
            logger.info("Whisper model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            self.is_available = False
    
    def transcribe_file(self, audio_file_path: str) -> Dict[str, Any]:
        """
        Transcribe an audio file.
        
        Args:
            audio_file_path: Path to the audio file
            
        Returns:
            Dictionary containing transcription results
        """
        if not self.is_available or not self.model:
            return {
                "success": False,
                "error": "Speech recognition not available",
                "text": ""
            }
        
        try:
            logger.info(f"Transcribing audio file: {audio_file_path}")
            result = self.model.transcribe(audio_file_path)
            
            return {
                "success": True,
                "text": result["text"].strip(),
                "language": result.get("language", "unknown"),
                "confidence": getattr(result, "confidence", None)
            }
            
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            return {
                "success": False,
                "error": f"Transcription failed: {str(e)}",
                "text": ""
            }
    
    def transcribe_audio_data(self, audio_data: np.ndarray, sample_rate: int = 16000) -> Dict[str, Any]:
        """
        Transcribe audio data directly.
        
        Args:
            audio_data: Audio data as numpy array
            sample_rate: Sample rate of the audio
            
        Returns:
            Dictionary containing transcription results
        """
        if not self.is_available or not self.model:
            return {
                "success": False,
                "error": "Speech recognition not available",
                "text": ""
            }
        
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
                sf.write(tmp_file.name, audio_data, sample_rate)
                tmp_path = tmp_file.name
            
            # Transcribe the temporary file
            result = self.transcribe_file(tmp_path)
            
            # Clean up
            os.unlink(tmp_path)
            
            return result
            
        except Exception as e:
            logger.error(f"Audio data transcription failed: {e}")
            return {
                "success": False,
                "error": f"Audio transcription failed: {str(e)}",
                "text": ""
            }
    
    def record_and_transcribe(self, duration: float = 5.0, sample_rate: int = 16000) -> Dict[str, Any]:
        """
        Record audio from microphone and transcribe it.
        
        Args:
            duration: Recording duration in seconds
            sample_rate: Audio sample rate
            
        Returns:
            Dictionary containing transcription results
        """
        if not AUDIO_AVAILABLE:
            return {
                "success": False,
                "error": "Audio recording not available",
                "text": ""
            }
        
        try:
            logger.info(f"Recording audio for {duration} seconds...")
            
            # Initialize PyAudio
            audio = pyaudio.PyAudio()
            
            # Start recording
            stream = audio.open(
                format=pyaudio.paFloat32,
                channels=1,
                rate=sample_rate,
                input=True,
                frames_per_buffer=1024
            )
            
            frames = []
            for _ in range(0, int(sample_rate / 1024 * duration)):
                data = stream.read(1024)
                frames.append(np.frombuffer(data, dtype=np.float32))
            
            # Stop recording
            stream.stop_stream()
            stream.close()
            audio.terminate()
            
            # Convert to numpy array
            audio_data = np.concatenate(frames)
            
            logger.info("Recording complete, transcribing...")
            
            # Transcribe the recorded audio
            return self.transcribe_audio_data(audio_data, sample_rate)
            
        except Exception as e:
            logger.error(f"Recording and transcription failed: {e}")
            return {
                "success": False,
                "error": f"Recording failed: {str(e)}",
                "text": ""
            }
    
    def get_available_models(self) -> list:
        """
        Get list of available Whisper models.
        
        Returns:
            List of model names
        """
        return ["tiny", "base", "small", "medium", "large", "large-v2", "large-v3"]
    
    def is_ready(self) -> bool:
        """
        Check if the STT engine is ready.
        
        Returns:
            True if ready, False otherwise
        """
        return self.is_available and self.model is not None
"""
Speech-to-Text (STT) module for OpenAGI voice interface.

This module provides speech recognition capabilities using OpenAI Whisper
for hands-free interaction with the agent.
"""

import logging
import tempfile
import os
from typing import Dict, Any, Optional
import numpy as np

logger = logging.getLogger(__name__)

try:
    import whisper
    import torch
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
    logger.warning("Whisper not available. Speech recognition will be disabled.")

try:
    import pyaudio
    import wave
    AUDIO_RECORDING_AVAILABLE = True
except ImportError:
    AUDIO_RECORDING_AVAILABLE = False
    logger.warning("PyAudio not available. Live audio recording will be disabled.")

class SpeechToText:
    """
    Speech-to-Text system using OpenAI Whisper.
    
    Provides both file-based and real-time speech recognition capabilities
    for hands-free interaction with OpenAGI.
    """
    
    def __init__(self, model_size: str = "base"):
        """
        Initialize the STT system.
        
        Args:
            model_size: Whisper model size (tiny, base, small, medium, large)
        """
        self.model_size = model_size
        self.model = None
        self.is_recording = False
        
        if WHISPER_AVAILABLE:
            self._load_model()
        else:
            logger.error("Whisper not available - STT functionality disabled")
    
    def _load_model(self):
        """Load the Whisper model."""
        try:
            logger.info(f"Loading Whisper model: {self.model_size}")
            self.model = whisper.load_model(self.model_size)
            logger.info("Whisper model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            self.model = None
    
    def transcribe_file(self, audio_file_path: str, language: Optional[str] = None) -> Dict[str, Any]:
        """
        Transcribe audio from a file.
        
        Args:
            audio_file_path: Path to the audio file
            language: Optional language hint (e.g., 'en', 'es', 'fr')
            
        Returns:
            Dictionary containing transcription result
        """
        if not WHISPER_AVAILABLE or not self.model:
            return {
                "success": False,
                "error": "Whisper not available",
                "text": "",
                "confidence": 0.0
            }
        
        if not os.path.exists(audio_file_path):
            return {
                "success": False,
                "error": f"Audio file not found: {audio_file_path}",
                "text": "",
                "confidence": 0.0
            }
        
        try:
            # Transcribe the audio
            options = {}
            if language:
                options["language"] = language
            
            result = self.model.transcribe(audio_file_path, **options)
            
            return {
                "success": True,
                "text": result["text"].strip(),
                "language": result.get("language", "unknown"),
                "confidence": self._calculate_confidence(result),
                "segments": result.get("segments", []),
                "file_path": audio_file_path
            }
            
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "text": "",
                "confidence": 0.0
            }
    
    def transcribe_audio_data(self, audio_data: np.ndarray, sample_rate: int = 16000, 
                             language: Optional[str] = None) -> Dict[str, Any]:
        """
        Transcribe audio from numpy array data.
        
        Args:
            audio_data: Audio data as numpy array
            sample_rate: Sample rate of the audio
            language: Optional language hint
            
        Returns:
            Dictionary containing transcription result
        """
        if not WHISPER_AVAILABLE or not self.model:
            return {
                "success": False,
                "error": "Whisper not available",
                "text": "",
                "confidence": 0.0
            }
        
        try:
            # Create temporary file for the audio data
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                # Write audio data to temporary WAV file
                self._write_wav_file(tmp_file.name, audio_data, sample_rate)
                temp_path = tmp_file.name
            
            try:
                # Transcribe the temporary file
                result = self.transcribe_file(temp_path, language)
                return result
                
            finally:
                # Clean up temporary file
                try:
                    os.unlink(temp_path)
                except OSError:
                    pass
                    
        except Exception as e:
            logger.error(f"Audio data transcription failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "text": "",
                "confidence": 0.0
            }
    
    def start_recording(self, duration: float = 5.0, sample_rate: int = 16000) -> Dict[str, Any]:
        """
        Record audio from microphone and transcribe it.
        
        Args:
            duration: Recording duration in seconds
            sample_rate: Audio sample rate
            
        Returns:
            Dictionary containing recording and transcription result
        """
        if not AUDIO_RECORDING_AVAILABLE:
            return {
                "success": False,
                "error": "PyAudio not available for recording",
                "text": "",
                "confidence": 0.0
            }
        
        if not WHISPER_AVAILABLE or not self.model:
            return {
                "success": False,
                "error": "Whisper not available",
                "text": "",
                "confidence": 0.0
            }
        
        try:
            # Initialize PyAudio
            audio = pyaudio.PyAudio()
            
            # Recording parameters
            chunk = 1024
            format = pyaudio.paFloat32
            channels = 1
            
            # Start recording
            stream = audio.open(
                format=format,
                channels=channels,
                rate=sample_rate,
                input=True,
                frames_per_buffer=chunk
            )
            
            logger.info(f"Recording for {duration} seconds...")
            self.is_recording = True
            
            frames = []
            for _ in range(int(sample_rate / chunk * duration)):
                if not self.is_recording:
                    break
                data = stream.read(chunk)
                frames.append(data)
            
            # Stop recording
            stream.stop_stream()
            stream.close()
            audio.terminate()
            self.is_recording = False
            
            # Convert to numpy array
            audio_data = np.frombuffer(b''.join(frames), dtype=np.float32)
            
            # Transcribe the recorded audio
            result = self.transcribe_audio_data(audio_data, sample_rate)
            result["duration"] = duration
            result["sample_rate"] = sample_rate
            
            return result
            
        except Exception as e:
            logger.error(f"Recording failed: {e}")
            self.is_recording = False
            return {
                "success": False,
                "error": str(e),
                "text": "",
                "confidence": 0.0
            }
    
    def stop_recording(self):
        """Stop the current recording."""
        self.is_recording = False
    
    def _write_wav_file(self, filename: str, audio_data: np.ndarray, sample_rate: int):
        """Write audio data to a WAV file."""
        try:
            import soundfile as sf
            sf.write(filename, audio_data, sample_rate)
        except ImportError:
            # Fallback using wave module
            with wave.open(filename, 'wb') as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)  # 16-bit
                wav_file.setframerate(sample_rate)
                
                # Convert float32 to int16
                audio_int16 = (audio_data * 32767).astype(np.int16)
                wav_file.writeframes(audio_int16.tobytes())
    
    def _calculate_confidence(self, whisper_result: Dict) -> float:
        """
        Calculate confidence score from Whisper result.
        
        Args:
            whisper_result: Result from Whisper transcription
            
        Returns:
            Confidence score between 0.0 and 1.0
        """
        # Whisper doesn't provide direct confidence scores,
        # so we estimate based on segment properties
        segments = whisper_result.get("segments", [])
        
        if not segments:
            return 0.5  # Default moderate confidence
        
        # Average the "no_speech_prob" (inverted) as a proxy for confidence
        confidences = []
        for segment in segments:
            no_speech_prob = segment.get("no_speech_prob", 0.5)
            confidence = 1.0 - no_speech_prob
            confidences.append(confidence)
        
        return sum(confidences) / len(confidences) if confidences else 0.5
    
    def get_supported_languages(self) -> List[str]:
        """
        Get list of supported languages.
        
        Returns:
            List of language codes supported by Whisper
        """
        if not WHISPER_AVAILABLE:
            return []
        
        # Common languages supported by Whisper
        return [
            "en", "es", "fr", "de", "it", "pt", "ru", "ja", "ko", "zh",
            "ar", "tr", "pl", "nl", "sv", "da", "no", "fi", "el", "he",
            "hi", "th", "vi", "id", "ms", "uk", "cs", "hu", "bg", "hr"
        ]
    
    def is_available(self) -> bool:
        """Check if STT functionality is available."""
        return WHISPER_AVAILABLE and self.model is not None
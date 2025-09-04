"""
Text-to-Speech (TTS) module for OpenAGI voice interface.

This module provides text-to-speech capabilities using Coqui TTS
for natural voice output from the agent.
"""

import logging
import tempfile
import os
from typing import Dict, Any, Optional, List
import numpy as np

logger = logging.getLogger(__name__)

try:
    import TTS
    from TTS.api import TTS as CoquiTTS
    import torch
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False
    logger.warning("Coqui TTS not available. Speech synthesis will be disabled.")

try:
    import soundfile as sf
    import pyaudio
    AUDIO_PLAYBACK_AVAILABLE = True
except ImportError:
    AUDIO_PLAYBACK_AVAILABLE = False
    logger.warning("Audio playback libraries not available. Direct audio playback will be disabled.")

class TextToSpeech:
    """
    Text-to-Speech system using Coqui TTS.
    
    Provides natural voice synthesis capabilities for OpenAGI's
    voice interface, enabling the agent to speak its responses.
    """
    
    def __init__(self, model_name: Optional[str] = None, speaker: Optional[str] = None):
        """
        Initialize the TTS system.
        
        Args:
            model_name: Specific TTS model to use (default: auto-select best)
            speaker: Speaker voice to use if model supports multiple speakers
        """
        self.model_name = model_name
        self.speaker = speaker
        self.tts = None
        self.available_models = []
        
        if TTS_AVAILABLE:
            self._initialize_tts()
        else:
            logger.error("Coqui TTS not available - TTS functionality disabled")
    
    def _initialize_tts(self):
        """Initialize the TTS model."""
        try:
            # List available models
            self.available_models = CoquiTTS.list_models()
            logger.info(f"Available TTS models: {len(self.available_models)}")
            
            # Select model
            if not self.model_name:
                # Try to find a good English model
                english_models = [m for m in self.available_models if 'en' in m.lower()]
                if english_models:
                    self.model_name = english_models[0]
                else:
                    self.model_name = self.available_models[0] if self.available_models else None
            
            if self.model_name:
                logger.info(f"Loading TTS model: {self.model_name}")
                self.tts = CoquiTTS(model_name=self.model_name)
                logger.info("TTS model loaded successfully")
            else:
                logger.error("No TTS models available")
                
        except Exception as e:
            logger.error(f"Failed to initialize TTS: {e}")
            self.tts = None
    
    def synthesize_to_file(self, text: str, output_path: str, 
                          speaker: Optional[str] = None) -> Dict[str, Any]:
        """
        Synthesize text to speech and save to file.
        
        Args:
            text: Text to synthesize
            output_path: Path where to save the audio file
            speaker: Optional speaker voice override
            
        Returns:
            Dictionary containing synthesis result
        """
        if not TTS_AVAILABLE or not self.tts:
            return {
                "success": False,
                "error": "TTS not available",
                "file_path": "",
                "duration": 0.0
            }
        
        if not text.strip():
            return {
                "success": False,
                "error": "Empty text provided",
                "file_path": "",
                "duration": 0.0
            }
        
        try:
            # Use provided speaker or default
            speaker_voice = speaker or self.speaker
            
            # Synthesize speech
            if speaker_voice:
                self.tts.tts_to_file(text=text, file_path=output_path, speaker=speaker_voice)
            else:
                self.tts.tts_to_file(text=text, file_path=output_path)
            
            # Get audio duration
            duration = self._get_audio_duration(output_path)
            
            return {
                "success": True,
                "file_path": output_path,
                "text": text,
                "speaker": speaker_voice,
                "model": self.model_name,
                "duration": duration
            }
            
        except Exception as e:
            logger.error(f"TTS synthesis failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "file_path": "",
                "duration": 0.0
            }
    
    def synthesize_to_audio(self, text: str, speaker: Optional[str] = None) -> Dict[str, Any]:
        """
        Synthesize text to speech and return audio data.
        
        Args:
            text: Text to synthesize
            speaker: Optional speaker voice override
            
        Returns:
            Dictionary containing synthesis result with audio data
        """
        # Create temporary file
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
            temp_path = tmp_file.name
        
        try:
            # Synthesize to temporary file
            result = self.synthesize_to_file(text, temp_path, speaker)
            
            if result["success"]:
                # Load audio data
                if AUDIO_PLAYBACK_AVAILABLE:
                    audio_data, sample_rate = sf.read(temp_path)
                    result["audio_data"] = audio_data
                    result["sample_rate"] = sample_rate
                else:
                    result["audio_data"] = None
                    result["sample_rate"] = None
                    result["note"] = "Audio data not available - soundfile not installed"
            
            return result
            
        finally:
            # Clean up temporary file
            try:
                os.unlink(temp_path)
            except OSError:
                pass
    
    def speak(self, text: str, speaker: Optional[str] = None, 
             blocking: bool = True) -> Dict[str, Any]:
        """
        Synthesize and play text immediately.
        
        Args:
            text: Text to speak
            speaker: Optional speaker voice override
            blocking: Whether to wait for speech to complete
            
        Returns:
            Dictionary containing synthesis and playback result
        """
        if not AUDIO_PLAYBACK_AVAILABLE:
            return {
                "success": False,
                "error": "Audio playback not available",
                "text": text
            }
        
        # Synthesize audio
        synthesis_result = self.synthesize_to_audio(text, speaker)
        
        if not synthesis_result["success"]:
            return synthesis_result
        
        # Play audio
        try:
            audio_data = synthesis_result["audio_data"]
            sample_rate = synthesis_result["sample_rate"]
            
            if audio_data is not None:
                playback_result = self._play_audio(audio_data, sample_rate, blocking)
                synthesis_result.update(playback_result)
            else:
                synthesis_result["playback_error"] = "No audio data available"
            
            return synthesis_result
            
        except Exception as e:
            logger.error(f"Audio playback failed: {e}")
            synthesis_result["playback_error"] = str(e)
            return synthesis_result
    
    def _play_audio(self, audio_data: np.ndarray, sample_rate: int, 
                   blocking: bool = True) -> Dict[str, Any]:
        """
        Play audio data using PyAudio.
        
        Args:
            audio_data: Audio data as numpy array
            sample_rate: Sample rate of the audio
            blocking: Whether to wait for playback to complete
            
        Returns:
            Dictionary containing playback result
        """
        try:
            # Initialize PyAudio
            audio = pyaudio.PyAudio()
            
            # Convert to the right format for PyAudio
            if audio_data.dtype != np.float32:
                audio_data = audio_data.astype(np.float32)
            
            # Open stream
            stream = audio.open(
                format=pyaudio.paFloat32,
                channels=1 if len(audio_data.shape) == 1 else audio_data.shape[1],
                rate=sample_rate,
                output=True
            )
            
            # Play audio
            chunk_size = 1024
            for i in range(0, len(audio_data), chunk_size):
                chunk = audio_data[i:i + chunk_size]
                stream.write(chunk.tobytes())
            
            # Clean up
            stream.stop_stream()
            stream.close()
            audio.terminate()
            
            return {
                "playback_success": True,
                "playback_duration": len(audio_data) / sample_rate
            }
            
        except Exception as e:
            logger.error(f"Audio playback failed: {e}")
            return {
                "playback_success": False,
                "playback_error": str(e)
            }
    
    def _get_audio_duration(self, file_path: str) -> float:
        """
        Get duration of audio file in seconds.
        
        Args:
            file_path: Path to audio file
            
        Returns:
            Duration in seconds
        """
        try:
            if AUDIO_PLAYBACK_AVAILABLE:
                audio_data, sample_rate = sf.read(file_path)
                return len(audio_data) / sample_rate
            else:
                # Fallback: estimate based on file size (very rough)
                file_size = os.path.getsize(file_path)
                return file_size / 32000  # Rough estimate
        except Exception:
            return 0.0
    
    def get_available_speakers(self) -> List[str]:
        """
        Get list of available speakers for the current model.
        
        Returns:
            List of available speaker names
        """
        if not TTS_AVAILABLE or not self.tts:
            return []
        
        try:
            if hasattr(self.tts, 'speakers') and self.tts.speakers:
                return list(self.tts.speakers)
            else:
                return []
        except Exception as e:
            logger.error(f"Failed to get speakers: {e}")
            return []
    
    def get_available_models(self) -> List[str]:
        """
        Get list of available TTS models.
        
        Returns:
            List of model names
        """
        return self.available_models if TTS_AVAILABLE else []
    
    def change_model(self, model_name: str) -> bool:
        """
        Change the TTS model.
        
        Args:
            model_name: Name of the model to switch to
            
        Returns:
            True if successful, False otherwise
        """
        if not TTS_AVAILABLE:
            return False
        
        if model_name not in self.available_models:
            logger.error(f"Model {model_name} not available")
            return False
        
        try:
            logger.info(f"Switching to TTS model: {model_name}")
            self.model_name = model_name
            self.tts = CoquiTTS(model_name=model_name)
            logger.info("TTS model changed successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to change TTS model: {e}")
            return False
    
    def is_available(self) -> bool:
        """Check if TTS functionality is available."""
        return TTS_AVAILABLE and self.tts is not None
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the current model.
        
        Returns:
            Dictionary with model information
        """
        return {
            "model_name": self.model_name,
            "speaker": self.speaker,
            "available_speakers": self.get_available_speakers(),
            "tts_available": TTS_AVAILABLE,
            "playback_available": AUDIO_PLAYBACK_AVAILABLE,
            "model_loaded": self.tts is not None
        }
"""
Text-to-Speech Engine for OpenAGI

Provides speech synthesis capabilities for the agent to communicate
through voice output.
"""

import logging
import tempfile
import os
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)

try:
    from TTS.api import TTS
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False
    logger.warning("TTS (Coqui) not available. Text-to-speech will be disabled.")

try:
    import soundfile as sf
    import numpy as np
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False
    logger.warning("Audio dependencies not available.")
    # Create dummy modules for type hints
    class _DummyNumpy:
        ndarray = object
    np = _DummyNumpy()

class TextToSpeechEngine:
    """
    Text-to-speech engine using Coqui TTS.
    
    Provides high-quality speech synthesis with multiple voices and languages.
    """
    
    def __init__(self, model_name: Optional[str] = None):
        """
        Initialize the TTS engine.
        
        Args:
            model_name: TTS model to use (None for default)
        """
        self.model_name = model_name or "tts_models/en/ljspeech/tacotron2-DCA"
        self.tts = None
        self.is_available = TTS_AVAILABLE and AUDIO_AVAILABLE
        
        if self.is_available:
            self._load_model()
    
    def _load_model(self):
        """Load the TTS model."""
        try:
            logger.info(f"Loading TTS model: {self.model_name}")
            self.tts = TTS(model_name=self.model_name, progress_bar=False)
            logger.info("TTS model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load TTS model: {e}")
            self.is_available = False
    
    def synthesize_to_file(self, text: str, output_path: str, 
                          speaker: Optional[str] = None) -> Dict[str, Any]:
        """
        Synthesize speech and save to file.
        
        Args:
            text: Text to synthesize
            output_path: Output audio file path
            speaker: Speaker voice (if supported by model)
            
        Returns:
            Dictionary containing synthesis results
        """
        if not self.is_available or not self.tts:
            return {
                "success": False,
                "error": "Text-to-speech not available",
                "file_path": None
            }
        
        if not text.strip():
            return {
                "success": False,
                "error": "No text provided",
                "file_path": None
            }
        
        try:
            logger.info(f"Synthesizing speech: {text[:50]}...")
            
            # Synthesize speech
            if speaker and hasattr(self.tts, 'speakers') and self.tts.speakers:
                self.tts.tts_to_file(text=text, file_path=output_path, speaker=speaker)
            else:
                self.tts.tts_to_file(text=text, file_path=output_path)
            
            return {
                "success": True,
                "file_path": output_path,
                "text": text,
                "speaker": speaker
            }
            
        except Exception as e:
            logger.error(f"Speech synthesis failed: {e}")
            return {
                "success": False,
                "error": f"Synthesis failed: {str(e)}",
                "file_path": None
            }
    
    def synthesize_to_audio(self, text: str, 
                          speaker: Optional[str] = None) -> Dict[str, Any]:
        """
        Synthesize speech and return audio data.
        
        Args:
            text: Text to synthesize
            speaker: Speaker voice (if supported by model)
            
        Returns:
            Dictionary containing synthesis results and audio data
        """
        if not self.is_available or not self.tts:
            return {
                "success": False,
                "error": "Text-to-speech not available",
                "audio_data": None
            }
        
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
                tmp_path = tmp_file.name
            
            # Synthesize to temporary file
            result = self.synthesize_to_file(text, tmp_path, speaker)
            
            if result["success"]:
                # Read audio data
                audio_data, sample_rate = sf.read(tmp_path)
                
                # Clean up temporary file
                os.unlink(tmp_path)
                
                return {
                    "success": True,
                    "audio_data": audio_data,
                    "sample_rate": sample_rate,
                    "text": text,
                    "speaker": speaker
                }
            else:
                # Clean up temporary file
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
                return result
                
        except Exception as e:
            logger.error(f"Audio synthesis failed: {e}")
            return {
                "success": False,
                "error": f"Audio synthesis failed: {str(e)}",
                "audio_data": None
            }
    
    def synthesize_and_play(self, text: str, speaker: Optional[str] = None) -> Dict[str, Any]:
        """
        Synthesize speech and play it immediately.
        
        Args:
            text: Text to synthesize
            speaker: Speaker voice (if supported by model)
            
        Returns:
            Dictionary containing synthesis results
        """
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
                tmp_path = tmp_file.name
            
            # Synthesize to temporary file
            result = self.synthesize_to_file(text, tmp_path, speaker)
            
            if result["success"]:
                # Play the audio file (platform-dependent)
                self._play_audio_file(tmp_path)
                
                # Clean up after a delay
                import threading
                def cleanup():
                    import time
                    time.sleep(5)  # Wait for playback to complete
                    if os.path.exists(tmp_path):
                        os.unlink(tmp_path)
                
                threading.Thread(target=cleanup, daemon=True).start()
                
                return {
                    "success": True,
                    "text": text,
                    "speaker": speaker,
                    "played": True
                }
            else:
                # Clean up temporary file
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
                return result
                
        except Exception as e:
            logger.error(f"Playback synthesis failed: {e}")
            return {
                "success": False,
                "error": f"Playback failed: {str(e)}",
                "played": False
            }
    
    def _play_audio_file(self, file_path: str):
        """
        Play an audio file using system commands.
        
        Args:
            file_path: Path to audio file to play
        """
        import subprocess
        import platform
        
        try:
            system = platform.system().lower()
            
            if system == "windows":
                os.startfile(file_path)
            elif system == "darwin":  # macOS
                subprocess.run(["open", file_path], check=True)
            else:  # Linux and others
                # Try common audio players
                for player in ["aplay", "paplay", "play", "vlc"]:
                    try:
                        subprocess.run([player, file_path], check=True, 
                                     stdout=subprocess.DEVNULL, 
                                     stderr=subprocess.DEVNULL)
                        break
                    except (subprocess.CalledProcessError, FileNotFoundError):
                        continue
                else:
                    logger.warning("No suitable audio player found")
                    
        except Exception as e:
            logger.error(f"Failed to play audio: {e}")
    
    def get_available_speakers(self) -> List[str]:
        """
        Get list of available speakers for the current model.
        
        Returns:
            List of speaker names
        """
        if not self.is_available or not self.tts:
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
        if not TTS_AVAILABLE:
            return []
        
        try:
            return TTS.list_models()
        except Exception as e:
            logger.error(f"Failed to get models: {e}")
            return []
    
    def is_ready(self) -> bool:
        """
        Check if the TTS engine is ready.
        
        Returns:
            True if ready, False otherwise
        """
        return self.is_available and self.tts is not None
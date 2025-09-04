"""
Voice Interface for OpenAGI

Combines speech-to-text and text-to-speech for hands-free interaction
with the OpenAGI agent.
"""

import logging
import threading
import time
from typing import Optional, Dict, Any, Callable

from .stt import SpeechToTextEngine
from .tts import TextToSpeechEngine

logger = logging.getLogger(__name__)

class VoiceInterface:
    """
    Complete voice interface for OpenAGI.
    
    Provides hands-free interaction through speech recognition and synthesis.
    """
    
    def __init__(self, stt_model: str = "base", tts_model: Optional[str] = None):
        """
        Initialize the voice interface.
        
        Args:
            stt_model: Whisper model for speech recognition
            tts_model: TTS model for speech synthesis
        """
        self.stt_engine = SpeechToTextEngine(stt_model)
        self.tts_engine = TextToSpeechEngine(tts_model)
        
        self.listening = False
        self.speaking = False
        self.voice_activated = False
        
        # Callbacks
        self.on_speech_recognized: Optional[Callable[[str], None]] = None
        self.on_voice_command: Optional[Callable[[str], str]] = None
        
        logger.info(f"Voice interface initialized - STT: {self.stt_engine.is_ready()}, TTS: {self.tts_engine.is_ready()}")
    
    def set_speech_callback(self, callback: Callable[[str], None]):
        """
        Set callback for when speech is recognized.
        
        Args:
            callback: Function to call with recognized text
        """
        self.on_speech_recognized = callback
    
    def set_command_callback(self, callback: Callable[[str], str]):
        """
        Set callback for processing voice commands.
        
        Args:
            callback: Function that takes recognized text and returns response
        """
        self.on_voice_command = callback
    
    def start_listening(self, continuous: bool = False, duration: float = 5.0):
        """
        Start listening for speech input.
        
        Args:
            continuous: Whether to listen continuously
            duration: Duration for single listening session
        """
        if not self.stt_engine.is_ready():
            logger.error("STT engine not ready")
            return
        
        if self.listening:
            logger.warning("Already listening")
            return
        
        self.listening = True
        
        if continuous:
            self._start_continuous_listening()
        else:
            self._start_single_listening(duration)
    
    def stop_listening(self):
        """Stop listening for speech input."""
        self.listening = False
        logger.info("Stopped listening")
    
    def _start_continuous_listening(self):
        """Start continuous listening in a background thread."""
        def listen_loop():
            logger.info("Starting continuous listening...")
            
            while self.listening:
                try:
                    if not self.speaking:  # Don't listen while speaking
                        result = self.stt_engine.record_and_transcribe(duration=3.0)
                        
                        if result["success"] and result["text"].strip():
                            text = result["text"].strip()
                            logger.info(f"Recognized speech: {text}")
                            
                            # Process the recognized speech
                            self._handle_recognized_speech(text)
                    
                    time.sleep(0.5)  # Brief pause between listening sessions
                    
                except Exception as e:
                    logger.error(f"Continuous listening error: {e}")
                    time.sleep(1)  # Longer pause on error
            
            logger.info("Continuous listening stopped")
        
        thread = threading.Thread(target=listen_loop, daemon=True)
        thread.start()
    
    def _start_single_listening(self, duration: float):
        """Start single listening session in background thread."""
        def listen_once():
            logger.info(f"Listening for {duration} seconds...")
            
            try:
                result = self.stt_engine.record_and_transcribe(duration=duration)
                
                if result["success"] and result["text"].strip():
                    text = result["text"].strip()
                    logger.info(f"Recognized speech: {text}")
                    
                    # Process the recognized speech
                    self._handle_recognized_speech(text)
                else:
                    logger.info("No speech recognized or recognition failed")
                    
            except Exception as e:
                logger.error(f"Single listening error: {e}")
            finally:
                self.listening = False
        
        thread = threading.Thread(target=listen_once, daemon=True)
        thread.start()
    
    def _handle_recognized_speech(self, text: str):
        """
        Handle recognized speech text.
        
        Args:
            text: Recognized speech text
        """
        # Call speech recognition callback
        if self.on_speech_recognized:
            try:
                self.on_speech_recognized(text)
            except Exception as e:
                logger.error(f"Speech callback error: {e}")
        
        # Process as voice command if callback is set
        if self.on_voice_command:
            try:
                response = self.on_voice_command(text)
                if response:
                    self.speak(response)
            except Exception as e:
                logger.error(f"Voice command callback error: {e}")
    
    def speak(self, text: str, speaker: Optional[str] = None, 
             wait_for_completion: bool = False) -> Dict[str, Any]:
        """
        Speak the given text.
        
        Args:
            text: Text to speak
            speaker: Speaker voice to use
            wait_for_completion: Whether to wait for speech to complete
            
        Returns:
            Dictionary containing speech synthesis results
        """
        if not self.tts_engine.is_ready():
            logger.error("TTS engine not ready")
            return {"success": False, "error": "TTS not available"}
        
        if self.speaking and not wait_for_completion:
            logger.warning("Already speaking, skipping")
            return {"success": False, "error": "Already speaking"}
        
        try:
            self.speaking = True
            logger.info(f"Speaking: {text[:50]}...")
            
            if wait_for_completion:
                result = self.tts_engine.synthesize_and_play(text, speaker)
            else:
                # Speak in background thread
                def speak_async():
                    try:
                        self.tts_engine.synthesize_and_play(text, speaker)
                    finally:
                        self.speaking = False
                
                thread = threading.Thread(target=speak_async, daemon=True)
                thread.start()
                
                result = {"success": True, "text": text, "async": True}
            
            return result
            
        except Exception as e:
            logger.error(f"Speech error: {e}")
            self.speaking = False
            return {"success": False, "error": str(e)}
    
    def transcribe_file(self, audio_file_path: str) -> Dict[str, Any]:
        """
        Transcribe an audio file.
        
        Args:
            audio_file_path: Path to audio file
            
        Returns:
            Transcription results
        """
        return self.stt_engine.transcribe_file(audio_file_path)
    
    def synthesize_to_file(self, text: str, output_path: str, 
                          speaker: Optional[str] = None) -> Dict[str, Any]:
        """
        Synthesize speech to an audio file.
        
        Args:
            text: Text to synthesize
            output_path: Output file path
            speaker: Speaker voice to use
            
        Returns:
            Synthesis results
        """
        return self.tts_engine.synthesize_to_file(text, output_path, speaker)
    
    def get_capabilities(self) -> Dict[str, Any]:
        """
        Get voice interface capabilities.
        
        Returns:
            Dictionary of capabilities
        """
        return {
            "stt_available": self.stt_engine.is_ready(),
            "tts_available": self.tts_engine.is_ready(),
            "stt_models": self.stt_engine.get_available_models(),
            "tts_models": self.tts_engine.get_available_models(),
            "tts_speakers": self.tts_engine.get_available_speakers(),
            "currently_listening": self.listening,
            "currently_speaking": self.speaking
        }
    
    def enable_voice_activation(self, wake_words: list = None):
        """
        Enable voice activation with wake words.
        
        Args:
            wake_words: List of wake words (default: ["hey openagi", "openagi"])
        """
        if wake_words is None:
            wake_words = ["hey openagi", "openagi", "hey agi"]
        
        self.voice_activated = True
        self.wake_words = [word.lower() for word in wake_words]
        
        logger.info(f"Voice activation enabled with wake words: {wake_words}")
    
    def disable_voice_activation(self):
        """Disable voice activation."""
        self.voice_activated = False
        logger.info("Voice activation disabled")
    
    def _check_wake_word(self, text: str) -> bool:
        """
        Check if text contains a wake word.
        
        Args:
            text: Text to check
            
        Returns:
            True if wake word detected
        """
        if not self.voice_activated:
            return True  # Always active if voice activation is disabled
        
        text_lower = text.lower()
        return any(wake_word in text_lower for wake_word in self.wake_words)
    
    def is_ready(self) -> bool:
        """
        Check if voice interface is ready for use.
        
        Returns:
            True if at least one engine is ready
        """
        return self.stt_engine.is_ready() or self.tts_engine.is_ready()
"""
Voice interface for OpenAGI - hands-free interaction module.

This module combines STT and TTS capabilities to provide a complete
voice interface for natural conversation with the agent.
"""

import logging
import asyncio
from typing import Dict, Any, Optional, Callable
from .stt import SpeechToText
from .tts import TextToSpeech

logger = logging.getLogger(__name__)

class VoiceInterface:
    """
    Complete voice interface for OpenAGI providing hands-free interaction.
    
    Combines speech recognition and synthesis for natural conversation
    with the agent, supporting the HUAIMKIND vision of seamless
    human-AI communication.
    """
    
    def __init__(self, stt_model: str = "base", tts_model: Optional[str] = None):
        """
        Initialize the voice interface.
        
        Args:
            stt_model: Whisper model size for speech recognition
            tts_model: TTS model name for speech synthesis
        """
        self.stt = SpeechToText(model_size=stt_model)
        self.tts = TextToSpeech(model_name=tts_model)
        
        # Voice interface state
        self.is_listening = False
        self.is_speaking = False
        self.conversation_active = False
        
        # Configuration
        self.voice_activation_threshold = 0.5
        self.silence_timeout = 3.0  # Seconds of silence before stopping listening
        self.max_recording_duration = 30.0  # Maximum recording length
        
        # Conversation callbacks
        self.on_speech_recognized = None
        self.on_response_ready = None
        self.on_conversation_started = None
        self.on_conversation_ended = None
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current voice interface status.
        
        Returns:
            Dictionary containing status information
        """
        return {
            "conversation_active": self.conversation_active,
            "is_listening": self.is_listening,
            "is_speaking": self.is_speaking,
            "stt_available": self.stt.is_available(),
            "tts_available": self.tts.is_available(),
            "stt_model": self.stt.model_size if self.stt else None,
            "tts_model": self.tts.model_name if self.tts else None,
        }

# Package exports
from .stt import SpeechToText
from .tts import TextToSpeech

__all__ = ["SpeechToText", "TextToSpeech", "VoiceInterface"]
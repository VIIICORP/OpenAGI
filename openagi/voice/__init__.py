"""
OpenAGI Voice Interface

This package provides speech-to-text (STT) and text-to-speech (TTS) capabilities
for hands-free interaction with the OpenAGI agent.
"""

from .stt import SpeechToTextEngine
from .tts import TextToSpeechEngine
from .voice_interface import VoiceInterface

__all__ = ["SpeechToTextEngine", "TextToSpeechEngine", "VoiceInterface"]
"""
OpenAGI Voice Interface

This package provides complete voice interface capabilities for OpenAGI,
including speech-to-text (STT) and text-to-speech (TTS) functionality.
"""

from .stt import SpeechToText
from .tts import TextToSpeech
from .voice_interface import VoiceInterface

__all__ = ["SpeechToText", "TextToSpeech", "VoiceInterface"]
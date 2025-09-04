"""
Audio generation tool for the OpenAGI agent.

This tool provides the agent with the ability to generate sound waves and music,
representing the first step toward creative expression and the language of
HUAIMKIND through sound.
"""

import os
import math
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from .base import BaseTool

logger = logging.getLogger(__name__)

try:
    import numpy as np
    import scipy.io.wavfile as wavfile
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False
    logger.warning("Audio dependencies not available. Audio generation will be disabled.")

class GenerateSoundWaveTool(BaseTool):
    """
    Tool for generating sound waves and basic music.
    
    This tool allows the agent to create audio content, from simple tones
    to more complex musical compositions. It represents the agent's first
    step into creative expression through sound.
    """
    
    @property
    def name(self) -> str:
        return "generate_sound_wave"
    
    @property
    def description(self) -> str:
        return "Generate sound waves and basic music. Can create sine, square, sawtooth, and triangle waves at specified frequencies. Supports creating simple melodies and chord progressions."
    
    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "frequency": {
                    "type": "number",
                    "description": "Frequency of the sound in Hz (default: 440 Hz - A note)",
                    "minimum": 20,
                    "maximum": 20000,
                    "default": 440
                },
                "duration": {
                    "type": "number",
                    "description": "Duration of the sound in seconds (default: 1.0)",
                    "minimum": 0.1,
                    "maximum": 30.0,
                    "default": 1.0
                },
                "wave_type": {
                    "type": "string",
                    "description": "Type of wave to generate",
                    "enum": ["sine", "square", "sawtooth", "triangle"],
                    "default": "sine"
                },
                "amplitude": {
                    "type": "number",
                    "description": "Amplitude of the wave (0.0 to 1.0, default: 0.5)",
                    "minimum": 0.0,
                    "maximum": 1.0,
                    "default": 0.5
                },
                "sample_rate": {
                    "type": "integer",
                    "description": "Sample rate in Hz (default: 44100)",
                    "enum": [22050, 44100, 48000],
                    "default": 44100
                },
                "output_file": {
                    "type": "string",
                    "description": "Output file path (default: generates unique filename)",
                    "default": None
                },
                "notes": {
                    "type": "array",
                    "description": "Array of notes to play in sequence. Each note is [frequency, duration]",
                    "items": {
                        "type": "array",
                        "items": {"type": "number"},
                        "minItems": 2,
                        "maxItems": 2
                    }
                }
            }
        }
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Generate a sound wave or melody.
        
        Args:
            frequency: Sound frequency in Hz (default: 440)
            duration: Duration in seconds (default: 1.0)
            wave_type: Type of wave (sine, square, sawtooth, triangle)
            amplitude: Wave amplitude (0.0 to 1.0, default: 0.5)
            sample_rate: Sample rate in Hz (default: 44100)
            output_file: Output file path (optional)
            notes: Array of [frequency, duration] pairs for melodies
            
        Returns:
            Dictionary containing generation results and file information
        """
        if not AUDIO_AVAILABLE:
            return {
                "success": False,
                "error": "Audio generation is not available. Required libraries (numpy, scipy) not installed.",
                "file_path": None
            }
        
        # Get parameters with defaults
        frequency = kwargs.get("frequency", 440)
        duration = kwargs.get("duration", 1.0)
        wave_type = kwargs.get("wave_type", "sine")
        amplitude = kwargs.get("amplitude", 0.5)
        sample_rate = kwargs.get("sample_rate", 44100)
        output_file = kwargs.get("output_file")
        notes = kwargs.get("notes")
        
        # Validate parameters
        frequency = max(20, min(20000, frequency))
        duration = max(0.1, min(30.0, duration))
        amplitude = max(0.0, min(1.0, amplitude))
        
        try:
            if notes:
                # Generate melody from notes
                audio_data = self._generate_melody(notes, wave_type, amplitude, sample_rate)
                total_duration = sum(note[1] for note in notes)
            else:
                # Generate single tone
                audio_data = self._generate_wave(frequency, duration, wave_type, amplitude, sample_rate)
                total_duration = duration
            
            # Generate output filename if not provided
            if not output_file:
                output_file = f"openagi_sound_{int(frequency)}hz_{wave_type}.wav"
            
            # Ensure output directory exists
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save the audio file
            # Convert to 16-bit integer format
            audio_int16 = (audio_data * 32767).astype(np.int16)
            wavfile.write(str(output_path), sample_rate, audio_int16)
            
            return {
                "success": True,
                "file_path": str(output_path.resolve()),
                "duration": total_duration,
                "frequency": frequency if not notes else "melody",
                "wave_type": wave_type,
                "sample_rate": sample_rate,
                "file_size_bytes": output_path.stat().st_size,
                "notes_count": len(notes) if notes else 1
            }
            
        except Exception as e:
            logger.error(f"Audio generation failed: {e}")
            return {
                "success": False,
                "error": f"Audio generation failed: {str(e)}",
                "file_path": None
            }
    
    def _generate_wave(self, frequency: float, duration: float, wave_type: str, 
                      amplitude: float, sample_rate: int) -> np.ndarray:
        """
        Generate a single wave of the specified type.
        
        Args:
            frequency: Wave frequency
            duration: Wave duration
            wave_type: Type of wave to generate
            amplitude: Wave amplitude
            sample_rate: Audio sample rate
            
        Returns:
            NumPy array containing the audio samples
        """
        # Generate time array
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        
        # Generate wave based on type
        if wave_type == "sine":
            wave = amplitude * np.sin(2 * np.pi * frequency * t)
        elif wave_type == "square":
            wave = amplitude * np.sign(np.sin(2 * np.pi * frequency * t))
        elif wave_type == "sawtooth":
            wave = amplitude * (2 * (t * frequency - np.floor(t * frequency + 0.5)))
        elif wave_type == "triangle":
            wave = amplitude * (2 * np.abs(2 * (t * frequency - np.floor(t * frequency + 0.5))) - 1)
        else:
            # Default to sine wave
            wave = amplitude * np.sin(2 * np.pi * frequency * t)
        
        # Apply fade in/out to avoid clicks
        fade_samples = int(0.01 * sample_rate)  # 10ms fade
        if len(wave) > 2 * fade_samples:
            # Fade in
            wave[:fade_samples] *= np.linspace(0, 1, fade_samples)
            # Fade out
            wave[-fade_samples:] *= np.linspace(1, 0, fade_samples)
        
        return wave
    
    def _generate_melody(self, notes: List[List[float]], wave_type: str, 
                        amplitude: float, sample_rate: int) -> np.ndarray:
        """
        Generate a melody from a sequence of notes.
        
        Args:
            notes: List of [frequency, duration] pairs
            wave_type: Type of wave to generate
            amplitude: Wave amplitude
            sample_rate: Audio sample rate
            
        Returns:
            NumPy array containing the complete melody
        """
        melody_parts = []
        
        for frequency, duration in notes:
            # Validate note parameters
            frequency = max(20, min(20000, frequency))
            duration = max(0.05, min(10.0, duration))
            
            # Generate this note
            note_wave = self._generate_wave(frequency, duration, wave_type, amplitude, sample_rate)
            melody_parts.append(note_wave)
            
            # Add a small gap between notes
            gap_duration = 0.02  # 20ms gap
            gap_samples = int(gap_duration * sample_rate)
            gap = np.zeros(gap_samples)
            melody_parts.append(gap)
        
        # Concatenate all parts
        return np.concatenate(melody_parts)
    
    def get_usage_examples(self) -> List[Dict[str, Any]]:
        return [
            {
                "description": "Generate a simple A note (440 Hz)",
                "parameters": {
                    "frequency": 440,
                    "duration": 2.0,
                    "wave_type": "sine"
                }
            },
            {
                "description": "Create a C major chord progression",
                "parameters": {
                    "notes": [
                        [261.63, 0.5],  # C
                        [329.63, 0.5],  # E
                        [392.00, 0.5],  # G
                        [523.25, 1.0]   # C octave
                    ],
                    "wave_type": "sine",
                    "output_file": "c_major_progression.wav"
                }
            },
            {
                "description": "Generate a square wave alarm sound",
                "parameters": {
                    "frequency": 800,
                    "duration": 0.5,
                    "wave_type": "square",
                    "amplitude": 0.8
                }
            }
        ]
    
    def get_safety_notes(self) -> List[str]:
        return [
            "Audio files are saved as WAV format at specified sample rate",
            "Large durations or complex melodies may create large files",
            "High frequencies or amplitudes may be uncomfortable with headphones",
            "Files are saved to the current working directory unless path specified",
            "Fade in/out is applied automatically to prevent audio clicks"
        ]

# Additional helper functions for musical notes
def get_note_frequency(note: str, octave: int = 4) -> float:
    """
    Get the frequency of a musical note.
    
    Args:
        note: Note name (C, C#, D, D#, E, F, F#, G, G#, A, A#, B)
        octave: Octave number (default: 4)
        
    Returns:
        Frequency in Hz
    """
    # Frequency of A4 is 440 Hz
    A4 = 440.0
    
    # Note offsets from A (in semitones)
    note_offsets = {
        'C': -9, 'C#': -8, 'DB': -8,
        'D': -7, 'D#': -6, 'EB': -6,
        'E': -5,
        'F': -4, 'F#': -3, 'GB': -3,
        'G': -2, 'G#': -1, 'AB': -1,
        'A': 0, 'A#': 1, 'BB': 1,
        'B': 2
    }
    
    if note.upper() not in note_offsets:
        raise ValueError(f"Unknown note: {note}")
    
    # Calculate frequency
    semitone_offset = note_offsets[note.upper()] + (octave - 4) * 12
    frequency = A4 * (2 ** (semitone_offset / 12))
    
    return frequency

class MusicalSoundWaveTool(GenerateSoundWaveTool):
    """
    Enhanced version of the sound wave tool with musical notation support.
    """
    
    @property
    def name(self) -> str:
        return "generate_musical_sound"
    
    @property
    def description(self) -> str:
        return "Generate musical sounds using note names (C, D, E, etc.) with octave numbers. Can create melodies, chords, and musical compositions."
    
    @property
    def parameters(self) -> Dict[str, Any]:
        base_params = super().parameters
        
        # Add musical notation parameters
        base_params["properties"]["note"] = {
            "type": "string",
            "description": "Musical note name (C, C#, D, D#, E, F, F#, G, G#, A, A#, B)",
            "pattern": "^[A-G](#|b)?$"
        }
        base_params["properties"]["octave"] = {
            "type": "integer",
            "description": "Octave number (0-8, default: 4)",
            "minimum": 0,
            "maximum": 8,
            "default": 4
        }
        base_params["properties"]["musical_notes"] = {
            "type": "array",
            "description": "Array of musical notes. Each note is [note_name, octave, duration]",
            "items": {
                "type": "array",
                "items": [{"type": "string"}, {"type": "integer"}, {"type": "number"}],
                "minItems": 3,
                "maxItems": 3
            }
        }
        
        return base_params
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute with musical notation support."""
        # Convert musical notation to frequencies
        if "note" in kwargs and "octave" in kwargs:
            note = kwargs.get("note", "A")
            octave = kwargs.get("octave", 4)
            try:
                kwargs["frequency"] = get_note_frequency(note, octave)
            except ValueError as e:
                return {
                    "success": False,
                    "error": f"Invalid note: {str(e)}",
                    "file_path": None
                }
        
        if "musical_notes" in kwargs:
            musical_notes = kwargs.get("musical_notes", [])
            try:
                # Convert musical notes to frequency/duration pairs
                frequency_notes = []
                for note, octave, duration in musical_notes:
                    freq = get_note_frequency(note, octave)
                    frequency_notes.append([freq, duration])
                kwargs["notes"] = frequency_notes
            except (ValueError, TypeError) as e:
                return {
                    "success": False,
                    "error": f"Invalid musical notation: {str(e)}",
                    "file_path": None
                }
        
        return super().execute(**kwargs)
"""
Voice Service - Handles text-to-speech announcements.
Uses edge-tts for natural-sounding female voice.
"""
import asyncio
import tempfile
import threading
from pathlib import Path
from typing import Optional
import os

try:
    import edge_tts
    EDGE_TTS_AVAILABLE = True
except ImportError:
    EDGE_TTS_AVAILABLE = False

try:
    import pygame
    pygame.mixer.init()
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False

from config import VOICE_NAME, VOICE_RATE


class VoiceService:
    """Handles text-to-speech announcements."""
    
    def __init__(self):
        """Initialize voice service."""
        self.voice = VOICE_NAME
        self.rate = VOICE_RATE
        self._is_speaking = False
        self._current_audio_file: Optional[Path] = None
    
    async def _generate_speech_async(self, text: str, output_path: str) -> bool:
        """Generate speech audio file asynchronously."""
        if not EDGE_TTS_AVAILABLE:
            print("Warning: edge-tts not available")
            return False
        
        try:
            communicate = edge_tts.Communicate(text, self.voice, rate=self.rate)
            await communicate.save(output_path)
            return True
        except Exception as e:
            print(f"Error generating speech: {e}")
            return False
    
    def generate_speech(self, text: str, output_path: str) -> bool:
        """Generate speech audio file synchronously."""
        return asyncio.run(self._generate_speech_async(text, output_path))
    
    def speak(self, text: str, blocking: bool = False):
        """
        Speak the given text.
        If blocking=True, wait for speech to complete.
        """
        if blocking:
            self._speak_sync(text)
        else:
            thread = threading.Thread(target=self._speak_sync, args=(text,))
            thread.daemon = True
            thread.start()
    
    def _speak_sync(self, text: str):
        """Synchronously generate and play speech."""
        if self._is_speaking:
            return
        
        self._is_speaking = True
        
        try:
            # Create temp file for audio
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f:
                temp_path = f.name
            
            # Generate speech
            if self.generate_speech(text, temp_path):
                self._play_audio(temp_path)
            
            # Cleanup
            if os.path.exists(temp_path):
                os.unlink(temp_path)
                
        except Exception as e:
            print(f"Error in speech: {e}")
        finally:
            self._is_speaking = False
    
    def _play_audio(self, audio_path: str):
        """Play audio file using pygame."""
        if not PYGAME_AVAILABLE:
            print(f"Warning: pygame not available, cannot play {audio_path}")
            return
        
        try:
            pygame.mixer.music.load(audio_path)
            pygame.mixer.music.play()
            
            # Wait for playback to finish
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
                
        except Exception as e:
            print(f"Error playing audio: {e}")
    
    def stop(self):
        """Stop current speech."""
        if PYGAME_AVAILABLE:
            pygame.mixer.music.stop()
        self._is_speaking = False
    
    def generate_boarding_announcement(
        self,
        passenger_name: str,
        seat: str,
        gate: str,
        flight_time: str
    ) -> str:
        """Generate boarding pass announcement text."""
        return (
            f"Attention passenger {passenger_name}. "
            f"Your boarding pass is ready. "
            f"Please proceed to Gate {gate} for your flight departing at {flight_time}. "
            f"Your seat number is {seat}. "
            f"Have a pleasant flight."
        )
    
    def announce_boarding(
        self,
        passenger_name: str,
        seat: str,
        gate: str,
        flight_time: str,
        blocking: bool = False
    ):
        """Make boarding announcement for passenger."""
        def _announce():
            # Play airport chime first
            self._play_airport_chime()
            
            # Then speak the announcement
            text = self.generate_boarding_announcement(
                passenger_name, seat, gate, flight_time
            )
            self._speak_sync(text)
        
        if blocking:
            _announce()
        else:
            thread = threading.Thread(target=_announce)
            thread.daemon = True
            thread.start()
    
    def _play_airport_chime(self):
        """Play airport chime sound before announcement."""
        if not PYGAME_AVAILABLE:
            return
        
        try:
            from config import SOUNDS_DIR
            chime_path = SOUNDS_DIR / "airportsound.mp3"
            
            if chime_path.exists():
                pygame.mixer.music.load(str(chime_path))
                pygame.mixer.music.play()
                
                # Wait for chime to finish
                while pygame.mixer.music.get_busy():
                    pygame.time.Clock().tick(10)
        except Exception as e:
            print(f"Error playing airport chime: {e}")
    
    @property
    def is_speaking(self) -> bool:
        """Check if currently speaking."""
        return self._is_speaking


# Global voice service instance
voice_service = VoiceService()

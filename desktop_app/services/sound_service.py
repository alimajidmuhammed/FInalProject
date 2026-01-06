"""
Sound Service - Audio feedback for the Flight Kiosk System.
Uses pygame for sound playback.
"""
import pygame
import numpy as np
from pathlib import Path
from typing import Optional

from config import SOUNDS_DIR, SOUND_ENABLED


class SoundService:
    """Manages audio feedback for the kiosk."""
    
    def __init__(self):
        """Initialize the sound service."""
        self.enabled = SOUND_ENABLED
        self._initialized = False
        self._sounds = {}
        
        self._init_pygame()
        self._generate_sounds()
    
    def _init_pygame(self):
        """Initialize pygame mixer."""
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            self._initialized = True
        except Exception as e:
            print(f"Warning: Could not initialize sound: {e}")
            self._initialized = False
    
    def _generate_sounds(self):
        """Generate simple sound effects programmatically."""
        if not self._initialized:
            return
        
        try:
            # Generate success beep (pleasant ascending tone)
            self._sounds['success'] = self._create_tone(880, 0.15, fade=True)
            
            # Generate error beep (low buzzer)
            self._sounds['error'] = self._create_tone(220, 0.3, fade=True)
            
            # Generate camera shutter (quick click)
            self._sounds['shutter'] = self._create_click(0.1)
            
            # Generate notification (chime)
            self._sounds['notify'] = self._create_chime()
            
            # Generate warning beep
            self._sounds['warning'] = self._create_tone(440, 0.2, fade=True)
            
        except Exception as e:
            print(f"Warning: Could not generate sounds: {e}")
    
    def _create_tone(self, frequency: int, duration: float, fade: bool = False) -> pygame.mixer.Sound:
        """Create a simple sine wave tone."""
        sample_rate = 44100
        n_samples = int(sample_rate * duration)
        
        # Generate sine wave
        t = np.linspace(0, duration, n_samples, dtype=np.float32)
        wave = np.sin(2 * np.pi * frequency * t)
        
        # Apply fade in/out for smoother sound
        if fade:
            fade_samples = int(n_samples * 0.1)
            fade_in = np.linspace(0, 1, fade_samples)
            fade_out = np.linspace(1, 0, fade_samples)
            wave[:fade_samples] *= fade_in
            wave[-fade_samples:] *= fade_out
        
        # Convert to stereo
        stereo = np.column_stack((wave, wave))
        
        # Scale to 16-bit integer range
        audio = (stereo * 32767).astype(np.int16)
        
        return pygame.sndarray.make_sound(audio)
    
    def _create_click(self, duration: float) -> pygame.mixer.Sound:
        """Create a click/shutter sound."""
        sample_rate = 44100
        n_samples = int(sample_rate * duration)
        
        # Generate noise burst with fast decay
        noise = np.random.uniform(-1, 1, n_samples).astype(np.float32)
        decay = np.exp(-np.linspace(0, 10, n_samples))
        wave = noise * decay * 0.5
        
        # Convert to stereo
        stereo = np.column_stack((wave, wave))
        audio = (stereo * 32767).astype(np.int16)
        
        return pygame.sndarray.make_sound(audio)
    
    def _create_chime(self) -> pygame.mixer.Sound:
        """Create a pleasant chime sound."""
        sample_rate = 44100
        duration = 0.4
        n_samples = int(sample_rate * duration)
        
        t = np.linspace(0, duration, n_samples, dtype=np.float32)
        
        # Combine multiple harmonics for richer sound
        wave = (
            np.sin(2 * np.pi * 523 * t) * 0.5 +  # C5
            np.sin(2 * np.pi * 659 * t) * 0.3 +  # E5
            np.sin(2 * np.pi * 784 * t) * 0.2    # G5
        )
        
        # Apply decay envelope
        decay = np.exp(-np.linspace(0, 5, n_samples))
        wave *= decay
        
        # Convert to stereo
        stereo = np.column_stack((wave, wave))
        audio = (stereo * 32767).astype(np.int16)
        
        return pygame.sndarray.make_sound(audio)
    
    def play(self, sound_name: str):
        """Play a sound by name."""
        if not self.enabled or not self._initialized:
            return
        
        sound = self._sounds.get(sound_name)
        if sound:
            try:
                sound.play()
            except Exception as e:
                print(f"Warning: Could not play sound '{sound_name}': {e}")
    
    def play_success(self):
        """Play success sound."""
        self.play('success')
    
    def play_error(self):
        """Play error sound."""
        self.play('error')
    
    def play_shutter(self):
        """Play camera shutter sound."""
        self.play('shutter')
    
    def play_notify(self):
        """Play notification sound."""
        self.play('notify')
    
    def play_warning(self):
        """Play warning sound."""
        self.play('warning')
    
    def set_enabled(self, enabled: bool):
        """Enable or disable sounds."""
        self.enabled = enabled


# Global sound service instance
sound_service = SoundService()

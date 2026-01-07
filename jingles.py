"""
Musical jingles and menu music for ASCII OutRun
"""

import numpy as np
import pygame
from music_generator import MusicGenerator


def generate_menu_music():
    """Generate upbeat menu music loop"""
    music_gen = MusicGenerator(sample_rate=22050)
    
    # Upbeat menu melody in C Major
    melody_notes = [
        523.25,  # C5
        659.25,  # E5
        783.99,  # G5
        659.25,  # E5
        698.46,  # F5
        659.25,  # E5
        587.33,  # D5
        523.25,  # C5
    ]
    
    # Simple bass line
    bass_notes = [
        261.63,  # C4
        261.63,  # C4
        329.63,  # E4
        329.63,  # E4
        349.23,  # F4
        349.23,  # F4
        293.66,  # D4
        261.63,  # C4
    ]
    
    # Energetic drum pattern
    drum_pattern = {
        'kick': [0, 2, 4, 6],
        'snare': [1, 3, 5, 7],
        'hihat': [0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5, 5.5, 6, 6.5, 7, 7.5]
    }
    
    duration = 4.0
    bpm = 140  # Fast and energetic
    
    sound = music_gen.create_pygame_sound(
        melody_notes,
        bass_notes,
        duration=duration,
        bpm=bpm,
        drum_pattern=drum_pattern
    )
    
    return sound, duration


def generate_game_over_jingle():
    """Generate short game over jingle"""
    music_gen = MusicGenerator(sample_rate=22050)
    
    # Descending melody (sad ending)
    melody_notes = [
        523.25,  # C5
        493.88,  # B4
        440.00,  # A4
        392.00,  # G4
        349.23,  # F4
        329.63,  # E4
        293.66,  # D4
        261.63,  # C4
    ]
    
    # Bass follows melody
    bass_notes = [
        261.63,  # C4
        246.94,  # B3
        220.00,  # A3
        196.00,  # G3
        174.61,  # F3
        164.81,  # E3
        146.83,  # D3
        130.81,  # C3
    ]
    
    # Minimal drums
    drum_pattern = {
        'kick': [0, 4],
        'snare': [2, 6],
        'hihat': []
    }
    
    duration = 3.0
    bpm = 80  # Slow and dramatic
    
    # Generate the jingle
    jingle_track = music_gen.generate_track(
        melody_notes,
        bass_notes,
        duration=duration,
        bpm=bpm,
        drum_pattern=drum_pattern
    )
    
    # Add fade out at the end
    fade_samples = int(music_gen.sample_rate * 0.5)  # 0.5 second fade
    fade_envelope = np.linspace(1.0, 0.0, fade_samples)
    
    for i in range(fade_samples):
        pos = len(jingle_track) - fade_samples + i
        if 0 <= pos < len(jingle_track):
            jingle_track[pos] = (jingle_track[pos] * fade_envelope[i]).astype(np.int16)
    
    sound = pygame.sndarray.make_sound(jingle_track)
    
    return sound, duration


def play_jingle_once(sound, duration):
    """Play a jingle sound once and block until complete"""
    import time
    sound.play()
    time.sleep(duration)

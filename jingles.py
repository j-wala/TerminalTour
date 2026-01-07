"""
Musical jingles and menu music for ASCII OutRun
"""

import numpy as np
import pygame
from music_generator import MusicGenerator
from music_theory import NOTES, Scale, ChordProgression


def generate_menu_music():
    """Generate upbeat menu music loop using music theory"""
    music_gen = MusicGenerator(sample_rate=22050)
    
    # Upbeat menu melody in C Major using music theory notes
    melody_notes = [
        NOTES['C5'],
        NOTES['E5'],
        NOTES['G5'],
        NOTES['E5'],
        NOTES['F5'],
        NOTES['E5'],
        NOTES['D5'],
        NOTES['C5'],
    ]
    
    # Simple bass line
    bass_notes = [
        NOTES['C4'],
        NOTES['C4'],
        NOTES['E4'],
        NOTES['E4'],
        NOTES['F4'],
        NOTES['F4'],
        NOTES['D4'],
        NOTES['C4'],
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
    """Generate short game over jingle using music theory"""
    music_gen = MusicGenerator(sample_rate=22050)
    
    # Descending melody (sad ending) using music theory notes
    melody_notes = [
        NOTES['C5'],
        NOTES['B4'],
        NOTES['A4'],
        NOTES['G4'],
        NOTES['F4'],
        NOTES['E4'],
        NOTES['D4'],
        NOTES['C4'],
    ]
    
    # Bass follows melody
    bass_notes = [
        NOTES['C4'],
        NOTES['B3'],
        NOTES['A3'],
        NOTES['G3'],
        NOTES['F3'],
        NOTES['E3'],
        NOTES['D3'],
        NOTES['C3'],
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


def generate_game_over_music():
    """Generate somber game over music loop"""
    music_gen = MusicGenerator(sample_rate=22050)
    
    # Melancholy melody in A Minor using music theory notes
    melody_notes = [
        NOTES['A4'],
        NOTES['G4'],
        NOTES['F4'],
        NOTES['E4'],
        NOTES['F4'],
        NOTES['E4'],
        NOTES['D4'],
        NOTES['C4'],
    ]
    
    # Bass line
    bass_notes = [
        NOTES['A3'],
        NOTES['G3'],
        NOTES['F3'],
        NOTES['E3'],
        NOTES['F3'],
        NOTES['E3'],
        NOTES['D3'],
        NOTES['C3'],
    ]
    
    # Slow, minimal drum pattern
    drum_pattern = {
        'kick': [0, 4],
        'snare': [2, 6],
        'hihat': []
    }
    
    duration = 4.0
    bpm = 70  # Very slow and somber
    
    sound = music_gen.create_pygame_sound(
        melody_notes,
        bass_notes,
        duration=duration,
        bpm=bpm,
        drum_pattern=drum_pattern
    )
    
    return sound, duration


def play_jingle_once(sound, duration):
    """Play a jingle sound once"""
    import time
    try:
        sound.play()
        # Wait for playback without blocking too long
        time.sleep(min(duration, 3.0))  # Cap at 3 seconds
    except Exception as e:
        print(f"Error playing jingle: {e}")  # Debug
        pass

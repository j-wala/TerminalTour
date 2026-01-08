"""
Musical jingles and menu music for Terminal Tour
"""

try:
    import numpy as np
    import pygame
    from music_generator import MusicGenerator
    from music_theory import NOTES, Scale, ChordProgression
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False
    np = None
    pygame = None


def generate_menu_music():
    """Generate fast, energetic racing-themed menu music"""
    if not AUDIO_AVAILABLE:
        return None, 0
    music_gen = MusicGenerator(sample_rate=22050)
    
    # Fast, driving melody in E Major (racing energy!)
    melody_notes = [
        NOTES['E5'], NOTES['E5'], NOTES['G#5'], NOTES['B5'],
        NOTES['E5'], NOTES['E5'], NOTES['G#5'], NOTES['B5'],
        NOTES['D#5'], NOTES['D#5'], NOTES['F#5'], NOTES['A5'],
        NOTES['C#5'], NOTES['C#5'], NOTES['E5'], NOTES['G#5'],
        NOTES['E5'], NOTES['B5'], NOTES['G#5'], NOTES['E5'],
        NOTES['F#5'], NOTES['A5'], NOTES['F#5'], NOTES['D#5'],
        NOTES['E5'], NOTES['G#5'], NOTES['B5'], NOTES['E6'],
        NOTES['B5'], NOTES['G#5'], NOTES['E5'], NOTES['E5'],
    ]
    
    # Driving bass line (eighth notes for momentum)
    bass_notes = [
        NOTES['E3'], NOTES['E3'], NOTES['E3'], NOTES['E3'],
        NOTES['E3'], NOTES['E3'], NOTES['E3'], NOTES['E3'],
        NOTES['B2'], NOTES['B2'], NOTES['B2'], NOTES['B2'],
        NOTES['A2'], NOTES['A2'], NOTES['A2'], NOTES['A2'],
        NOTES['E3'], NOTES['E3'], NOTES['E3'], NOTES['E3'],
        NOTES['F#3'], NOTES['F#3'], NOTES['F#3'], NOTES['F#3'],
        NOTES['G#3'], NOTES['G#3'], NOTES['G#3'], NOTES['G#3'],
        NOTES['E3'], NOTES['E3'], NOTES['E3'], NOTES['E3'],
    ]
    
    # Fast, driving drum pattern (16th notes on hi-hat)
    drum_pattern = {
        'kick': [0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5, 5.5, 6, 6.5, 7, 7.5],  # Every eighth
        'snare': [1, 3, 5, 7],  # Backbeat
        'hihat': [i * 0.25 for i in range(32)]  # 16th notes for energy!
    }
    
    # Calculate duration based on BPM
    bpm = 160  # Very fast, racing tempo!
    beats_per_note = 0.5
    num_notes = len(melody_notes)
    beat_duration = 60.0 / bpm
    duration = num_notes * beat_duration * beats_per_note
    
    sound = music_gen.create_pygame_sound(
        melody_notes,
        bass_notes,
        duration=duration,
        bpm=bpm,
        drum_pattern=drum_pattern,
        groove='straight'  # Fast straight eighths for racing
    )
    
    return sound, duration


def generate_game_over_jingle():
    """Generate dramatic game over jingle - descending chromatic crash"""
    if not AUDIO_AVAILABLE:
        return None, 0
    music_gen = MusicGenerator(sample_rate=22050)
    
    # Dramatic descending chromatic run (classic "game over" sound)
    melody_notes = [
        NOTES['E5'],   # High tension
        NOTES['E5'],   # Repeat for emphasis
        NOTES['Eb5'],  # Chromatic descent
        NOTES['D5'],
        NOTES['Db5'],
        NOTES['C5'],
        NOTES['B4'],
        NOTES['Bb4'],
        NOTES['A4'],   # Final resolution
    ]
    
    # Heavy bass hits - dramatic punches
    bass_notes = [
        NOTES['E2'],   # Low and ominous
        NOTES['E2'],
        NOTES['Eb2'],
        NOTES['D2'],
        NOTES['Db2'],
        NOTES['C2'],
        NOTES['B2'],
        NOTES['Bb2'],
        NOTES['A2'],   # Final thud
    ]
    
    # Dramatic drum hits
    drum_pattern = {
        'kick': [0, 0.5, 1, 1.5, 2, 2.5, 3],  # Heavy repeated hits
        'snare': [0.25, 1.25, 2.25, 3.25],    # Rolls
        'hihat': []  # No hi-hat for dramatic effect
    }
    
    duration = 2.5  # Shorter, more punchy
    bpm = 100  # Moderate tempo for drama
    
    # Generate the jingle with dramatic straight timing
    jingle_track = music_gen.generate_track(
        melody_notes,
        bass_notes,
        duration=duration,
        bpm=bpm,
        drum_pattern=drum_pattern,
        groove='straight'  # Dramatic straight timing
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
    """Generate reflective game over music loop (not just jingle)"""
    if not AUDIO_AVAILABLE:
        return None, 0
    music_gen = MusicGenerator(sample_rate=22050)
    
    # Melancholy but flowing melody in A Minor (4 bars)
    melody_notes = [
        # Bar 1: Descending sadness
        NOTES['A4'], NOTES['G4'], NOTES['F4'], NOTES['E4'],
        NOTES['F4'], NOTES['E4'], NOTES['D4'], NOTES['C4'],
        # Bar 2: Slight hope
        NOTES['E4'], NOTES['F4'], NOTES['G4'], NOTES['A4'],
        NOTES['G4'], NOTES['F4'], NOTES['E4'], NOTES['D4'],
        # Bar 3: Reflection
        NOTES['C4'], NOTES['D4'], NOTES['E4'], NOTES['F4'],
        NOTES['E4'], NOTES['D4'], NOTES['C4'], NOTES['B3'],
        # Bar 4: Acceptance
        NOTES['A3'], NOTES['C4'], NOTES['E4'], NOTES['A4'],
        NOTES['G4'], NOTES['F4'], NOTES['E4'], NOTES['A4'],
    ]
    
    # Bass line with some movement
    bass_notes = [
        # Bar 1
        NOTES['A2'], NOTES['A2'], NOTES['F2'], NOTES['F2'],
        NOTES['E2'], NOTES['E2'], NOTES['E2'], NOTES['E2'],
        # Bar 2
        NOTES['A2'], NOTES['A2'], NOTES['G2'], NOTES['G2'],
        NOTES['F2'], NOTES['F2'], NOTES['E2'], NOTES['E2'],
        # Bar 3
        NOTES['C3'], NOTES['C3'], NOTES['C3'], NOTES['C3'],
        NOTES['E2'], NOTES['E2'], NOTES['E2'], NOTES['E2'],
        # Bar 4
        NOTES['A2'], NOTES['A2'], NOTES['A2'], NOTES['A2'],
        NOTES['E2'], NOTES['E2'], NOTES['A2'], NOTES['A2'],
    ]
    
    # Slow, contemplative drum pattern
    drum_pattern = {
        'kick': [0, 4],
        'snare': [2, 6],
        'hihat': [0, 1, 2, 3, 4, 5, 6, 7]  # Quarter notes for slow pulse
    }
    
    # Calculate duration based on BPM
    bpm = 75  # Slow and reflective
    beats_per_note = 0.5
    num_notes = len(melody_notes)
    beat_duration = 60.0 / bpm
    duration = num_notes * beat_duration * beats_per_note
    
    sound = music_gen.create_pygame_sound(
        melody_notes,
        bass_notes,
        duration=duration,
        bpm=bpm,
        drum_pattern=drum_pattern,
        groove='straight'  # Contemplative straight timing
    )
    
    return sound, duration


def generate_pause_music():
    """Generate calm, ambient pause music"""
    if not AUDIO_AVAILABLE:
        return None, 0
    music_gen = MusicGenerator(sample_rate=22050)
    
    # Gentle, calming melody
    melody_notes = [
        NOTES['C4'], NOTES['E4'], NOTES['G4'], NOTES['E4'],
        NOTES['F4'], NOTES['A4'], NOTES['C5'], NOTES['A4'],
        NOTES['G4'], NOTES['B4'], NOTES['D5'], NOTES['B4'],
        NOTES['C5'], NOTES['E5'], NOTES['C5'], NOTES['G4']
    ]
    
    # Slow, steady bass
    bass_notes = [
        NOTES['C3'], NOTES['C3'], NOTES['C3'], NOTES['C3'],
        NOTES['F3'], NOTES['F3'], NOTES['F3'], NOTES['F3'],
        NOTES['G3'], NOTES['G3'], NOTES['G3'], NOTES['G3'],
        NOTES['C3'], NOTES['C3'], NOTES['C3'], NOTES['C3']
    ]
    
    # Minimal, soft drums
    drum_pattern = {
        'kick': [0, 4, 8, 12],
        'snare': [],
        'hihat': [2, 6, 10, 14]
    }
    
    duration = 8.0  # Longer loop
    bpm = 80  # Slow and relaxed
    
    # Generate the pause music
    sound = music_gen.create_pygame_sound(
        melody_notes,
        bass_notes,
        duration=duration,
        bpm=bpm,
        drum_pattern=drum_pattern,
        groove='straight'  # Calm straight timing
    )
    
    return sound, duration


def play_jingle_once(sound, duration):
    """Play a jingle sound once"""
    if not AUDIO_AVAILABLE or sound is None:
        return
    import time
    try:
        sound.play()
        # Wait for playback without blocking too long
        time.sleep(min(duration, 3.0))  # Cap at 3 seconds
    except Exception as e:
        print(f"Error playing jingle: {e}")  # Debug
        pass

"""
Music theory system for procedural music generation
Defines notes, scales, and chord progressions
"""

import random

# Note frequency definitions (A4 = 440 Hz standard)
NOTES = {
    # Octave 3
    'C3': 130.81, 'C#3': 138.59, 'Db3': 138.59,
    'D3': 146.83, 'D#3': 155.56, 'Eb3': 155.56,
    'E3': 164.81,
    'F3': 174.61, 'F#3': 185.00, 'Gb3': 185.00,
    'G3': 196.00, 'G#3': 207.65, 'Ab3': 207.65,
    'A3': 220.00, 'A#3': 233.08, 'Bb3': 233.08,
    'B3': 246.94,
    
    # Octave 4
    'C4': 261.63, 'C#4': 277.18, 'Db4': 277.18,
    'D4': 293.66, 'D#4': 311.13, 'Eb4': 311.13,
    'E4': 329.63,
    'F4': 349.23, 'F#4': 369.99, 'Gb4': 369.99,
    'G4': 392.00, 'G#4': 415.30, 'Ab4': 415.30,
    'A4': 440.00, 'A#4': 466.16, 'Bb4': 466.16,
    'B4': 493.88,
    
    # Octave 5
    'C5': 523.25, 'C#5': 554.37, 'Db5': 554.37,
    'D5': 587.33, 'D#5': 622.25, 'Eb5': 622.25,
    'E5': 659.25,
    'F5': 698.46, 'F#5': 739.99, 'Gb5': 739.99,
    'G5': 783.99, 'G#5': 830.61, 'Ab5': 830.61,
    'A5': 880.00, 'A#5': 932.33, 'Bb5': 932.33,
    'B5': 987.77,
}


class Scale:
    """Represents a musical scale"""
    
    def __init__(self, name, root, intervals, bass_root=None):
        """
        name: Scale name (e.g., "C Major")
        root: Root note (e.g., "C4")
        intervals: Semitone intervals from root (e.g., [0, 2, 4, 5, 7, 9, 11] for major)
        bass_root: Optional bass octave root (e.g., "C3")
        """
        self.name = name
        self.root = root
        self.intervals = intervals
        self.bass_root = bass_root or root.replace('4', '3').replace('5', '4')
    
    def get_notes(self, octave_shift=0):
        """Get all notes in the scale"""
        root_freq = NOTES[self.root]
        notes = []
        
        for interval in self.intervals:
            # Calculate frequency with semitone shift
            freq = root_freq * (2 ** (interval / 12.0))
            # Apply octave shift
            freq = freq * (2 ** octave_shift)
            notes.append(freq)
        
        return notes
    
    def get_bass_notes(self):
        """Get bass notes (lower octave)"""
        bass_freq = NOTES[self.bass_root]
        notes = []
        
        for interval in self.intervals:
            freq = bass_freq * (2 ** (interval / 12.0))
            notes.append(freq)
        
        return notes
    
    def get_chord(self, degree, octave_shift=0):
        """Get a chord (triad) starting from scale degree"""
        scale_notes = self.get_notes(octave_shift)
        degree_index = degree - 1
        
        if degree_index >= len(scale_notes):
            return []
        
        # Triad: root, third, fifth
        chord = [
            scale_notes[degree_index % len(scale_notes)],
            scale_notes[(degree_index + 2) % len(scale_notes)],
            scale_notes[(degree_index + 4) % len(scale_notes)]
        ]
        
        return chord


# Define common scales
SCALES = {
    'C_Major': Scale('C Major', 'C4', [0, 2, 4, 5, 7, 9, 11], 'C3'),
    'G_Major': Scale('G Major', 'G4', [0, 2, 4, 5, 7, 9, 11], 'G3'),
    'F_Major': Scale('F Major', 'F4', [0, 2, 4, 5, 7, 9, 11], 'F3'),
    'D_Minor': Scale('D Minor', 'D4', [0, 2, 3, 5, 7, 8, 10], 'D3'),
    'E_Minor': Scale('E Minor', 'E4', [0, 2, 3, 5, 7, 8, 10], 'E3'),
    'A_Minor': Scale('A Minor', 'A4', [0, 2, 3, 5, 7, 8, 10], 'A3'),
    'B_Diminished': Scale('B Diminished', 'B4', [0, 2, 3, 5, 6, 8, 9, 11], 'B3'),
}


class DrumPattern:
    """Drum pattern generator for different styles and grooves"""
    
    PATTERNS = {
        'standard': {
            'kick': [0, 2, 4, 6],           # On beats 1 and 3
            'snare': [1, 3, 5, 7],          # On beats 2 and 4
            'hihat': [0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5, 5.5, 6, 6.5, 7, 7.5],  # 8th notes
            'groove': 'straight'
        },
        'fast': {
            'kick': [0, 1, 2, 3, 4, 5, 6, 7],  # Every beat
            'snare': [1, 3, 5, 7],             # Backbeats
            'hihat': [0, 0.25, 0.5, 0.75, 1, 1.25, 1.5, 1.75, 2, 2.25, 2.5, 2.75, 3, 3.25, 3.5, 3.75,
                     4, 4.25, 4.5, 4.75, 5, 5.25, 5.5, 5.75, 6, 6.25, 6.5, 6.75, 7, 7.25, 7.5, 7.75],  # 16th notes
            'groove': 'triplet'
        },
        'syncopated': {
            'kick': [0, 1.5, 2, 4, 5.5, 6],    # Syncopated kicks
            'snare': [1, 3, 5, 7],             # Backbeats
            'hihat': [0, 0.67, 1.33, 2, 2.67, 3.33, 4, 4.67, 5.33, 6, 6.67, 7.33],  # Swing feel
            'groove': 'swing'
        },
        'minimal': {
            'kick': [0, 4],                    # Just on 1 and 5
            'snare': [2, 6],                   # Just on 3 and 7
            'hihat': [0, 1.33, 2.67, 4, 5.33, 6.67],  # Shuffle feel
            'groove': 'shuffle'
        },
    }
    
    @staticmethod
    def get_pattern(pattern_name='standard'):
        """Get drum pattern by name"""
        return DrumPattern.PATTERNS.get(pattern_name, DrumPattern.PATTERNS['standard'])


class ChordProgression:
    """Generates chord progressions using circle of fifths"""
    
    # Circle of fifths (major keys)
    CIRCLE_OF_FIFTHS = ['C', 'G', 'D', 'A', 'E', 'B', 'F#', 'Db', 'Ab', 'Eb', 'Bb', 'F']
    
    # Common progressions
    PROGRESSIONS = {
        'pop': [1, 5, 6, 4],      # I-V-vi-IV (very common)
        'blues': [1, 4, 1, 5],     # I-IV-I-V
        'jazz': [2, 5, 1],         # ii-V-I
        'sad': [1, 6, 4, 5],       # I-vi-IV-V
        'epic': [1, 3, 6, 4],      # I-iii-vi-IV
        'retro': [1, 4, 5, 4],     # I-IV-V-IV
    }
    
    @staticmethod
    def generate_melody(scale, num_notes=8, style='upbeat'):
        """Generate a melodic sequence using scale"""
        notes = scale.get_notes()
        melody = []
        
        if style == 'upbeat':
            # Tend toward higher notes, more jumps
            for _ in range(num_notes):
                if random.random() < 0.3:
                    # Jump
                    melody.append(random.choice(notes))
                else:
                    # Step
                    if len(melody) > 0:
                        current_idx = notes.index(melody[-1]) if melody[-1] in notes else 0
                        step = random.choice([-1, 0, 1, 2])
                        new_idx = (current_idx + step) % len(notes)
                        melody.append(notes[new_idx])
                    else:
                        melody.append(notes[0])
        
        elif style == 'melancholy':
            # Tend toward lower notes, more steps
            for _ in range(num_notes):
                if random.random() < 0.1:
                    # Jump down
                    melody.append(random.choice(notes[:4]))
                else:
                    # Step
                    if len(melody) > 0:
                        current_idx = notes.index(melody[-1]) if melody[-1] in notes else 0
                        step = random.choice([-1, 0, 1])
                        new_idx = max(0, (current_idx + step) % len(notes))
                        melody.append(notes[new_idx])
                    else:
                        melody.append(notes[0])
        
        else:  # balanced
            for _ in range(num_notes):
                if len(melody) > 0:
                    current_idx = notes.index(melody[-1]) if melody[-1] in notes else 0
                    step = random.choice([-2, -1, 0, 1, 2])
                    new_idx = (current_idx + step) % len(notes)
                    melody.append(notes[new_idx])
                else:
                    melody.append(notes[0])
        
        return melody
    
    @staticmethod
    def generate_bass(scale, progression_type='pop', num_notes=8):
        """Generate a bass line following chord progression"""
        bass_notes = scale.get_bass_notes()
        progression = ChordProgression.PROGRESSIONS.get(progression_type, [1, 5, 6, 4])
        
        bass_line = []
        notes_per_chord = num_notes // len(progression)
        
        for degree in progression:
            # Use root of chord
            root = bass_notes[(degree - 1) % len(bass_notes)]
            
            # Add variations
            for _ in range(notes_per_chord):
                if random.random() < 0.7:
                    bass_line.append(root)
                else:
                    # Fifth
                    fifth = bass_notes[(degree - 1 + 4) % len(bass_notes)]
                    bass_line.append(fifth)
        
        # Pad to exact length
        while len(bass_line) < num_notes:
            bass_line.append(bass_notes[0])
        
        return bass_line[:num_notes]


def generate_music_from_config(music_config):
    """Generate music from a level's music configuration"""
    
    # Determine scale intervals based on type
    if music_config.scale_type == 'major':
        intervals = [0, 2, 4, 5, 7, 9, 11]
    elif music_config.scale_type == 'minor':
        intervals = [0, 2, 3, 5, 7, 8, 10]
    elif music_config.scale_type == 'diminished':
        intervals = [0, 2, 3, 5, 6, 8, 9, 11]
    else:
        intervals = [0, 2, 4, 5, 7, 9, 11]  # Default to major
    
    # Create scale from config
    bass_root = music_config.root_note.replace('4', '3').replace('5', '4')
    scale = Scale(
        music_config.scale_name,
        music_config.root_note,
        intervals,
        bass_root
    )
    
    # Generate melody and bass
    melody = ChordProgression.generate_melody(scale, 8, music_config.melody_style)
    bass = ChordProgression.generate_bass(scale, music_config.progression_style, 8)
    
    # Get drum pattern
    drum_pattern = DrumPattern.get_pattern(music_config.drum_pattern)
    
    return {
        'melody': melody,
        'bass': bass,
        'scale': scale,
        'bpm': music_config.bpm,
        'drum_pattern': drum_pattern,
        'groove': music_config.groove
    }

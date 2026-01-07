"""
Enhanced procedural music generation for ASCII OutRun
Generates chiptune music with melody, bass, harmony, and drums
"""

import numpy as np
import pygame


class MusicGenerator:
    """Generates procedural chiptune music with multiple instruments"""
    
    def __init__(self, sample_rate=22050):
        self.sample_rate = sample_rate
    
    def generate_square_wave(self, freq, duration):
        """Generate a square wave (classic chiptune sound)"""
        t = np.linspace(0, duration, int(self.sample_rate * duration))
        wave = np.sign(np.sin(2 * np.pi * freq * t))
        return (wave * 8192).astype(np.int16)
    
    def generate_triangle_wave(self, freq, duration):
        """Generate a triangle wave (softer than square)"""
        t = np.linspace(0, duration, int(self.sample_rate * duration))
        wave = 2 * np.abs(2 * ((freq * t) % 1.0) - 1) - 1
        return (wave * 8192).astype(np.int16)
    
    def generate_sawtooth_wave(self, freq, duration):
        """Generate a sawtooth wave (bright, cutting sound)"""
        t = np.linspace(0, duration, int(self.sample_rate * duration))
        wave = 2 * ((freq * t) % 1.0) - 1
        return (wave * 8192).astype(np.int16)
    
    def generate_noise(self, duration):
        """Generate white noise for drums"""
        samples = int(self.sample_rate * duration)
        noise = np.random.uniform(-1, 1, samples)
        return (noise * 8192).astype(np.int16)
    
    def apply_envelope(self, wave, attack=0.01, decay=0.1, sustain=0.7, release=0.2):
        """Apply ADSR envelope to a waveform"""
        total_samples = len(wave)
        envelope = np.ones(total_samples)
        
        attack_samples = int(attack * total_samples)
        decay_samples = int(decay * total_samples)
        release_samples = int(release * total_samples)
        sustain_samples = total_samples - attack_samples - decay_samples - release_samples
        
        # Attack
        envelope[:attack_samples] = np.linspace(0, 1, attack_samples)
        
        # Decay
        decay_start = attack_samples
        decay_end = decay_start + decay_samples
        envelope[decay_start:decay_end] = np.linspace(1, sustain, decay_samples)
        
        # Sustain
        sustain_start = decay_end
        sustain_end = sustain_start + sustain_samples
        envelope[sustain_start:sustain_end] = sustain
        
        # Release
        release_start = sustain_end
        envelope[release_start:] = np.linspace(sustain, 0, release_samples)
        
        return (wave * envelope).astype(np.int16)
    
    def generate_kick_drum(self, duration=0.15):
        """Generate a kick drum sound"""
        t = np.linspace(0, duration, int(self.sample_rate * duration))
        
        # Frequency sweep from 150Hz to 40Hz
        freq_start = 150
        freq_end = 40
        freq_sweep = freq_start + (freq_end - freq_start) * (t / duration)
        
        # Generate tone
        phase = 2 * np.pi * np.cumsum(freq_sweep) / self.sample_rate
        kick = np.sin(phase)
        
        # Apply envelope
        envelope = np.exp(-t * 15)
        kick = kick * envelope
        
        return (kick * 16384).astype(np.int16)
    
    def generate_snare_drum(self, duration=0.1):
        """Generate a snare drum sound"""
        # Mix of tone and noise
        tone = self.generate_triangle_wave(200, duration) * 0.3
        noise = self.generate_noise(duration) * 0.7
        
        snare = tone + noise
        
        # Sharp envelope
        t = np.linspace(0, 1, len(snare))
        envelope = np.exp(-t * 20)
        snare = (snare * envelope).astype(np.int16)
        
        return snare
    
    def generate_hihat(self, duration=0.05):
        """Generate a hi-hat sound"""
        noise = self.generate_noise(duration)
        
        # High-pass filter effect (simplified)
        t = np.linspace(0, 1, len(noise))
        envelope = np.exp(-t * 30)
        
        hihat = (noise * envelope * 0.5).astype(np.int16)
        return hihat
    
    def generate_drum_pattern(self, duration, bpm=120, pattern=None):
        """Generate a drum pattern based on pattern definition"""
        if pattern is None:
            # Default pattern
            pattern = {
                'kick': [0, 2, 4, 6],
                'snare': [1, 3, 5, 7],
                'hihat': [0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5, 5.5, 6, 6.5, 7, 7.5]
            }
        
        beat_duration = 60.0 / bpm
        
        # Create silent array
        drum_track = np.zeros(int(self.sample_rate * duration), dtype=np.int16)
        
        # Add kicks
        for beat_time in pattern.get('kick', []):
            beat_pos = int(beat_time * beat_duration * self.sample_rate)
            if beat_pos < len(drum_track):
                kick = self.generate_kick_drum()
                end_pos = min(beat_pos + len(kick), len(drum_track))
                drum_track[beat_pos:end_pos] += kick[:end_pos - beat_pos]
        
        # Add snares
        for beat_time in pattern.get('snare', []):
            beat_pos = int(beat_time * beat_duration * self.sample_rate)
            if beat_pos < len(drum_track):
                snare = self.generate_snare_drum()
                end_pos = min(beat_pos + len(snare), len(drum_track))
                drum_track[beat_pos:end_pos] += snare[:end_pos - beat_pos]
        
        # Add hi-hats
        for beat_time in pattern.get('hihat', []):
            beat_pos = int(beat_time * beat_duration * self.sample_rate)
            if beat_pos < len(drum_track):
                hihat = self.generate_hihat()
                end_pos = min(beat_pos + len(hihat), len(drum_track))
                drum_track[beat_pos:end_pos] += hihat[:end_pos - beat_pos]
        
        return drum_track
    
    def generate_melody_track(self, notes, duration):
        """Generate melody using square wave"""
        note_duration = duration / len(notes)
        melody = np.array([], dtype=np.int16)
        
        for note in notes:
            wave = self.generate_square_wave(note, note_duration)
            wave = self.apply_envelope(wave, attack=0.01, decay=0.1, sustain=0.6, release=0.2)
            melody = np.concatenate([melody, wave])
        
        return melody
    
    def generate_bass_track(self, notes, duration):
        """Generate bass using triangle wave"""
        note_duration = duration / len(notes)
        bass = np.array([], dtype=np.int16)
        
        for note in notes:
            wave = self.generate_triangle_wave(note, note_duration)
            wave = self.apply_envelope(wave, attack=0.02, decay=0.05, sustain=0.8, release=0.1)
            bass = np.concatenate([bass, wave])
        
        return bass
    
    def generate_harmony_track(self, melody_notes, duration):
        """Generate harmony (third above melody)"""
        note_duration = duration / len(melody_notes)
        harmony = np.array([], dtype=np.int16)
        
        for note in melody_notes:
            # Third above (multiply by 1.26 for major third)
            harmony_freq = note * 1.26
            wave = self.generate_sawtooth_wave(harmony_freq, note_duration)
            wave = self.apply_envelope(wave, attack=0.02, decay=0.1, sustain=0.4, release=0.3)
            harmony = np.concatenate([harmony, wave])
        
        return harmony * 0.4  # Lower volume for harmony
    
    def generate_track(self, melody_notes, bass_notes, duration=4.0, bpm=120, drum_pattern=None, mix_levels=None):
        """Generate complete music track with all instruments"""
        # Default mix levels
        if mix_levels is None:
            mix_levels = {
                'melody': 0.35,
                'bass': 0.35,
                'harmony': 0.15,
                'drums': 0.25
            }
        
        # Generate individual tracks
        melody = self.generate_melody_track(melody_notes, duration)
        bass = self.generate_bass_track(bass_notes, duration)
        harmony = self.generate_harmony_track(melody_notes, duration)
        drums = self.generate_drum_pattern(duration, bpm, drum_pattern)
        
        # Ensure all tracks are the same length
        max_len = max(len(melody), len(bass), len(harmony), len(drums))
        
        # Pad tracks if needed
        melody = np.pad(melody, (0, max_len - len(melody)))
        bass = np.pad(bass, (0, max_len - len(bass)))
        harmony = np.pad(harmony, (0, max_len - len(harmony)))
        drums = np.pad(drums, (0, max_len - len(drums)))
        
        # Mix tracks with custom levels
        mixed = (melody * mix_levels['melody'] + 
                bass * mix_levels['bass'] + 
                harmony * mix_levels['harmony'] + 
                drums * mix_levels['drums']).astype(np.int16)
        
        # Create stereo by duplicating and adding slight variation
        stereo_left = mixed
        stereo_right = mixed
        
        # Combine into stereo
        stereo = np.stack([stereo_left, stereo_right], axis=1)
        
        return stereo
    
    def create_pygame_sound(self, melody_notes, bass_notes, duration=4.0, bpm=120, drum_pattern=None, mix_levels=None):
        """Create a pygame Sound object from the generated music"""
        stereo_audio = self.generate_track(melody_notes, bass_notes, duration, bpm, drum_pattern, mix_levels)
        return pygame.sndarray.make_sound(stereo_audio)

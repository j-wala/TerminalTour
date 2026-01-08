"""
Audio and music management for Terminal Tour
Centralizes all music and sound operations
"""

import time
import threading

try:
    import pygame
    from jingles import (
        generate_menu_music, 
        generate_game_over_jingle, 
        generate_game_over_music,
        play_jingle_once
    )
    from music_theory import generate_music_from_config
    from music_generator import MusicGenerator
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False


class MusicManager:
    """Manages all game music and audio"""
    
    def __init__(self, sound_mixer):
        self.sound_mixer = sound_mixer
        
        # Music tracks
        self.game_music = None
        self.menu_music = None
        self.menu_music_duration = 0
        self.game_over_jingle = None
        self.game_over_jingle_duration = 0
        self.game_over_music = None
        self.game_over_music_duration = 0
        
        # Playback state
        self.music_thread_active = False
        self.menu_music_playing = False
        self.game_over_music_playing = False
        
        # Music cache for levels
        self.music_cache = {}
        
        # Initialize all tracks
        self._init_all_music()
    
    def _init_all_music(self):
        """Initialize all music tracks"""
        if not AUDIO_AVAILABLE:
            return
        
        try:
            self.menu_music, self.menu_music_duration = generate_menu_music()
        except Exception as e:
            import sys
            print(f"Error initializing menu music: {e}", file=sys.stderr)
        
        try:
            self.game_over_jingle, self.game_over_jingle_duration = generate_game_over_jingle()
        except:
            pass
        
        try:
            self.game_over_music, self.game_over_music_duration = generate_game_over_music()
        except Exception as e:
            import sys
            print(f"Error initializing game over music: {e}", file=sys.stderr)
    
    def play_looping_music(self, sound, duration, playing_flag_name):
        """Generic method to play music in a loop"""
        if not AUDIO_AVAILABLE or not sound:
            return
        
        setattr(self, playing_flag_name, True)
        
        def music_loop():
            while getattr(self, playing_flag_name):
                if getattr(self, playing_flag_name):
                    sound.play()
                time.sleep(duration)
        
        music_thread = threading.Thread(target=music_loop, daemon=True)
        music_thread.start()
    
    def stop_looping_music(self, sound, playing_flag_name):
        """Generic method to stop looping music"""
        if not AUDIO_AVAILABLE:
            return
        
        setattr(self, playing_flag_name, False)
        time.sleep(0.1)  # Give thread time to stop
        
        if sound:
            try:
                sound.stop()
            except:
                pass
    
    def play_menu_music(self, settings):
        """Start menu music loop"""
        if not settings or not settings.music_enabled:
            return
        
        if not self.menu_music_playing:
            self.stop_game_music()
            self.stop_game_over_music()
            self.play_looping_music(self.menu_music, self.menu_music_duration, 'menu_music_playing')
    
    def stop_menu_music(self):
        """Stop menu music"""
        self.stop_looping_music(self.menu_music, 'menu_music_playing')
    
    def play_game_over_music(self, settings):
        """Start game over music loop"""
        if not settings or not settings.music_enabled:
            return
        
        if not self.game_over_music_playing:
            self.stop_game_music()
            self.stop_menu_music()
            self.play_looping_music(self.game_over_music, self.game_over_music_duration, 'game_over_music_playing')
    
    def stop_game_over_music(self):
        """Stop game over music"""
        self.stop_looping_music(self.game_over_music, 'game_over_music_playing')
    
    def play_game_over_jingle(self, settings):
        """Play game over jingle once"""
        if not AUDIO_AVAILABLE or not self.game_over_jingle or not settings or not settings.music_enabled:
            return
        
        try:
            self.stop_all_music()
            time.sleep(0.1)
            play_jingle_once(self.game_over_jingle, self.game_over_jingle_duration)
        except:
            pass
    
    def stop_game_music(self):
        """Stop game music and music thread"""
        if not AUDIO_AVAILABLE:
            return
        
        self.music_thread_active = False
        
        if self.game_music:
            try:
                self.game_music.stop()
            except:
                pass
        
        time.sleep(0.05)
    
    def stop_all_music(self):
        """Stop all music and audio"""
        self.stop_game_music()
        self.stop_menu_music()
        self.stop_game_over_music()
        
        if AUDIO_AVAILABLE:
            try:
                pygame.mixer.stop()
            except:
                pass
    
    def pregenerate_level_music(self, level):
        """Pre-generate and cache music for a level"""
        if not AUDIO_AVAILABLE or level.name in self.music_cache:
            return
        
        try:
            music_gen = MusicGenerator(sample_rate=22050)
            
            if level.music_config:
                level_music = generate_music_from_config(level.music_config, num_bars=8)
                melody_notes = level_music['melody']
                bass_notes = level_music['bass']
                bpm = level_music['bpm']
                drum_pattern = level_music['drum_pattern']
                groove = level_music['groove']
                
                beats_per_note = 0.5
                num_notes = len(melody_notes)
                beat_duration = 60.0 / bpm
                duration = num_notes * beat_duration * beats_per_note
            else:
                melody_notes = [523, 659, 784, 659, 523, 392, 523, 659]
                bass_notes = [262, 330, 262, 330, 262, 196, 262, 330]
                bpm = 120
                drum_pattern = None
                groove = 'straight'
                duration = 4.0
            
            mix_levels = self.sound_mixer.get_mix_levels()
            
            sound = music_gen.create_pygame_sound(
                melody_notes, 
                bass_notes, 
                duration=duration, 
                bpm=bpm,
                drum_pattern=drum_pattern,
                mix_levels=mix_levels,
                groove=groove
            )
            
            self.music_cache[level.name] = (sound, duration)
        except:
            pass
    
    def pregenerate_all_music(self, levels):
        """Pre-generate music for all levels in background"""
        if not AUDIO_AVAILABLE:
            return
        
        def generate_all():
            for level in levels:
                self.pregenerate_level_music(level)
        
        music_preload_thread = threading.Thread(target=generate_all, daemon=True)
        music_preload_thread.start()
    
    def play_level_music(self, level, game_state):
        """Play music for a specific level"""
        if not AUDIO_AVAILABLE:
            return
        
        try:
            self.stop_game_music()
            
            # Check cache first
            if level.name in self.music_cache:
                self.game_music, duration = self.music_cache[level.name]
            else:
                # Generate on-demand if not cached
                self.pregenerate_level_music(level)
                if level.name in self.music_cache:
                    self.game_music, duration = self.music_cache[level.name]
                else:
                    return
            
            def play_loop():
                self.music_thread_active = True
                while not game_state.game_over and self.music_thread_active:
                    if game_state.music_enabled and self.game_music:
                        self.game_music.stop()
                        self.game_music.play()
                    time.sleep(duration)
                self.music_thread_active = False
            
            music_thread = threading.Thread(target=play_loop, daemon=True)
            music_thread.start()
        except:
            pass
    
    def fade_volume(self, volume):
        """Fade game music volume"""
        if not AUDIO_AVAILABLE or not self.game_music:
            return
        
        try:
            self.game_music.set_volume(max(0.0, min(1.0, volume)))
        except:
            pass

import curses
import time
import pygame
import threading

from level_specs import LEVELS, get_level_for_distance, PLAYER_CAR, TRAFFIC_CAR
from rendering import SkyRenderer, SceneryRenderer, CarRenderer, RoadRenderer, BackgroundRenderer
from game_state import GameState, TrafficManager, InputHandler
from ui import HUDRenderer, TitleScreen, GameOverScreen
from music_generator import MusicGenerator
from music_theory import generate_music_from_config
from transitions import TransitionEffect
from menu_system import MainMenu, GameOverMenu
from jingles import generate_menu_music, generate_game_over_jingle, generate_game_over_music, play_jingle_once
from sound_mixer import SoundMixer


class OutRunGame:
    """Main game class with modular architecture"""
    
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.height, self.width = stdscr.getmaxyx()
        
        # Initialize curses settings
        curses.curs_set(0)
        stdscr.nodelay(1)
        stdscr.timeout(0)
        
        # Initialize color pairs
        self._init_colors()
        
        # Initialize game components
        self.game_state = GameState(self.width, self.height)
        self.traffic_manager = TrafficManager(self.width, self.height)
        
        # Initialize renderers
        self.sky_renderer = SkyRenderer(stdscr, self.width, self.height)
        # self.background_renderer = BackgroundRenderer(stdscr, self.width, self.height)  # Disabled for performance
        self.scenery_renderer = SceneryRenderer(stdscr, self.width, self.height)
        self.road_renderer = RoadRenderer(stdscr, self.width, self.height)
        self.hud_renderer = HUDRenderer(stdscr, self.width, self.height)
        self.transition_effect = TransitionEffect(stdscr, self.width, self.height)
        
        # Initialize UI screens
        self.title_screen = TitleScreen(stdscr, self.width, self.height)
        self.game_over_screen = GameOverScreen(stdscr, self.width, self.height)
        self.sound_mixer = SoundMixer(stdscr, self.width, self.height)
        self.main_menu = MainMenu(stdscr, self.width, self.height, self.sound_mixer, game=self)
        self.game_over_menu = GameOverMenu(stdscr, self.width, self.height)
        
        # Level tracking
        self.current_level = LEVELS[0]
        self.previous_level = None
        
        # Music
        self.sound = None
        self.menu_music = None
        self.menu_music_duration = 0
        self.game_over_jingle = None
        self.game_over_jingle_duration = 0
        self.game_over_music = None
        self.game_over_music_duration = 0
        # Initialize default settings for menu music
        from menu_system import GameSettings
        self.settings = GameSettings()
        self.menu_music_playing = False
        self.game_over_music_playing = False
        
        # Initialize pygame first
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        except:
            pass
        
        self.init_menu_music()
        self.init_game_over_jingle()
        self.init_game_over_music()
    
    def _init_colors(self):
        """Initialize color pairs"""
        curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(5, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
        curses.init_pair(6, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(7, curses.COLOR_BLUE, curses.COLOR_BLACK)
    
    def init_music(self):
        """Initialize game music"""
        try:
            self.generate_music()
        except:
            pass
    
    def init_menu_music(self):
        """Initialize menu music"""
        try:
            self.menu_music, self.menu_music_duration = generate_menu_music()
        except Exception as e:
            import sys
            print(f"Error initializing menu music: {e}", file=sys.stderr)
            self.menu_music = None
            self.menu_music_duration = 0
    
    def init_game_over_jingle(self):
        """Initialize game over jingle"""
        try:
            self.game_over_jingle, self.game_over_jingle_duration = generate_game_over_jingle()
        except:
            pass
    
    def init_game_over_music(self):
        """Initialize game over music"""
        try:
            self.game_over_music, self.game_over_music_duration = generate_game_over_music()
        except Exception as e:
            import sys
            print(f"Error initializing game over music: {e}", file=sys.stderr)
            self.game_over_music = None
            self.game_over_music_duration = 0
    
    def play_menu_music(self):
        """Start menu music loop"""
        # Check if music is enabled (settings always exists now)
        if self.settings and not self.settings.music_enabled:
            return
        
        if self.menu_music and not self.menu_music_playing:
            # Stop any other music first
            self.stop_game_music()
            self.stop_game_over_music()
            
            self.menu_music_playing = True
            def menu_loop():
                while self.menu_music_playing:
                    # Check settings before playing
                    if self.menu_music_playing and self.settings and self.settings.music_enabled:
                        self.menu_music.play()
                    time.sleep(self.menu_music_duration)
            
            music_thread = threading.Thread(target=menu_loop, daemon=True)
            music_thread.start()
    
    def stop_menu_music(self):
        """Stop menu music loop"""
        self.menu_music_playing = False
        time.sleep(0.1)  # Give thread time to stop
        if self.menu_music:
            try:
                self.menu_music.stop()
            except:
                pass
    
    def play_game_over_music(self):
        """Start game over music loop"""
        # Check if music is enabled
        if not (self.settings and self.settings.music_enabled):
            return
        
        if self.game_over_music and not self.game_over_music_playing:
            # Stop any other music first
            self.stop_game_music()
            self.stop_menu_music()
            
            self.game_over_music_playing = True
            def game_over_loop():
                while self.game_over_music_playing:
                    # Check settings before playing
                    if self.game_over_music_playing and self.settings and self.settings.music_enabled:
                        self.game_over_music.play()
                    time.sleep(self.game_over_music_duration)
            
            music_thread = threading.Thread(target=game_over_loop, daemon=True)
            music_thread.start()
    
    def stop_game_over_music(self):
        """Stop game over music loop"""
        self.game_over_music_playing = False
        time.sleep(0.1)  # Give thread time to stop
        if self.game_over_music:
            try:
                self.game_over_music.stop()
            except:
                pass
    
    def stop_game_music(self):
        """Stop game music"""
        if self.sound:
            try:
                self.sound.stop()
            except:
                pass
    
    def stop_all_music(self):
        """Stop all music and audio to prevent bleeding"""
        # Stop game music
        self.stop_game_music()
        # Stop menu music
        self.stop_menu_music()
        # Stop game over music
        self.stop_game_over_music()
        
        # Stop pygame mixer channels
        try:
            pygame.mixer.stop()
        except:
            pass
    
    def play_game_over_jingle(self):
        """Play game over jingle once"""
        if self.game_over_jingle and self.settings and self.settings.music_enabled:
            try:
                # Stop ALL music first to prevent bleeding
                self.stop_all_music()
                
                # Wait for audio to clear
                time.sleep(0.1)
                
                # Play jingle (play_jingle_once already waits for completion)
                play_jingle_once(self.game_over_jingle, self.game_over_jingle_duration)
            except:
                pass
    
    def generate_music(self):
        """Generate procedural chiptune music using music theory from level config"""
        try:
            music_gen = MusicGenerator(sample_rate=22050)
            
            # Generate music from level's music configuration with 4 bars
            if self.current_level.music_config:
                level_music = generate_music_from_config(self.current_level.music_config, num_bars=4)
                
                melody_notes = level_music['melody']
                bass_notes = level_music['bass']
                bpm = level_music['bpm']
                drum_pattern = level_music['drum_pattern']
                groove = level_music['groove']
                
                # Calculate duration based on BPM and number of notes (32 eighth notes = 4 bars)
                beats_per_note = 0.5  # Eighth notes
                num_notes = len(melody_notes)
                beat_duration = 60.0 / bpm
                duration = num_notes * beat_duration * beats_per_note
            else:
                # Fallback if no music config
                melody_notes = [523, 659, 784, 659, 523, 392, 523, 659]
                bass_notes = [262, 330, 262, 330, 262, 196, 262, 330]
                bpm = 120
                drum_pattern = None
                groove = 'straight'
                duration = 4.0
            
            # Get current mix levels from sound mixer
            mix_levels = self.sound_mixer.get_mix_levels()
            
            # Generate rich music with melody, bass, harmony, and drums with groove
            self.sound = music_gen.create_pygame_sound(
                melody_notes, 
                bass_notes, 
                duration=duration, 
                bpm=bpm,
                drum_pattern=drum_pattern,
                mix_levels=mix_levels,
                groove=groove
            )
            
            def play_loop():
                while not self.game_state.game_over:
                    if self.game_state.music_enabled and self.sound:
                        self.sound.play()
                    time.sleep(duration)
            
            music_thread = threading.Thread(target=play_loop, daemon=True)
            music_thread.start()
        except Exception as e:
            # Silently fail if music generation fails
            pass
    
    def check_level_transition(self):
        """Check and handle level transitions with element-based effects"""
        new_level = get_level_for_distance(self.game_state.distance)
        
        if new_level != self.current_level:
            # Start transition sequence
            if self.game_state.transition_stage == 'none':
                self.game_state.transition_stage = 'horizon_out'
                self.game_state.transition_progress = 0
                self.game_state.old_level_color = self.current_level.sky_config.color_pair
                self.game_state.new_level_color = new_level.sky_config.color_pair
        
        # Handle transition stages
        if self.game_state.transition_stage == 'horizon_out':
            # Fade out horizon decorations and music
            self.game_state.transition_progress += 0.1
            
            # Fade out music volume
            if self.sound:
                fade_volume = 1.0 - self.game_state.transition_progress
                try:
                    self.sound.set_volume(max(0.0, fade_volume))
                except:
                    pass
            
            if self.game_state.transition_progress >= 1.0:
                self.game_state.transition_stage = 'color_fade'
                self.game_state.transition_progress = 0
                
                # Stop old music
                self.stop_game_music()
        
        elif self.game_state.transition_stage == 'color_fade':
            # Gradient to new sky color
            self.game_state.transition_progress += 0.08
            if self.game_state.transition_progress >= 1.0:
                # Switch to new level
                self.current_level = new_level
                self.game_state.level_transition_message = f"ENTERING {new_level.name} ZONE!"
                self.game_state.level_transition_timer = 60
                
                # Clear renderers for new level
                self.sky_renderer.clear_objects()
                self.scenery_renderer.clear_objects()
                
                # Regenerate music for new level (starts at 0 volume)
                try:
                    self.generate_music()
                    if self.sound:
                        self.sound.set_volume(0.0)  # Start silent, will fade in
                except:
                    pass
                
                self.game_state.transition_stage = 'horizon_in'
                self.game_state.transition_progress = 0
        
        elif self.game_state.transition_stage == 'horizon_in':
            # Fade in new horizon decorations and music
            self.game_state.transition_progress += 0.1
            
            # Fade in music volume
            if self.sound:
                fade_volume = self.game_state.transition_progress
                try:
                    self.sound.set_volume(min(1.0, fade_volume))
                except:
                    pass
            
            if self.game_state.transition_progress >= 1.0:
                self.game_state.transition_stage = 'none'
                self.game_state.transition_progress = 0
                
                # Ensure volume is at full
                if self.sound:
                    try:
                        self.sound.set_volume(1.0)
                    except:
                        pass
    
    def update_game(self):
        """Update all game logic"""
        self.game_state.update_road_offset()
        self.game_state.update_distance()
        self.game_state.update_curve()
        self.check_level_transition()
        
        # Spawn and update traffic
        self.traffic_manager.spawn_traffic(
            self.game_state.traffic,
            self.game_state.speed,
            self.game_state.get_curve_offset
        )
        
        points = self.traffic_manager.update_traffic(
            self.game_state.traffic,
            self.game_state.speed,
            self.game_state.get_curve_offset
        )
        self.game_state.score += points
        
        # Spawn and update scenery
        self.scenery_renderer.spawn(self.current_level, self.game_state.get_curve_offset)
        self.scenery_renderer.update(self.game_state.speed)
        
        # Check collisions
        if self.game_state.check_collision():
            self.game_state.game_over = True
            # Flash screen on death
            self.death_flash()
    
    def render_game(self):
        """Render all game elements"""
        self.stdscr.clear()
        
        # Render in order: sky -> road -> scenery -> cars -> HUD
        # Get curve offset for parallax
        curve_offset_at_horizon = self.game_state.get_curve_offset(10)
        
        # Handle transition rendering
        if self.game_state.transition_stage == 'horizon_out':
            # Render sky without horizon decorations fading out
            self.sky_renderer.render(self.current_level, curve_offset_at_horizon)
        elif self.game_state.transition_stage == 'color_fade':
            # Render gradient between colors
            self.transition_effect.render_sky_gradient(
                self.game_state.old_level_color,
                self.game_state.new_level_color,
                self.game_state.transition_progress
            )
        elif self.game_state.transition_stage == 'horizon_in':
            # Render sky with new horizon decorations fading in
            self.sky_renderer.render(self.current_level, curve_offset_at_horizon)
        else:
            # Normal rendering with parallax
            self.sky_renderer.render(self.current_level, curve_offset_at_horizon)
        
        # self.background_renderer.render(self.current_level, self.game_state.road_offset)  # Disabled for performance
        self.road_renderer.render(
            self.game_state.get_curve_offset,
            self.game_state.road_offset
        )
        self.scenery_renderer.render(self.game_state.get_curve_offset)
        
        # Render traffic
        for car in self.game_state.traffic:
            CarRenderer.render(
                self.stdscr,
                car.x,
                car.y,
                TRAFFIC_CAR,
                self.width,
                self.height
            )
        
        # Render player
        CarRenderer.render(
            self.stdscr,
            self.game_state.player.x,
            self.game_state.player.y,
            PLAYER_CAR,
            self.width,
            self.height
        )
        
        # Render HUD
        self.hud_renderer.render(self.game_state, self.current_level.name)
        
        self.stdscr.refresh()
    
    def death_flash(self):
        """Flash screen red when player dies"""
        try:
            # Flash red 3 times quickly
            for _ in range(3):
                # Fill screen with red
                for y in range(self.height):
                    for x in range(self.width - 1):
                        try:
                            self.stdscr.addstr(y, x, ' ', curses.color_pair(1) | curses.A_REVERSE)
                        except:
                            pass
                self.stdscr.refresh()
                time.sleep(0.1)
                
                # Clear
                self.stdscr.clear()
                self.stdscr.refresh()
                time.sleep(0.05)
        except:
            pass
    
    def run(self):
        """Main game loop with menu system"""
        
        while True:
            # Ensure we're in the right mode for menu
            self.stdscr.nodelay(0)  # Wait for input in menu
            
            # Play menu music
            self.play_menu_music()
            
            # Show main menu
            action, settings, music_changed = self.main_menu.show()
            
            # Stop menu music when starting game
            self.stop_menu_music()
            
            if action == 'quit':
                break
            
            if action == 'start':
                self.settings = settings
                self.game_state.music_enabled = settings.music_enabled
                
                # Reset game state for new game
                self.game_state.reset()
                self.sky_renderer.clear_objects()
                self.scenery_renderer.clear_objects()
                
                # Set starting level based on settings
                if settings.starting_level > 0:
                    self.current_level = LEVELS[settings.starting_level]
                    self.game_state.distance = LEVELS[settings.starting_level].distance_threshold
                else:
                    self.current_level = LEVELS[0]
                    self.game_state.distance = 0
                
                # Initialize or regenerate game music
                self.stdscr.nodelay(1)  # Non-blocking mode for gameplay
                self.init_music()
                self.main_menu.music_changed = False  # Reset flag
                
                # Run game
                if not self._run_game_loop():
                    break
    
    def _run_game_loop(self):
        """Internal game loop - returns False to quit, True to continue"""
        frame_time = 0.05
        
        while True:
            if not self.game_state.game_over:
                frame_start = time.time()
                
                # Update
                self.update_game()
                
                # Render
                self.render_game()
                
                # Handle input
                if not InputHandler.handle_input(self.stdscr, self.game_state, self.sound):
                    return False
                
                # Frame timing
                frame_elapsed = time.time() - frame_start
                sleep_time = frame_time - frame_elapsed
                if sleep_time > 0:
                    time.sleep(sleep_time)
            
            else:
                # Switch to blocking mode for menu
                self.stdscr.nodelay(0)
                
                # Play game over jingle (stops all music internally)
                self.play_game_over_jingle()
                
                # Start game over music (jingle is finished now)
                self.play_game_over_music()
                
                # Game over menu
                action = self.game_over_menu.show(self.game_state.score, self.game_state.distance)
                
                # Stop game over music
                self.stop_game_over_music()
                
                if action == 'restart':
                    # Reset game state
                    self.game_state.reset()
                    self.sky_renderer.clear_objects()
                    self.scenery_renderer.clear_objects()
                    
                    # Reset to configured starting level
                    if self.settings and self.settings.starting_level > 0:
                        self.current_level = LEVELS[self.settings.starting_level]
                        self.game_state.distance = LEVELS[self.settings.starting_level].distance_threshold
                    else:
                        self.current_level = LEVELS[0]
                        self.game_state.distance = 0
                    
                    # Switch back to non-blocking mode
                    self.stdscr.nodelay(1)
                    
                    # Regenerate music
                    self.init_music()
                    
                    # Small delay to ensure clean state
                    time.sleep(0.1)
                    
                    # Continue game loop
                    continue
                elif action == 'menu':
                    return True  # Return to main menu
                elif action == 'quit':
                    return False  # Exit game


def main(stdscr):
    game = OutRunGame(stdscr)
    game.run()


if __name__ == "__main__":
    curses.wrapper(main)

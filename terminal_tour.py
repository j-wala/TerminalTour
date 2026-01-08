#!/usr/bin/env python3
import curses
import time
import threading

try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False

from level_specs import LEVELS, get_level_for_distance, PLAYER_CAR, TRAFFIC_CAR
from rendering import SkyRenderer, SceneryRenderer, CarRenderer, RoadRenderer, BackgroundRenderer
from game_state import GameState, TrafficManager, InputHandler
from ui import HUDRenderer, TitleScreen, GameOverScreen
from transitions import TransitionEffect
from menu_system import MainMenu, GameOverMenu
from pause_menu import PauseMenu
from countdown import CountdownTimer
from sound_mixer import SoundMixer
from audio_manager import MusicManager
from transition_manager import TransitionManager


class TerminalTourGame:
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
        
        # Initialize pygame mixer FIRST (before any music generation)
        if PYGAME_AVAILABLE:
            try:
                pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            except:
                pass
        
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
        self.pause_menu = PauseMenu(stdscr, self.width, self.height)
        self.countdown_timer = CountdownTimer(stdscr, self.width, self.height)
        
        # Level tracking
        self.current_level = LEVELS[0]
        
        # Initialize default settings
        from menu_system import GameSettings
        self.settings = GameSettings()
        
        # Initialize managers
        self.music_manager = MusicManager(self.sound_mixer)
        self.transition_manager = TransitionManager(self.game_state)
    
    def _init_colors(self):
        """Initialize color pairs"""
        curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(5, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
        curses.init_pair(6, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(7, curses.COLOR_BLUE, curses.COLOR_BLACK)
    
    
    def check_level_transition(self):
        """Check and handle level transitions"""
        new_level = self.transition_manager.check_and_update_transition(
            self.current_level,
            self.settings,
            self.music_manager,
            self.sky_renderer,
            self.scenery_renderer
        )
        
        if new_level:
            self.current_level = new_level
    
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
        
        # Pre-generate all level music in background to prevent slowdowns
        self.music_manager.pregenerate_all_music(LEVELS)
        
        while True:
            # Ensure we're in the right mode for menu
            self.stdscr.nodelay(0)  # Wait for input in menu
            
            # Play menu music
            self.music_manager.play_menu_music(self.settings)
            
            # Show main menu
            action, settings, music_changed = self.main_menu.show()
            
            # Stop menu music when starting game
            self.music_manager.stop_menu_music()
            
            if action == 'quit':
                break
            
            if action == 'start':
                self.settings = settings
                self.game_state.music_enabled = settings.music_enabled
                
                # Randomize level order if enabled
                if settings.randomize_levels:
                    settings.shuffle_level_order()
                
                # Reset game state for new game
                self.game_state.reset()
                self.sky_renderer.clear_objects()
                self.scenery_renderer.clear_objects()
                
                # Always start at first active level with distance 0
                active_indices = settings.get_active_levels()
                if active_indices:
                    self.current_level = LEVELS[active_indices[0]]
                else:
                    self.current_level = LEVELS[0]  # Fallback
                self.game_state.distance = 0
                
                # Initialize music
                self.music_manager.play_level_music(self.current_level, self.game_state)
                
                # Set to non-blocking mode before countdown
                self.stdscr.nodelay(1)
                
                # Show countdown with game rendered in background
                self.countdown_timer.show(render_callback=self.render_game)
                
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
                
                # Handle input (including ESC for pause)
                input_result = InputHandler.handle_input(self.stdscr, self.game_state, self.music_manager)
                if input_result == False:
                    return False
                elif input_result == 'pause':
                    pause_action = self._handle_pause()
                    if pause_action == 'quit':
                        return False
                    elif pause_action == 'menu':
                        return True
                    elif pause_action == 'restart':
                        # Reset and restart
                        self.game_state.reset()
                        self.sky_renderer.clear_objects()
                        self.scenery_renderer.clear_objects()
                        active_indices = self.settings.get_active_levels() if self.settings else [0, 1, 2, 3, 4, 5]
                        if active_indices:
                            self.current_level = LEVELS[active_indices[0]]
                        else:
                            self.current_level = LEVELS[0]
                        self.game_state.distance = 0
                        
                        # Restart music
                        self.music_manager.play_level_music(self.current_level, self.game_state)
                        
                        # Show countdown with game rendered
                        self.countdown_timer.show(render_callback=self.render_game)
                        continue
                    # else resume - continue loop
                
                # Frame timing
                frame_elapsed = time.time() - frame_start
                sleep_time = frame_time - frame_elapsed
                if sleep_time > 0:
                    time.sleep(sleep_time)
            
            else:
                # Switch to blocking mode for menu
                self.stdscr.nodelay(0)
                
                # Play game over jingle (stops all music internally)
                self.music_manager.play_game_over_jingle(self.settings)
                
                # Start game over music (jingle is finished now)
                self.music_manager.play_game_over_music(self.settings)
                
                # Game over menu
                action = self.game_over_menu.show(self.game_state.score, self.game_state.distance)
                
                # Stop game over music
                self.music_manager.stop_game_over_music()
                
                if action == 'restart':
                    # Reset game state
                    self.game_state.reset()
                    self.sky_renderer.clear_objects()
                    self.scenery_renderer.clear_objects()
                    
                    # Always start at first active level with distance 0
                    active_indices = self.settings.get_active_levels() if self.settings else [0, 1, 2, 3]
                    if active_indices:
                        self.current_level = LEVELS[active_indices[0]]
                    else:
                        self.current_level = LEVELS[0]
                    self.game_state.distance = 0
                    
                    # Restart music
                    self.music_manager.play_level_music(self.current_level, self.game_state)
                    
                    # Switch to non-blocking mode before countdown
                    self.stdscr.nodelay(1)
                    
                    # Show countdown with game rendered
                    self.countdown_timer.show(render_callback=self.render_game)
                    
                    # Continue game loop
                    continue
                elif action == 'menu':
                    return True  # Return to main menu
                elif action == 'quit':
                    return False  # Exit game
    
    def _handle_pause(self):
        """Handle pause menu"""
        # Stop game music
        self.music_manager.stop_game_music()
        
        # Show pause menu
        action = self.pause_menu.show()
        
        # Resume game music if resuming
        if action == 'resume':
            # Restart music loop
            self.music_manager.play_level_music(self.current_level, self.game_state)
        
        return action


def main(stdscr):
    game = TerminalTourGame(stdscr)
    game.run()


if __name__ == "__main__":
    curses.wrapper(main)

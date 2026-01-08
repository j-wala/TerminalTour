"""
Menu system for Terminal Tour
Handles main menu, settings, and navigation
"""

import curses
import json
import os


class GameSettings:
    """Holds game settings with persistence"""
    SETTINGS_FILE = 'terminal_tour_settings.json'
    
    def __init__(self):
        # Basic settings
        self.music_enabled = True
        self.difficulty = 'normal'  # 'easy', 'normal', 'hard'
        
        # Level configuration
        self.level_length = 500  # Distance in meters per level
        self.enabled_levels = [True, True, True, True, True, True, True, True, True, True, True]  # All 11 levels
        self.level_order = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]  # Order of levels (first is starting level)
        self.endless_mode = False  # Loop levels infinitely
        self.randomize_levels = True  # Randomize level order on game start
        
        # Audio mixer settings
        self.mixer_levels = {'melody': 0.7, 'bass': 0.6, 'harmony': 0.5, 'drums': 0.4}
        
        # Try to load saved settings
        self.load()
    
    def save(self):
        """Save settings to JSON file"""
        try:
            settings_data = {
                'music_enabled': self.music_enabled,
                'difficulty': self.difficulty,
                'level_length': self.level_length,
                'enabled_levels': self.enabled_levels,
                'level_order': self.level_order,
                'endless_mode': self.endless_mode,
                'randomize_levels': self.randomize_levels,
                'mixer_levels': self.mixer_levels
            }
            with open(self.SETTINGS_FILE, 'w') as f:
                json.dump(settings_data, f, indent=2)
            return True
        except Exception as e:
            import sys
            print(f"Error saving settings: {e}", file=sys.stderr)
            return False
    
    def load(self):
        """Load settings from JSON file"""
        try:
            if os.path.exists(self.SETTINGS_FILE):
                with open(self.SETTINGS_FILE, 'r') as f:
                    settings_data = json.load(f)
                
                # Load settings with defaults
                self.music_enabled = settings_data.get('music_enabled', True)
                self.difficulty = settings_data.get('difficulty', 'normal')
                self.level_length = settings_data.get('level_length', 500)
                self.enabled_levels = settings_data.get('enabled_levels', [True, True, True, True, True, True, True, True, True, True, True])
                self.level_order = settings_data.get('level_order', [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
                self.endless_mode = settings_data.get('endless_mode', False)
                self.randomize_levels = settings_data.get('randomize_levels', False)
                self.mixer_levels = settings_data.get('mixer_levels', {'melody': 0.7, 'bass': 0.6, 'harmony': 0.5, 'drums': 0.4})
                
                # Ensure settings are compatible with current level count
                from level_specs import LEVELS
                num_levels = len(LEVELS)
                
                # Extend enabled_levels if new levels were added
                while len(self.enabled_levels) < num_levels:
                    self.enabled_levels.append(True)
                
                # Extend level_order if new levels were added
                while len(self.level_order) < num_levels:
                    self.level_order.append(len(self.level_order))
                return True
        except Exception as e:
            import sys
            print(f"Error loading settings: {e}", file=sys.stderr)
        return False
    
    def get_active_levels(self):
        """Get list of active level indices in play order"""
        return [idx for idx in self.level_order if idx < len(self.enabled_levels) and self.enabled_levels[idx]]
    
    def shuffle_level_order(self):
        """Randomize the level order while keeping enabled status"""
        import random
        # Get all level indices that are enabled
        enabled_indices = [i for i in range(len(self.enabled_levels)) if self.enabled_levels[i]]
        disabled_indices = [i for i in range(len(self.enabled_levels)) if not self.enabled_levels[i]]
        
        # Shuffle only the enabled levels
        random.shuffle(enabled_indices)
        
        # Combine shuffled enabled with disabled at the end
        self.level_order = enabled_indices + disabled_indices


class MainMenu:
    """Main menu with options and settings"""
    
    def __init__(self, stdscr, width, height, sound_mixer=None, game=None):
        self.stdscr = stdscr
        self.width = width
        self.height = height
        self.selected_option = 0
        self.menu_state = 'main'  # 'main', 'settings', 'level_select', 'mixer'
        self.settings = GameSettings()
        self.sound_mixer = sound_mixer
        self.music_changed = False
        self.game = game  # Reference to game object for music control
    
    def show(self):
        """Display and handle main menu"""
        self.stdscr.nodelay(0)  # Wait for input
        
        while True:
            self.stdscr.clear()
            
            if self.menu_state == 'main':
                result = self._show_main_menu()
                if result == 'start':
                    self.stdscr.nodelay(1)
                    return 'start', self.settings, self.music_changed
                elif result == 'settings':
                    self.menu_state = 'settings'
                    self.selected_option = 0
                elif result == 'quit':
                    return 'quit', None, False
            
            elif self.menu_state == 'settings':
                result = self._show_settings_menu()
                if result == 'back':
                    self.menu_state = 'main'
                    self.selected_option = 0
                elif result == 'mixer':
                    self.menu_state = 'mixer'
                    self.selected_option = 0
            
            elif self.menu_state == 'level_select':
                result = self._show_level_select()
                if result == 'back':
                    self.menu_state = 'settings'
                    self.selected_option = 0
            
            elif self.menu_state == 'mixer':
                result = self._show_mixer_menu()
                if result == 'back':
                    self.menu_state = 'settings'
                    self.selected_option = 0
    
    def _show_main_menu(self):
        """Show main menu options"""
        # Title
        title = [
            "╔╦╗┌─┐┬─┐┌┬┐┬┌┐┌┌─┐┬  ",
            " ║ ├┤ ├┬┘│││││││├─┤│  ",
            " ╩ └─┘┴└─┴ ┴┴┘└┘┴ ┴┴─┘",
            "     ╔╦╗┌─┐┬ ┬┬─┐     ",
            "      ║ │ ││ │├┬┘     ",
            "      ╩ └─┘└─┘┴└─     "
        ]
        
        start_y = self.height // 2 - len(title) - 8
        for i, line in enumerate(title):
            x = self.width // 2 - len(line) // 2
            if x >= 0 and start_y + i >= 0:
                try:
                    self.stdscr.addstr(start_y + i, x, line, 
                                     curses.color_pair(5) | curses.A_BOLD)
                except:
                    pass
        
        subtitle = "ASCII RACING GAME"
        try:
            self.stdscr.addstr(start_y + len(title) + 2, 
                             self.width // 2 - len(subtitle) // 2,
                             subtitle, curses.color_pair(2) | curses.A_BOLD)
        except:
            pass
        
        # Menu options
        options = ["START GAME", "SETTINGS", "QUIT"]
        menu_y = start_y + len(title) + 6
        
        for i, option in enumerate(options):
            x = self.width // 2 - len(option) // 2
            if i == self.selected_option:
                try:
                    self.stdscr.addstr(menu_y + i * 2, x - 2, "> ", 
                                     curses.color_pair(2) | curses.A_BOLD)
                    self.stdscr.addstr(menu_y + i * 2, x, option, 
                                     curses.color_pair(3) | curses.A_BOLD | curses.A_REVERSE)
                except:
                    pass
            else:
                try:
                    self.stdscr.addstr(menu_y + i * 2, x, option, 
                                     curses.color_pair(6))
                except:
                    pass
        
        # Controls hint
        hint = "[UP/DOWN: Navigate] [ENTER: Select]"
        try:
            self.stdscr.addstr(self.height - 3, self.width // 2 - len(hint) // 2,
                             hint, curses.color_pair(6) | curses.A_DIM)
        except:
            pass
        
        self.stdscr.refresh()
        
        # Handle input
        while True:
            key = self.stdscr.getch()
            
            if key == curses.KEY_UP or key == ord('w'):
                self.selected_option = (self.selected_option - 1) % len(options)
                return None
            elif key == curses.KEY_DOWN or key == ord('s'):
                self.selected_option = (self.selected_option + 1) % len(options)
                return None
            elif key == ord('\n') or key == ord(' '):
                if self.selected_option == 0:
                    return 'start'
                elif self.selected_option == 1:
                    return 'settings'
                elif self.selected_option == 2:
                    return 'quit'
    
    def _show_settings_menu(self):
        """Show settings menu"""
        self.stdscr.clear()
        
        title = "SETTINGS"
        try:
            self.stdscr.addstr(5, self.width // 2 - len(title) // 2,
                             title, curses.color_pair(5) | curses.A_BOLD)
        except:
            pass
        
        # Settings options
        settings_y = 7
        options = [
            f"Level Length: {self.settings.level_length}m",
            f"Endless Mode: {'ON' if self.settings.endless_mode else 'OFF'}",
            f"Randomize Levels: {'ON' if self.settings.randomize_levels else 'OFF'}",
            f"Music: {'ON' if self.settings.music_enabled else 'OFF'}",
            f"Difficulty: {self.settings.difficulty.upper()}",
            "CONFIGURE LEVELS",
            "SOUND MIXER",
            "SAVE SETTINGS",
            "BACK"
        ]
        
        for i, option in enumerate(options):
            x = self.width // 2 - len(option) // 2
            if i == self.selected_option:
                try:
                    self.stdscr.addstr(settings_y + i * 2, x - 2, "> ",
                                     curses.color_pair(2) | curses.A_BOLD)
                    self.stdscr.addstr(settings_y + i * 2, x, option,
                                     curses.color_pair(3) | curses.A_BOLD | curses.A_REVERSE)
                except:
                    pass
            else:
                try:
                    self.stdscr.addstr(settings_y + i * 2, x, option,
                                     curses.color_pair(6))
                except:
                    pass
        
        # Controls hint
        hint = "[UP/DOWN: Navigate] [LEFT/RIGHT: Change] [ENTER: Select] [ESC: Back]"
        try:
            self.stdscr.addstr(self.height - 3, self.width // 2 - len(hint) // 2,
                             hint, curses.color_pair(6) | curses.A_DIM)
        except:
            pass
        
        self.stdscr.refresh()
        
        # Handle input
        key = self.stdscr.getch()
        
        if key == curses.KEY_UP or key == ord('w'):
            self.selected_option = (self.selected_option - 1) % len(options)
        elif key == curses.KEY_DOWN or key == ord('s'):
            self.selected_option = (self.selected_option + 1) % len(options)
        elif key == curses.KEY_LEFT or key == ord('a'):
            if self.selected_option == 0:  # Level length
                self.settings.level_length = max(100, self.settings.level_length - 100)
            elif self.selected_option == 1:  # Endless mode
                self.settings.endless_mode = not self.settings.endless_mode
            elif self.selected_option == 2:  # Randomize levels
                self.settings.randomize_levels = not self.settings.randomize_levels
            elif self.selected_option == 3:  # Music
                self.settings.music_enabled = not self.settings.music_enabled
                # Control menu music based on setting
                if self.game:
                    if self.settings.music_enabled:
                        self.game.music_manager.play_menu_music(self.settings)
                    else:
                        self.game.music_manager.stop_menu_music()
            elif self.selected_option == 4:  # Difficulty
                difficulties = ['easy', 'normal', 'hard']
                idx = difficulties.index(self.settings.difficulty)
                self.settings.difficulty = difficulties[(idx - 1) % len(difficulties)]
        elif key == curses.KEY_RIGHT or key == ord('d'):
            if self.selected_option == 0:  # Level length
                self.settings.level_length = min(2000, self.settings.level_length + 100)
            elif self.selected_option == 1:  # Endless mode
                self.settings.endless_mode = not self.settings.endless_mode
            elif self.selected_option == 2:  # Randomize levels
                self.settings.randomize_levels = not self.settings.randomize_levels
            elif self.selected_option == 3:  # Music
                self.settings.music_enabled = not self.settings.music_enabled
                # Control menu music based on setting
                if self.game:
                    if self.settings.music_enabled:
                        self.game.music_manager.play_menu_music(self.settings)
                    else:
                        self.game.music_manager.stop_menu_music()
            elif self.selected_option == 4:  # Difficulty
                difficulties = ['easy', 'normal', 'hard']
                idx = difficulties.index(self.settings.difficulty)
                self.settings.difficulty = difficulties[(idx + 1) % len(difficulties)]
        elif key == ord('\n') or key == ord(' '):
            if self.selected_option == 5:  # Configure Levels
                self.menu_state = 'level_select'
                self.selected_option = 0
                return None
            elif self.selected_option == 6:  # Sound Mixer
                return 'mixer'
            elif self.selected_option == 7:  # Save Settings
                if self.settings.save():
                    # Show confirmation briefly
                    try:
                        self.stdscr.addstr(self.height - 5, self.width // 2 - 10,
                                         "Settings Saved!", curses.color_pair(3) | curses.A_BOLD)
                        self.stdscr.refresh()
                        import time
                        time.sleep(0.5)
                    except:
                        pass
            elif self.selected_option == 8:  # Back
                return 'back'
        elif key == 27:  # ESC
            return 'back'
        
        return None
    
    def _show_level_select(self):
        """Show level configuration menu"""
        self.stdscr.clear()
        
        title = "CONFIGURE LEVELS"
        try:
            self.stdscr.addstr(3, self.width // 2 - len(title) // 2,
                             title, curses.color_pair(5) | curses.A_BOLD)
        except:
            pass
        
        # Instructions
        instructions = [
            "[UP/DOWN: Navigate] [SPACE: Enable/Disable] [LEFT/RIGHT: Reorder]",
            "[ENTER: Done] [ESC: Cancel]"
        ]
        
        for i, inst in enumerate(instructions):
            try:
                self.stdscr.addstr(5 + i, self.width // 2 - len(inst) // 2,
                                 inst, curses.color_pair(6) | curses.A_DIM)
            except:
                pass
        
        # Get level names dynamically from LEVELS
        from level_specs import LEVELS
        level_names = [level.name for level in LEVELS]
        num_levels = len(level_names)
        
        levels_y = 10
        
        # Display level list with enable status and order
        for i in range(num_levels):
            # Get the level index at this position in play order
            level_idx = self.settings.level_order[i] if i < len(self.settings.level_order) else i
            level_name = level_names[level_idx] if level_idx < num_levels else f"Level {level_idx}"
            enabled = self.settings.enabled_levels[level_idx] if level_idx < len(self.settings.enabled_levels) else True
            
            status = "[ON]" if enabled else "[OFF]"
            # Use wider field for level name to prevent cutoff
            display = f"{i+1}. {level_name:15s} {status}"
            
            x = self.width // 2 - 25
            
            if i == self.selected_option:
                try:
                    self.stdscr.addstr(levels_y + i * 2, x - 2, "> ",
                                     curses.color_pair(2) | curses.A_BOLD)
                    color = curses.color_pair(3) | curses.A_BOLD | curses.A_REVERSE
                    if not enabled:
                        color = curses.color_pair(1) | curses.A_BOLD | curses.A_REVERSE
                    self.stdscr.addstr(levels_y + i * 2, x, display, color)
                except:
                    pass
            else:
                try:
                    color = curses.color_pair(6)
                    if not enabled:
                        color = curses.color_pair(1) | curses.A_DIM
                    self.stdscr.addstr(levels_y + i * 2, x, display, color)
                except:
                    pass
        
        # Show active levels count (dynamic total)
        active_count = len(self.settings.get_active_levels())
        total_levels = num_levels
        info = f"Active Levels: {active_count}/{total_levels}"
        try:
            # Position dynamically based on number of levels
            self.stdscr.addstr(levels_y + num_levels * 2 + 2, self.width // 2 - len(info) // 2,
                             info, curses.color_pair(3) | curses.A_BOLD)
        except:
            pass
        
        self.stdscr.refresh()
        
        # Handle input
        key = self.stdscr.getch()
        
        if key == curses.KEY_UP or key == ord('w'):
            self.selected_option = (self.selected_option - 1) % num_levels
        elif key == curses.KEY_DOWN or key == ord('s'):
            self.selected_option = (self.selected_option + 1) % num_levels
        elif key == ord(' '):
            # Toggle enable/disable for selected level
            level_idx = self.settings.level_order[self.selected_option]
            self.settings.enabled_levels[level_idx] = not self.settings.enabled_levels[level_idx]
            # Ensure at least one level is enabled
            if not any(self.settings.enabled_levels):
                self.settings.enabled_levels[level_idx] = True
        elif key == curses.KEY_LEFT or key == ord('a'):
            # Move level up in order
            if self.selected_option > 0:
                idx = self.selected_option
                if idx < len(self.settings.level_order) and idx - 1 < len(self.settings.level_order):
                    self.settings.level_order[idx], self.settings.level_order[idx-1] = \
                        self.settings.level_order[idx-1], self.settings.level_order[idx]
                self.selected_option -= 1
        elif key == curses.KEY_RIGHT or key == ord('d'):
            # Move level down in order
            from level_specs import LEVELS
            num_levels = len(LEVELS)
            if self.selected_option < num_levels - 1:
                idx = self.selected_option
                if idx < len(self.settings.level_order) and idx + 1 < len(self.settings.level_order):
                    self.settings.level_order[idx], self.settings.level_order[idx+1] = \
                        self.settings.level_order[idx+1], self.settings.level_order[idx]
                    self.selected_option += 1
        elif key == ord('\n'):
            return 'back'
        elif key == 27:  # ESC
            return 'back'
        
        return None
    
    def _show_mixer_menu(self):
        """Show sound mixer menu"""
        if self.sound_mixer:
            # Load current settings into mixer
            self.sound_mixer.load_from_settings(self.settings)
            
            if self.sound_mixer.show():
                self.music_changed = True
                # Save mixer settings back to settings
                self.sound_mixer.save_to_settings(self.settings)
                # Auto-save settings
                self.settings.save()
        return 'back'


class GameOverMenu:
    """Game over screen with menu options"""
    
    def __init__(self, stdscr, width, height):
        self.stdscr = stdscr
        self.width = width
        self.height = height
        self.selected_option = 0
    
    def show(self, score, distance):
        """Display game over menu and return user choice"""
        self.stdscr.nodelay(0)  # Wait for input
        
        while True:
            self.stdscr.clear()
            
            # Game over text
            game_over_text = [
                "  ___   _   __  __ ___    _____   _______ ___ ",
                " / __| /_\\ |  \\/  | __|  / _ \\ \\ / / __| _ \\",
                "| (_ |/ _ \\| |\\/| | _|  | (_) \\ V /| _||   /",
                " \\___/_/ \\_\\_|  |_|___|  \\___/ \\_/ |___|_|_\\"
            ]
            
            start_y = self.height // 2 - len(game_over_text) - 8
            for i, line in enumerate(game_over_text):
                x = self.width // 2 - len(line) // 2
                if x >= 0 and start_y + i >= 0:
                    try:
                        self.stdscr.addstr(start_y + i, x, line,
                                         curses.color_pair(1) | curses.A_BOLD)
                    except:
                        pass
            
            # Stats
            final_score = f"FINAL SCORE: {score}"
            final_dist = f"DISTANCE: {int(distance)}m"
            
            try:
                self.stdscr.addstr(start_y + len(game_over_text) + 2,
                                 self.width // 2 - len(final_score) // 2,
                                 final_score, curses.color_pair(3) | curses.A_BOLD)
                self.stdscr.addstr(start_y + len(game_over_text) + 3,
                                 self.width // 2 - len(final_dist) // 2,
                                 final_dist, curses.color_pair(5) | curses.A_BOLD)
            except:
                pass
            
            # Menu options
            options = ["RESTART", "MAIN MENU", "QUIT"]
            menu_y = start_y + len(game_over_text) + 7
            
            for i, option in enumerate(options):
                x = self.width // 2 - len(option) // 2
                if i == self.selected_option:
                    try:
                        self.stdscr.addstr(menu_y + i * 2, x - 2, "> ",
                                         curses.color_pair(2) | curses.A_BOLD)
                        self.stdscr.addstr(menu_y + i * 2, x, option,
                                         curses.color_pair(3) | curses.A_BOLD | curses.A_REVERSE)
                    except:
                        pass
                else:
                    try:
                        self.stdscr.addstr(menu_y + i * 2, x, option,
                                         curses.color_pair(6))
                    except:
                        pass
            
            # Controls hint
            hint = "[UP/DOWN: Navigate] [ENTER: Select]"
            try:
                self.stdscr.addstr(self.height - 3, self.width // 2 - len(hint) // 2,
                                 hint, curses.color_pair(6) | curses.A_DIM)
            except:
                pass
            
            self.stdscr.refresh()
            
            # Handle input
            key = self.stdscr.getch()
            
            if key == curses.KEY_UP or key == ord('w'):
                self.selected_option = (self.selected_option - 1) % len(options)
            elif key == curses.KEY_DOWN or key == ord('s'):
                self.selected_option = (self.selected_option + 1) % len(options)
            elif key == ord('\n') or key == ord(' '):
                if self.selected_option == 0:
                    return 'restart'
                elif self.selected_option == 1:
                    return 'menu'
                elif self.selected_option == 2:
                    return 'quit'

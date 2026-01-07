"""
Menu system for ASCII OutRun
Handles main menu, settings, and navigation
"""

import curses


class GameSettings:
    """Holds game settings"""
    def __init__(self):
        self.level_order = [0, 1, 2, 3]  # Beach, City, Factory, Desert
        self.starting_level = 0
        self.music_enabled = True
        self.difficulty = 'normal'  # 'easy', 'normal', 'hard'


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
            "   ___  __  __________ __  ___   __",
            "  / _ \\/ / / /_  __/ _ \\ / / / | / /",
            " / // / /_/ / / / / , _/ /_/ /  |/ /",
            "/____/\\____/ /_/ /_/|_|\\____/_/|___/"
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
        settings_y = 10
        options = [
            f"Starting Level: {['Beach', 'City', 'Factory', 'Desert'][self.settings.starting_level]}",
            f"Music: {'ON' if self.settings.music_enabled else 'OFF'}",
            f"Difficulty: {self.settings.difficulty.upper()}",
            "SOUND MIXER",
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
            if self.selected_option == 0:  # Starting level
                self.settings.starting_level = (self.settings.starting_level - 1) % 4
            elif self.selected_option == 1:  # Music
                self.settings.music_enabled = not self.settings.music_enabled
                # Control menu music based on setting
                if self.game:
                    if self.settings.music_enabled:
                        self.game.play_menu_music()
                    else:
                        self.game.stop_menu_music()
            elif self.selected_option == 2:  # Difficulty
                difficulties = ['easy', 'normal', 'hard']
                idx = difficulties.index(self.settings.difficulty)
                self.settings.difficulty = difficulties[(idx - 1) % len(difficulties)]
        elif key == curses.KEY_RIGHT or key == ord('d'):
            if self.selected_option == 0:  # Starting level
                self.settings.starting_level = (self.settings.starting_level + 1) % 4
            elif self.selected_option == 1:  # Music
                self.settings.music_enabled = not self.settings.music_enabled
                # Control menu music based on setting
                if self.game:
                    if self.settings.music_enabled:
                        self.game.play_menu_music()
                    else:
                        self.game.stop_menu_music()
            elif self.selected_option == 2:  # Difficulty
                difficulties = ['easy', 'normal', 'hard']
                idx = difficulties.index(self.settings.difficulty)
                self.settings.difficulty = difficulties[(idx + 1) % len(difficulties)]
        elif key == ord('\n') or key == ord(' '):
            if self.selected_option == 3:  # Sound Mixer
                return 'mixer'
            elif self.selected_option == 4:  # Back
                return 'back'
        elif key == 27:  # ESC
            return 'back'
        
        return None
    
    def _show_mixer_menu(self):
        """Show sound mixer menu"""
        if self.sound_mixer:
            if self.sound_mixer.show():
                self.music_changed = True
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

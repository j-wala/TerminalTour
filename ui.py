"""
UI components for Terminal Tour
Handles HUD, menus, and screen displays
"""

import curses


class HUDRenderer:
    """Renders the heads-up display"""
    
    def __init__(self, stdscr, width, height):
        self.stdscr = stdscr
        self.width = width
        self.height = height
    
    def render(self, game_state, current_level_name):
        """Render all HUD elements"""
        try:
            # Speed indicator
            speed_text = f"SPEED: {int(game_state.speed * 100)} km/h"
            self.stdscr.addstr(self.height - 1, 2, speed_text, 
                             curses.color_pair(2) | curses.A_BOLD)
            
            # Score
            score_text = f"SCORE: {game_state.score}"
            self.stdscr.addstr(self.height - 1, self.width - len(score_text) - 2, 
                             score_text, curses.color_pair(3) | curses.A_BOLD)
            
            # Distance
            dist_text = f"DISTANCE: {int(game_state.distance)}m"
            self.stdscr.addstr(self.height - 1, self.width // 2 - len(dist_text) // 2, 
                             dist_text, curses.color_pair(5) | curses.A_BOLD)
            
            # Music status
            sound_text = f"[M]USIC: {'ON' if game_state.music_enabled else 'OFF'}"
            sound_color = curses.color_pair(3) if game_state.music_enabled else curses.color_pair(1)
            self.stdscr.addstr(0, 2, sound_text, sound_color)
            
            # Current level
            level_text = f"LEVEL: {current_level_name}"
            level_colors = [curses.color_pair(2), curses.color_pair(4), curses.color_pair(1)]
            level_index = min(2, int(game_state.distance / 500))
            self.stdscr.addstr(0, self.width - len(level_text) - 2, level_text, 
                             level_colors[level_index] | curses.A_BOLD)
            
            # Level transition message
            if game_state.level_transition_timer > 0:
                transition_y = self.height // 2
                transition_x = self.width // 2 - len(game_state.level_transition_message) // 2
                if transition_x >= 0:
                    self.stdscr.addstr(transition_y, transition_x, 
                                     game_state.level_transition_message,
                                     curses.color_pair(5) | curses.A_BOLD | curses.A_REVERSE)
                game_state.level_transition_timer -= 1
        except:
            pass


class TitleScreen:
    """Handles the title screen display"""
    
    def __init__(self, stdscr, width, height):
        self.stdscr = stdscr
        self.width = width
        self.height = height
    
    def show(self):
        """Display the title screen and wait for input"""
        self.stdscr.clear()
        
        title = [
            "╔╦╗┌─┐┬─┐┌┬┐┬┌┐┌┌─┐┬  ",
            " ║ ├┤ ├┬┘│││││││├─┤│  ",
            " ╩ └─┘┴└─┴ ┴┴┘└┘┴ ┴┴─┘",
            "     ╔╦╗┌─┐┬ ┬┬─┐     ",
            "      ║ │ ││ │├┬┘     ",
            "      ╩ └─┘└─┘┴└─     "
        ]
        
        start_y = self.height // 2 - len(title) - 5
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
        
        instructions = [
            "CONTROLS:",
            "Arrow Keys / WASD - Move & Speed",
            "M - Toggle Music",
            "Q - Quit",
            "",
            "Press any key to start..."
        ]
        
        inst_y = start_y + len(title) + 5
        for i, line in enumerate(instructions):
            x = self.width // 2 - len(line) // 2
            try:
                color = curses.color_pair(4) if i == 0 else curses.color_pair(6)
                self.stdscr.addstr(inst_y + i, x, line, color)
            except:
                pass
        
        self.stdscr.refresh()
        self.stdscr.nodelay(0)
        self.stdscr.getch()
        self.stdscr.nodelay(1)


class GameOverScreen:
    """Handles the game over screen display"""
    
    def __init__(self, stdscr, width, height):
        self.stdscr = stdscr
        self.width = width
        self.height = height
    
    def show(self, score, distance):
        """Display the game over screen"""
        self.stdscr.clear()
        
        game_over_text = [
            "  ___   _   __  __ ___    _____   _______ ___ ",
            " / __| /_\\ |  \\/  | __|  / _ \\ \\ / / __| _ \\",
            "| (_ |/ _ \\| |\\/| | _|  | (_) \\ V /| _||   /",
            " \\___/_/ \\_\\_|  |_|___|  \\___/ \\_/ |___|_|_\\"
        ]
        
        start_y = self.height // 2 - len(game_over_text) - 5
        for i, line in enumerate(game_over_text):
            x = self.width // 2 - len(line) // 2
            if x >= 0 and start_y + i >= 0:
                try:
                    self.stdscr.addstr(start_y + i, x, line, 
                                     curses.color_pair(1) | curses.A_BOLD)
                except:
                    pass
        
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
        
        restart_text = "Press R to restart or Q to quit"
        try:
            self.stdscr.addstr(start_y + len(game_over_text) + 6,
                             self.width // 2 - len(restart_text) // 2,
                             restart_text, curses.color_pair(6))
        except:
            pass
        
        self.stdscr.refresh()
    
    def handle_input(self, stdscr):
        """Handle input on game over screen. Returns 'restart', 'quit', or None"""
        import curses
        
        try:
            key = stdscr.getch()
            if key == ord('r') or key == ord('R'):
                return 'restart'
            elif key == ord('q') or key == ord('Q'):
                return 'quit'
        except:
            pass
        
        return None

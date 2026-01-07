"""
Pause menu system for ASCII OutRun
Handles pause state and pause music
"""

import curses
import pygame
import numpy as np
from jingles import generate_pause_music


class PauseMenu:
    """Pause menu with music"""
    
    def __init__(self, stdscr, width, height):
        self.stdscr = stdscr
        self.width = width
        self.height = height
        self.selected_option = 0
        self.pause_music = None
        self.pause_music_duration = 0
        self.pause_music_playing = False
        
        # Initialize pause music
        self.init_pause_music()
    
    def init_pause_music(self):
        """Initialize calming pause music"""
        try:
            self.pause_music, self.pause_music_duration = generate_pause_music()
        except Exception as e:
            import sys
            print(f"Error initializing pause music: {e}", file=sys.stderr)
    
    def start_pause_music(self):
        """Start playing pause music in loop"""
        if self.pause_music and not self.pause_music_playing:
            self.pause_music_playing = True
            self.pause_music.play(loops=-1)  # Loop indefinitely
    
    def stop_pause_music(self):
        """Stop pause music"""
        self.pause_music_playing = False
        if self.pause_music:
            try:
                self.pause_music.stop()
            except:
                pass
    
    def show(self):
        """Display pause menu and return action"""
        self.stdscr.nodelay(0)  # Wait for input
        self.selected_option = 0
        
        # Start pause music
        self.start_pause_music()
        
        while True:
            self.stdscr.clear()
            
            # Title
            title = "PAUSED"
            try:
                self.stdscr.addstr(self.height // 2 - 6, self.width // 2 - len(title) // 2,
                                 title, curses.color_pair(2) | curses.A_BOLD)
            except:
                pass
            
            # Menu options
            options = ["RESUME", "RESTART", "MAIN MENU", "QUIT"]
            menu_y = self.height // 2 - 2
            
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
            hint = "[UP/DOWN: Navigate] [ENTER: Select] [ESC: Resume]"
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
                self.stop_pause_music()
                if self.selected_option == 0:
                    return 'resume'
                elif self.selected_option == 1:
                    return 'restart'
                elif self.selected_option == 2:
                    return 'menu'
                elif self.selected_option == 3:
                    return 'quit'
            elif key == 27:  # ESC
                self.stop_pause_music()
                return 'resume'

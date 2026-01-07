"""
Countdown timer for game start
Displays 3...2...1...GO!
"""

import curses
import time


class CountdownTimer:
    """Displays countdown before game starts"""
    
    def __init__(self, stdscr, width, height):
        self.stdscr = stdscr
        self.width = width
        self.height = height
    
    def show(self, render_callback=None):
        """Display countdown animation with optional background rendering"""
        countdown_sequence = ["3", "2", "1", "GO!"]
        delay = 0.8  # Seconds between counts
        
        # Save original nodelay setting
        # Note: We'll set it to non-blocking during countdown
        self.stdscr.nodelay(1)
        
        for count in countdown_sequence:
            # Render game background if callback provided
            if render_callback:
                render_callback()
            else:
                self.stdscr.clear()
            
            # Center the countdown text
            text = count
            y = self.height // 2
            x = self.width // 2 - len(text) // 2
            
            # Determine color and style based on count
            if count == "GO!":
                color = curses.color_pair(3) | curses.A_BOLD  # Green
                text_large = self._make_large_text(count)
            elif count == "1":
                color = curses.color_pair(2) | curses.A_BOLD  # Yellow
                text_large = self._make_large_text(count)
            else:
                color = curses.color_pair(1) | curses.A_BOLD  # Red
                text_large = self._make_large_text(count)
            
            # Draw large text as overlay
            self._draw_large_text(text_large, y - len(text_large) // 2, color)
            
            self.stdscr.refresh()
            time.sleep(delay)
        
        # Brief pause after GO!
        time.sleep(0.3)
        
        # Ensure nodelay is set to 1 for gameplay
        self.stdscr.nodelay(1)
    
    def _make_large_text(self, text):
        """Create ASCII art for countdown numbers"""
        large_digits = {
            "3": [
                " ##### ",
                "     # ",
                " ##### ",
                "     # ",
                " ##### "
            ],
            "2": [
                " ##### ",
                "     # ",
                " ##### ",
                " #     ",
                " ##### "
            ],
            "1": [
                "   #   ",
                "  ##   ",
                "   #   ",
                "   #   ",
                " ##### "
            ],
            "GO!": [
                "  ###   ###   # ",
                " #     #   #  # ",
                " # ##  #   #  # ",
                " #  #  #   #    ",
                "  ###   ###   # "
            ]
        }
        
        return large_digits.get(text, [text])
    
    def _draw_large_text(self, text_lines, start_y, color):
        """Draw large ASCII art text centered on screen"""
        for i, line in enumerate(text_lines):
            y = start_y + i
            x = self.width // 2 - len(line) // 2
            
            if 0 <= y < self.height and 0 <= x < self.width:
                try:
                    self.stdscr.addstr(y, x, line, color)
                except:
                    pass

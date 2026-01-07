"""
Transition effects for level changes
"""

import curses


class TransitionEffect:
    """Handles element-based transitions between levels"""
    
    def __init__(self, stdscr, width, height):
        self.stdscr = stdscr
        self.width = width
        self.height = height
        self.transition_stage = 'none'  # 'none', 'horizon_out', 'color_fade', 'horizon_in'
        self.transition_progress = 0
    
    def render_sky_gradient(self, from_color, to_color, progress):
        """Render a gradient transition in the sky area"""
        sky_height = min(15, self.height // 3)
        
        for row in range(sky_height):
            for col in range(self.width):
                try:
                    # Interpolate between colors based on progress
                    if progress < 0.5:
                        color = curses.color_pair(from_color) | curses.A_DIM
                    else:
                        color = curses.color_pair(to_color) | curses.A_DIM
                    
                    # Add some dithering for smoother transition
                    if 0.3 < progress < 0.7:
                        if (row + col) % 2 == 0:
                            color = curses.color_pair(from_color) | curses.A_DIM
                        else:
                            color = curses.color_pair(to_color) | curses.A_DIM
                    
                    self.stdscr.addch(row, col, ' ', color | curses.A_REVERSE)
                except:
                    pass
    
    def render_wipe(self, wipe_progress, direction='down'):
        """
        Render a wipe transition effect
        wipe_progress: 0.0 to 1.0
        direction: 'down', 'up', 'left', 'right'
        """
        if direction == 'down':
            wipe_row = int(wipe_progress * self.height)
            for row in range(wipe_row):
                for col in range(self.width):
                    try:
                        self.stdscr.addch(row, col, ' ', curses.A_REVERSE)
                    except:
                        pass
        
        elif direction == 'up':
            wipe_row = int((1.0 - wipe_progress) * self.height)
            for row in range(wipe_row, self.height):
                for col in range(self.width):
                    try:
                        self.stdscr.addch(row, col, ' ', curses.A_REVERSE)
                    except:
                        pass

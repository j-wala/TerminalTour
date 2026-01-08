"""
In-game sound mixer for controlling instrument volumes
"""

import curses


class SoundMixer:
    """In-game sound mixer menu"""
    
    def __init__(self, stdscr, width, height):
        self.stdscr = stdscr
        self.width = width
        self.height = height
        self.selected_option = 0
        self.volumes = {
            'melody': 0.35,
            'bass': 0.35,
            'harmony': 0.15,
            'drums': 0.25,
        }
        self.muted = {
            'melody': False,
            'bass': False,
            'harmony': False,
            'drums': False,
        }
    
    def load_from_settings(self, settings):
        """Load mixer levels from GameSettings"""
        if hasattr(settings, 'mixer_levels'):
            for key in self.volumes.keys():
                if key in settings.mixer_levels:
                    self.volumes[key] = settings.mixer_levels[key]
    
    def save_to_settings(self, settings):
        """Save mixer levels to GameSettings"""
        settings.mixer_levels = self.get_mix_levels()
    
    def show(self):
        """Display mixer menu and return if music should be regenerated"""
        original_volumes = self.volumes.copy()
        original_muted = self.muted.copy()
        
        self.stdscr.nodelay(0)  # Wait for input
        
        while True:
            self.stdscr.clear()
            
            # Title
            title = "SOUND MIXER"
            try:
                self.stdscr.addstr(3, self.width // 2 - len(title) // 2,
                                 title, curses.color_pair(5) | curses.A_BOLD)
            except:
                pass
            
            # Instructions
            instructions = [
                "[LEFT/RIGHT: Adjust Volume]",
                "[M: Toggle Mute]",
                "[ENTER: Apply & Close]",
                "[ESC: Cancel]"
            ]
            
            for i, line in enumerate(instructions):
                try:
                    self.stdscr.addstr(5 + i, self.width // 2 - len(line) // 2,
                                     line, curses.color_pair(6) | curses.A_DIM)
                except:
                    pass
            
            # Mixer controls
            mixer_y = 12
            instruments = ['melody', 'bass', 'harmony', 'drums']
            
            for i, inst in enumerate(instruments):
                y = mixer_y + i * 3
                x = self.width // 2 - 30
                
                # Instrument name
                inst_name = inst.upper()
                if i == self.selected_option:
                    try:
                        self.stdscr.addstr(y, x, "> ", curses.color_pair(2) | curses.A_BOLD)
                    except:
                        pass
                    color = curses.color_pair(3) | curses.A_BOLD
                else:
                    color = curses.color_pair(6)
                
                try:
                    self.stdscr.addstr(y, x + 2, inst_name.ljust(10), color)
                except:
                    pass
                
                # Mute status
                mute_text = "[MUTED]" if self.muted[inst] else ""
                if self.muted[inst]:
                    try:
                        self.stdscr.addstr(y, x + 14, mute_text, 
                                         curses.color_pair(1) | curses.A_BOLD)
                    except:
                        pass
                
                # Volume bar
                bar_x = x + 25
                bar_width = 30
                
                if not self.muted[inst]:
                    filled = int(self.volumes[inst] * bar_width / 1.0)
                    bar = "[" + "=" * filled + " " * (bar_width - filled) + "]"
                    percent = f" {int(self.volumes[inst] * 100)}%"
                else:
                    bar = "[" + " " * bar_width + "]"
                    percent = "  0%"
                
                try:
                    self.stdscr.addstr(y, bar_x, bar, color)
                    self.stdscr.addstr(y, bar_x + len(bar) + 1, percent, color)
                except:
                    pass
            
            # Reset option
            reset_y = mixer_y + len(instruments) * 3 + 2
            reset_text = "RESET TO DEFAULTS"
            if self.selected_option == len(instruments):
                try:
                    self.stdscr.addstr(reset_y, self.width // 2 - len(reset_text) // 2 - 2,
                                     "> ", curses.color_pair(2) | curses.A_BOLD)
                    self.stdscr.addstr(reset_y, self.width // 2 - len(reset_text) // 2,
                                     reset_text, curses.color_pair(3) | curses.A_BOLD | curses.A_REVERSE)
                except:
                    pass
            else:
                try:
                    self.stdscr.addstr(reset_y, self.width // 2 - len(reset_text) // 2,
                                     reset_text, curses.color_pair(6))
                except:
                    pass
            
            self.stdscr.refresh()
            
            # Handle input
            key = self.stdscr.getch()
            
            if key == curses.KEY_UP or key == ord('w'):
                self.selected_option = (self.selected_option - 1) % (len(instruments) + 1)
            
            elif key == curses.KEY_DOWN or key == ord('s'):
                self.selected_option = (self.selected_option + 1) % (len(instruments) + 1)
            
            elif key == curses.KEY_LEFT or key == ord('a'):
                if self.selected_option < len(instruments):
                    inst = instruments[self.selected_option]
                    self.volumes[inst] = max(0.0, self.volumes[inst] - 0.05)
            
            elif key == curses.KEY_RIGHT or key == ord('d'):
                if self.selected_option < len(instruments):
                    inst = instruments[self.selected_option]
                    self.volumes[inst] = min(1.0, self.volumes[inst] + 0.05)
            
            elif key == ord('m') or key == ord('M'):
                if self.selected_option < len(instruments):
                    inst = instruments[self.selected_option]
                    self.muted[inst] = not self.muted[inst]
            
            elif key == ord('\n') or key == ord(' '):
                if self.selected_option == len(instruments):
                    # Reset to defaults
                    self.volumes = {
                        'melody': 0.35,
                        'bass': 0.35,
                        'harmony': 0.15,
                        'drums': 0.25,
                    }
                    self.muted = {k: False for k in self.muted}
                else:
                    # Apply and close
                    self.stdscr.nodelay(1)
                    # Check if anything changed
                    changed = (self.volumes != original_volumes or 
                             self.muted != original_muted)
                    return changed
            
            elif key == 27:  # ESC
                # Cancel - restore original
                self.volumes = original_volumes
                self.muted = original_muted
                self.stdscr.nodelay(1)
                return False
    
    def get_mix_levels(self):
        """Get current mix levels accounting for mutes"""
        return {
            'melody': 0.0 if self.muted['melody'] else self.volumes['melody'],
            'bass': 0.0 if self.muted['bass'] else self.volumes['bass'],
            'harmony': 0.0 if self.muted['harmony'] else self.volumes['harmony'],
            'drums': 0.0 if self.muted['drums'] else self.volumes['drums'],
        }

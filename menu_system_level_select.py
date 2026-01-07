"""
Level configuration menu for MainMenu
This extends the menu system with level selection/ordering
"""

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
    
    level_names = ['Beach', 'City', 'Factory', 'Desert']
    levels_y = 10
    
    # Display level list with enable status and order
    for i in range(len(level_names)):
        # Get the level index at this position in play order
        level_idx = self.settings.level_order[i] if i < len(self.settings.level_order) else i
        level_name = level_names[level_idx]
        enabled = self.settings.enabled_levels[level_idx] if level_idx < len(self.settings.enabled_levels) else True
        
        status = "[ON]" if enabled else "[OFF]"
        display = f"{i+1}. {level_name:10s} {status}"
        
        x = self.width // 2 - 20
        
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
    
    # Show active levels count
    active_count = len(self.settings.get_active_levels())
    info = f"Active Levels: {active_count}/4"
    try:
        self.stdscr.addstr(levels_y + 10, self.width // 2 - len(info) // 2,
                         info, curses.color_pair(3) | curses.A_BOLD)
    except:
        pass
    
    self.stdscr.refresh()
    
    # Handle input
    key = self.stdscr.getch()
    
    if key == curses.KEY_UP or key == ord('w'):
        self.selected_option = (self.selected_option - 1) % 4
    elif key == curses.KEY_DOWN or key == ord('s'):
        self.selected_option = (self.selected_option + 1) % 4
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
            self.settings.level_order[idx], self.settings.level_order[idx-1] = \
                self.settings.level_order[idx-1], self.settings.level_order[idx]
            self.selected_option -= 1
    elif key == curses.KEY_RIGHT or key == ord('d'):
        # Move level down in order
        if self.selected_option < 3:
            idx = self.selected_option
            self.settings.level_order[idx], self.settings.level_order[idx+1] = \
                self.settings.level_order[idx+1], self.settings.level_order[idx]
            self.selected_option += 1
    elif key == ord('\n'):
        return 'back'
    elif key == 27:  # ESC
        return 'back'
    
    return None

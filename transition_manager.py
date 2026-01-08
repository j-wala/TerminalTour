"""
Level transition management for Terminal Tour
Handles smooth transitions between game levels
"""

from level_specs import LEVELS, get_level_for_distance


class TransitionManager:
    """Manages level transitions and effects"""
    
    def __init__(self, game_state):
        self.game_state = game_state
        self.transition_target_level = None
        self.previous_level = None
        self.current_level = None
    
    def check_and_update_transition(self, current_level, settings, music_manager, sky_renderer, scenery_renderer):
        """Check if a transition should start and update transition state"""
        transition_window = 50  # meters
        
        # Get active level indices
        active_indices = settings.get_active_levels() if settings else [0, 1, 2, 3]
        if not active_indices:
            return current_level
        
        # Calculate current level index based on distance
        if settings and settings.endless_mode:
            total_length = len(active_indices) * settings.level_length
            normalized_distance = self.game_state.distance % total_length
            current_level_idx = int(normalized_distance / settings.level_length)
        else:
            current_level_idx = int(self.game_state.distance / settings.level_length) if settings else 0
        
        # Calculate next level index
        next_level_idx = (current_level_idx + 1) % len(active_indices)
        
        # Get threshold for next level
        if settings and settings.endless_mode:
            total_length = len(active_indices) * settings.level_length
            base_threshold = (current_level_idx + 1) * settings.level_length
            normalized_distance = self.game_state.distance % total_length
            distance_to_threshold = base_threshold - normalized_distance
        else:
            next_threshold = (current_level_idx + 1) * (settings.level_length if settings else 500)
            distance_to_threshold = next_threshold - self.game_state.distance
        
        # Start transition when within window before threshold
        if (0 <= distance_to_threshold <= transition_window and 
            self.game_state.transition_stage == 'none' and 
            not self.game_state.transition_triggered):
            
            if current_level_idx < len(active_indices) - 1 or (settings and settings.endless_mode):
                next_level_index = active_indices[next_level_idx]
                new_level = LEVELS[next_level_index]
                
                self.transition_target_level = new_level
                self.previous_level = current_level
                
                self.game_state.transition_stage = 'horizon_out'
                self.game_state.transition_progress = 0
                self.game_state.transition_triggered = True
                self.game_state.old_level_color = current_level.sky_config.color_pair
                self.game_state.new_level_color = new_level.sky_config.color_pair
        
        # Handle transition stages
        new_level = self._update_transition_stage(
            current_level, 
            music_manager, 
            sky_renderer, 
            scenery_renderer,
            settings
        )
        
        return new_level if new_level else current_level
    
    def _update_transition_stage(self, current_level, music_manager, sky_renderer, scenery_renderer, settings):
        """Update the current transition stage"""
        if self.game_state.transition_stage == 'horizon_out':
            return self._handle_horizon_out(music_manager)
        
        elif self.game_state.transition_stage == 'color_fade':
            return self._handle_color_fade(sky_renderer, scenery_renderer, music_manager, settings)
        
        elif self.game_state.transition_stage == 'horizon_in':
            return self._handle_horizon_in(music_manager)
        
        return None
    
    def _handle_horizon_out(self, music_manager):
        """Handle horizon fade out stage"""
        self.game_state.transition_progress += 0.1
        
        # Fade out music volume
        fade_volume = 1.0 - self.game_state.transition_progress
        music_manager.fade_volume(fade_volume)
        
        if self.game_state.transition_progress >= 1.0:
            self.game_state.transition_stage = 'color_fade'
            self.game_state.transition_progress = 0
            music_manager.stop_game_music()
        
        return None
    
    def _handle_color_fade(self, sky_renderer, scenery_renderer, music_manager, settings):
        """Handle color fade stage"""
        self.game_state.transition_progress += 0.08
        
        if self.game_state.transition_progress >= 1.0:
            # Use the stored target level
            if self.transition_target_level:
                new_level = self.transition_target_level
            else:
                new_level = get_level_for_distance(self.game_state.distance, settings)
            
            self.game_state.level_transition_message = f"ENTERING {new_level.name} ZONE!"
            self.game_state.level_transition_timer = 60
            
            # Clear old objects
            sky_renderer.clear_objects()
            scenery_renderer.clear_objects()
            
            # Load music from cache (instant)
            try:
                music_manager.play_level_music(new_level, self.game_state)
                music_manager.fade_volume(0.0)  # Start silent
            except:
                pass
            
            self.game_state.transition_stage = 'horizon_in'
            self.game_state.transition_progress = 0
            
            return new_level
        
        return None
    
    def _handle_horizon_in(self, music_manager):
        """Handle horizon fade in stage"""
        self.game_state.transition_progress += 0.1
        
        # Fade in music volume
        fade_volume = self.game_state.transition_progress
        music_manager.fade_volume(fade_volume)
        
        if self.game_state.transition_progress >= 1.0:
            self.game_state.transition_stage = 'none'
            self.game_state.transition_progress = 0
            self.game_state.transition_triggered = False
            
            # Ensure volume is at full
            music_manager.fade_volume(1.0)
        
        return None

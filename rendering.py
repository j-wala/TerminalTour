"""
Rendering components for ASCII OutRun
Modular rendering system for game objects
"""

import curses
import random
from typing import List, Dict, Any


class SkyRenderer:
    """Handles sky rendering for different level types"""
    
    def __init__(self, stdscr, width, height):
        self.stdscr = stdscr
        self.width = width
        self.height = height
        self.sky_objects = []
        self.background_offset = 0
    
    def clear_objects(self):
        """Clear all sky objects"""
        self.sky_objects = []
    
    def render(self, level_spec, curve_offset=0):
        """Render sky based on level specification"""
        sky_height = min(15, self.height // 3)
        sky_config = level_spec.sky_config
        
        # Render sky background with gradient
        for row in range(sky_height):
            gradient_intensity = 1.0 - (row / max(sky_height, 1)) * 0.3
            for col in range(self.width):
                try:
                    if gradient_intensity > 0.85:
                        color = curses.color_pair(sky_config.color_pair)
                    elif gradient_intensity > 0.7:
                        color = curses.color_pair(sky_config.color_pair) | curses.A_DIM
                    else:
                        color = curses.color_pair(sky_config.color_pair) | curses.A_DIM
                    self.stdscr.addch(row, col, ' ', color | curses.A_REVERSE)
                except:
                    pass
        
        if len(self.sky_objects) == 0:
            self._initialize_sky_objects(sky_config, sky_height)
        
        self._render_sky_objects(sky_height)
        self._render_horizon_decorations(level_spec, sky_height, curve_offset)
    
    def _initialize_sky_objects(self, sky_config, sky_height):
        """Initialize sky objects based on config"""
        for obj_def in sky_config.objects:
            obj_type = obj_def['type']
            
            if obj_type == 'sun':
                sun_x = self.width - 15
                sun_y = 3
                self.sky_objects.append({
                    'type': 'sun',
                    'x': sun_x,
                    'y': sun_y
                })
            
            elif obj_type == 'cloud':
                count = obj_def.get('count', 3)
                speed = obj_def.get('speed', 0.1)
                for _ in range(count):
                    cloud_x = random.randint(10, self.width - 20)
                    cloud_y = random.randint(2, max(2, sky_height - 3))
                    self.sky_objects.append({
                        'type': 'cloud',
                        'x': cloud_x,
                        'y': cloud_y,
                        'offset': random.randint(0, 50),
                        'speed': speed
                    })
            
            elif obj_type == 'smoke':
                count = obj_def.get('count', 8)
                speed = obj_def.get('speed', 0.3)
                for _ in range(count):
                    smoke_x = random.randint(10, self.width - 10)
                    smoke_y = random.randint(3, max(3, sky_height - 1))
                    self.sky_objects.append({
                        'type': 'smoke',
                        'x': smoke_x,
                        'y': smoke_y,
                        'offset': 0,
                        'speed': speed
                    })
    
    def _render_sky_objects(self, sky_height):
        """Render all sky objects"""
        for obj in self.sky_objects:
            if obj['type'] == 'sun':
                self._render_sun(obj, sky_height)
            elif obj['type'] == 'cloud':
                self._render_cloud(obj, sky_height)
            elif obj['type'] == 'smoke':
                self._render_smoke(obj, sky_height)
    
    def _render_sun(self, obj, sky_height):
        """Render sun object"""
        sun_art = [
            "  \\|/  ",
            " -(@)- ",
            "  /|\\  "
        ]
        for i, line in enumerate(sun_art):
            for j, ch in enumerate(line):
                x = obj['x'] + j
                y = obj['y'] + i
                if 0 <= x < self.width and 0 <= y < sky_height:
                    try:
                        self.stdscr.addch(y, x, ch, curses.color_pair(2) | curses.A_BOLD)
                    except:
                        pass
    
    def _render_cloud(self, obj, sky_height):
        """Render animated cloud"""
        obj['offset'] = (obj['offset'] + obj['speed']) % self.width
        cloud_x = int(obj['x'] + obj['offset']) % self.width
        cloud_art = "  .--.  "
        
        for j, ch in enumerate(cloud_art):
            x = cloud_x + j
            if 0 <= x < self.width and 0 <= obj['y'] < sky_height:
                try:
                    color = curses.color_pair(6)
                    if obj.get('dimmed', False):
                        color |= curses.A_DIM
                    self.stdscr.addch(obj['y'], x, ch, color)
                except:
                    pass
    
    def _render_smoke(self, obj, sky_height):
        """Render animated smoke particles"""
        obj['offset'] = (obj['offset'] + obj['speed']) % 10
        smoke_chars = ['~', '≈', '∼']
        char = smoke_chars[int(obj['offset']) % len(smoke_chars)]
        
        if 0 <= obj['x'] < self.width and 0 <= obj['y'] < sky_height:
            try:
                self.stdscr.addch(obj['y'], obj['x'], char, curses.color_pair(6) | curses.A_DIM)
            except:
                pass
    
    def _render_horizon_decorations(self, level_spec, sky_height, curve_offset=0):
        """Render horizon decorations with parallax effect"""
        horizon_row = sky_height - 1
        
        # Parallax: horizon moves with curves (0.6x speed for more visible effect)
        parallax_offset = int(curve_offset * 0.6)
        
        for decoration in level_spec.sky_config.horizon_decorations:
            positions = decoration.get('positions', [])
            art = decoration.get('art', [])
            
            for pos in positions:
                # Center positions around screen width and apply parallax
                # Map positions from 0-120 range to span full screen width
                screen_pos = int((pos / 120.0) * self.width)
                adjusted_pos = screen_pos + parallax_offset
                
                # Draw decoration from bottom to top
                for i, line in enumerate(reversed(art)):
                    row = horizon_row - i
                    if 0 <= row < sky_height:
                        col = adjusted_pos
                        for j, ch in enumerate(line):
                            c = col + j
                            if 0 <= c < self.width and ch != ' ':
                                try:
                                    color = curses.color_pair(6) | curses.A_DIM
                                    self.stdscr.addch(row, c, ch, color)
                                except:
                                    pass


class SceneryRenderer:
    """Handles roadside scenery rendering"""
    
    def __init__(self, stdscr, width, height):
        self.stdscr = stdscr
        self.width = width
        self.height = height
        self.scenery_objects = []
    
    def clear_objects(self):
        """Clear all scenery objects"""
        self.scenery_objects = []
    
    def spawn(self, level_spec, curve_offset_func):
        """Spawn new scenery based on level spec"""
        max_objects = 50  # Increased for more detail
        roadside_spawn_rate = 0.4  # Roadside objects spawn rate
        distant_spawn_rate = 0.3  # Distant objects spawn rate
        
        if len(self.scenery_objects) < max_objects:
            # Spawn roadside scenery (close to road) - independent check
            if random.random() < roadside_spawn_rate and level_spec.roadside_scenery:
                side = random.choice(['left', 'right'])
                scenery_y = -5
                
                scenery_type = self._weighted_choice(level_spec.roadside_scenery)
                
                # Roadside: 6-10 pixels from road edge
                horizontal_offset = random.randint(6, 10)
                
                self.scenery_objects.append({
                    'side': side,
                    'y': scenery_y,
                    'scenery_type': scenery_type,
                    'h_offset': horizontal_offset,
                    'is_distant': False
                })
            
            # Spawn distant scenery (far from road) - independent check
            if random.random() < distant_spawn_rate and level_spec.distant_scenery:
                side = random.choice(['left', 'right'])
                scenery_y = -5
                
                scenery_type = self._weighted_choice(level_spec.distant_scenery)
                
                # Distant: 15-30 pixels from road edge
                horizontal_offset = random.randint(15, 30)
                
                self.scenery_objects.append({
                    'side': side,
                    'y': scenery_y,
                    'scenery_type': scenery_type,
                    'h_offset': horizontal_offset,
                    'is_distant': True
                })
    
    def _weighted_choice(self, scenery_types):
        """Choose scenery type based on weights"""
        total_weight = sum(s.spawn_weight for s in scenery_types)
        rand_val = random.uniform(0, total_weight)
        
        current = 0
        for scenery in scenery_types:
            current += scenery.spawn_weight
            if rand_val <= current:
                return scenery
        
        return scenery_types[0]
    
    def update(self, speed):
        """Update scenery positions"""
        for obj in self.scenery_objects[:]:
            obj['y'] += speed + 1
            
            if obj['y'] > self.height:
                self.scenery_objects.remove(obj)
    
    def render(self, curve_offset_func):
        """Render all scenery objects"""
        for obj in self.scenery_objects:
            self._render_scenery_object(obj, curve_offset_func)
    
    def _render_scenery_object(self, obj, curve_offset_func):
        """Render a single scenery object"""
        row_base = int(obj['y'])
        scenery_type = obj['scenery_type']
        
        # Start rendering from where road begins (after sky)
        sky_height = min(15, self.height // 3)
        
        if sky_height <= row_base < self.height - 5:
            # Adjust progress calculation to match road rendering
            progress = (row_base - sky_height) / (self.height - 2 - sky_height)
            curve_offset = curve_offset_func(row_base)
            
            # Match road width calculation
            road_width = int(20 + (60 - 20) * progress)
            center = self.width // 2 + curve_offset
            
            # Get horizontal offset for feathering (varies per object)
            h_offset = obj.get('h_offset', 10)  # Default to 10 if not set
            
            # Position objects at varying distances from road edges
            if obj['side'] == 'left':
                scenery_x = center - road_width // 2 - h_offset
            else:
                scenery_x = center + road_width // 2 + h_offset
            
            scale = 0.3 + progress * 0.7
            
            for i, line in enumerate(scenery_type.art):
                row = row_base + int(i * scale)
                if 0 <= row < self.height - 1:
                    scaled_line = line if scale > 0.6 else line[1:-1] if len(line) > 2 else line
                    col = scenery_x
                    
                    for j, ch in enumerate(scaled_line):
                        c = col + j
                        if 0 <= c < self.width and ch != ' ':
                            try:
                                color = curses.color_pair(scenery_type.color_pair)
                                self.stdscr.addch(row, c, ch, color)
                            except:
                                pass


class CarRenderer:
    """Handles car rendering with different models"""
    
    @staticmethod
    def render(stdscr, x, y, car_model, width, height):
        """Render a car using the specified model"""
        for i, line in enumerate(car_model.art):
            row = int(y) + i
            col = int(x) - len(line) // 2
            if 0 <= row < height:
                for j, ch in enumerate(line):
                    c = col + j
                    if 0 <= c < width and ch != ' ':
                        try:
                            color = curses.color_pair(car_model.color_pair) | curses.A_BOLD
                            stdscr.addch(row, c, ch, color)
                        except:
                            pass


class BackgroundRenderer:
    """Renders background patterns and scenery behind the road"""
    
    def __init__(self, stdscr, width, height):
        self.stdscr = stdscr
        self.width = width
        self.height = height
        self.pattern_offset = 0
    
    def render(self, level_spec, road_offset):
        """Render background based on level type"""
        sky_height = min(15, self.height // 3)
        bg_config = level_spec.sky_config.background_pattern
        
        for row in range(sky_height, self.height - 2):
            progress = (row - sky_height) / max((self.height - sky_height - 2), 1)
            
            for col in range(self.width):
                char, color = self._get_background_char(bg_config, row, col, progress, road_offset)
                if char:
                    try:
                        self.stdscr.addch(row, col, char, color)
                    except:
                        pass
    
    def _get_background_char(self, bg_config, row, col, progress, offset):
        """Get character and color for background position"""
        pattern_type = bg_config.get('type', 'solid')
        base_color = curses.color_pair(bg_config.get('color_pair', 0))
        
        if pattern_type == 'gradient':
            # Vertical gradient from dark to light
            if progress < 0.3:
                return ' ', base_color | curses.A_DIM | curses.A_REVERSE
            elif progress < 0.6:
                return '.', base_color | curses.A_DIM
            else:
                return '.', base_color
        
        elif pattern_type == 'dots':
            # Scattered dot pattern
            if (row + col + int(offset)) % 5 == 0:
                return '.', base_color
            return ' ', base_color | curses.A_DIM | curses.A_REVERSE
        
        elif pattern_type == 'waves':
            # Wave pattern
            wave = int((col + offset) / 4) % 3
            if wave == 0 and row % 2 == 0:
                return '~', base_color | curses.A_DIM
            return ' ', base_color | curses.A_DIM | curses.A_REVERSE
        
        elif pattern_type == 'grid':
            # Grid pattern for industrial
            if row % 4 == 0 or col % 8 == 0:
                return '#', base_color | curses.A_DIM
            return ' ', base_color | curses.A_DIM | curses.A_REVERSE
        
        else:
            # Solid color
            return ' ', base_color | curses.A_DIM | curses.A_REVERSE


class RoadRenderer:
    """Handles road rendering with perspective"""
    
    def __init__(self, stdscr, width, height):
        self.stdscr = stdscr
        self.width = width
        self.height = height
        self.road_width_top = 20
        self.road_width_bottom = 60
    
    def render(self, curve_offset_func, road_offset):
        """Render the road with curves and markings"""
        segment_height = 3
        
        # Start road from horizon (where sky ends)
        sky_height = min(15, self.height // 3)
        start_row = sky_height
        
        for row in range(start_row, self.height - 2):
            # Adjust progress to account for starting position
            progress = (row - start_row) / (self.height - 2 - start_row)
            road_width = int(self.road_width_top + 
                           (self.road_width_bottom - self.road_width_top) * progress)
            
            curve_offset = curve_offset_func(row)
            center = self.width // 2 + curve_offset
            left_edge = center - road_width // 2
            right_edge = center + road_width // 2
            
            segment_index = int((row + road_offset) / segment_height) % 2
            
            if segment_index == 0:
                road_color = curses.color_pair(6)
            else:
                road_color = curses.color_pair(6) | curses.A_DIM
            
            for col in range(max(0, left_edge), min(self.width, right_edge)):
                try:
                    self.stdscr.addch(row, col, ' ', road_color | curses.A_REVERSE)
                except:
                    pass
            
            left_line_col = left_edge - 1
            if 0 <= left_line_col < self.width:
                try:
                    if segment_index == 0:
                        self.stdscr.addch(row, left_line_col, '|', curses.color_pair(1))
                except:
                    pass
            
            right_line_col = right_edge
            if 0 <= right_line_col < self.width:
                try:
                    if segment_index == 0:
                        self.stdscr.addch(row, right_line_col, '|', curses.color_pair(1))
                except:
                    pass
            
            if row % segment_height == 0:
                dash_positions = [center - 2, center + 2]
                for dash_col in dash_positions:
                    if left_edge < dash_col < right_edge:
                        try:
                            self.stdscr.addch(row, dash_col, '-', curses.color_pair(2))
                        except:
                            pass

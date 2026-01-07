"""
Game state management for ASCII OutRun
Handles game state, collision detection, and game logic
"""

import curses
from dataclasses import dataclass
from typing import List


@dataclass
class Car:
    x: float
    y: float
    width: int = 5
    height: int = 3


@dataclass
class TrafficCar:
    x: float
    y: float
    speed: float
    width: int = 5
    height: int = 3


class GameState:
    """Manages the overall game state"""
    
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.reset()
    
    def reset(self):
        """Reset game to initial state"""
        self.player = Car(x=self.width // 2, y=self.height - 6)
        self.traffic = []
        self.road_offset = 0
        self.speed = 1.0
        self.score = 0
        self.game_over = False
        self.distance = 0
        self.curve = 0.0
        self.curve_target = 0.0
        self.curve_change_timer = 0
        self.music_enabled = True
        self.level_transition_message = ""
        self.level_transition_timer = 0
        self.transition_stage = 'none'  # 'none', 'horizon_out', 'color_fade', 'horizon_in'
        self.transition_progress = 0
        self.old_level_color = None
        self.new_level_color = None
    
    def get_curve_offset(self, row):
        """Calculate curve offset for a given row"""
        progress = row / (self.height - 2)
        curve_effect = self.curve * progress * 30
        return int(curve_effect)
    
    def update_road_offset(self):
        """Update road scrolling offset"""
        self.road_offset += self.speed
        if self.road_offset >= 6:
            self.road_offset = 0
    
    def update_distance(self):
        """Update distance traveled"""
        self.distance += self.speed * 0.5
    
    def update_curve(self):
        """Update road curve dynamics"""
        import random
        
        self.curve_change_timer -= 1
        
        if self.curve_change_timer <= 0:
            self.curve_target = random.uniform(-1.0, 1.0)
            self.curve_change_timer = random.randint(100, 300)
        
        curve_diff = self.curve_target - self.curve
        self.curve += curve_diff * 0.02
    
    def check_collision(self):
        """Check for collisions with traffic and road edges"""
        px, py = int(self.player.x), int(self.player.y)
        
        # Check collision with traffic
        for car in self.traffic:
            cx, cy = int(car.x), int(car.y)
            
            if abs(px - cx) < 5 and abs(py - cy) < 3:
                return True
        
        # Check collision with road edges
        road_width_bottom = 60
        curve_offset = self.get_curve_offset(int(self.player.y))
        center = self.width // 2 + curve_offset
        left_edge = center - road_width_bottom // 2
        right_edge = center + road_width_bottom // 2
        
        if px - 2 < left_edge or px + 2 > right_edge:
            return True
        
        return False


class TrafficManager:
    """Manages traffic cars"""
    
    def __init__(self, width, height):
        self.width = width
        self.height = height
    
    def spawn_traffic(self, traffic_list, speed, curve_offset_func):
        """Spawn new traffic car"""
        import random
        
        if random.random() < 0.02 + speed * 0.01:
            road_width_top = 20
            curve_offset = curve_offset_func(0)
            center = self.width // 2 + curve_offset
            x_offset = random.randint(-road_width_top // 3, road_width_top // 3)
            x = center + x_offset
            
            traffic_list.append(TrafficCar(
                x=x,
                y=-3,
                speed=speed * random.uniform(0.3, 0.7)
            ))
    
    def update_traffic(self, traffic_list, speed, curve_offset_func):
        """Update all traffic cars"""
        for car in traffic_list[:]:
            car.y += speed + 1 - car.speed
            
            # Update position based on curve
            old_curve_offset = curve_offset_func(int(car.y - (speed + 1 - car.speed)))
            new_curve_offset = curve_offset_func(int(car.y))
            car.x += (new_curve_offset - old_curve_offset)
            
            if car.y > self.height:
                traffic_list.remove(car)
                return 10  # Points for passing a car
        
        return 0


class InputHandler:
    """Handles user input"""
    
    @staticmethod
    def handle_input(stdscr, game_state, sound=None):
        """Process keyboard input - returns False to quit, True to continue"""
        try:
            key = stdscr.getch()
            
            if key == ord('q'):
                return False
            
            if key == curses.KEY_LEFT or key == ord('a'):
                game_state.player.x -= 2
            
            if key == curses.KEY_RIGHT or key == ord('d'):
                game_state.player.x += 2
            
            if key == curses.KEY_UP or key == ord('w'):
                game_state.speed = min(3.0, game_state.speed + 0.1)
            
            if key == curses.KEY_DOWN or key == ord('s'):
                game_state.speed = max(0.5, game_state.speed - 0.1)
            
            if key == ord('m') or key == ord('M'):
                game_state.music_enabled = not game_state.music_enabled
                if not game_state.music_enabled and sound:
                    try:
                        sound.stop()
                    except:
                        pass
        
        except:
            pass
        
        return True

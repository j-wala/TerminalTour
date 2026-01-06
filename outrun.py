import curses
import random
import time
import pygame
import threading
from dataclasses import dataclass
from typing import List, Tuple

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

class OutRunGame:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.height, self.width = stdscr.getmaxyx()
        
        curses.curs_set(0)
        stdscr.nodelay(1)
        stdscr.timeout(0)
        
        curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(5, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
        curses.init_pair(6, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(7, curses.COLOR_BLUE, curses.COLOR_BLACK)
        
        self.player = Car(x=self.width // 2, y=self.height - 6)
        self.traffic: List[TrafficCar] = []
        self.road_offset = 0
        self.speed = 1.0
        self.score = 0
        self.game_over = False
        self.distance = 0
        self.curve = 0.0
        self.curve_target = 0.0
        self.curve_change_timer = 0
        self.tree_positions = []
        self.tree_offset = 0
        self.music_enabled = True
        self.sound = None
        self.current_level = 0
        self.level_names = ["BEACH", "CITY", "FACTORY"]
        self.level_transition_message = ""
        self.level_transition_timer = 0
        self.sky_objects = []
        self.environmental_objects = []
        
        self.init_music()
        
    def init_music(self):
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            self.generate_music()
        except:
            pass
    
    def generate_music(self):
        try:
            import numpy as np
            
            duration = 4.0
            sample_rate = 22050
            
            def generate_square_wave(freq, duration, sample_rate):
                t = np.linspace(0, duration, int(sample_rate * duration))
                wave = np.sign(np.sin(2 * np.pi * freq * t))
                return (wave * 16384).astype(np.int16)
            
            melody_notes = [523, 659, 784, 659, 523, 392, 523, 659]
            bass_notes = [262, 330, 262, 330, 262, 196, 262, 330]
            
            note_duration = duration / len(melody_notes)
            
            melody = np.array([], dtype=np.int16)
            bass = np.array([], dtype=np.int16)
            
            for i in range(len(melody_notes)):
                melody = np.concatenate([melody, generate_square_wave(melody_notes[i], note_duration, sample_rate)])
                bass = np.concatenate([bass, generate_square_wave(bass_notes[i], note_duration, sample_rate)])
            
            combined = np.stack([melody + bass * 0.5, melody + bass * 0.5], axis=1)
            self.sound = pygame.sndarray.make_sound(combined.astype(np.int16))
            
            def play_loop():
                while True:
                    if self.music_enabled:
                        self.sound.play()
                    time.sleep(duration)
            
            music_thread = threading.Thread(target=play_loop, daemon=True)
            music_thread.start()
        except:
            pass
    
    def get_curve_offset(self, row: int) -> int:
        progress = row / (self.height - 2)
        curve_effect = self.curve * progress * 30
        return int(curve_effect)
    
    def draw_sky(self):
        sky_height = min(15, self.height // 3)
        
        if self.current_level == 0:
            for row in range(sky_height):
                for col in range(self.width):
                    try:
                        self.stdscr.addch(row, col, ' ', curses.color_pair(4) | curses.A_DIM)
                    except:
                        pass
            
            if len(self.sky_objects) == 0:
                sun_x = self.width - 15
                sun_y = 3
                self.sky_objects.append({'type': 'sun', 'x': sun_x, 'y': sun_y})
                
                for _ in range(3):
                    cloud_x = random.randint(10, self.width - 20)
                    cloud_y = random.randint(2, sky_height - 3)
                    self.sky_objects.append({'type': 'cloud', 'x': cloud_x, 'y': cloud_y, 'offset': random.randint(0, 50)})
            
            for obj in self.sky_objects:
                if obj['type'] == 'sun':
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
                
                elif obj['type'] == 'cloud':
                    obj['offset'] = (obj['offset'] + 0.1) % self.width
                    cloud_x = int(obj['x'] + obj['offset']) % self.width
                    cloud_art = "  .--.  "
                    for j, ch in enumerate(cloud_art):
                        x = cloud_x + j
                        if 0 <= x < self.width and 0 <= obj['y'] < sky_height:
                            try:
                                self.stdscr.addch(obj['y'], x, ch, curses.color_pair(6))
                            except:
                                pass
        
        elif self.current_level == 1:
            for row in range(sky_height):
                for col in range(self.width):
                    try:
                        self.stdscr.addch(row, col, ' ', curses.color_pair(7) | curses.A_DIM)
                    except:
                        pass
            
            if len(self.sky_objects) == 0:
                for _ in range(5):
                    cloud_x = random.randint(5, self.width - 15)
                    cloud_y = random.randint(2, sky_height - 2)
                    self.sky_objects.append({'type': 'cloud', 'x': cloud_x, 'y': cloud_y, 'offset': random.randint(0, 50)})
            
            for obj in self.sky_objects:
                if obj['type'] == 'cloud':
                    obj['offset'] = (obj['offset'] + 0.15) % self.width
                    cloud_x = int(obj['x'] + obj['offset']) % self.width
                    cloud_art = " .--. "
                    for j, ch in enumerate(cloud_art):
                        x = cloud_x + j
                        if 0 <= x < self.width and 0 <= obj['y'] < sky_height:
                            try:
                                self.stdscr.addch(obj['y'], x, ch, curses.color_pair(6) | curses.A_DIM)
                            except:
                                pass
        
        else:
            for row in range(sky_height):
                for col in range(self.width):
                    try:
                        self.stdscr.addch(row, col, ' ', curses.color_pair(1) | curses.A_DIM)
                    except:
                        pass
            
            if len(self.sky_objects) == 0:
                for _ in range(8):
                    smoke_x = random.randint(10, self.width - 10)
                    smoke_y = random.randint(3, sky_height - 1)
                    self.sky_objects.append({'type': 'smoke', 'x': smoke_x, 'y': smoke_y, 'offset': 0})
            
            for obj in self.sky_objects:
                if obj['type'] == 'smoke':
                    obj['offset'] = (obj['offset'] + 0.3) % 10
                    smoke_chars = ['~', '≈', '∼']
                    char = smoke_chars[int(obj['offset']) % len(smoke_chars)]
                    if 0 <= obj['x'] < self.width and 0 <= obj['y'] < sky_height:
                        try:
                            self.stdscr.addch(obj['y'], obj['x'], char, curses.color_pair(6) | curses.A_DIM)
                        except:
                            pass
    
    def draw_road(self):
        road_width_top = 20
        road_width_bottom = 60
        
        for row in range(self.height - 2):
            progress = row / (self.height - 2)
            road_width = int(road_width_top + (road_width_bottom - road_width_top) * progress)
            
            curve_offset = self.get_curve_offset(row)
            center = self.width // 2 + curve_offset
            left_edge = center - road_width // 2
            right_edge = center + road_width // 2
            
            segment_height = 3
            segment_index = int((row + self.road_offset) / segment_height) % 2
            
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
    
    def get_current_level(self):
        if self.distance < 500:
            return 0
        elif self.distance < 1000:
            return 1
        else:
            return 2
    
    def check_level_transition(self):
        new_level = self.get_current_level()
        if new_level != self.current_level:
            self.current_level = new_level
            self.level_transition_message = f"ENTERING {self.level_names[new_level]} ZONE!"
            self.level_transition_timer = 100
            self.sky_objects = []
            self.tree_positions = []
    
    def spawn_scenery(self):
        if len(self.tree_positions) < 25:
            if random.random() < 0.35:
                side = random.choice(['left', 'right'])
                scenery_y = -5
                
                if self.current_level == 0:
                    scenery_type = random.choice(['palm', 'umbrella', 'rock'])
                elif self.current_level == 1:
                    scenery_type = random.choice(['building', 'lamp', 'sign'])
                else:
                    scenery_type = random.choice(['smokestack', 'tank', 'pipe'])
                
                self.tree_positions.append({
                    'side': side, 
                    'y': scenery_y, 
                    'type': self.current_level,
                    'subtype': scenery_type
                })
    
    def update_scenery(self):
        for item in self.tree_positions[:]:
            item['y'] += self.speed + 1
            
            if item['y'] > self.height:
                self.tree_positions.remove(item)
    
    def draw_scenery(self):
        scenery_defs = {
            'palm': (["  Y  ", " /|\ ", "//|\\\\"], curses.color_pair(3)),
            'umbrella': ([" _|_ ", "(___)", "  |  "], curses.color_pair(2)),
            'rock': ([" ___ ", "/   \\", "\\___/"], curses.color_pair(6) | curses.A_DIM),
            'building': (["[##]", "[##]", "[##]"], curses.color_pair(6)),
            'lamp': ([" O ", " | ", " | "], curses.color_pair(2) | curses.A_BOLD),
            'sign': (["###", "[>]", " | "], curses.color_pair(3)),
            'smokestack': ([" ≈≈ ", "[##]", "[##]"], curses.color_pair(1) | curses.A_DIM),
            'tank': ([" __ ", "[__]", "[__]"], curses.color_pair(6) | curses.A_DIM),
            'pipe': (["]===", "]===", "]==="], curses.color_pair(1))
        }
        
        for item in self.tree_positions:
            row_base = int(item['y'])
            subtype = item.get('subtype', 'palm')
            
            if subtype in scenery_defs:
                art, color = scenery_defs[subtype]
            else:
                art = ["  ?  ", "  ?  ", "  ?  "]
                color = curses.color_pair(6)
            
            if 0 <= row_base < self.height - 5:
                progress = row_base / (self.height - 2)
                curve_offset = self.get_curve_offset(row_base)
                
                road_width = int(20 + (60 - 20) * progress)
                center = self.width // 2 + curve_offset
                
                if item['side'] == 'left':
                    scenery_x = center - road_width // 2 - 8
                else:
                    scenery_x = center + road_width // 2 + 3
                
                scale = 0.3 + progress * 0.7
                
                for i, line in enumerate(art):
                    row = row_base + int(i * scale)
                    if 0 <= row < self.height - 1:
                        scaled_line = line if scale > 0.6 else line[1:-1]
                        col = scenery_x
                        
                        for j, ch in enumerate(scaled_line):
                            c = col + j
                            if 0 <= c < self.width and ch != ' ':
                                try:
                                    self.stdscr.addch(row, c, ch, color)
                                except:
                                    pass
    
    def draw_car(self, x: int, y: int, color_pair: int):
        car_art = [
            " _=_ ",
            "[###]",
            " | | "
        ]
        
        for i, line in enumerate(car_art):
            row = int(y) + i
            col = int(x) - len(line) // 2
            if 0 <= row < self.height:
                for j, ch in enumerate(line):
                    c = col + j
                    if 0 <= c < self.width and ch != ' ':
                        try:
                            self.stdscr.addch(row, c, ch, curses.color_pair(color_pair) | curses.A_BOLD)
                        except:
                            pass
    
    def draw_player(self):
        self.draw_car(int(self.player.x), int(self.player.y), 4)
        
    def draw_traffic(self):
        for car in self.traffic:
            self.draw_car(int(car.x), int(car.y), 1)
    
    def draw_hud(self):
        try:
            speed_text = f"SPEED: {int(self.speed * 100)} km/h"
            self.stdscr.addstr(self.height - 1, 2, speed_text, curses.color_pair(2) | curses.A_BOLD)
            
            score_text = f"SCORE: {self.score}"
            self.stdscr.addstr(self.height - 1, self.width - len(score_text) - 2, score_text, curses.color_pair(3) | curses.A_BOLD)
            
            dist_text = f"DISTANCE: {int(self.distance)}m"
            self.stdscr.addstr(self.height - 1, self.width // 2 - len(dist_text) // 2, dist_text, curses.color_pair(5) | curses.A_BOLD)
            
            sound_text = f"[M]USIC: {'ON' if self.music_enabled else 'OFF'}"
            sound_color = curses.color_pair(3) if self.music_enabled else curses.color_pair(1)
            self.stdscr.addstr(0, 2, sound_text, sound_color)
            
            level_text = f"LEVEL: {self.level_names[self.current_level]}"
            level_colors = [curses.color_pair(2), curses.color_pair(4), curses.color_pair(1)]
            self.stdscr.addstr(0, self.width - len(level_text) - 2, level_text, level_colors[self.current_level] | curses.A_BOLD)
            
            if self.level_transition_timer > 0:
                transition_y = self.height // 2
                transition_x = self.width // 2 - len(self.level_transition_message) // 2
                if transition_x >= 0:
                    self.stdscr.addstr(transition_y, transition_x, self.level_transition_message, 
                                     curses.color_pair(5) | curses.A_BOLD | curses.A_REVERSE)
                self.level_transition_timer -= 1
        except:
            pass
    
    def spawn_traffic(self):
        if random.random() < 0.02 + self.speed * 0.01:
            road_width_top = 20
            curve_offset = self.get_curve_offset(0)
            center = self.width // 2 + curve_offset
            x_offset = random.randint(-road_width_top // 3, road_width_top // 3)
            x = center + x_offset
            
            self.traffic.append(TrafficCar(
                x=x,
                y=-3,
                speed=self.speed * random.uniform(0.3, 0.7)
            ))
    
    def update_traffic(self):
        for car in self.traffic[:]:
            car.y += self.speed + 1 - car.speed
            
            old_curve_offset = self.get_curve_offset(int(car.y - (self.speed + 1 - car.speed)))
            new_curve_offset = self.get_curve_offset(int(car.y))
            car.x += (new_curve_offset - old_curve_offset)
            
            if car.y > self.height:
                self.traffic.remove(car)
                self.score += 10
    
    def check_collision(self) -> bool:
        px, py = int(self.player.x), int(self.player.y)
        
        for car in self.traffic:
            cx, cy = int(car.x), int(car.y)
            
            if abs(px - cx) < 5 and abs(py - cy) < 3:
                return True
                
        road_width_bottom = 60
        curve_offset = self.get_curve_offset(int(self.player.y))
        center = self.width // 2 + curve_offset
        left_edge = center - road_width_bottom // 2
        right_edge = center + road_width_bottom // 2
        
        if px - 2 < left_edge or px + 2 > right_edge:
            return True
            
        return False
    
    def handle_input(self):
        try:
            key = self.stdscr.getch()
            
            if key == ord('q'):
                return False
                
            if key == curses.KEY_LEFT or key == ord('a'):
                self.player.x -= 2
                
            if key == curses.KEY_RIGHT or key == ord('d'):
                self.player.x += 2
                
            if key == curses.KEY_UP or key == ord('w'):
                self.speed = min(3.0, self.speed + 0.1)
                
            if key == curses.KEY_DOWN or key == ord('s'):
                self.speed = max(0.5, self.speed - 0.1)
            
            if key == ord('m') or key == ord('M'):
                self.music_enabled = not self.music_enabled
                if not self.music_enabled and self.sound:
                    try:
                        self.sound.stop()
                    except:
                        pass
                
        except:
            pass
            
        return True
    
    def draw_title_screen(self):
        self.stdscr.clear()
        
        title = [
            "   ___  __  __________ __  ___   __",
            "  / _ \\/ / / /_  __/ _ \\ / / / | / /",
            " / // / /_/ / / / / , _/ /_/ /  |/ /",
            "/____/\\____/ /_/ /_/|_|\\____/_/|___/"
        ]
        
        start_y = self.height // 2 - len(title) - 5
        for i, line in enumerate(title):
            x = self.width // 2 - len(line) // 2
            if x >= 0 and start_y + i >= 0:
                try:
                    self.stdscr.addstr(start_y + i, x, line, curses.color_pair(5) | curses.A_BOLD)
                except:
                    pass
        
        subtitle = "ASCII RACING GAME"
        try:
            self.stdscr.addstr(start_y + len(title) + 2, self.width // 2 - len(subtitle) // 2, 
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
    
    def draw_game_over(self):
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
                    self.stdscr.addstr(start_y + i, x, line, curses.color_pair(1) | curses.A_BOLD)
                except:
                    pass
        
        final_score = f"FINAL SCORE: {self.score}"
        final_dist = f"DISTANCE: {int(self.distance)}m"
        
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
    
    def update_curve(self):
        self.curve_change_timer -= 1
        
        if self.curve_change_timer <= 0:
            self.curve_target = random.uniform(-1.0, 1.0)
            self.curve_change_timer = random.randint(100, 300)
        
        curve_diff = self.curve_target - self.curve
        self.curve += curve_diff * 0.02
    
    def reset_game(self):
        self.player = Car(x=self.width // 2, y=self.height - 6)
        self.traffic = []
        self.road_offset = 0
        self.speed = 1.0
        self.score = 0
        self.game_over = False
        self.distance = 0
        self.curve = 0.0
        self.curve_target = 0.0
        self.curve_change_timer = 100
        self.tree_positions = []
        self.tree_offset = 0
        self.music_enabled = True
        self.current_level = 0
        self.level_transition_message = ""
        self.level_transition_timer = 0
        self.sky_objects = []
        self.environmental_objects = []
    
    def run(self):
        self.draw_title_screen()
        
        frame_time = 0.05
        
        while True:
            if not self.game_over:
                frame_start = time.time()
                
                self.stdscr.clear()
                
                self.road_offset += self.speed
                if self.road_offset >= 6:
                    self.road_offset = 0
                
                self.distance += self.speed * 0.5
                self.update_curve()
                self.check_level_transition()
                
                self.draw_sky()
                self.draw_road()
                self.spawn_scenery()
                self.update_scenery()
                self.draw_scenery()
                self.spawn_traffic()
                self.update_traffic()
                self.draw_traffic()
                self.draw_player()
                self.draw_hud()
                
                if self.check_collision():
                    self.game_over = True
                
                if not self.handle_input():
                    break
                
                self.stdscr.refresh()
                
                frame_elapsed = time.time() - frame_start
                sleep_time = frame_time - frame_elapsed
                if sleep_time > 0:
                    time.sleep(sleep_time)
                
            else:
                self.draw_game_over()
                
                try:
                    key = self.stdscr.getch()
                    if key == ord('r') or key == ord('R'):
                        self.reset_game()
                    elif key == ord('q') or key == ord('Q'):
                        break
                except:
                    pass

def main(stdscr):
    game = OutRunGame(stdscr)
    game.run()

if __name__ == "__main__":
    curses.wrapper(main)

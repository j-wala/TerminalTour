# ASCII OutRun - Architecture Documentation

## Overview

The game has been refactored into a modular, data-driven architecture that makes it easy to add new content, levels, and features without modifying core game logic.

## Project Structure

```
ASCII OutRun/
├── outrun.py                 # Original monolithic version (legacy)
├── outrun_refactored.py      # New modular game entry point
├── level_specs.py            # Level configuration and asset definitions
├── rendering.py              # Rendering components (sky, background, road, etc.)
├── game_state.py             # Game state and logic management
├── ui.py                     # UI components (HUD, menus)
├── music_generator.py        # Procedural music generation system
├── requirements.txt          # Dependencies
├── README.md                 # User-facing documentation
└── ARCHITECTURE.md           # This file
```

## Module Breakdown

### `level_specs.py` - Content Definition System

**Purpose**: Central location for all level configurations, assets, and content.

**Key Classes**:
- `LevelSpec`: Defines a complete level with all its properties
- `SkyConfig`: Sky rendering configuration (colors, objects, type)
- `SceneryType`: Individual scenery object definition with art and weights
- `CarModel`: Car appearance definition

**Adding a New Level**:
```python
NEW_LEVEL = LevelSpec(
    name="DESERT",
    distance_threshold=1500,
    sky_config=SkyConfig(
        color_pair=2,
        sky_type='sunny',
        objects=[
            {'type': 'sun', 'position': 'center'},
        ],
        background_pattern={'type': 'gradient', 'color_pair': 2},
        horizon_decorations=[
            {'type': 'mesa', 'positions': [25, 70], 'art': ['___', '| |', '| |']},
        ]
    ),
    scenery_types=[
        SceneryType('cactus', ["  Y  ", " /|\\ ", "  |  "], 3, spawn_weight=2.0),
        SceneryType('tumbleweed', [" oo ", "(oo)", " oo "], 6, spawn_weight=1.0),
    ],
    music_config=MusicConfig(
        scale_name='G Major',
        root_note='G4',
        scale_type='major',           # 'major', 'minor', 'diminished'
        progression_style='retro',    # 'pop', 'jazz', 'blues', 'retro'
        melody_style='balanced',      # 'upbeat', 'melancholy', 'balanced'
        drum_pattern='fast',          # 'standard', 'fast', 'syncopated', 'minimal'
        groove='triplet',             # 'straight', 'swing', 'shuffle', 'triplet'
        bpm=135
    )
)

# Add to LEVELS list
LEVELS = [BEACH_LEVEL, CITY_LEVEL, FACTORY_LEVEL, DESERT_LEVEL, NEW_LEVEL]
```

### `rendering.py` - Rendering Component System

**Purpose**: Modular rendering classes that handle visual output.

**Key Classes**:
- `SkyRenderer`: Manages sky background with gradients and atmospheric objects
- `BackgroundRenderer`: Renders level-specific background patterns (waves, dots, grid, gradient)
- `SceneryRenderer`: Handles roadside scenery with perspective
- `CarRenderer`: Renders car models
- `RoadRenderer`: Draws road with curves and markings

**Adding a New Renderer**:
```python
class ParticleRenderer:
    def __init__(self, stdscr, width, height):
        self.stdscr = stdscr
        self.particles = []
    
    def spawn(self, x, y, char):
        self.particles.append({'x': x, 'y': y, 'char': char})
    
    def update(self):
        for p in self.particles:
            p['y'] += 1
    
    def render(self):
        for p in self.particles:
            # Render particle
            pass
```

### `game_state.py` - State Management

**Purpose**: Manages game state, collision detection, and core game logic.

**Key Classes**:
- `GameState`: Central game state container
- `TrafficManager`: Spawns and updates traffic
- `InputHandler`: Processes player input
- `Car` / `TrafficCar`: Data classes for vehicles

**Extending Game State**:
```python
# Add new state variables in GameState.reset()
def reset(self):
    # ... existing code ...
    self.power_ups = []
    self.boost_timer = 0
```

### `music_generator.py` - Procedural Music System

**Purpose**: Generates rich chiptune music with multiple instruments.

**Key Features**:
- Multiple waveforms (square, triangle, sawtooth)
- ADSR envelope system for realistic instrument sounds
- Drum synthesis (kick, snare, hi-hat)
- Automatic harmony generation
- Multi-track mixing (melody, bass, harmony, drums)

### `ui.py` - User Interface Components

**Purpose**: Handles all UI rendering (HUD, menus, screens).

**Key Classes**:
- `HUDRenderer`: In-game heads-up display
- `TitleScreen`: Main menu
- `GameOverScreen`: End game screen

**Adding a New Screen**:
```python
class PauseScreen:
    def __init__(self, stdscr, width, height):
        self.stdscr = stdscr
        self.width = width
        self.height = height
    
    def show(self):
        # Display pause menu
        pass
    
    def handle_input(self, stdscr):
        # Process pause menu input
        return 'resume' or 'quit'
```

### `outrun_refactored.py` - Main Game Loop

**Purpose**: Orchestrates all components and manages the game loop.

**Main Flow**:
1. Initialize all components
2. Show title screen
3. Game loop:
   - Update game state
   - Render all components
   - Handle input
   - Maintain frame timing
4. Handle game over

## Data Flow

```
Player Input → InputHandler → GameState
                                   ↓
                          TrafficManager ← Level Specs
                                   ↓
                            Check Collision
                                   ↓
                            Update Renderers
                                   ↓
         Sky → Road → Scenery → Cars → HUD
                                   ↓
                              Screen Output
```

## Adding New Features

### Adding a New Scenery Object

1. Define in `level_specs.py`:
```python
SceneryType('windmill', [" /\\ ", "[##]", " || "], 6, spawn_weight=1.0)
```

2. Add to a level's `scenery_types` list

### Adding a New Sky Element

1. Define in level's `SkyConfig`:
```python
{'type': 'bird', 'count': 3, 'speed': 0.2}
```

2. Add rendering logic in `SkyRenderer._initialize_sky_objects()` and `_render_sky_objects()`

### Adding a New Car Model

1. Define in `level_specs.py`:
```python
SPORTS_CAR = CarModel(
    name="sports",
    art=[
        " ___ ",
        "<###>",
        " | | "
    ],
    color_pair=5
)
```

2. Use it in traffic spawning or player rendering

### Adding a New Level

See the `level_specs.py` section above for complete example.

## Benefits of This Architecture

1. **Separation of Concerns**: Each module has a single responsibility
2. **Easy Content Addition**: New levels and assets don't require code changes
3. **Testable**: Components can be tested independently
4. **Maintainable**: Changes to one component don't affect others
5. **Extensible**: Easy to add new features (power-ups, weather, etc.)
6. **Reusable**: Rendering components can be reused in different contexts

## Migration Guide

The original `outrun.py` remains for reference. To switch to the new architecture:

```bash
# Old way
python outrun.py

# New way (recommended)
python outrun_refactored.py
```

Both versions are functionally equivalent, but the refactored version is easier to extend and modify.

## Future Enhancements

With this architecture, these features would be easy to add:

- **Power-ups**: Add to `game_state.py` and create `PowerUpRenderer`
- **Weather effects**: Add to `SkyConfig` and `SkyRenderer`
- **Multiple car types**: Define in `level_specs.py`
- **Animated scenery**: Add animation state to `SceneryType`
- **Boss levels**: Create special `LevelSpec` with unique logic
- **Multiplayer**: Add second `Car` to `GameState`
- **Day/night cycle**: Extend `SkyRenderer` with time-based colors
- **Achievements**: Add `AchievementSystem` class
- **Save/Load**: Serialize `GameState`
- **Leaderboards**: Add `ScoreManager` class

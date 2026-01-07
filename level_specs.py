"""
Level specification module for ASCII OutRun
Defines all level configurations, assets, and rendering data
"""

import curses

class LevelSpec:
    """Base class for level specifications"""
    def __init__(self, name, distance_threshold, sky_config, scenery_types, music_notes=None):
        self.name = name
        self.distance_threshold = distance_threshold
        self.sky_config = sky_config
        self.scenery_types = scenery_types
        self.music_notes = music_notes or []

class SkyConfig:
    """Configuration for sky rendering"""
    def __init__(self, color_pair, sky_type, objects, background_pattern=None, horizon_decorations=None):
        self.color_pair = color_pair
        self.sky_type = sky_type  # 'sunny', 'overcast', 'polluted'
        self.objects = objects  # List of sky object definitions
        self.background_pattern = background_pattern or {'type': 'solid', 'color_pair': 0}
        self.horizon_decorations = horizon_decorations or []  # Buildings, mountains, etc.

class SceneryType:
    """Definition for a type of roadside scenery"""
    def __init__(self, name, art, color_pair, spawn_weight=1.0):
        self.name = name
        self.art = art  # List of strings for ASCII art
        self.color_pair = color_pair
        self.spawn_weight = spawn_weight

class CarModel:
    """Definition for car appearance"""
    def __init__(self, name, art, color_pair):
        self.name = name
        self.art = art
        self.color_pair = color_pair


PLAYER_CAR = CarModel(
    name="player",
    art=[
        " _=_ ",
        "[###]",
        " | | "
    ],
    color_pair=4
)

TRAFFIC_CAR = CarModel(
    name="traffic",
    art=[
        " _=_ ",
        "[###]",
        " | | "
    ],
    color_pair=1
)


BEACH_LEVEL = LevelSpec(
    name="BEACH",
    distance_threshold=0,
    sky_config=SkyConfig(
        color_pair=4,  # Cyan
        sky_type='sunny',
        objects=[
            {'type': 'sun', 'position': 'top-right'},
            {'type': 'cloud', 'count': 3, 'speed': 0.1}
        ],
        background_pattern={'type': 'waves', 'color_pair': 4},
        horizon_decorations=[
            {'type': 'island', 'positions': [20, 60, 100], 'art': ['^', '/\\', '~~']},
        ]
    ),
    scenery_types=[
        SceneryType('palm', ["  Y  ", " /|\\ ", "//|\\\\"], 3, spawn_weight=1.5),
        SceneryType('umbrella', [" _|_ ", "(___)", "  |  "], 2, spawn_weight=1.0),
        SceneryType('rock', [" ___ ", "/   \\", "\\___/"], 6, spawn_weight=0.8),
    ],
    music_notes={
        'melody': [523, 659, 784, 659, 523, 392, 523, 659],
        'bass': [262, 330, 262, 330, 262, 196, 262, 330]
    }
)

CITY_LEVEL = LevelSpec(
    name="CITY",
    distance_threshold=500,
    sky_config=SkyConfig(
        color_pair=7,  # Blue/dark
        sky_type='overcast',
        objects=[
            {'type': 'cloud', 'count': 5, 'speed': 0.15}
        ],
        background_pattern={'type': 'dots', 'color_pair': 6},
        horizon_decorations=[
            {'type': 'skyscraper', 'positions': [15, 35, 55, 75, 95], 'art': ['|||', '|||', '[#]']},
        ]
    ),
    scenery_types=[
        SceneryType('building', ["[##]", "[##]", "[##]"], 6, spawn_weight=1.5),
        SceneryType('lamp', [" O ", " | ", " | "], 2, spawn_weight=1.0),
        SceneryType('sign', ["###", "[>]", " | "], 3, spawn_weight=0.8),
    ],
    music_notes={
        'melody': [659, 784, 880, 784, 659, 523, 659, 784],
        'bass': [330, 392, 330, 392, 330, 262, 330, 392]
    }
)

FACTORY_LEVEL = LevelSpec(
    name="FACTORY",
    distance_threshold=1000,
    sky_config=SkyConfig(
        color_pair=1,  # Red/polluted
        sky_type='polluted',
        objects=[
            {'type': 'smoke', 'count': 8, 'speed': 0.3}
        ],
        background_pattern={'type': 'grid', 'color_pair': 1},
        horizon_decorations=[
            {'type': 'smokestack', 'positions': [10, 30, 50, 70, 90, 110], 'art': ['≈', '≈', '[#]', '[#]']},
        ]
    ),
    scenery_types=[
        SceneryType('smokestack', [" ≈≈ ", "[##]", "[##]"], 1, spawn_weight=1.5),
        SceneryType('tank', [" __ ", "[__]", "[__]"], 6, spawn_weight=1.0),
        SceneryType('pipe', ["]===", "]===", "]==="], 1, spawn_weight=1.2),
    ],
    music_notes={
        'melody': [392, 523, 659, 523, 392, 330, 392, 523],
        'bass': [196, 262, 196, 262, 196, 165, 196, 262]
    }
)


DESERT_LEVEL = LevelSpec(
    name="DESERT",
    distance_threshold=1500,
    sky_config=SkyConfig(
        color_pair=2,  # Yellow/orange
        sky_type='sunny',
        objects=[
            {'type': 'sun', 'position': 'center'},
        ],
        background_pattern={'type': 'gradient', 'color_pair': 2},
        horizon_decorations=[
            {'type': 'mesa', 'positions': [25, 70], 'art': ['___', '| |', '| |']},
            {'type': 'cactus', 'positions': [40, 85], 'art': [' Y ']},
        ]
    ),
    scenery_types=[
        SceneryType('cactus', ["  Y  ", " /|\ ", "  |  "], 3, spawn_weight=2.0),
        SceneryType('tumbleweed', [" oo ", "(oo)", " oo "], 6, spawn_weight=1.0),
        SceneryType('rock', [" ___ ", "/   \\", "\\___/"], 6, spawn_weight=1.2),
    ],
    music_notes={
        'melody': [440, 550, 660, 550, 440, 330, 440, 550],
        'bass': [220, 275, 220, 275, 220, 165, 220, 275]
    }
)

LEVELS = [BEACH_LEVEL, CITY_LEVEL, FACTORY_LEVEL, DESERT_LEVEL]


def get_level_for_distance(distance):
    """Returns the appropriate level spec based on distance traveled"""
    for level in reversed(LEVELS):
        if distance >= level.distance_threshold:
            return level
    return LEVELS[0]

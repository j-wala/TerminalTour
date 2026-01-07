"""
Level specification module for Terminal Tour
Defines all level configurations, assets, and rendering data
"""

import curses

class MusicConfig:
    """Configuration for level music"""
    def __init__(self, scale_name, root_note, scale_type, progression_style, melody_style, drum_pattern, groove='straight', bpm=120):
        self.scale_name = scale_name
        self.root_note = root_note
        self.scale_type = scale_type  # 'major', 'minor', 'diminished'
        self.progression_style = progression_style  # 'pop', 'jazz', 'blues', etc.
        self.melody_style = melody_style  # 'upbeat', 'melancholy', 'balanced'
        self.drum_pattern = drum_pattern  # 'standard', 'fast', 'syncopated', 'minimal'
        self.groove = groove  # 'straight', 'swing', 'shuffle', 'triplet'
        self.bpm = bpm

class LevelSpec:
    """Base class for level specifications"""
    def __init__(self, name, distance_threshold, sky_config, scenery_types=None, music_config=None, roadside_scenery=None, distant_scenery=None):
        self.name = name
        self.distance_threshold = distance_threshold
        self.sky_config = sky_config
        # Support both old and new scenery system
        self.scenery_types = scenery_types or []
        self.roadside_scenery = roadside_scenery or scenery_types or []
        self.distant_scenery = distant_scenery or []
        self.music_config = music_config

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
        " ____ ",
        "|####|",
        "=O==O="
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
    roadside_scenery=[
        SceneryType('palm', ["  Y  ", " /|\\ ", "//|\\\\"], 3, spawn_weight=1.5),
        SceneryType('umbrella', [" _|_ ", "(___)", "  |  "], 2, spawn_weight=1.0),
        SceneryType('rock', [" ___ ", "/   \\", "\\___/"], 6, spawn_weight=0.8),
    ],
    distant_scenery=[
        SceneryType('seagull', [" >v< "], 4, spawn_weight=0.6),
        SceneryType('driftwood', ["~___~"], 6, spawn_weight=0.5),
        SceneryType('shell', [" @ "], 2, spawn_weight=0.4),
    ],
    music_config=MusicConfig(
        scale_name='C Major',
        root_note='C4',
        scale_type='major',
        progression_style='pop',
        melody_style='upbeat',
        drum_pattern='standard',
        groove='straight',
        bpm=120
    )
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
    roadside_scenery=[
        SceneryType('building', ["[##]", "[##]", "[##]"], 6, spawn_weight=1.5),
        SceneryType('lamp', [" O ", " | ", " | "], 2, spawn_weight=1.0),
        SceneryType('sign', ["###", "[>]", " | "], 3, spawn_weight=0.8),
    ],
    distant_scenery=[
        SceneryType('bench', ["[___]", " | | "], 6, spawn_weight=0.7),
        SceneryType('trash', [" [#] ", "\\___/"], 1, spawn_weight=0.5),
        SceneryType('hydrant', [" H ", "[#]"], 1, spawn_weight=0.4),
    ],
    music_config=MusicConfig(
        scale_name='A Minor',
        root_note='A4',
        scale_type='minor',
        progression_style='jazz',
        melody_style='balanced',
        drum_pattern='syncopated',
        groove='swing',
        bpm=128
    )
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
    roadside_scenery=[
        SceneryType('smokestack', [" ≈≈ ", "[##]", "[##]"], 1, spawn_weight=1.5),
        SceneryType('tank', [" __ ", "[__]", "[__]"], 6, spawn_weight=1.0),
        SceneryType('pipe', ["]===", "]===", "]==="], 1, spawn_weight=1.2),
    ],
    distant_scenery=[
        SceneryType('barrel', [" __ ", "(##)", "|__|"], 2, spawn_weight=0.8),
        SceneryType('crate', ["[##]", "[##]"], 6, spawn_weight=0.6),
        SceneryType('warning', [" /!\\ ", "[!!]"], 2, spawn_weight=0.5),
    ],
    music_config=MusicConfig(
        scale_name='E Minor',
        root_note='E4',
        scale_type='minor',
        progression_style='blues',
        melody_style='melancholy',
        drum_pattern='minimal',
        groove='shuffle',
        bpm=110
    )
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
    roadside_scenery=[
        SceneryType('cactus', ["  Y  ", " /|\\ ", "  |  "], 3, spawn_weight=2.0),
        SceneryType('tumbleweed', [" oo ", "(oo)", " oo "], 6, spawn_weight=1.0),
        SceneryType('rock', [" ___ ", "/   \\", "\\___/"], 6, spawn_weight=1.2),
    ],
    distant_scenery=[
        SceneryType('skull', [" ___ ", "(o_o)", " --- "], 6, spawn_weight=0.6),
        SceneryType('dead_tree', ["  ^  ", " /X\\ "], 6, spawn_weight=0.7),
        SceneryType('snake', ["~S~~"], 3, spawn_weight=0.4),
    ],
    music_config=MusicConfig(
        scale_name='G Major',
        root_note='G4',
        scale_type='major',
        progression_style='retro',
        melody_style='balanced',
        drum_pattern='fast',
        groove='triplet',
        bpm=135
    )
)

HAUNTED_LEVEL = LevelSpec(
    name="HAUNTED",
    distance_threshold=2000,
    sky_config=SkyConfig(
        color_pair=5,  # Purple/dark magenta
        sky_type='overcast',
        objects=[
            {'type': 'moon', 'position': 'top-left'},
            {'type': 'bats', 'count': 6, 'speed': 0.4}
        ],
        background_pattern={'type': 'fog', 'color_pair': 5},
        horizon_decorations=[
            {'type': 'mansion', 'positions': [30, 80], 'art': ['^^^', '[#]', '[#]', '###']},
            {'type': 'tombstone', 'positions': [15, 45, 65, 95], 'art': ['RIP']},
        ]
    ),
    roadside_scenery=[
        SceneryType('tombstone', [" RIP ", "|###|", "\\___/"], 6, spawn_weight=2.0),
        SceneryType('dead_tree', ["  ^  ", " /|\\ ", "/   \\"], 5, spawn_weight=1.5),
        SceneryType('ghost', [" ooo ", "(o_o)", "  ~  "], 7, spawn_weight=0.8),
    ],
    distant_scenery=[
        SceneryType('fog', ["~~~~~", "~~~~~"], 7, spawn_weight=0.6),
        SceneryType('chains', [" |^| ", " |_| "], 6, spawn_weight=0.5),
        SceneryType('candle', [" * ", " | ", "(_)"], 2, spawn_weight=0.4),
    ],
    music_config=MusicConfig(
        scale_name='D Minor',
        root_note='D4',
        scale_type='minor',
        progression_style='blues',
        melody_style='melancholy',
        drum_pattern='minimal',
        groove='shuffle',
        bpm=95
    )
)

NEON_LEVEL = LevelSpec(
    name="NEON CITY",
    distance_threshold=2500,
    sky_config=SkyConfig(
        color_pair=5,  # Magenta/pink
        sky_type='overcast',
        objects=[
            {'type': 'neon_grid', 'count': 10, 'speed': 0.2}
        ],
        background_pattern={'type': 'grid', 'color_pair': 5},
        horizon_decorations=[
            {'type': 'neon_tower', 'positions': [20, 40, 60, 80, 100], 'art': ['|||', '[#]', '[#]']},
        ]
    ),
    roadside_scenery=[
        SceneryType('neon_sign', ["<##>", "[##]", "<##>"], 5, spawn_weight=1.8),
        SceneryType('hologram', [" /\\ ", "/  \\", "\\  /"], 4, spawn_weight=1.2),
        SceneryType('laser_pole', [" ||| ", " ||| ", " ||| "], 6, spawn_weight=1.5),
    ],
    distant_scenery=[
        SceneryType('terminal', [" ___ ", "[###]", "[___]"], 4, spawn_weight=0.7),
        SceneryType('antenna', [" ))) ", "  |  ", " [#] "], 5, spawn_weight=0.6),
        SceneryType('energy_core', [" <O> ", " ||| "], 5, spawn_weight=0.5),
    ],
    music_config=MusicConfig(
        scale_name='E Minor',
        root_note='E4',
        scale_type='minor',
        progression_style='pop',
        melody_style='upbeat',
        drum_pattern='syncopated',
        groove='straight',
        bpm=140
    )
)

SNOW_LEVEL = LevelSpec(
    name="ARCTIC",
    distance_threshold=3000,
    sky_config=SkyConfig(
        color_pair=7,  # White/light blue
        sky_type='overcast',
        objects=[
            {'type': 'snowflakes', 'count': 12, 'speed': 0.2}
        ],
        background_pattern={'type': 'dots', 'color_pair': 7},
        horizon_decorations=[
            {'type': 'mountain', 'positions': [20, 50, 80, 110], 'art': ['/\\', '/  \\', '----']},
            {'type': 'igloo', 'positions': [35, 95], 'art': [' n ', '(_)']},
        ]
    ),
    roadside_scenery=[
        SceneryType('pine_tree', ["  ^  ", " /|\\ ", "/___\\"], 3, spawn_weight=2.0),
        SceneryType('snowman', [" _o_ ", "(oOo)", " ||| "], 7, spawn_weight=1.2),
        SceneryType('ice_block', [" ### ", "[###]", "[###]"], 4, spawn_weight=1.0),
    ],
    distant_scenery=[
        SceneryType('snowdrift', [" ~~~ ", "~~~~~"], 7, spawn_weight=0.8),
        SceneryType('icicle', [" ||| "], 4, spawn_weight=0.6),
        SceneryType('penguin', [" <o> ", " /|\\ "], 7, spawn_weight=0.4),
    ],
    music_config=MusicConfig(
        scale_name='F Major',
        root_note='F4',
        scale_type='major',
        progression_style='pop',
        melody_style='upbeat',
        drum_pattern='standard',
        groove='straight',
        bpm=125
    )
)

JUNGLE_LEVEL = LevelSpec(
    name="JUNGLE",
    distance_threshold=3500,
    sky_config=SkyConfig(
        color_pair=3,  # Green
        sky_type='overcast',
        objects=[
            {'type': 'birds', 'count': 8, 'speed': 0.25},
            {'type': 'vines', 'count': 5, 'speed': 0.05}
        ],
        background_pattern={'type': 'leaves', 'color_pair': 3},
        horizon_decorations=[
            {'type': 'temple', 'positions': [30, 90], 'art': [' A ', '[#]', '[#]', '###']},
            {'type': 'waterfall', 'positions': [60], 'art': ['|||', '|||', '~~~']},
        ]
    ),
    roadside_scenery=[
        SceneryType('jungle_tree', ["  Y  ", " {|} ", "{|||}", " ||| "], 3, spawn_weight=2.0),
        SceneryType('fern', [" \\|/ ", "  |  "], 3, spawn_weight=1.5),
        SceneryType('vine', ["  ~  ", "  ~  ", "  ~  "], 3, spawn_weight=1.0),
    ],
    distant_scenery=[
        SceneryType('monkey', [" @_@ ", "\\o_o/"], 6, spawn_weight=0.7),
        SceneryType('flower', [" \\|/ ", " (o) "], 2, spawn_weight=0.6),
        SceneryType('mushroom', [" _n_ ", "(___)"], 1, spawn_weight=0.5),
    ],
    music_config=MusicConfig(
        scale_name='E Major',
        root_note='E4',
        scale_type='major',
        progression_style='retro',
        melody_style='upbeat',
        drum_pattern='fast',
        groove='triplet',
        bpm=140
    )
)

SPACE_LEVEL = LevelSpec(
    name="GALAXY",
    distance_threshold=4000,
    sky_config=SkyConfig(
        color_pair=5,  # Purple/magenta
        sky_type='overcast',
        objects=[
            {'type': 'stars', 'count': 20, 'speed': 0.05},
            {'type': 'planets', 'count': 3, 'speed': 0.02}
        ],
        background_pattern={'type': 'stars', 'color_pair': 5},
        horizon_decorations=[
            {'type': 'planet', 'positions': [25, 75], 'art': [' O ', '(O)', ' O ']},
            {'type': 'satellite', 'positions': [40, 100], 'art': ['<|>', ' | ']},
        ]
    ),
    roadside_scenery=[
        SceneryType('space_rock', [" ___ ", "/ o \\", "\\___/"], 6, spawn_weight=1.8),
        SceneryType('antenna_dish', [" ((( ", " ||| ", "[###]"], 4, spawn_weight=1.3),
        SceneryType('alien_plant', ["  @  ", " \\|/ ", "  |  "], 5, spawn_weight=1.0),
    ],
    distant_scenery=[
        SceneryType('alien', [" o_o ", "/[#]\\"], 3, spawn_weight=0.7),
        SceneryType('crater', ["  _  ", "/ _ \\", "\\___/"], 6, spawn_weight=0.6),
        SceneryType('ufo', [" <o> ", " === "], 7, spawn_weight=0.4),
    ],
    music_config=MusicConfig(
        scale_name='B Minor',
        root_note='B4',
        scale_type='minor',
        progression_style='pop',
        melody_style='balanced',
        drum_pattern='syncopated',
        groove='straight',
        bpm=130
    )
)

VOLCANO_LEVEL = LevelSpec(
    name="VOLCANO",
    distance_threshold=4500,
    sky_config=SkyConfig(
        color_pair=1,  # Red/orange
        sky_type='overcast',
        objects=[
            {'type': 'ash', 'count': 15, 'speed': 0.15},
            {'type': 'embers', 'count': 8, 'speed': 0.3}
        ],
        background_pattern={'type': 'smoke', 'color_pair': 1},
        horizon_decorations=[
            {'type': 'volcano', 'positions': [40, 80], 'art': ['  ^  ', ' /X\\ ', '/XXX\\', '-----']},
            {'type': 'lava_flow', 'positions': [25, 60, 95], 'art': ['~~~', '~~~']},
        ]
    ),
    roadside_scenery=[
        SceneryType('lava_rock', [" ___ ", "/XXX\\", "\\XXX/"], 1, spawn_weight=2.0),
        SceneryType('smoke_vent', ["  ~  ", " ~~~ ", "~~~~~"], 4, spawn_weight=1.5),
        SceneryType('charred_tree', ["  |  ", " /|\\ ", "  |  ", "  |  "], 1, spawn_weight=1.2),
    ],
    distant_scenery=[
        SceneryType('lava_pool', [" oOo ", "(~~~)", " ~~~ "], 1, spawn_weight=0.8),
        SceneryType('steam', ["  ~  ", " ~~~ "], 7, spawn_weight=0.7),
        SceneryType('ash_pile', [" ___ ", "/___\\"], 7, spawn_weight=0.5),
    ],
    music_config=MusicConfig(
        scale_name='D Minor',
        root_note='D4',
        scale_type='minor',
        progression_style='dark',
        melody_style='dramatic',
        drum_pattern='heavy',
        groove='straight',
        bpm=135
    )
)

OCEAN_LEVEL = LevelSpec(
    name="OCEAN",
    distance_threshold=5000,
    sky_config=SkyConfig(
        color_pair=4,  # Cyan/blue
        sky_type='clear',
        objects=[
            {'type': 'waves', 'count': 10, 'speed': 0.1},
            {'type': 'bubbles', 'count': 12, 'speed': 0.25},
            {'type': 'fish', 'count': 6, 'speed': 0.2}
        ],
        background_pattern={'type': 'water', 'color_pair': 4},
        horizon_decorations=[
            {'type': 'coral', 'positions': [30, 70, 100], 'art': [' Y ', 'YYY', ' Y ']},
            {'type': 'shipwreck', 'positions': [50], 'art': ['|~|', '|#|', '###']},
        ]
    ),
    roadside_scenery=[
        SceneryType('coral_reef', ["  Y  ", " YYY ", "YYYYY"], 4, spawn_weight=2.0),
        SceneryType('seaweed', ["  ~  ", "  ~  ", " ~~~ "], 3, spawn_weight=1.8),
        SceneryType('treasure_chest', [" ___ ", "[===]", "[###]"], 2, spawn_weight=1.0),
    ],
    distant_scenery=[
        SceneryType('jellyfish', ["  o  ", " (o) ", "  ~  "], 4, spawn_weight=0.9),
        SceneryType('starfish', [" \\|/ ", "--*--", " /|\\ "], 6, spawn_weight=0.7),
        SceneryType('anemone', [" ))) ", " ||| "], 5, spawn_weight=0.6),
    ],
    music_config=MusicConfig(
        scale_name='A Major',
        root_note='A4',
        scale_type='major',
        progression_style='ambient',
        melody_style='flowing',
        drum_pattern='light',
        groove='triplet',
        bpm=110
    )
)

LEVELS = [BEACH_LEVEL, CITY_LEVEL, FACTORY_LEVEL, DESERT_LEVEL, HAUNTED_LEVEL, NEON_LEVEL, SNOW_LEVEL, JUNGLE_LEVEL, SPACE_LEVEL, VOLCANO_LEVEL, OCEAN_LEVEL]


def get_level_for_distance(distance, settings=None):
    """Return the appropriate level based on distance traveled and settings"""
    if settings is None:
        # Fallback to default behavior
        for level in reversed(LEVELS):
            if distance >= level.distance_threshold:
                return level
        return LEVELS[0]
    
    # Get active levels from settings
    active_indices = settings.get_active_levels()
    if not active_indices:
        return LEVELS[0]  # Fallback
    
    # Build active levels with dynamic thresholds
    active_levels = []
    for i, level_idx in enumerate(active_indices):
        threshold = i * settings.level_length
        active_levels.append((threshold, LEVELS[level_idx]))
    
    # Handle endless mode
    if settings.endless_mode and active_levels:
        # Calculate which loop we're in
        total_length = len(active_indices) * settings.level_length
        normalized_distance = distance % total_length
        
        for threshold, level in reversed(active_levels):
            if normalized_distance >= threshold:
                return level
        return active_levels[0][1]
    else:
        # Normal mode - find current level
        for threshold, level in reversed(active_levels):
            if distance >= threshold:
                return level
        return active_levels[0][1]

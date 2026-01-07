# Terminal Tour 🚗

A retro-style endless racing game built entirely in your terminal with ASCII art! 

## Features

- **11 Themed Levels**: Diverse zones including Beach, City, Factory, Desert, Haunted, Neon, Arctic, Jungle, Galaxy, Volcano, and Ocean
- **Procedural Chiptune Music**: Unique music for each level with melody, bass, harmony, and drums
- **3D Perspective Road**: Dynamic curves and realistic perspective rendering
- **Traffic System**: Dodge traffic cars and earn points
- **Smooth Transitions**: Seamless level changes with visual effects
- **Customizable Settings**: Configure levels, music, and game modes
- **Sound Mixer**: Adjust individual instrument volumes

## Controls

- **Arrow Keys** or **WASD**: Steer and control speed
- **ESC**: Pause menu
- **Q**: Quit

## Installation

**Windows**:
```bash
pip install -r requirements.txt
python terminal_tour.py
```

**Linux/macOS**:
```bash
pip3 install -r requirements.txt
python3 terminal_tour.py
# Or make executable:
chmod +x terminal_tour.py
./terminal_tour.py
```

## Requirements

- Python 3.6+
- pygame (for music)
- numpy (for audio generation)
- curses (built-in on Linux/macOS, auto-installed on Windows)

Music is optional - the game works without pygame/numpy.

## Tips

- Moderate speed in heavy traffic
- Use full road width strategically
- Higher speeds = more distance but harder dodging

Enjoy the ride! 🌴🌅

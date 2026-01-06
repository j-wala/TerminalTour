# ASCII OutRun 🏎️

A retro OutRun-style racing game built entirely with ASCII art in the terminal!

## Features

- **Perspective Road Rendering**: 3D-style road with proper perspective effect and curves
- **Dynamic Curves**: Road bends left and right for realistic racing
- **Player Controls**: Smooth, responsive left/right movement and speed control
- **Traffic System**: Dynamic traffic cars to avoid
- **Roadside Trees**: Scrolling trees with perspective scaling for immersion
- **Collision Detection**: Game over when hitting traffic or road edges
- **Scoring System**: Earn points for each car you pass
- **Chiptune Music**: Procedurally generated retro 8-bit background music
- **Retro Aesthetics**: Colorful terminal graphics with classic arcade feel
- **Speed Control**: Accelerate and decelerate to navigate traffic

## Controls

- **Arrow Keys** or **WASD**: Navigate your car
  - Left/Right or A/D: Move left and right
  - Up/Down or W/S: Increase/decrease speed
- **Q**: Quit game
- **R**: Restart after game over

## How to Play

1. Run the game:
   ```
   python outrun.py
   ```

2. Avoid traffic cars (red) while staying on the road
3. Pass cars to earn points (10 points per car)
4. Control your speed to navigate through traffic
5. Try to drive as far as possible without crashing!

## Requirements

- Python 3.6+
- Windows `windows-curses` module
- pygame for music
- numpy for audio generation

## Installation

```bash
pip install -r requirements.txt
```

Then simply run:
```bash
python outrun.py
```

To play without music (if pygame/numpy aren't available), the game will still work - music is optional.

## Tips

- Higher speeds earn distance faster but make it harder to dodge
- Keep your speed moderate in heavy traffic
- Use the full width of the road to your advantage
- Watch the road edges - they narrow at the top!

Enjoy the ride! 🌴🌅

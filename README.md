# PySnakes 🐍

A modern, feature-rich implementation of the classic Snake game built with Python and Pygame.

![Python](https://img.shields.io/badge/Python-3.14-blue.svg)
![Pygame](https://img.shields.io/badge/Pygame--CE-2.6.1-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## ✨ Features

### �� Gameplay

- **Classic Snake Mechanics** - Eat food, grow longer, avoid collisions
- **Progressive Difficulty** - More enemy snakes as you advance through levels
- **Multiple Game Modes** - Normal play and screensaver mode
- **God Mode** - Toggle invincibility with the 'G' key
- **Spawn Protection** - 3-second invincibility after respawning
- **High Score System** - Your best scores are saved and displayed

### 🎨 Visual Design

- **Smooth 60 FPS** - Interpolated graphics for fluid movement
- **Spherical Snake Design** - Rendered as circles with gradients and 3D highlights
- **Animated Eyes** - Snake eyes dynamically look in the direction of movement
- **Detailed Food** - Four fruit types (apples, cherries, oranges, lemons) with pulsing glow effects
- **Dynamic Background** - Engaging particle animations during gameplay
- **Death Animation** - Dramatic blinking and falling effects when you lose
- **Visual Feedback** - Invincibility indicators, god mode display, and smooth transitions

### 🤖 Advanced AI

- **Smart Enemy Snakes** - Intelligent pathfinding and collision avoidance
- **Predictive Planning** - Look-ahead algorithm to avoid traps
- **Corner Escape Logic** - Specialized behavior to escape dangerous positions
- **Food Seeking** - Balanced food pursuit with safety checks
- **Multiple AI Snakes** - Up to 5 AI opponents in higher levels

### 🔊 Audio

- **Sound Effects** - Audio feedback for eating, collisions, and game events
- **Background Music** - Dynamic music during gameplay
- **Volume Control** - Adjustable audio levels

### 🖥️ Screen Modes

- **Windowed Mode** - Standard 800x800 gameplay window
- **Fullscreen Screensaver** - Press 'S' for fullscreen with decorative snakes
- **Adaptive Scaling** - Proper scaling across different screen resolutions

## 🎯 Controls

| Key            | Action                                        |
| -------------- | --------------------------------------------- |
| **Arrow Keys** | Control snake direction                       |
| **SPACE**      | Start game / Continue to next level / Restart |
| **R**          | Restart game after game over                  |
| **ESC**        | Return to main menu                           |
| **P**          | Pause/Resume game                             |
| **S**          | Toggle screensaver mode (fullscreen)          |
| **G**          | Toggle god mode (invincibility)               |

## 🚀 Installation

### Prerequisites

- Python 3.14 or later
- pip (Python package installer)

**macOS Users**: Install SDL libraries for proper Pygame audio support:
\`\`\`bash
brew install sdl2 sdl2_image sdl2_mixer sdl2_ttf portmidi
\`\`\`

### Setup

1. **Clone the repository**
   \`\`\`bash
   git clone https://github.com/JoergKau/Python-Modern-SnakeGame.git
   cd Python-Modern-SnakeGame
   \`\`\`

2. **Create virtual environment**
   \`\`\`bash
   python3 -m venv .venv
   \`\`\`

3. **Activate virtual environment**

   - macOS/Linux:
     \`\`\`bash
     source .venv/bin/activate
     \`\`\`
   - Windows:
     \`\`\`bash
     .venv\Scripts\activate
     \`\`\`

4. **Install dependencies**
   \`\`\`bash
   pip install -r requirements.txt
   \`\`\`

5. **Run the game**
   \`\`\`bash
   python main.py
   \`\`\`

## 📦 Building Executable (Windows)

Create a standalone Windows executable that runs without Python installed.

### Quick Build

Simply double-click `build_windows.bat` or run it from command line:

```batch
build_windows.bat
```

The script will:

- Clean previous builds (`build/` and `dist/` folders)
- Use PyInstaller to create a single executable
- Bundle all assets (fonts, sounds, highscores.json)
- Include the application icon
- Create `dist/PySnakes.exe` (one file, ~15-20 MB)

### What You Get

- **Single File**: `dist/PySnakes.exe` - no folders, no dependencies
- **All Assets Included**: Fonts, sounds, and resources bundled inside
- **No Python Required**: Runs on any Windows PC (Windows 7+)
- **No Installation**: Just copy and run

### Distribution

Copy `PySnakes.exe` from the `dist/` folder to any Windows computer and double-click to play. No installation or configuration needed!

### Build Requirements

- Windows OS (executable must be built on Windows)
- Python 3.14+ with PyInstaller installed (from `requirements.txt`)

## 🏗️ Project Structure

\`\`\`
PySnakes/
├── main.py # Game entry point
├── requirements.txt # Python dependencies
├── src/
│ ├── game.py # Main game loop and state management
│ ├── snake.py # Core snake entity (358 lines)
│ ├── snake_rendering.py # Snake rendering mixin (179 lines)
│ ├── snake_death_animation.py # Death animation mixin (208 lines)
│ ├── snake_ai.py # AI decision-making mixin (475 lines)
│ ├── food.py # Food spawning and rendering
│ ├── particle.py # Particle system for effects
│ ├── sound_manager.py # Audio management
│ ├── highscore_manager.py # High score persistence
│ ├── background.py # Animated backgrounds
│ ├── screensaver.py # Screensaver mode
│ ├── renderer.py # UI and screen rendering
│ ├── config.py # Game configuration
│ └── utils.py # Resource path utilities
└── assets/
├── fonts/ # Game fonts
└── sounds/ # Sound effects and music
\`\`\`

## 🏛️ Architecture Highlights

### Mixin Pattern

The snake entity uses a clean mixin architecture for separation of concerns:

- **SnakeRenderingMixin** - All visual rendering
- **SnakeDeathAnimationMixin** - Death animation effects
- **SnakeAIMixin** - AI decision-making and pathfinding

This reduces the main snake.py from 1,184 lines to 358 lines (70% reduction) while maintaining full functionality.

### Key Design Patterns

- **State Machine** - Game state management (menu, playing, paused, game over, screensaver)
- **Entity-Component** - Modular game entities (snake, food, particles)
- **Observer Pattern** - Event-driven audio and visual effects
- **Resource Management** - PyInstaller-compatible asset loading

## 🎓 Learning Resources

This project demonstrates:

- Python game development with Pygame
- Object-oriented design patterns
- AI pathfinding algorithms (flood-fill, danger scoring)
- Smooth interpolation and animation
- Audio/visual effect management
- Executable packaging with PyInstaller

## 🐛 Troubleshooting

### macOS: \`NotImplementedError: mixer module not available\`

Install SDL libraries and rebuild Pygame:
\`\`\`bash
brew install sdl2 sdl2_image sdl2_mixer sdl2_ttf portmidi
pip install --no-cache-dir --force-reinstall pygame-ce
\`\`\`

### Windows: Missing fonts/sounds in executable

Use the provided \`build_windows.bat\` script which properly bundles all assets.

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👤 Author

**Jörg Kauschke**

- GitHub: [@JoergKau](https://github.com/JoergKau)
- Repository: [Python-Modern-SnakeGame](https://github.com/JoergKau/Python-Modern-SnakeGame)

## 🙏 Acknowledgments

- Pygame Community Edition team
- SDL library developers

---

**Enjoy the game! 🎮🐍**

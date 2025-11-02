# PySnakes Development Documentation

Complete technical documentation for developers working on PySnakes.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Mixin Refactoring](#mixin-refactoring)
3. [Asset Bundling & PyInstaller](#asset-bundling--pyinstaller)
4. [Game Features Implementation](#game-features-implementation)
5. [AI System](#ai-system)
6. [Visual Effects](#visual-effects)
7. [Code Organization](#code-organization)
8. [Build Process](#build-process)

---

## Architecture Overview

### Project Structure

```
PySnakes/
├── main.py                      # Entry point
├── requirements.txt             # Dependencies (pygame-ce==2.6.1)
├── src/
│   ├── __init__.py
│   ├── game.py                  # Game loop & state machine (700+ lines)
│   ├── config.py                # Configuration constants
│   ├── renderer.py              # UI rendering (417 lines)
│   ├── snake.py                 # Core snake (358 lines) - uses mixins
│   ├── snake_rendering.py       # Rendering mixin (179 lines)
│   ├── snake_death_animation.py # Death animation mixin (208 lines)
│   ├── snake_ai.py              # AI mixin (475 lines)
│   ├── food.py                  # Food entity
│   ├── particle.py              # Particle effects
│   ├── sound_manager.py         # Audio management
│   ├── highscore_manager.py     # Score persistence
│   ├── background.py            # Background animations
│   ├── screensaver.py           # Screensaver mode
│   └── utils.py                 # Resource utilities
└── assets/
    ├── fonts/                   # TTF fonts
    └── sounds/                  # WAV audio files
```

### State Machine

Game uses enum-based state management:

```python
class GameState(Enum):
    SPLASH = 0
    MENU = 1
    PLAYING = 2
    LEVEL_COMPLETE = 3
    GAME_OVER = 4
    PAUSED = 5
    GAME_WON = 6
    SCREENSAVER = 7
```

**State Transitions:**

- SPLASH → MENU (after 3 seconds)
- MENU → PLAYING (SPACE key)
- PLAYING → PAUSED (P key)
- PLAYING → LEVEL_COMPLETE (all food eaten)
- PLAYING → GAME_OVER (player dies)
- GAME_OVER → PLAYING (SPACE/R key)
- GAME_OVER → MENU (ESC key)
- Any → SCREENSAVER (S key)
- SCREENSAVER → previous state (S/ESC key)

---

## Mixin Refactoring

### Overview

**Problem:** Original `snake.py` was 1,184 lines - difficult to maintain and navigate.

**Solution:** Split into focused mixin classes using multiple inheritance.

### Architecture

```python
class Snake(SnakeRenderingMixin, SnakeDeathAnimationMixin, SnakeAIMixin):
    # Core logic only (358 lines)
```

### File Breakdown

#### 1. `snake.py` (358 lines - Core)

**Responsibilities:**

- Snake initialization and configuration
- Spawning and position management
- Movement and growth logic
- Invincibility system
- Grid utility methods

**Key Methods:**

- `__init__()` - Setup with game reference, AI flag
- `spawn(segment_count, avoid_snakes)` - Spawn with safety checks
- `_find_safe_spawn_position()` - Avoid other snakes when spawning
- `update()` - Main update loop (calls AI if needed)
- `update_smooth_movement(dt)` - Interpolation for smooth rendering
- `grow()` - Add segment on food consumption
- `set_direction()` - Prevent 180-degree turns
- `update_invincibility()` - Manage spawn protection
- Grid methods: `get_grid_width()`, `get_grid_height()`, `get_cell_size()`

#### 2. `snake_rendering.py` (179 lines - Rendering Mixin)

**Responsibilities:**

- Visual rendering of snake
- Alpha transparency effects
- Highlight and outline drawing
- Eye animation

**Key Methods:**

- `draw(alpha_multiplier, surface)` - Main draw with optional surface parameter
- `draw_circular_segment()` - Segment rendering with alpha
- `draw_circular_highlight()` - 3D highlight effect
- `draw_outline_with_alpha()` - Pulsing outline for player
- `draw_eyes()` - Direction-aware eye rendering
- `draw_circle_with_alpha()` - Helper for alpha blending

**Features:**

- Optional surface parameter for decorative snakes
- Smooth interpolation between grid positions
- Invincibility blink effect
- Direction-based eye positioning (4 directions)
- Gradient coloring from head to tail

#### 3. `snake_death_animation.py` (208 lines - Animation Mixin)

**Responsibilities:**

- Death animation sequence
- Blinking and falling effects
- X-shaped death eyes

**Key Methods:**

- `start_death_animation()` - Initialize animation state
- `update_death_animation(dt)` - Update animation phases
- `draw_death_animation()` - Render death sequence
- `draw_death_eyes()` - X eyes during death
- `draw_line_with_alpha()` - Helper for X drawing

**Animation Phases:**

1. **Blink Phase** (0.6s):

   - Snake blinks on/off
   - X-shaped eyes appear
   - Body remains in place

2. **Fall Phase** (1.5s):
   - Segments fall at different speeds
   - Alpha fades out
   - Segments disappear off-screen

#### 4. `snake_ai.py` (475 lines - AI Mixin)

**Responsibilities:**

- AI decision-making
- Pathfinding and danger avoidance
- Food seeking
- Trap detection and escape

**Key Methods:**

- `make_ai_decision()` - Main AI logic (126 lines)
- `calculate_direction_score(direction)` - Score movement options (99 lines)
- `_find_immediate_dangers()` - Detect immediate threats
- `_find_potential_traps()` - Identify trap situations
- `_plan_escape_route()` - Calculate escape paths
- `_calculate_escape_space(pos)` - Flood-fill space calculation
- `_choose_direction_away_from_danger()` - Select safest direction
- `_is_path_to_food_safe()` - Validate food pathfinding
- `_calculate_corner_danger()` - Corner/wall danger scoring
- `is_safe(pos)` - Basic position safety check

### Benefits

**Code Organization:**

- 70% reduction in main file size (1,184 → 358 lines)
- Single responsibility per file
- Clear separation of concerns
- Easy to locate and modify specific functionality

**Maintainability:**

- Changes to rendering don't affect AI
- AI improvements don't risk breaking animations
- Each mixin testable in isolation
- Better code readability

**Reusability:**

- Mixins can be reused for other entities
- Easy to create variants (e.g., AI-only snake)
- Flexible composition

**No Breaking Changes:**

- All methods still accessible via `self`
- Python MRO handles method lookup
- Cross-mixin calls work seamlessly
- 100% backward compatible

### Method Resolution Order (MRO)

Python searches for methods in this order:

1. Snake (core class)
2. SnakeRenderingMixin
3. SnakeDeathAnimationMixin
4. SnakeAIMixin
5. object (base class)

All mixins share access to `self` attributes:

- `self.screen` - Pygame surface
- `self.game` - Game instance
- `self.body` - List of positions
- `self.direction` - Current direction vector
- `self.position` - Head position
- `self.is_ai` - AI flag
- All other Snake attributes

---

## Asset Bundling & PyInstaller

### Problem

Original PyInstaller builds failed when deployed to other PCs:

- Missing fonts → default ugly system font
- Missing sounds → silent game
- Missing highscores.json → crash on save

**Root Cause:** Python code used relative paths (`"assets/fonts/font.ttf"`) that don't work in PyInstaller bundles where resources are extracted to `sys._MEIPASS`.

### Solution

Created `src/utils.py` with PyInstaller-aware resource management:

```python
import sys
import os

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and PyInstaller."""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)
```

### Updated Files

**1. `sound_manager.py`**

```python
from src.utils import resource_path

def load_sound(self, filename):
    path = resource_path(f"assets/sounds/{filename}")
    return pygame.mixer.Sound(path)
```

**2. `game.py` (Font Loading)**

```python
from src.utils import resource_path

self.font_large = pygame.font.Font(
    resource_path("assets/fonts/PressStart2P-Regular.ttf"), 24
)
```

**3. `highscore_manager.py`**

```python
from src.utils import resource_path

def __init__(self):
    self.highscore_file = resource_path("highscores.json")
```

### Build Script Enhancement

`build_windows.bat` now:

1. Uses `--onefile` for single executable
2. Bundles all assets with `--add-data`
3. Sets proper icon with `--icon`
4. Hides console with `--windowed`
5. Validates build output

```batch
pyinstaller --onefile --windowed ^
  --add-data "assets;assets" ^
  --add-data "highscores.json;." ^
  --icon="assets/icon.ico" ^
  --name PySnakes ^
  main.py
```

### Result

✅ Single `PySnakes.exe` file  
✅ All fonts, sounds, and data included  
✅ Works on any Windows PC  
✅ No Python installation required  
✅ No separate asset folders needed

---

## Game Features Implementation

### 1. God Mode

**Feature:** Press 'G' to toggle invincibility.

**Implementation:**

```python
# In game.py
if event.key == pygame.K_g:
    self.god_mode_enabled = not self.god_mode_enabled

# Collision detection
if not self.god_mode_enabled:
    # Check collisions
    pass
```

**Visual Indicator:**

- "GOD MODE" text at top of screen when active
- Yellow color for visibility

### 2. Spawn Invincibility

**Feature:** 3-second protection after spawning.

**Why:** Prevents instant death when spawning near enemies or in corners.

**Implementation:**

```python
# Automatic activation in spawn()
def _activate_invincibility(self):
    if not self.is_ai:
        self.is_invincible = True
        self.invincibility_start_time = pygame.time.get_ticks()

# Update each frame
def update_invincibility(self):
    if self.is_invincible:
        elapsed = pygame.time.get_ticks() - self.invincibility_start_time
        if elapsed >= self.invincibility_duration:  # 3000ms
            self.is_invincible = False
```

**Visual Feedback:**

- Snake blinks (alpha modulation)
- HUD shows "INVINCIBLE X.Xs" countdown
- Faster blinking in final 30% of duration
- Text color changes to yellow when ending

**Collision Behavior:**

- Player immune to all collisions
- Can pass through enemies and self
- Cannot leave boundaries (like god mode)

### 3. Progressive Scoring

**Feature:** Points per apple increase with level.

**Formula:**

```python
def get_points_per_apple(level):
    return 10 + (level - 1) * 5

# Level 1: 10 points
# Level 2: 15 points
# Level 3: 20 points
# Level 10: 55 points
```

**Implementation:** Centralized in `config.py` for easy tuning.

### 4. Decorative Snakes

**Feature:** Background snakes on menu screens that turn instead of respawning.

**Why:** More natural movement, less jarring than disappearing/reappearing.

**Implementation:**

```python
def _update_decorative_snakes(self, dt):
    for snake in self.decorative_snakes:
        # Check if about to hit wall or self
        next_pos = snake.position + snake.direction

        if not snake.is_safe(next_pos):
            # Find safe directions
            safe_dirs = [d for d in all_directions
                        if snake.is_safe(snake.position + d)]

            if safe_dirs:
                snake.direction = random.choice(safe_dirs)
```

**Note:** Uses `is_safe()` method with special handling:

```python
def is_safe(self, pos):
    # During menu screens, game.snakes might not exist
    if hasattr(self.game, 'snakes'):
        # Check game snakes
        pass
    return True
```

### 5. Screensaver Mode

**Feature:** Fullscreen mode with decorative snakes.

**Implementation:**

- Detects native resolution
- Calculates grid to fill screen
- Spawns snakes with random segment counts (3-6)
- Returns to windowed on exit

```python
def enter_screensaver_mode(self):
    info = pygame.display.Info()
    self.screen = pygame.display.set_mode((info.current_w, info.current_h),
                                          pygame.FULLSCREEN)

    # Calculate grid for full screen
    self.screensaver_grid_width = info.current_w // cell_size
    self.screensaver_grid_height = info.current_h // cell_size

    # Spawn decorative snakes
    for _ in range(num_snakes):
        snake = Snake(self, is_ai=True, min_segments=3, max_segments=6)
```

### 6. Death Animation

**Original Problem:** Player death was instant - jarring and no visual feedback.

**Solution:** Two-phase animation system:

**Phase 1 - Blink (0.6s):**

- Snake blinks on/off every 100ms
- X-shaped eyes appear
- Red coloration (if desired)
- Body stays in place

**Phase 2 - Fall (1.5s):**

- Each segment falls at random speed (100-300 px/s)
- Alpha fades from 255 → 0
- Segments fall off screen

**Total Duration:** 2.1s + buffer before game over screen

**Code:**

```python
# Start animation
def start_death_animation(self):
    self.is_dying = True
    self.segment_fall_speed = [random.uniform(100, 300)
                               for _ in self.body]
    self.segment_alpha = [255 for _ in self.body]
    self.blink_timer = 0

# Update each frame
def update_death_animation(self, dt):
    self.blink_timer += dt

    if self.blink_timer < BLINK_DURATION:
        # Blink phase
        self.blink_phase = (int(self.blink_timer / 100) % 2 == 0)
    else:
        # Fall phase
        for i in range(len(self.body)):
            self.body[i].y += self.segment_fall_speed[i] * dt / 1000
            self.segment_alpha[i] = max(0, self.segment_alpha[i] - 200 * dt / 1000)
```

**Timing:** Provides smooth visual feedback with appropriate pacing.

### 7. Surface Parameter Pattern

**Problem:** Decorative snakes used hacky screen swapping.

**Original Code:**

```python
# Save screen
temp_screen = snake.screen
snake.screen = decorative_surface

# Draw
snake.draw()

# Restore
snake.screen = temp_screen
```

**Solution:** Optional surface parameter:

```python
def draw(self, alpha_multiplier=1.0, surface=None):
    target = surface if surface is not None else self.screen
    # Draw to target
```

**Benefits:**

- Cleaner API
- No state mutation
- More flexible
- Thread-safe

**Usage:**

```python
# Draw to main screen
snake.draw()

# Draw to custom surface
snake.draw(surface=decorative_surface)

# Draw with alpha
snake.draw(alpha_multiplier=0.5, surface=overlay)
```

---

## AI System

### Overview

Enemy snakes use a sophisticated AI system with multiple layers of decision-making:

1. **Emergency Response** - Escape corners/edges
2. **Danger Avoidance** - Avoid immediate threats
3. **Exploration** - Random movement for variety
4. **Food Seeking** - Head toward food when safe

### Decision Priority

```
Corner Detection (100% response)
    ↓
Edge Avoidance (90% chance)
    ↓
Immediate Danger (always)
    ↓
Random Exploration (30% chance)
    ↓
Continue Current Direction
```

### Main Algorithm

```python
def make_ai_decision(self):
    # 1. Check if in corner
    in_corner = (near_left and near_top) or ...

    if in_corner:
        # ALWAYS escape - find directions away from BOTH edges
        escape_dirs = [d for d in all_dirs
                      if escapes_corner(d) and is_safe(d)]
        if escape_dirs:
            self.direction = random.choice(escape_dirs)
            return

    # 2. Near edge? Turn away (90% chance)
    if near_edge and random.random() < 0.9:
        away_dirs = [d for d in all_dirs
                    if moves_away_from_edge(d) and is_safe(d)]
        if away_dirs:
            self.direction = random.choice(away_dirs)
            return

    # 3. Current direction dangerous?
    if not is_safe(position + direction):
        safe_dirs = [d for d in all_dirs if is_safe(position + d)]
        if safe_dirs:
            self.direction = random.choice(safe_dirs)
            return

    # 4. Random exploration (30% chance)
    if random.random() < 0.3:
        valid_dirs = [d for d in all_dirs if is_safe(position + d)]
        if valid_dirs:
            self.direction = random.choice(valid_dirs)
```

### Direction Scoring

For more sophisticated AI, each direction gets a score:

```python
def calculate_direction_score(self, direction):
    score = 0
    next_pos = self.position + direction

    # 1. Wall check (-1000 if hits wall)
    if not in_bounds(next_pos):
        return -1000

    # 2. Self-collision check (-1000)
    if next_pos in self.body:
        return -1000

    # 3. Other snakes
    for snake in other_snakes:
        for segment in snake.body:
            dist = (next_pos - segment).length()

            # Very close = heavy penalty
            if dist < BODY_DANGER_RADIUS:
                score -= (BODY_DANGER_RADIUS - dist) * 100
            elif dist < DANGER_ZONE_RADIUS:
                score -= (DANGER_ZONE_RADIUS - dist) * 10

    # 4. Look-ahead (check future positions)
    for step in range(1, LOOK_AHEAD_STEPS):
        look_pos = next_pos + direction * step
        if not in_bounds(look_pos):
            score -= 50  # Approaching wall

    # 5. Food pathfinding
    if food exists:
        dist_to_food = (next_pos - food.position).length()

        if is_path_to_food_safe(next_pos, direction):
            score += (max_grid_size - dist_to_food) * 1.5
        else:
            score += (max_grid_size - dist_to_food) * 0.3

    # 6. Center preference
    dist_to_center = (next_pos - center).length()
    score += (1 - dist_to_center / max_dist) * 15

    # 7. Corner danger
    score -= calculate_corner_danger(next_pos, direction)

    return score
```

### Escape Route Planning

When trapped, AI uses flood-fill to find open space:

```python
def _calculate_escape_space(self, pos):
    """Count reachable cells from position."""
    visited = set()
    queue = [pos]
    count = 0
    max_search = 10  # Don't search too deep

    while queue and count < max_search:
        current = queue.pop(0)

        if current in visited:
            continue

        visited.add(current)
        count += 1

        # Check neighbors
        for direction in [UP, DOWN, LEFT, RIGHT]:
            neighbor = current + direction

            if neighbor not in visited and is_safe(neighbor):
                queue.append(neighbor)

    return count
```

**Usage:** Pick direction with most open space when escaping.

### Food Path Safety

Before chasing food, verify path is safe:

```python
def _is_path_to_food_safe(self, current_pos, direction):
    """Check if heading toward food won't trap us."""

    # Calculate direction to food
    to_food = (food.position - current_pos).normalize()
    alignment = direction.dot(to_food)

    # Not aligned? Not heading to food
    if alignment < 0.5:
        return False

    # Look ahead several steps
    for step in range(1, MEDIUM_LOOK_AHEAD):
        look_pos = current_pos + direction * step

        # Hit wall?
        if not in_bounds(look_pos):
            return False

        # Too close to other snakes?
        for snake in other_snakes:
            for segment in snake.body:
                if (look_pos - segment).length() < 2:
                    return False

    return True  # Path looks safe
```

### AI Configuration

All AI parameters in `config.py`:

```python
# AI Settings
AI_DANGER_ZONE_RADIUS = 5      # Avoid snakes within this distance
AI_BODY_DANGER_RADIUS = 2      # High danger if very close
AI_LOOK_AHEAD_STEPS = 3        # Steps to predict ahead
AI_MEDIUM_LOOK_AHEAD = 5       # Food path lookahead
AI_CORNER_TRAP_THRESHOLD = 3   # Corner detection distance
AI_WALL_EMERGENCY_THRESHOLD = 5 # Wall escape threshold
```

**Tuning:** Adjust these to change AI difficulty.

---

## Visual Effects

### 1. Smooth Movement Interpolation

Snakes move on a grid, but rendering interpolates for smooth visuals:

```python
def update_smooth_movement(self, dt):
    move_interval = get_move_interval()
    self.move_progress += dt / move_interval
    self.move_progress = min(self.move_progress, 1.0)

def draw(self):
    for i, segment in enumerate(self.body):
        # Interpolate position
        if i == 0 and self.move_progress > 0:
            # Head: interpolate from previous position
            prev_pos = self.body[1] if len(self.body) > 1 else self.body[0]
            draw_pos = prev_pos + (segment - prev_pos) * self.move_progress
        else:
            # Other segments follow
            if i < len(self.body) - 1:
                next_pos = self.body[i + 1]
                draw_pos = next_pos + (segment - next_pos) * self.move_progress
            else:
                draw_pos = segment

        # Draw at interpolated position
        draw_segment(draw_pos)
```

**Result:** 60 FPS smooth movement even though game logic updates every 150-400ms.

### 2. Particle System

Food creates particles when eaten:

```python
class Particle:
    def __init__(self, position, velocity, color, lifetime):
        self.position = position
        self.velocity = velocity
        self.color = color
        self.lifetime = lifetime
        self.age = 0

    def update(self, dt):
        self.position += self.velocity * dt / 1000
        self.age += dt
        self.velocity *= 0.95  # Friction

    def draw(self, screen):
        alpha = 1.0 - (self.age / self.lifetime)
        radius = int(5 * alpha)
        # Draw with fading alpha
```

**Usage:**

```python
# When food eaten
for _ in range(10):
    velocity = random_direction() * random.uniform(50, 150)
    particle = Particle(food.position, velocity, food.color, 500)
    particles.append(particle)
```

### 3. Pulsing Effects

Food and player outline pulse for emphasis:

```python
# Food glow
glow_alpha = 150 + 105 * sin(time)
draw_circle_with_alpha(position, radius * 1.5, glow_color, glow_alpha)

# Player outline
pulse_alpha = 150 + 105 * sin(pulse_time)
draw_outline(position, radius * 1.1, WHITE, pulse_alpha)
```

### 4. Invincibility Blink

Visual feedback for spawn protection:

```python
def draw(self, alpha_multiplier=1.0):
    if self.is_invincible:
        elapsed = pygame.time.get_ticks() - self.invincibility_start_time

        # Modulate alpha for blinking
        blink_cycle = (elapsed % self.blink_speed) / self.blink_speed
        alpha_multiplier *= 0.3 + 0.7 * abs(sin(blink_cycle * pi))

    # Draw with modified alpha
    draw_segments(alpha_multiplier)
```

**Result:** Snake pulses between 30% and 100% opacity.

### 5. 3D Highlight Effect

Segments look spherical with highlight:

```python
def draw_circular_segment(self, x, y, radius, color, alpha):
    # Main circle
    draw_circle(x, y, radius, color, alpha)

    # Highlight (offset up-left)
    offset = radius // 4
    highlight_color = (255, 255, 200)  # Yellowish white
    draw_circle(x - offset, y - offset, radius // 2, highlight_color, alpha * 0.6)
```

**Result:** Gives depth and 3D appearance to 2D circles.

### 6. Dynamic Background

Animated particles in background:

```python
class BackgroundParticle:
    def __init__(self):
        self.x = random.randint(0, screen_width)
        self.y = random.randint(0, screen_height)
        self.speed = random.uniform(10, 30)
        self.radius = random.randint(1, 3)
        self.color = random_gray()

    def update(self, dt):
        self.y += self.speed * dt / 1000
        if self.y > screen_height:
            self.y = 0
            self.x = random.randint(0, screen_width)

    def draw(self, screen):
        draw_circle(self.x, self.y, self.radius, self.color)
```

**Usage:** 50-100 particles moving slowly downward.

---

## Code Organization

### Renderer Module

**Purpose:** Centralized UI rendering with helper methods.

**Key Methods:**

```python
def _draw_overlay(self, color, alpha):
    """Draw semi-transparent overlay."""
    overlay = pygame.Surface((self.screen.get_width(),
                             self.screen.get_height()))
    overlay.set_alpha(alpha)
    overlay.fill(color)
    self.screen.blit(overlay, (0, 0))

def _draw_centered_text(self, text, y_pos, color, font):
    """Draw text centered horizontally."""
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(self.screen.get_width() // 2, y_pos))
    self.screen.blit(text_surface, text_rect)

def _draw_title(self, text, y_pos, color):
    """Helper for title-sized text."""
    self._draw_centered_text(text, y_pos, color, self.font_title)

def _draw_large_text(self, text, y_pos, color):
    """Helper for large-sized text."""
    self._draw_centered_text(text, y_pos, color, self.font_large)
```

**Benefits:**

- Eliminated 45+ lines of duplicate code
- Consistent text centering
- Easy to modify UI appearance
- DRY principle

### Config Module

**Purpose:** Single source of truth for game parameters.

**Categories:**

```python
# Screen
SCREEN_SIZE = 800
FPS = 60

# Grid
GRID_SIZE = 20
CELL_SIZE = SCREEN_SIZE / GRID_SIZE  # 40 pixels

# Speed (milliseconds between moves)
PLAYER_MOVE_INTERVAL = 150  # Fast
ENEMY_MOVE_INTERVAL = 400   # Slower

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
# ... more colors

# Snake colors
SNAKE_COLOR_SCHEMES = [
    ((255, 140, 0), (255, 200, 100)),   # Orange
    ((0, 255, 127), (144, 238, 144)),   # Green
    # ... more schemes
]

# AI Parameters
AI_DANGER_ZONE_RADIUS = 5
AI_LOOK_AHEAD_STEPS = 3
# ... more AI params

# Game Logic
INITIAL_ENEMY_COUNT = 1
def get_enemy_count(level):
    return min(INITIAL_ENEMY_COUNT + (level - 1), 5)

def get_points_per_apple(level):
    return 10 + (level - 1) * 5

def get_enemy_initial_segments():
    return random.randint(3, 5)
```

**Benefits:**

- Easy tuning without searching code
- Consistent values across modules
- Dynamic calculations (level-based)
- Self-documenting

### Utils Module

**Purpose:** PyInstaller-compatible resource loading.

```python
import sys
import os

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and PyInstaller."""
    try:
        # PyInstaller extracts to temp folder
        base_path = sys._MEIPASS
    except AttributeError:
        # Normal Python execution
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)
```

**Usage:**

```python
# Instead of:
font = pygame.font.Font("assets/fonts/font.ttf", 24)

# Use:
from src.utils import resource_path
font = pygame.font.Font(resource_path("assets/fonts/font.ttf"), 24)
```

**Result:** Code works in development AND in PyInstaller executables.

---

## Build Process

### Windows Build (`build_windows.bat`)

```batch
@echo off
echo ========================================
echo Building PySnakes for Windows
echo ========================================

REM Clean previous builds
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist PySnakes.spec del PySnakes.spec

REM Build with PyInstaller
pyinstaller --onefile --windowed ^
  --add-data "assets;assets" ^
  --add-data "highscores.json;." ^
  --icon="assets/icon.ico" ^
  --name PySnakes ^
  main.py

REM Check if build succeeded
if exist dist\PySnakes.exe (
    echo.
    echo ========================================
    echo Build successful!
    echo Executable: dist\PySnakes.exe
    echo ========================================
) else (
    echo.
    echo ========================================
    echo Build failed! Check errors above.
    echo ========================================
    exit /b 1
)

pause
```

**Key Points:**

- `--onefile`: Single executable (not a folder)
- `--windowed`: No console window
- `--add-data`: Bundle assets into executable
- `--icon`: Custom application icon
- `--name`: Output filename

### Testing Build

After building, test on a clean system:

1. **Copy executable** to PC without Python
2. **Run executable** - should work immediately
3. **Check fonts** - should see custom fonts, not system defaults
4. **Check sounds** - should hear audio effects
5. **Check highscores** - should save/load correctly

### Build Validation Script

```python
# test_resources.py
import os
import sys

def test_resources():
    print("Testing resource bundling...")

    # Check if running from PyInstaller bundle
    if hasattr(sys, '_MEIPASS'):
        print(f"Running from bundle: {sys._MEIPASS}")

        # List bundled files
        for root, dirs, files in os.walk(sys._MEIPASS):
            for file in files:
                print(f"  {os.path.join(root, file)}")
    else:
        print("Running from source")

    # Test resource loading
    from src.utils import resource_path

    font_path = resource_path("assets/fonts/PressStart2P-Regular.ttf")
    print(f"\nFont path: {font_path}")
    print(f"Font exists: {os.path.exists(font_path)}")

    sound_path = resource_path("assets/sounds/eat.wav")
    print(f"Sound path: {sound_path}")
    print(f"Sound exists: {os.path.exists(sound_path)}")

if __name__ == "__main__":
    test_resources()
```

**Usage:**

```batch
# In source
python test_resources.py

# In build
PySnakes.exe --test-resources
```

### Common Build Issues

**Issue 1: Missing Module**

```
ModuleNotFoundError: No module named 'pygame'
```

**Solution:** Install in correct environment:

```bash
pip install -r requirements.txt
```

**Issue 2: Missing DLLs**

```
Error loading Python DLL
```

**Solution:** Use `--onefile` and ensure Python is properly installed.

**Issue 3: Assets Not Found**

```
FileNotFoundError: [Errno 2] No such file or directory: 'assets/sounds/eat.wav'
```

**Solution:**

1. Use `resource_path()` in all asset loading
2. Add assets to PyInstaller with `--add-data`

**Issue 4: Multiple Executables**
**Solution:** Use `--onefile` instead of `--onedir`

---

## Summary

### Key Achievements

1. **Mixin Architecture** - 70% reduction in main file complexity
2. **Asset Bundling** - Single-file executable with all resources
3. **Advanced AI** - Multi-layered decision-making with pathfinding
4. **Visual Polish** - Smooth animations, particle effects, 3D highlights
5. **Code Quality** - DRY principle, single responsibility, clear structure
6. **Build Process** - Automated, validated, cross-platform ready

### Design Principles

- **Separation of Concerns** - Each module has clear responsibility
- **DRY** - Helper methods eliminate duplication
- **Single Responsibility** - Classes focused on one task
- **Resource Management** - PyInstaller-compatible paths
- **State Machine** - Clear game state management
- **Progressive Enhancement** - Features built incrementally

### Performance

- **60 FPS** - Consistent frame rate
- **Smooth Interpolation** - Visual movement independent of logic updates
- **Efficient AI** - Decision-making doesn't impact frame rate
- **Particle System** - Hundreds of particles without slowdown

### Maintainability

- **Clear Structure** - Easy to find specific functionality
- **Mixin Pattern** - Changes isolated to specific areas
- **Config Centralization** - Easy parameter tuning
- **Helper Methods** - Consistent code patterns
- **Documentation** - Inline comments and docstrings

---

## Development Tips

### Adding New Features

1. **Determine module** - Where does it belong?
2. **Check config** - Any parameters to add?
3. **Update state machine** - New states needed?
4. **Test thoroughly** - Dev and built executable
5. **Update docs** - Document the feature

### Debugging

1. **Use print statements** - Visible in console (not with `--windowed`)
2. **Check logs** - PyInstaller creates logs in build folder
3. **Test resource paths** - Use `test_resources.py`
4. **Verify state transitions** - Print state changes
5. **Profile performance** - Use `cProfile` for bottlenecks

### Code Review Checklist

- [ ] No hardcoded paths (use `resource_path()`)
- [ ] Config values in `config.py`
- [ ] Methods < 50 lines (consider splitting)
- [ ] Docstrings on public methods
- [ ] No duplicate code (DRY principle)
- [ ] State transitions handled correctly
- [ ] Error handling for file operations
- [ ] Compatible with PyInstaller

---

**Last Updated:** November 2, 2025
**Version:** 1.0.0
**Python:** 3.14
**Pygame-CE:** 2.6.1

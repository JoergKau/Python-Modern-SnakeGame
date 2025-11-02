import pygame
import random
import math
from typing import List, Tuple, Optional, TYPE_CHECKING
from src import config
from src.snake_rendering import SnakeRenderingMixin
from src.snake_death_animation import SnakeDeathAnimationMixin
from src.snake_ai import SnakeAIMixin

if TYPE_CHECKING:
    from src.game import Game

class Snake(SnakeRenderingMixin, SnakeDeathAnimationMixin, SnakeAIMixin):
    def __init__(self, game: 'Game', is_ai: bool = False, min_segments: Optional[int] = None, max_segments: Optional[int] = None) -> None:
        self.game = game
        self.screen = game.screen
        self.is_ai = is_ai
        self.pulse_time = 0
        self.is_dead = False
        self.is_dying = False  # For death animation
        self.segment_fall_speed = []
        self.segment_alpha = []
        self.blink_phase = True
        self.blink_timer = 0
        self.blink_duration = config.BLINK_DURATION
        
        # Invincibility system for unsafe spawns - initialize BEFORE spawn
        self.is_invincible = False
        self.invincibility_start_time = 0
        self.invincibility_duration = 3000  # 3 seconds in milliseconds
        self.invincibility_blink_speed = 200  # Blink every 200ms
        
        # Store the initial segment count for respawning
        segment_count = self._get_segment_count(min_segments, max_segments)
        self.initial_segment_count = segment_count
        
        # For screensaver mode, allow random segment count
        self.spawn(segment_count=segment_count)

    def _get_segment_count(self, min_segments: Optional[int], max_segments: Optional[int]) -> int:
        """Get the appropriate segment count based on game state and parameters."""
        if min_segments is not None and max_segments is not None:
            return random.randint(min_segments, max_segments)
        elif self.is_ai and self.in_screensaver_mode():
            # For screensaver, use random length between 3-6
            return random.randint(3, 6)
        else:
            # Regular game mode - use default lengths
            if not self.is_ai:
                return 2  # Player starts with 2 segments
            else:
                return config.get_enemy_initial_segments()

    def in_screensaver_mode(self):
        """Check if the game is in screensaver mode."""
        return hasattr(self.game, 'game_state') and self.game.game_state.value == 7  # SCREENSAVER

    def get_grid_size(self):
        """Get the appropriate grid size based on game state.
        Returns a single value for backward compatibility (uses width)."""
        if self.in_screensaver_mode() and hasattr(self.game, 'screensaver_grid_width'):
            return self.game.screensaver_grid_width
        return config.GRID_SIZE
    
    def get_grid_width(self):
        """Get the grid width for the current mode."""
        if self.in_screensaver_mode() and hasattr(self.game, 'screensaver_grid_width'):
            return self.game.screensaver_grid_width
        return config.GRID_SIZE
    
    def get_grid_height(self):
        """Get the grid height for the current mode."""
        if self.in_screensaver_mode() and hasattr(self.game, 'screensaver_grid_height'):
            return self.game.screensaver_grid_height
        return config.GRID_SIZE

    def get_cell_size(self):
        """Get the appropriate cell size based on game state."""
        if self.in_screensaver_mode() and hasattr(self.game, 'screensaver_cell_size'):
            return self.game.screensaver_cell_size
        return config.SCREEN_SIZE / config.GRID_SIZE

    def spawn(self, segment_count: int = 2, avoid_snakes=True) -> None:
        """Spawn the snake with specified segment count."""
        grid_width = self.get_grid_width()
        grid_height = self.get_grid_height()
        
        # Reset invincibility state
        self.is_invincible = False
        
        # For screensaver mode, position might be already set by the game
        if not hasattr(self, 'position') or self.position is None:
            if avoid_snakes and self.is_ai:
                # AI snakes should always try to find a safe position
                self.position = self._find_safe_spawn_position(grid_width, grid_height)
            elif avoid_snakes and not self.is_ai:
                # Player snake: find position and always activate invincibility
                self.position = self._find_safe_spawn_position(grid_width, grid_height)
                self._activate_invincibility()
            else:
                # Use screensaver grid dimensions if in screensaver mode, otherwise use config grid size
                self.position = pygame.Vector2(random.randint(0, grid_width - 1), random.randint(0, grid_height - 1))
        elif avoid_snakes and self.is_ai:
            # Try to find a safe position when respawning due to collision
            self.position = self._find_safe_spawn_position(grid_width, grid_height)
        elif avoid_snakes and not self.is_ai:
            # Player respawn: find position and always activate invincibility
            self.position = self._find_safe_spawn_position(grid_width, grid_height)
            self._activate_invincibility()
        
        self.direction = random.choice([pygame.Vector2(1, 0), pygame.Vector2(-1, 0), pygame.Vector2(0, 1), pygame.Vector2(0, -1)])
        
        # Make sure the direction is not zero
        if self.direction.x == 0 and self.direction.y == 0:
            self.direction = pygame.Vector2(1, 0)
        
        self.body = []
        # Create initial body based on the direction and segment count
        self._create_initial_body(segment_count)
        self.previous_body = list(self.body)
        self.grow_pending = False
        self.move_progress = 0.0

        # Color scheme
        try:
            self.color_scheme_index = random.randint(0, len(config.SNAKE_COLOR_SCHEMES) - 1)
            self.color_head, self.color_tail = config.SNAKE_COLOR_SCHEMES[self.color_scheme_index]
        except (IndexError, ValueError):
            # Fallback to first color scheme if there's an issue
            self.color_scheme_index = 0
            if config.SNAKE_COLOR_SCHEMES:
                self.color_head, self.color_tail = config.SNAKE_COLOR_SCHEMES[0]
            else:
                # Ultimate fallback colors
                self.color_head, self.color_tail = (255, 140, 0), (255, 200, 100)

    def _find_safe_spawn_position(self, grid_width: int, grid_height: int) -> pygame.Vector2:
        """Find a safe position to spawn the snake, avoiding other snakes when possible."""
        max_attempts = 200  # Even more attempts for crowded scenarios
        min_distance = 5  # Larger minimum distance for better safety
        
        # First pass: try to find a position with good distance
        for attempt in range(max_attempts):
            # Try a random position
            pos = pygame.Vector2(random.randint(0, grid_width - 1), random.randint(0, grid_height - 1))
            
            # Check if position is safe (not occupied by any snake)
            is_safe = True
            min_dist_found = float('inf')
            
            if hasattr(self.game, 'snakes') and self.game.snakes:
                for snake in self.game.snakes:
                    if snake is not self and hasattr(snake, 'body') and snake.body:
                        # Check distance to all segments of this snake
                        for segment in snake.body:
                            dist = (pos - segment).length()
                            min_dist_found = min(min_dist_found, dist)
                            if dist < min_distance:
                                is_safe = False
                            break
                    if not is_safe:
                        break
            
            # If basic position is safe, check future body placement
            if is_safe:
                # Test all 4 possible directions to see which gives the safest body placement
                directions = [pygame.Vector2(1, 0), pygame.Vector2(-1, 0), 
                             pygame.Vector2(0, 1), pygame.Vector2(0, -1)]
                
                for test_direction in directions:
                    body_safe = True
                    # Check where our body segments would be placed (test 4 segments)
                    for i in range(1, 5):  # Skip head (i=0), check body positions
                        future_segment = pos + (test_direction * i * -1)
                        
                        # Make sure body segment is within bounds
                        if (future_segment.x < 0 or future_segment.x >= grid_width or 
                            future_segment.y < 0 or future_segment.y >= grid_height):
                            body_safe = False
                            break
                        
                        # Check distance to all other snake segments
                        if hasattr(self.game, 'snakes') and self.game.snakes:
                            for snake in self.game.snakes:
                                if snake is not self and hasattr(snake, 'body') and snake.body:
                                    for segment in snake.body:
                                        dist = (future_segment - segment).length()
                                        if dist < 2:  # Stricter check for body segments
                                            body_safe = False
                                            break
                                    if not body_safe:
                                        break
                        if not body_safe:
                            break
                    
                    if body_safe:
                        # Found a good direction, update snake direction and return position
                        self.direction = test_direction
                        return pos
            
            # Early exit if we found a decent position (even if not perfect)
            if attempt > 50 and min_dist_found > 2:
                return pos
        
        # Second pass: find the best available position (least conflicting)
        best_pos = None
        best_min_distance = 0
        best_direction = pygame.Vector2(1, 0)
        
        for _ in range(50):  # Final attempt to minimize conflicts
            pos = pygame.Vector2(random.randint(0, grid_width - 1), random.randint(0, grid_height - 1))
            min_dist_to_any_snake = float('inf')
            
            if hasattr(self.game, 'snakes') and self.game.snakes:
                for snake in self.game.snakes:
                    if snake is not self and hasattr(snake, 'body') and snake.body:
                        for segment in snake.body:
                            dist = (pos - segment).length()
                            min_dist_to_any_snake = min(min_dist_to_any_snake, dist)
            
            if min_dist_to_any_snake > best_min_distance:
                best_min_distance = min_dist_to_any_snake
                best_pos = pos
                # Also pick a safe direction
                directions = [pygame.Vector2(1, 0), pygame.Vector2(-1, 0), 
                             pygame.Vector2(0, 1), pygame.Vector2(0, -1)]
                best_direction = random.choice(directions)
        
        # Set direction for the best position found
        if best_pos:
            self.direction = best_direction
            return best_pos
        else:
            # Last resort: random position
            self.direction = random.choice([pygame.Vector2(1, 0), pygame.Vector2(-1, 0), 
                                          pygame.Vector2(0, 1), pygame.Vector2(0, -1)])
            return pygame.Vector2(random.randint(0, grid_width - 1), random.randint(0, grid_height - 1))

    def _find_safe_spawn_position_with_safety_check(self, grid_width: int, grid_height: int) -> Tuple[pygame.Vector2, bool]:
        """Find a safe spawn position and return whether it's actually safe."""
        max_attempts = 100
        min_safe_distance = 4
        
        for attempt in range(max_attempts):
            pos = pygame.Vector2(random.randint(0, grid_width - 1), random.randint(0, grid_height - 1))
            
            # Check if position is safe
            min_distance_found = float('inf')
            # Only check existing snakes if the list exists and is initialized
            if hasattr(self.game, 'snakes') and self.game.snakes:
                for snake in self.game.snakes:
                    if snake is not self and hasattr(snake, 'body') and snake.body:
                        for segment in snake.body:
                            dist = (pos - segment).length()
                            min_distance_found = min(min_distance_found, dist)
            
            # If we found a truly safe position
            if min_distance_found >= min_safe_distance:
                return pos, True
            
            # If we found a moderately safe position (after many attempts)
            if attempt > 50 and min_distance_found >= 2:
                return pos, True
        
        # No safe position found - return best available position and mark as unsafe
        best_pos = pygame.Vector2(random.randint(0, grid_width - 1), random.randint(0, grid_height - 1))
        return best_pos, False

    def _activate_invincibility(self):
        """Activate invincibility mode for player spawn."""
        if not self.is_ai:  # Only for player snake
            self.is_invincible = True
            self.invincibility_start_time = pygame.time.get_ticks()

    def update_invincibility(self):
        """Update invincibility state."""
        if self.is_invincible:
            current_time = pygame.time.get_ticks()
            elapsed = current_time - self.invincibility_start_time
            
            if elapsed >= self.invincibility_duration:
                self.is_invincible = False

    def is_invincible_and_blinking(self) -> bool:
        """Check if snake should be rendered with blinking effect."""
        if not self.is_invincible:
            return False
        
        current_time = pygame.time.get_ticks()
        elapsed = current_time - self.invincibility_start_time
        
        # Blink faster as invincibility is about to end
        if elapsed > self.invincibility_duration * 0.7:  # Last 30% of time
            blink_interval = self.invincibility_blink_speed // 2  # Faster blinking
        else:
            blink_interval = self.invincibility_blink_speed
        
        # Return True to show snake, False to hide it (blinking effect)
        return (current_time // blink_interval) % 2 == 0

    def _create_initial_body(self, segment_count: int) -> None:
        """Create the initial body for the snake."""
        for i in range(segment_count):
            offset = self.direction * i * -1  # Start segments behind the head
            pos = self.position + offset
            self.body.append(pos)

    def update(self):
        """Update snake state."""
        if self.is_ai:
            self.make_ai_decision()

        self.previous_body = list(self.body)
        # NEW LOGIC: body[0] = head, body[-1] = tail
        # Move the snake: add new head position and remove old tail position (unless growing)
        next_pos = self.position + self.direction
        
        # Add new head to the front of the body
        self.body.insert(0, next_pos)  # New head at front
        self.position = next_pos  # Update head position
        
        # Remove tail from the end unless growing
        if not self.grow_pending:
            self.body.pop()  # Remove old tail (from end)
        else:
            self.grow_pending = False  # Reset grow flag, snake grows (tail stays in place)
        
        self.move_progress = 0.0

    def update_smooth_movement(self, dt):
        """Update smooth movement interpolation."""
        move_interval = config.get_enemy_move_interval() if self.is_ai else config.get_player_move_interval()
        self.move_progress += dt / move_interval
        self.move_progress = min(self.move_progress, 1.0)

    # Note: Rendering methods (draw, draw_circular_segment, etc.) are in SnakeRenderingMixin
    # Note: Death animation methods (start_death_animation, update_death_animation, etc.) are in SnakeDeathAnimationMixin
    # Note: AI methods (make_ai_decision, calculate_direction_score, etc.) are in SnakeAIMixin

    def grow(self):
        """Mark the snake to grow on next update."""
        self.grow_pending = True

    def set_direction(self, direction):
        """Set the snake's direction, preventing 180-degree turns."""
        # Prevent reversing direction (180-degree turn)
        # If new direction is exactly opposite to current direction, ignore it
        if direction.x == -self.direction.x and direction.y == -self.direction.y:
            return
        
        # Additional check: if snake has more than 1 segment, ensure new direction
        # doesn't immediately collide with the segment behind the head
        if len(self.body) > 1:
            next_pos = self.position + direction
            if next_pos == self.body[1]:  # Check against segment immediately behind head
                return
        
        self.direction = direction

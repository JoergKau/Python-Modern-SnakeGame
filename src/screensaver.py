import pygame
import random
from typing import TYPE_CHECKING
from src import config
from src.snake import Snake
from src.food import Food

if TYPE_CHECKING:
    from src.game import Game, GameState

class ScreensaverManager:
    """Manages screensaver mode functionality for the Snake game."""
    
    def __init__(self, game: 'Game') -> None:
        """Initialize the screensaver manager.
        
        Args:
            game: Reference to the main Game instance
        """
        self.game = game
        self.screensaver_grid_width = 0
        self.screensaver_grid_height = 0
        self.screensaver_cell_size = 0
        
        # Saved game state variables
        self.original_game_state = None
        self.original_snakes = None
        self.original_food = None
        self.original_score = 0
        self.original_level = 1
        self.original_apples_eaten = 0
    
    def start(self) -> None:
        """Start the screensaver mode, saving the current game state."""
        # Switch to fullscreen mode before setting up grid to ensure correct dimensions
        if not self.game.check_fullscreen():
            self.game.set_fullscreen()
            # Small delay to ensure the screen has been updated with new dimensions
            pygame.display.flip()
            pygame.time.delay(100)  # Brief delay to allow system to settle
        
        self._save_game_state()
        self._setup_grid()
        self.game.background_renderer.grid_size = max(self.screensaver_grid_width, self.screensaver_grid_height)
        
        # Set game state to screensaver BEFORE creating snakes
        # This is critical so that snakes use the correct grid size
        from src.game import GameState
        self.game.game_state = GameState.SCREENSAVER
        
        self._create_snakes()
        self.game.ai_last_move_time = pygame.time.get_ticks()
    
    def stop(self) -> None:
        """Stop the screensaver mode and restore previous game state."""
        self._exit_fullscreen_if_needed()
        self.game.background_renderer.grid_size = config.GRID_SIZE
        self._restore_game_state()
    
    def run(self, dt: float) -> None:
        """Handle the screensaver state.
        
        Args:
            dt: Delta time in seconds
        """
        self._process_events()
        self._update_snakes(dt)
        self._draw()
    
    def _save_game_state(self) -> None:
        """Save the current game state before starting screensaver."""
        if hasattr(self.game, 'snakes') and len(self.game.snakes) > 0:
            # Save the actual game state
            self.original_game_state = self.game.game_state
            self.original_snakes = self.game.snakes
            self.original_food = self.game.food
            self.original_score = self.game.score
            self.original_level = self.game.level
            self.original_apples_eaten = self.game.apples_eaten
        else:
            # If game hasn't been started, set to None to indicate no state to restore
            self.original_game_state = None
            self.original_snakes = None
            self.original_food = None
            self.original_score = 0
            self.original_level = 1
            self.original_apples_eaten = 0
    
    def _setup_grid(self) -> None:
        """Set up the grid size for screensaver mode based on screen dimensions."""
        # Always get the current screen dimensions (fullscreen or windowed)
        screen_width, screen_height = self.game.screen.get_size()
        
        # Calculate optimal grid size for fullscreen (maintain square cells)
        cell_pixel_size = config.SCREEN_SIZE // config.GRID_SIZE
        
        # Use separate width and height to fill the entire screen
        self.screensaver_grid_width = screen_width // cell_pixel_size
        self.screensaver_grid_height = screen_height // cell_pixel_size
        
        # Cell size is the same for both dimensions (square cells)
        self.screensaver_cell_size = cell_pixel_size
        
        # Store grid dimensions on game object so Snake methods can access them
        self.game.screensaver_grid_width = self.screensaver_grid_width
        self.game.screensaver_grid_height = self.screensaver_grid_height
        self.game.screensaver_cell_size = self.screensaver_cell_size
    
    def _create_snakes(self) -> None:
        """Create decorative snakes for the screensaver mode."""
        self.game.snakes = []
        
        # Create food for screensaver snakes to reference in their AI (but don't draw it)
        self.game.food = Food(self.game, self.game.snakes)
        
        # Create decorative snakes for screensaver
        for i in range(config.GameConfig.SCREENSAVER_SNAKE_COUNT):
            ss_snake = self._create_and_position_snake(i)
            self.game.snakes.append(ss_snake)
    
    def _create_and_position_snake(self, index: int) -> Snake:
        """Create and position a single screensaver snake.
        
        Args:
            index: Snake index (for tracking purposes)
            
        Returns:
            Configured Snake instance
        """
        # Create snake with random length between 3-6 segments
        # The Snake class will handle positioning and body creation automatically
        ss_snake = Snake(self.game, is_ai=True, min_segments=3, max_segments=6)
        
        return ss_snake
    
    def _exit_fullscreen_if_needed(self) -> None:
        """Switch back to windowed mode if currently in fullscreen."""
        if self.game.check_fullscreen():
            self.game.set_windowed()
    
    def _restore_game_state(self) -> None:
        """Restore the game state from before screensaver."""
        if self.original_game_state is not None:
            self.game.snakes = self.original_snakes
            self.game.food = self.original_food
            self.game.score = self.original_score
            self.game.level = self.original_level
            self.game.apples_eaten = self.original_apples_eaten
            self.game.game_state = self.original_game_state
        else:
            # If no original state to restore, go back to splash
            from src.game import GameState
            self.game.game_state = GameState.SPLASH
    
    def _process_events(self) -> None:
        """Process events during screensaver state."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s or event.key == pygame.K_SPACE:
                    self.stop()
    
    def _update_snakes(self, dt: float) -> None:
        """Update screensaver snake movements and positions.
        
        Args:
            dt: Delta time in seconds
        """
        # Update screensaver snakes using the same movement timing as in playing mode
        for snake in self.game.snakes:
            snake.update_smooth_movement(dt)
        
        # Update snake positions using consistent timing
        current_time = pygame.time.get_ticks()
        # Use player speed for more lively screensaver animations
        screensaver_move_interval = config.get_player_move_interval(config.GRID_SIZE) * 1000
        
        if current_time - self.game.ai_last_move_time > screensaver_move_interval:
            for snake in self.game.snakes:
                self._update_single_snake(snake)
            self.game.ai_last_move_time = current_time
    
    def _update_single_snake(self, snake: Snake) -> None:
        """Update a single screensaver snake.
        
        Args:
            snake: Snake instance to update
        """
        # Call the same AI decision-making as in gameplay mode
        snake.make_ai_decision()
        
        # Check if the next position would go out of bounds
        next_pos = snake.position + snake.direction
        if (next_pos.x < 0 or next_pos.x >= self.screensaver_grid_width or
            next_pos.y < 0 or next_pos.y >= self.screensaver_grid_height):
            # If out of bounds, find a safe direction
            possible_dirs = [
                pygame.Vector2(1, 0), 
                pygame.Vector2(-1, 0), 
                pygame.Vector2(0, 1), 
                pygame.Vector2(0, -1)
            ]
            safe_dirs = []
            
            for direction in possible_dirs:
                if direction != snake.direction * -1:  # Not opposite direction
                    test_pos = snake.position + direction
                    if (0 <= test_pos.x < self.screensaver_grid_width and 
                        0 <= test_pos.y < self.screensaver_grid_height):
                        safe_dirs.append(direction)
            
            if safe_dirs:
                snake.direction = random.choice(safe_dirs)
            else:
                # If no safe directions, just reverse (last resort)
                snake.direction = snake.direction * -1
        
        # Call the normal update method
        snake.update()
    
    def _draw(self) -> None:
        """Draw the screensaver screen."""
        self.game.background_renderer.draw_animated_grid(0, 0, 0, self.game.level)
        self._draw_snakes()
        pygame.display.flip()
    
    def _draw_snakes(self) -> None:
        """Draw screensaver snakes using smooth interpolation."""
        cell_size = self.screensaver_cell_size
        
        for snake in self.game.snakes:
            for i, segment in enumerate(snake.body):
                # Interpolate position for smooth movement
                if i < len(snake.previous_body):
                    prev_segment = snake.previous_body[i]
                    draw_pos = prev_segment.lerp(segment, snake.move_progress)
                else:
                    draw_pos = segment

                x = draw_pos.x * cell_size + cell_size / 2
                y = draw_pos.y * cell_size + cell_size / 2
                radius = cell_size / 2 * 0.95

                color = snake.color_head if i == 0 else snake.color_tail

                # Draw main body segment
                pygame.draw.circle(self.game.screen, color, (int(x), int(y)), int(radius))

                # Draw highlight for 3D effect
                highlight_color = (
                    min(255, color[0] + 50), 
                    min(255, color[1] + 50), 
                    min(255, color[2] + 50)
                )
                highlight_radius = max(1, int(radius * 0.4))
                highlight_offset = int(radius * 0.3)
                pygame.draw.circle(
                    self.game.screen, 
                    highlight_color, 
                    (int(x - highlight_offset), int(y - highlight_offset)), 
                    highlight_radius
                )

                # Draw eyes for head
                if i == 0:
                    self._draw_snake_eyes(snake, x, y, radius)
    
    def _draw_snake_eyes(self, snake: Snake, x: float, y: float, radius: float) -> None:
        """Draw eyes for the snake head.
        
        Args:
            snake: Snake instance
            x: X coordinate of head center
            y: Y coordinate of head center
            radius: Radius of the head
        """
        eye_radius = max(1, int(radius * 0.25))
        eye_offset = int(radius * 0.5)
        
        # Calculate eye positions based on direction
        if snake.direction.x == 1:  # Right
            left_eye_x = int(x + eye_offset * 0.5)
            left_eye_y = int(y - eye_offset * 0.6)
            right_eye_x = int(x + eye_offset * 0.5)
            right_eye_y = int(y + eye_offset * 0.6)
        elif snake.direction.x == -1:  # Left
            left_eye_x = int(x - eye_offset * 0.5)
            left_eye_y = int(y - eye_offset * 0.6)
            right_eye_x = int(x - eye_offset * 0.5)
            right_eye_y = int(y + eye_offset * 0.6)
        elif snake.direction.y == 1:  # Down
            left_eye_x = int(x - eye_offset * 0.6)
            left_eye_y = int(y + eye_offset * 0.5)
            right_eye_x = int(x + eye_offset * 0.6)
            right_eye_y = int(y + eye_offset * 0.5)
        else:  # Up
            left_eye_x = int(x - eye_offset * 0.6)
            left_eye_y = int(y - eye_offset * 0.5)
            right_eye_x = int(x + eye_offset * 0.6)
            right_eye_y = int(y - eye_offset * 0.5)
        
        # Draw eyes (pupils)
        pygame.draw.circle(self.game.screen, (0, 0, 0), (left_eye_x, left_eye_y), eye_radius)
        pygame.draw.circle(self.game.screen, (0, 0, 0), (right_eye_x, right_eye_y), eye_radius)

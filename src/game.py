import pygame
import os
import random
from typing import Optional, List, Tuple
from enum import Enum
from src import config
from src.utils import get_font_path
from src.snake import Snake
from src.food import Food
from src.sound_manager import SoundManager
from src.highscore_manager import HighScoreManager
from src.particle import ParticleManager
from src.background import BackgroundRenderer
from src.screensaver import ScreensaverManager
from src.renderer import GameRenderer

class GameState(Enum):
    SPLASH = 1
    PLAYING = 2
    PAUSED = 3
    LEVEL_COMPLETE = 4
    DEATH_ANIMATION = 5
    GAME_OVER = 6
    SCREENSAVER = 7

class Game:
    def __init__(self) -> None:
        self._initialize_pygame()
        self._setup_game_state()
        self._setup_managers()
        self._setup_fonts()
        self._initialize_screensaver_vars()

    def _initialize_pygame(self) -> None:
        """Initialize pygame and set up the display."""
        try:
            pygame.mixer.pre_init(44100, -16, 2, 512)
            pygame.init()
            self.screen = pygame.display.set_mode((config.SCREEN_SIZE, config.SCREEN_SIZE))
            pygame.display.set_caption("PySnake")
            self.clock = pygame.time.Clock()
        except pygame.error as e:
            print(f"Pygame initialization error: {e}")
            raise

    def _setup_game_state(self) -> None:
        """Set up initial game state variables."""
        self.running = True
        self.game_state = GameState.SPLASH
        self.god_mode = False  # God Mode functionality
        self.player_last_move_time = 0
        self.ai_last_move_time = 0
        # Initialize game state variables that might be accessed even before starting a game
        self.score = 0
        self.level = 1
        self.apples_eaten = 0
        
        # Initialize decorative snakes for splash/game over/level complete screens
        self._init_decorative_snakes()

    def _setup_managers(self) -> None:
        """Initialize game managers."""
        self.sound_manager = SoundManager()
        self.highscore_manager = HighScoreManager()
        self.particle_manager = ParticleManager()
        self.background_renderer = BackgroundRenderer(self.screen)
        self.screensaver_manager = ScreensaverManager(self)
        self.renderer = GameRenderer(self)
        self.sound_manager.play_music("start")

    def _setup_fonts(self) -> None:
        """Set up fonts for the game."""
        # Use Heroking-Regular.ttf for general UI text (like in the original Java project)
        try:
            heroking_path = get_font_path("Heroking-Regular.ttf")
            self.font = pygame.font.Font(heroking_path, config.TEXT_SIZE_NORMAL)
            self.large_font = pygame.font.Font(heroking_path, config.TEXT_SIZE_TITLE)
        except FileNotFoundError:
            print("Warning: Heroking-Regular.ttf font not found, using default font")
            self.font = pygame.font.Font(None, config.TEXT_SIZE_NORMAL)
            self.large_font = pygame.font.Font(None, config.TEXT_SIZE_TITLE)
        
        # Use NewryDemoRegular.ttf for title text (like 'SNAKES' in the original Java project)
        try:
            newry_path = get_font_path("NewryDemoRegular.ttf")
            self.title_font = pygame.font.Font(newry_path, config.TEXT_SIZE_TITLE)
        except FileNotFoundError:
            print("Warning: NewryDemoRegular.ttf font not found, using default font")
            self.title_font = pygame.font.Font(None, config.TEXT_SIZE_TITLE)

    def _initialize_screensaver_vars(self) -> None:
        """Initialize screensaver mode variables."""
        # Track previous game state for music management
        self.previous_game_state = self.game_state
    
    def _init_decorative_snakes(self) -> None:
        """Initialize decorative snakes for menu screens."""
        self.decorative_snakes = []
        self.decorative_last_move_time = 0
        for _ in range(config.SPLASH_SNAKE_COUNT):
            snake = Snake(self, is_ai=True, min_segments=3, max_segments=6)
            # Make them move at enemy speed
            self.decorative_snakes.append(snake)
    
    def _update_decorative_snakes(self, dt: float) -> None:
        """Update decorative snakes for menu screens."""
        current_time = pygame.time.get_ticks()
        
        # Update smooth movement for all decorative snakes
        for snake in self.decorative_snakes:
            snake.update_smooth_movement(dt)
        
        # Update snake positions based on enemy interval
        if current_time - self.decorative_last_move_time > config.get_enemy_move_interval() * 1000:
            for snake in self.decorative_snakes:
                # Check if next move would hit wall or self
                next_pos = snake.position + snake.direction
                would_hit_wall = not (0 <= next_pos.x < config.GRID_SIZE and 0 <= next_pos.y < config.GRID_SIZE)
                would_hit_self = next_pos in snake.body[1:]
                
                # If would collide, pick a random safe direction
                if would_hit_wall or would_hit_self:
                    # Get all possible directions
                    possible_dirs = [
                        pygame.Vector2(1, 0),   # right
                        pygame.Vector2(-1, 0),  # left
                        pygame.Vector2(0, 1),   # down
                        pygame.Vector2(0, -1)   # up
                    ]
                    
                    # Filter to safe directions (not opposite, not wall, not self)
                    safe_dirs = []
                    for test_dir in possible_dirs:
                        # Skip opposite direction
                        if test_dir == snake.direction * -1:
                            continue
                        test_pos = snake.position + test_dir
                        # Check if safe
                        if (0 <= test_pos.x < config.GRID_SIZE and 
                            0 <= test_pos.y < config.GRID_SIZE and 
                            test_pos not in snake.body[1:]):
                            safe_dirs.append(test_dir)
                    
                    # Pick random safe direction if available
                    if safe_dirs:
                        snake.direction = random.choice(safe_dirs)
                
                # Update snake position
                snake.update()
            
            self.decorative_last_move_time = current_time

    def run(self) -> None:
        while self.running:
            dt = self.clock.tick(config.FRAME_RATE) / 1000.0
            self.background_renderer.update(dt)
            
            # Store current state to detect changes for music management
            previous_state = self.game_state
            
            if self.game_state == GameState.SPLASH:
                self.run_splash(dt)
            elif self.game_state == GameState.PLAYING:
                self.run_playing(dt)
            elif self.game_state == GameState.PAUSED:
                self.run_paused(dt)
            elif self.game_state == GameState.LEVEL_COMPLETE:
                self.run_level_complete(dt)
            elif self.game_state == GameState.DEATH_ANIMATION:
                self.run_death_animation(dt)
            elif self.game_state == GameState.GAME_OVER:
                # Play game over music when entering GAME_OVER state
                if previous_state != GameState.GAME_OVER:
                    self.sound_manager.play_music("gameover")
                self.run_game_over(dt)
            elif self.game_state == GameState.SCREENSAVER:
                self.run_screensaver(dt)
        
        self._cleanup_before_exit()
        pygame.quit()

    def _cleanup_before_exit(self) -> None:
        """Clean up before exiting the game."""
        # If we exit the game loop while in fullscreen, ensure we return to windowed mode
        if self.check_fullscreen():
            self.set_windowed()

    def check_fullscreen(self):
        """Check if the current display is in fullscreen mode"""
        flags = self.screen.get_flags()
        return bool(flags & pygame.FULLSCREEN)

    def set_fullscreen(self):
        """Switch to fullscreen mode"""
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

    def set_windowed(self):
        """Switch to windowed mode"""
        self.screen = pygame.display.set_mode((config.SCREEN_SIZE, config.SCREEN_SIZE))

    def get_grid_size(self):
        """Get the grid size based on game state."""
        if self.game_state == GameState.SCREENSAVER:
            return max(self.screensaver_manager.screensaver_grid_width, 
                      self.screensaver_manager.screensaver_grid_height)
        return config.GRID_SIZE

    def start_game(self) -> None:
        """Initialize a new game session."""
        self._initialize_game_entities()
        self._reset_game_state()
        self.start_level()

    def continue_game(self) -> None:
        """Continue the game from the current level after game over."""
        # Don't reset score or level - keep them as is
        # Just respawn the player and restart the level
        if self.player_snake:
            self.player_snake.spawn(segment_count=2, avoid_snakes=True)
        
        # Clear player trail particles
        self.particle_manager.clear_player_particles()
        
        # Restart the current level
        self.start_level()

    def _initialize_game_entities(self) -> None:
        """Initialize game entities like snakes and food."""
        self.snakes = [Snake(self)]
        self.player_snake = self.snakes[0]
        self.food = Food(self, self.snakes)

    def _reset_game_state(self) -> None:
        """Reset game state variables."""
        self.score = 0
        self.level = 1
        self.apples_eaten = 0
        self.player_last_move_time = 0
        self.ai_last_move_time = 0
        # Clear background particles when starting a new game
        self.particle_manager.clear_background_particles()
        # Clear player trail particles
        self.particle_manager.clear_player_particles()

    def start_level(self):
        self.game_state = GameState.PLAYING
        self.sound_manager.stop_music()
        self.sound_manager.play_music("game")
        
        # Clear any existing enemy snakes, keeping only the player snake
        self.snakes = [self.player_snake]
        
        # Reset player snake to 2 segments at the start of each level (player spawns first)
        if self.player_snake:
            self.player_snake.spawn(segment_count=2, avoid_snakes=True)  # Player spawns with invincibility
        
        # Add AI snakes based on level with increasing segments (like original Java game)
        # Enemy snakes will automatically avoid existing snakes (including the player) during spawn
        for i in range(self.level - 1):
            segments = min(config.get_enemy_initial_segments() + i, config.get_enemy_max_segments())
            enemy_snake = Snake(self, is_ai=True, min_segments=segments, max_segments=segments)
            self.snakes.append(enemy_snake)

    def start_screensaver(self) -> None:
        """Start the screensaver mode, saving the current game state."""
        self.screensaver_manager.start()

    def stop_screensaver(self) -> None:
        """Stop the screensaver mode and restore previous game state."""
        self.screensaver_manager.stop()

    def run_splash(self, dt):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.start_game()
                elif event.key == pygame.K_s:
                    self.start_screensaver()

        # Update decorative snakes
        self._update_decorative_snakes(dt)
        
        self.particle_manager.update(dt)
        # Spawn title particles periodically
        if int(pygame.time.get_ticks() / 100) % 10 == 0:  # Every 1000ms / 10 frames
            self.particle_manager.spawn_title_particles(config.TITLE_PARTICLES_PER_FRAME)
        
        self.renderer.draw_splash_screen()

    def run_playing(self, dt: float) -> None:
        """Main game loop when in PLAYING state."""
        self.events_playing()
        
        # If state changed during events (e.g., starting screensaver), skip update and draw
        if self.game_state != GameState.PLAYING:
            return
            
        self.update_playing(dt)
        self.renderer.draw_playing()

    def events_playing(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.player_snake.set_direction(pygame.Vector2(0, -1))
                elif event.key == pygame.K_DOWN:
                    self.player_snake.set_direction(pygame.Vector2(0, 1))
                elif event.key == pygame.K_LEFT:
                    self.player_snake.set_direction(pygame.Vector2(-1, 0))
                elif event.key == pygame.K_RIGHT:
                    self.player_snake.set_direction(pygame.Vector2(1, 0))
                elif event.key == pygame.K_p or event.key == pygame.K_PAUSE:
                    self.game_state = GameState.PAUSED
                elif event.key == pygame.K_g:  # God mode toggle
                    self.god_mode = not self.god_mode
                elif event.key == pygame.K_s:
                    self.start_screensaver()

    def update_playing(self, dt: float) -> None:
        """Update game logic when in PLAYING state."""
        self.food.update(dt)
        self._update_snake_movements(dt)
        self._handle_snake_updates()
        
        # Update invincibility state for player snake
        self.player_snake.update_invincibility()
        
        self._handle_player_collisions()
        self._handle_ai_snake_collisions()
        self._handle_food_collisions()
        
        # Update and spawn player trail particles
        self.particle_manager.update(dt)
        current_time = pygame.time.get_ticks() / 1000.0  # Convert to seconds
        self.particle_manager.spawn_player_particles(self.player_snake, current_time)

    def _update_snake_movements(self, dt: float) -> None:
        """Update smooth movement for all snakes."""
        for snake in self.snakes:
            snake.update_smooth_movement(dt)

    def _handle_snake_updates(self) -> None:
        """Handle timing-based updates for snake positions."""
        current_time = pygame.time.get_ticks()
        
        # Update player snake based on player interval
        if current_time - self.player_last_move_time > config.get_player_move_interval() * 1000:
            # In God Mode or Invincible Mode, prevent player snake from moving beyond boundaries
            if self.player_snake and (self.god_mode or self.player_snake.is_invincible):
                # Calculate next position
                next_pos = self.player_snake.position + self.player_snake.direction
                # Only update if the move keeps the snake within bounds
                if 0 <= next_pos.x < config.GRID_SIZE and 0 <= next_pos.y < config.GRID_SIZE:
                    self.player_snake.update()
                # If out of bounds, don't update (snake stays in place)
            else:
                # Normal mode: update normally
                self.player_snake.update()
            self.player_last_move_time = current_time
        
        # Update AI snakes based on enemy interval
        if current_time - self.ai_last_move_time > config.get_enemy_move_interval() * 1000:
            for snake in self.snakes:
                if snake != self.player_snake and snake.is_ai:  # Only update AI snakes here
                    snake.update()
            self.ai_last_move_time = current_time

    def _update_snake_position(self, snake: Snake) -> None:
        """Update the position of a snake based on game mode."""
        # This method is now deprecated as we handle updates directly in _handle_snake_updates
        pass

    def _handle_player_collisions(self) -> None:
        """Handle collision detection and response for the player snake."""
        if self.god_mode:
            return  # Skip collision checks in god mode
            
        # Skip ALL collision checks if player is invincible (like god mode)
        if self.player_snake.is_invincible:
            return
            
        if not 0 <= self.player_snake.position.x < config.GRID_SIZE or not 0 <= self.player_snake.position.y < config.GRID_SIZE:
            if self.game_state != GameState.DEATH_ANIMATION:  # Only if not already in death state
                self._trigger_player_death()
        elif self.player_snake.position in self.player_snake.body[1:]:
            if self.game_state != GameState.DEATH_ANIMATION:  # Only if not already in death state
                self._trigger_player_death()
        elif any(self.player_snake.position in snake.body for snake in self.snakes if self.player_snake != snake):
            if self.game_state != GameState.DEATH_ANIMATION:  # Only if not already in death state
                self._trigger_player_death()

    def _trigger_player_death(self) -> None:
        """Trigger the player snake's death animation."""
        self.game_state = GameState.DEATH_ANIMATION
        self.sound_manager.stop_music()
        self.sound_manager.play("lost")
        # Clear player trail particles when player dies
        self.particle_manager.clear_player_particles()

    def _handle_ai_snake_collisions(self) -> None:
        """Handle collision detection and response for AI snakes."""
        # Don't handle collisions in screensaver mode
        if self.game_state == GameState.SCREENSAVER:
            return
            
        for snake in self.snakes:
            if snake.is_ai:
                self._handle_single_ai_collision(snake)

    def _handle_single_ai_collision(self, snake: Snake) -> None:
        """Handle collision checks for a single AI snake."""
        # Wall collision - AI snakes respawn when hitting walls
        if not 0 <= snake.position.x < config.GRID_SIZE or not 0 <= snake.position.y < config.GRID_SIZE:
            snake.spawn(segment_count=snake.initial_segment_count, avoid_snakes=True)
            return
        
        # Self collision - AI snakes respawn when hitting themselves
        if snake.position in snake.body[1:]:
            snake.spawn(segment_count=snake.initial_segment_count, avoid_snakes=True)
            return
        
        # Enemy snakes can pass through each other, only check collision with player (if not in god mode)
        # In god mode or when player is invincible, enemy snakes pass through the player too
        if not self.god_mode and not self.player_snake.is_invincible:
            # Only check collision with player when player is NOT invincible
            # Enemy snakes still pass through each other, they only avoid the vulnerable player
            pass  # No collision check needed - enemies pass through everything except walls and themselves

    def _handle_food_collisions(self) -> None:
        """Handle food collision detection and response."""
        for snake in self.snakes:
            if snake.position == self.food.position:
                self._handle_food_eaten(snake)

    def _handle_food_eaten(self, snake: Snake) -> None:
        """Handle logic when a snake eats food."""
        food_position = self.food.position
        snake.grow()
        self.food.position = self.food.spawn()
        self.sound_manager.play("eat")
        
        if not snake.is_ai:
            self._update_player_score()
        
        self._create_food_particles(food_position)

    def _update_player_score(self) -> None:
        """Update the player's score and check for level completion."""
        points = config.get_points_per_apple(self.level)
        self.score += points
        self.apples_eaten += 1
        if self.apples_eaten >= config.APPLES_PER_LEVEL:
            self.game_state = GameState.LEVEL_COMPLETE

    def _create_food_particles(self, position: pygame.Vector2) -> None:
        """Create particles when food is eaten."""
        for _ in range(config.ParticleConfig.FOOD_PARTICLE_COUNT):
            cell_size = self.player_snake.get_cell_size()
            self.particle_manager.add_particle(
                position.x * cell_size + cell_size / 2,
                position.y * cell_size + cell_size / 2,
                config.GREEN_YELLOW_PARTICLES,
                config.PLAYER_PARTICLE_MIN_LIFE, config.PLAYER_PARTICLE_MAX_LIFE,
                config.PLAYER_PARTICLE_MIN_SPEED, config.PLAYER_PARTICLE_MAX_SPEED,
                config.PLAYER_PARTICLE_MIN_SIZE, config.PLAYER_PARTICLE_MAX_SIZE
            )

    def run_paused(self, dt):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p or event.key == pygame.K_PAUSE or event.key == pygame.K_SPACE:
                    self.game_state = GameState.PLAYING
                elif event.key == pygame.K_s:
                    self.start_screensaver()

        self.renderer.draw_game_elements()
        self.renderer.draw_pause_overlay()
        pygame.display.flip()

    def run_level_complete(self, dt: float) -> None:
        """Handle the level complete game state."""
        self.sound_manager.stop_music()
        self.sound_manager.play("win")

        self._process_level_complete_events()
        
        # Update decorative snakes
        self._update_decorative_snakes(dt)
        
        # Update particles and spawn title particles for level complete screen
        self.particle_manager.update(dt)
        if int(pygame.time.get_ticks() / 100) % 10 == 0:  # Every 1000ms / 10 frames
            self.particle_manager.spawn_title_particles(config.TITLE_PARTICLES_PER_FRAME)

        self.renderer.draw_level_complete_screen()

    def _process_level_complete_events(self) -> None:
        """Process events during level complete state."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.level += 1
                    self.apples_eaten = 0
                    # Clear background particles when starting the next level
                    self.particle_manager.clear_background_particles()
                    self.start_level()
                elif event.key == pygame.K_s:
                    self.start_screensaver()

    def run_death_animation(self, dt: float) -> None:
        """Handle the death animation state."""
        self._initialize_death_animation()
        self._update_death_animation_state(dt)
        self.renderer.draw_death_animation()
        self._check_death_animation_completion(dt)

    def _initialize_death_animation(self) -> None:
        """Initialize death animation if not already started."""
        if not hasattr(self, 'death_start_time'):
            self.death_start_time = pygame.time.get_ticks()
            # Initialize death animation for the player snake
            if hasattr(self, 'player_snake'):
                self.player_snake.start_death_animation()  # Use the proper death animation
                self._create_death_particles()

    def _create_death_particles(self) -> None:
        """Create particles for the death animation."""
        cell_size = self.player_snake.get_cell_size()
        for segment in self.player_snake.body:
            for _ in range(3):  # Multiple particles per segment
                self.particle_manager.add_particle(
                    segment.x * cell_size + cell_size / 2,
                    segment.y * cell_size + cell_size / 2,
                    config.RED_ORANGE_PARTICLES,
                    config.PLAYER_PARTICLE_MIN_LIFE, config.PLAYER_PARTICLE_MAX_LIFE,
                    config.PLAYER_PARTICLE_MIN_SPEED, config.PLAYER_PARTICLE_MAX_SPEED,
                    config.PLAYER_PARTICLE_MIN_SIZE, config.PLAYER_PARTICLE_MAX_SIZE
                )

    def _update_death_animation_state(self, dt: float) -> None:
        """Update the state of the death animation."""
        # Update the death animation
        if hasattr(self, 'player_snake'):
            self.player_snake.update_death_animation(dt)

    def _check_death_animation_completion(self, dt: float) -> None:
        """Check if the death animation is complete and handle transition."""
        current_time = pygame.time.get_ticks()
        elapsed_time = (current_time - self.death_start_time) / 1000.0  # Convert to seconds
        
        # Check if death animation is complete
        # Wait slightly longer than the death animation duration to ensure all effects finish
        if elapsed_time >= config.AnimationConfig.DEATH_ANIMATION_DURATION + config.AnimationConfig.DEATH_ANIMATION_DELAY:  # Wait 0.2 seconds longer
            # Animation complete, transition to game over
            self.game_state = GameState.GAME_OVER
            # Play the game over music when transitioning
            self.sound_manager.play_music("gameover")
            delattr(self, 'death_start_time')  # Clean up the death timer
            if hasattr(self, 'player_snake'):
                self.player_snake.is_dying = False  # Reset dying state
        else:
            # Continue animation
            pygame.display.flip()

    def run_game_over(self, dt: float) -> None:
        """Handle the game over state."""
        # Only add score once when entering game over state
        if not hasattr(self, '_score_added'):
            self.highscore_manager.add_score(self.score)
            self._score_added = True
        
        self._process_game_over_events()
        
        # Update decorative snakes
        self._update_decorative_snakes(dt)
        
        self.particle_manager.update(dt)
        # Spawn game over particles periodically
        if int(pygame.time.get_ticks() / 100) % 10 == 0:  # Every 1000ms / 10 frames
            self.particle_manager.spawn_game_over_particles(config.GAME_OVER_PARTICLES_PER_FRAME)
        
        self.renderer.draw_game_over_screen()

    def _process_game_over_events(self) -> None:
        """Process events during game over state."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # Press SPACE to continue from current level
                    if hasattr(self, '_score_added'):
                        delattr(self, '_score_added')  # Reset flag for next game over
                    self.continue_game()
                    self.sound_manager.play_music("game")
                elif event.key == pygame.K_r:
                    # Press R to restart the game from level 1
                    if hasattr(self, '_score_added'):
                        delattr(self, '_score_added')  # Reset flag for next game over
                    self.start_game()
                    self.sound_manager.play_music("game")
                elif event.key == pygame.K_ESCAPE:
                    # Press ESC to return to main menu (original functionality)
                    if hasattr(self, '_score_added'):
                        delattr(self, '_score_added')  # Reset flag for next game over
                    self.game_state = GameState.SPLASH
                    self.particle_manager.clear_background_particles()  # Clear particles when changing state
                    self.sound_manager.play_music("start")
                elif event.key == pygame.K_s:
                    self.start_screensaver()

    def run_screensaver(self, dt: float) -> None:
        """Handle the screensaver state."""
        self.screensaver_manager.run(dt)

    def draw_hud(self):
        """Draw the heads-up display with score, level, and god mode indicator."""
        score_text = self.font.render(f"Score: {self.score}", True, config.WHITE_TEXT)
        self.screen.blit(score_text, (10, 10))

        level_text = self.font.render(f"Level: {self.level}", True, config.WHITE_TEXT)
        self.screen.blit(level_text, (10, 40))
        
        # Display God Mode indicator if active
        if self.god_mode:
            god_text = self.font.render("GOD MODE", True, (255, 0, 0))  # Red text for visibility
            self.screen.blit(god_text, (config.SCREEN_SIZE - 120, 10))  # Top right corner


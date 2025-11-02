import pygame
from typing import TYPE_CHECKING
from src import config

if TYPE_CHECKING:
    from src.game import Game, GameState

class GameRenderer:
    """Handles all rendering/drawing operations for the Snake game."""
    
    def __init__(self, game: 'Game') -> None:
        """Initialize the game renderer.
        
        Args:
            game: Reference to the main Game instance
        """
        self.game = game
    
    # ==================== Helper Methods ====================
    
    def _draw_overlay(self, color: tuple, alpha: int) -> None:
        """Draw a semi-transparent overlay on the screen.
        
        Args:
            color: RGB color tuple (r, g, b)
            alpha: Transparency value (0-255)
        """
        overlay = pygame.Surface((config.SCREEN_SIZE, config.SCREEN_SIZE))
        overlay.set_alpha(alpha)
        overlay.fill(color)
        self.game.screen.blit(overlay, (0, 0))
    
    def _draw_centered_text(self, text: str, y_pos: float, color: tuple, font: pygame.font.Font = None) -> None:
        """Draw centered text at specified y position.
        
        Args:
            text: Text to render
            y_pos: Vertical position (center point)
            color: RGB color tuple
            font: Font to use (defaults to self.game.font)
        """
        if font is None:
            font = self.game.font
        
        rendered_text = font.render(text, True, color)
        text_rect = rendered_text.get_rect(center=(config.SCREEN_SIZE / 2, y_pos))
        self.game.screen.blit(rendered_text, text_rect)
    
    def _draw_title(self, text: str, y_pos: float, color: tuple) -> None:
        """Draw a title using the title font.
        
        Args:
            text: Title text to render
            y_pos: Vertical position (center point)
            color: RGB color tuple
        """
        self._draw_centered_text(text, y_pos, color, self.game.title_font)
    
    def _draw_large_text(self, text: str, y_pos: float, color: tuple) -> None:
        """Draw large text using the large font.
        
        Args:
            text: Text to render
            y_pos: Vertical position (center point)
            color: RGB color tuple
        """
        self._draw_centered_text(text, y_pos, color, self.game.large_font)
    
    def _draw_decorative_snakes(self) -> None:
        """Draw decorative snakes with transparency for menu screens."""
        if not hasattr(self.game, 'decorative_snakes'):
            return
        
        # Create a surface with per-pixel alpha
        snake_surface = pygame.Surface((config.SCREEN_SIZE, config.SCREEN_SIZE), pygame.SRCALPHA)
        
        # Draw snakes directly onto the surface using the new surface parameter
        for snake in self.game.decorative_snakes:
            snake.draw(surface=snake_surface)
        
        # Apply transparency to the entire surface
        snake_surface.set_alpha(config.DECORATIVE_SNAKE_OPACITY)
        self.game.screen.blit(snake_surface, (0, 0))
    
    # ==================== Splash Screen ====================
    
    def draw_splash_screen(self) -> None:
        """Draw the splash/main menu screen."""
        self.game.background_renderer.draw_animated_grid(
            config.SPLASH_BG[0], config.SPLASH_BG[1], config.SPLASH_BG[2], 1
        )
        
        # Draw decorative snakes with transparency
        self._draw_decorative_snakes()
        
        # Light overlay for text readability
        self._draw_overlay(
            (config.SPLASH_OVERLAY[0], config.SPLASH_OVERLAY[1], config.SPLASH_OVERLAY[2]),
            config.SPLASH_OVERLAY[3]
        )
        
        # Title
        self._draw_title("PySnake", config.SCREEN_SIZE / 3, config.DARK_BLUE_TEXT)
        
        # GitHub reference (smaller font)
        github_text = self.game.font.render("JoergKau/Python-Modern-SnakeGame // on github", True, config.MEDIUM_BLUE_TEXT)
        github_rect = github_text.get_rect(center=(config.SCREEN_SIZE / 2, config.SCREEN_SIZE / 3 + 40))
        self.game.screen.blit(github_text, github_rect)

        # Start instruction
        self._draw_centered_text("Press SPACE to start", config.SCREEN_SIZE / 2, config.MEDIUM_BLUE_TEXT)
        
        # Screensaver instruction
        self._draw_centered_text("Press S for Screensaver", config.SCREEN_SIZE / 2 + 30, config.MEDIUM_BLUE_TEXT)

        # High scores
        self.draw_high_scores()
        
        # Particles
        self.game.particle_manager.draw(self.game.screen)
        
        pygame.display.flip()
    
    # ==================== Playing State ====================
    
    def draw_game_elements(self) -> None:
        """Draw common game elements like snakes, food, particles, and HUD."""
        self.game.background_renderer.draw_animated_grid(
            config.GAME_BG[0], config.GAME_BG[1], config.GAME_BG[2], self.game.level
        )
        
        for snake in self.game.snakes:
            # Handle invincibility blinking for player snake
            if not snake.is_ai and snake.is_invincible:
                if snake.is_invincible_and_blinking():
                    snake.draw()  # Show snake
                # else: don't draw snake (blinking effect)
            else:
                snake.draw()  # Normal drawing
        
        self.game.food.draw()
        self.game.particle_manager.draw(self.game.screen)
        self.draw_hud()

    def draw_playing(self) -> None:
        """Draw the playing state screen."""
        self.draw_game_elements()
        
        # Draw pause indicator when game is paused
        from src.game import GameState
        if self.game.game_state == GameState.PAUSED:
            self.draw_pause_overlay()
        
        pygame.display.flip()
    
    # ==================== Pause Screen ====================
    
    def draw_pause_overlay(self) -> None:
        """Draw the pause screen overlay."""
        # Semi-transparent black overlay
        overlay = pygame.Surface((config.SCREEN_SIZE, config.SCREEN_SIZE), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.game.screen.blit(overlay, (0, 0))

        # "PAUSED" text
        self._draw_title("PAUSED", config.SCREEN_SIZE / 2 - 50, config.PAUSE_YELLOW)

        # Continue instruction
        self._draw_centered_text("Press P or SPACE to continue", config.SCREEN_SIZE / 2 + 20, config.PAUSE_YELLOW)

        # Highlight around "PAUSED"
        pause_text = self.game.title_font.render("PAUSED", True, config.PAUSE_YELLOW)
        pause_rect = pause_text.get_rect(center=(config.SCREEN_SIZE / 2, config.SCREEN_SIZE / 2 - 50))
        highlight = pygame.Surface((pause_rect.width + 20, pause_rect.height + 10), pygame.SRCALPHA)
        highlight.fill((*config.PAUSE_HIGHLIGHT[:3], 120))
        self.game.screen.blit(highlight, (pause_rect.x - 10, pause_rect.y - 5))
    
    # ==================== Level Complete Screen ====================
    
    def draw_level_complete_screen(self) -> None:
        """Draw the level complete screen."""
        self.game.background_renderer.draw_animated_grid(
            config.LEVEL_COMPLETE_BG[0], config.LEVEL_COMPLETE_BG[1], config.LEVEL_COMPLETE_BG[2], self.game.level
        )
        
        # Draw decorative snakes with transparency
        self._draw_decorative_snakes()
        
        # Light overlay for text readability
        self._draw_overlay(config.LEVEL_COMPLETE_BG, 100)
        
        # Level complete headline
        self._draw_large_text(
            f"Level {self.game.level} Completed",
            config.SCREEN_SIZE / 3,
            config.DARK_BROWN_TEXT
        )

        # Score
        self._draw_centered_text(
            f"Score: {self.game.score}",
            config.SCREEN_SIZE / 2,
            config.MEDIUM_BROWN_TEXT
        )

        # Food collected
        self._draw_centered_text(
            f"Food: {self.game.apples_eaten}/{config.APPLES_PER_LEVEL}",
            config.SCREEN_SIZE / 2 + 30,
            config.MEDIUM_BROWN_TEXT
        )

        # Continue instruction
        self._draw_centered_text(
            "Press SPACE to continue",
            config.SCREEN_SIZE * 2 / 3,
            config.MEDIUM_BROWN_TEXT
        )

        # High scores
        self._draw_level_complete_high_scores()

        # Particles
        self.game.particle_manager.draw(self.game.screen)

        pygame.display.flip()

    def _draw_level_complete_high_scores(self) -> None:
        """Draw high scores on the level complete screen."""
        high_scores = self.game.highscore_manager.scores
        for i, score in enumerate(high_scores[:5]):
            y_position = config.SCREEN_SIZE * 3 / 4 + i * 25
            
            # Rank number
            rank_text = self.game.font.render(f"{i+1}.", True, config.MEDIUM_BROWN_TEXT)
            self.game.screen.blit(rank_text, (config.SCREEN_SIZE / 2 - 40, y_position))
            
            # Score
            score_text = self.game.font.render(str(score), True, config.MEDIUM_BROWN_TEXT)
            self.game.screen.blit(score_text, (config.SCREEN_SIZE / 2 + 10, y_position))
    
    # ==================== Death Animation ====================
    
    def draw_death_animation(self) -> None:
        """Draw the death animation."""
        self.game.background_renderer.draw_animated_grid(
            config.GAME_BG[0], config.GAME_BG[1], config.GAME_BG[2], self.game.level
        )
        
        # Draw enemy snakes (not the player)
        for snake in self.game.snakes:
            if snake != self.game.player_snake:
                # Handle invincibility blinking for AI snakes (if any)
                if snake.is_ai and snake.is_invincible:
                    if snake.is_invincible_and_blinking():
                        snake.draw()
                else:
                    snake.draw()
                
        # Draw food
        self.game.food.draw()
        
        # Draw the player snake with death animation
        if hasattr(self.game, 'player_snake'):
            self.game.player_snake.draw_death_animation()
        
        # Draw UI elements
        score_text = self.game.font.render(f"Score: {self.game.score}", True, config.WHITE_TEXT)
        self.game.screen.blit(score_text, (10, 10))
        
        level_text = self.game.font.render(f"Level: {self.game.level}", True, config.WHITE_TEXT)
        self.game.screen.blit(level_text, (10, 40))
    
    # ==================== Game Over Screen ====================
    
    def draw_game_over_screen(self) -> None:
        """Draw the game over screen."""
        self.game.background_renderer.draw_animated_grid(
            config.GAME_OVER_BG[0], config.GAME_OVER_BG[1], config.GAME_OVER_BG[2], self.game.level
        )
        
        # Draw decorative snakes with transparency
        self._draw_decorative_snakes()
        
        # Light overlay for text readability
        self._draw_overlay(config.GAME_OVER_BG, 100)
        
        # "Game Over" title
        self._draw_title("Game Over", config.SCREEN_SIZE / 3, config.DARK_BROWN_TEXT)

        # Score
        self._draw_centered_text(
            f"Your Score: {self.game.score}",
            config.SCREEN_SIZE / 2,
            config.MEDIUM_BROWN_TEXT
        )

        # Restart instructions
        self._draw_centered_text(
            "Press SPACE to play on",
            config.SCREEN_SIZE * 2 / 3 - 25,
            config.MEDIUM_BROWN_TEXT
        )

        self._draw_centered_text(
            "Press R to restart game",
            config.SCREEN_SIZE * 2 / 3,
            config.MEDIUM_BROWN_TEXT
        )

        self._draw_centered_text(
            "Press ESC to return to menu",
            config.SCREEN_SIZE * 2 / 3 + 25,
            config.MEDIUM_BROWN_TEXT
        )

        # High scores
        self.draw_high_scores()
        
        # Particles
        self.game.particle_manager.draw(self.game.screen)
        
        pygame.display.flip()
    
    # ==================== HUD ====================
    
    def draw_hud(self) -> None:
        """Draw the heads-up display showing score, level, and other game info."""
        # Score
        score_text = self.game.font.render(f"Score: {self.game.score}", True, config.WHITE_TEXT)
        self.game.screen.blit(score_text, (10, 10))
        
        # Level
        level_text = self.game.font.render(f"Level: {self.game.level}", True, config.WHITE_TEXT)
        self.game.screen.blit(level_text, (10, 40))
        
        # God Mode indicator
        if self.game.god_mode:
            god_text = self.game.font.render("GOD MODE", True, (255, 0, 0))
            self.game.screen.blit(god_text, (config.SCREEN_SIZE - 120, 10))
        
        # Invincibility indicator - only show if NOT in god mode
        if self.game.player_snake and self.game.player_snake.is_invincible and not self.game.god_mode:
            current_time = pygame.time.get_ticks()
            elapsed = current_time - self.game.player_snake.invincibility_start_time
            remaining = max(0, (self.game.player_snake.invincibility_duration - elapsed) / 1000.0)
            
            # Blinking text for last second
            if remaining < 1.0:
                if (current_time // 200) % 2 == 0:  # Blink every 200ms
                    invincible_text = self.game.font.render(f"INVINCIBLE {remaining:.1f}s", True, (255, 255, 0))
                    self.game.screen.blit(invincible_text, (config.SCREEN_SIZE - 180, 40))
            else:
                invincible_text = self.game.font.render(f"INVINCIBLE {remaining:.1f}s", True, (0, 255, 255))
                self.game.screen.blit(invincible_text, (config.SCREEN_SIZE - 180, 40))
    
    # ==================== High Scores ====================
    
    def draw_high_scores(self) -> None:
        """Draw high scores based on the current game state."""
        from src.game import GameState
        if self.game.game_state == GameState.GAME_OVER:
            self._draw_game_over_high_scores()
        else:
            self._draw_splash_high_scores()

    def _draw_game_over_high_scores(self) -> None:
        """Draw high scores on the game over screen."""
        box_y = int(config.SCREEN_SIZE / 2 + config.GAME_OVER_SCORE_BOX_Y_OFFSET)
        scores_to_show = min(5, len(self.game.highscore_manager.scores))
        
        if scores_to_show > 0:
            self._draw_high_scores_box(box_y, scores_to_show)
            self._draw_high_scores_title(box_y)
            self._draw_high_scores_list(box_y)

    def _draw_high_scores_box(self, box_y: int, scores_to_show: int) -> None:
        """Draw the decorative box background for high scores."""
        pygame.draw.rect(
            self.game.screen, 
            (220, 150, 130, 180), 
            (int(config.SCREEN_SIZE / 2 - config.HIGH_SCORE_BOX_WIDTH / 2), 
             box_y, 
             config.HIGH_SCORE_BOX_WIDTH, 
             30 + scores_to_show * 25), 
            border_radius=config.HIGH_SCORE_BOX_RADIUS
        )

    def _draw_high_scores_title(self, box_y: int) -> None:
        """Draw the high scores title."""
        self._draw_centered_text(
            "High Scores",
            box_y + config.GAMEOVER_BOX_TITLE_Y,
            config.DARK_BROWN_TEXT
        )

    def _draw_high_scores_list(self, box_y: int) -> None:
        """Draw the list of high scores."""
        for i, score in enumerate(self.game.highscore_manager.scores[:5]):
            self._draw_centered_text(
                f"{i + 1}. {score}",
                box_y + config.GAMEOVER_BOX_LIST_Y + i * config.HIGH_SCORE_LINE_SPACING,
                config.MEDIUM_BROWN_TEXT
            )

    def _draw_splash_high_scores(self) -> None:
        """Draw high scores on the splash screen."""
        y_pos = config.SCREEN_SIZE / 2 + 50
        
        # Title
        self._draw_centered_text("High Scores", y_pos, config.DARK_BLUE_TEXT)
        y_pos += 40

        # Scores list
        for i, score in enumerate(self.game.highscore_manager.scores):
            self._draw_centered_text(f"{i + 1}. {score}", y_pos, config.MEDIUM_BROWN_TEXT)
            y_pos += 30

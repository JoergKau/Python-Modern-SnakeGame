import pygame
import random
import math
from enum import Enum
from typing import List
from src import config

class FruitType(Enum):
    APPLE = 0
    CHERRY = 1
    ORANGE = 2
    LEMON = 3

    @staticmethod
    def random():
        return random.choice(list(FruitType))

class Food:
    def __init__(self, game: 'Game', snakes: List['Snake']) -> None:
        self.game = game
        self.snakes = snakes
        self.screen = game.screen
        self.pulse_time = 0
        self.visible = True
        self.fruit_type = FruitType.random()
        self.position = self.spawn()

    def spawn(self) -> pygame.Vector2:
        self.pulse_time = 0
        grid_size = self.game.get_grid_size()
        while True:
            pos = pygame.Vector2(random.randint(0, grid_size - 1), random.randint(0, grid_size - 1))
            if not any(pos in snake.body for snake in self.snakes):
                self.fruit_type = FruitType.random()
                return pos

    def update(self, dt: float) -> None:
        self.pulse_time += dt

    def draw(self) -> None:
        if not self.visible:
            return

        cell_size = self.game.player_snake.get_cell_size()
        center_x = self.position.x * cell_size + cell_size / 2
        center_y = self.position.y * cell_size + cell_size / 2

        pulse = 1.0 + 0.1 * math.sin(self.pulse_time * 4)
        size = cell_size * 0.8 * config.FOOD_SIZE_MULTIPLIER * pulse

        # Pulsing glow
        glow_pulse = 1.0 + 0.2 * math.sin(self.pulse_time * 4)

        # Outer glow
        s = pygame.Surface((size * 2.5, size * 2.5), pygame.SRCALPHA)
        pygame.draw.circle(s, (255, 255, 255, int(15 * glow_pulse)), (size * 1.25, size * 1.25), size * 1.25)
        self.screen.blit(s, (center_x - size * 1.25, center_y - size * 1.25))

        # Middle-outer glow
        s = pygame.Surface((size * 2.0, size * 2.0), pygame.SRCALPHA)
        pygame.draw.circle(s, (255, 255, 255, int(25 * glow_pulse)), (size, size), size)
        self.screen.blit(s, (center_x - size, center_y - size))

        # Middle glow
        s = pygame.Surface((size * 1.5, size * 1.5), pygame.SRCALPHA)
        pygame.draw.circle(s, (255, 255, 255, int(40 * glow_pulse)), (size * 0.75, size * 0.75), size * 0.75)
        self.screen.blit(s, (center_x - size * 0.75, center_y - size * 0.75))

        # Inner glow
        s = pygame.Surface((size * 1.2, size * 1.2), pygame.SRCALPHA)
        pygame.draw.circle(s, (255, 255, 255, int(60 * glow_pulse)), (size * 0.6, size * 0.6), size * 0.6)
        self.screen.blit(s, (center_x - size * 0.6, center_y - size * 0.6))


        if self.fruit_type == FruitType.APPLE:
            # Create a single surface for the apple
            apple_surface = pygame.Surface((size * 1.2, size * 1.2), pygame.SRCALPHA)

            # Shadow
            pygame.draw.ellipse(apple_surface, (100, 50, 50, 100), (2, 2, size, size))

            # Main body
            brightness = int(220 + 35 * math.sin(self.pulse_time * 6))
            pygame.draw.ellipse(apple_surface, (brightness, 50, 50), (0, 0, size, size))
            
            # Highlight
            highlight_surface = pygame.Surface((size * 0.3, size * 0.3), pygame.SRCALPHA)
            pygame.draw.ellipse(highlight_surface, (255, 150, 150, 180), highlight_surface.get_rect())
            apple_surface.blit(highlight_surface, (size * 0.15, size * 0.15))

            # Leaf
            leaf_surface = pygame.Surface((size * 0.25, size * 0.15), pygame.SRCALPHA)
            pygame.draw.ellipse(leaf_surface, (100, 180, 80), leaf_surface.get_rect())
            leaf_surface = pygame.transform.rotate(leaf_surface, -20)
            apple_surface.blit(leaf_surface, (size * 0.4, 0))

            self.screen.blit(apple_surface, (center_x - size * 0.6, center_y - size * 0.6))


        elif self.fruit_type == FruitType.CHERRY:
            cherry_size = size * 0.65
            brightness = int(200 + 35 * math.sin(self.pulse_time * 6))
            cherry_surface = pygame.Surface((size * 1.2, size), pygame.SRCALPHA)

            # Stems (adjusted positions)
            pygame.draw.line(cherry_surface, (100, 80, 40), (size * 0.3, size * 0.5 - cherry_size * 0.5), (size * 0.6, size * 0.5 - cherry_size * 0.5), 2)
            pygame.draw.line(cherry_surface, (100, 80, 40), (size * 0.9, size * 0.5 - cherry_size * 0.5), (size * 0.6, size * 0.5 - cherry_size * 0.5), 2)

            # Left cherry
            pygame.draw.circle(cherry_surface, (brightness, 30, 50), (size * 0.3, size * 0.5), cherry_size / 2)
            pygame.draw.circle(cherry_surface, (255, 100, 120, 180), (int(size * 0.25), int(size * 0.5 - cherry_size * 0.1)), int(cherry_size * 0.15))

            # Right cherry
            pygame.draw.circle(cherry_surface, (brightness, 30, 50), (size * 0.9, size * 0.5), cherry_size / 2)
            pygame.draw.circle(cherry_surface, (255, 100, 120, 180), (int(size * 0.85), int(size * 0.5 - cherry_size * 0.1)), int(cherry_size * 0.15))

            self.screen.blit(cherry_surface, (center_x - size * 0.6, center_y - size * 0.5))

        elif self.fruit_type == FruitType.ORANGE:
            brightness = int(220 + 35 * math.sin(self.pulse_time * 6))
            orange_surface = pygame.Surface((size * 1.2, size * 1.2), pygame.SRCALPHA)

            # Shadow
            pygame.draw.ellipse(orange_surface, (150, 80, 30, 100), (2, 2, size, size))

            # Main orange body
            pygame.draw.ellipse(orange_surface, (brightness, int(brightness * 0.6), 30), (0, 0, size, size))

            # Highlight
            highlight_surface = pygame.Surface((size * 0.3, size * 0.3), pygame.SRCALPHA)
            pygame.draw.ellipse(highlight_surface, (255, 200, 100, 180), highlight_surface.get_rect())
            orange_surface.blit(highlight_surface, (size * 0.15, size * 0.15))

            # Texture dots
            for i in range(8):
                angle = i * (2 * math.pi) / 8
                dot_x = size/2 + math.cos(angle) * size * 0.25
                dot_y = size/2 + math.sin(angle) * size * 0.25
                pygame.draw.circle(orange_surface, (brightness - 30, int(brightness * 0.5), 20, 100), (dot_x, dot_y), size * 0.04)

            # Green leaf
            leaf_surface = pygame.Surface((size * 0.2, size * 0.12), pygame.SRCALPHA)
            pygame.draw.ellipse(leaf_surface, (80, 150, 60), leaf_surface.get_rect())
            leaf_surface = pygame.transform.rotate(leaf_surface, -20)
            orange_surface.blit(leaf_surface, (size * 0.4, 0))

            self.screen.blit(orange_surface, (center_x - size * 0.6, center_y - size * 0.6))

        elif self.fruit_type == FruitType.LEMON:
            brightness = int(230 + 25 * math.sin(self.pulse_time * 6))
            lemon_surface = pygame.Surface((size, size * 1.2), pygame.SRCALPHA)

            # Shadow
            pygame.draw.ellipse(lemon_surface, (150, 150, 60, 100), (2, 2, size * 0.8, size))

            # Main lemon body
            pygame.draw.ellipse(lemon_surface, (brightness, brightness - 10, 50), (0, 0, size * 0.8, size))

            # Highlight
            highlight_surface = pygame.Surface((size * 0.25, size * 0.35), pygame.SRCALPHA)
            pygame.draw.ellipse(highlight_surface, (255, 255, 150, 180), highlight_surface.get_rect())
            lemon_surface.blit(highlight_surface, (size * 0.15, size * 0.2))

            # Small green leaf
            leaf_surface = pygame.Surface((size * 0.15, size * 0.1), pygame.SRCALPHA)
            pygame.draw.ellipse(leaf_surface, (80, 150, 60), leaf_surface.get_rect())
            leaf_surface = pygame.transform.rotate(leaf_surface, 30)
            lemon_surface.blit(leaf_surface, (size * 0.1, 0))

            self.screen.blit(lemon_surface, (center_x - size * 0.4, center_y - size * 0.6))
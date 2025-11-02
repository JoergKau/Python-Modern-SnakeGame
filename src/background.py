
import pygame
import math
from src import config

class BackgroundRenderer:
    def __init__(self, screen):
        self.screen = screen
        self.grid_size = config.GRID_SIZE
        self.animation_time = 0

    def update(self, dt):
        self.animation_time += dt

    def draw_animated_grid(self, bg_r, bg_g, bg_b, level):
        level_tint = self._get_level_background_tint(level)
        tinted_r = (bg_r + level_tint[0]) // 2
        tinted_g = (bg_g + level_tint[1]) // 2
        tinted_b = (bg_b + level_tint[2]) // 2
        self.screen.fill((tinted_r, tinted_g, tinted_b))

        cell_size = self.screen.get_width() / self.grid_size
        
        pulse_speed = 1.5 + (level - 1) * 0.3
        wave_speed = 2.0 + (level - 1) * 0.5
        wave_amplitude = 2.0 + (level - 1) * 0.5
        phase_shift = 0.3 + (level - 1) * 0.1
        
        grid_color = self._get_grid_color_for_level(level)
        
        pulse_alpha = 15 + (35 - 15) * (0.5 + 0.5 * math.sin(self.animation_time * pulse_speed))
        
        wave_pattern = (level - 1) % 4

        # Draw vertical lines
        for i in range(self.grid_size + 1):
            x = i * cell_size
            wave_offset = self._calculate_wave_offset(i, wave_speed, wave_amplitude, phase_shift, wave_pattern, True)
            
            color_mod = 1.0 if i % 2 == 0 else 0.9
            line_color = (grid_color[0] * color_mod, grid_color[1] * color_mod, grid_color[2] * color_mod)
            
            # Create a new surface for the line to handle alpha
            line_surface = pygame.Surface((2, self.screen.get_height()), pygame.SRCALPHA)
            pygame.draw.line(line_surface, (*line_color, pulse_alpha), (0, 0), (0, self.screen.get_height()))
            self.screen.blit(line_surface, (x + wave_offset - 1, 0))


        # Draw horizontal lines
        for i in range(self.grid_size + 1):
            y = i * cell_size
            wave_offset = self._calculate_wave_offset(i, wave_speed, wave_amplitude, phase_shift, wave_pattern, False)
            
            color_mod = 1.0 if i % 2 == 0 else 0.9
            line_color = (grid_color[0] * color_mod, grid_color[1] * color_mod, grid_color[2] * color_mod)

            line_surface = pygame.Surface((self.screen.get_width(), 2), pygame.SRCALPHA)
            pygame.draw.line(line_surface, (*line_color, pulse_alpha), (0, 0), (self.screen.get_width(), 0))
            self.screen.blit(line_surface, (0, y + wave_offset -1))

        # Draw center crosshair
        center_x = self.screen.get_width() / 2
        center_y = self.screen.get_height() / 2
        crosshair_alpha = pulse_alpha * (1.5 + level * 0.1)
        crosshair_color = (*grid_color, crosshair_alpha)
        
        line_surface_h = pygame.Surface((self.screen.get_width(), 1 + level * 0.2), pygame.SRCALPHA)
        pygame.draw.line(line_surface_h, crosshair_color, (0, 0), (self.screen.get_width(), 0))
        self.screen.blit(line_surface_h, (0, center_y))

        line_surface_v = pygame.Surface((1 + level * 0.2, self.screen.get_height()), pygame.SRCALPHA)
        pygame.draw.line(line_surface_v, crosshair_color, (0, 0), (0, self.screen.get_height()))
        self.screen.blit(line_surface_v, (center_x, 0))

        self._draw_background_shapes(level, cell_size)

    def _get_grid_color_for_level(self, level):
        colors = [
            (255, 255, 255),  # White
            (200, 220, 255),  # Light blue
            (200, 255, 220),  # Light green
            (255, 255, 200),  # Light yellow
            (255, 220, 255)   # Light magenta
        ]
        return colors[(level - 1) % 5]

    def _calculate_wave_offset(self, index, wave_speed, amplitude, phase, pattern, is_vertical):
        if pattern == 0:
            return math.sin(self.animation_time * wave_speed + index * phase) * amplitude
        elif pattern == 1:
            return math.sin(self.animation_time * wave_speed * 2 + index * phase) * amplitude * 0.7
        elif pattern == 2:
            return math.sin(self.animation_time * wave_speed - index * phase) * amplitude
        elif pattern == 3:
            wave1 = math.sin(self.animation_time * wave_speed + index * phase) * amplitude * 0.6
            wave2 = math.sin(self.animation_time * wave_speed * 1.5 - index * phase * 0.5) * amplitude * 0.4
            return wave1 + wave2
        return 0

    def _get_level_background_tint(self, level):
        tints = [
            (155, 204, 153),  # Green
            (155, 190, 210),  # Blueish
            (200, 200, 153),  # Yellowish
            (200, 180, 200),  # Purplish
            (180, 200, 180)   # Cyanish
        ]
        return tints[(level - 1) % 5]

    def _draw_background_shapes(self, level, cell_size):
        shape_type = (level - 1) % 4
        grid_color = self._get_grid_color_for_level(level)

        if shape_type == 0:
            self._draw_pulsing_circles(cell_size, grid_color)
        elif shape_type == 1:
            self._draw_rotating_corners(grid_color)
        elif shape_type == 2:
            self._draw_diagonal_pattern(cell_size, grid_color)
        elif shape_type == 3:
            self._draw_concentric_circles(grid_color)

    def _draw_pulsing_circles(self, cell_size, color):
        pulse = 1.0 + 0.3 * math.sin(self.animation_time * 3)
        
        for i in range(0, self.grid_size + 1, 3):
            for j in range(0, self.grid_size + 1, 3):
                x = i * cell_size
                y = j * cell_size
                
                local_pulse = pulse * math.sin(self.animation_time * 2 + i * 0.5 + j * 0.5)
                size = cell_size * 0.3 * abs(local_pulse)
                
                circle_surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                pygame.draw.ellipse(circle_surface, (*color, 60), (0, 0, size*2, size*2))
                self.screen.blit(circle_surface, (x - size, y - size))


    def _draw_rotating_corners(self, color):
        rotation = self.animation_time * 0.5
        size = self.screen.get_width() * 0.15
        
        corners = [
            (size / 2, size / 2),
            (self.screen.get_width() - size / 2, size / 2),
            (size / 2, self.screen.get_height() - size / 2),
            (self.screen.get_width() - size / 2, self.screen.get_height() - size / 2)
        ]
        
        for corner_x, corner_y in corners:
            # Create a surface for rotation
            rect_surface = pygame.Surface((size, size), pygame.SRCALPHA)
            pygame.draw.rect(rect_surface, (*color, 80), (0, 0, size, size), 2)
            
            rotated_surface = pygame.transform.rotate(rect_surface, math.degrees(rotation))
            new_rect = rotated_surface.get_rect(center = (corner_x, corner_y))
            self.screen.blit(rotated_surface, new_rect.topleft)

            # Inner rect
            rect_surface_inner = pygame.Surface((size * 0.6, size * 0.6), pygame.SRCALPHA)
            pygame.draw.rect(rect_surface_inner, (*color, 80), (0,0, size*0.6, size*0.6), 2)

            rotated_surface_inner = pygame.transform.rotate(rect_surface_inner, math.degrees(-rotation * 2))
            new_rect_inner = rotated_surface_inner.get_rect(center = (corner_x, corner_y))
            self.screen.blit(rotated_surface_inner, new_rect_inner.topleft)


    def _draw_diagonal_pattern(self, cell_size, color):
        offset = (self.animation_time * 20) % (cell_size * 2)
        
        for i in range(int(-self.screen.get_height() / (cell_size * 2)) - 1, int(self.screen.get_width() / (cell_size * 2)) + 1):
            x1 = i * cell_size * 2 + offset
            y1 = 0
            x2 = x1 + self.screen.get_height()
            y2 = self.screen.get_height()
            
            pygame.draw.line(self.screen, (*color, 50), (x1, y1), (x2, y2), 1)


    def _draw_concentric_circles(self, color):
        center_x = self.screen.get_width() / 2
        center_y = self.screen.get_height() / 2
        max_radius = math.sqrt(center_x**2 + center_y**2)
        
        offset = (self.animation_time * 30) % 100
        
        for r in range(int(offset), int(max_radius), 100):
            pygame.draw.ellipse(self.screen, (*color, 70), (center_x - r, center_y - r, r * 2, r * 2), 1)

    def reset(self):
        self.animation_time = 0

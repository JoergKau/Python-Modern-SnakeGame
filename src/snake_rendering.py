"""Snake rendering mixin - handles all visual drawing of the snake."""

import pygame
import math


class SnakeRenderingMixin:
    """Mixin class that handles all snake rendering functionality."""
    
    def draw_circular_segment(self, x, y, radius, color, alpha_multiplier=1.0, surface=None):
        """Helper method to draw a circular segment with alpha transparency."""
        target = surface if surface is not None else self.screen
        
        if alpha_multiplier < 1.0:
            # Draw with alpha using surface
            temp_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(temp_surface, (*color, int(255 * alpha_multiplier)), (radius, radius), radius)
            target.blit(temp_surface, (x - radius, y - radius))
        else:
            # Draw normally if no transparency needed
            pygame.draw.circle(target, color, (x, y), radius)

    def draw_circular_highlight(self, x, y, radius, offset, alpha_multiplier=1.0, surface=None):
        """Helper method to draw a circular highlight with alpha transparency."""
        target = surface if surface is not None else self.screen
        
        if alpha_multiplier < 1.0:
            highlight_temp = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            highlight_color = (255, 255, 200, int(150 * alpha_multiplier))
            pygame.draw.circle(highlight_temp, highlight_color, (radius, radius), radius)
            target.blit(highlight_temp, (x - offset - radius, y - offset - radius))
        else:
            highlight_color = (255, 255, 200, 150)
            pygame.draw.circle(target, highlight_color, (x - offset, y - offset), radius)

    def draw_outline_with_alpha(self, x, y, radius, alpha_multiplier=1.0, surface=None):
        """Helper method to draw a circular outline with alpha transparency."""
        target = surface if surface is not None else self.screen
        
        # Calculate pulsing alpha
        pulse_alpha = int((150 + 105 * math.sin(self.pulse_time)) * alpha_multiplier)
        pulse_alpha = max(0, min(255, pulse_alpha))  # Clamp between 0-255
        
        # Create a temporary surface with alpha support for the outline
        outline_radius = int(radius * 1.1)
        temp_surface = pygame.Surface((outline_radius * 2 + 12, outline_radius * 2 + 12), pygame.SRCALPHA)
        center_pos = (outline_radius + 6, outline_radius + 6)
        
        # Draw the outline circle on the temporary surface with thicker width (6 instead of 3)
        outline_color = (255, 255, 255, pulse_alpha)
        pygame.draw.circle(temp_surface, outline_color, center_pos, outline_radius, width=6)
        
        # Blit the temporary surface to the target
        blit_pos = (int(x - outline_radius - 6), int(y - outline_radius - 6))
        target.blit(temp_surface, blit_pos)

    def draw_circle_with_alpha(self, surface, color, pos, radius, alpha_multiplier=1.0):
        """Helper method to draw a circle with alpha transparency."""
        if alpha_multiplier < 1.0:
            alpha_color = (*color[:3], int(color[3] * alpha_multiplier)) if len(color) == 4 else (*color, int(255 * alpha_multiplier))
            pygame.draw.circle(surface, alpha_color, pos, radius)
        else:
            pygame.draw.circle(surface, color, pos, radius)

    def draw_eyes(self, head_x, head_y, cell_size, alpha_multiplier=1.0, surface=None):
        """Draw snake eyes.
        
        Args:
            head_x: X position of head
            head_y: Y position of head
            cell_size: Size of the cell
            alpha_multiplier: Alpha transparency multiplier
            surface: Optional surface to draw on (defaults to self.screen)
        """
        target = surface if surface is not None else self.screen
        
        eye_size = cell_size * 0.15
        eye_offset = cell_size * 0.25

        dir_x = self.direction.x
        dir_y = self.direction.y

        # Calculate eye positions based on direction
        if dir_x == 1: # Right
            eye1_pos = (head_x + eye_offset, head_y - eye_offset * 0.6)
            eye2_pos = (head_x + eye_offset, head_y + eye_offset * 0.6)
        elif dir_x == -1: # Left
            eye1_pos = (head_x - eye_offset, head_y - eye_offset * 0.6)
            eye2_pos = (head_x - eye_offset, head_y + eye_offset * 0.6)
        elif dir_y == 1: # Down
            eye1_pos = (head_x - eye_offset * 0.6, head_y + eye_offset)
            eye2_pos = (head_x + eye_offset * 0.6, head_y + eye_offset)
        else: # Up
            eye1_pos = (head_x - eye_offset * 0.6, head_y - eye_offset)
            eye2_pos = (head_x + eye_offset * 0.6, head_y - eye_offset)

        # Apply alpha for transparency if needed
        if alpha_multiplier < 1.0:
            # Draw with alpha using surface
            eye_surface = pygame.Surface((cell_size, cell_size), pygame.SRCALPHA)
            
            # Draw white of eyes
            self.draw_circle_with_alpha(eye_surface, (255, 255, 255), (eye1_pos[0] - head_x + cell_size/2, eye1_pos[1] - head_y + cell_size/2), eye_size * 1.2, alpha_multiplier)
            self.draw_circle_with_alpha(eye_surface, (255, 255, 255), (eye2_pos[0] - head_x + cell_size/2, eye2_pos[1] - head_y + cell_size/2), eye_size * 1.2, alpha_multiplier)

            # Draw pupils
            pupil_size = eye_size * 0.6
            self.draw_circle_with_alpha(eye_surface, (0, 0, 0), (eye1_pos[0] - head_x + cell_size/2, eye1_pos[1] - head_y + cell_size/2), pupil_size, alpha_multiplier)
            self.draw_circle_with_alpha(eye_surface, (0, 0, 0), (eye2_pos[0] - head_x + cell_size/2, eye2_pos[1] - head_y + cell_size/2), pupil_size, alpha_multiplier)
            
            target.blit(eye_surface, (head_x - cell_size/2, head_y - cell_size/2))
        else:
            # Draw normally if no transparency needed
            # Draw white of eyes
            pygame.draw.circle(target, (255, 255, 255), eye1_pos, eye_size * 1.2)
            pygame.draw.circle(target, (255, 255, 255), eye2_pos, eye_size * 1.2)

            # Draw pupils
            pupil_size = eye_size * 0.6
            pygame.draw.circle(target, (0, 0, 0), eye1_pos, pupil_size)
            pygame.draw.circle(target, (0, 0, 0), eye2_pos, pupil_size)

    def draw(self, alpha_multiplier=1.0, surface=None):
        """Draw the snake.
        
        Args:
            alpha_multiplier: Alpha transparency multiplier (0.0 to 1.0)
            surface: Optional surface to draw on (defaults to self.screen)
        """
        target = surface if surface is not None else self.screen
        if not self.is_ai:
            self.pulse_time += self.game.clock.get_time() / 1000.0 * 5

        cell_size = self.get_cell_size()

        for i, segment in enumerate(self.body):
            lerp_factor = (len(self.body) - 1 - i) / max(1, len(self.body) - 1)
            color = (
                int(self.color_head[0] + (self.color_tail[0] - self.color_head[0]) * lerp_factor),
                int(self.color_head[1] + (self.color_tail[1] - self.color_head[1]) * lerp_factor),
                int(self.color_head[2] + (self.color_tail[2] - self.color_head[2]) * lerp_factor)
            )

            if i < len(self.previous_body):
                prev_segment = self.previous_body[i]
                draw_pos = prev_segment.lerp(segment, self.move_progress)
            else:
                draw_pos = segment

            x = draw_pos.x * cell_size + cell_size / 2
            y = draw_pos.y * cell_size + cell_size / 2
            radius = cell_size / 2 * 0.95

            # Draw player outline with alpha
            if not self.is_ai:
                self.draw_outline_with_alpha(x, y, radius, alpha_multiplier, target)

            # Draw main body segment with alpha
            self.draw_circular_segment(x, y, radius, color, alpha_multiplier, target)

            # Define highlight variables early to avoid scope issues
            highlight_radius = radius * 0.4
            highlight_offset = radius * 0.3

            # Draw 3D highlight with alpha
            self.draw_circular_highlight(x, y, highlight_radius, highlight_offset, alpha_multiplier, target)

        # Draw eyes
        if len(self.body) > 0:
            head_segment = self.body[0]
            if len(self.previous_body) > 0:
                prev_head_segment = self.previous_body[0]
                head_pos = prev_head_segment.lerp(head_segment, self.move_progress)
            else:
                head_pos = head_segment

            head_x = head_pos.x * cell_size + cell_size / 2
            head_y = head_pos.y * cell_size + cell_size / 2
            self.draw_eyes(head_x, head_y, cell_size, alpha_multiplier, target)

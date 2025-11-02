"""Snake death animation mixin - handles death visual effects."""

import pygame


class SnakeDeathAnimationMixin:
    """Mixin class that handles snake death animation functionality."""
    
    def start_death_animation(self):
        """Initialize the death animation."""
        self.is_dying = True
        self.segment_fall_speed = []
        self.segment_alpha = []
        self.segment_positions = []  # Store initial screen positions for falling effect
        self.segment_offsets = []    # Store vertical offsets for falling
        
        # Initialize fall speeds, alpha, and positions for each segment
        # Segments fall at different speeds for cascading effect
        # Increase the fall speeds significantly for much faster falling
        for i in range(len(self.body)):
            speed = int((100 + i * 20) * 5)  # Original speed increased by 400% (5x faster)
            self.segment_fall_speed.append(speed)
            self.segment_alpha.append(255.0)  # Start fully opaque
            # Store the original grid position
            self.segment_positions.append(self.body[i].copy())
            self.segment_offsets.append(0.0)  # No initial offset

    def update_death_animation(self, dt):
        """Update the death animation state."""
        if not self.is_dying:
            return

        # Handle blink phase
        if self.blink_phase:
            self.blink_timer += dt
            if self.blink_timer >= self.blink_duration:
                self.blink_phase = False
        else:
            cell_size = self.get_cell_size()

            # Update each segment's offset and alpha for falling phase
            for i in range(len(self.segment_offsets)):
                # Increase the vertical offset to make segment appear to fall
                # Use the increased speeds and apply to screen coordinates
                self.segment_offsets[i] += (self.segment_fall_speed[i] / 100.0) * dt * cell_size  # Apply to screen coordinates
                    
                # Fade out
                if i < len(self.segment_alpha):
                    alpha = self.segment_alpha[i]
                    alpha -= 170 * dt  # Fade speed
                    self.segment_alpha[i] = max(0, alpha)

    def draw_line_with_alpha(self, surface, color, start_pos, end_pos, width, alpha_multiplier=1.0):
        """Helper method to draw a line with alpha transparency."""
        if alpha_multiplier < 1.0:
            alpha_color = (*color[:3], int(color[3] * alpha_multiplier)) if len(color) == 4 else (*color, int(255 * alpha_multiplier))
            pygame.draw.line(surface, alpha_color, start_pos, end_pos, width)
        else:
            pygame.draw.line(surface, color, start_pos, end_pos, width)

    def draw_death_eyes(self, head_x, head_y, cell_size, alpha_multiplier=1.0):
        """Draw X-style eyes for death animation."""
        eye_size = cell_size * 0.15
        eye_offset = cell_size * 0.25

        # Calculate eye positions
        if len(self.body) > 0:
            dir_x = self.direction.x
            dir_y = self.direction.y

            # Calculate eye positions based on direction
            if dir_x == 1:  # Right
                eye1_pos = (head_x + eye_offset, head_y - eye_offset * 0.6)
                eye2_pos = (head_x + eye_offset, head_y + eye_offset * 0.6)
            elif dir_x == -1:  # Left
                eye1_pos = (head_x - eye_offset, head_y - eye_offset * 0.6)
                eye2_pos = (head_x - eye_offset, head_y + eye_offset * 0.6)
            elif dir_y == 1:  # Down
                eye1_pos = (head_x - eye_offset * 0.6, head_y + eye_offset)
                eye2_pos = (head_x + eye_offset * 0.6, head_y + eye_offset)
            else:  # Up
                eye1_pos = (head_x - eye_offset * 0.6, head_y - eye_offset)
                eye2_pos = (head_x + eye_offset * 0.6, head_y - eye_offset)

            # Draw X-shaped eyes for death effect
            if alpha_multiplier < 1.0:
                # Draw with alpha
                eye_surface = pygame.Surface((cell_size, cell_size), pygame.SRCALPHA)
                # Draw X for each eye
                offset = eye_size * 0.7
                self.draw_line_with_alpha(eye_surface, (255, 0, 0), 
                                (eye1_pos[0] - head_x + cell_size/2 - offset, eye1_pos[1] - head_y + cell_size/2 - offset),
                                (eye1_pos[0] - head_x + cell_size/2 + offset, eye1_pos[1] - head_y + cell_size/2 + offset), 3, alpha_multiplier)
                self.draw_line_with_alpha(eye_surface, (255, 0, 0), 
                                (eye1_pos[0] - head_x + cell_size/2 + offset, eye1_pos[1] - head_y + cell_size/2 - offset),
                                (eye1_pos[0] - head_x + cell_size/2 - offset, eye1_pos[1] - head_y + cell_size/2 + offset), 3, alpha_multiplier)
                
                self.draw_line_with_alpha(eye_surface, (255, 0, 0), 
                                (eye2_pos[0] - head_x + cell_size/2 - offset, eye2_pos[1] - head_y + cell_size/2 - offset),
                                (eye2_pos[0] - head_x + cell_size/2 + offset, eye2_pos[1] - head_y + cell_size/2 + offset), 3, alpha_multiplier)
                self.draw_line_with_alpha(eye_surface, (255, 0, 0), 
                                (eye2_pos[0] - head_x + cell_size/2 + offset, eye2_pos[1] - head_y + cell_size/2 - offset),
                                (eye2_pos[0] - head_x + cell_size/2 - offset, eye2_pos[1] - head_y + cell_size/2 + offset), 3, alpha_multiplier)
                
                self.screen.blit(eye_surface, (head_x - cell_size/2, head_y - cell_size/2))
            else:
                # Draw X for each eye
                offset = eye_size * 0.7
                pygame.draw.line(self.screen, (255, 0, 0), 
                                (eye1_pos[0] - offset, eye1_pos[1] - offset),
                                (eye1_pos[0] + offset, eye1_pos[1] + offset), 3)
                pygame.draw.line(self.screen, (255, 0, 0), 
                                (eye1_pos[0] + offset, eye1_pos[1] - offset),
                                (eye1_pos[0] - offset, eye1_pos[1] + offset), 3)
                
                pygame.draw.line(self.screen, (255, 0, 0), 
                                (eye2_pos[0] - offset, eye2_pos[1] - offset),
                                (eye2_pos[0] + offset, eye2_pos[1] + offset), 3)
                pygame.draw.line(self.screen, (255, 0, 0), 
                                (eye2_pos[0] + offset, eye2_pos[1] - offset),
                                (eye2_pos[0] - offset, eye2_pos[1] + offset), 3)

    def draw_death_animation(self):
        """Draw the death animation."""
        if not self.is_dying:
            return

        cell_size = self.get_cell_size()

        # Blink phase: draw with red blinking effect
        if self.blink_phase:
            blink_frequency = 8  # Blink 8 times per second
            blink_state = int(self.blink_timer * blink_frequency) % 2
            if blink_state == 1:  # Only draw when visible
                for i, segment in enumerate(self.segment_positions):  # Use original positions
                    # Use red color for death animation
                    r = 255
                    g = 50
                    b = 50
                    
                    # Use cell_size for positioning
                    x = segment.x * cell_size + cell_size / 2
                    y = (segment.y * cell_size + cell_size / 2)  # Keep original y for now
                    radius = cell_size / 2 * 0.95

                    # Draw player outline even during death blink
                    if not self.is_ai:
                        pygame.draw.circle(self.screen, (255, 255, 255), (x, y), radius * 1.1, width=3)

                    # Draw main circle with red color
                    pygame.draw.circle(self.screen, (r, g, b), (x, y), radius)

                    # Add highlight for 3D effect
                    highlight_color = (255, 200, 200, 150)
                    highlight_radius = radius * 0.4
                    highlight_offset = radius * 0.3
                    pygame.draw.circle(self.screen, highlight_color, (x - highlight_offset, y - highlight_offset), highlight_radius)

                # Draw eyes for head (X eyes for death effect)
                if len(self.segment_positions) > 0:
                    head_segment = self.segment_positions[0]
                    head_x = head_segment.x * cell_size + cell_size / 2
                    head_y = head_segment.y * cell_size + cell_size / 2
                    # For death effect, we can draw X eyes instead of normal eyes
                    self.draw_death_eyes(head_x, head_y, cell_size)
        else:
            # Falling and fading phase: draw each segment individually with different alpha and vertical offset
            for i in range(len(self.segment_positions) - 1, -1, -1):  # Draw from tail to head
                if i >= len(self.segment_positions) or i >= len(self.segment_alpha):
                    continue
                    
                segment = self.segment_positions[i]
                alpha = self.segment_alpha[i]
                
                if alpha <= 0:  # Skip fully faded segments
                    continue
                
                lerp_factor = i / max(1, len(self.segment_positions) - 1)
                base_color = (
                    int(self.color_head[0] + (self.color_tail[0] - self.color_head[0]) * lerp_factor),
                    int(self.color_head[1] + (self.color_tail[1] - self.color_head[1]) * lerp_factor),
                    int(self.color_head[2] + (self.color_tail[2] - self.color_head[2]) * lerp_factor)
                )
                
                # Use cell_size for positioning with vertical offset for falling effect
                x = segment.x * cell_size + cell_size / 2
                y = (segment.y * cell_size + cell_size / 2) + self.segment_offsets[i]  # Apply vertical offset
                radius = cell_size / 2 * 0.95

                # Draw with alpha using surface
                temp_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(temp_surface, (*base_color, int(alpha)), (radius, radius), radius)
                self.screen.blit(temp_surface, (x - radius, y - radius))

                # Add highlight for 3D effect with alpha
                highlight_temp = pygame.Surface((radius * 0.8, radius * 0.8), pygame.SRCALPHA)
                highlight_color = (255, 255, 200, int(alpha * 0.6))
                highlight_radius = radius * 0.4
                pygame.draw.circle(highlight_temp, highlight_color, (radius * 0.4, radius * 0.4), highlight_radius)
                self.screen.blit(highlight_temp, (x - radius * 0.6, y - radius * 0.6))

            # Draw eyes for head if not fully faded
            if len(self.segment_positions) > 0 and len(self.segment_alpha) > 0 and self.segment_alpha[0] > 0:
                head_segment = self.segment_positions[0]
                head_x = head_segment.x * cell_size + cell_size / 2
                head_y = (head_segment.y * cell_size + cell_size / 2) + self.segment_offsets[0]  # Apply offset
                # Draw eyes with alpha
                self.draw_eyes(head_x, head_y, cell_size, alpha_multiplier=self.segment_alpha[0]/255.0)

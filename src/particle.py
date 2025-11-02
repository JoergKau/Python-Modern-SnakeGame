import pygame
import random
import math
from src import config

class Particle:
    def __init__(self, x, y, color, min_life, max_life, min_speed, max_speed, min_size, max_size):
        self.x = x
        self.y = y
        self.color = color
        self.lifetime = random.uniform(min_life, max_life)
        self.life = self.lifetime
        speed = random.uniform(min_speed, max_speed)
        angle = random.uniform(0, 2 * math.pi) # Use math.pi for radians
        rotated_vector = pygame.math.Vector2(1, 0).rotate(math.degrees(angle)) # Convert to degrees for pygame.Vector2.rotate
        self.vx = speed * rotated_vector.x
        self.vy = speed * rotated_vector.y
        self.size = random.uniform(min_size, max_size)

    def update(self, dt):
        self.life -= dt
        self.x += self.vx * dt
        self.y += self.vy * dt

    def draw(self, surface, draw_glow=False):
        """Draw the particle with optional glow effect."""
        if self.life > 0:
            alpha = int(255 * (self.life / self.lifetime))
            # Check if color has alpha
            if len(self.color) == 4:
                color = self.color[:3] + (int(self.color[3] * (self.life / self.lifetime)),)
            else:
                color = self.color + (alpha,)
            
            # Draw glow effect FIRST if requested (for player particles)
            if draw_glow:
                glow_alpha = int(alpha * 0.3)
                if len(self.color) == 4:
                    glow_color = self.color[:3] + (glow_alpha,)
                else:
                    glow_color = self.color + (glow_alpha,)
                pygame.draw.circle(surface, glow_color, (int(self.x), int(self.y)), int(self.size * 2))
            
            # Draw main particle on top
            pygame.draw.circle(surface, color, (int(self.x), int(self.y)), int(self.size))

class ParticleManager:
    def __init__(self):
        self.particles = []
        # Separate particle lists for different screen backgrounds
        self.title_particles = []  # For splash and level complete screens
        self.game_over_particles = []  # For game over screen
        self.player_particles = []  # For player snake trail
        self.last_player_particle_spawn = 0.0  # Time tracking for player particle spawning
        self.particle_surface = pygame.Surface((config.SCREEN_SIZE, config.SCREEN_SIZE), pygame.SRCALPHA)

    def add_particle(self, x, y, color_palette, min_life, max_life, min_speed, max_speed, min_size, max_size):
        color = random.choice(color_palette)
        self.particles.append(Particle(x, y, color, min_life, max_life, min_speed, max_speed, min_size, max_size))

    def add_background_particle(self, x, y, color_palette, min_life, max_life, min_speed, max_speed, min_size, max_size, particle_type="title"):
        """Add a background particle for title screens."""
        color = random.choice(color_palette)
        particle = Particle(x, y, color, min_life, max_life, min_speed, max_speed, min_size, max_size)
        
        if particle_type == "game_over":
            self.game_over_particles.append(particle)
        else:  # Default to title particles
            self.title_particles.append(particle)

    def spawn_title_particles(self, count):
        """Spawn blue particles for splash and level complete screens."""
        for _ in range(count):
            x = random.uniform(0, config.SCREEN_SIZE)
            y = random.uniform(0, config.SCREEN_SIZE)
            self.add_background_particle(
                x, y,
                config.BLUE_PARTICLES,
                config.TITLE_PARTICLE_MIN_LIFE, config.TITLE_PARTICLE_MAX_LIFE,
                config.PLAYER_PARTICLE_MIN_SPEED, config.PLAYER_PARTICLE_MAX_SPEED,
                config.TITLE_PARTICLE_MIN_SIZE, config.TITLE_PARTICLE_MAX_SIZE,
                particle_type="title"
            )

    def spawn_game_over_particles(self, count):
        """Spawn red/orange particles for game over screen."""
        for _ in range(count):
            x = random.uniform(0, config.SCREEN_SIZE)
            y = random.uniform(0, config.SCREEN_SIZE)
            self.add_background_particle(
                x, y,
                config.RED_ORANGE_PARTICLES,
                config.TITLE_PARTICLE_MIN_LIFE, config.TITLE_PARTICLE_MAX_LIFE,
                config.PLAYER_PARTICLE_MIN_SPEED, config.PLAYER_PARTICLE_MAX_SPEED,
                config.TITLE_PARTICLE_MIN_SIZE, config.TITLE_PARTICLE_MAX_SIZE,
                particle_type="game_over"
            )

    def spawn_player_particles(self, snake, current_time):
        """Spawn trail particles for the player snake."""
        if snake is None or len(snake.body) == 0:
            return
        
        # Check if enough time has passed to spawn new particles
        if current_time - self.last_player_particle_spawn >= config.PLAYER_PARTICLE_SPAWN_INTERVAL:
            self.last_player_particle_spawn = current_time
            
            # Don't spawn if we're at the limit, but keep updating the timer
            if len(self.player_particles) >= config.MAX_PLAYER_PARTICLES:
                return
            
            cell_size = config.SCREEN_SIZE / config.GRID_SIZE
            
            # Spawn fewer particles - reduced from body size // 3 to // 5
            particles_to_spawn = max(1, len(snake.body) // 5)
            
            for _ in range(particles_to_spawn):
                if len(self.player_particles) >= config.MAX_PLAYER_PARTICLES:
                    break
                
                # Pick a random segment starting from the second segment (skip the head)
                # This makes trails appear behind the head, not at the head position
                if len(snake.body) > 1:
                    segment_index = random.randint(1, len(snake.body) - 1)
                    segment = snake.body[segment_index]
                else:
                    segment = snake.body[0]
                
                # Get segment position and add randomness
                px = segment.x * cell_size + cell_size / 2
                py = segment.y * cell_size + cell_size / 2
                
                px += random.uniform(-cell_size * 0.3, cell_size * 0.3)
                py += random.uniform(-cell_size * 0.3, cell_size * 0.3)
                
                # Create particle with proper min/max ranges
                color = random.choice(config.PLAYER_PARTICLES)
                particle = Particle(
                    px, py, color,
                    config.PLAYER_PARTICLE_MIN_LIFE, config.PLAYER_PARTICLE_MAX_LIFE,
                    config.PLAYER_PARTICLE_MIN_SPEED, config.PLAYER_PARTICLE_MAX_SPEED,
                    config.PLAYER_PARTICLE_MIN_SIZE, config.PLAYER_PARTICLE_MAX_SIZE
                )
                self.player_particles.append(particle)

    def update(self, dt):
        # Update main particles
        for particle in self.particles:
            particle.update(dt)
        self.particles = [p for p in self.particles if p.life > 0]

        # Update title particles
        for particle in self.title_particles:
            particle.update(dt)
        self.title_particles = [p for p in self.title_particles if p.life > 0]

        # Update game over particles
        for particle in self.game_over_particles:
            particle.update(dt)
        self.game_over_particles = [p for p in self.game_over_particles if p.life > 0]

        # Update player particles
        for particle in self.player_particles:
            particle.update(dt)
        self.player_particles = [p for p in self.player_particles if p.life > 0]

    def draw(self, screen):
        self.particle_surface.fill((0, 0, 0, 0))  # Clear the surface with transparent color

        # Draw all particle types onto the shared particle_surface
        for particle in self.particles:
            particle.draw(self.particle_surface)
        for particle in self.title_particles:
            particle.draw(self.particle_surface, draw_glow=True)
        for particle in self.game_over_particles:
            particle.draw(self.particle_surface, draw_glow=True)
        # Draw player particles with glow effect
        for particle in self.player_particles:
            particle.draw(self.particle_surface, draw_glow=True)
        
        screen.blit(self.particle_surface, (0, 0))

    def clear_background_particles(self):
        """Clear background particles when transitioning between screens."""
        self.title_particles.clear()
        self.game_over_particles.clear()

    def clear_player_particles(self):
        """Clear player trail particles."""
        self.player_particles.clear()

    def clear_all(self):
        """Clear all particles."""
        self.particles.clear()
        self.title_particles.clear()
        self.game_over_particles.clear()
        self.player_particles.clear()

"""Snake AI mixin - handles all artificial intelligence and decision-making."""

import pygame
import random
from src import config


class SnakeAIMixin:
    """Mixin class that handles snake AI functionality."""
    
    def make_ai_decision(self):
        """Main AI decision-making method."""
        # Get cell size for position calculations
        cell_size = self.get_cell_size()
        grid_width = self.get_grid_width()
        grid_height = self.get_grid_height()
        
        # Check if near edge (within 3 cells for earlier detection)
        near_left_edge = self.position.x < 3
        near_right_edge = self.position.x >= grid_width - 3
        near_top_edge = self.position.y < 3
        near_bottom_edge = self.position.y >= grid_height - 3
        near_edge = near_left_edge or near_right_edge or near_top_edge or near_bottom_edge
        
        # Check if in corner (very dangerous)
        in_corner = (near_left_edge and near_top_edge) or \
                   (near_left_edge and near_bottom_edge) or \
                   (near_right_edge and near_top_edge) or \
                   (near_right_edge and near_bottom_edge)
        
        # Check if next move in current direction is immediately dangerous
        next_pos = self.position + self.direction
        current_dir_dangerous = not self.is_safe(next_pos)
        
        # PRIORITY 1: If in corner, ALWAYS try to escape (100% chance)
        if in_corner:
            escape_dirs = []
            
            # Find directions that lead away from BOTH edges
            for test_dir in [pygame.Vector2(1, 0), pygame.Vector2(-1, 0), pygame.Vector2(0, 1), pygame.Vector2(0, -1)]:
                # Skip opposite direction
                if test_dir == self.direction * -1:
                    continue
                
                test_pos = self.position + test_dir
                
                # Check if this direction escapes corner
                escapes_corner = False
                if near_left_edge and near_top_edge and (test_dir.x > 0 or test_dir.y > 0):  # right or down
                    escapes_corner = True
                if near_left_edge and near_bottom_edge and (test_dir.x > 0 or test_dir.y < 0):  # right or up
                    escapes_corner = True
                if near_right_edge and near_top_edge and (test_dir.x < 0 or test_dir.y > 0):  # left or down
                    escapes_corner = True
                if near_right_edge and near_bottom_edge and (test_dir.x < 0 or test_dir.y < 0):  # left or up
                    escapes_corner = True
                
                # Add if safe and escapes corner
                if escapes_corner and self.is_safe(test_pos):
                    escape_dirs.append(test_dir)
            
            # Pick escape direction if available
            if escape_dirs:
                self.direction = random.choice(escape_dirs)
                return
        
        # PRIORITY 2: If near edge (but not in corner), turn away (90% chance)
        if near_edge and not current_dir_dangerous and random.random() < 0.9:
            away_dirs = []
            
            # Prefer directions away from edges
            for test_dir in [pygame.Vector2(1, 0), pygame.Vector2(-1, 0), pygame.Vector2(0, 1), pygame.Vector2(0, -1)]:
                # Skip opposite direction
                if test_dir == self.direction * -1:
                    continue
                
                test_pos = self.position + test_dir
                
                # Check if this direction moves away from edges
                moves_away_from_edge = False
                if near_left_edge and test_dir.x > 0:  # Move right
                    moves_away_from_edge = True
                if near_right_edge and test_dir.x < 0:  # Move left
                    moves_away_from_edge = True
                if near_top_edge and test_dir.y > 0:   # Move down
                    moves_away_from_edge = True
                if near_bottom_edge and test_dir.y < 0: # Move up
                    moves_away_from_edge = True
                
                # Add if safe and moves away from edge
                if moves_away_from_edge and self.is_safe(test_pos):
                    away_dirs.append(test_dir)
            
            # Pick a direction away from edge if available
            if away_dirs:
                self.direction = random.choice(away_dirs)
                return
        
        # If current direction is dangerous, find a safe one
        if current_dir_dangerous:
            safe_dirs = []
            
            # Check all directions (except opposite)
            for test_dir in [pygame.Vector2(1, 0), pygame.Vector2(-1, 0), pygame.Vector2(0, 1), pygame.Vector2(0, -1)]:
                # Skip opposite direction
                if test_dir == self.direction * -1:
                    continue
                
                test_pos = self.position + test_dir
                
                # Check if safe
                if self.is_safe(test_pos):
                    safe_dirs.append(test_dir)
            
            # Pick a random safe direction
            if safe_dirs:
                self.direction = random.choice(safe_dirs)
        # Randomly change direction for exploration (30% chance, like original Java)
        elif random.random() < 0.3:
            valid_dirs = []
            
            for test_dir in [pygame.Vector2(1, 0), pygame.Vector2(-1, 0), pygame.Vector2(0, 1), pygame.Vector2(0, -1)]:
                # Skip opposite direction
                if test_dir == self.direction * -1:
                    continue
                
                test_pos = self.position + test_dir
                
                # Only add if not immediately dangerous
                if self.is_safe(test_pos):
                    valid_dirs.append(test_dir)
            
            # Pick a random valid direction
            if valid_dirs:
                self.direction = random.choice(valid_dirs)
        # Otherwise, keep current direction

    def _find_immediate_dangers(self):
        """Find immediate dangers that require urgent action."""
        immediate_dangers = []
        for direction in [pygame.Vector2(1, 0), pygame.Vector2(-1, 0), pygame.Vector2(0, 1), pygame.Vector2(0, -1)]:
            next_pos = self.position + direction
            
            # Check wall collision
            grid_width = self.get_grid_width()
            grid_height = self.get_grid_height()
            if not 0 <= next_pos.x < grid_width or not 0 <= next_pos.y < grid_height:
                immediate_dangers.append(direction)
            
            # Check body collision
            if next_pos in self.body:
                immediate_dangers.append(direction)
            
            # Check for other snake collision (including head to head)
            for snake in self.game.snakes:
                if snake is not self and next_pos in snake.body:
                    immediate_dangers.append(direction)
        
        return immediate_dangers

    def _find_potential_traps(self):
        """Find potential trap situations that require careful planning."""
        # Look for situations where the snake might be boxing itself in
        grid_width = self.get_grid_width()
        grid_height = self.get_grid_height()
        
        # Count available safe cells in the immediate vicinity
        safe_neighbors = 0
        for direction in [pygame.Vector2(1, 0), pygame.Vector2(-1, 0), pygame.Vector2(0, 1), pygame.Vector2(0, -1)]:
            next_pos = self.position + direction
            if self.is_safe(next_pos):
                safe_neighbors += 1
        
        # If there are few safe neighbors, the snake might be in a tight spot
        return safe_neighbors < 2

    def _plan_escape_route(self):
        """Plan an escape route when in a dangerous situation."""
        # Find all safe directions
        safe_directions = []
        for direction in [pygame.Vector2(1, 0), pygame.Vector2(-1, 0), pygame.Vector2(0, 1), pygame.Vector2(0, -1)]:
            if direction != self.direction * -1 and self.is_safe(self.position + direction):
                safe_directions.append(direction)
        
        if not safe_directions:
            return self.direction  # No safe options, keep current direction
        
        # Choose direction that leads to the most open space
        best_direction = safe_directions[0]
        max_escape_space = 0
        
        for direction in safe_directions:
            escape_space = self._calculate_escape_space(self.position + direction)
            if escape_space > max_escape_space:
                max_escape_space = escape_space
                best_direction = direction
        
        return best_direction

    def _calculate_escape_space(self, pos):
        """Calculate how much open space is available from a given position."""
        # Use a simple flood-fill-like approach to count reachable safe cells
        visited = set()
        queue = [pos]
        count = 0
        max_count = 10  # Don't search too deeply for performance
        
        grid_width = self.get_grid_width()
        grid_height = self.get_grid_height()
        
        while queue and count < max_count:
            current_pos = queue.pop(0)
            current_key = (int(current_pos.x), int(current_pos.y))
            
            if current_key in visited:
                continue
            
            visited.add(current_key)
            count += 1
            
            # Check neighbors
            for direction in [pygame.Vector2(1, 0), pygame.Vector2(-1, 0), pygame.Vector2(0, 1), pygame.Vector2(0, -1)]:
                neighbor = current_pos + direction
                neighbor_key = (int(neighbor.x), int(neighbor.y))
                
                if (neighbor_key not in visited and 
                    0 <= neighbor.x < grid_width and 0 <= neighbor.y < grid_height):
                    # Check if this position is safe (not in any snake's body)
                    is_safe = True
                    for snake in self.game.snakes:
                        for segment in snake.body:
                            if neighbor == segment:
                                is_safe = False
                                break
                        if not is_safe:
                            break
                    
                    if is_safe:
                        queue.append(neighbor)
        
        return count

    def _is_least_dangerous_position(self, pos):
        """Determine if a position is the least dangerous among all options."""
        grid_width = self.get_grid_width()
        grid_height = self.get_grid_height()
        
        # Calculate danger factors
        wall_danger = 0
        if not (0 <= pos.x < grid_width and 0 <= pos.y < grid_height):
            wall_danger = 1000  # High danger for walls
        
        body_danger = 0
        if pos in self.body:
            body_danger = 1000  # High danger for self collision
        
        other_snake_danger = 0
        for snake in self.game.snakes:
            if snake is not self and pos in snake.body:
                other_snake_danger = 1000  # High danger for other snake collision
        
        total_danger = wall_danger + body_danger + other_snake_danger
        return total_danger == min(wall_danger + body_danger + other_snake_danger,
                                  1000)  # Compare to other possible moves

    def _choose_direction_away_from_danger(self, safe_directions):
        """Choose the direction that moves away from immediate dangers."""
        if not safe_directions:
            return self.direction  # Return current if no safe options
        
        best_direction = safe_directions[0]
        best_score = -float('inf')
        
        for direction in safe_directions:
            score = 0
            next_pos = self.position + direction
            
            # Score based on distance to walls (prefer center)
            grid_width = self.get_grid_width()
            grid_height = self.get_grid_height()
            dist_to_walls = min(next_pos.x, next_pos.y, grid_width - 1 - next_pos.x, grid_height - 1 - next_pos.y)
            score += dist_to_walls * 10  # Prioritize staying away from walls
            
            # Score based on distance to other snakes
            min_dist_to_snakes = float('inf')
            for snake in self.game.snakes:
                if snake is not self:
                    for segment in snake.body:
                        dist = (next_pos - segment).length()
                        if dist < min_dist_to_snakes:
                            min_dist_to_snakes = dist
            
            if min_dist_to_snakes < float('inf'):
                if min_dist_to_snakes < config.AI_DANGER_ZONE_RADIUS:
                    score -= (config.AI_DANGER_ZONE_RADIUS - min_dist_to_snakes) * 50
                else:
                    score += min_dist_to_snakes * 2
            
            if score > best_score:
                best_score = score
                best_direction = direction
        
        return best_direction

    def calculate_direction_score(self, direction):
        """Calculate a score for moving in a given direction."""
        next_pos = self.position + direction
        score = 0

        grid_width = self.get_grid_width()
        grid_height = self.get_grid_height()

        # Wall avoidance - highest priority
        if not 0 <= next_pos.x < grid_width or not 0 <= next_pos.y < grid_height:
            return -1000

        # Self collision avoidance - high priority
        if next_pos in self.body:
            return -1000

        # Check for predicted collisions with other snakes
        min_distance_to_snakes = float('inf')
        for snake in self.game.snakes:
            if snake is not self:
                # Check if this position collides with the head of other snake (predicted position)
                if next_pos == snake.position + snake.direction:
                    return -1000  # Avoid head-on collisions
                
                # Find minimum distance to any part of other snakes
                for segment in snake.body:
                    dist = (next_pos - segment).length()
                    if dist < min_distance_to_snakes:
                        min_distance_to_snakes = dist
                    
                    # If too close to any segment, heavily penalize
                    if dist < config.AI_BODY_DANGER_RADIUS:
                        score -= (config.AI_BODY_DANGER_RADIUS - dist) * 100
                    elif dist < config.AI_DANGER_ZONE_RADIUS:
                        score -= (config.AI_DANGER_ZONE_RADIUS - dist) * 10  # Less penalty but still negative

        # Look ahead for potential dangers
        look_ahead_steps = min(config.AI_LOOK_AHEAD_STEPS, min(grid_width, grid_height) // 4)  # Don't look too far on small grids
        current_pos = next_pos
        for step in range(1, look_ahead_steps + 1):
            look_ahead_pos = current_pos + direction * step
            if (not 0 <= look_ahead_pos.x < grid_width or 
                not 0 <= look_ahead_pos.y < grid_height):
                score -= 50  # Penalize approaching walls
            else:
                # Check for potential snake collisions in the path
                for snake in self.game.snakes:
                    if snake is not self:
                        for segment in snake.body:
                            dist = (look_ahead_pos - segment).length()
                            if dist < 2:  # Very close in path
                                score -= 40 * (look_ahead_steps - step + 1)  # More penalty for closer steps

        # Evaluate potential path to food (look ahead)
        if hasattr(self.game, 'food') and self.game.food is not None:
            dist_to_food = (next_pos - self.game.food.position).length()
            
            # Calculate if going toward food is actually safe
            is_path_to_food_safe = self._is_path_to_food_safe(next_pos, direction, grid_width, grid_height)
            
            if is_path_to_food_safe:
                # Higher reward when path is safe
                score += max(0, (max(grid_width, grid_height) - dist_to_food)) * 1.5  # Higher reward for safe food approach
            else:
                # Lower reward for unsafe food approach
                score += max(0, (max(grid_width, grid_height) - dist_to_food)) * 0.3

        # Center preference (keep away from edges) - moderate priority
        center_pos = pygame.Vector2(grid_width / 2, grid_height / 2)
        dist_to_center = (next_pos - center_pos).length()
        max_dist_to_center = (max(grid_width, grid_height) / 2) * 0.7  # Approximate max distance
        center_bonus = (1 - min(dist_to_center / max_dist_to_center, 1.0)) * 15  # Increased center preference
        score += center_bonus

        # Avoid corners where possible - moderate priority
        if (next_pos.x < config.AI_CORNER_TRAP_THRESHOLD or 
            next_pos.x >= grid_width - config.AI_CORNER_TRAP_THRESHOLD or
            next_pos.y < config.AI_CORNER_TRAP_THRESHOLD or 
            next_pos.y >= grid_height - config.AI_CORNER_TRAP_THRESHOLD):
            score -= 25  # Increased penalty for being near walls/corners

        # If in a dangerous situation, prefer directions that increase distance from threats
        if min_distance_to_snakes < config.AI_DANGER_ZONE_RADIUS:
            for snake in self.game.snakes:
                if snake is not self:
                    for segment in snake.body:
                        dist = (next_pos - segment).length()
                        if dist < config.AI_DANGER_ZONE_RADIUS * 1.5:  # Consider wider danger zone
                            # Prefer moving away from this segment
                            direction_to_segment = (segment - self.position).normalize()
                            direction_away = -direction_to_segment
                            if direction.dot(direction_away) > 0:  # Moving away
                                score += dist * 2
        
        # Avoid getting trapped in corners by checking ahead
        corner_danger = self._calculate_corner_danger(next_pos, direction, grid_width, grid_height)
        score -= corner_danger

        return score

    def _is_path_to_food_safe(self, current_pos, direction, grid_width, grid_height):
        """Check if going toward food is safe by looking ahead."""
        if not hasattr(self.game, 'food') or self.game.food is None:
            return False
        
        # Calculate the general direction from current pos to food
        to_food = (self.game.food.position - current_pos).normalize()
        
        # Check if the direction is roughly aligned with food direction
        alignment = direction.dot(to_food)
        
        # Look ahead a few steps in that direction to make sure it's safe
        for step in range(1, min(config.AI_MEDIUM_LOOK_AHEAD, min(grid_width, grid_height) // 3)):
            look_pos = current_pos + direction * step
            
            # Check if this look-ahead position is safe
            if not (0 <= look_pos.x < grid_width and 0 <= look_pos.y < grid_height):
                return False  # Path leads into wall
            
            for snake in self.game.snakes:
                if snake is not self:
                    for segment in snake.body:
                        dist = (look_pos - segment).length()
                        if dist < 2:  # Very close to snake body
                            return False  # Path leads into another snake
        
        # Path looks safe, now check if we're generally heading toward food
        return alignment > 0.5  # Reasonable threshold for "toward food"

    def _calculate_corner_danger(self, pos, direction, grid_width, grid_height):
        """Calculate danger of heading toward corners or edges."""
        danger = 0
        
        # Check if we're approaching a corner or wall
        distance_to_walls = [
            pos.x,                      # Distance to left wall
            grid_width - 1 - pos.x,     # Distance to right wall
            pos.y,                      # Distance to top wall
            grid_height - 1 - pos.y     # Distance to bottom wall
        ]
        
        # If we're already close to any wall, check if we're moving toward it
        min_wall_distance = min(distance_to_walls)
        if min_wall_distance < config.AI_WALL_EMERGENCY_THRESHOLD:
            # We're close to a wall - check if we're moving toward it
            if direction.x < 0 and pos.x < grid_width // 4:  # Moving left toward left wall
                danger += 50
            elif direction.x > 0 and pos.x > grid_width * 3 // 4:  # Moving right toward right wall
                danger += 50
            if direction.y < 0 and pos.y < grid_height // 4:  # Moving up toward top wall
                danger += 50
            elif direction.y > 0 and pos.y > grid_height * 3 // 4:  # Moving down toward bottom wall
                danger += 50
        
        return danger

    def is_safe(self, pos):
        """Check if a position is safe to move to."""
        grid_width = self.get_grid_width()
        grid_height = self.get_grid_height()
            
        if not 0 <= pos.x < grid_width or not 0 <= pos.y < grid_height:
            return False
        if pos in self.body:
            return False
        # Check collision with game snakes (only if they exist - not during menu screens)
        if hasattr(self.game, 'snakes'):
            for snake in self.game.snakes:
                if snake is not self and pos in snake.body:
                    return False
        return True

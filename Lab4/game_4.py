import pygame
import random
import heapq
from enum import Enum
from collections import deque
import sys

# Initialize Pygame
pygame.init()

# Constants
GRID_WIDTH = 30
GRID_HEIGHT = 20
CELL_SIZE = 20
SCREEN_WIDTH = GRID_WIDTH * CELL_SIZE
SCREEN_HEIGHT = GRID_HEIGHT * CELL_SIZE + 60  # Extra space for UI

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GRAY = (128, 128, 128)
YELLOW = (255, 255, 0)
DARK_GREEN = (0, 150, 0)
BROWN = (139, 69, 19)
DARK_GRAY = (64, 64, 64)
PURPLE = (128, 0, 128)

# Direction enum
class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

class Snake:
    def __init__(self):
        self.reset()
    
    def reset(self):
        # Start snake in the middle of the grid
        start_x = GRID_WIDTH // 2
        start_y = GRID_HEIGHT // 2
        self.body = [(start_x, start_y), (start_x - 1, start_y), (start_x - 2, start_y)]
        self.direction = Direction.RIGHT
        self.grow_pending = False
    
    def get_head(self):
        return self.body[0]
    
    def wrap_position(self, x, y):
        """Handle wall wrapping/teleportation"""
        wrapped_x = x % GRID_WIDTH
        wrapped_y = y % GRID_HEIGHT
        return wrapped_x, wrapped_y
    
    def move(self, new_direction=None):
        if new_direction:
            # Prevent snake from moving into itself
            if self.is_opposite_direction(new_direction):
                new_direction = self.direction
            self.direction = new_direction
        
        head_x, head_y = self.get_head()
        dx, dy = self.direction.value
        new_x, new_y = head_x + dx, head_y + dy
        
        # Handle wall wrapping
        new_head = self.wrap_position(new_x, new_y)
        
        self.body.insert(0, new_head)
        
        if not self.grow_pending:
            self.body.pop()
        else:
            self.grow_pending = False
    
    def is_opposite_direction(self, direction):
        current_dx, current_dy = self.direction.value
        new_dx, new_dy = direction.value
        return (current_dx == -new_dx and current_dy == -new_dy)
    
    def grow(self):
        self.grow_pending = True
    
    def check_collision(self, walls=None):
        head_x, head_y = self.get_head()
        
        # Check wall barriers collision
        if walls and (head_x, head_y) in walls:
            return True
        
        # Check self collision
        if self.get_head() in self.body[1:]:
            return True
        
        return False

class Food:
    def __init__(self):
        self.position = self.generate_position()
    
    def generate_position(self):
        return (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
    
    def respawn(self, snake_body, walls=None):
        obstacles = set(snake_body)
        if walls:
            obstacles.update(walls)
        
        # Ensure there's at least one free space
        max_attempts = GRID_WIDTH * GRID_HEIGHT
        attempts = 0
        
        while attempts < max_attempts:
            new_pos = self.generate_position()
            if new_pos not in obstacles:
                self.position = new_pos
                break
            attempts += 1
        
        # If we couldn't find a spot, place it at a random location anyway
        if attempts >= max_attempts:
            self.position = self.generate_position()

class WallGenerator:
    def __init__(self):
        self.walls = set()
    
    def is_path_exists(self, start, goal, walls, snake_body=None):
        """Check if a path exists between start and goal using BFS with wrapping"""
        if start == goal:
            return True
        
        obstacles = set(walls)
        if snake_body:
            obstacles.update(snake_body)
        
        queue = [start]
        visited = {start}
        
        while queue:
            current = queue.pop(0)
            x, y = current
            
            # Check all 4 directions with wrapping
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                new_x = (x + dx) % GRID_WIDTH
                new_y = (y + dy) % GRID_HEIGHT
                new_pos = (new_x, new_y)
                
                if new_pos == goal:
                    return True
                
                if new_pos not in obstacles and new_pos not in visited:
                    visited.add(new_pos)
                    queue.append(new_pos)
        
        return False
    
    def generate_safe_walls(self, num_walls=None, snake_body=None, food_pos=None):
        """Generate walls ensuring the game remains playable"""
        if num_walls is None:
            num_walls = random.randint(10, 25)  # Reduced max walls
        
        self.walls.clear()
        
        # Get key positions
        snake_head = snake_body[0] if snake_body else (GRID_WIDTH // 2, GRID_HEIGHT // 2)
        food_position = food_pos if food_pos else (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
        
        # Create buffer zones around snake and food
        protected_zones = set()
        
        # Snake buffer zone (3x3 around head)
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                buff_x = (snake_head[0] + dx) % GRID_WIDTH
                buff_y = (snake_head[1] + dy) % GRID_HEIGHT
                protected_zones.add((buff_x, buff_y))
        
        # Add snake body to protected zones
        if snake_body:
            protected_zones.update(snake_body)
        
        # Food buffer zone (small buffer)
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                buff_x = (food_position[0] + dx) % GRID_WIDTH
                buff_y = (food_position[1] + dy) % GRID_HEIGHT
                protected_zones.add((buff_x, buff_y))
        
        attempts = 0
        max_attempts = num_walls * 5
        
        while len(self.walls) < num_walls and attempts < max_attempts:
            x = random.randint(0, GRID_WIDTH - 1)
            y = random.randint(0, GRID_HEIGHT - 1)
            wall_pos = (x, y)
            
            if wall_pos not in protected_zones and wall_pos not in self.walls:
                # Temporarily add the wall and check if path still exists
                temp_walls = self.walls | {wall_pos}
                
                if self.is_path_exists(snake_head, food_position, temp_walls, snake_body):
                    self.walls.add(wall_pos)
            
            attempts += 1
    
    def generate_pattern_walls(self, pattern="sparse", snake_body=None, food_pos=None):
        """Generate different wall patterns"""
        self.walls.clear()
        snake_head = snake_body[0] if snake_body else (GRID_WIDTH // 2, GRID_HEIGHT // 2)
        food_position = food_pos if food_pos else (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
        
        if pattern == "corridors":
            # Create vertical corridors
            for x in range(5, GRID_WIDTH - 5, 8):
                for y in range(2, GRID_HEIGHT - 2):
                    if y % 4 != 0:  # Leave gaps for horizontal movement
                        self.walls.add((x, y))
        
        elif pattern == "islands":
            # Create small islands of walls
            island_centers = [(7, 5), (22, 5), (7, 14), (22, 14), (15, 10)]
            for center_x, center_y in island_centers:
                for dx in range(-1, 2):
                    for dy in range(-1, 2):
                        wall_x = (center_x + dx) % GRID_WIDTH
                        wall_y = (center_y + dy) % GRID_HEIGHT
                        if abs(dx) + abs(dy) <= 1:  # Plus shape
                            self.walls.add((wall_x, wall_y))
        
        elif pattern == "maze":
            # Simple maze pattern
            for x in range(0, GRID_WIDTH, 4):
                for y in range(2, GRID_HEIGHT - 2, 4):
                    self.walls.add((x, y))
                    if x + 2 < GRID_WIDTH:
                        self.walls.add((x + 2, y))
        
        # Remove walls that block essential positions
        protected = set()
        if snake_body:
            protected.update(snake_body)
        
        # Protect around snake head
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                buff_x = (snake_head[0] + dx) % GRID_WIDTH
                buff_y = (snake_head[1] + dy) % GRID_HEIGHT
                protected.add((buff_x, buff_y))
        
        # Protect food position
        protected.add(food_position)
        
        self.walls -= protected
        
        # Ensure path exists, remove problematic walls if needed
        if not self.is_path_exists(snake_head, food_position, self.walls, snake_body):
            # Fallback to safe generation
            self.generate_safe_walls(15, snake_body, food_pos)

class SnakeAI:
    def __init__(self):
        pass
    
    def wrap_position(self, x, y):
        """Handle position wrapping for AI pathfinding"""
        return x % GRID_WIDTH, y % GRID_HEIGHT
    
    def get_neighbors(self, pos):
        """Get all valid neighbor positions with wrapping"""
        x, y = pos
        neighbors = []
        
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            new_x, new_y = self.wrap_position(x + dx, y + dy)
            neighbors.append((new_x, new_y))
        
        return neighbors
    
    def dijkstra(self, start, goal, snake_body, walls=None):
        """
        Find shortest path with wrapping support
        """
        # Priority queue: (distance, position, path)
        pq = [(0, start, [])]
        visited = set()
        
        # Combine obstacles
        obstacles = set(snake_body)
        if walls:
            obstacles.update(walls)
        
        while pq:
            dist, current, path = heapq.heappop(pq)
            
            if current in visited:
                continue
            
            visited.add(current)
            
            # If we reached the goal, return the first direction in the path
            if current == goal:
                if path:
                    first_move = path[0]
                    dx = (first_move[0] - start[0]) % GRID_WIDTH
                    dy = (first_move[1] - start[1]) % GRID_HEIGHT
                    
                    # Handle wrapping for direction calculation
                    if dx == 1 or dx == -(GRID_WIDTH - 1):
                        return Direction.RIGHT
                    elif dx == GRID_WIDTH - 1 or dx == -1:
                        return Direction.LEFT
                    elif dy == 1 or dy == -(GRID_HEIGHT - 1):
                        return Direction.DOWN
                    elif dy == GRID_HEIGHT - 1 or dy == -1:
                        return Direction.UP
                return None
            
            # Explore neighbors with wrapping
            for next_pos in self.get_neighbors(current):
                if next_pos not in obstacles and next_pos not in visited:
                    new_path = path + [next_pos]
                    heapq.heappush(pq, (dist + 1, next_pos, new_path))
        
        # If no path found, try to move to an empty space
        return self.find_safe_direction(start, obstacles)
    
    def find_safe_direction(self, head, obstacles):
        """Find a safe direction with wrapping support"""
        x, y = head
        
        best_direction = None
        max_space = -1
        
        for direction in Direction:
            dx, dy = direction.value
            next_x, next_y = self.wrap_position(x + dx, y + dy)
            next_pos = (next_x, next_y)
            
            if next_pos not in obstacles:
                # Count available space from this position
                space_count = self.count_reachable_space(next_pos, obstacles)
                
                if space_count > max_space:
                    max_space = space_count
                    best_direction = direction
        
        return best_direction if best_direction else Direction.RIGHT
    
    def count_reachable_space(self, start, obstacles, max_depth=15):
        """Count reachable space with wrapping"""
        visited = set()
        queue = [(start, 0)]
        count = 0
        
        while queue and count < max_depth:
            current, depth = queue.pop(0)
            
            if current in visited or depth >= max_depth:
                continue
            
            visited.add(current)
            count += 1
            
            for next_pos in self.get_neighbors(current):
                if next_pos not in obstacles and next_pos not in visited:
                    queue.append((next_pos, depth + 1))
        
        return count
    
    def get_next_move(self, snake, food, walls=None):
        """Get the next move for the AI snake"""
        head = snake.get_head()
        food_pos = food.position
        
        # Use Dijkstra to find path to food
        next_direction = self.dijkstra(head, food_pos, snake.body, walls)
        
        if next_direction is None:
            # If no path to food, find safe direction
            obstacles = set(snake.body)
            if walls:
                obstacles.update(walls)
            next_direction = self.find_safe_direction(head, obstacles)
        
        return next_direction

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Snake Game")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        self.wall_generator = WallGenerator()
        self.reset_game()
        
    def reset_game(self):
        self.snake = Snake()
        self.food = Food()
        self.ai = SnakeAI()
        self.score = 0
        self.game_over = False
        self.ai_mode = False
        self.move_delay = 120  # milliseconds
        self.last_move_time = 0
        
        # Generate walls after snake is initialized
        self.generate_new_walls()
        self.food.respawn(self.snake.body, self.wall_generator.walls)
        
    def generate_new_walls(self):
        """Generate new wall pattern"""
        patterns = ['safe', 'corridors', 'islands', 'maze']
        pattern = random.choice(patterns)
        
        if pattern == 'safe':
            self.wall_generator.generate_safe_walls(
                num_walls=random.randint(8, 20),
                snake_body=self.snake.body, 
                food_pos=self.food.position
            )
        else:
            self.wall_generator.generate_pattern_walls(
                pattern=pattern,
                snake_body=self.snake.body, 
                food_pos=self.food.position
            )
        
    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # Toggle AI mode
                    self.ai_mode = not self.ai_mode
                
                elif event.key == pygame.K_r and self.game_over:
                    # Restart game
                    self.reset_game()
                
                elif event.key == pygame.K_g:
                    # Generate new walls (G key)
                    if not self.game_over:
                        self.generate_new_walls()
                        self.food.respawn(self.snake.body, self.wall_generator.walls)
                
                elif not self.ai_mode and not self.game_over:
                    # Manual controls
                    if event.key == pygame.K_UP or event.key == pygame.K_w:
                        self.snake.move(Direction.UP)
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        self.snake.move(Direction.DOWN)
                    elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        self.snake.move(Direction.LEFT)
                    elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        self.snake.move(Direction.RIGHT)
        
        return True
    
    def update(self):
        if self.game_over:
            return
        
        current_time = pygame.time.get_ticks()
        
        # AI mode automatic movement
        if self.ai_mode and current_time - self.last_move_time > self.move_delay:
            next_direction = self.ai.get_next_move(self.snake, self.food, self.wall_generator.walls)
            if next_direction:
                self.snake.move(next_direction)
            self.last_move_time = current_time
        
        # Check collisions (walls only, no boundary collisions due to wrapping)
        if self.snake.check_collision(self.wall_generator.walls):
            self.game_over = True
            return
        
        # Check if snake ate food
        if self.snake.get_head() == self.food.position:
            self.snake.grow()
            self.score += 1
            self.food.respawn(self.snake.body, self.wall_generator.walls)
            
            # Increase speed slightly in AI mode
            if self.ai_mode and self.move_delay > 60:
                self.move_delay = max(60, self.move_delay - 3)
            
            # Generate new walls every 8 points (less frequent)
            if self.score % 8 == 0:
                self.generate_new_walls()
                self.food.respawn(self.snake.body, self.wall_generator.walls)
    
    def draw_grid(self):
        """Draw a subtle grid for better visualization"""
        for x in range(0, SCREEN_WIDTH, CELL_SIZE):
            pygame.draw.line(self.screen, (20, 20, 20), (x, 0), (x, SCREEN_HEIGHT - 60))
        for y in range(0, SCREEN_HEIGHT - 60, CELL_SIZE):
            pygame.draw.line(self.screen, (20, 20, 20), (0, y), (SCREEN_WIDTH, y))
    
    def draw_wrapping_indicators(self):
        """Draw indicators to show wrapping boundaries"""
        # Draw edge highlights to indicate wrapping
        edge_color = PURPLE
        # Top edge
        pygame.draw.line(self.screen, edge_color, (0, 0), (SCREEN_WIDTH, 0), 3)
        # Bottom edge
        pygame.draw.line(self.screen, edge_color, (0, SCREEN_HEIGHT - 60), (SCREEN_WIDTH, SCREEN_HEIGHT - 60), 3)
        # Left edge
        pygame.draw.line(self.screen, edge_color, (0, 0), (0, SCREEN_HEIGHT - 60), 3)
        # Right edge
        pygame.draw.line(self.screen, edge_color, (SCREEN_WIDTH - 1, 0), (SCREEN_WIDTH - 1, SCREEN_HEIGHT - 60), 3)
    
    def draw_walls(self):
        """Draw wall barriers"""
        for x, y in self.wall_generator.walls:
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            
            # Draw wall with a brick-like pattern
            pygame.draw.rect(self.screen, BROWN, rect)
            pygame.draw.rect(self.screen, DARK_GRAY, rect, 2)
            
            # Add some texture to walls
            inner_rect1 = pygame.Rect(x * CELL_SIZE + 2, y * CELL_SIZE + 2, 
                                    CELL_SIZE // 2 - 3, CELL_SIZE // 2 - 3)
            inner_rect2 = pygame.Rect(x * CELL_SIZE + CELL_SIZE // 2 + 1, 
                                    y * CELL_SIZE + CELL_SIZE // 2 + 1, 
                                    CELL_SIZE // 2 - 3, CELL_SIZE // 2 - 3)
            
            pygame.draw.rect(self.screen, (160, 82, 45), inner_rect1)
            pygame.draw.rect(self.screen, (160, 82, 45), inner_rect2)
    
    def draw_snake(self):
        for i, (x, y) in enumerate(self.snake.body):
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            
            if i == 0:  # Head
                pygame.draw.rect(self.screen, DARK_GREEN, rect)
                pygame.draw.rect(self.screen, GREEN, rect, 2)
                
                # Draw eyes on the head
                eye_size = 3
                head_center_x = x * CELL_SIZE + CELL_SIZE // 2
                head_center_y = y * CELL_SIZE + CELL_SIZE // 2
                
                if self.snake.direction == Direction.UP:
                    eye1_pos = (head_center_x - 4, head_center_y - 3)
                    eye2_pos = (head_center_x + 4, head_center_y - 3)
                elif self.snake.direction == Direction.DOWN:
                    eye1_pos = (head_center_x - 4, head_center_y + 3)
                    eye2_pos = (head_center_x + 4, head_center_y + 3)
                elif self.snake.direction == Direction.LEFT:
                    eye1_pos = (head_center_x - 3, head_center_y - 4)
                    eye2_pos = (head_center_x - 3, head_center_y + 4)
                else:  # RIGHT
                    eye1_pos = (head_center_x + 3, head_center_y - 4)
                    eye2_pos = (head_center_x + 3, head_center_y + 4)
                
                pygame.draw.circle(self.screen, WHITE, eye1_pos, eye_size)
                pygame.draw.circle(self.screen, WHITE, eye2_pos, eye_size)
                pygame.draw.circle(self.screen, BLACK, eye1_pos, eye_size - 1)
                pygame.draw.circle(self.screen, BLACK, eye2_pos, eye_size - 1)
            else:  # Body
                pygame.draw.rect(self.screen, GREEN, rect)
                pygame.draw.rect(self.screen, DARK_GREEN, rect, 1)
    
    def draw_food(self):
        x, y = self.food.position
        rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(self.screen, RED, rect)
        pygame.draw.rect(self.screen, (200, 0, 0), rect, 2)
        
        # Draw a small highlight
        highlight_rect = pygame.Rect(x * CELL_SIZE + 2, y * CELL_SIZE + 2, 
                                   CELL_SIZE - 4, CELL_SIZE - 4)
        pygame.draw.rect(self.screen, (255, 100, 100), highlight_rect)
    
    def draw_ui(self):
        # Status bar background
        ui_rect = pygame.Rect(0, SCREEN_HEIGHT - 60, SCREEN_WIDTH, 60)
        pygame.draw.rect(self.screen, GRAY, ui_rect)
        pygame.draw.line(self.screen, WHITE, (0, SCREEN_HEIGHT - 60), (SCREEN_WIDTH, SCREEN_HEIGHT - 60), 2)
        
        # Score
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, SCREEN_HEIGHT - 50))
        
        # Walls count
        walls_text = self.small_font.render(f"Walls: {len(self.wall_generator.walls)}", True, WHITE)
        self.screen.blit(walls_text, (150, SCREEN_HEIGHT - 50))
        
        # Mode indicator
        mode_text = "AI MODE" if self.ai_mode else "MANUAL"
        mode_color = BLUE if self.ai_mode else WHITE
        mode_surface = self.font.render(mode_text, True, mode_color)
        self.screen.blit(mode_surface, (10, SCREEN_HEIGHT - 25))
        
        # Wrapping indicator
        wrap_text = self.small_font.render("WRAPPING ON", True, PURPLE)
        self.screen.blit(wrap_text, (250, SCREEN_HEIGHT - 50))
        
        # Instructions
        if not self.game_over:
            if self.ai_mode:
                instruction = "Space: Manual | G: New Walls | Purple edges = Wrapping"
            else:
                instruction = "Space: AI | WASD/Arrows: Move | G: New Walls"
        else:
            instruction = "R: Restart | Space: Toggle Mode"
        
        instruction_surface = self.small_font.render(instruction, True, WHITE)
        text_width = instruction_surface.get_width()
        self.screen.blit(instruction_surface, (SCREEN_WIDTH - text_width - 10, SCREEN_HEIGHT - 35))
        
        # Game Over message
        if self.game_over:
            game_over_text = self.font.render("GAME OVER!", True, RED)
            text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            
            # Draw background for game over text
            bg_rect = text_rect.inflate(20, 10)
            pygame.draw.rect(self.screen, BLACK, bg_rect)
            pygame.draw.rect(self.screen, WHITE, bg_rect, 2)
            
            self.screen.blit(game_over_text, text_rect)
            
            restart_text = self.small_font.render("Press R to restart", True, WHITE)
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40))
            self.screen.blit(restart_text, restart_rect)
    
    def draw(self):
        self.screen.fill(BLACK)
        
        self.draw_grid()
        self.draw_wrapping_indicators()  # Show wrapping boundaries
        self.draw_walls()
        self.draw_food()
        self.draw_snake()
        self.draw_ui()
        
        pygame.display.flip()
    
    def run(self):
        running = True
        
        while running:
            running = self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(60)  # 60 FPS
        
        pygame.quit()
        sys.exit()

def main():
    game = Game()
    game.run()

if __name__ == "__main__":
    main()
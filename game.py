import pygame
import sys
import random
import heapq
from collections import deque

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 600, 600
GRID_SIZE = 20
GRID_WIDTH = WIDTH // GRID_SIZE
GRID_HEIGHT = HEIGHT // GRID_SIZE
FPS = 10

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
DARK_GREEN = (0, 200, 0)

# Directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

class Snake:
    def __init__(self):
        self.body = deque([(GRID_WIDTH // 2, GRID_HEIGHT // 2)])
        self.direction = RIGHT
        self.grow = False
        self.auto_mode = False
        self.path = []
    
    def move(self):
        if self.auto_mode and self.path:
            next_pos = self.path.pop(0)
            head_x, head_y = self.body[0]
            
            # Calculate the direction to move based on the next position
            dx = next_pos[0] - head_x
            dy = next_pos[1] - head_y
            
            if dx == 1:
                self.direction = RIGHT
            elif dx == -1:
                self.direction = LEFT
            elif dy == 1:
                self.direction = DOWN
            elif dy == -1:
                self.direction = UP
        
        head_x, head_y = self.body[0]
        dx, dy = self.direction
        new_head = ((head_x + dx) % GRID_WIDTH, (head_y + dy) % GRID_HEIGHT)
        
        # Check if the snake collides with itself
        if new_head in self.body:
            return False
        
        self.body.appendleft(new_head)
        
        if not self.grow:
            self.body.pop()
        else:
            self.grow = False
            
        return True
    
    def grow_snake(self):
        self.grow = True
    
    def get_head_position(self):
        return self.body[0]
    
    def toggle_auto_mode(self):
        self.auto_mode = not self.auto_mode
        return self.auto_mode

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Snake Game with Dijkstra's Algorithm")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 36)
        self.reset_game()
    
    def reset_game(self):
        self.snake = Snake()
        self.food = self.place_food()
        self.score = 0
        self.game_over = False
    
    def place_food(self):
        while True:
            food = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
            if food not in self.snake.body:
                return food
    
    def dijkstra(self, start, target):
        # Initialize distances
        distances = {(x, y): float('infinity') for x in range(GRID_WIDTH) for y in range(GRID_HEIGHT)}
        distances[start] = 0
        pq = [(0, start)]
        previous = {}
        
        while pq:
            current_distance, current = heapq.heappop(pq)
            
            if current == target:
                # Reconstruct path
                path = []
                while current in previous:
                    path.append(current)
                    current = previous[current]
                return path[::-1]  # Reverse the path
            
            if current_distance > distances[current]:
                continue
            
            # Check all four directions
            for dx, dy in [UP, DOWN, LEFT, RIGHT]:
                next_x = (current[0] + dx) % GRID_WIDTH
                next_y = (current[1] + dy) % GRID_HEIGHT
                neighbor = (next_x, next_y)
                
                # Skip if the neighbor is part of the snake body (except the tail which will move)
                if neighbor in list(self.snake.body)[:-1]:
                    continue
                
                # Calculate new distance
                new_distance = current_distance + 1
                
                if new_distance < distances[neighbor]:
                    distances[neighbor] = new_distance
                    previous[neighbor] = current
                    heapq.heappush(pq, (new_distance, neighbor))
        
        # If no path is found, return an empty path
        return []
    
    def update(self):
        if self.game_over:
            return
        
        # Calculate path using Dijkstra's algorithm if in auto mode
        if self.snake.auto_mode and not self.snake.path:
            head = self.snake.get_head_position()
            self.snake.path = self.dijkstra(head, self.food)
        
        # Move snake
        if not self.snake.move():
            self.game_over = True
            return
        
        # Check if snake ate food
        if self.snake.get_head_position() == self.food:
            self.snake.grow_snake()
            self.food = self.place_food()
            self.score += 1
            
            # Clear the path if food is eaten
            if self.snake.auto_mode:
                self.snake.path = []
    
    def draw(self):
        self.screen.fill(BLACK)
        
        # Draw grid lines
        for x in range(0, WIDTH, GRID_SIZE):
            pygame.draw.line(self.screen, (50, 50, 50), (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, GRID_SIZE):
            pygame.draw.line(self.screen, (50, 50, 50), (0, y), (WIDTH, y))
        
        # Draw food
        food_rect = pygame.Rect(
            self.food[0] * GRID_SIZE, 
            self.food[1] * GRID_SIZE, 
            GRID_SIZE, GRID_SIZE
        )
        pygame.draw.rect(self.screen, RED, food_rect)
        
        # Draw snake
        for i, (x, y) in enumerate(self.snake.body):
            snake_rect = pygame.Rect(
                x * GRID_SIZE, 
                y * GRID_SIZE, 
                GRID_SIZE, GRID_SIZE
            )
            
            # Head is a different color
            if i == 0:
                pygame.draw.rect(self.screen, GREEN, snake_rect)
            else:
                pygame.draw.rect(self.screen, DARK_GREEN, snake_rect)
        
        # Draw path if in auto mode
        if self.snake.auto_mode:
            head = self.snake.get_head_position()
            path = [head] + self.snake.path
            for i in range(len(path) - 1):
                start_x, start_y = path[i]
                end_x, end_y = path[i + 1]
                start_pos = (start_x * GRID_SIZE + GRID_SIZE // 2, start_y * GRID_SIZE + GRID_SIZE // 2)
                end_pos = (end_x * GRID_SIZE + GRID_SIZE // 2, end_y * GRID_SIZE + GRID_SIZE // 2)
                pygame.draw.line(self.screen, BLUE, start_pos, end_pos, 2)
        
        # Draw score
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
        
        # Draw mode indicator
        mode_text = self.font.render(
            f"Mode: {'AUTO' if self.snake.auto_mode else 'MANUAL'}", 
            True, WHITE
        )
        self.screen.blit(mode_text, (WIDTH - mode_text.get_width() - 10, 10))
        
        # Draw game over text
        if self.game_over:
            game_over_text = self.font.render("GAME OVER! Press R to Restart", True, WHITE)
            text_rect = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            self.screen.blit(game_over_text, text_rect)
        
        pygame.display.flip()
    
    def run(self):
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r and self.game_over:
                        self.reset_game()
                    
                    elif event.key == pygame.K_SPACE:
                        auto_mode = self.snake.toggle_auto_mode()
                        if auto_mode:
                            self.snake.path = []  # Clear existing path
                    
                    elif not self.snake.auto_mode:  # Only allow manual control in manual mode
                        if event.key == pygame.K_UP and self.snake.direction != DOWN:
                            self.snake.direction = UP
                        elif event.key == pygame.K_DOWN and self.snake.direction != UP:
                            self.snake.direction = DOWN
                        elif event.key == pygame.K_LEFT and self.snake.direction != RIGHT:
                            self.snake.direction = LEFT
                        elif event.key == pygame.K_RIGHT and self.snake.direction != LEFT:
                            self.snake.direction = RIGHT
            
            if not self.game_over:
                self.update()
            
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

# Start the game
if __name__ == "__main__":
    game = Game()
    game.run()
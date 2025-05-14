import pygame
import random
import math
import sys
from queue import PriorityQueue

pygame.init()

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Tower Defense - MST Paths")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
GRAY = (128, 128, 128)
ORANGE = (255, 165, 0)
DARK_RED = (139, 0, 0)

class Village:
    def __init__(self, x, y, id):
        self.x = x
        self.y = y
        self.id = id
        self.connected_to = []
        self.radius = 15
        self.captured = False  # New property to track if this village is captured
    
    def draw(self, is_base=False, is_spawn=False):
        if is_base:
            pygame.draw.circle(screen, RED, (self.x, self.y), self.radius)
        elif is_spawn:
            pygame.draw.circle(screen, YELLOW, (self.x, self.y), self.radius)
        elif self.captured:  # Draw captured villages in a dark red color
            pygame.draw.circle(screen, DARK_RED, (self.x, self.y), self.radius)
        else:
            pygame.draw.circle(screen, GREEN, (self.x, self.y), self.radius)
        
        font = pygame.font.SysFont(None, 20)
        text = font.render(str(self.id), True, BLACK)
        screen.blit(text, (self.x - text.get_width() // 2, self.y - text.get_height() // 2))

class Edge:
    def __init__(self, start, end, weight):
        self.start = start
        self.end = end
        self.weight = weight

class Tower:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.level = 1
        self.radius = 100
        self.damage = 10
        self.attack_speed = 1.0
        self.attack_timer = 0
        self.cost = 100
        self.upgrade_cost = 75
        self.targets = []
    
    def draw(self):
        pygame.draw.circle(screen, (200, 200, 200, 100), (self.x, self.y), self.radius, 1)
        if self.level == 1:
            tower_color = BLUE
        elif self.level == 2:
            tower_color = PURPLE
        else:
            tower_color = ORANGE
        pygame.draw.circle(screen, tower_color, (self.x, self.y), 15)
        level_indicator = "+" * self.level
        font = pygame.font.SysFont(None, 20)
        text = font.render(level_indicator, True, WHITE)
        screen.blit(text, (self.x - text.get_width() // 2, self.y - text.get_height() // 2))
    
    def upgrade(self):
        if self.level < 3:
            self.level += 1
            self.radius += 20
            self.damage += 10
            self.attack_speed += 0.5
            return self.upgrade_cost
        return 0
    
    def can_attack(self, time_delta):
        self.attack_timer += time_delta
        if self.attack_timer >= 1.0 / self.attack_speed:
            self.attack_timer = 0
            return True
        return False
    
    def get_targets(self, enemies):
        self.targets = []
        for enemy in enemies:
            dist = math.sqrt((self.x - enemy.x) ** 2 + (self.y - enemy.y) ** 2)
            if dist <= self.radius:
                self.targets.append(enemy)
        return self.targets
    
    def attack(self, enemies):
        targets = self.get_targets(enemies)
        if targets:
            target = min(targets, key=lambda e: e.distance_traveled)
            target.health -= self.damage
            pygame.draw.line(screen, RED, (self.x, self.y), (target.x, target.y), 2)
            return target
        return None

class Enemy:
    def __init__(self, path, wave_number, target_village):
        self.path = path
        self.path_index = 0
        self.x = path[0][0]
        self.y = path[0][1]
        self.speed = 4.0 + wave_number * 0.2
        self.health = 50 + wave_number * 20
        self.max_health = self.health
        self.distance_traveled = 0
        self.radius = 10
        self.value = 20 + wave_number * 5
        self.edge_index = 0
        self.target_village = target_village  # Store the target village this enemy is heading to
        
    def move(self, time_delta):
        if self.path_index < len(self.path) - 1:
            target_x, target_y = self.path[self.path_index + 1]
            dx = target_x - self.x
            dy = target_y - self.y
            distance = math.sqrt(dx**2 + dy**2)
            if distance < self.speed * time_delta:
                self.x = target_x
                self.y = target_y
                self.distance_traveled += distance
                self.path_index += 1
            else:
                move_ratio = self.speed * time_delta / distance
                self.x += dx * move_ratio
                self.y += dy * move_ratio
                self.distance_traveled += self.speed * time_delta
    
    def draw(self):
        pygame.draw.circle(screen, RED, (int(self.x), int(self.y)), self.radius)
        health_percentage = self.health / self.max_health
        bar_width = 30
        health_width = max(0, int(bar_width * health_percentage))
        pygame.draw.rect(screen, RED, (int(self.x) - bar_width//2, int(self.y) - 20, bar_width, 5))
        pygame.draw.rect(screen, GREEN, (int(self.x) - bar_width//2, int(self.y) - 20, health_width, 5))
    
    def reached_end(self):
        return self.path_index >= len(self.path) - 1
        
    def is_dead(self):
        return self.health <= 0

class Game:
    def __init__(self):
        self.villages = []
        self.edges = []
        self.mst = []
        self.towers = []
        self.enemies = []
        self.gold = 300
        self.lives = 20
        self.wave = 0
        self.wave_timer = 0
        self.enemy_timer = 0
        self.enemies_to_spawn = 0
        self.level_started = False
        self.enemy_paths = {}  # Changed to a dictionary to store paths for each spawn point
        self.base_village = None
        self.spawn_village = None
        self.spawn_villages = []  # List to store all active spawn villages
        self.font = pygame.font.SysFont(None, 24)
        self.tower_selected = None
        self.difficulty_multiplier = 1.0  # Added to adjust difficulty as more spawns appear
        self.generate_map()
    
    def generate_map(self):
        self.villages = []
        self.edges = []
        self.mst = []
        num_villages = 15
        for i in range(num_villages):
            while True:
                x = random.randint(50, SCREEN_WIDTH - 50)
                y = random.randint(50, SCREEN_HEIGHT - 50)
                too_close = False
                for village in self.villages:
                    dist = math.sqrt((x - village.x) ** 2 + (y - village.y) ** 2)
                    if dist < 100:
                        too_close = True
                        break
                if not too_close:
                    break
            self.villages.append(Village(x, y, i))
        
        # Find two furthest villages for base and initial spawn
        max_distance = 0
        for i in range(len(self.villages)):
            for j in range(i + 1, len(self.villages)):
                dist = math.sqrt((self.villages[i].x - self.villages[j].x) ** 2 + (self.villages[i].y - self.villages[j].y) ** 2)
                if dist > max_distance:
                    max_distance = dist
                    self.base_village = self.villages[i]
                    self.spawn_village = self.villages[j]
        
        # Mark the initial spawn village as captured
        self.spawn_village.captured = True
        self.spawn_villages = [self.spawn_village]
        
        # Generate all edges between villages
        for i in range(len(self.villages)):
            for j in range(i + 1, len(self.villages)):
                village1 = self.villages[i]
                village2 = self.villages[j]
                distance = math.sqrt((village1.x - village2.x) ** 2 + (village1.y - village2.y) ** 2)
                self.edges.append(Edge(village1, village2, distance))
        
        self.edges.sort(key=lambda x: x.weight)
        self.mst = self.calculate_mst()
        self.calculate_enemy_paths()
    
    def calculate_mst(self):
        def find(parent, i):
            if parent[i] != i:
                parent[i] = find(parent, parent[i])
            return parent[i]
        
        def union(parent, rank, x, y):
            root_x = find(parent, x)
            root_y = find(parent, y)
            if root_x == root_y:
                return
            if rank[root_x] < rank[root_y]:
                parent[root_x] = root_y
            elif rank[root_x] > rank[root_y]:
                parent[root_y] = root_x
            else:
                parent[root_y] = root_x
                rank[root_x] += 1
        
        parent = {village.id: village.id for village in self.villages}
        rank = {village.id: 0 for village in self.villages}
        mst = []
        
        # Apply tower penalties to edges
        for edge in self.edges:
            tower_penalty = 0
            for tower in self.towers:
                edge_length = edge.weight
                mid_x = (edge.start.x + edge.end.x) / 2
                mid_y = (edge.start.y + edge.end.y) / 2
                if math.sqrt((tower.x - mid_x) ** 2 + (tower.y - mid_y) ** 2) < edge_length / 2:
                    tower_penalty = tower.level * 100
            adjusted_weight = edge.weight + tower_penalty
            
            if find(parent, edge.start.id) != find(parent, edge.end.id):
                mst.append(edge)
                union(parent, rank, edge.start.id, edge.end.id)
                edge.start.connected_to.append(edge.end)
                edge.end.connected_to.append(edge.start)
        
        return mst
    
    def calculate_enemy_paths(self):
        def find_path(start, end):
            visited = {village.id: False for village in self.villages}
            queue = [[start]]
            visited[start.id] = True
            while queue:
                path = queue.pop(0)
                current = path[-1]
                if current.id == end.id:
                    return path
                for neighbor in current.connected_to:
                    if not visited[neighbor.id]:
                        new_path = list(path)
                        new_path.append(neighbor)
                        queue.append(new_path)
                        visited[neighbor.id] = True
            return []
        
        # Clear the existing paths
        self.enemy_paths = {}
        
        # Calculate paths from each spawn village to the base
        for spawn in self.spawn_villages:
            village_path = find_path(spawn, self.base_village)
            coords_path = []
            for village in village_path:
                coords_path.append((village.x, village.y))
            
            if coords_path:  # Only add valid paths
                self.enemy_paths[spawn.id] = coords_path
            
        # If no valid paths, regenerate the map
        if not self.enemy_paths:
            self.generate_map()
    
    def start_wave(self):
        self.wave += 1
        # Scale enemies per spawn point based on number of spawn points and wave
        enemies_per_spawn = 3 + self.wave
        self.enemies_to_spawn = enemies_per_spawn * len(self.spawn_villages)
        self.enemy_timer = 0
        self.wave_timer = 0
        self.level_started = True
        # Increase difficulty as the game progresses
        self.difficulty_multiplier = 1.0 + (len(self.spawn_villages) - 1) * 0.2
    
    def update(self, time_delta):
        if self.level_started:
            self.wave_timer += time_delta
            self.enemy_timer += time_delta
            
            # Spawn enemies from captured villages
            if self.enemies_to_spawn > 0 and self.enemy_timer >= 1.0:
                # Choose a random spawn point from the available spawns
                if self.spawn_villages:
                    spawn_village = random.choice(self.spawn_villages)
                    # Make sure we have a path from this spawn to the base
                    if spawn_village.id in self.enemy_paths:
                        path = self.enemy_paths[spawn_village.id]
                        # Create a new enemy with this path
                        self.enemies.append(Enemy(path, self.wave, self.base_village))
                        self.enemies_to_spawn -= 1
                        self.enemy_timer = 0
            
            # Update enemy positions and check for base captures
            for enemy in self.enemies[:]:
                enemy.move(time_delta)
                
                # Check if enemy reached the base
                if enemy.reached_end():
                    self.enemies.remove(enemy)
                    self.lives -= 1
                # Check if enemy is dead
                elif enemy.is_dead():
                    self.enemies.remove(enemy)
                    self.gold += enemy.value
                # Check if enemy is at a village that isn't already captured
                else:
                    # Check if enemy is at any uncaptured village
                    for village in self.villages:
                        if not village.captured and village != self.base_village:
                            if math.sqrt((enemy.x - village.x) ** 2 + (enemy.y - village.y) ** 2) < village.radius:
                                village.captured = True
                                if village not in self.spawn_villages:
                                    self.spawn_villages.append(village)
                                    # Recalculate paths when a new village is captured
                                    self.calculate_enemy_paths()
            
            # Process tower attacks
            for tower in self.towers:
                if tower.can_attack(time_delta):
                    tower.attack(self.enemies)
            
            # Check if wave is over
            if self.enemies_to_spawn == 0 and not self.enemies:
                self.level_started = False
                self.recalculate_paths()
        
        # Check for game over
        if self.lives <= 0:
            self.reset_game()
    
    def recalculate_paths(self):
        old_mst = self.mst
        for village in self.villages:
            village.connected_to = []
        self.mst = self.calculate_mst()
        self.calculate_enemy_paths()
    
    def reset_game(self):
        self.villages = []
        self.edges = []
        self.mst = []
        self.towers = []
        self.enemies = []
        self.gold = 300
        self.lives = 20
        self.wave = 0
        self.wave_timer = 0
        self.enemy_timer = 0
        self.enemies_to_spawn = 0
        self.level_started = False
        self.enemy_paths = {}
        self.base_village = None
        self.spawn_village = None
        self.spawn_villages = []
        self.difficulty_multiplier = 1.0
        self.generate_map()
    
    def draw(self):
        screen.fill(BLACK)
        
        # Draw all edges from the MST to show all possible paths
        for edge in self.mst:
            pygame.draw.line(screen, GRAY, (edge.start.x, edge.start.y), (edge.end.x, edge.end.y), 2)
        
        # Draw active enemy paths in different colors
        for spawn_id, path in self.enemy_paths.items():
            if len(path) > 1:
                for i in range(len(path) - 1):
                    pygame.draw.line(screen, ORANGE, path[i], path[i+1], 3)
        
        # Draw villages
        for village in self.villages:
            is_base = village == self.base_village
            is_spawn = village == self.spawn_village
            village.draw(is_base, is_spawn)
        
        # Draw towers and enemies
        for tower in self.towers:
            tower.draw()
        
        for enemy in self.enemies:
            enemy.draw()
        
        # Draw UI elements
        gold_text = self.font.render(f"Gold: {self.gold}", True, YELLOW)
        lives_text = self.font.render(f"Lives: {self.lives}", True, RED)
        wave_text = self.font.render(f"Wave: {self.wave}", True, WHITE)
        spawn_text = self.font.render(f"Enemy Bases: {len(self.spawn_villages)}", True, DARK_RED)
        
        screen.blit(gold_text, (10, 10))
        screen.blit(lives_text, (10, 40))
        screen.blit(wave_text, (10, 70))
        screen.blit(spawn_text, (10, 100))
        
        if not self.level_started and self.wave > 0:
            next_wave_text = self.font.render("Press SPACE to start next wave", True, WHITE)
            screen.blit(next_wave_text, (SCREEN_WIDTH // 2 - next_wave_text.get_width() // 2, 20))
        elif self.wave == 0:
            first_wave_text = self.font.render("Press SPACE to start game", True, WHITE)
            screen.blit(first_wave_text, (SCREEN_WIDTH // 2 - first_wave_text.get_width() // 2, 20))
        
        if self.tower_selected is not None:
            tower = self.towers[self.tower_selected]
            pygame.draw.circle(screen, WHITE, (tower.x, tower.y), tower.radius + 5, 2)
            if tower.level < 3:
                upgrade_text = self.font.render(f"Right-click to upgrade ({tower.upgrade_cost} gold)", True, WHITE)
                screen.blit(upgrade_text, (SCREEN_WIDTH // 2 - upgrade_text.get_width() // 2, SCREEN_HEIGHT - 30))
            else:
                max_level_text = self.font.render("Tower at maximum level", True, WHITE)
                screen.blit(max_level_text, (SCREEN_WIDTH // 2 - max_level_text.get_width() // 2, SCREEN_HEIGHT - 30))
        
        pygame.display.flip()
    
    def handle_click(self, pos, button):
        x, y = pos
        # Check if clicked on an existing tower
        for i, tower in enumerate(self.towers):
            if math.sqrt((x - tower.x) ** 2 + (y - tower.y) ** 2) < 15:
                self.tower_selected = i
                if button == 3:  # Right click to upgrade
                    if tower.level < 3 and self.gold >= tower.upgrade_cost:
                        self.gold -= tower.upgrade_cost
                        tower.upgrade()
                        self.recalculate_paths()
                return
        
        if button == 1:  # Left click to place tower
            self.tower_selected = None
            # Check if clicked near a village (can't place tower there)
            for village in self.villages:
                if math.sqrt((x - village.x) ** 2 + (y - village.y) ** 2) < village.radius + 20:
                    return
            # Check if clicked near an existing tower
            for tower in self.towers:
                if math.sqrt((x - tower.x) ** 2 + (y - tower.y) ** 2) < 30:
                    return
            
            # Place a new tower if can afford it
            tower_cost = 100
            if self.gold >= tower_cost:
                self.gold -= tower_cost
                self.towers.append(Tower(x, y))
                self.recalculate_paths()

def main():
    clock = pygame.time.Clock()
    game = Game()
    running = True
    while running:
        time_delta = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not game.level_started:
                    game.start_wave()
                elif event.key == pygame.K_r:
                    game.reset_game()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                game.handle_click(pygame.mouse.get_pos(), event.button)
        game.update(time_delta)
        game.draw()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
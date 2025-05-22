import tkinter as tk
from tkinter import ttk, messagebox
import heapq
import random
from collections import deque
from enum import Enum
import math

class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

class PathfindingVisualizer:
    def __init__(self, root):
        self.root = root
        self.root.title("Snake AI Pathfinding Visualizer")
        self.root.geometry("1400x900")
        
        # Grid settings
        self.grid_width = 25
        self.grid_height = 20
        self.cell_size = 25
        
        # Grid state
        self.grid = {}  # (x, y): cell_type
        self.snake_body = [(12, 10), (11, 10), (10, 10)]  # Default snake
        self.food_pos = (20, 15)
        self.walls = set()
        
        # Algorithm state
        self.algorithm = "Dijkstra"
        self.start_pos = self.snake_body[0]
        self.goal_pos = self.food_pos
        self.current_step = 0
        self.is_running = False
        self.path_found = []
        
        # Visualization state
        self.visited = set()
        self.frontier = {}  # pos: (distance, previous)
        self.current_node = None
        self.final_path = []
        
        # Colors
        self.colors = {
            'empty': '#F8F9FA',
            'snake_head': '#2E8B57',
            'snake_body': '#90EE90',
            'food': '#FF4444',
            'wall': '#8B4513',
            'start': '#FF6B6B',
            'goal': '#4ECDC4',
            'visited': '#FFE66D',
            'frontier': '#A8E6CF',
            'current': '#FF1744',
            'path': '#9C27B0',
            'grid_line': '#E0E0E0'
        }
        
        self.setup_ui()
        self.reset_visualization()
        
    def setup_ui(self):
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Control panel
        control_frame = ttk.LabelFrame(main_frame, text="Controls", padding=10)
        control_frame.pack(side=tk.TOP, fill=tk.X, pady=(0, 10))
        
        # Algorithm selection
        algo_frame = ttk.Frame(control_frame)
        algo_frame.pack(side=tk.LEFT, padx=(0, 20))
        ttk.Label(algo_frame, text="Algorithm:").pack(side=tk.LEFT)
        self.algo_var = tk.StringVar(value="Dijkstra")
        algo_combo = ttk.Combobox(algo_frame, textvariable=self.algo_var, 
                                 values=["Dijkstra", "BFS", "A*"], state="readonly", width=10)
        algo_combo.pack(side=tk.LEFT, padx=(5, 0))
        algo_combo.bind("<<ComboboxSelected>>", self.on_algorithm_change)
        
        # Control buttons
        btn_frame = ttk.Frame(control_frame)
        btn_frame.pack(side=tk.LEFT, padx=(0, 20))
        
        ttk.Button(btn_frame, text="Reset", command=self.reset_visualization).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Step", command=self.step_forward).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Auto Run", command=self.auto_run).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Stop", command=self.stop_auto_run).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Generate Walls", command=self.generate_walls).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Clear Walls", command=self.clear_walls).pack(side=tk.LEFT, padx=2)
        
        # Speed control
        speed_frame = ttk.Frame(control_frame)
        speed_frame.pack(side=tk.LEFT)
        ttk.Label(speed_frame, text="Speed:").pack(side=tk.LEFT)
        self.speed_var = tk.DoubleVar(value=2.0)
        speed_scale = ttk.Scale(speed_frame, from_=0.5, to=5.0, variable=self.speed_var, 
                               orient=tk.HORIZONTAL, length=100)
        speed_scale.pack(side=tk.LEFT, padx=(5, 0))
        
        # Main content area
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Canvas area
        canvas_frame = ttk.LabelFrame(content_frame, text="Pathfinding Visualization")
        canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Canvas with scrollbars
        self.canvas = tk.Canvas(canvas_frame, bg='white', width=700, height=600)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        
        # Info panel
        info_frame = ttk.Frame(content_frame)
        info_frame.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Algorithm info
        algo_info_frame = ttk.LabelFrame(info_frame, text="Algorithm Info")
        algo_info_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.info_text = tk.Text(algo_info_frame, width=45, height=15, wrap=tk.WORD, font=('Consolas', 9))
        info_scrollbar = ttk.Scrollbar(algo_info_frame, orient=tk.VERTICAL, command=self.info_text.yview)
        self.info_text.configure(yscrollcommand=info_scrollbar.set)
        self.info_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        info_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Step info
        step_frame = ttk.LabelFrame(info_frame, text="Current Step")
        step_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.step_label = ttk.Label(step_frame, text="Step: 0")
        self.step_label.pack(anchor=tk.W, padx=5, pady=2)
        
        self.current_label = ttk.Label(step_frame, text="Current: None")
        self.current_label.pack(anchor=tk.W, padx=5, pady=2)
        
        self.frontier_label = ttk.Label(step_frame, text="Frontier: 0 nodes")
        self.frontier_label.pack(anchor=tk.W, padx=5, pady=2)
        
        self.visited_label = ttk.Label(step_frame, text="Visited: 0 nodes")
        self.visited_label.pack(anchor=tk.W, padx=5, pady=2)
        
        self.path_label = ttk.Label(step_frame, text="Path: None")
        self.path_label.pack(anchor=tk.W, padx=5, pady=2)
        
        # Legend
        legend_frame = ttk.LabelFrame(info_frame, text="Legend")
        legend_frame.pack(fill=tk.X)
        
        legend_items = [
            ("Snake Head", self.colors['snake_head']),
            ("Snake Body", self.colors['snake_body']),
            ("Food (Goal)", self.colors['food']),
            ("Wall", self.colors['wall']),
            ("Current Node", self.colors['current']),
            ("Visited", self.colors['visited']),
            ("Frontier", self.colors['frontier']),
            ("Final Path", self.colors['path'])
        ]
        
        for i, (text, color) in enumerate(legend_items):
            frame = ttk.Frame(legend_frame)
            frame.pack(fill=tk.X, padx=5, pady=1)
            canvas = tk.Canvas(frame, width=15, height=15, bg=color, highlightthickness=1)
            canvas.pack(side=tk.LEFT)
            ttk.Label(frame, text=text, font=('Arial', 8)).pack(side=tk.LEFT, padx=(5, 0))
    
    def wrap_position(self, x, y):
        """Handle position wrapping like in the snake game"""
        return x % self.grid_width, y % self.grid_height
    
    def get_neighbors(self, pos):
        """Get all valid neighbor positions with wrapping"""
        x, y = pos
        neighbors = []
        
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            new_x, new_y = self.wrap_position(x + dx, y + dy)
            neighbors.append((new_x, new_y))
        
        return neighbors
    
    def heuristic(self, pos1, pos2):
        """Manhattan distance with wrapping consideration"""
        x1, y1 = pos1
        x2, y2 = pos2
        
        # Consider wrapping in both directions
        dx = min(abs(x2 - x1), self.grid_width - abs(x2 - x1))
        dy = min(abs(y2 - y1), self.grid_height - abs(y2 - y1))
        
        return dx + dy
    
    def is_obstacle(self, pos):
        """Check if position is an obstacle"""
        return pos in self.walls or pos in self.snake_body[1:]  # Don't include head
    
    def dijkstra_step(self):
        """Perform one step of Dijkstra's algorithm"""
        if not hasattr(self, 'priority_queue'):
            # Initialize
            self.priority_queue = [(0, self.start_pos, [])]
            self.distances = {self.start_pos: 0}
            self.visited = set()
            self.frontier = {self.start_pos: (0, None)}
            heapq.heapify(self.priority_queue)
        
        if not self.priority_queue:
            return False  # No more nodes to explore
        
        current_dist, current_pos, path = heapq.heappop(self.priority_queue)
        
        if current_pos in self.visited:
            return True  # Continue with next iteration
        
        self.visited.add(current_pos)
        self.current_node = current_pos
        
        # Check if we reached the goal
        if current_pos == self.goal_pos:
            self.final_path = path + [current_pos]
            direction = self.path_to_direction(self.final_path)
            self.path_label.config(text=f"Path: {direction} ({len(self.final_path)} steps)")
            return False  # Found path, stop
        
        # Explore neighbors
        for neighbor in self.get_neighbors(current_pos):
            if neighbor not in self.visited and not self.is_obstacle(neighbor):
                new_dist = current_dist + 1
                
                if neighbor not in self.distances or new_dist < self.distances[neighbor]:
                    self.distances[neighbor] = new_dist
                    self.frontier[neighbor] = (new_dist, current_pos)
                    new_path = path + [current_pos]
                    heapq.heappush(self.priority_queue, (new_dist, neighbor, new_path))
        
        return True
    
    def bfs_step(self):
        """Perform one step of BFS"""
        if not hasattr(self, 'queue'):
            # Initialize
            self.queue = deque([(self.start_pos, [])])
            self.visited = {self.start_pos}
            self.frontier = {self.start_pos: (0, None)}
        
        if not self.queue:
            return False
        
        current_pos, path = self.queue.popleft()
        self.current_node = current_pos
        
        # Check if we reached the goal
        if current_pos == self.goal_pos:
            self.final_path = path + [current_pos]
            direction = self.path_to_direction(self.final_path)
            self.path_label.config(text=f"Path: {direction} ({len(self.final_path)} steps)")
            return False
        
        # Explore neighbors
        for neighbor in self.get_neighbors(current_pos):
            if neighbor not in self.visited and not self.is_obstacle(neighbor):
                self.visited.add(neighbor)
                self.frontier[neighbor] = (len(path) + 1, current_pos)
                new_path = path + [current_pos]
                self.queue.append((neighbor, new_path))
        
        return True
    
    def astar_step(self):
        """Perform one step of A* algorithm"""
        if not hasattr(self, 'priority_queue'):
            # Initialize
            start_h = self.heuristic(self.start_pos, self.goal_pos)
            self.priority_queue = [(start_h, 0, self.start_pos, [])]
            self.g_scores = {self.start_pos: 0}
            self.visited = set()
            self.frontier = {self.start_pos: (0, None)}
            heapq.heapify(self.priority_queue)
        
        if not self.priority_queue:
            return False
        
        f_score, g_score, current_pos, path = heapq.heappop(self.priority_queue)
        
        if current_pos in self.visited:
            return True
        
        self.visited.add(current_pos)
        self.current_node = current_pos
        
        # Check if we reached the goal
        if current_pos == self.goal_pos:
            self.final_path = path + [current_pos]
            direction = self.path_to_direction(self.final_path)
            self.path_label.config(text=f"Path: {direction} ({len(self.final_path)} steps)")
            return False
        
        # Explore neighbors
        for neighbor in self.get_neighbors(current_pos):
            if neighbor not in self.visited and not self.is_obstacle(neighbor):
                tentative_g = g_score + 1
                
                if neighbor not in self.g_scores or tentative_g < self.g_scores[neighbor]:
                    self.g_scores[neighbor] = tentative_g
                    h_score = self.heuristic(neighbor, self.goal_pos)
                    f_score = tentative_g + h_score
                    self.frontier[neighbor] = (tentative_g, current_pos)
                    new_path = path + [current_pos]
                    heapq.heappush(self.priority_queue, (f_score, tentative_g, neighbor, new_path))
        
        return True
    
    def path_to_direction(self, path):
        """Convert path to first direction for snake movement"""
        if len(path) < 2:
            return "No movement needed"
        
        start = path[0]
        next_pos = path[1]
        
        dx = (next_pos[0] - start[0]) % self.grid_width
        dy = (next_pos[1] - start[1]) % self.grid_height
        
        # Handle wrapping
        if dx == 1 or dx == -(self.grid_width - 1):
            return "RIGHT"
        elif dx == self.grid_width - 1 or dx == -1:
            return "LEFT"
        elif dy == 1 or dy == -(self.grid_height - 1):
            return "DOWN"
        elif dy == self.grid_height - 1 or dy == -1:
            return "UP"
        
        return "UNKNOWN"
    
    def step_forward(self):
        """Perform one step of the selected algorithm"""
        if self.algorithm == "Dijkstra":
            has_more = self.dijkstra_step()
        elif self.algorithm == "BFS":
            has_more = self.bfs_step()
        elif self.algorithm == "A*":
            has_more = self.astar_step()
        else:
            has_more = False
        
        self.current_step += 1
        self.update_display()
        
        if not has_more:
            self.is_running = False
        
        return has_more
    
    def auto_run(self):
        """Start automatic stepping"""
        if not self.is_running:
            self.is_running = True
            self.run_step()
    
    def run_step(self):
        """Run one step automatically"""
        if self.is_running:
            has_more = self.step_forward()
            if has_more:
                delay = int(200 / self.speed_var.get())
                self.root.after(delay, self.run_step)
            else:
                self.is_running = False
    
    def stop_auto_run(self):
        """Stop automatic running"""
        self.is_running = False
    
    def reset_visualization(self):
        """Reset the visualization state"""
        self.current_step = 0
        self.visited = set()
        self.frontier = {}
        self.current_node = None
        self.final_path = []
        self.is_running = False
        
        # Clear algorithm-specific data
        if hasattr(self, 'priority_queue'):
            delattr(self, 'priority_queue')
        if hasattr(self, 'queue'):
            delattr(self, 'queue')
        if hasattr(self, 'distances'):
            delattr(self, 'distances')
        if hasattr(self, 'g_scores'):
            delattr(self, 'g_scores')
        
        self.start_pos = self.snake_body[0]
        self.goal_pos = self.food_pos
        
        self.update_display()
        self.update_info()
    
    def generate_walls(self):
        """Generate random walls"""
        self.walls.clear()
        
        # Generate 15-25 random walls
        num_walls = random.randint(15, 25)
        
        for _ in range(num_walls * 3):  # Try more times to place walls
            if len(self.walls) >= num_walls:
                break
            
            x = random.randint(0, self.grid_width - 1)
            y = random.randint(0, self.grid_height - 1)
            pos = (x, y)
            
            # Don't place walls on snake, food, or existing walls
            if (pos not in self.snake_body and 
                pos != self.food_pos and 
                pos not in self.walls):
                self.walls.add(pos)
        
        self.reset_visualization()
    
    def clear_walls(self):
        """Clear all walls"""
        self.walls.clear()
        self.reset_visualization()
    
    def on_canvas_click(self, event):
        """Handle canvas clicks to toggle walls"""
        x = event.x // self.cell_size
        y = event.y // self.cell_size
        
        if 0 <= x < self.grid_width and 0 <= y < self.grid_height:
            pos = (x, y)
            
            if pos not in self.snake_body and pos != self.food_pos:
                if pos in self.walls:
                    self.walls.remove(pos)
                else:
                    self.walls.add(pos)
                
                self.reset_visualization()
    
    def on_canvas_drag(self, event):
        """Handle canvas dragging to draw walls"""
        self.on_canvas_click(event)
    
    def draw_grid(self):
        """Draw the grid visualization"""
        self.canvas.delete("all")
        
        # Draw grid lines
        for x in range(self.grid_width + 1):
            x_pos = x * self.cell_size
            self.canvas.create_line(x_pos, 0, x_pos, self.grid_height * self.cell_size, 
                                  fill=self.colors['grid_line'], width=1)
        
        for y in range(self.grid_height + 1):
            y_pos = y * self.cell_size
            self.canvas.create_line(0, y_pos, self.grid_width * self.cell_size, y_pos, 
                                  fill=self.colors['grid_line'], width=1)
        
        # Draw wrapping indicators (purple border)
        border_width = 3
        self.canvas.create_rectangle(0, 0, self.grid_width * self.cell_size, 
                                   self.grid_height * self.cell_size, 
                                   outline='purple', width=border_width, fill='')
        
        # Draw cells
        for x in range(self.grid_width):
            for y in range(self.grid_height):
                pos = (x, y)
                rect_x1 = x * self.cell_size + 1
                rect_y1 = y * self.cell_size + 1
                rect_x2 = (x + 1) * self.cell_size - 1
                rect_y2 = (y + 1) * self.cell_size - 1
                
                color = self.colors['empty']
                
                # Determine cell color based on state
                if pos == self.snake_body[0]:  # Snake head
                    color = self.colors['snake_head']
                elif pos in self.snake_body[1:]:  # Snake body
                    color = self.colors['snake_body']
                elif pos == self.food_pos:  # Food
                    color = self.colors['food']
                elif pos in self.walls:  # Wall
                    color = self.colors['wall']
                elif pos == self.current_node:  # Current node being processed
                    color = self.colors['current']
                elif pos in self.final_path:  # Final path
                    color = self.colors['path']
                elif pos in self.visited:  # Visited nodes
                    color = self.colors['visited']
                elif pos in self.frontier:  # Frontier nodes
                    color = self.colors['frontier']
                
                self.canvas.create_rectangle(rect_x1, rect_y1, rect_x2, rect_y2, 
                                           fill=color, outline='', width=0)
                
                # Add text for special cells
                center_x = x * self.cell_size + self.cell_size // 2
                center_y = y * self.cell_size + self.cell_size // 2
                
                if pos == self.snake_body[0]:
                    self.canvas.create_text(center_x, center_y, text="S", 
                                          fill="white", font=('Arial', 8, 'bold'))
                elif pos == self.food_pos:
                    self.canvas.create_text(center_x, center_y, text="F", 
                                          fill="white", font=('Arial', 8, 'bold'))
                elif pos in self.frontier and pos not in self.visited:
                    dist, _ = self.frontier[pos]
                    self.canvas.create_text(center_x, center_y, text=str(dist), 
                                          fill="black", font=('Arial', 6))
    
    def update_display(self):
        """Update the visual display"""
        self.draw_grid()
        
        # Update labels
        self.step_label.config(text=f"Step: {self.current_step}")
        self.current_label.config(text=f"Current: {self.current_node}")
        self.frontier_label.config(text=f"Frontier: {len(self.frontier)} nodes")
        self.visited_label.config(text=f"Visited: {len(self.visited)} nodes")
        
        if self.final_path:
            direction = self.path_to_direction(self.final_path)
            self.path_label.config(text=f"Path: {direction} ({len(self.final_path)} steps)")
        else:
            self.path_label.config(text="Path: Searching...")
    
    def update_info(self):
        """Update the algorithm information panel"""
        self.info_text.delete(1.0, tk.END)
        
        if self.algorithm == "Dijkstra":
            info = """DIJKSTRA'S ALGORITHM

A graph search algorithm that finds the shortest path between nodes.

Key Features:
- Guarantees shortest path
- Uses priority queue (min-heap)
- Explores nodes in order of distance from start
- Works with weighted graphs

In Snake AI Context:
- Each grid cell is a node
- All edges have weight 1 (uniform cost)
- Handles grid wrapping (teleportation)
- Avoids snake body and walls

Steps:
1. Start with source in priority queue
2. Pop node with minimum distance
3. Mark as visited
4. Update distances to neighbors
5. Add unvisited neighbors to queue
6. Repeat until goal found

Time Complexity: O(V log V + E)
Space Complexity: O(V)

Current Status:"""
        
        elif self.algorithm == "BFS":
            info = """BREADTH-FIRST SEARCH (BFS)

A graph traversal algorithm that explores neighbors level by level.

Key Features:
- Guarantees shortest path in unweighted graphs
- Uses queue (FIFO)
- Explores all nodes at distance k before distance k+1
- Simple and intuitive

In Snake AI Context:
- Perfect for uniform grid movement
- All moves have equal cost
- Handles grid wrapping
- Avoids obstacles (walls, snake body)

Steps:
1. Start with source in queue
2. Dequeue front node
3. Check if it's the goal
4. Add unvisited neighbors to queue
5. Mark neighbors as visited
6. Repeat until goal found

Time Complexity: O(V + E)
Space Complexity: O(V)

Current Status:"""
        
        elif self.algorithm == "A*":
            info = """A* ALGORITHM

An informed search algorithm using heuristics to guide exploration.

Key Features:
- Guarantees optimal path with admissible heuristic
- Uses f(n) = g(n) + h(n)
- g(n): actual cost from start
- h(n): heuristic estimate to goal
- More efficient than Dijkstra

In Snake AI Context:
- Heuristic: Manhattan distance with wrapping
- Considers shortest wrapped distance
- Prioritizes nodes closer to food
- Handles obstacles and wrapping

Heuristic Function:
For positions (x1,y1) and (x2,y2):
dx = min(|x2-x1|, grid_width - |x2-x1|)
dy = min(|y2-y1|, grid_height - |y2-y1|)
h = dx + dy

Steps:
1. Maintain open set with f-scores
2. Pick node with lowest f-score
3. Move to closed set
4. Update neighbors' g and f scores
5. Repeat until goal found

Time Complexity: O(b^d) where b=branching factor, d=depth
Space Complexity: O(b^d)

Current Status:"""
        
        # Add current algorithm state
        if hasattr(self, 'visited'):
            info += f"\n\nNodes Visited: {len(self.visited)}"
            info += f"\nNodes in Frontier: {len(self.frontier)}"
            
            if self.current_node:
                info += f"\nCurrent Node: {self.current_node}"
                
                if self.current_node in self.frontier:
                    dist, prev = self.frontier[self.current_node]
                    info += f"\nDistance from start: {dist}"
                    if prev:
                        info += f"\nPrevious node: {prev}"
            
            if self.final_path:
                info += f"\n\nPATH FOUND!"
                info += f"\nPath length: {len(self.final_path)}"
                info += f"\nNext direction: {self.path_to_direction(self.final_path)}"
                info += f"\nPath: {' → '.join(map(str, self.final_path[:10]))}"
                if len(self.final_path) > 10:
                    info += "..."
        
        self.info_text.insert(1.0, info)
    
    def on_algorithm_change(self, event=None):
        """Handle algorithm selection change"""
        self.algorithm = self.algo_var.get()
        self.reset_visualization()
        self.update_info()

def main():
    root = tk.Tk()
    app = PathfindingVisualizer(root)
    root.mainloop()

if __name__ == "__main__":
    main()
import tkinter as tk
from tkinter import ttk, messagebox
import math
import time
from collections import deque
import random

class GraphVisualizer:
    def __init__(self, root):
        self.root = root
        self.root.title("Interactive DFS/BFS Step-by-Step Visualizer")
        self.root.geometry("1200x800")
        
        # Graph data
        self.vertices = []
        self.edges = []
        self.adj_list = {}
        self.num_vertices = 8
        
        # Visualization state
        self.visited = set()
        self.current_vertex = None
        self.stack = []  # For DFS
        self.queue = deque()  # For BFS
        self.path = []
        self.step_count = 0
        self.is_running = False
        self.algorithm = "DFS"
        
        # Colors
        self.colors = {
            'unvisited': '#E8F4FD',
            'current': '#FF6B6B',
            'visited': '#4ECDC4',
            'in_stack': '#FFE66D',
            'in_queue': '#A8E6CF',
            'edge': '#34495E',
            'traversed_edge': '#E74C3C'
        }
        
        self.setup_ui()
        self.generate_random_graph()
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Control panel
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(side=tk.TOP, fill=tk.X, pady=(0, 10))
        
        # Algorithm selection
        ttk.Label(control_frame, text="Algorithm:").pack(side=tk.LEFT, padx=5)
        self.algorithm_var = tk.StringVar(value="DFS")
        algorithm_combo = ttk.Combobox(control_frame, textvariable=self.algorithm_var, 
                                     values=["DFS", "BFS"], state="readonly", width=10)
        algorithm_combo.pack(side=tk.LEFT, padx=5)
        algorithm_combo.bind("<<ComboboxSelected>>", self.on_algorithm_change)
        
        # Vertex count
        ttk.Label(control_frame, text="Vertices:").pack(side=tk.LEFT, padx=(20, 5))
        self.vertex_var = tk.IntVar(value=8)
        vertex_spinner = tk.Spinbox(control_frame, from_=5, to=15, textvariable=self.vertex_var, 
                                   width=5, command=self.on_vertex_count_change)
        vertex_spinner.pack(side=tk.LEFT, padx=5)
        
        # Control buttons
        ttk.Button(control_frame, text="Generate New Graph", 
                  command=self.generate_random_graph).pack(side=tk.LEFT, padx=(20, 5))
        ttk.Button(control_frame, text="Reset", command=self.reset).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Step Forward", command=self.step_forward).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Auto Run", command=self.auto_run).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Stop", command=self.stop_auto_run).pack(side=tk.LEFT, padx=5)
        
        # Speed control
        ttk.Label(control_frame, text="Speed:").pack(side=tk.LEFT, padx=(20, 5))
        self.speed_var = tk.DoubleVar(value=1.0)
        speed_scale = ttk.Scale(control_frame, from_=0.1, to=3.0, variable=self.speed_var, 
                               orient=tk.HORIZONTAL, length=100)
        speed_scale.pack(side=tk.LEFT, padx=5)
        
        # Canvas frame
        canvas_frame = ttk.Frame(main_frame)
        canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Canvas for graph visualization
        self.canvas = tk.Canvas(canvas_frame, bg='white', width=700, height=600)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Info panel
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        
        # Algorithm info
        self.info_text = tk.Text(info_frame, width=40, height=15, wrap=tk.WORD)
        self.info_text.pack(fill=tk.BOTH, expand=True)
        
        # Step info
        step_frame = ttk.LabelFrame(info_frame, text="Current Step")
        step_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.step_label = ttk.Label(step_frame, text="Step: 0")
        self.step_label.pack(anchor=tk.W, padx=5, pady=2)
        
        self.current_label = ttk.Label(step_frame, text="Current: None")
        self.current_label.pack(anchor=tk.W, padx=5, pady=2)
        
        self.stack_queue_label = ttk.Label(step_frame, text="Stack/Queue: []")
        self.stack_queue_label.pack(anchor=tk.W, padx=5, pady=2)
        
        self.visited_label = ttk.Label(step_frame, text="Visited: []")
        self.visited_label.pack(anchor=tk.W, padx=5, pady=2)
        
        # Legend
        legend_frame = ttk.LabelFrame(info_frame, text="Legend")
        legend_frame.pack(fill=tk.X, pady=(10, 0))
        
        legend_items = [
            ("Unvisited", self.colors['unvisited']),
            ("Current", self.colors['current']),
            ("Visited", self.colors['visited']),
            ("In Stack/Queue", self.colors['in_stack']),
        ]
        
        for text, color in legend_items:
            frame = ttk.Frame(legend_frame)
            frame.pack(fill=tk.X, padx=5, pady=2)
            canvas = tk.Canvas(frame, width=20, height=20, bg=color, highlightthickness=1)
            canvas.pack(side=tk.LEFT)
            ttk.Label(frame, text=text).pack(side=tk.LEFT, padx=(5, 0))
    
    def generate_random_graph(self):
        self.num_vertices = self.vertex_var.get()
        self.vertices = []
        self.edges = []
        self.adj_list = {i: [] for i in range(self.num_vertices)}
        
        # Position vertices in a circle
        center_x, center_y = 350, 300
        radius = min(250, 200)
        
        for i in range(self.num_vertices):
            angle = 2 * math.pi * i / self.num_vertices
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            self.vertices.append((x, y, i))
        
        # Generate random edges (ensuring connectivity)
        # First, create a spanning tree to ensure connectivity
        for i in range(1, self.num_vertices):
            parent = random.randint(0, i - 1)
            self.adj_list[parent].append(i)
            self.adj_list[i].append(parent)
            self.edges.append((parent, i))
        
        # Add some random edges
        edge_probability = 0.3
        for i in range(self.num_vertices):
            for j in range(i + 1, self.num_vertices):
                if j not in self.adj_list[i] and random.random() < edge_probability:
                    self.adj_list[i].append(j)
                    self.adj_list[j].append(i)
                    self.edges.append((i, j))
        
        self.reset()
        self.draw_graph()
        self.update_info()
    
    def reset(self):
        self.visited = set()
        self.current_vertex = None
        self.stack = []
        self.queue = deque()
        self.path = []
        self.step_count = 0
        self.is_running = False
        self.algorithm = self.algorithm_var.get()
        
        if self.algorithm == "DFS":
            self.stack = [0]  # Start from vertex 0
        else:
            self.queue = deque([0])
            self.visited.add(0)
        
        self.draw_graph()
        self.update_labels()
        self.update_info()
    
    def step_forward(self):
        if self.algorithm == "DFS":
            self.dfs_step()
        else:
            self.bfs_step()
        
        self.draw_graph()
        self.update_labels()
    
    def dfs_step(self):
        if not self.stack:
            return False
        
        current = self.stack.pop()
        
        if current not in self.visited:
            self.visited.add(current)
            self.current_vertex = current
            self.path.append(current)
            self.step_count += 1
            
            # Add unvisited neighbors to stack (in reverse order for left-to-right traversal)
            neighbors = sorted(self.adj_list[current], reverse=True)
            for neighbor in neighbors:
                if neighbor not in self.visited:
                    self.stack.append(neighbor)
        
        return len(self.stack) > 0 or len(self.visited) < self.num_vertices
    
    def bfs_step(self):
        if not self.queue:
            return False
        
        current = self.queue.popleft()
        self.current_vertex = current
        self.path.append(current)
        self.step_count += 1
        
        # Add unvisited neighbors to queue
        neighbors = sorted(self.adj_list[current])
        for neighbor in neighbors:
            if neighbor not in self.visited:
                self.visited.add(neighbor)
                self.queue.append(neighbor)
        
        return len(self.queue) > 0
    
    def auto_run(self):
        if not self.is_running:
            self.is_running = True
            self.run_step()
    
    def run_step(self):
        if self.is_running:
            has_more = self.step_forward()
            if has_more:
                delay = int(1000 / self.speed_var.get())
                self.root.after(delay, self.run_step)
            else:
                self.is_running = False
    
    def stop_auto_run(self):
        self.is_running = False
    
    def draw_graph(self):
        self.canvas.delete("all")
        
        # Draw edges
        for i, j in self.edges:
            x1, y1, _ = self.vertices[i]
            x2, y2, _ = self.vertices[j]
            
            color = self.colors['edge']
            width = 2
            
            # Highlight traversed edges
            if (i in self.path and j in self.path):
                i_idx = self.path.index(i) if i in self.path else -1
                j_idx = self.path.index(j) if j in self.path else -1
                if i_idx != -1 and j_idx != -1 and abs(i_idx - j_idx) == 1:
                    color = self.colors['traversed_edge']
                    width = 3
            
            self.canvas.create_line(x1, y1, x2, y2, fill=color, width=width)
        
        # Draw vertices
        for x, y, vertex_id in self.vertices:
            # Determine vertex color
            if vertex_id == self.current_vertex:
                color = self.colors['current']
            elif vertex_id in self.visited:
                color = self.colors['visited']
            elif (self.algorithm == "DFS" and vertex_id in self.stack) or \
                 (self.algorithm == "BFS" and vertex_id in self.queue):
                color = self.colors['in_stack']
            else:
                color = self.colors['unvisited']
            
            # Draw vertex circle
            radius = 25
            self.canvas.create_oval(x - radius, y - radius, x + radius, y + radius,
                                  fill=color, outline='black', width=2)
            
            # Draw vertex label
            self.canvas.create_text(x, y, text=str(vertex_id), font=('Arial', 12, 'bold'))
    
    def update_labels(self):
        self.step_label.config(text=f"Step: {self.step_count}")
        self.current_label.config(text=f"Current: {self.current_vertex}")
        
        if self.algorithm == "DFS":
            self.stack_queue_label.config(text=f"Stack: {list(reversed(self.stack))}")
        else:
            self.stack_queue_label.config(text=f"Queue: {list(self.queue)}")
        
        self.visited_label.config(text=f"Visited: {sorted(list(self.visited))}")
    
    def update_info(self):
        self.info_text.delete(1.0, tk.END)
        
        if self.algorithm == "DFS":
            info = """DEPTH-FIRST SEARCH (DFS)

Algorithm: Uses a stack (LIFO - Last In, First Out)

Steps:
1. Start with initial vertex in stack
2. Pop vertex from stack
3. If not visited, mark as visited
4. Add unvisited neighbors to stack
5. Repeat until stack is empty

Characteristics:
• Goes as deep as possible before backtracking
• Uses O(V) space for stack
• Time complexity: O(V + E)
• Good for: Finding paths, topological sorting

Current path: """ + " → ".join(map(str, self.path))
        else:
            info = """BREADTH-FIRST SEARCH (BFS)

Algorithm: Uses a queue (FIFO - First In, First Out)

Steps:
1. Start with initial vertex in queue
2. Dequeue vertex from front
3. Add unvisited neighbors to back of queue
4. Mark neighbors as visited when added
5. Repeat until queue is empty

Characteristics:
• Explores all neighbors before going deeper
• Uses O(V) space for queue
• Time complexity: O(V + E)
• Good for: Shortest paths, level-order traversal

Current path: """ + " → ".join(map(str, self.path))
        
        self.info_text.insert(1.0, info)
    
    def on_algorithm_change(self, event=None):
        self.reset()
    
    def on_vertex_count_change(self):
        self.generate_random_graph()

def main():
    root = tk.Tk()
    app = GraphVisualizer(root)
    root.mainloop()

if __name__ == "__main__":
    main()
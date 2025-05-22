import tkinter as tk
from tkinter import ttk, messagebox
import heapq
import random
import math
from collections import defaultdict
import time

class ShortestPathVisualizer:
    def __init__(self, root):
        self.root = root
        self.root.title("Interactive Shortest Path Algorithms Visualizer")
        self.root.geometry("1400x900")
        
        # Graph data
        self.vertices = 6
        self.graph = {}  # adjacency list with weights
        self.pos = {}  # vertex positions for visualization
        self.edges = []  # list of (u, v, weight) tuples
        
        # Algorithm state
        self.algorithm = "Dijkstra"
        self.current_step = 0
        self.is_running = False
        self.start_vertex = 0
        self.target_vertex = None
        
        # Dijkstra state
        self.distances = {}
        self.previous = {}
        self.visited = set()
        self.priority_queue = []
        self.current_vertex = None
        
        # Floyd-Warshall state
        self.dist_matrix = None
        self.k = 0  # current intermediate vertex
        self.i = 0  # current source vertex
        self.j = 0  # current destination vertex
        self.fw_iterations = []
        self.fw_current_iteration = 0
        
        # Canvas settings
        self.canvas_width = 700
        self.canvas_height = 500
        self.vertex_radius = 25
        
        # Colors
        self.colors = {
            'vertex_default': '#E3F2FD',
            'vertex_start': '#4CAF50',
            'vertex_target': '#F44336',
            'vertex_current': '#FF9800',
            'vertex_visited': '#9C27B0',
            'vertex_in_queue': '#FFEB3B',
            'vertex_fw_k': '#FF5722',
            'vertex_fw_i': '#2196F3',
            'vertex_fw_j': '#9C27B0',
            'edge_default': '#757575',
            'edge_relaxed': '#2196F3',
            'edge_shortest_path': '#4CAF50',
            'edge_fw_considering': '#FF5722'
        }
        
        self.setup_ui()
        self.generate_random_graph()
        
    def setup_ui(self):
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Control panel
        control_frame = ttk.LabelFrame(main_frame, text="Algorithm Controls", padding=10)
        control_frame.pack(side=tk.TOP, fill=tk.X, pady=(0, 10))
        
        # Algorithm selection
        algo_frame = ttk.Frame(control_frame)
        algo_frame.pack(side=tk.LEFT, padx=(0, 20))
        ttk.Label(algo_frame, text="Algorithm:").pack(side=tk.LEFT)
        self.algo_var = tk.StringVar(value="Dijkstra")
        algo_combo = ttk.Combobox(algo_frame, textvariable=self.algo_var, 
                                 values=["Dijkstra", "Floyd-Warshall"], state="readonly", width=15)
        algo_combo.pack(side=tk.LEFT, padx=(5, 0))
        algo_combo.bind("<<ComboboxSelected>>", self.on_algorithm_change)
        
        # Vertex settings
        vertex_frame = ttk.Frame(control_frame)
        vertex_frame.pack(side=tk.LEFT, padx=(0, 20))
        ttk.Label(vertex_frame, text="Vertices:").pack(side=tk.LEFT)
        self.vertex_var = tk.IntVar(value=6)
        vertex_spinner = tk.Spinbox(vertex_frame, from_=4, to=8, textvariable=self.vertex_var, 
                                   width=5, command=self.on_vertex_count_change)
        vertex_spinner.pack(side=tk.LEFT, padx=(5, 0))
        
        # Start vertex selection
        start_frame = ttk.Frame(control_frame)
        start_frame.pack(side=tk.LEFT, padx=(0, 20))
        ttk.Label(start_frame, text="Start:").pack(side=tk.LEFT)
        self.start_var = tk.IntVar(value=0)
        self.start_spinner = tk.Spinbox(start_frame, from_=0, to=self.vertices-1, 
                                       textvariable=self.start_var, width=5, 
                                       command=self.on_start_change)
        self.start_spinner.pack(side=tk.LEFT, padx=(5, 0))
        
        # Control buttons
        btn_frame = ttk.Frame(control_frame)
        btn_frame.pack(side=tk.LEFT, padx=(0, 20))
        
        ttk.Button(btn_frame, text="Generate Graph", command=self.generate_random_graph).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Reset", command=self.reset_algorithm).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Step", command=self.step_forward).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Auto Run", command=self.auto_run).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Stop", command=self.stop_auto_run).pack(side=tk.LEFT, padx=2)
        
        # Speed control
        speed_frame = ttk.Frame(control_frame)
        speed_frame.pack(side=tk.LEFT)
        ttk.Label(speed_frame, text="Speed:").pack(side=tk.LEFT)
        self.speed_var = tk.DoubleVar(value=1.5)
        speed_scale = ttk.Scale(speed_frame, from_=0.5, to=3.0, variable=self.speed_var, 
                               orient=tk.HORIZONTAL, length=100)
        speed_scale.pack(side=tk.LEFT, padx=(5, 0))
        
        # Main content area
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Visualization area
        viz_frame = ttk.LabelFrame(content_frame, text="Graph Visualization")
        viz_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Canvas for graph visualization
        self.canvas = tk.Canvas(viz_frame, bg='white', width=self.canvas_width, height=self.canvas_height)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.canvas.bind("<Button-1>", self.on_vertex_click)
        
        # Info panel
        info_frame = ttk.Frame(content_frame)
        info_frame.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Algorithm info
        algo_info_frame = ttk.LabelFrame(info_frame, text="Algorithm Information")
        algo_info_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.info_text = tk.Text(algo_info_frame, width=45, height=18, wrap=tk.WORD, font=('Consolas', 9))
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
        
        self.queue_label = ttk.Label(step_frame, text="Queue: []")
        self.queue_label.pack(anchor=tk.W, padx=5, pady=2)
        
        self.distances_label = ttk.Label(step_frame, text="Distances: {}")
        self.distances_label.pack(anchor=tk.W, padx=5, pady=2)
        
        # Distance matrix for Floyd-Warshall
        matrix_frame = ttk.LabelFrame(info_frame, text="Distance Matrix")
        matrix_frame.pack(fill=tk.X)
        
        self.matrix_text = tk.Text(matrix_frame, width=45, height=8, wrap=tk.NONE, font=('Consolas', 8))
        matrix_scroll_x = ttk.Scrollbar(matrix_frame, orient=tk.HORIZONTAL, command=self.matrix_text.xview)
        matrix_scroll_y = ttk.Scrollbar(matrix_frame, orient=tk.VERTICAL, command=self.matrix_text.yview)
        self.matrix_text.configure(xscrollcommand=matrix_scroll_x.set, yscrollcommand=matrix_scroll_y.set)
        self.matrix_text.pack(fill=tk.BOTH, expand=True)
        matrix_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        matrix_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
    
    def generate_random_graph(self):
        """Generate a random weighted graph"""
        self.vertices = self.vertex_var.get()
        self.graph = {i: [] for i in range(self.vertices)}
        self.edges = []
        
        # Generate vertex positions in a circle
        center_x, center_y = self.canvas_width // 2, self.canvas_height // 2
        radius = min(self.canvas_width, self.canvas_height) // 3
        self.pos = {}
        
        for i in range(self.vertices):
            angle = 2 * math.pi * i / self.vertices
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            self.pos[i] = (x, y)
        
        # Generate random edges (ensure connectivity)
        # First create a spanning tree
        for i in range(1, self.vertices):
            parent = random.randint(0, i - 1)
            weight = random.randint(1, 15)
            self.graph[parent].append((i, weight))
            self.graph[i].append((parent, weight))
            self.edges.append((parent, i, weight))
        
        # Add additional random edges
        edge_probability = 0.4
        for i in range(self.vertices):
            for j in range(i + 1, self.vertices):
                # Check if edge already exists
                existing = any(neighbor == j for neighbor, _ in self.graph[i])
                if not existing and random.random() < edge_probability:
                    weight = random.randint(1, 15)
                    self.graph[i].append((j, weight))
                    self.graph[j].append((i, weight))
                    self.edges.append((i, j, weight))
        
        # Update start spinner range
        self.start_spinner.configure(to=self.vertices-1)
        
        self.reset_algorithm()
    
    def reset_algorithm(self):
        """Reset algorithm state"""
        self.current_step = 0
        self.is_running = False
        self.start_vertex = self.start_var.get()
        self.current_vertex = None
        
        if self.algorithm == "Dijkstra":
            self.reset_dijkstra()
        else:
            self.reset_floyd_warshall()
        
        self.update_display()
        self.update_info()
    
    def reset_dijkstra(self):
        """Reset Dijkstra's algorithm state"""
        self.distances = {v: float('inf') for v in range(self.vertices)}
        self.distances[self.start_vertex] = 0
        self.previous = {v: None for v in range(self.vertices)}
        self.visited = set()
        self.priority_queue = [(0, self.start_vertex)]
        heapq.heapify(self.priority_queue)
        self.current_vertex = None
    
    def reset_floyd_warshall(self):
        """Reset Floyd-Warshall algorithm state"""
        # Initialize distance matrix
        self.dist_matrix = [[float('inf') for _ in range(self.vertices)] for _ in range(self.vertices)]
        
        # Set diagonal to 0
        for i in range(self.vertices):
            self.dist_matrix[i][i] = 0
        
        # Set direct edges
        for u, v, weight in self.edges:
            self.dist_matrix[u][v] = weight
            self.dist_matrix[v][u] = weight
        
        # Reset iteration variables
        self.k = 0
        self.i = 0
        self.j = 0
        self.fw_iterations = []
        self.fw_current_iteration = 0
        
        # Pre-compute all iterations for step-by-step visualization
        self.compute_fw_iterations()
    
    def compute_fw_iterations(self):
        """Pre-compute Floyd-Warshall iterations for visualization"""
        self.fw_iterations = []
        dist = [row[:] for row in self.dist_matrix]  # Deep copy
        
        for k in range(self.vertices):
            for i in range(self.vertices):
                for j in range(self.vertices):
                    old_dist = dist[i][j]
                    new_dist = dist[i][k] + dist[k][j]
                    if new_dist < old_dist:
                        dist[i][j] = new_dist
                        self.fw_iterations.append({
                            'k': k, 'i': i, 'j': j,
                            'old_dist': old_dist,
                            'new_dist': new_dist,
                            'improved': True,
                            'matrix': [row[:] for row in dist]
                        })
                    else:
                        self.fw_iterations.append({
                            'k': k, 'i': i, 'j': j,
                            'old_dist': old_dist,
                            'new_dist': new_dist,
                            'improved': False,
                            'matrix': [row[:] for row in dist]
                        })
    
    def dijkstra_step(self):
        """Perform one step of Dijkstra's algorithm"""
        if not self.priority_queue:
            return False  # Algorithm finished
        
        # Get vertex with minimum distance
        current_dist, current_vertex = heapq.heappop(self.priority_queue)
        
        if current_vertex in self.visited:
            return True  # Continue with next iteration
        
        self.visited.add(current_vertex)
        self.current_vertex = current_vertex
        
        # Relax neighbors
        for neighbor, weight in self.graph[current_vertex]:
            if neighbor not in self.visited:
                new_distance = current_dist + weight
                if new_distance < self.distances[neighbor]:
                    self.distances[neighbor] = new_distance
                    self.previous[neighbor] = current_vertex
                    heapq.heappush(self.priority_queue, (new_distance, neighbor))
        
        return len(self.priority_queue) > 0 or len(self.visited) < self.vertices
    
    def floyd_warshall_step(self):
        """Perform one step of Floyd-Warshall algorithm"""
        if self.fw_current_iteration >= len(self.fw_iterations):
            return False  # Algorithm finished
        
        iteration = self.fw_iterations[self.fw_current_iteration]
        self.k = iteration['k']
        self.i = iteration['i']
        self.j = iteration['j']
        self.dist_matrix = iteration['matrix']
        
        self.fw_current_iteration += 1
        return self.fw_current_iteration < len(self.fw_iterations)
    
    def step_forward(self):
        """Perform one step of the selected algorithm"""
        if self.algorithm == "Dijkstra":
            has_more = self.dijkstra_step()
        else:
            has_more = self.floyd_warshall_step()
        
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
                delay = int(1000 / self.speed_var.get())
                self.root.after(delay, self.run_step)
            else:
                self.is_running = False
    
    def stop_auto_run(self):
        """Stop automatic running"""
        self.is_running = False
    
    def draw_graph(self):
        """Draw the graph on canvas"""
        self.canvas.delete("all")
        
        # Draw edges first (so they appear behind vertices)
        for u, v, weight in self.edges:
            x1, y1 = self.pos[u]
            x2, y2 = self.pos[v]
            
            # Determine edge color
            edge_color = self.colors['edge_default']
            edge_width = 2
            
            if self.algorithm == "Floyd-Warshall" and hasattr(self, 'k') and hasattr(self, 'i') and hasattr(self, 'j'):
                if ((u == self.i and v == self.k) or (u == self.k and v == self.i) or
                    (u == self.k and v == self.j) or (u == self.j and v == self.k)):
                    edge_color = self.colors['edge_fw_considering']
                    edge_width = 4
            
            # Draw edge
            self.canvas.create_line(x1, y1, x2, y2, fill=edge_color, width=edge_width)
            
            # Draw weight label
            mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
            self.canvas.create_oval(mid_x - 12, mid_y - 12, mid_x + 12, mid_y + 12, 
                                  fill='white', outline='gray')
            self.canvas.create_text(mid_x, mid_y, text=str(weight), font=('Arial', 8, 'bold'))
        
        # Draw vertices
        for vertex in range(self.vertices):
            x, y = self.pos[vertex]
            
            # Determine vertex color
            if self.algorithm == "Dijkstra":
                if vertex == self.start_vertex:
                    color = self.colors['vertex_start']
                elif vertex == self.current_vertex:
                    color = self.colors['vertex_current']
                elif vertex in self.visited:
                    color = self.colors['vertex_visited']
                elif any(v == vertex for _, v in self.priority_queue):
                    color = self.colors['vertex_in_queue']
                else:
                    color = self.colors['vertex_default']
            else:  # Floyd-Warshall
                if hasattr(self, 'k') and hasattr(self, 'i') and hasattr(self, 'j'):
                    if vertex == self.k:
                        color = self.colors['vertex_fw_k']
                    elif vertex == self.i:
                        color = self.colors['vertex_fw_i']
                    elif vertex == self.j:
                        color = self.colors['vertex_fw_j']
                    else:
                        color = self.colors['vertex_default']
                else:
                    color = self.colors['vertex_default']
            
            # Draw vertex circle
            self.canvas.create_oval(x - self.vertex_radius, y - self.vertex_radius, 
                                  x + self.vertex_radius, y + self.vertex_radius,
                                  fill=color, outline='black', width=2)
            
            # Draw vertex label
            self.canvas.create_text(x, y, text=str(vertex), font=('Arial', 12, 'bold'))
            
            # Draw distance for Dijkstra
            if self.algorithm == "Dijkstra" and vertex in self.distances:
                dist = self.distances[vertex]
                dist_text = str(dist) if dist != float('inf') else "∞"
                self.canvas.create_text(x, y + self.vertex_radius + 15, text=f"d={dist_text}", 
                                      font=('Arial', 9), fill='blue')
    
    def update_display(self):
        """Update the visual display"""
        self.draw_graph()
        
        # Update step information
        self.step_label.config(text=f"Step: {self.current_step}")
        
        if self.algorithm == "Dijkstra":
            self.current_label.config(text=f"Current: {self.current_vertex}")
            queue_contents = [f"{v}({d})" for d, v in sorted(self.priority_queue)]
            self.queue_label.config(text=f"Queue: {queue_contents}")
            
            # Format distances nicely
            dist_display = {}
            for v, d in self.distances.items():
                dist_display[v] = str(d) if d != float('inf') else "∞"
            self.distances_label.config(text=f"Distances: {dist_display}")
        else:
            if hasattr(self, 'k'):
                self.current_label.config(text=f"k={self.k}, i={self.i}, j={self.j}")
                self.queue_label.config(text=f"Considering path: {self.i}→{self.k}→{self.j}")
            
            # Update distance matrix display
            self.update_matrix_display()
    
    def update_matrix_display(self):
        """Update the distance matrix display for Floyd-Warshall"""
        if self.dist_matrix is None:
            return
        
        self.matrix_text.delete(1.0, tk.END)
        
        # Header row
        header = "     " + "".join(f"{i:6}" for i in range(self.vertices))
        self.matrix_text.insert(tk.END, header + "\n")
        
        # Matrix rows
        for i in range(self.vertices):
            row_text = f"{i:2}: "
            for j in range(self.vertices):
                dist = self.dist_matrix[i][j]
                dist_str = f"{dist:4}" if dist != float('inf') else "  ∞"
                
                # Highlight current cells
                if (hasattr(self, 'i') and hasattr(self, 'j') and hasattr(self, 'k') and
                    ((i == self.i and j == self.j) or (i == self.i and j == self.k) or (i == self.k and j == self.j))):
                    dist_str = f"[{dist_str.strip()}]"
                
                row_text += f"{dist_str:6}"
            
            self.matrix_text.insert(tk.END, row_text + "\n")
    
    def update_info(self):
        """Update the algorithm information panel"""
        self.info_text.delete(1.0, tk.END)
        
        if self.algorithm == "Dijkstra":
            info = """DIJKSTRA'S ALGORITHM

Single-source shortest path algorithm for weighted graphs with non-negative edge weights.

ALGORITHM STEPS:
1. Initialize distances: source = 0, others = ∞
2. Maintain priority queue of unvisited vertices
3. Extract vertex with minimum distance
4. For each neighbor, relax edge if shorter path found
5. Repeat until all vertices visited

RELAXATION:
If dist[u] + weight(u,v) < dist[v]:
   dist[v] = dist[u] + weight(u,v)
   previous[v] = u

COMPLEXITY:
- Time: O((V + E) log V) with binary heap
- Space: O(V)

CURRENT STATE:"""
            
            if hasattr(self, 'current_vertex') and self.current_vertex is not None:
                info += f"\n\nProcessing vertex: {self.current_vertex}"
                info += f"\nVisited vertices: {sorted(list(self.visited))}"
                info += f"\nQueue size: {len(self.priority_queue)}"
                
                if self.current_vertex in self.graph:
                    neighbors = [f"{v}(w={w})" for v, w in self.graph[self.current_vertex]]
                    info += f"\nNeighbors: {neighbors}"
        
        else:  # Floyd-Warshall
            info = """FLOYD-WARSHALL ALGORITHM

All-pairs shortest path algorithm using dynamic programming.

ALGORITHM STEPS:
1. Initialize distance matrix with direct edge weights
2. For each intermediate vertex k (0 to V-1):
   3. For each source vertex i (0 to V-1):
      4. For each destination vertex j (0 to V-1):
         5. If dist[i][k] + dist[k][j] < dist[i][j]:
            6. dist[i][j] = dist[i][k] + dist[k][j]

KEY INSIGHT:
Consider all possible intermediate vertices one by one.
For each k, update shortest paths that go through vertex k.

COMPLEXITY:
- Time: O(V³)
- Space: O(V²)

CURRENT STATE:"""
            
            if hasattr(self, 'k'):
                info += f"\n\nIntermediate vertex k: {self.k}"
                info += f"\nSource vertex i: {self.i}"
                info += f"\nDestination vertex j: {self.j}"
                
                if (hasattr(self, 'dist_matrix') and self.i < len(self.dist_matrix) and 
                    self.j < len(self.dist_matrix[0]) and self.k < len(self.dist_matrix)):
                    
                    current_dist = self.dist_matrix[self.i][self.j]
                    via_k_dist = self.dist_matrix[self.i][self.k] + self.dist_matrix[self.k][self.j]
                    
                    info += f"\n\nCurrent distance[{self.i}][{self.j}]: {current_dist if current_dist != float('inf') else '∞'}"
                    info += f"\nDistance via k ({self.i}→{self.k}→{self.j}): {via_k_dist if via_k_dist != float('inf') else '∞'}"
                    
                    if via_k_dist < current_dist:
                        info += f"\n✓ UPDATE: {current_dist if current_dist != float('inf') else '∞'} → {via_k_dist}"
                    else:
                        info += f"\n✗ NO UPDATE: {via_k_dist} ≥ {current_dist if current_dist != float('inf') else '∞'}"
        
        self.info_text.insert(1.0, info)
    
    def on_algorithm_change(self, event=None):
        """Handle algorithm selection change"""
        self.algorithm = self.algo_var.get()
        self.reset_algorithm()
    
    def on_vertex_count_change(self):
        """Handle vertex count change"""
        self.generate_random_graph()
    
    def on_start_change(self):
        """Handle start vertex change"""
        self.reset_algorithm()
    
    def on_vertex_click(self, event):
        """Handle vertex clicks for target selection"""
        # Find clicked vertex
        for vertex in range(self.vertices):
            x, y = self.pos[vertex]
            if ((event.x - x) ** 2 + (event.y - y) ** 2) <= self.vertex_radius ** 2:
                if self.algorithm == "Dijkstra":
                    self.target_vertex = vertex
                    messagebox.showinfo("Target Selected", f"Target vertex set to {vertex}")
                break

def main():
    root = tk.Tk()
    app = ShortestPathVisualizer(root)
    root.mainloop()

if __name__ == "__main__":
    main()
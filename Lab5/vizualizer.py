import tkinter as tk
from tkinter import ttk, messagebox
import heapq
import random
import math
from collections import defaultdict

class MSTVisualizer:
    def __init__(self, root):
        self.root = root
        self.root.title("Interactive MST Algorithms Visualizer")
        self.root.geometry("1500x900")
        
        # Graph data
        self.vertices = 6
        self.edges = []  # list of (u, v, weight) tuples
        self.pos = {}  # vertex positions for visualization
        
        # Algorithm state
        self.algorithm = "Kruskal"
        self.current_step = 0
        self.is_running = False
        self.mst_edges = []  # edges in the MST
        self.total_weight = 0
        
        # Kruskal's state
        self.sorted_edges = []
        self.parent = []
        self.rank = []
        self.current_edge_index = 0
        self.considered_edge = None
        self.edge_accepted = False
        
        # Prim's state
        self.visited_vertices = set()
        self.priority_queue = []
        self.key_values = {}
        self.parent_prim = {}
        self.current_vertex = None
        self.current_edge_prim = None
        
        # Canvas settings
        self.canvas_width = 700
        self.canvas_height = 500
        self.vertex_radius = 25
        
        # Colors
        self.colors = {
            'vertex_default': '#E3F2FD',
            'vertex_start': '#4CAF50',
            'vertex_visited': '#9C27B0',
            'vertex_current': '#FF9800',
            'vertex_in_queue': '#FFEB3B',
            'edge_default': '#BDBDBD',
            'edge_considering': '#FF5722',
            'edge_accepted': '#4CAF50',
            'edge_rejected': '#F44336',
            'edge_mst': '#2196F3'
        }
        
        self.setup_ui()
        self.generate_random_graph()
    
    def setup_ui(self):
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Control panel
        control_frame = ttk.LabelFrame(main_frame, text="MST Algorithm Controls", padding=10)
        control_frame.pack(side=tk.TOP, fill=tk.X, pady=(0, 10))
        
        # Algorithm selection
        algo_frame = ttk.Frame(control_frame)
        algo_frame.pack(side=tk.LEFT, padx=(0, 20))
        ttk.Label(algo_frame, text="Algorithm:").pack(side=tk.LEFT)
        self.algo_var = tk.StringVar(value="Kruskal")
        algo_combo = ttk.Combobox(algo_frame, textvariable=self.algo_var, 
                                 values=["Kruskal", "Prim"], state="readonly", width=12)
        algo_combo.pack(side=tk.LEFT, padx=(5, 0))
        algo_combo.bind("<<ComboboxSelected>>", self.on_algorithm_change)
        
        # Vertex settings
        vertex_frame = ttk.Frame(control_frame)
        vertex_frame.pack(side=tk.LEFT, padx=(0, 20))
        ttk.Label(vertex_frame, text="Vertices:").pack(side=tk.LEFT)
        self.vertex_var = tk.IntVar(value=6)
        vertex_spinner = tk.Spinbox(vertex_frame, from_=4, to=10, textvariable=self.vertex_var, 
                                   width=5, command=self.on_vertex_count_change)
        vertex_spinner.pack(side=tk.LEFT, padx=(5, 0))
        
        # Density control
        density_frame = ttk.Frame(control_frame)
        density_frame.pack(side=tk.LEFT, padx=(0, 20))
        ttk.Label(density_frame, text="Density:").pack(side=tk.LEFT)
        self.density_var = tk.DoubleVar(value=0.5)
        density_scale = ttk.Scale(density_frame, from_=0.3, to=0.8, variable=self.density_var, 
                                 orient=tk.HORIZONTAL, length=100, command=self.on_density_change)
        density_scale.pack(side=tk.LEFT, padx=(5, 0))
        
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
        
        # Info panel
        info_frame = ttk.Frame(content_frame)
        info_frame.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Algorithm info
        algo_info_frame = ttk.LabelFrame(info_frame, text="Algorithm Information")
        algo_info_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.info_text = tk.Text(algo_info_frame, width=50, height=18, wrap=tk.WORD, font=('Consolas', 9))
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
        
        self.mst_weight_label = ttk.Label(step_frame, text="MST Weight: 0")
        self.mst_weight_label.pack(anchor=tk.W, padx=5, pady=2)
        
        self.mst_edges_label = ttk.Label(step_frame, text="MST Edges: 0")
        self.mst_edges_label.pack(anchor=tk.W, padx=5, pady=2)
        
        # Edge list for Kruskal
        edge_frame = ttk.LabelFrame(info_frame, text="Edge Information")
        edge_frame.pack(fill=tk.X)
        
        self.edge_text = tk.Text(edge_frame, width=50, height=8, wrap=tk.NONE, font=('Consolas', 8))
        edge_scroll_y = ttk.Scrollbar(edge_frame, orient=tk.VERTICAL, command=self.edge_text.yview)
        self.edge_text.configure(yscrollcommand=edge_scroll_y.set)
        self.edge_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        edge_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
    
    def generate_random_graph(self):
        """Generate a random weighted graph"""
        self.vertices = self.vertex_var.get()
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
        
        # Generate random edges with weights
        edge_probability = self.density_var.get()
        
        # First ensure connectivity with a spanning tree
        for i in range(1, self.vertices):
            parent = random.randint(0, i - 1)
            weight = random.randint(1, 20)
            self.edges.append((parent, i, weight))
        
        # Add additional random edges
        for i in range(self.vertices):
            for j in range(i + 1, self.vertices):
                # Check if edge already exists
                existing = any((min(u, v) == min(i, j) and max(u, v) == max(i, j)) for u, v, _ in self.edges)
                if not existing and random.random() < edge_probability:
                    weight = random.randint(1, 20)
                    self.edges.append((i, j, weight))
        
        self.reset_algorithm()
    
    def reset_algorithm(self):
        """Reset algorithm state"""
        self.current_step = 0
        self.is_running = False
        self.mst_edges = []
        self.total_weight = 0
        
        if self.algorithm == "Kruskal":
            self.reset_kruskal()
        else:
            self.reset_prim()
        
        self.update_display()
        self.update_info()
    
    def reset_kruskal(self):
        """Reset Kruskal's algorithm state"""
        # Sort edges by weight
        self.sorted_edges = sorted(self.edges, key=lambda x: x[2])
        
        # Initialize Union-Find
        self.parent = list(range(self.vertices))
        self.rank = [0] * self.vertices
        
        self.current_edge_index = 0
        self.considered_edge = None
        self.edge_accepted = False
    
    def reset_prim(self):
        """Reset Prim's algorithm state"""
        # Start from vertex 0
        start_vertex = 0
        self.visited_vertices = {start_vertex}
        self.priority_queue = []
        self.key_values = {i: float('inf') for i in range(self.vertices)}
        self.parent_prim = {i: None for i in range(self.vertices)}
        self.current_vertex = start_vertex
        self.current_edge_prim = None
        
        # Add edges from start vertex to priority queue
        for u, v, weight in self.edges:
            if u == start_vertex and v not in self.visited_vertices:
                heapq.heappush(self.priority_queue, (weight, u, v))
                if weight < self.key_values[v]:
                    self.key_values[v] = weight
                    self.parent_prim[v] = u
            elif v == start_vertex and u not in self.visited_vertices:
                heapq.heappush(self.priority_queue, (weight, v, u))
                if weight < self.key_values[u]:
                    self.key_values[u] = weight
                    self.parent_prim[u] = v
    
    def find(self, parent, i):
        """Find with path compression for Union-Find"""
        if parent[i] != i:
            parent[i] = self.find(parent, parent[i])
        return parent[i]
    
    def union(self, parent, rank, x, y):
        """Union by rank for Union-Find"""
        root_x = self.find(parent, x)
        root_y = self.find(parent, y)
        
        if root_x == root_y:
            return False
        
        if rank[root_x] < rank[root_y]:
            parent[root_x] = root_y
        elif rank[root_x] > rank[root_y]:
            parent[root_y] = root_x
        else:
            parent[root_y] = root_x
            rank[root_x] += 1
        
        return True
    
    def kruskal_step(self):
        """Perform one step of Kruskal's algorithm"""
        if self.current_edge_index >= len(self.sorted_edges) or len(self.mst_edges) >= self.vertices - 1:
            return False  # Algorithm finished
        
        # Get current edge
        u, v, weight = self.sorted_edges[self.current_edge_index]
        self.considered_edge = (u, v, weight)
        
        # Check if adding this edge creates a cycle
        if self.find(self.parent, u) != self.find(self.parent, v):
            # Accept edge
            self.union(self.parent, self.rank, u, v)
            self.mst_edges.append((u, v, weight))
            self.total_weight += weight
            self.edge_accepted = True
        else:
            # Reject edge (would create cycle)
            self.edge_accepted = False
        
        self.current_edge_index += 1
        return len(self.mst_edges) < self.vertices - 1 and self.current_edge_index < len(self.sorted_edges)
    
    def prim_step(self):
        """Perform one step of Prim's algorithm"""
        if not self.priority_queue or len(self.visited_vertices) >= self.vertices:
            return False  # Algorithm finished
        
        # Get minimum weight edge from priority queue
        while self.priority_queue:
            weight, u, v = heapq.heappop(self.priority_queue)
            
            # Check if this edge is still valid (v not yet visited)
            if v not in self.visited_vertices:
                # Accept this edge
                self.current_edge_prim = (u, v, weight)
                self.visited_vertices.add(v)
                self.mst_edges.append((u, v, weight))
                self.total_weight += weight
                self.current_vertex = v
                
                # Add new edges from v to priority queue
                for edge_u, edge_v, edge_weight in self.edges:
                    if edge_u == v and edge_v not in self.visited_vertices:
                        if edge_weight < self.key_values[edge_v]:
                            self.key_values[edge_v] = edge_weight
                            self.parent_prim[edge_v] = v
                        heapq.heappush(self.priority_queue, (edge_weight, v, edge_v))
                    elif edge_v == v and edge_u not in self.visited_vertices:
                        if edge_weight < self.key_values[edge_u]:
                            self.key_values[edge_u] = edge_weight
                            self.parent_prim[edge_u] = v
                        heapq.heappush(self.priority_queue, (edge_weight, v, edge_u))
                
                break
        
        return len(self.visited_vertices) < self.vertices
    
    def step_forward(self):
        """Perform one step of the selected algorithm"""
        if self.algorithm == "Kruskal":
            has_more = self.kruskal_step()
        else:
            has_more = self.prim_step()
        
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
        
        # Draw edges
        for u, v, weight in self.edges:
            x1, y1 = self.pos[u]
            x2, y2 = self.pos[v]
            
            # Determine edge color and width
            edge_color = self.colors['edge_default']
            edge_width = 2
            
            # Check if this edge is in MST
            if (u, v, weight) in self.mst_edges or (v, u, weight) in self.mst_edges:
                edge_color = self.colors['edge_mst']
                edge_width = 4
            # Check if this is the edge being considered
            elif (self.algorithm == "Kruskal" and self.considered_edge and 
                  ((u, v, weight) == self.considered_edge or (v, u, weight) == self.considered_edge)):
                if self.edge_accepted:
                    edge_color = self.colors['edge_accepted']
                else:
                    edge_color = self.colors['edge_rejected']
                edge_width = 4
            elif (self.algorithm == "Prim" and self.current_edge_prim and 
                  ((u, v, weight) == self.current_edge_prim or (v, u, weight) == self.current_edge_prim)):
                edge_color = self.colors['edge_considering']
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
            if self.algorithm == "Prim":
                if vertex in self.visited_vertices:
                    if vertex == self.current_vertex:
                        color = self.colors['vertex_current']
                    else:
                        color = self.colors['vertex_visited']
                else:
                    color = self.colors['vertex_default']
            else:  # Kruskal
                color = self.colors['vertex_default']
            
            # Draw vertex circle
            self.canvas.create_oval(x - self.vertex_radius, y - self.vertex_radius, 
                                  x + self.vertex_radius, y + self.vertex_radius,
                                  fill=color, outline='black', width=2)
            
            # Draw vertex label
            self.canvas.create_text(x, y, text=str(vertex), font=('Arial', 12, 'bold'))
    
    def update_display(self):
        """Update the visual display"""
        self.draw_graph()
        
        # Update step information
        self.step_label.config(text=f"Step: {self.current_step}")
        self.mst_weight_label.config(text=f"MST Weight: {self.total_weight}")
        self.mst_edges_label.config(text=f"MST Edges: {len(self.mst_edges)}/{self.vertices-1}")
        
        if self.algorithm == "Kruskal":
            if self.considered_edge:
                u, v, w = self.considered_edge
                status = "✓ ACCEPTED" if self.edge_accepted else "✗ REJECTED (cycle)"
                self.current_label.config(text=f"Edge ({u},{v},w={w}) - {status}")
            else:
                self.current_label.config(text="Ready to start")
        else:  # Prim
            if self.current_edge_prim:
                u, v, w = self.current_edge_prim
                self.current_label.config(text=f"Added edge ({u},{v},w={w})")
            else:
                self.current_label.config(text=f"Starting from vertex {self.current_vertex}")
        
        # Update edge information
        self.update_edge_display()
    
    def update_edge_display(self):
        """Update the edge information display"""
        self.edge_text.delete(1.0, tk.END)
        
        if self.algorithm == "Kruskal":
            self.edge_text.insert(tk.END, "SORTED EDGES:\n")
            self.edge_text.insert(tk.END, "Rank | Edge    | Weight | Status\n")
            self.edge_text.insert(tk.END, "-" * 35 + "\n")
            
            for i, (u, v, w) in enumerate(self.sorted_edges):
                status = ""
                if i < self.current_edge_index:
                    if (u, v, w) in self.mst_edges or (v, u, w) in self.mst_edges:
                        status = "✓ MST"
                    else:
                        status = "✗ CYCLE"
                elif i == self.current_edge_index - 1 and self.considered_edge:
                    status = "→ CURRENT"
                
                self.edge_text.insert(tk.END, f"{i+1:4} | ({u},{v})  | {w:6} | {status}\n")
        
        else:  # Prim
            self.edge_text.insert(tk.END, "PRIM'S ALGORITHM STATE:\n\n")
            self.edge_text.insert(tk.END, "VISITED VERTICES:\n")
            self.edge_text.insert(tk.END, f"{sorted(list(self.visited_vertices))}\n\n")
            
            self.edge_text.insert(tk.END, "KEY VALUES (minimum edge weights):\n")
            for v in range(self.vertices):
                key_val = self.key_values[v] if self.key_values[v] != float('inf') else "∞"
                parent = self.parent_prim[v] if self.parent_prim[v] is not None else "-"
                visited = "✓" if v in self.visited_vertices else " "
                self.edge_text.insert(tk.END, f"V{v}: key={key_val:3}, parent={parent} {visited}\n")
            
            if self.priority_queue:
                self.edge_text.insert(tk.END, f"\nPRIORITY QUEUE SIZE: {len(self.priority_queue)}\n")
    
    def update_info(self):
        """Update the algorithm information panel"""
        self.info_text.delete(1.0, tk.END)
        
        if self.algorithm == "Kruskal":
            info = """KRUSKAL'S ALGORITHM

A greedy algorithm that finds the Minimum Spanning Tree by considering edges in order of increasing weight.

ALGORITHM STEPS:
1. Sort all edges by weight (ascending)
2. Initialize Union-Find data structure
3. For each edge (u,v) in sorted order:
   a. If u and v are in different components:
      - Add edge to MST
      - Union the components
   b. Otherwise: skip (would create cycle)
4. Stop when MST has V-1 edges

UNION-FIND OPERATIONS:
- Find(x): Get root/representative of x's component
- Union(x,y): Merge components containing x and y
- Path compression optimizes Find operations
- Union by rank optimizes Union operations

TIME COMPLEXITY: O(E log E) - dominated by sorting
SPACE COMPLEXITY: O(V) - for Union-Find structure

GREEDY CHOICE: Always pick the minimum weight edge that doesn't create a cycle.

CURRENT STATE:"""
            
            if self.considered_edge:
                u, v, w = self.considered_edge
                info += f"\n\nConsidering edge: ({u}, {v}) with weight {w}"
                
                # Show component information
                root_u = self.find(self.parent, u)
                root_v = self.find(self.parent, v)
                
                info += f"\nVertex {u} is in component rooted at {root_u}"
                info += f"\nVertex {v} is in component rooted at {root_v}"
                
                if root_u == root_v:
                    info += f"\n✗ REJECTED: Both vertices in same component (would create cycle)"
                else:
                    info += f"\n✓ ACCEPTED: Vertices in different components"
                    info += f"\nUnion operation merges components {root_u} and {root_v}"
        
        else:  # Prim
            info = """PRIM'S ALGORITHM

A greedy algorithm that grows the MST one vertex at a time, always adding the minimum weight edge that connects a new vertex.

ALGORITHM STEPS:
1. Start with arbitrary vertex (mark as visited)
2. Maintain key[v] = minimum weight of edge connecting v to MST
3. While there are unvisited vertices:
   a. Pick unvisited vertex u with minimum key[u]
   b. Add u to MST
   c. Update key values of u's neighbors

KEY INSIGHT:
At each step, we grow the MST by adding the cheapest edge that connects an unvisited vertex to the current MST.

DATA STRUCTURES:
- Priority queue: Extract minimum key vertex efficiently
- Key array: Minimum edge weight to reach each vertex
- Parent array: Track MST edges

TIME COMPLEXITY: 
- O(V²) with array
- O((V + E) log V) with binary heap
- O(V log V + E) with Fibonacci heap

GREEDY CHOICE: Always add the closest unvisited vertex to the growing MST.

CURRENT STATE:"""
            
            info += f"\n\nVisited vertices: {sorted(list(self.visited_vertices))}"
            info += f"\nUnvisited vertices: {sorted([v for v in range(self.vertices) if v not in self.visited_vertices])}"
            
            if self.current_edge_prim:
                u, v, w = self.current_edge_prim
                info += f"\n\nLast added edge: ({u}, {v}) with weight {w}"
                info += f"\nThis edge connects vertex {v} to the MST"
            
            # Show current minimum edges to unvisited vertices
            unvisited = [v for v in range(self.vertices) if v not in self.visited_vertices]
            if unvisited:
                info += f"\n\nMinimum edges to unvisited vertices:"
                for v in unvisited:
                    key_val = self.key_values[v] if self.key_values[v] != float('inf') else "∞"
                    parent = self.parent_prim[v] if self.parent_prim[v] is not None else "-"
                    info += f"\nVertex {v}: key={key_val}, parent={parent}"
        
        self.info_text.insert(1.0, info)
    
    def on_algorithm_change(self, event=None):
        """Handle algorithm selection change"""
        self.algorithm = self.algo_var.get()
        self.reset_algorithm()
    
    def on_vertex_count_change(self):
        """Handle vertex count change"""
        self.generate_random_graph()
    
    def on_density_change(self, event=None):
        """Handle density change"""
        self.generate_random_graph()

def main():
    root = tk.Tk()
    app = MSTVisualizer(root)
    root.mainloop()

if __name__ == "__main__":
    main()
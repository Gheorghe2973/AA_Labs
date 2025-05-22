import tkinter as tk
from tkinter import messagebox, ttk
import random
import math

class PrimsGame:
    def __init__(self, root):
        self.root = root
        self.root.title("🌲 Prim's Algorithm Learning Game")
        self.root.geometry("1200x800")
        self.root.configure(bg="#f0f8ff")
        
        # Enhanced color scheme
        self.colors = {
            'bg': "#f0f8ff",
            'canvas_bg': "#ffffff",
            'vertex_default': "#2c3e50",
            'vertex_in_mst': "#3498db",
            'vertex_start': "#e74c3c",
            'edge_default': "#bdc3c7",
            'edge_selected': "#3498db",
            'edge_correct': "#27ae60",
            'edge_wrong': "#e74c3c",
            'edge_hint': "#f39c12",
            'weight_bg': "#ffffff",
            'weight_border': "#34495e",
            'button_new': "#3498db",
            'button_check': "#27ae60",
            'button_reset': "#e67e22",
            'button_hint': "#f39c12",
            'button_help': "#9b59b6"
        }
        
        # Game state
        self.vertices = []
        self.edges = []
        self.selected_edges = []
        self.correct_mst_edges = []
        self.game_completed = False
        self.current_mst_vertices = set()
        self.start_vertex = 0
        self.animation_step = 0
        
        self.setup_ui()
        self.generate_new_graph()
    
    def setup_ui(self):
        # Main container with gradient-like effect
        main_frame = tk.Frame(self.root, bg=self.colors['bg'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        title_frame.pack(fill=tk.X, pady=(0, 10))
        
        title_label = tk.Label(title_frame, text="🌲 Prim's Algorithm Learning Game", 
                              font=("Arial", 20, "bold"), 
                              bg=self.colors['bg'], fg="#2c3e50")
        title_label.pack()
        
        subtitle_label = tk.Label(title_frame, text="Build the Minimum Spanning Tree!", 
                                 font=("Arial", 12, "italic"), 
                                 bg=self.colors['bg'], fg="#7f8c8d")
        subtitle_label.pack()
        
        # Control panel with styled buttons
        control_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Button style configuration
        button_style = {
            'font': ("Arial", 11, "bold"),
            'relief': tk.RAISED,
            'bd': 2,
            'padx': 15,
            'pady': 8,
            'cursor': 'hand2'
        }
        
        self.new_btn = tk.Button(control_frame, text="🎲 New Graph", 
                                command=self.generate_new_graph,
                                bg=self.colors['button_new'], fg="white",
                                activebackground="#2980b9", **button_style)
        self.new_btn.pack(side=tk.LEFT, padx=5)
        
        self.check_btn = tk.Button(control_frame, text="✓ Check Solution", 
                                  command=self.check_solution,
                                  bg=self.colors['button_check'], fg="white",
                                  activebackground="#229954", **button_style)
        self.check_btn.pack(side=tk.LEFT, padx=5)
        
        self.reset_btn = tk.Button(control_frame, text="↺ Reset", 
                                  command=self.reset_selection,
                                  bg=self.colors['button_reset'], fg="white",
                                  activebackground="#d35400", **button_style)
        self.reset_btn.pack(side=tk.LEFT, padx=5)
        
        self.hint_btn = tk.Button(control_frame, text="💡 Show Solution", 
                                 command=self.show_solution,
                                 bg=self.colors['button_hint'], fg="white",
                                 activebackground="#e67e22", **button_style)
        self.hint_btn.pack(side=tk.LEFT, padx=5)
        
        self.help_btn = tk.Button(control_frame, text="❓ Help", 
                                 command=self.show_help,
                                 bg=self.colors['button_help'], fg="white",
                                 activebackground="#8e44ad", **button_style)
        self.help_btn.pack(side=tk.LEFT, padx=5)
        
        # Info panel with modern styling
        info_frame = tk.Frame(main_frame, bg="#ecf0f1", relief=tk.RAISED, bd=1)
        info_frame.pack(fill=tk.X, pady=(0, 10), padx=2)
        
        info_inner = tk.Frame(info_frame, bg="#ecf0f1")
        info_inner.pack(fill=tk.X, padx=15, pady=10)
        
        self.info_label = tk.Label(info_inner, text="🎯 Click on edges to select them for the MST", 
                                  font=("Arial", 12), bg="#ecf0f1", fg="#2c3e50")
        self.info_label.pack(side=tk.LEFT)
        
        self.score_label = tk.Label(info_inner, text="", 
                                   font=("Arial", 12, "bold"), bg="#ecf0f1", fg="#27ae60")
        self.score_label.pack(side=tk.RIGHT)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress = ttk.Progressbar(info_inner, variable=self.progress_var, 
                                       maximum=100, length=200)
        self.progress.pack(side=tk.RIGHT, padx=(0, 20))
        
        # Canvas with border
        canvas_frame = tk.Frame(main_frame, bg="#34495e", relief=tk.RAISED, bd=2)
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(canvas_frame, bg=self.colors['canvas_bg'], 
                               highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=3, pady=3)
        
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<Motion>", self.on_mouse_motion)
        
        # Legend    
    
    
    def generate_new_graph(self):
        """Generate a new random connected graph with improved distribution"""
        self.canvas.delete("all")
        self.vertices = []
        self.edges = []
        self.selected_edges = []
        self.correct_mst_edges = []
        self.game_completed = False
        self.current_mst_vertices = set()
        self.animation_step = 0
        
        # Generate vertices in a more aesthetically pleasing way
        num_vertices = random.randint(6, 9)
        canvas_width = self.canvas.winfo_width() or 800
        canvas_height = self.canvas.winfo_height() or 600
        
        # Use circular distribution for better visual appeal
        center_x, center_y = canvas_width // 2, canvas_height // 2
        radius = min(canvas_width, canvas_height) // 3
        
        for i in range(num_vertices):
            if i == 0:
                # Center vertex
                x, y = center_x, center_y
            else:
                # Distribute around circle with some randomness
                angle = (2 * math.pi * (i - 1)) / (num_vertices - 1)
                base_x = center_x + radius * math.cos(angle)
                base_y = center_y + radius * math.sin(angle)
                
                # Add some randomness
                x = base_x + random.randint(-50, 50)
                y = base_y + random.randint(-50, 50)
                
                # Keep within bounds
                x = max(60, min(canvas_width - 60, x))
                y = max(60, min(canvas_height - 60, y))
            
            self.vertices.append((x, y, i))
        
        # Generate edges with better weight distribution
        self.edges = []
        
        # Create spanning tree for connectivity
        remaining_vertices = list(range(1, num_vertices))
        connected_vertices = [0]
        
        while remaining_vertices:
            v1 = random.choice(connected_vertices)
            v2 = random.choice(remaining_vertices)
            
            # Calculate distance-based weight with some randomness
            x1, y1, _ = self.vertices[v1]
            x2, y2, _ = self.vertices[v2]
            distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
            weight = max(1, int(distance / 20) + random.randint(-3, 8))
            
            self.edges.append((v1, v2, weight))
            connected_vertices.append(v2)
            remaining_vertices.remove(v2)
        
        # Add additional edges for complexity
        num_additional = random.randint(3, min(10, num_vertices * (num_vertices - 1) // 2 - len(self.edges)))
        attempts = 0
        while len(self.edges) - (num_vertices - 1) < num_additional and attempts < 50:
            v1 = random.randint(0, num_vertices - 1)
            v2 = random.randint(0, num_vertices - 1)
            
            if v1 != v2 and not any(
                (e[0] == v1 and e[1] == v2) or (e[0] == v2 and e[1] == v1) for e in self.edges
            ):
                x1, y1, _ = self.vertices[v1]
                x2, y2, _ = self.vertices[v2]
                distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
                weight = max(1, int(distance / 20) + random.randint(-3, 8))
                self.edges.append((v1, v2, weight))
            
            attempts += 1
        
        # Calculate MST and set start vertex
        self.start_vertex = 0
        self.current_mst_vertices.add(0)
        self.correct_mst_edges = self.calculate_mst()
        
        self.draw_graph()
        self.update_info()
        self.update_progress()
    
    def calculate_mst(self):
        """Calculate MST using Prim's algorithm"""
        if not self.vertices:
            return []
        
        mst_edges = []
        visited = set([self.start_vertex])
        
        while len(visited) < len(self.vertices):
            min_edge = None
            min_weight = float('inf')
            
            for v1, v2, weight in self.edges:
                if (v1 in visited) != (v2 in visited):
                    if weight < min_weight:
                        min_weight = weight
                        min_edge = (v1, v2, weight)
            
            if min_edge:
                mst_edges.append(min_edge)
                visited.add(min_edge[0])
                visited.add(min_edge[1])
        
        return mst_edges
    
    def draw_graph(self):
        """Draw the graph with enhanced visuals"""
        self.canvas.delete("all")
        
        # Draw background grid for better visual appeal
        self.draw_grid()
        
        # Draw edges with improved styling
        for i, (v1, v2, weight) in enumerate(self.edges):
            x1, y1, _ = self.vertices[v1]
            x2, y2, _ = self.vertices[v2]
            
            # Determine edge appearance
            edge_color = self.colors['edge_default']
            edge_width = 3
            edge_style = ()
            
            if (v1, v2, weight) in self.selected_edges or (v2, v1, weight) in self.selected_edges:
                edge_color = self.colors['edge_selected']
                edge_width = 5
            
            # Draw edge with shadow effect
            self.canvas.create_line(x1 + 2, y1 + 2, x2 + 2, y2 + 2, 
                                  fill="#95a5a6", width=edge_width, tags=f"shadow_{i}")
            
            edge_id = self.canvas.create_line(x1, y1, x2, y2, 
                                            fill=edge_color, width=edge_width, 
                                            tags=f"edge_{i}", capstyle=tk.ROUND)
            
            # Draw weight with enhanced styling
            mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
            
            # Weight background with shadow
            self.canvas.create_oval(mid_x - 14, mid_y - 14, mid_x + 14, mid_y + 14, 
                                  fill="#7f8c8d", outline="", tags=f"weight_shadow_{i}")
            self.canvas.create_oval(mid_x - 12, mid_y - 12, mid_x + 12, mid_y + 12, 
                                  fill=self.colors['weight_bg'], 
                                  outline=self.colors['weight_border'], width=2,
                                  tags=f"weight_bg_{i}")
            
            # Weight text
            self.canvas.create_text(mid_x, mid_y, text=str(weight), 
                                  font=("Arial", 10, "bold"), 
                                  fill="#2c3e50", tags=f"weight_{i}")
        
        # Draw vertices with enhanced styling
        for i, (x, y, vertex_id) in enumerate(self.vertices):
            # Determine vertex color
            if vertex_id == self.start_vertex:
                color = self.colors['vertex_start']
            elif vertex_id in self.current_mst_vertices:
                color = self.colors['vertex_in_mst']
            else:
                color = self.colors['vertex_default']
            
            # Draw vertex with shadow and gradient effect
            self.canvas.create_oval(x - 17, y - 17, x + 17, y + 17, 
                                  fill="#34495e", outline="", tags=f"vertex_shadow_{i}")
            self.canvas.create_oval(x - 15, y - 15, x + 15, y + 15, 
                                  fill=color, outline="#ffffff", width=3, 
                                  tags=f"vertex_{i}")
            
            # Vertex label
            text_color = "white" if vertex_id != self.start_vertex else "white"
            self.canvas.create_text(x, y, text=str(vertex_id), 
                                  fill=text_color, font=("Arial", 12, "bold"))
    
    def draw_grid(self):
        """Draw a subtle background grid"""
        canvas_width = self.canvas.winfo_width() or 800
        canvas_height = self.canvas.winfo_height() or 600
        
        # Draw grid lines
        for x in range(0, canvas_width, 50):
            self.canvas.create_line(x, 0, x, canvas_height, 
                                  fill="#f8f9fa", width=1, tags="grid")
        
        for y in range(0, canvas_height, 50):
            self.canvas.create_line(0, y, canvas_width, y, 
                                  fill="#f8f9fa", width=1, tags="grid")
    
    def on_canvas_click(self, event):
        """Handle canvas clicks with improved edge detection"""
        if self.game_completed:
            return
        
        # Find clicked edge with larger tolerance
        tolerance = 8
        clicked_items = self.canvas.find_overlapping(
            event.x - tolerance, event.y - tolerance, 
            event.x + tolerance, event.y + tolerance
        )
        
        for item in clicked_items:
            tags = self.canvas.gettags(item)
            for tag in tags:
                if tag.startswith("edge_"):
                    edge_index = int(tag.split("_")[1])
                    edge = self.edges[edge_index]
                    
                    # Toggle edge selection
                    if edge in self.selected_edges:
                        self.selected_edges.remove(edge)
                    else:
                        reverse_edge = (edge[1], edge[0], edge[2])
                        if reverse_edge not in self.selected_edges:
                            self.selected_edges.append(edge)
                    
                    self.update_mst_vertices()
                    self.draw_graph()
                    self.update_info()
                    self.update_progress()
                    return
    
    def on_mouse_motion(self, event):
        """Add hover effects"""
        # Find items under mouse
        items = self.canvas.find_overlapping(event.x - 5, event.y - 5, 
                                           event.x + 5, event.y + 5)
        
        # Reset cursor
        self.canvas.config(cursor="")
        
        # Check if hovering over clickable edge
        for item in items:
            tags = self.canvas.gettags(item)
            for tag in tags:
                if tag.startswith("edge_") and not self.game_completed:
                    self.canvas.config(cursor="hand2")
                    return
    
    def update_mst_vertices(self):
        """Update vertices in current MST"""
        self.current_mst_vertices = set([self.start_vertex])
        for v1, v2, _ in self.selected_edges:
            self.current_mst_vertices.add(v1)
            self.current_mst_vertices.add(v2)
    
    def update_progress(self):
        """Update progress bar"""
        if len(self.vertices) > 1:
            target_edges = len(self.vertices) - 1
            current_edges = len(self.selected_edges)
            progress = min(100, (current_edges / target_edges) * 100)
            self.progress_var.set(progress)
    
    def edges_equal(self, edge1, edge2):
        """Check if edges are equal (bidirectional)"""
        return ((edge1[0] == edge2[0] and edge1[1] == edge2[1]) or 
                (edge1[0] == edge2[1] and edge1[1] == edge2[0])) and edge1[2] == edge2[2]
    
    def check_solution(self):
        """Check solution with detailed feedback"""
        target_edges = len(self.vertices) - 1
        
        if len(self.selected_edges) != target_edges:
            messagebox.showwarning("⚠️ Incomplete Solution", 
                                 f"An MST needs exactly {target_edges} edges.\n"
                                 f"You have selected {len(self.selected_edges)} edges.")
            return
        
        # Check connectivity
        if not self.is_connected():
            messagebox.showwarning("⚠️ Not Connected", 
                                 "Your selected edges don't form a connected graph!")
            return
        
        # Check if it's the optimal MST
        correct_count = 0
        for selected_edge in self.selected_edges:
            for correct_edge in self.correct_mst_edges:
                if self.edges_equal(selected_edge, correct_edge):
                    correct_count += 1
                    break
        
        selected_weight = sum(edge[2] for edge in self.selected_edges)
        optimal_weight = sum(edge[2] for edge in self.correct_mst_edges)
        
        if correct_count == len(self.correct_mst_edges):
            messagebox.showinfo("🎉 Perfect!", 
                              f"Congratulations! You found the optimal MST!\n\n"
                              f"✓ All {correct_count} edges correct\n"
                              f"✓ Total weight: {selected_weight}\n"
                              f"✓ This is the minimum possible weight!")
            self.game_completed = True
            self.highlight_solution(True)
        elif selected_weight == optimal_weight:
            messagebox.showinfo("🌟 Great Job!", 
                              f"Excellent! You found an MST with optimal weight!\n\n"
                              f"• Your weight: {selected_weight}\n"
                              f"• Optimal weight: {optimal_weight}\n"
                              f"• Correct edges: {correct_count}/{target_edges}")
            self.game_completed = True
            self.highlight_solution(True)
        else:
            messagebox.showwarning("❌ Not Optimal", 
                                 f"You created a spanning tree, but it's not minimal.\n\n"
                                 f"• Your weight: {selected_weight}\n"
                                 f"• Optimal weight: {optimal_weight}\n"
                                 f"• Difference: +{selected_weight - optimal_weight}")
            self.highlight_solution(False)
    
    def is_connected(self):
        """Check if selected edges form a connected graph"""
        if not self.selected_edges:
            return False
        
        # Build adjacency list
        adj = {i: [] for i in range(len(self.vertices))}
        for v1, v2, _ in self.selected_edges:
            adj[v1].append(v2)
            adj[v2].append(v1)
        
        # DFS to check connectivity
        visited = set()
        stack = [0]
        
        while stack:
            v = stack.pop()
            if v not in visited:
                visited.add(v)
                stack.extend(adj[v])
        
        return len(visited) == len(self.vertices)
    
    def highlight_solution(self, all_correct):
        """Highlight solution with enhanced visuals"""
        self.canvas.delete("all")
        self.draw_grid()
        
        # Draw edges with solution highlighting
        for i, (v1, v2, weight) in enumerate(self.edges):
            x1, y1, _ = self.vertices[v1]
            x2, y2, _ = self.vertices[v2]
            
            edge = (v1, v2, weight)
            is_selected = edge in self.selected_edges or (v2, v1, weight) in self.selected_edges
            is_correct = any(self.edges_equal(edge, correct_edge) for correct_edge in self.correct_mst_edges)
            
            # Determine edge appearance
            if is_selected and is_correct:
                edge_color = self.colors['edge_correct']
                edge_width = 6
            elif is_selected and not is_correct:
                edge_color = self.colors['edge_wrong']
                edge_width = 6
            elif not is_selected and is_correct and not all_correct:
                edge_color = self.colors['edge_hint']
                edge_width = 4
            else:
                edge_color = self.colors['edge_default']
                edge_width = 2
            
            # Draw with glow effect for highlighted edges
            if edge_width > 4:
                self.canvas.create_line(x1, y1, x2, y2, 
                                      fill=edge_color, width=edge_width + 4, 
                                      tags="glow")
            
            self.canvas.create_line(x1, y1, x2, y2, 
                                  fill=edge_color, width=edge_width, 
                                  capstyle=tk.ROUND)
            
            # Weight display
            mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
            self.canvas.create_oval(mid_x - 12, mid_y - 12, mid_x + 12, mid_y + 12, 
                                  fill="white", outline="#2c3e50", width=2)
            self.canvas.create_text(mid_x, mid_y, text=str(weight), 
                                  font=("Arial", 10, "bold"), fill="#2c3e50")
        
        # Draw vertices
        for x, y, vertex_id in self.vertices:
            color = self.colors['vertex_in_mst'] if vertex_id in self.current_mst_vertices else self.colors['vertex_default']
            self.canvas.create_oval(x - 15, y - 15, x + 15, y + 15, 
                                  fill=color, outline="white", width=3)
            self.canvas.create_text(x, y, text=str(vertex_id), 
                                  fill="white", font=("Arial", 12, "bold"))
    
    def show_solution(self):
        """Show the optimal solution"""
        self.selected_edges = self.correct_mst_edges.copy()
        self.update_mst_vertices()
        self.game_completed = True
        
        total_weight = sum(edge[2] for edge in self.correct_mst_edges)
        
        self.draw_graph()
        self.update_info()
        self.update_progress()
        
        messagebox.showinfo("💡 Solution Revealed", 
                          f"Here's the optimal MST using Prim's algorithm!\n\n"
                          f"🌲 Minimum total weight: {total_weight}\n"
                          f"🔗 Edges in MST: {len(self.correct_mst_edges)}")
    
    def reset_selection(self):
        """Reset current selection"""
        self.selected_edges = []
        self.current_mst_vertices = set([self.start_vertex])
        self.game_completed = False
        self.draw_graph()
        self.update_info()
        self.update_progress()
    
    def update_info(self):
        """Update information display"""
        if self.selected_edges:
            total_weight = sum(edge[2] for edge in self.selected_edges)
            target_edges = len(self.vertices) - 1
            self.info_label.config(text=f"🔗 Selected: {len(self.selected_edges)}/{target_edges} edges")
            self.score_label.config(text=f"⚖️ Total Weight: {total_weight}")
        else:
            self.info_label.config(text="🎯 Click on edges to build your MST")
            self.score_label.config(text="")
    
    def show_help(self):
        """Show comprehensive help"""
        help_text = """🌲 PRIM'S ALGORITHM - MINIMUM SPANNING TREE

📚 ALGORITHM STEPS:
1️⃣ Start with any vertex (red vertex is the starting point)
2️⃣ Repeatedly add the cheapest edge that connects:
   • A vertex already in the MST (blue)
   • A vertex not yet in the MST (black)
3️⃣ Continue until all vertices are connected
4️⃣ Result: Tree with minimum total edge weight

🎮 HOW TO PLAY:
- 🖱️ Click edges to select/deselect them
- 🎯 Build an MST with exactly n-1 edges (n = vertex count)
- ✅ Use 'Check Solution' to verify your answer
- 💡 Use 'Show Solution' if you need help

🎨 COLOR GUIDE:
🔴 Start vertex (where Prim's algorithm begins)
🔵 Vertices in your current MST
⚫ Vertices not yet in MST
━ Gray: Available edges
━ Blue: Your selected edges  
━ Green: Correct edges (after checking)
━ Red: Wrong edges (after checking)
━ Orange: Hint edges (missing from your solution)

🏆 SCORING:
- Perfect: All edges correct + minimum weight
- Good: Minimum weight achieved
- Try again: Higher than minimum weight

💡 TIP: Always choose the cheapest available edge that doesn't create a cycle!"""
        
        # Create custom help window
        help_window = tk.Toplevel(self.root)
        help_window.title("❓ Help - Prim's Algorithm")
        help_window.geometry("600x700")
        help_window.configure(bg="#2c3e50")
        help_window.resizable(False, False)
        
        # Make window modal
        help_window.transient(self.root)
        help_window.grab_set()
        
        # Help content
        text_frame = tk.Frame(help_window, bg="#2c3e50")
        text_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        help_label = tk.Label(text_frame, text=help_text, 
                             font=("Consolas", 11), bg="#2c3e50", fg="white",
                             justify=tk.LEFT, anchor="nw")
        help_label.pack(fill=tk.BOTH, expand=True)
        
        # Close button
        close_btn = tk.Button(help_window, text="✖️ Close", 
                             command=help_window.destroy,
                             bg="#e74c3c", fg="white", font=("Arial", 12, "bold"),
                            padx=20, pady=10, cursor="hand2")
        close_btn.pack(pady=(0, 20))

def main():
   root = tk.Tk()
   
   # Center the window on screen
   root.update_idletasks()
   width = 1200
   height = 800
   x = (root.winfo_screenwidth() // 2) - (width // 2)
   y = (root.winfo_screenheight() // 2) - (height // 2)
   root.geometry(f'{width}x{height}+{x}+{y}')
   
   # Set minimum window size
   root.minsize(800, 600)
   
   # Configure window icon (if you have one)
   try:
       # You can add an icon file here
       # root.iconbitmap('icon.ico')
       pass
   except:
       pass
   
   # Start the game
   game = PrimsGame(root)
   
   # Add some keyboard shortcuts
   def on_key_press(event):
       if event.keysym == 'n' or event.keysym == 'N':
           game.generate_new_graph()
       elif event.keysym == 'c' or event.keysym == 'C':
           game.check_solution()
       elif event.keysym == 'r' or event.keysym == 'R':
           game.reset_selection()
       elif event.keysym == 'h' or event.keysym == 'H':
           game.show_help()
       elif event.keysym == 's' or event.keysym == 'S':
           game.show_solution()
   
   root.bind('<KeyPress>', on_key_press)
   root.focus_set()  # Allow window to receive key events
   
   # Add a welcome message
   def show_welcome():
       welcome_msg = """🎉 Welcome to Prim's Algorithm Learning Game! 🎉

This interactive game will help you learn Prim's algorithm for finding Minimum Spanning Trees.

🎯 Your Goal: Select edges to build the MST with minimum total weight

⌨️ Keyboard Shortcuts:
- N - New Graph
- C - Check Solution  
- R - Reset Selection
- H - Help
- S - Show Solution

Good luck and have fun learning! 🌲"""
       
       messagebox.showinfo("🌲 Welcome!", welcome_msg)
   
   # Show welcome message after a short delay
   root.after(500, show_welcome)
   
   root.mainloop()

if __name__ == "__main__":
   main()
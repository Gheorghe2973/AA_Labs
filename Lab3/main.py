import time
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
from collections import deque
import random

class Graph:
    def __init__(self, vertices):
        self.V = vertices
        self.adj = [[] for _ in range(vertices)]
    
    def add_edge(self, v, w):
        self.adj[v].append(w)
    
    def generate_random_graph(self, edge_probability=0.2):
        for i in range(self.V):
            for j in range(self.V):
                if i != j and random.random() < edge_probability:
                    self.add_edge(i, j)
    
    def dfs(self, start_vertex):
        visited = [False] * self.V
        path = []
        start_time = time.time()
        
        def dfs_util(vertex):
            visited[vertex] = True
            path.append(vertex)
            
            for neighbor in self.adj[vertex]:
                if not visited[neighbor]:
                    dfs_util(neighbor)
        
        dfs_util(start_vertex)
        end_time = time.time()
        
        return path, end_time - start_time
    
    def bfs(self, start_vertex):
        visited = [False] * self.V
        queue = deque([start_vertex])
        visited[start_vertex] = True
        path = []
        
        start_time = time.time()
        
        while queue:
            vertex = queue.popleft()
            path.append(vertex)
            
            for neighbor in self.adj[vertex]:
                if not visited[neighbor]:
                    visited[neighbor] = True
                    queue.append(neighbor)
        
        end_time = time.time()
        
        return path, end_time - start_time

def run_analysis(sizes):
    dfs_times = []
    bfs_times = []
    dfs_vertices_visited = []
    bfs_vertices_visited = []
    
    for size in sizes:
        g = Graph(size)
        g.generate_random_graph(edge_probability=2/size)
        
        dfs_path, dfs_time = g.dfs(0)
        bfs_path, bfs_time = g.bfs(0)
        
        dfs_times.append(dfs_time * 1000)  
        bfs_times.append(bfs_time * 1000)  
        
        dfs_vertices_visited.append(len(dfs_path))
        bfs_vertices_visited.append(len(bfs_path))
    
    return dfs_times, bfs_times, dfs_vertices_visited, bfs_vertices_visited

def visualize_search_algorithm(graph, path, title):
    G = nx.DiGraph()
    
    for v in range(graph.V):
        G.add_node(v)
    
    for v in range(graph.V):
        for w in graph.adj[v]:
            G.add_edge(v, w)
    
    pos = nx.spring_layout(G, seed=42)
    
    plt.figure(figsize=(10, 6))
    
    edge_colors = ['black' for _ in G.edges()]
    node_colors = ['lightblue' for _ in G.nodes()]
    
    visited_edges = []
    for i in range(len(path) - 1):
        for j in range(i + 1, len(path)):
            if path[j] in graph.adj[path[i]]:
                visited_edges.append((path[i], path[j]))
                break
    
    for i, (u, v) in enumerate(G.edges()):
        if (u, v) in visited_edges:
            edge_colors[i] = 'red'
    
    for i, node in enumerate(G.nodes()):
        if node in path:
            node_colors[i] = 'lightgreen'
            if node == path[0]:
                node_colors[i] = 'orange'
    
    nx.draw(G, pos, with_labels=True, node_color=node_colors, 
            edge_color=edge_colors, arrows=True, node_size=500, font_size=10)
    
    plt.title(title)
    plt.tight_layout()
    plt.savefig(f"{title.lower().replace(' ', '_')}.png")
    plt.close()

def compare_algorithms():
    sizes = [10, 50, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000]
    dfs_times, bfs_times, dfs_visits, bfs_visits = run_analysis(sizes)
    
    plt.figure(figsize=(14, 6))
    
    plt.subplot(1, 2, 1)
    plt.plot(sizes, dfs_times, 'o-', label='DFS')
    plt.plot(sizes, bfs_times, 's-', label='BFS')
    plt.xlabel('Number of Vertices')
    plt.ylabel('Execution Time (ms)')
    plt.title('Time Complexity Comparison')
    plt.legend()
    plt.grid(True)
    
    plt.subplot(1, 2, 2)
    plt.plot(sizes, dfs_visits, 'o-', label='DFS')
    plt.plot(sizes, bfs_visits, 's-', label='BFS')
    plt.xlabel('Number of Vertices')
    plt.ylabel('Number of Vertices Visited')
    plt.title('Vertices Visited Comparison')
    plt.legend()
    plt.grid(True)
    
    plt.tight_layout()
    plt.savefig("algorithm_comparison.png")
    plt.close()
    
    small_graph = Graph(8)
    small_graph.generate_random_graph(edge_probability=0.3)
    
    dfs_path, _ = small_graph.dfs(0)
    bfs_path, _ = small_graph.bfs(0)
    
    visualize_search_algorithm(small_graph, dfs_path, "DFS Traversal")
    visualize_search_algorithm(small_graph, bfs_path, "BFS Traversal")
    
    return dfs_times, bfs_times, dfs_visits, bfs_visits, sizes

def main():
    dfs_times, bfs_times, dfs_visits, bfs_visits, sizes = compare_algorithms()
    
    print("Depth-First Search (DFS) vs Breadth-First Search (BFS) Analysis")
    print("\nGraph Sizes:", sizes)
    print("\nDFS Execution Times (ms):", [round(t, 4) for t in dfs_times])
    print("BFS Execution Times (ms):", [round(t, 4) for t in bfs_times])
    
    print("\nDFS Vertices Visited:", dfs_visits)
    print("BFS Vertices Visited:", bfs_visits)
    
    print("\nConclusion:")
    avg_dfs_time = sum(dfs_times) / len(dfs_times)
    avg_bfs_time = sum(bfs_times) / len(bfs_times)
    
    if avg_dfs_time < avg_bfs_time:
        print(f"DFS was faster on average by {round((avg_bfs_time - avg_dfs_time), 4)} ms")
    else:
        print(f"BFS was faster on average by {round((avg_dfs_time - avg_bfs_time), 4)} ms")
    
    for i, size in enumerate(sizes):
        if dfs_visits[i] != bfs_visits[i]:
            print(f"For graph size {size}, DFS visited {dfs_visits[i]} vertices while BFS visited {bfs_visits[i]} vertices")
    
    print("\nVisualizations have been saved as 'dfs_traversal.png', 'bfs_traversal.png', and 'algorithm_comparison.png'")

if __name__ == "__main__":
    main()
import time
import random
import networkx as nx
import matplotlib.pyplot as plt
from collections import deque
import numpy as np

class Graph:
    def __init__(self, vertices):
        self.V = vertices
        self.graph = [[] for _ in range(vertices)]

    def add_edge(self, u, v):
        self.graph[u].append(v)

    def bfs(self, start_vertex):
        visited = [False] * self.V
        queue = deque([start_vertex])
        visited[start_vertex] = True
        path = []

        while queue:
            vertex = queue.popleft()
            path.append(vertex)
            
            for adjacent in self.graph[vertex]:
                if not visited[adjacent]:
                    queue.append(adjacent)
                    visited[adjacent] = True
        
        return path, visited.count(True)

    def dfs(self, start_vertex):
        visited = [False] * self.V
        path = []
        
        def dfs_util(vertex):
            visited[vertex] = True
            path.append(vertex)
            
            for adjacent in self.graph[vertex]:
                if not visited[adjacent]:
                    dfs_util(adjacent)
        
        dfs_util(start_vertex)
        return path, visited.count(True)

def generate_random_graph(n, edge_probability=0.3):
    g = Graph(n)
    for i in range(n):
        for j in range(n):
            if i != j and random.random() < edge_probability:
                g.add_edge(i, j)
    return g

def visualize_graph(g, bfs_path=None, dfs_path=None):
    G = nx.DiGraph()
    
    for i in range(g.V):
        G.add_node(i)
        
    for i in range(g.V):
        for j in g.graph[i]:
            G.add_edge(i, j)
    
    plt.figure(figsize=(12, 10))
    pos = nx.spring_layout(G, seed=42)
    
    if bfs_path:
        bfs_edges = [(bfs_path[i], bfs_path[i+1]) for i in range(len(bfs_path)-1) if (bfs_path[i], bfs_path[i+1]) in G.edges()]
        nx.draw_networkx_edges(G, pos, edgelist=bfs_edges, edge_color='r', width=2)
    
    if dfs_path:
        dfs_edges = [(dfs_path[i], dfs_path[i+1]) for i in range(len(dfs_path)-1) if (dfs_path[i], dfs_path[i+1]) in G.edges()]
        nx.draw_networkx_edges(G, pos, edgelist=dfs_edges, edge_color='b', width=2)
    
    edge_colors = ['red' if dfs_path and edge in [(dfs_path[i], dfs_path[i+1]) for i in range(len(dfs_path)-1) if (dfs_path[i], dfs_path[i+1]) in G.edges()] 
                  else 'blue' if bfs_path and edge in [(bfs_path[i], bfs_path[i+1]) for i in range(len(bfs_path)-1) if (bfs_path[i], bfs_path[i+1]) in G.edges()]
                  else 'gray' for edge in G.edges()]
    
    nx.draw(G, pos, with_labels=True, node_color='lightblue', node_size=500, arrows=True, edge_color=edge_colors)
    
    if bfs_path and dfs_path:
        plt.title(f"Graph with BFS path (blue) and DFS path (red)")
    elif bfs_path:
        plt.title("Graph with BFS path")
    elif dfs_path:
        plt.title("Graph with DFS path")
    else:
        plt.title("Random Graph")
        
    plt.tight_layout()
    plt.savefig("graph_visualization.png")
    plt.close()

def compare_algorithms():
    vertices_range = range(10, 501, 50)
    bfs_times = []
    dfs_times = []
    bfs_coverage = []
    dfs_coverage = []
    
    for v in vertices_range:
        g = generate_random_graph(v)
        
        start_time = time.time()
        _, bfs_covered = g.bfs(0)
        bfs_time = time.time() - start_time
        
        start_time = time.time()
        _, dfs_covered = g.dfs(0)
        dfs_time = time.time() - start_time
        
        bfs_times.append(bfs_time)
        dfs_times.append(dfs_time)
        bfs_coverage.append(bfs_covered / v)
        dfs_coverage.append(dfs_covered / v)
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    ax1.plot(vertices_range, bfs_times, 'b-', label='BFS')
    ax1.plot(vertices_range, dfs_times, 'r-', label='DFS')
    ax1.set_xlabel('Number of Vertices')
    ax1.set_ylabel('Execution Time (seconds)')
    ax1.set_title('Time Complexity Comparison')
    ax1.legend()
    ax1.grid(True)
    
    ax2.plot(vertices_range, bfs_coverage, 'b-', label='BFS')
    ax2.plot(vertices_range, dfs_coverage, 'r-', label='DFS')
    ax2.set_xlabel('Number of Vertices')
    ax2.set_ylabel('Coverage (fraction of vertices)')
    ax2.set_title('Coverage Comparison')
    ax2.legend()
    ax2.grid(True)
    
    plt.tight_layout()
    plt.savefig("comparison_chart.png")
    plt.close()

    return vertices_range, bfs_times, dfs_times, bfs_coverage, dfs_coverage

def visualize_additional_metrics():
    vertices_range = list(range(10, 101, 10))
    edge_probs = [0.1, 0.3, 0.5, 0.7]
    
    bfs_depth = []
    dfs_depth = []
    
    for prob in edge_probs:
        bfs_depths = []
        dfs_depths = []
        
        for v in vertices_range:
            total_bfs_depth = 0
            total_dfs_depth = 0
            trials = 5
            
            for _ in range(trials):
                g = generate_random_graph(v, prob)
                
                bfs_path, _ = g.bfs(0)
                dfs_path, _ = g.dfs(0)
                
                total_bfs_depth += len(bfs_path)
                total_dfs_depth += len(dfs_path)
            
            bfs_depths.append(total_bfs_depth / trials)
            dfs_depths.append(total_dfs_depth / trials)
        
        bfs_depth.append(bfs_depths)
        dfs_depth.append(dfs_depths)
    
    plt.figure(figsize=(12, 10))
    
    for i, prob in enumerate(edge_probs):
        plt.subplot(2, 2, i+1)
        plt.plot(vertices_range, bfs_depth[i], 'b-', label='BFS')
        plt.plot(vertices_range, dfs_depth[i], 'r-', label='DFS')
        plt.xlabel('Number of Vertices')
        plt.ylabel('Average Path Length')
        plt.title(f'Path Length (Edge Probability = {prob})')
        plt.legend()
        plt.grid(True)
    
    plt.tight_layout()
    plt.savefig("path_length_comparison.png")
    plt.close()

def main():
    small_graph_size = 10
    g = generate_random_graph(small_graph_size, 0.3)
    
    start_vertex = 0
    bfs_path, _ = g.bfs(start_vertex)
    dfs_path, _ = g.dfs(start_vertex)
    
    print(f"BFS Path: {bfs_path}")
    print(f"DFS Path: {dfs_path}")
    
    visualize_graph(g, bfs_path, dfs_path)
    
    vertices_range, bfs_times, dfs_times, bfs_coverage, dfs_coverage = compare_algorithms()
    
    print("\nPerformance Comparison:")
    print("Vertices | BFS Time | DFS Time | BFS Coverage | DFS Coverage")
    print("-" * 65)
    
    for i, v in enumerate(vertices_range):
        print(f"{v:8d} | {bfs_times[i]:.6f} | {dfs_times[i]:.6f} | {bfs_coverage[i]:.4f} | {dfs_coverage[i]:.4f}")
    
    visualize_additional_metrics()
    
    print("\nAnalysis complete. Check the generated visualization files.")

if __name__ == "__main__":
    main()
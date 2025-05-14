import time
import random
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from heapq import heappush, heappop

class Graph:
    def __init__(self, vertices):
        self.V = vertices
        self.graph = []
        
    def add_edge(self, u, v, w):
        self.graph.append([u, v, w])
        
    def find(self, parent, i):
        if parent[i] != i:
            parent[i] = self.find(parent, parent[i])
        return parent[i]
    
    def union(self, parent, rank, x, y):
        root_x = self.find(parent, x)
        root_y = self.find(parent, y)
        
        if root_x == root_y:
            return
        
        if rank[root_x] < rank[root_y]:
            parent[root_x] = root_y
        elif rank[root_x] > rank[root_y]:
            parent[root_y] = root_x
        else:
            parent[root_y] = root_x
            rank[root_x] += 1
    
    def kruskal_mst(self):
        result = []
        i, e = 0, 0
        
        self.graph = sorted(self.graph, key=lambda item: item[2])
        
        parent = []
        rank = []
        
        for node in range(self.V):
            parent.append(node)
            rank.append(0)
        
        start_time = time.time()
        while e < self.V - 1 and i < len(self.graph):
            u, v, w = self.graph[i]
            i += 1
            
            x = self.find(parent, u)
            y = self.find(parent, v)
            
            if x != y:
                e += 1
                result.append([u, v, w])
                self.union(parent, rank, x, y)
        end_time = time.time()
        
        total_weight = sum(w for u, v, w in result)
        return result, end_time - start_time, total_weight

class GraphAdjList:
    def __init__(self, vertices):
        self.V = vertices
        self.graph = [[] for _ in range(vertices)]
    
    def add_edge(self, u, v, w):
        self.graph[u].append((v, w))
        self.graph[v].append((u, w))
    
    def prim_mst(self):
        key = [float('inf')] * self.V
        parent = [-1] * self.V
        mst_set = [False] * self.V
        
        key[0] = 0
        pq = [(0, 0)]  # (weight, vertex)
        
        start_time = time.time()
        while pq:
            weight, u = heappop(pq)
            
            if mst_set[u]:
                continue
                
            mst_set[u] = True
            
            for v, w in self.graph[u]:
                if not mst_set[v] and w < key[v]:
                    key[v] = w
                    parent[v] = u
                    heappush(pq, (w, v))
        end_time = time.time()
        
        result = []
        for i in range(1, self.V):
            result.append([parent[i], i, key[i]])
        
        total_weight = sum(key[i] for i in range(1, self.V))
        return result, end_time - start_time, total_weight

def generate_random_weighted_graph(n, edge_probability=0.3, min_weight=1, max_weight=10):
    g_kruskal = Graph(n)
    g_prim = GraphAdjList(n)
    
    edges_added = 0
    
    for i in range(n):
        for j in range(i+1, n):  # Undirected graph, so only need i < j
            if random.random() < edge_probability:
                weight = random.randint(min_weight, max_weight)
                g_kruskal.add_edge(i, j, weight)
                g_prim.add_edge(i, j, weight)
                edges_added += 1
    
    return g_kruskal, g_prim, edges_added

def visualize_graph_and_mst(n, edges, mst_edges, algorithm_name):
    G = nx.Graph()
    
    for i in range(n):
        G.add_node(i)
    
    for u, v, w in edges:
        G.add_edge(u, v, weight=w)
    
    plt.figure(figsize=(12, 10))
    pos = nx.spring_layout(G, seed=42)
    
    edge_colors = ['gray' for _ in range(len(G.edges()))]
    edge_widths = [1 for _ in range(len(G.edges()))]
    
    mst_edge_set = {(min(u, v), max(u, v)) for u, v, _ in mst_edges}
    
    for i, (u, v) in enumerate(G.edges()):
        if (min(u, v), max(u, v)) in mst_edge_set:
            edge_colors[i] = 'red'
            edge_widths[i] = 2.5
    
    nx.draw(G, pos, with_labels=True, node_color='lightblue', 
            node_size=500, edge_color=edge_colors, width=edge_widths)
    
    edge_labels = {(u, v): d['weight'] for u, v, d in G.edges(data=True)}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
    
    plt.title(f"Graph with {algorithm_name} MST (highlighted in red)")
    plt.tight_layout()
    plt.savefig(f"{algorithm_name.lower()}_mst_visualization.png")
    plt.close()

def compare_algorithms():
    vertices_range = range(10, 501, 50)
    kruskal_times = []
    prim_times = []
    edge_counts = []
    kruskal_weights = []
    prim_weights = []
    
    for v in vertices_range:
        print(f"Processing graph with {v} vertices...")
        g_kruskal, g_prim, edges = generate_random_weighted_graph(v, edge_probability=2.5/v)
        
        kruskal_mst, kruskal_time, kruskal_weight = g_kruskal.kruskal_mst()
        prim_mst, prim_time, prim_weight = g_prim.prim_mst()
        
        kruskal_times.append(kruskal_time)
        prim_times.append(prim_time)
        edge_counts.append(edges)
        kruskal_weights.append(kruskal_weight)
        prim_weights.append(prim_weight)
        
        if v == 10:
            all_edges = g_kruskal.graph
            visualize_graph_and_mst(v, all_edges, kruskal_mst, "Kruskal's")
            visualize_graph_and_mst(v, all_edges, prim_mst, "Prim's")
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    ax1.plot(vertices_range, kruskal_times, 'r-', label="Kruskal's")
    ax1.plot(vertices_range, prim_times, 'b-', label="Prim's")
    ax1.set_xlabel('Number of Vertices')
    ax1.set_ylabel('Execution Time (seconds)')
    ax1.set_title('Time Complexity Comparison')
    ax1.legend()
    ax1.grid(True)
    
    ax2.plot(vertices_range, kruskal_weights, 'r-', label="Kruskal's")
    ax2.plot(vertices_range, prim_weights, 'b-', label="Prim's")
    ax2.set_xlabel('Number of Vertices')
    ax2.set_ylabel('MST Total Weight')
    ax2.set_title('MST Weight Comparison')
    ax2.legend()
    ax2.grid(True)
    
    plt.tight_layout()
    plt.savefig("comparison_chart.png")
    plt.close()
    
    plt.figure(figsize=(10, 6))
    plt.plot(vertices_range, edge_counts, 'g-')
    plt.xlabel('Number of Vertices')
    plt.ylabel('Number of Edges')
    plt.title('Edge Count for Generated Graphs')
    plt.grid(True)
    plt.savefig("edge_count.png")
    plt.close()
    
    return vertices_range, kruskal_times, prim_times, edge_counts, kruskal_weights, prim_weights

def visualize_density_impact():
    vertices = 100
    densities = [0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.7, 0.9]
    kruskal_times = []
    prim_times = []
    edge_counts = []
    
    for density in densities:
        print(f"Testing with density {density}...")
        g_kruskal, g_prim, edges = generate_random_weighted_graph(vertices, edge_probability=density)
        
        _, kruskal_time, _ = g_kruskal.kruskal_mst()
        _, prim_time, _ = g_prim.prim_mst()
        
        kruskal_times.append(kruskal_time)
        prim_times.append(prim_time)
        edge_counts.append(edges)
    
    plt.figure(figsize=(12, 6))
    
    plt.subplot(1, 2, 1)
    plt.plot(densities, kruskal_times, 'r-', label="Kruskal's")
    plt.plot(densities, prim_times, 'b-', label="Prim's")
    plt.xlabel('Edge Density')
    plt.ylabel('Execution Time (seconds)')
    plt.title('Time vs. Graph Density')
    plt.legend()
    plt.grid(True)
    
    plt.subplot(1, 2, 2)
    plt.plot(densities, edge_counts, 'g-')
    plt.xlabel('Edge Density')
    plt.ylabel('Number of Edges')
    plt.title('Edge Count vs. Density')
    plt.grid(True)
    
    plt.tight_layout()
    plt.savefig("density_impact.png")
    plt.close()

def main():
    print("Starting Greedy Algorithms Analysis - Minimum Spanning Trees...")
    
    small_graph_size = 10
    g_kruskal, g_prim, _ = generate_random_weighted_graph(small_graph_size)
    
    print("Computing MSTs for sample graph...")
    kruskal_mst, kruskal_time, kruskal_weight = g_kruskal.kruskal_mst()
    prim_mst, prim_time, prim_weight = g_prim.prim_mst()
    
    print(f"Kruskal's MST edges: {kruskal_mst}")
    print(f"Prim's MST edges: {prim_mst}")
    print(f"Kruskal's Time: {kruskal_time:.6f} seconds")
    print(f"Prim's Time: {prim_time:.6f} seconds")
    print(f"Kruskal's MST Weight: {kruskal_weight}")
    print(f"Prim's MST Weight: {prim_weight}")
    
    all_edges = g_kruskal.graph
    visualize_graph_and_mst(small_graph_size, all_edges, kruskal_mst, "Kruskal's")
    visualize_graph_and_mst(small_graph_size, all_edges, prim_mst, "Prim's")
    
    print("\nComparing algorithms across various graph sizes...")
    vertices_range, kruskal_times, prim_times, edge_counts, kruskal_weights, prim_weights = compare_algorithms()
    
    print("\nPerformance Comparison:")
    print("Vertices | Edges | Kruskal Time | Prim Time | Kruskal Weight | Prim Weight")
    print("-" * 80)
    
    for i, v in enumerate(vertices_range):
        print(f"{v:8d} | {edge_counts[i]:5d} | {kruskal_times[i]:.6f} | {prim_times[i]:.6f} | {kruskal_weights[i]:14.2f} | {prim_weights[i]:10.2f}")
    
    print("\nAnalyzing impact of graph density...")
    visualize_density_impact()
    
    print("\nAnalysis complete. Check the generated visualization files.")

if __name__ == "__main__":
    main()
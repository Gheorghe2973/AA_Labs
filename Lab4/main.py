import time
import heapq
import random
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
from collections import defaultdict
import pandas as pd
import seaborn as sns

class Graph:
    def __init__(self, vertices, is_dense=False, edge_probability=0.3):
        self.V = vertices
        self.is_dense = is_dense
        self.graph = [[float('inf') for _ in range(vertices)] for _ in range(vertices)]
        for i in range(vertices):
            self.graph[i][i] = 0
        edge_prob = 0.7 if is_dense else edge_probability
        for i in range(vertices):
            for j in range(vertices):
                if i != j and random.random() < edge_prob:
                    self.graph[i][j] = random.randint(1, 10)

    def dijkstra(self, start_vertex):
        start_time = time.time()
        distances = [float('inf')] * self.V
        distances[start_vertex] = 0
        priority_queue = [(0, start_vertex)]
        visited = [False] * self.V
        while priority_queue:
            current_distance, current_vertex = heapq.heappop(priority_queue)
            if visited[current_vertex]:
                continue
            visited[current_vertex] = True
            for adj_vertex in range(self.V):
                if self.graph[current_vertex][adj_vertex] != float('inf'):
                    distance = current_distance + self.graph[current_vertex][adj_vertex]
                    if distance < distances[adj_vertex]:
                        distances[adj_vertex] = distance
                        heapq.heappush(priority_queue, (distance, adj_vertex))
        end_time = time.time()
        execution_time = end_time - start_time
        return distances, execution_time

    def floyd_warshall(self):
        start_time = time.time()
        dist = [row[:] for row in self.graph]
        for k in range(self.V):
            for i in range(self.V):
                for j in range(self.V):
                    if dist[i][k] != float('inf') and dist[k][j] != float('inf') and dist[i][k] + dist[k][j] < dist[i][j]:
                        dist[i][j] = dist[i][k] + dist[k][j]
        end_time = time.time()
        execution_time = end_time - start_time
        return dist, execution_time

def visualize_graph(graph, algorithm="Both", sparse_or_dense=""):
    G = nx.DiGraph()
    for i in range(graph.V):
        G.add_node(i)
    for i in range(graph.V):
        for j in range(graph.V):
            if i != j and graph.graph[i][j] != float('inf'):
                G.add_edge(i, j, weight=graph.graph[i][j])
    plt.figure(figsize=(10, 8))
    pos = nx.spring_layout(G, seed=42)
    nx.draw_networkx_nodes(G, pos, node_size=500, node_color='lightblue')
    nx.draw_networkx_edges(G, pos, width=1.0, alpha=0.7, arrows=True)
    edge_labels = {(i, j): graph.graph[i][j] for i in range(graph.V) for j in range(graph.V) if i != j and graph.graph[i][j] != float('inf')}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
    nx.draw_networkx_labels(G, pos)
    density_type = "Dense" if graph.is_dense else "Sparse"
    title = f"{algorithm} Algorithm - {density_type} Graph ({graph.V} nodes){sparse_or_dense}"
    plt.title(title)
    plt.axis('off')
    plt.tight_layout()
    plt.savefig(f"graph_{algorithm.lower()}_{density_type.lower()}_{graph.V}.png")
    plt.close()

def compare_algorithms(vertex_range=range(10, 201, 20)):
    dijkstra_sparse_times = []
    dijkstra_dense_times = []
    floyd_warshall_sparse_times = []
    floyd_warshall_dense_times = []
    for v in vertex_range:
        sparse_graph = Graph(v, is_dense=False)
        dense_graph = Graph(v, is_dense=True)
        if v == vertex_range[0]:
            visualize_graph(sparse_graph, "Both", " (Sparse)")
            visualize_graph(dense_graph, "Both", " (Dense)")
        _, dijkstra_sparse_time = sparse_graph.dijkstra(0)
        dijkstra_sparse_times.append(dijkstra_sparse_time)
        _, dijkstra_dense_time = dense_graph.dijkstra(0)
        dijkstra_dense_times.append(dijkstra_dense_time)
        _, floyd_sparse_time = sparse_graph.floyd_warshall()
        floyd_warshall_sparse_times.append(floyd_sparse_time)
        _, floyd_dense_time = dense_graph.floyd_warshall()
        floyd_warshall_dense_times.append(floyd_dense_time)
        print(f"Completed analysis for {v} vertices")
    plt.figure(figsize=(14, 8))
    plt.subplot(1, 2, 1)
    plt.plot(list(vertex_range), dijkstra_sparse_times, 'b-', label='Dijkstra (Sparse)')
    plt.plot(list(vertex_range), dijkstra_dense_times, 'b--', label='Dijkstra (Dense)')
    plt.plot(list(vertex_range), floyd_warshall_sparse_times, 'r-', label='Floyd-Warshall (Sparse)')
    plt.plot(list(vertex_range), floyd_warshall_dense_times, 'r--', label='Floyd-Warshall (Dense)')
    plt.xlabel('Number of Vertices')
    plt.ylabel('Execution Time (seconds)')
    plt.title('Algorithm Performance: Execution Time vs. Graph Size')
    plt.legend()
    plt.grid(True)
    plt.subplot(1, 2, 2)
    plt.plot(list(vertex_range), [t / v for v, t in zip(vertex_range, dijkstra_sparse_times)], 'b-', label='Dijkstra (Sparse) per vertex')
    plt.plot(list(vertex_range), [t / v for v, t in zip(vertex_range, dijkstra_dense_times)], 'b--', label='Dijkstra (Dense) per vertex')
    plt.plot(list(vertex_range), [t / (v*v) for v, t in zip(vertex_range, floyd_warshall_sparse_times)], 'r-', label='Floyd-Warshall (Sparse) per edge')
    plt.plot(list(vertex_range), [t / (v*v) for v, t in zip(vertex_range, floyd_warshall_dense_times)], 'r--', label='Floyd-Warshall (Dense) per edge')
    plt.xlabel('Number of Vertices')
    plt.ylabel('Normalized Execution Time')
    plt.title('Normalized Algorithm Performance')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("algorithm_comparison.png")
    plt.close()
    plt.figure(figsize=(12, 8))
    plt.subplot(2, 2, 1)
    plt.plot(list(vertex_range), dijkstra_sparse_times, 'b-o', label='Dijkstra (Sparse)')
    plt.plot(list(vertex_range), dijkstra_dense_times, 'g-o', label='Dijkstra (Dense)')
    plt.xlabel('Number of Vertices')
    plt.ylabel('Execution Time (seconds)')
    plt.title('Dijkstra Algorithm Performance')
    plt.legend()
    plt.grid(True)
    plt.subplot(2, 2, 2)
    plt.plot(list(vertex_range), floyd_warshall_sparse_times, 'r-o', label='Floyd-Warshall (Sparse)')
    plt.plot(list(vertex_range), floyd_warshall_dense_times, 'm-o', label='Floyd-Warshall (Dense)')
    plt.xlabel('Number of Vertices')
    plt.ylabel('Execution Time (seconds)')
    plt.title('Floyd-Warshall Algorithm Performance')
    plt.legend()
    plt.grid(True)
    plt.subplot(2, 2, 3)
    plt.plot(list(vertex_range), dijkstra_sparse_times, 'b-o', label='Dijkstra (Sparse)')
    plt.plot(list(vertex_range), floyd_warshall_sparse_times, 'r-o', label='Floyd-Warshall (Sparse)')
    plt.xlabel('Number of Vertices')
    plt.ylabel('Execution Time (seconds)')
    plt.title('Sparse Graph Comparison')
    plt.legend()
    plt.grid(True)
    plt.subplot(2, 2, 4)
    plt.plot(list(vertex_range), dijkstra_dense_times, 'g-o', label='Dijkstra (Dense)')
    plt.plot(list(vertex_range), floyd_warshall_dense_times, 'm-o', label='Floyd-Warshall (Dense)')
    plt.xlabel('Number of Vertices')
    plt.ylabel('Execution Time (seconds)')
    plt.title('Dense Graph Comparison')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("detailed_comparison.png")
    plt.close()
    data = {
        'Vertices': list(vertex_range),
        'Dijkstra (Sparse)': dijkstra_sparse_times,
        'Dijkstra (Dense)': dijkstra_dense_times,
        'Floyd-Warshall (Sparse)': floyd_warshall_sparse_times,
        'Floyd-Warshall (Dense)': floyd_warshall_dense_times
    }
    df = pd.DataFrame(data)
    print("\nExecution Time Comparison (seconds):")
    print(df.to_string(index=False))
    df.to_csv("algorithm_execution_times.csv", index=False)
    plt.figure(figsize=(12, 8))
    heatmap_data = df.iloc[:, 1:].T
    heatmap_data.columns = df['Vertices']
    sns.heatmap(heatmap_data, annot=True, cmap="YlGnBu", fmt=".6f")
    plt.title('Algorithm Execution Times Heatmap')
    plt.xlabel('Number of Vertices')
    plt.ylabel('Algorithm')
    plt.tight_layout()
    plt.savefig("algorithm_heatmap.png")
    plt.close()
    return df

def analyze_complexity_vs_theory():
    vertex_range = range(10, 201, 20)
    vertices = list(vertex_range)
    dijkstra_theoretical = [v**2 * np.log2(v) for v in vertices]
    floyd_theoretical = [v**3 for v in vertices]
    df = compare_algorithms(vertex_range)
    max_dijkstra_sparse = max(df['Dijkstra (Sparse)'])
    max_dijkstra_theory = max(dijkstra_theoretical)
    max_floyd_sparse = max(df['Floyd-Warshall (Sparse)'])
    max_floyd_theory = max(floyd_theoretical)
    dijkstra_empirical_normalized = [t * (max_dijkstra_theory / max_dijkstra_sparse) for t in df['Dijkstra (Sparse)']]
    floyd_empirical_normalized = [t * (max_floyd_theory / max_floyd_sparse) for t in df['Floyd-Warshall (Sparse)']]
    plt.figure(figsize=(14, 6))
    plt.subplot(1, 2, 1)
    plt.plot(vertices, dijkstra_theoretical, 'b-', label='Theoretical O(V² log V)')
    plt.plot(vertices, dijkstra_empirical_normalized, 'r--', label='Empirical (Normalized)')
    plt.xlabel('Number of Vertices')
    plt.ylabel('Normalized Complexity')
    plt.title('Dijkstra: Theoretical vs. Empirical Complexity')
    plt.legend()
    plt.grid(True)
    plt.subplot(1, 2, 2)
    plt.plot(vertices, floyd_theoretical, 'b-', label='Theoretical O(V³)')
    plt.plot(vertices, floyd_empirical_normalized, 'r--', label='Empirical (Normalized)')
    plt.xlabel('Number of Vertices')
    plt.ylabel('Normalized Complexity')
    plt.title('Floyd-Warshall: Theoretical vs. Empirical Complexity')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("theoretical_vs_empirical.png")
    plt.close()

def test_algorithm_correctness():
    g = Graph(5, is_dense=False)
    g.graph = [
        [0, 9, float('inf'), 5, float('inf')],
        [float('inf'), 0, 1, float('inf'), float('inf')],
        [float('inf'), float('inf'), 0, float('inf'), 2],
        [float('inf'), 3, float('inf'), 0, 6],
        [float('inf'), float('inf'), float('inf'), float('inf'), 0]
    ]
    dijkstra_distances, _ = g.dijkstra(0)
    print("Dijkstra's algorithm distances from vertex 0:", dijkstra_distances)
    floyd_distances, _ = g.floyd_warshall()
    print("Floyd-Warshall algorithm all-pairs shortest paths:")
    for row in floyd_distances:
        print([x if x != float('inf') else "inf" for x in row])
    visualize_graph(g, "Test", " (Test Graph)")

def optimize_sparse_graph_parameters():
    vertices = 100
    probabilities = [0.05, 0.1, 0.2, 0.3, 0.4, 0.5]
    dijkstra_times = []
    floyd_times = []
    for prob in probabilities:
        sparse_graph = Graph(vertices, is_dense=False, edge_probability=prob)
        _, dijkstra_time = sparse_graph.dijkstra(0)
        dijkstra_times.append(dijkstra_time)
        _, floyd_time = sparse_graph.floyd_warshall()
        floyd_times.append(floyd_time)
        print(f"Completed analysis for edge probability {prob}")
    plt.figure(figsize=(10, 6))
    plt.plot(probabilities, dijkstra_times, 'b-o', label='Dijkstra')
    plt.plot(probabilities, floyd_times, 'r-o', label='Floyd-Warshall')
    plt.xlabel('Edge Probability')
    plt.ylabel('Execution Time (seconds)')
    plt.title(f'Algorithm Performance vs. Edge Probability (V={vertices})')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("edge_probability_analysis.png")
    plt.close()

def main():
    print("Testing algorithm correctness...")
    test_algorithm_correctness()
    print("\nComparing algorithms across different graph sizes...")
    compare_algorithms()
    print("\nAnalyzing complexity vs. theoretical expectations...")
    analyze_complexity_vs_theory()
    print("\nOptimizing sparse graph parameters...")
    optimize_sparse_graph_parameters()

if __name__ == "__main__":
    main()

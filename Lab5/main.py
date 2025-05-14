import networkx as nx
import matplotlib.pyplot as plt
import time
import random
import numpy as np

def generate_random_graph(n, edge_probability=0.3, weight_range=(1, 10)):
    G = nx.Graph()
    
    for i in range(n):
        G.add_node(i)
    
    for i in range(n):
        for j in range(i+1, n):
            if random.random() < edge_probability:
                weight = random.randint(weight_range[0], weight_range[1])
                G.add_edge(i, j, weight=weight)
    
    if not nx.is_connected(G):
        components = list(nx.connected_components(G))
        for i in range(len(components) - 1):
            u = random.choice(list(components[i]))
            v = random.choice(list(components[i + 1]))
            weight = random.randint(weight_range[0], weight_range[1])
            G.add_edge(u, v, weight=weight)
    
    return G

def prim_algorithm(G):
    if not nx.is_connected(G):
        raise nx.NetworkXError("Graph is not connected.")
    
    start_time = time.time()
    
    mst = nx.Graph()
    nodes = list(G.nodes())
    start_node = nodes[0]
    mst.add_node(start_node)
    
    edges = []
    for step in range(len(nodes) - 1):
        potential_edges = []
        for u in mst.nodes():
            for v in G.neighbors(u):
                if v not in mst.nodes():
                    potential_edges.append((u, v, G[u][v]['weight']))
        
        if not potential_edges:
            break
        
        u, v, weight = min(potential_edges, key=lambda x: x[2])
        mst.add_node(v)
        mst.add_edge(u, v, weight=weight)
        edges.append((u, v))
    
    end_time = time.time()
    execution_time = end_time - start_time
    
    return mst, edges, execution_time

def kruskal_algorithm(G):
    if not nx.is_connected(G):
        raise nx.NetworkXError("Graph is not connected.")
    
    start_time = time.time()
    
    mst = nx.Graph()
    for node in G.nodes():
        mst.add_node(node)
    
    edges = [(u, v, G[u][v]['weight']) for u, v in G.edges()]
    edges.sort(key=lambda x: x[2])
    
    parent = {node: node for node in G.nodes()}
    
    def find_set(node):
        if parent[node] != node:
            parent[node] = find_set(parent[node])
        return parent[node]
    
    def union(u, v):
        parent[find_set(u)] = find_set(v)
    
    mst_edges = []
    for u, v, weight in edges:
        if find_set(u) != find_set(v):
            mst.add_edge(u, v, weight=weight)
            mst_edges.append((u, v))
            union(u, v)
    
    end_time = time.time()
    execution_time = end_time - start_time
    
    return mst, mst_edges, execution_time

def visualize_mst(G, mst, edges, title):
    plt.figure(figsize=(10, 8))
    
    pos = nx.spring_layout(G, seed=42)
    
    edge_colors = ['gray' if edge not in edges and (edge[1], edge[0]) not in edges else 'red' for edge in G.edges()]
    edge_widths = [1 if edge not in edges and (edge[1], edge[0]) not in edges else 2.5 for edge in G.edges()]
    
    nx.draw_networkx_nodes(G, pos, node_size=500, node_color='lightblue')
    nx.draw_networkx_labels(G, pos, font_size=12)
    
    nx.draw_networkx_edges(G, pos, width=edge_widths, edge_color=edge_colors)
    
    edge_labels = {(u, v): G[u][v]['weight'] for u, v in G.edges()}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
    
    plt.title(title)
    plt.axis('off')
    plt.tight_layout()
    plt.savefig(f"{title.replace(' ', '_').lower()}.png", dpi=300)
    plt.show()

def compare_algorithms(node_counts):
    prim_times = []
    kruskal_times = []
    
    for n in node_counts:
        G = generate_random_graph(n)
        
        _, _, prim_time = prim_algorithm(G)
        prim_times.append(prim_time)
        
        _, _, kruskal_time = kruskal_algorithm(G)
        kruskal_times.append(kruskal_time)
    
    plt.figure(figsize=(10, 6))
    plt.plot(node_counts, prim_times, marker='o', label='Prim')
    plt.plot(node_counts, kruskal_times, marker='s', label='Kruskal')
    plt.xlabel('Number of Nodes')
    plt.ylabel('Execution Time (seconds)')
    plt.title('Algorithm Performance Comparison')
    plt.legend()
    plt.grid(True)
    plt.savefig("performance_comparison.png", dpi=300)
    plt.show()
    
    return prim_times, kruskal_times

if __name__ == "__main__":
    n_nodes = 10
    G = generate_random_graph(n_nodes)
    
    mst_prim, edges_prim, time_prim = prim_algorithm(G)
    visualize_mst(G, mst_prim, edges_prim, "Prim's Algorithm MST")
    print(f"Prim's Algorithm Execution Time: {time_prim:.6f} seconds")
    
    mst_kruskal, edges_kruskal, time_kruskal = kruskal_algorithm(G)
    visualize_mst(G, mst_kruskal, edges_kruskal, "Kruskal's Algorithm MST")
    print(f"Kruskal's Algorithm Execution Time: {time_kruskal:.6f} seconds")
    
    node_counts = [10, 20, 50, 100, 200, 500]
    prim_times, kruskal_times = compare_algorithms(node_counts)
    
    results = list(zip(node_counts, prim_times, kruskal_times))
    print("\nPerformance Results:")
    print("Nodes\tPrim (s)\tKruskal (s)")
    for n, p, k in results:
        print(f"{n}\t{p:.6f}\t{k:.6f}")
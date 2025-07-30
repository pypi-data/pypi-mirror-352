import random
import warnings

import networkx as nx


# --- Helper Function: generate_random_graph ---
def generate_random_graph(num_nodes: int, num_edges: int, num_types: int) -> nx.Graph:
    """
    Generates a random undirected, unweighted graph with node types.
    Optimized to avoid MemoryError for large sparse graphs by not materializing
    all non-edges.
    """

    G = nx.Graph()
    nodes = list(range(num_nodes))
    G.add_nodes_from(nodes)

    # Assign types
    types = [f"Type{i}" for i in range(num_types)]
    node_types = {node: random.choice(types) for node in nodes}
    nx.set_node_attributes(G, node_types, "type")

    # Add edges by randomly sampling pairs
    added_edges = set()  # To store unique edges (canonical form (u,v) with u < v)
    edges_to_add_count = 0
    max_possible_edges = num_nodes * (num_nodes - 1) // 2

    if num_edges > max_possible_edges:
        warnings.warn(
            f"Requested {num_edges} edges but only {max_possible_edges} possible. Adding all possible edges."
        )
        num_edges = max_possible_edges  # Cap num_edges at max possible

    max_attempts = num_edges * 10 if num_edges > 0 else 1000  # Heuristic max attempts

    attempts_made = 0
    while edges_to_add_count < num_edges and attempts_made < max_attempts:
        u = random.randint(0, num_nodes - 1)
        v = random.randint(0, num_nodes - 1)
        attempts_made += 1

        if u == v:  # No self-loops
            continue

        # Ensure (u,v) or (v,u) is not already added (for undirected graph)
        edge_tuple = tuple(sorted((u, v)))  # Canonical representation
        if edge_tuple not in added_edges:
            G.add_edge(u, v)
            added_edges.add(edge_tuple)
            edges_to_add_count += 1

    if edges_to_add_count < num_edges:
        warnings.warn(
            f"Could only add {edges_to_add_count} out of {num_edges} requested edges. Graph might not have desired density."
        )

    return G

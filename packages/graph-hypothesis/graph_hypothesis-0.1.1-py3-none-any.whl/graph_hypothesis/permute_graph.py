import random
import warnings
from typing import Any, Callable, Tuple

import networkx as nx


# --- Helper for Multiprocessing Pool ---
def _generate_permuted_graph_and_calc_metric(
    args: Tuple[nx.Graph, Any, Any, Callable, int],
) -> float:
    """
    Helper function for multiprocessing pool.
    Generates one permuted graph (holding 'fixed_type' nodes fixed, shuffling others)
    and calculates the specified metric on it.

    Args:
        args (Tuple): A tuple containing:
            - original_graph (nx.Graph): The base graph (will be copied).
            - fixed_type (Any): The node type to keep fixed during shuffling.
            - target_type (Any): The other node type for the metric calculation.
            - metric_func (Callable): The metric function to apply.
            - seed (int): A unique seed for this permutation for reproducibility.

    Returns:
        float: The metric value calculated on the permuted graph.
    """
    original_graph, fixed_type, target_type, metric_func, seed = args

    # Each process needs its own random state for independent permutations
    # and consistent seeding across processes.
    rng = random.Random(seed)

    # Create a deep copy of the graph to ensure process independence
    # Only copy node attributes if graph structure is large but attributes are small
    # For NetworkX, graph.copy() makes a shallow copy of attributes, so we'll do deeper for types
    perm_graph = nx.Graph(
        original_graph
    )  # Copies structure, but node/edge attr dicts are shallow

    # Deep copy node 'type' attributes explicitly
    # This ensures modifications to perm_graph.nodes[n]['type'] don't affect original_graph
    for node in perm_graph.nodes():
        if "type" in original_graph.nodes[node]:
            perm_graph.nodes[node]["type"] = original_graph.nodes[node]["type"]

    # Identify nodes whose types will be shuffled
    # Nodes of 'fixed_type' for the metric are the ones we *keep fixed* during shuffle
    nodes_to_keep_fixed_in_shuffle = [
        n for n, data in perm_graph.nodes(data=True) if data.get("type") == fixed_type
    ]

    # All other nodes will have their types shuffled
    nodes_to_shuffle = [
        n for n in perm_graph.nodes() if n not in nodes_to_keep_fixed_in_shuffle
    ]

    if not nodes_to_shuffle:
        # If there are no nodes to shuffle, the permutation won't change anything.
        # This can happen if fixed_type accounts for all nodes or only one type exists.
        # In permutation testing, this implies the null distribution would be trivial (all same as observed).
        warnings.warn(
            "No nodes to shuffle for permutation. Permutation will not vary from original."
        )
        # Return the original metric to keep the permutation_statistics list filled
        return metric_func(original_graph, fixed_type, target_type)

    # Extract types to shuffle and shuffle them
    shuffled_types_pool = [perm_graph.nodes[n]["type"] for n in nodes_to_shuffle]
    rng.shuffle(shuffled_types_pool)  # Use the process-specific RNG

    # Reassign shuffled types to nodes
    for i, node in enumerate(nodes_to_shuffle):
        perm_graph.nodes[node]["type"] = shuffled_types_pool[i]

    # Calculate metric on the permuted graph
    perm_metric_value = metric_func(perm_graph, fixed_type, target_type)
    return perm_metric_value

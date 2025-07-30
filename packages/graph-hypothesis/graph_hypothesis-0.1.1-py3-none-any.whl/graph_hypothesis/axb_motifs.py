import warnings
from typing import Any

import networkx as nx

from .validate_graph import validate_graph_parameters


def calculate_axb_motifs_metric(
    graph: nx.Graph, fixed_type: Any, target_type: Any
) -> int:
    """
    Calculates the number of A-X-B motifs (paths of length 2) in the graph.

    An A-X-B motif consists of a path where a node of `fixed_type` (A) is connected
    to a central node (X), which is then connected to a node of `target_type` (B).
    The central node X can be of any type. Since the graph is undirected,
    B-X-A is considered the same motif as A-X-B. This function counts each
    unique A-X-B motif once.

    Args:
        graph (nx.Graph): The input undirected, unweighted NetworkX graph.
                          Each node must have a 'type' attribute.
        fixed_type (Any): The node type for the 'A' position in the A-X-B motif.
        target_type (Any): The node type for the 'B' position in the A-X-B motif.

    Returns:
        int: The total count of A-X-B motifs. Returns 0 if no such motifs exist,
             or if either `fixed_type` or `target_type` nodes are not present
             in the graph.

    Raises:
        AssertionError:
            - If the input `graph` is empty (has no nodes).
            - If `fixed_type` is the same as `target_type`.
            - If `fixed_type` is not found as a node type in the graph.
            - If `target_type` is not found as a node type in the graph.
    """
    validate_graph_parameters(graph, fixed_type, target_type)

    # Assert graph is not empty
    assert (
        graph.number_of_nodes() > 0
    ), "Input graph cannot be empty (must have at least one node)."

    # Get all distinct node types present in the graph
    all_distinct_types = {graph.nodes[n]["type"] for n in graph.nodes()}

    # Assertions for fixed_type and target_type
    assert (
        fixed_type != target_type
    ), f"fixed_type ('{fixed_type}') and target_type ('{target_type}') cannot be the same."
    assert (
        fixed_type in all_distinct_types
    ), f"fixed_type ('{fixed_type}') is not found as a node type in the graph."
    assert (
        target_type in all_distinct_types
    ), f"target_type ('{target_type}') is not found as a node type in the graph."

    # Check if there are any nodes of the specified types before proceeding
    nodes_of_fixed_type_exist = any(
        graph.nodes[n]["type"] == fixed_type for n in graph.nodes()
    )
    nodes_of_target_type_exist = any(
        graph.nodes[n]["type"] == target_type for n in graph.nodes()
    )

    if not nodes_of_fixed_type_exist or not nodes_of_target_type_exist:
        warnings.warn(
            f"No nodes of type '{fixed_type}' or '{target_type}' found in the graph. "
            f"Returning 0 as no A-X-B motifs are possible."
        )
        return 0

    motif_count = 0
    # Iterate through each node as the potential central node 'X'
    for center_node in graph.nodes():
        fixed_type_neighbors_count = 0
        target_type_neighbors_count = 0

        # Categorize neighbors of center_node by type
        for neighbor_node in graph.neighbors(center_node):
            neighbor_type = graph.nodes[neighbor_node].get("type")
            if neighbor_type == fixed_type:
                fixed_type_neighbors_count += 1
            elif neighbor_type == target_type:
                target_type_neighbors_count += 1

        # The number of A-X-B paths centered at center_node is the product of
        # fixed_type neighbors and target_type neighbors.
        # This correctly counts each unique path once for undirected graphs.
        motif_count += fixed_type_neighbors_count * target_type_neighbors_count

    return motif_count

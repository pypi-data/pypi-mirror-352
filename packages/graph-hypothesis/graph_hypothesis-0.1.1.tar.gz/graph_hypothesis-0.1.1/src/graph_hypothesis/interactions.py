import warnings
from typing import Any

import networkx as nx

from .validate_graph import validate_graph_parameters


def calculate_interactions_metric(
    graph: nx.Graph, fixed_type: Any, target_type: Any
) -> int:
    """
    Calculates the number of edges (interactions) connecting a node of `fixed_type`
    to a node of `target_type`.

    This metric counts every edge where one endpoint has `fixed_type` and the other
    has `target_type`. Since the graph is undirected, an edge (u, v) where u is `fixed_type`
    and v is `target_type` is counted once, and is equivalent to v being `target_type` and u
    being `fixed_type`.

    Args:
        graph (nx.Graph): The input undirected, unweighted NetworkX graph.
                          Each node must have a 'type' attribute.
        fixed_type (Any): The first node type for the interaction.
        target_type (Any): The second node type for the interaction.

    Returns:
        int: The total count of edges (interactions) between nodes of `fixed_type` and `target_type`.
             Returns 0 if no such edges exist, or if either type is not present
             in the graph, or if no nodes of the specified types are found.

    Raises:
        AssertionError:
            - If the input `graph` is empty (has no nodes).
            - If `fixed_type` is the same as `target_type`.
            - If `fixed_type` is not found as a node type in the graph.
            - If `target_type` is not found as a node type in the graph.
    """
    # Validate core graph properties (undirected, unweighted, node types, type count cap)
    validate_graph_parameters(graph, fixed_type, target_type)

    # Check if there are any nodes of the specified types
    nodes_of_fixed_type_exist = any(
        graph.nodes[n]["type"] == fixed_type for n in graph.nodes()
    )
    nodes_of_target_type_exist = any(
        graph.nodes[n]["type"] == target_type for n in graph.nodes()
    )

    if not nodes_of_fixed_type_exist or not nodes_of_target_type_exist:
        warnings.warn(
            f"No nodes of type '{fixed_type}' or '{target_type}' found in the graph. "
            f"Returning 0 as no interactions are possible."
        )
        return 0

    interaction_count = 0
    # Iterate through all edges once, which is efficient for sparse graphs.
    for node_u, node_v in graph.edges():
        node_u_type = graph.nodes[node_u].get("type")
        node_v_type = graph.nodes[node_v].get("type")

        # Check if the edge connects the specified types
        # Since it's undirected, (fixed_type, target_type) is same as (target_type, fixed_type)
        if (node_u_type == fixed_type and node_v_type == target_type) or (
            node_u_type == target_type and node_v_type == fixed_type
        ):
            interaction_count += 1
    return interaction_count
